/* ============ FLYLYFE storefront — Shopify Storefront API (Cart API) ============ */
const SHOP = '31zn52-zd.myshopify.com';
const TOKEN = '5a0bb1dcf0c57b7764bbebf0cc40c898'; // public storefront token (safe for client)
const API = `https://${SHOP}/api/2025-10/graphql.json`;

const COLOR_HEX = {
  'White':'#f4f4f2','Black':'#1b1b1c','Ivory':'#f1e8d2','Natural':'#fff7e9'
};
const MEN_HANDLES = ['the-anthem-tee','the-conga-tee','the-signature-tee'];
const WOMEN_HANDLES = ['the-anthem-tee-womens','the-conga-tee-womens','the-signature-tee-womens'];
const TAGLINES = {
  'the-anthem-tee':'THE MANTRA, WORN LOUD','the-conga-tee':'MOVE THE BODY','the-signature-tee':'THE CLASSIC',
  'the-anthem-tee-womens':'THE MANTRA, WORN LOUD','the-conga-tee-womens':'MOVE THE BODY','the-signature-tee-womens':'THE CLASSIC'
};

let PRODUCTS = {};          // handle -> product node
let cartId = localStorage.getItem('flylyfe_cart');
let modalState = null;      // {handle, color, size}

/* ---------- GraphQL helper ---------- */
async function gql(query, variables = {}) {
  const res = await fetch(API, {
    method: 'POST',
    headers: {'Content-Type':'application/json','X-Shopify-Storefront-Access-Token': TOKEN},
    body: JSON.stringify({query, variables})
  });
  const j = await res.json();
  if (j.errors) console.error('Storefront API:', j.errors);
  return j.data;
}

/* ---------- Load products ---------- */
const PRODUCT_QUERY = `{
  products(first: 20) {
    edges { node {
      id handle title descriptionHtml
      images(first: 12) { edges { node { url altText } } }
      options { name values }
      variants(first: 50) { edges { node {
        id title availableForSale price { amount currencyCode }
        selectedOptions { name value }
      } } }
    } }
  }
}`;

async function loadProducts() {
  const data = await gql(PRODUCT_QUERY);
  if (!data) return showLoadError();
  data.products.edges.forEach(e => { PRODUCTS[e.node.handle] = e.node; });
  renderGrid('gridMen', MEN_HANDLES);
  renderGrid('gridWomen', WOMEN_HANDLES);
}

function showLoadError(){
  document.querySelectorAll('.grid__loading').forEach(el=>{
    el.textContent = 'DROP TEMPORARILY OFFLINE — REFRESH TO RETRY';
  });
}

function money(amount){ return '$' + parseFloat(amount).toFixed(2); }

function imagesFor(p, color, placement){
  // match by alt text "... {Color} {front|back}"
  const imgs = p.images.edges.map(e=>e.node);
  const hit = imgs.find(i => (i.altText||'').includes(color) && (i.altText||'').toLowerCase().includes(placement));
  return hit ? hit.url : (imgs[0] ? imgs[0].url : '');
}

/* ---------- Render product grids ---------- */
function renderGrid(elId, handles){
  const grid = document.getElementById(elId);
  grid.innerHTML = '';
  handles.forEach((h, idx) => {
    const p = PRODUCTS[h];
    if (!p) return;
    const colors = p.options.find(o=>o.name==='Color').values;
    const price = p.variants.edges[0].node.price.amount;
    const front = imagesFor(p, 'Black', 'front');
    const back = imagesFor(p, 'Black', 'back');
    const card = document.createElement('article');
    card.className = 'card reveal';
    card.style.transitionDelay = (idx*80)+'ms';
    card.innerHTML = `
      <div class="card__media">
        <img src="${front}" alt="${p.title} front" loading="lazy">
        ${back && back!==front ? `<img class="back" src="${back}" alt="${p.title} back" loading="lazy">` : ''}
        <span class="card__tag">${TAGLINES[h]||'FLYLYFE'}</span>
        <span class="card__quick">QUICK ADD +</span>
      </div>
      <div class="card__body">
        <div>
          <div class="card__name">${p.title.replace(" — Women's","")}</div>
          <div class="card__colors">${colors.map(c=>`<span class="dot" style="background:${COLOR_HEX[c]||'#777'}"></span>`).join('')}</div>
        </div>
        <div class="card__price">${money(price)}</div>
      </div>`;
    card.addEventListener('click', ()=>openModal(h));
    grid.appendChild(card);
  });
  observeReveals();
}

