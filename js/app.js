/* ============ FLYLYFE — back-first product display + accurate mockups + lifestyle ============ */

const SHOP_DOMAIN = '31zn52-zd.myshopify.com';
const STOREFRONT_TOKEN = '5a0bb1dcf0c57b7764bbebf0cc40c898';
const API_URL = `https://${SHOP_DOMAIN}/api/2025-10/graphql.json`;

const COLOR_HEX = {
  'White':'#f4f4f2', 'Black':'#1b1b1c',
  'Ivory':'#f1e8d2', 'Natural':'#fff7e9'
};

/* Accurate Printful mockups — handle → color → {front, back} (the TRUE designs customers receive) */
let MOCKUPS = {};

/* Lifestyle "worn" shots — real models, used as supporting imagery in the PDP */
const LIFESTYLE = {
  'the-anthem-tee':       ['assets/models/black-back.jpg','assets/models/black-front.jpg'],
  'the-anthem-tee-womens':['assets/models/black-back.jpg'],
  'the-conga-tee':        ['assets/models/cream-back.jpg'],
  'the-signature-tee':    ['assets/models/cream-alt-back.jpg'],
};

const MEN_HANDLES = ['the-anthem-tee','the-conga-tee','the-signature-tee'];
const WOMEN_HANDLES = ['the-anthem-tee-womens','the-conga-tee-womens','the-signature-tee-womens'];
const TAGLINES = {
  'the-anthem-tee':'FEEL THE MUSIC','the-conga-tee':'MOVE THE BODY','the-signature-tee':'THE CLASSIC',
  'the-anthem-tee-womens':'FEEL THE MUSIC','the-conga-tee-womens':'MOVE THE BODY','the-signature-tee-womens':'THE CLASSIC'
};
/* short selling descriptor under each product name */
const SUBTITLE = {
  'the-anthem-tee':'The mantra, worn big on the back',
  'the-conga-tee':'Dancer & conga — the rhythm on your back',
  'the-signature-tee':'Clean FLYLYFE wordmark',
  'the-anthem-tee-womens':'The mantra, relaxed cut',
  'the-conga-tee-womens':'Dancer & conga, relaxed cut',
  'the-signature-tee-womens':'Clean wordmark, relaxed cut',
};

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

const PRODUCT_Q = `{ products(first:20){ edges{ node{
  id handle title descriptionHtml
  options{ name values }
  variants(first:50){ edges{ node{
    id title availableForSale price{ amount currencyCode }
    selectedOptions{ name value }
  } } }
} } } }`;

let PRODUCTS = {};
let cartId = localStorage.getItem('flylyfe_cart');

function money(a){ return '$' + parseFloat(a).toFixed(2); }
function gender(h){ return h.includes('womens') ? 'women' : 'men'; }

/* Image lookup — always prefer accurate mockup */
function mockup(handle, color, view) {
  const m = MOCKUPS[handle];
  if (!m) return '';
  const c = m[color] || Object.values(m)[0];
  return (c && (c[view] || c.back || c.front)) || '';
}

async function init() {
  // load mockup manifest + products in parallel
  const [manifest, data] = await Promise.all([
    fetch('assets/products/manifest.json').then(r=>r.json()).catch(()=>({})),
    gql(PRODUCT_Q)
  ]);
  MOCKUPS = manifest;
  if (!data) { document.querySelectorAll('.grid__loading').forEach(e=>e.textContent='DROP TEMPORARILY OFFLINE'); return; }
  data.products.edges.forEach(e => PRODUCTS[e.node.handle] = e.node);
  renderGrid('gridMen', MEN_HANDLES, 'men');
  renderGrid('gridWomen', WOMEN_HANDLES, 'women');
  renderFeatured();
  observeReveals();
  if (cartId) renderCart(await ensureCart());
}

