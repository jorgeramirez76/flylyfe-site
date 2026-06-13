/* ============ FLYLYFE product page JS — model photos, color-accurate images, PDP ============ */

const SHOP_DOMAIN = '31zn52-zd.myshopify.com';
const STOREFRONT_TOKEN = '5a0bb1dcf0c57b7764bbebf0cc40c898';
const API_URL = `https://${SHOP_DOMAIN}/api/2025-10/graphql.json`;

/* ---- Brand data ---- */
const COLOR_HEX = {
  'White':'#f4f4f2', 'Black':'#1b1b1c',
  'Ivory':'#f1e8d2', 'Natural':'#fff7e9'
};

/* Model photos — local, colour-accurate, front + back per colour */
const MODEL_IMGS = {
  men: {
    Black:   { front:'assets/models/black-front.jpg',  back:'assets/models/black-back.jpg'  },
    White:   { front:'assets/models/white-front.jpg',  back:'assets/models/white-back.jpg'  },
    Ivory:   { front:'assets/models/cream-front.jpg',  back:'assets/models/cream-back.jpg'  },
  },
  women: {
    Black:   { front:'assets/models/black-front.jpg',  back:'assets/models/black-back.jpg'  },
    White:   { front:'assets/models/white-front.jpg',  back:'assets/models/white-back.jpg'  },
    Natural: { front:'assets/models/cream-alt-front.jpg', back:'assets/models/cream-alt-back.jpg' },
  }
};

/* Fallback order when a model shot is missing */
function modelImg(gender, color, view) {
  const g = MODEL_IMGS[gender] || MODEL_IMGS.men;
  const c = g[color] || Object.values(g)[0];
  return c[view] || c.front;
}

/* Shopify Storefront helpers */
async function gql(query, vars={}) {
  const res = await fetch(API_URL, {
    method:'POST',
    headers:{ 'Content-Type':'application/json', 'X-Shopify-Storefront-Access-Token': STOREFRONT_TOKEN },
    body: JSON.stringify({ query, variables: vars })
  });
  const j = await res.json();
  if (j.errors) console.error('SF:', j.errors);
  return j.data;
}

const MEN_HANDLES = ['the-anthem-tee','the-conga-tee','the-signature-tee'];
const WOMEN_HANDLES = ['the-anthem-tee-womens','the-conga-tee-womens','the-signature-tee-womens'];
const TAGLINES = {
  'the-anthem-tee':'FEEL THE MUSIC','the-conga-tee':'MOVE THE BODY','the-signature-tee':'THE CLASSIC',
  'the-anthem-tee-womens':'FEEL THE MUSIC','the-conga-tee-womens':'MOVE THE BODY','the-signature-tee-womens':'THE CLASSIC'
};

const PRODUCT_Q = `{ products(first:20){ edges{ node{
  id handle title descriptionHtml
  images(first:12){ edges{ node{ url altText } } }
  options{ name values }
  variants(first:50){ edges{ node{
    id title availableForSale price{ amount currencyCode }
    selectedOptions{ name value }
  } } }
} } } }`;

let PRODUCTS = {};
let cartId = localStorage.getItem('flylyfe_cart');

/* ---- Load products ---- */
async function loadProducts() {
  const data = await gql(PRODUCT_Q);
  if (!data) { document.querySelectorAll('.grid__loading').forEach(e=>e.textContent='DROP TEMPORARILY OFFLINE'); return; }
  data.products.edges.forEach(e => PRODUCTS[e.node.handle] = e.node);
  renderGrid('gridMen', MEN_HANDLES, 'men');
  renderGrid('gridWomen', WOMEN_HANDLES, 'women');
}

function money(a){ return '$' + parseFloat(a).toFixed(2); }
function gender(handle){ return handle.includes('womens') ? 'women' : 'men'; }
function firstColor(p){ return p.options.find(o=>o.name==='Color')?.values[0] || 'Black'; }