/* ---------- Product modal ---------- */
const modal = document.getElementById('modal');
function openModal(handle){
  const p = PRODUCTS[handle];
  const colors = p.options.find(o=>o.name==='Color').values;
  modalState = {handle, color: colors[0], size: null};
  document.getElementById('mTitle').textContent = p.title;
  document.getElementById('mPrice').textContent = money(p.variants.edges[0].node.price.amount);
  document.getElementById('mDesc').innerHTML = p.descriptionHtml;
  renderModalColors(p, colors);
  renderModalSizes(p);
  renderModalGallery(p);
  modal.hidden = false;
  document.body.style.overflow = 'hidden';
}
function closeModal(){ modal.hidden = true; document.body.style.overflow=''; }

function renderModalColors(p, colors){
  const wrap = document.getElementById('mColors');
  wrap.innerHTML = '';
  document.getElementById('mColorName').textContent = modalState.color.toUpperCase();
  colors.forEach(c=>{
    const b = document.createElement('button');
    b.className = 'swatch' + (c===modalState.color?' on':'');
    b.style.background = COLOR_HEX[c]||'#777';
    b.title = c; b.setAttribute('aria-label', c);
    b.onclick = ()=>{ modalState.color=c; renderModalColors(p,colors); renderModalSizes(p); renderModalGallery(p); };
    wrap.appendChild(b);
  });
}

function renderModalSizes(p){
  const sizes = p.options.find(o=>o.name==='Size').values;
  const wrap = document.getElementById('mSizes');
  wrap.innerHTML = '';
  sizes.forEach(s=>{
    const v = findVariant(p, modalState.color, s);
    const b = document.createElement('button');
    const ok = v && v.availableForSale;
    b.className = 'size' + (modalState.size===s?' on':'') + (ok?'':' off');
    b.textContent = s;
    if (ok) b.onclick = ()=>{ modalState.size=s; renderModalSizes(p); };
    wrap.appendChild(b);
  });
}

function renderModalGallery(p){
  const main = document.getElementById('mImg');
  const thumbs = document.getElementById('mThumbs');
  const imgs = p.images.edges.map(e=>e.node).filter(i=>(i.altText||'').includes(modalState.color));
  const list = imgs.length ? imgs : p.images.edges.map(e=>e.node).slice(0,2);
  main.src = list[0] ? list[0].url : '';
  main.alt = p.title + ' ' + modalState.color;
  thumbs.innerHTML = '';
  list.forEach((im,i)=>{
    const t = document.createElement('img');
    t.src = im.url; t.alt = im.altText||p.title;
    t.className = i===0?'on':'';
    t.onclick = ()=>{ main.src = im.url; thumbs.querySelectorAll('img').forEach(x=>x.classList.remove('on')); t.classList.add('on'); };
    thumbs.appendChild(t);
  });
}

function findVariant(p, color, size){
  return p.variants.edges.map(e=>e.node).find(v=>{
    const so = Object.fromEntries(v.selectedOptions.map(o=>[o.name,o.value]));
    return so.Color===color && so.Size===size;
  });
}

document.getElementById('mAdd').onclick = async ()=>{
  if (!modalState.size){ toast('PICK A SIZE FIRST'); return; }
  const p = PRODUCTS[modalState.handle];
  const v = findVariant(p, modalState.color, modalState.size);
  if (!v){ toast('UNAVAILABLE'); return; }
  await addToCart(v.id);
  closeModal();
  toast('ADDED TO CART ✓');
  openCart();
};

/* ---------- Cart (Storefront Cart API) ---------- */
const CART_FIELDS = `id checkoutUrl totalQuantity
  cost { subtotalAmount { amount } }
  lines(first: 30) { edges { node {
    id quantity
    merchandise { ... on ProductVariant {
      id title price { amount }
      product { title handle }
      selectedOptions { name value }
    } }
  } } }`;

async function ensureCart(){
  if (cartId){
    const d = await gql(`query($id:ID!){ cart(id:$id){ ${CART_FIELDS} } }`, {id: cartId});
    if (d && d.cart) return d.cart;
  }
  const d = await gql(`mutation{ cartCreate{ cart{ ${CART_FIELDS} } userErrors{ message } } }`);
  const cart = d.cartCreate.cart;
  cartId = cart.id;
  localStorage.setItem('flylyfe_cart', cartId);
  return cart;
}