/* ---- Product cards: BACK design is the hero ---- */
function renderGrid(elId, handles, g) {
  const grid = document.getElementById(elId);
  grid.innerHTML = '';
  handles.forEach((h, idx) => {
    const p = PRODUCTS[h];
    if (!p) return;
    const colors = p.options.find(o=>o.name==='Color')?.values || [];
    const price = p.variants.edges[0].node.price.amount;
    let activeColor = colors.includes('Black') ? 'Black' : colors[0];

    const card = document.createElement('article');
    card.className = 'card';

    function build() {
      const back  = mockup(h, activeColor, 'back');
      const front = mockup(h, activeColor, 'front');
      card.innerHTML = `
        <div class="card__media card--mockup" data-color="${activeColor}">
          <img class="front back-hero" src="${back}" alt="${p.title} ${activeColor} back design" loading="${idx<3?'eager':'lazy'}">
          <img class="back" src="${front}" alt="${p.title} ${activeColor} front" loading="lazy">
          <span class="card__tag">${TAGLINES[h]||'FLYLYFE'}</span>
          <span class="card__view mono">BACK · HOVER FOR FRONT</span>
          <span class="card__quick mono">VIEW &amp; BUY →</span>
        </div>
        <div class="card__body">
          <div class="card__info">
            <div class="card__name">${p.title.replace(" — Women's","")}</div>
            <div class="card__sub">${SUBTITLE[h]||''}</div>
            <div class="card__colors">
              ${colors.map(c=>`<span class="dot${c===activeColor?' on':''}" data-color="${c}" title="${c}" style="background:${COLOR_HEX[c]||'#888'}"></span>`).join('')}
            </div>
          </div>
          <div class="card__price">${money(price)}</div>
        </div>`;

      card.querySelectorAll('.card__colors .dot').forEach(dot=>{
        dot.addEventListener('click', e=>{ e.stopPropagation(); activeColor=dot.dataset.color; build(); });
      });
      card.querySelector('.card__media').addEventListener('click', ()=>openPDP(h, activeColor));
      card.querySelector('.card__body').addEventListener('click', ()=>openPDP(h, activeColor));
    }
    build();
    grid.appendChild(card);
  });
}

/* ---- PDP: back hero + gallery (back, front, lifestyle), color-accurate ---- */
const pdp = document.getElementById('pdp');
let pdpState = { handle:null, color:null, size:null };