/* ---- Render product grid with model cards ---- */
function renderGrid(elId, handles, g) {
  const grid = document.getElementById(elId);
  grid.innerHTML = '';
  handles.forEach((h, idx) => {
    const p = PRODUCTS[h];
    if (!p) return;
    const colors = p.options.find(o=>o.name==='Color')?.values || [];
    const price = p.variants.edges[0].node.price.amount;
    let activeColor = colors[0];

    const card = document.createElement('article');
    card.className = 'card';

    function buildCard() {
      const front = modelImg(g, activeColor, 'front');
      const back  = modelImg(g, activeColor, 'back');
      card.innerHTML = `
        <div class="card__media">
          <img class="front" src="${front}" alt="${p.title} ${activeColor} front" loading="${idx<3?'eager':'lazy'}">
          <img class="back"  src="${back}"  alt="${p.title} ${activeColor} back"  loading="lazy">
          <span class="card__tag">${TAGLINES[h]||'FLYLYFE'}</span>
          <span class="card__quick mono">VIEW DETAILS →</span>
        </div>
        <div class="card__body">
          <div>
            <div class="card__name">${p.title.replace(" — Women's","")}</div>
            <div class="card__fit mono">${g==='men'?'HEAVYWEIGHT GARMENT-DYE':'WOMEN\'S RELAXED FIT'}</div>
            <div class="card__colors">
              ${colors.map(c=>`<span class="dot${c===activeColor?' on':''}" data-color="${c}" title="${c}" style="background:${COLOR_HEX[c]||'#888'}"></span>`).join('')}
            </div>
          </div>
          <div class="card__price">${money(price)}</div>
        </div>`;

      /* Colour dot clicks — swap model image WITHOUT opening PDP */
      card.querySelectorAll('.card__colors .dot').forEach(dot => {
        dot.addEventListener('click', e => {
          e.stopPropagation();
          activeColor = dot.dataset.color;
          buildCard(); // re-render card with new model image
        });
      });

      /* Clicking card body / image → open PDP */
      card.querySelector('.card__media').addEventListener('click', () => openPDP(h, activeColor));
      card.querySelector('.card__name').closest('.card__body').addEventListener('click', () => openPDP(h, activeColor));
    }

    buildCard();
    grid.appendChild(card);
  });
  renderFeatured();
}

/* ---- Full-Screen Product Detail Page ---- */
const pdp = document.getElementById('pdp');
let pdpState = { handle:null, color:null, size:null };