async function addToCart(variantId){
  await ensureCart();
  const d = await gql(
    `mutation($cartId:ID!,$lines:[CartLineInput!]!){ cartLinesAdd(cartId:$cartId, lines:$lines){ cart{ ${CART_FIELDS} } userErrors{ message } } }`,
    {cartId, lines:[{merchandiseId: variantId, quantity: 1}]});
  renderCart(d.cartLinesAdd.cart);
}

async function updateLine(lineId, qty){
  const d = await gql(
    `mutation($cartId:ID!,$lines:[CartLineUpdateInput!]!){ cartLinesUpdate(cartId:$cartId, lines:$lines){ cart{ ${CART_FIELDS} } userErrors{ message } } }`,
    {cartId, lines:[{id: lineId, quantity: qty}]});
  renderCart(d.cartLinesUpdate.cart);
}

let CURRENT_CART = null;
function renderCart(cart){
  CURRENT_CART = cart;
  document.getElementById('cartCount').textContent = cart.totalQuantity;
  document.getElementById('cartTotal').textContent = money(cart.cost.subtotalAmount.amount);
  const wrap = document.getElementById('cartItems');
  const lines = cart.lines.edges;
  if (!lines.length){ wrap.innerHTML = '<p class="drawer__empty mono">YOUR CART IS EMPTY.<br>GO FEEL SOMETHING.</p>'; return; }
  wrap.innerHTML = '';
  lines.forEach(e=>{
    const l = e.node, m = l.merchandise;
    const opts = m.selectedOptions.map(o=>o.value).join(' / ');
    const p = PRODUCTS[m.product.handle];
    const color = m.selectedOptions.find(o=>o.name==='Color');
    const img = p ? imagesFor(p, color?color.value:'Black', 'front') : '';
    const div = document.createElement('div');
    div.className = 'citem';
    div.innerHTML = `
      <img src="${img}" alt="${m.product.title}">
      <div>
        <div class="citem__name">${m.product.title}</div>
        <div class="citem__meta">${opts}</div>
        <div class="citem__qty">
          <button data-d="-1" aria-label="Decrease">−</button><span class="mono">${l.quantity}</span><button data-d="1" aria-label="Increase">+</button>
        </div>
      </div>
      <div style="text-align:right">
        <div class="citem__price">${money(m.price.amount * l.quantity)}</div>
        <button class="citem__rm">remove</button>
      </div>`;
    div.querySelectorAll('[data-d]').forEach(b=>b.onclick=()=>updateLine(l.id, l.quantity + parseInt(b.dataset.d)));
    div.querySelector('.citem__rm').onclick = ()=>updateLine(l.id, 0);
    wrap.appendChild(div);
  });
}

/* ---------- Drawer / modal wiring ---------- */
const drawer = document.getElementById('drawer');
async function openCart(){
  drawer.hidden = false;
  document.body.style.overflow = 'hidden';
  renderCart(await ensureCart());
}
function closeCart(){ drawer.hidden = true; document.body.style.overflow=''; }
document.getElementById('cartBtn').onclick = openCart;
document.querySelectorAll('[data-closecart]').forEach(el=>el.onclick=closeCart);
document.querySelectorAll('[data-close]').forEach(el=>el.onclick=closeModal);
document.addEventListener('keydown', e=>{ if(e.key==='Escape'){ closeModal(); closeCart(); } });

document.getElementById('checkoutBtn').onclick = ()=>{
  if (CURRENT_CART && CURRENT_CART.totalQuantity > 0) window.location.href = CURRENT_CART.checkoutUrl;
  else toast('CART IS EMPTY');
};

/* ---------- Toast ---------- */
let toastTimer;
function toast(msg){
  const t = document.getElementById('toast');
  t.textContent = msg; t.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(()=>{ t.hidden = true; }, 2200);
}

/* ---------- Scroll reveals ---------- */
function observeReveals(){
  if (!('IntersectionObserver' in window)) {
    document.querySelectorAll('.reveal').forEach(el=>el.classList.add('in'));
    return;
  }
  const io = new IntersectionObserver(es=>es.forEach(e=>{ if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target);} }),{threshold:.08, rootMargin:'0px 0px -40px 0px'});
  document.querySelectorAll('.reveal:not(.in)').forEach(el=>io.observe(el));
  // safety: force-reveal anything still hidden after 1.2s (covers headless/odd viewports)
  setTimeout(()=>document.querySelectorAll('.reveal:not(.in)').forEach(el=>{
    if (el.getBoundingClientRect().top < window.innerHeight) el.classList.add('in');
  }), 1200);
}