function openPDP(handle, startColor) {
  const p = PRODUCTS[handle];
  if (!p) return;
  const colors = p.options.find(o=>o.name==='Color')?.values || [];
  const sizes  = p.options.find(o=>o.name==='Size')?.values  || [];
  pdpState = { handle, color: startColor || (colors.includes('Black')?'Black':colors[0]), size:null };

  function render() {
    const back  = mockup(handle, pdpState.color, 'back');
    const front = mockup(handle, pdpState.color, 'front');
    const lifestyle = LIFESTYLE[handle] || [];
    const price = p.variants.edges[0].node.price.amount;

    document.getElementById('pdpTitle').textContent = p.title;
    document.getElementById('pdpPrice').textContent = money(price);
    document.getElementById('pdpDesc').innerHTML = p.descriptionHtml;
    document.getElementById('pdpColorName').textContent = pdpState.color.toUpperCase();

    /* Gallery: BACK first (hero), then front, then lifestyle shots */
    const gallery = [
      {url:back,  label:'BACK'},
      {url:front, label:'FRONT'},
      ...lifestyle.map(u=>({url:u, label:'WORN'}))
    ].filter(x=>x.url);

    const mainImg = document.getElementById('pdpMain');
    function setMain(url){ mainImg.classList.add('switching'); setTimeout(()=>{ mainImg.src=url; mainImg.classList.remove('switching'); },180); }
    setMain(gallery[0].url);

    const thumbs = document.getElementById('pdpThumbs');
    thumbs.innerHTML = '';
    gallery.forEach((im,i)=>{
      const t=document.createElement('img');
      t.src=im.url; t.alt=im.label; t.className='pdp__thumb'+(i===0?' on':'');
      t.onclick=()=>{ setMain(im.url); thumbs.querySelectorAll('.pdp__thumb').forEach(x=>x.classList.remove('on')); t.classList.add('on'); };
      thumbs.appendChild(t);
    });

    /* Swatches */
    const sw=document.getElementById('pdpSwatches');
    sw.innerHTML='';
    colors.forEach(c=>{
      const b=document.createElement('button');
      b.className='pdp__swatch'+(c===pdpState.color?' on':'');
      b.style.background=COLOR_HEX[c]||'#888'; b.title=c; b.setAttribute('aria-label',c);
      b.onclick=()=>{ pdpState.color=c; pdpState.size=null; render(); };
      sw.appendChild(b);
    });

    /* Sizes */
    const sz=document.getElementById('pdpSizes');
    sz.innerHTML='';
    sizes.forEach(s=>{
      const v=findVariant(p,pdpState.color,s);
      const b=document.createElement('button');
      const avail=v&&v.availableForSale;
      b.className='pdp__size'+(pdpState.size===s?' on':'')+(avail?'':' off');
      b.textContent=s;
      if(avail) b.onclick=()=>{ pdpState.size=s; sz.querySelectorAll('.pdp__size').forEach(x=>x.classList.remove('on')); b.classList.add('on'); updateATC(); };
      sz.appendChild(b);
    });
    updateATC();
  }

  function updateATC(){
    const atc=document.getElementById('pdpATC');
    if(pdpState.size){ atc.textContent='ADD TO CART · '+document.getElementById('pdpPrice').textContent; atc.classList.remove('pdp__atc--wait'); }
    else { atc.textContent='SELECT A SIZE'; atc.classList.add('pdp__atc--wait'); }
  }

  render();
  pdp.hidden=false;
  pdp.scrollTop=0;
  document.body.style.overflow='hidden';
}
function closePDP(){ pdp.hidden=true; document.body.style.overflow=''; }
document.getElementById('pdpBack').onclick=closePDP;
document.addEventListener('keydown',e=>{ if(e.key==='Escape'){ closePDP(); closeCart(); } });

document.getElementById('pdpATC').onclick=async()=>{
  if(!pdpState.size){ document.getElementById('pdpSizes').classList.add('shake'); setTimeout(()=>document.getElementById('pdpSizes').classList.remove('shake'),500); showToast('PICK A SIZE FIRST'); return; }
  const p=PRODUCTS[pdpState.handle];
  const v=findVariant(p,pdpState.color,pdpState.size);
  if(!v){ showToast('UNAVAILABLE'); return; }
  const atc=document.getElementById('pdpATC');
  atc.disabled=true; atc.textContent='ADDING…';
  await addToCart(v.id);
  atc.disabled=false;
  closePDP();
  openCart();
};

/* ---- Cart ---- */
const CART_FIELDS = `id checkoutUrl totalQuantity
  cost{ subtotalAmount{ amount } }
  lines(first:30){ edges{ node{ id quantity
    merchandise{ ... on ProductVariant{ id title price{ amount }
      product{ title handle } selectedOptions{ name value } } } } } }`;

async function ensureCart(){
  if(cartId){ const d=await gql(`query($id:ID!){ cart(id:$id){ ${CART_FIELDS} } }`,{id:cartId}); if(d?.cart) return d.cart; }
  const d=await gql(`mutation{ cartCreate{ cart{ ${CART_FIELDS} } } }`);
  const cart=d.cartCreate.cart; cartId=cart.id; localStorage.setItem('flylyfe_cart',cartId); return cart;
}
async function addToCart(vid){
  await ensureCart();
  const d=await gql(`mutation($cid:ID!,$lines:[CartLineInput!]!){ cartLinesAdd(cartId:$cid,lines:$lines){ cart{ ${CART_FIELDS} } } }`,{cid:cartId,lines:[{merchandiseId:vid,quantity:1}]});
  renderCart(d.cartLinesAdd.cart);
}
async function updateLine(id,qty){
  const d=await gql(`mutation($cid:ID!,$lines:[CartLineUpdateInput!]!){ cartLinesUpdate(cartId:$cid,lines:$lines){ cart{ ${CART_FIELDS} } } }`,{cid:cartId,lines:[{id,quantity:qty}]});
  renderCart(d.cartLinesUpdate.cart);
}