function openPDP(handle, startColor) {
  const p = PRODUCTS[handle];
  if (!p) return;
  const g = gender(handle);
  const colors = p.options.find(o=>o.name==='Color')?.values || [];
  const sizes  = p.options.find(o=>o.name==='Size')?.values  || [];
  pdpState = { handle, color: startColor || colors[0], size: null };

  function render() {
    const front = modelImg(g, pdpState.color, 'front');
    const back  = modelImg(g, pdpState.color, 'back');
    const price = p.variants.edges[0].node.price.amount;

    document.getElementById('pdpTitle').textContent = p.title;
    document.getElementById('pdpPrice').textContent = money(price);
    document.getElementById('pdpDesc').innerHTML = p.descriptionHtml;

    /* Main image */
    const mainImg = document.getElementById('pdpMain');
    mainImg.classList.add('switching');
    setTimeout(() => {
      mainImg.src = front;
      mainImg.classList.remove('switching');
    }, 200);

    /* Thumbnails: front + back per selected color */
    const thumbs = document.getElementById('pdpThumbs');
    thumbs.innerHTML = '';
    [{ url:front, view:'front' },{ url:back, view:'back' }].forEach((im, i) => {
      const t = document.createElement('img');
      t.src = im.url; t.alt = im.view; t.className = 'pdp__thumb' + (i===0?' on':'');
      t.onclick = () => {
        mainImg.classList.add('switching');
        setTimeout(() => { mainImg.src = im.url; mainImg.classList.remove('switching'); }, 200);
        thumbs.querySelectorAll('.pdp__thumb').forEach(x=>x.classList.remove('on'));
        t.classList.add('on');
      };
      thumbs.appendChild(t);
    });

    /* Color swatches */
    const sw = document.getElementById('pdpSwatches');
    document.getElementById('pdpColorName').textContent = pdpState.color.toUpperCase();
    sw.innerHTML = '';
    colors.forEach(c => {
      const b = document.createElement('button');
      b.className = 'pdp__swatch' + (c===pdpState.color?' on':'');
      b.style.background = COLOR_HEX[c]||'#888';
      b.title = c; b.setAttribute('aria-label', c);
      b.onclick = () => { pdpState.color = c; pdpState.size = null; render(); };
      sw.appendChild(b);
    });

    /* Sizes */
    const sz = document.getElementById('pdpSizes');
    sz.innerHTML = '';
    sizes.forEach(s => {
      const v = findVariant(p, pdpState.color, s);
      const b = document.createElement('button');
      const avail = v && v.availableForSale;
      b.className = 'pdp__size' + (pdpState.size===s?' on':'') + (avail?'':' off');
      b.textContent = s;
      if (avail) b.onclick = () => { pdpState.size = s; sz.querySelectorAll('.pdp__size').forEach(x=>x.classList.remove('on')); b.classList.add('on'); };
      sz.appendChild(b);
    });
  }

  render();
  pdp.hidden = false;
  document.body.style.overflow = 'hidden';
}

function closePDP() {
  pdp.hidden = true;
  document.body.style.overflow = '';
}

document.getElementById('pdpBack').onclick = closePDP;
document.addEventListener('keydown', e => { if(e.key==='Escape') { closePDP(); closeCart(); } });

document.getElementById('pdpATC').onclick = async () => {
  if (!pdpState.size) { showToast('PICK A SIZE FIRST'); return; }
  const p = PRODUCTS[pdpState.handle];
  const v = findVariant(p, pdpState.color, pdpState.size);
  if (!v) { showToast('UNAVAILABLE'); return; }
  document.getElementById('pdpATC').disabled = true;
  await addToCart(v.id);
  document.getElementById('pdpATC').disabled = false;
  showToast('ADDED TO CART ✓');
  closePDP();
  openCart();
};

/* ---- Cart (unchanged Storefront Cart API) ---- */
const CART_FIELDS = `id checkoutUrl totalQuantity
  cost{ subtotalAmount{ amount } }
  lines(first:30){ edges{ node{
    id quantity
    merchandise{ ... on ProductVariant{
      id title price{ amount }
      product{ title handle }
      selectedOptions{ name value }
    } }
  } } }`;

async function ensureCart() {
  if (cartId) {
    const d = await gql(`query($id:ID!){ cart(id:$id){ ${CART_FIELDS} } }`, {id:cartId});
    if (d?.cart) return d.cart;
  }
  const d = await gql(`mutation{ cartCreate{ cart{ ${CART_FIELDS} } userErrors{ message } } }`);
  const cart = d.cartCreate.cart;
  cartId = cart.id; localStorage.setItem('flylyfe_cart', cartId);
  return cart;
}

async function addToCart(variantId) {
  await ensureCart();
  const d = await gql(
    `mutation($cid:ID!,$lines:[CartLineInput!]!){ cartLinesAdd(cartId:$cid,lines:$lines){ cart{ ${CART_FIELDS} } } }`,
    { cid:cartId, lines:[{merchandiseId:variantId, quantity:1}] });
  renderCart(d.cartLinesAdd.cart);
}

async function updateLine(lineId, qty) {
  const d = await gql(
    `mutation($cid:ID!,$lines:[CartLineUpdateInput!]!){ cartLinesUpdate(cartId:$cid,lines:$lines){ cart{ ${CART_FIELDS} } } }`,
    { cid:cartId, lines:[{id:lineId, quantity:qty}] });
  renderCart(d.cartLinesUpdate.cart);
}