/* ---------- Hero carousel ---------- */
const HERO_SLIDES = [
  {img:'assets/hero/carousel-1-black.jpg', alt:'FLYLYFE Anthem Tee — black'},
  {img:'assets/hero/carousel-2-freedom.jpg', alt:'FLYLYFE House Music Is Freedom tee'},
  {img:'assets/hero/carousel-3-house.jpg', alt:'FLYLYFE house music tee'},
];
function initHeroCarousel(){
  const wrap = document.getElementById('heroCarousel');
  const numsWrap = document.getElementById('heroNums');
  if (!wrap) return;
  HERO_SLIDES.forEach((s,i)=>{
    const slide = document.createElement('div');
    slide.className = 'hero__slide' + (i===0?' on':'');
    slide.innerHTML = `<img src="${s.img}" alt="${s.alt}" ${i===0?'fetchpriority="high"':'loading="lazy"'}>`;
    wrap.appendChild(slide);
    const num = document.createElement('button');
    num.className = 'hero__num' + (i===0?' on':'');
    num.textContent = '0'+(i+1);
    num.setAttribute('aria-label','Slide '+(i+1));
    num.onclick = ()=>goToSlide(i);
    numsWrap.appendChild(num);
  });
  let idx = 0;
  const slides = wrap.querySelectorAll('.hero__slide');
  const nums = numsWrap.querySelectorAll('.hero__num');
  window.goToSlide = (n)=>{
    slides[idx].classList.remove('on'); nums[idx].classList.remove('on');
    idx = (n+slides.length)%slides.length;
    slides[idx].classList.add('on'); nums[idx].classList.add('on');
  };
  let timer = setInterval(()=>window.goToSlide(idx+1), 4500);
  wrap.addEventListener('mouseenter', ()=>clearInterval(timer));
  wrap.addEventListener('mouseleave', ()=>{ timer = setInterval(()=>window.goToSlide(idx+1), 4500); });
}

/* ---------- Featured AFTER HOURS strip ---------- */
function renderFeatured(){
  const strip = document.getElementById('featuredStrip');
  if (!strip) return;
  // Pull 4 cells: women's 3 + 1 men's, back-graphic shots
  const picks = [
    {handle:'the-anthem-tee-womens', color:'Black'},
    {handle:'the-conga-tee-womens', color:'Natural'},
    {handle:'the-signature-tee-womens', color:'Black'},
    {handle:'the-anthem-tee', color:'Ivory'},
  ];
  strip.innerHTML = '';
  picks.forEach(p=>{
    const prod = PRODUCTS[p.handle];
    if (!prod) return;
    const img = imagesFor(prod, p.color, 'back') || imagesFor(prod, p.color, 'front');
    const price = prod.variants.edges[0].node.price.amount;
    const cell = document.createElement('div');
    cell.className = 'fcell';
    cell.innerHTML = `<img src="${img}" alt="${prod.title}" loading="lazy">
      <div class="fcell__label"><div class="nm">${prod.title.replace(" — Women's","")}</div><div class="pr">${money(price)}</div></div>`;
    cell.onclick = ()=>openModal(p.handle);
    strip.appendChild(cell);
  });
}

/* ---------- Nav shrink + scroll spy ---------- */
function initScrollUX(){
  const nav = document.getElementById('nav');
  const hero = document.getElementById('heroBg');
  const links = document.querySelectorAll('.nav__links a');
  const sections = ['top','shop','after-hours','story','journal'];
  function onScroll(){
    const y = window.scrollY;
    nav.classList.toggle('shrink', y > 60);
    // hero parallax
    if (hero && y < window.innerHeight) hero.style.transform = `translateY(${y*0.18}px)`;
    // scroll spy
    let active = 'top';
    sections.forEach(id=>{
      const el = document.getElementById(id);
      if (el && el.getBoundingClientRect().top <= 120) active = id;
    });
    links.forEach(a=>a.classList.toggle('active', a.getAttribute('href')==='#'+active));
  }
  window.addEventListener('scroll', onScroll, {passive:true});
  onScroll();
}

/* ---------- Init ---------- */
document.body.classList.add('has-js');
document.getElementById('year').textContent = new Date().getFullYear();
initHeroCarousel();
initScrollUX();
observeReveals();
loadProducts().then(async ()=>{
  renderFeatured();
  observeReveals();
  if (cartId) renderCart(await ensureCart());
});