let CURRENT_CART=null;
function renderCart(cart){
  CURRENT_CART=cart;
  document.getElementById('cartCount').textContent=cart.totalQuantity;
  document.getElementById('cartTotal').textContent=money(cart.cost.subtotalAmount.amount);
  document.getElementById('checkoutBtn').textContent = cart.totalQuantity>0 ? `CHECKOUT · ${money(cart.cost.subtotalAmount.amount)} →` : 'CHECKOUT →';
  const wrap=document.getElementById('cartItems');
  const lines=cart.lines.edges;
  if(!lines.length){ wrap.innerHTML='<p class="drawer__empty mono">YOUR CART IS EMPTY.<br>GO FEEL SOMETHING.</p>'; return; }
  wrap.innerHTML='';
  lines.forEach(e=>{
    const l=e.node,m=l.merchandise;
    const opts=m.selectedOptions.map(o=>o.value).join(' / ');
    const colorOpt=m.selectedOptions.find(o=>o.name==='Color');
    const img=mockup(m.product.handle, colorOpt?colorOpt.value:'Black','back');
    const div=document.createElement('div');
    div.className='citem';
    div.innerHTML=`
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
    div.querySelectorAll('[data-d]').forEach(b=>b.onclick=()=>updateLine(l.id,l.quantity+parseInt(b.dataset.d)));
    div.querySelector('.citem__rm').onclick=()=>updateLine(l.id,0);
    wrap.appendChild(div);
  });
}

const drawer=document.getElementById('drawer');
async function openCart(){ drawer.hidden=false; document.body.style.overflow='hidden'; renderCart(await ensureCart()); }
function closeCart(){ drawer.hidden=true; document.body.style.overflow=''; }
document.getElementById('cartBtn').onclick=openCart;
document.querySelectorAll('[data-closecart]').forEach(el=>el.onclick=closeCart);
document.getElementById('checkoutBtn').onclick=()=>{ if(CURRENT_CART?.totalQuantity>0) window.location.href=CURRENT_CART.checkoutUrl; else showToast('CART IS EMPTY'); };

/* ---- Featured AFTER HOURS: back designs ---- */
function renderFeatured(){
  const strip=document.getElementById('featuredStrip');
  if(!strip) return;
  const picks=[
    {handle:'the-anthem-tee-womens',color:'Black'},
    {handle:'the-conga-tee',color:'Ivory'},
    {handle:'the-signature-tee',color:'Black'},
    {handle:'the-conga-tee-womens',color:'Natural'},
  ];
  strip.innerHTML='';
  picks.forEach(pk=>{
    const p=PRODUCTS[pk.handle]; if(!p) return;
    const img=mockup(pk.handle,pk.color,'back');
    const price=p.variants.edges[0].node.price.amount;
    const cell=document.createElement('div');
    cell.className='fcell fcell--mockup';
    cell.innerHTML=`<img src="${img}" alt="${p.title}" loading="lazy">
      <div class="fcell__label"><div class="nm">${p.title.replace(" — Women's","")}</div><div class="pr mono">${money(price)}</div></div>`;
    cell.onclick=()=>openPDP(pk.handle,pk.color);
    strip.appendChild(cell);
  });
}

/* ---- Utils ---- */
function findVariant(p,color,size){
  return p.variants.edges.map(e=>e.node).find(v=>{
    const so=Object.fromEntries(v.selectedOptions.map(o=>[o.name,o.value]));
    return so.Color===color && so.Size===size;
  });
}
let toastTimer;
function showToast(msg){ const t=document.getElementById('toast'); t.textContent=msg; t.hidden=false; clearTimeout(toastTimer); toastTimer=setTimeout(()=>t.hidden=true,2200); }

/* ---- Hero carousel: real model BACK shots (the attraction) ---- */
const HERO_SLIDES=[
  {img:'assets/models/black-back.jpg',    alt:'FLYLYFE Anthem Tee back'},
  {img:'assets/models/cream-back.jpg',     alt:'FLYLYFE House Music Is Freedom tee'},
  {img:'assets/models/cream-alt-back.jpg', alt:'FLYLYFE spiritual thing tee'},
];
function initHeroCarousel(){
  const wrap=document.getElementById('heroCarousel');
  const numsWrap=document.getElementById('heroNums');
  if(!wrap) return;
  HERO_SLIDES.forEach((s,i)=>{
    const slide=document.createElement('div');
    slide.className='hero__slide'+(i===0?' on':'');
    slide.innerHTML=`<img src="${s.img}" alt="${s.alt}" ${i===0?'fetchpriority="high"':'loading="lazy"'}>`;
    wrap.appendChild(slide);
    const num=document.createElement('button');
    num.className='hero__num'+(i===0?' on':''); num.textContent='0'+(i+1);
    num.setAttribute('aria-label','Slide '+(i+1)); num.onclick=()=>goToSlide(i);
    numsWrap.appendChild(num);
  });
  let idx=0;
  const slides=wrap.querySelectorAll('.hero__slide');
  const nums=numsWrap.querySelectorAll('.hero__num');
  window.goToSlide=n=>{ slides[idx].classList.remove('on'); nums[idx].classList.remove('on'); idx=(n+slides.length)%slides.length; slides[idx].classList.add('on'); nums[idx].classList.add('on'); };
  let timer=setInterval(()=>goToSlide(idx+1),4500);
  wrap.addEventListener('mouseenter',()=>clearInterval(timer));
  wrap.addEventListener('mouseleave',()=>{ timer=setInterval(()=>goToSlide(idx+1),4500); });
}

function initScrollUX(){
  const nav=document.getElementById('nav');
  const heroBg=document.getElementById('heroBg');
  const links=document.querySelectorAll('.nav__links a');
  const sections=['top','shop','after-hours','story','journal'];
  const onScroll=()=>{
    const y=window.scrollY;
    nav.classList.toggle('shrink',y>60);
    if(heroBg&&y<window.innerHeight) heroBg.style.transform=`translateY(${y*.18}px)`;
    let active='top';
    sections.forEach(id=>{ const el=document.getElementById(id); if(el&&el.getBoundingClientRect().top<=120) active=id; });
    links.forEach(a=>a.classList.toggle('active',a.getAttribute('href')==='#'+active));
  };
  window.addEventListener('scroll',onScroll,{passive:true}); onScroll();
}

function observeReveals(){
  if(!('IntersectionObserver' in window)){ document.querySelectorAll('.reveal').forEach(el=>el.classList.add('in')); return; }
  const io=new IntersectionObserver(es=>es.forEach(e=>{ if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target);} }),{threshold:.08,rootMargin:'0px 0px -40px 0px'});
  document.querySelectorAll('.reveal:not(.in)').forEach(el=>io.observe(el));
  setTimeout(()=>document.querySelectorAll('.reveal:not(.in)').forEach(el=>{ if(el.getBoundingClientRect().top<window.innerHeight) el.classList.add('in'); }),1200);
}

/* ---- Boot ---- */
document.body.classList.add('has-js');
document.getElementById('year').textContent=new Date().getFullYear();
initHeroCarousel();
initScrollUX();
observeReveals();
init();