let CURRENT_CART = null;
function renderCart(cart) {
  CURRENT_CART = cart;
  document.getElementById('cartCount').textContent = cart.totalQuantity;
  document.getElementById('cartTotal').textContent = money(cart.cost.subtotalAmount.amount);
  const wrap = document.getElementById('cartItems');
  const lines = cart.lines.edges;
  if (!lines.length) { wrap.innerHTML='<p class="drawer__empty mono">YOUR CART IS EMPTY.<br>GO FEEL SOMETHING.</p>'; return; }
  wrap.innerHTML = '';
  lines.forEach(e => {
    const l=e.node, m=l.merchandise;
    const opts = m.selectedOptions.map(o=>o.value).join(' / ');
    const colorOpt = m.selectedOptions.find(o=>o.name==='Color');
    const g = gender(m.product.handle);
    const img = colorOpt ? modelImg(g, colorOpt.value, 'front') : 'assets/models/black-front.jpg';
    const div = document.createElement('div');
    div.className = 'citem';
    div.innerHTML = `
      <img src="${img}" alt="${m.product.title}">
      <div>
        <div class="citem__name">${m.product.title}</div>
        <div class="citem__meta mono">${opts}</div>
        <div class="citem__qty">
          <button data-d="-1" aria-label="Decrease">−</button>
          <span class="mono">${l.quantity}</span>
          <button data-d="1" aria-label="Increase">+</button>
        </div>
        <button class="citem__rm mono">remove</button>
      </div>
      <div class="citem__price mono">${money(parseFloat(m.price.amount)*l.quantity)}</div>`;
    div.querySelectorAll('[data-d]').forEach(b=>b.onclick=()=>updateLine(l.id, l.quantity+parseInt(b.dataset.d)));
    div.querySelector('.citem__rm').onclick=()=>updateLine(l.id,0);
    wrap.appendChild(div);
  });
}

/* ---- Cart drawer ---- */
const drawer = document.getElementById('drawer');
async function openCart() {
  drawer.hidden = false;
  document.body.style.overflow='hidden';
  renderCart(await ensureCart());
}
function closeCart() { drawer.hidden=true; document.body.style.overflow=''; }
document.getElementById('cartBtn').onclick = openCart;
document.querySelectorAll('[data-closecart]').forEach(el=>el.onclick=closeCart);
document.getElementById('checkoutBtn').onclick = () => {
  if (CURRENT_CART?.totalQuantity > 0) window.location.href = CURRENT_CART.checkoutUrl;
  else showToast('CART IS EMPTY');
};

/* ---- Featured strip (AFTER HOURS) ---- */
function renderFeatured() {
  const strip = document.getElementById('featuredStrip');
  if (!strip) return;
  const picks = [
    {handle:'the-anthem-tee-womens', color:'Black'},
    {handle:'the-conga-tee-womens',  color:'Natural'},
    {handle:'the-anthem-tee',        color:'Ivory'},
    {handle:'the-conga-tee',         color:'Black'},
  ];
  strip.innerHTML='';
  picks.forEach(pk => {
    const p = PRODUCTS[pk.handle];
    if (!p) return;
    const g = gender(pk.handle);
    const img = modelImg(g, pk.color, 'back');
    const price = p.variants.edges[0].node.price.amount;
    const cell = document.createElement('div');
    cell.className = 'fcell';
    cell.innerHTML = `<img src="${img}" alt="${p.title}" loading="lazy">
      <div class="fcell__label">
        <div class="nm">${p.title.replace(" — Women's","")}</div>
        <div class="pr mono">${money(price)}</div>
      </div>`;
    cell.onclick = () => openPDP(pk.handle, pk.color);
    strip.appendChild(cell);
  });
}

/* ---- Utility ---- */
function findVariant(p, color, size) {
  return p.variants.edges.map(e=>e.node).find(v => {
    const so = Object.fromEntries(v.selectedOptions.map(o=>[o.name,o.value]));
    return so.Color===color && so.Size===size;
  });
}

let toastTimer;
function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent=msg; t.hidden=false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(()=>t.hidden=true, 2200);
}

/* ---- Hero carousel ---- */
const HERO_SLIDES = [
  {img:'assets/models/black-back.jpg',      alt:'FLYLYFE Anthem Tee black'},
  {img:'assets/models/cream-back.jpg',       alt:'FLYLYFE tee cream'},
  {img:'assets/models/cream-alt-back.jpg',   alt:'FLYLYFE house music tee'},
];

function initHeroCarousel() {
  const wrap = document.getElementById('heroCarousel');
  const numsWrap = document.getElementById('heroNums');
  if (!wrap) return;
  HERO_SLIDES.forEach((s,i) => {
    const slide = document.createElement('div');
    slide.className = 'hero__slide'+(i===0?' on':'');
    slide.innerHTML = `<img src="${s.img}" alt="${s.alt}" ${i===0?'fetchpriority="high"':'loading="lazy"'}>`;
    wrap.appendChild(slide);
    const num = document.createElement('button');
    num.className='hero__num'+(i===0?' on':'');
    num.textContent='0'+(i+1);
    num.setAttribute('aria-label','Slide '+(i+1));
    num.onclick=()=>goToSlide(i);
    numsWrap.appendChild(num);
  });
  let idx=0;
  const slides=wrap.querySelectorAll('.hero__slide');
  const nums=numsWrap.querySelectorAll('.hero__num');
  window.goToSlide = n => {
    slides[idx].classList.remove('on'); nums[idx].classList.remove('on');
    idx=(n+slides.length)%slides.length;
    slides[idx].classList.add('on'); nums[idx].classList.add('on');
  };
  let timer=setInterval(()=>goToSlide(idx+1),4500);
  wrap.addEventListener('mouseenter',()=>clearInterval(timer));
  wrap.addEventListener('mouseleave',()=>{ timer=setInterval(()=>goToSlide(idx+1),4500); });
}

/* ---- Nav shrink + scroll spy ---- */
function initScrollUX() {
  const nav=document.getElementById('nav');
  const heroBg=document.getElementById('heroBg');
  const links=document.querySelectorAll('.nav__links a');
  const sections=['top','shop','after-hours','story','journal'];
  const onScroll = () => {
    const y=window.scrollY;
    nav.classList.toggle('shrink',y>60);
    if (heroBg && y<window.innerHeight) heroBg.style.transform=`translateY(${y*.18}px)`;
    let active='top';
    sections.forEach(id=>{ const el=document.getElementById(id); if(el&&el.getBoundingClientRect().top<=120) active=id; });
    links.forEach(a=>a.classList.toggle('active',a.getAttribute('href')==='#'+active));
  };
  window.addEventListener('scroll',onScroll,{passive:true});
  onScroll();
}

/* ---- Scroll reveals ---- */
function observeReveals() {
  if (!('IntersectionObserver' in window)) {
    document.querySelectorAll('.reveal').forEach(el=>el.classList.add('in')); return;
  }
  const io = new IntersectionObserver(es=>es.forEach(e=>{
    if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target); }
  }),{threshold:.08,rootMargin:'0px 0px -40px 0px'});
  document.querySelectorAll('.reveal:not(.in)').forEach(el=>io.observe(el));
  setTimeout(()=>document.querySelectorAll('.reveal:not(.in)').forEach(el=>{
    if(el.getBoundingClientRect().top < window.innerHeight) el.classList.add('in');
  }),1200);
}

/* ---- Init ---- */
document.body.classList.add('has-js');
document.getElementById('year').textContent = new Date().getFullYear();
initHeroCarousel();
initScrollUX();
observeReveals();
loadProducts().then(async () => {
  observeReveals();
  if (cartId) renderCart(await ensureCart());
});
