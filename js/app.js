/* ============ FLYLYFE — male model hero cards + popup modal PDP ============ */

const SHOP_DOMAIN = '31zn52-zd.myshopify.com';
const STOREFRONT_TOKEN = '5a0bb1dcf0c57b7764bbebf0cc40c898';
const API_URL = `https://${SHOP_DOMAIN}/api/2025-10/graphql.json`;

const COLOR_HEX = {
  'White':'#f4f4f2', 'Black':'#1b1b1c',
  'Ivory':'#f1e8d2', 'Natural':'#fff7e9'
};

/* ---- Male model images per color: back (hero) + front (hover) ---- */
const MODEL_SHOTS = {
  Black:   { back:'assets/models/black-back.jpg',     front:'assets/models/black-front.jpg'    },
  White:   { back:'assets/models/white-back.jpg',     front:'assets/models/white-front.jpg'    },
  Ivory:   { back:'assets/models/cream-back.jpg',     front:'assets/models/cream-front.jpg'    },
  Natural: { back:'assets/models/cream-alt-back.jpg', front:'assets/models/cream-alt-front.jpg'}
};

/* ---- Approved male model direction: the curly-haired NYC model used on Conga, Signature, and Drop 02.
   Product cards and PDP color changes should keep this model visible. If an exact product/color
   model shot does not exist yet, fall back to the same model wearing the selected color, then show
   accurate Printful mockups as proof thumbnails in the PDP. */
const APPROVED_MODEL_SHOTS = {
  Black:   { back:'assets/models/black-back.jpg',     front:'assets/models/black-front.jpg'    },
  White:   { back:'assets/models/white-back.jpg',     front:'assets/models/white-front.jpg'    },
  Ivory:   { back:'assets/models/cream-back.jpg',     front:'assets/models/cream-front.jpg'    },
  Natural: { back:'assets/models/cream-alt-back.jpg', front:'assets/models/cream-alt-front.jpg'}
};

const PRODUCT_MODEL_SHOTS = {
  'the-anthem-tee': {
    Black: { back:'assets/models/black-back.jpg', front:'assets/models/black-front.jpg', exact:true },
    White: { back:'assets/models/white-back.jpg', front:'assets/models/white-front.jpg', exact:true },
    Ivory: { back:'assets/models/cream-back.jpg', front:'assets/models/cream-front.jpg', exact:false }
  },
  'the-conga-tee': {
    /* Only use exact Conga imagery for Black. Do not show the generic plain front model here — it makes the Conga Tee look blank. */
    Black: { back:'assets/products/the-conga-tee-model-back.jpg', front:null, exact:true },
    White: { back:'assets/models/white-back.jpg', front:'assets/models/white-front.jpg', exact:false },
    Ivory: { back:'assets/models/cream-back.jpg', front:'assets/models/cream-front.jpg', exact:false }
  },
  'the-signature-tee': {
    Black: { back:'assets/products/the-signature-tee-model-back.jpg', front:'assets/models/black-front.jpg', exact:true },
    White: { back:'assets/models/white-back.jpg', front:'assets/models/white-front.jpg', exact:false },
    Ivory: { back:'assets/models/cream-back.jpg', front:'assets/models/cream-front.jpg', exact:false }
  },
  'the-house-music-tee': {
    Black: { back:'assets/products/generated/the-house-music-tee-Black-back-matched-mockup.jpg', front:'assets/products/generated/the-house-music-tee-Black-front-matched-mockup.jpg', exact:false },
    Ivory: { back:'assets/models/cream-alt-back.jpg', front:'assets/models/cream-alt-front.jpg', exact:true }
  },
  'the-after-hours-tee': {
    Black: { back:'assets/products/drop02-after-hours-model.jpg', front:null, exact:true }
  },
  'the-tempo-tee': {
    Black: { back:'assets/products/drop02-tempo-model.jpg', front:null, exact:true }
  },
  'the-coordinates-tee': {
    Ivory: { back:'assets/products/drop02-coordinates-model.jpg', front:null, exact:true }
  },
  'the-spiritual-thing-tee': {
    Ivory: { back:'assets/products/drop02-spiritual-thing-model.jpg', front:null, exact:true }
  },
  'the-sanitary-code-tee': {
    White: { back:'assets/products/limited-sanitary-back.jpg', front:'assets/products/limited-sanitary-front-model.jpg', exact:true }
  },
  'the-token-tee': {
    Ivory: { back:'assets/products/the-token-tee-model-back.jpg', front:'assets/products/the-token-tee-model-front.jpg', exact:true }
  },
  'the-anthem-tee-womens':    { Black: { back:'assets/lookbook/wren-feelmusic-back.jpg', front:'assets/lookbook/wren-black-front.jpg', exact:true } },
  'the-conga-tee-womens':     { Black: { back:'assets/lookbook/wren-conga-back.jpg', front:'assets/lookbook/wren-black-front.jpg', exact:true } },
  'the-signature-tee-womens': { Black: { back:'assets/lookbook/wren-black-front.jpg', front:'assets/lookbook/wren-cream-front.jpg', exact:true } }
};

/* Legacy aliases kept for fallback/helper compatibility. */
const MODEL_MAP = Object.fromEntries(Object.entries(PRODUCT_MODEL_SHOTS).map(([handle, colors]) => {
  const first = Object.entries(colors)[0];
  return [handle, { color:first[0], back:first[1].back, front:first[1].front }];
}));

/* Accurate Printful mockups — used as thumbnails in the modal */
let MOCKUPS = {};

/* Per-product default colorway shown on the card hero (overrides the Black default) */
const DEFAULT_COLOR = { 'the-house-music-tee':'Ivory', 'the-token-tee':'Ivory' };
/* Consistent on-model shots (assets/products-model/) are now the primary visual for EVERY product
   and color — same curly-haired man on all men's colors, same long-haired woman on all women's
   colors, front + back. Flat Printful mockups are no longer used as the primary card image. */
const MOCKUP_PRIMARY_HANDLES = new Set([]);
/* Front-logo products lead with the FRONT view; back-graphic tees lead with the BACK (the hero print). */
const FRONT_PRIMARY_HANDLES = new Set(['the-signature-tee','the-signature-tee-womens','the-sanitary-code-tee']);
const MEN_HANDLES = ['the-anthem-tee','the-conga-tee','the-signature-tee','the-house-music-tee','the-token-tee'];
const WOMEN_HANDLES = ['the-anthem-tee-womens','the-conga-tee-womens','the-signature-tee-womens'];
const DROP_HANDLES = ['the-after-hours-tee','the-tempo-tee','the-coordinates-tee','the-spiritual-thing-tee'];
const LIMITED_HANDLE = 'the-sanitary-code-tee';
const TAGLINES = {
  'the-anthem-tee':'FEEL THE MUSIC','the-conga-tee':'MOVE THE BODY','the-signature-tee':'THE CLASSIC','the-house-music-tee':'HOUSE MUSIC',
  'the-anthem-tee-womens':'FEEL THE MUSIC','the-conga-tee-womens':'MOVE THE BODY','the-signature-tee-womens':'THE CLASSIC',
  'the-after-hours-tee':'AFTER HOURS','the-tempo-tee':'124 BPM','the-coordinates-tee':'NEW YORK CITY','the-spiritual-thing-tee':'SPIRITUAL THING','the-sanitary-code-tee':'LIMITED',
  'the-token-tee':'NYC TOKEN'
};
const SUBTITLE = {
  'the-anthem-tee':'The mantra, worn big on the back',
  'the-conga-tee':'Dancer & conga — the rhythm on your back',
  'the-signature-tee':'Clean FLYLYFE wordmark',
  'the-house-music-tee':'Not everyone understands · front & back',
  'the-anthem-tee-womens':'The mantra, relaxed cut',
  'the-conga-tee-womens':'Dancer & conga, relaxed cut',
  'the-signature-tee-womens':'Clean wordmark, relaxed cut',
  'the-after-hours-tee':'The set that never stops',
  'the-tempo-tee':'124 BPM · the tempo of the city',
  'the-coordinates-tee':'40.7128° N · New York City',
  'the-spiritual-thing-tee':'A body thing · a soul thing',
  'the-sanitary-code-tee':'Vintage NYC · Sanitary Code Sect. 216',
  'the-token-tee':'NYC subway token · bronze back print',
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

const PRODUCT_Q = `{ products(first:50){ edges{ node{
  id handle title descriptionHtml
  featuredImage{ url }
  options{ name values }
  variants(first:50){ edges{ node{
    id title availableForSale price{ amount currencyCode }
    image{ url }
    selectedOptions{ name value }
  } } }
} } } }`;

let PRODUCTS = {};
let cartId = localStorage.getItem('flylyfe_cart');

function money(a){ return '$' + parseFloat(a).toFixed(2); }

/* helper: mockup from manifest */
function mockup(handle, color, view) {
  const m = MOCKUPS[handle];
  if (!m || !m[color]) return '';
  const c = m[color];
  return (c && (c[view] || c.back || c.front)) || '';
}

/* approved model shot for a given color/view */
function modelShot(color, view) {
  const shots = APPROVED_MODEL_SHOTS[color] || APPROVED_MODEL_SHOTS['Black'];
  return shots[view] || shots.back;
}

function productModelShot(handle, color, view) {
  const byHandle = PRODUCT_MODEL_SHOTS[handle] || {};
  const shot = byHandle[color];
  if (shot && (shot[view] || shot.back || shot.front)) return shot;
  const fallback = modelShot(color, view);
  return fallback ? { back:modelShot(color, 'back'), front:modelShot(color, 'front'), exact:false } : null;
}

function modelUrl(handle, color, view) {
  const shot = (PRODUCT_MODEL_SHOTS[handle] || {})[color];
  if (!shot || !shot.exact) return '';
  return shot[view] || '';
}

/* live Shopify (Printful-synced) mockup for a given color — the ACTUAL printed garment.
   Used as a truthful fallback before generic model shots, so what's shown matches what prints
   (critical for women's White/Natural, which have no local model photo). */
function shopVarImg(p, color) {
  if (!p || !p.variants) return '';
  const v = p.variants.edges.map(e=>e.node).find(n=>{
    const c = n.selectedOptions.find(o=>o.name==='Color');
    return c && c.value===color && n.image && n.image.url;
  });
  return (v && v.image && v.image.url) || (p.featuredImage && p.featuredImage.url) || '';
}

async function init() {
  const [modelMan, data] = await Promise.all([
    fetch('assets/products-model/manifest.json').then(r=>r.json()).catch(()=>({})),
    gql(PRODUCT_Q)
  ]);
  MOCKUPS = modelMan;
  /* Wire the consistent on-model set as the EXACT, primary image for every product/color.
     Each color is the same model/pose/background with only the shirt color (and print) changing,
     so switching the color swatch swaps just the shirt — front + back both available. */
  Object.entries(modelMan).forEach(([handle, colors])=>{
    PRODUCT_MODEL_SHOTS[handle] = PRODUCT_MODEL_SHOTS[handle] || {};
    Object.entries(colors).forEach(([color, views])=>{
      PRODUCT_MODEL_SHOTS[handle][color] = {
        back:  views.back  || views.front || '',
        front: views.front || views.back  || '',
        exact: true
      };
    });
  });
  if (!data) { document.querySelectorAll('.grid__loading').forEach(e=>e.textContent='DROP TEMPORARILY OFFLINE'); return; }
  data.products.edges.forEach(e => PRODUCTS[e.node.handle] = e.node);
  renderGrid('gridMen', MEN_HANDLES, 'men');
  renderGrid('gridWomen', WOMEN_HANDLES, 'women');
  renderGrid('gridDrop', DROP_HANDLES, 'drop');
  wireLimited();
  renderFeatured();
  injectProductSchema();
  observeReveals();
  if (cartId) renderCart(await ensureCart());
}

/* ===== PRODUCT CARDS: male model images, back as hero, hover flips to front =====
   Color dot click → swaps to the model photo in that color */
function renderGrid(elId, handles) {
  const grid = document.getElementById(elId);
  grid.innerHTML = '';
  handles.forEach((h, idx) => {
    const p = PRODUCTS[h];
    if (!p) return;
    const colors = p.options.find(o=>o.name==='Color')?.values || [];
    const price = p.variants.edges[0].node.price.amount;
    let activeColor = DEFAULT_COLOR[h] || (colors.includes('Black') ? 'Black' : colors[0]);

    const card = document.createElement('article');
    card.className = 'card';

    function build() {
      /* Keep the approved curly-haired NYC model as the primary product visual for every color.
         Printful/mockup images remain secondary proof in PDP, not the main customer-facing card. */
      const mockupPrimary = MOCKUP_PRIMARY_HANDLES.has(h);
      const frontPrimary = FRONT_PRIMARY_HANDLES.has(h);
      const primaryView = frontPrimary ? 'front' : 'back';
      const secondaryView = frontPrimary ? 'back' : 'front';
      const heroBack  = mockupPrimary
        ? (mockup(h, activeColor, primaryView) || shopVarImg(p, activeColor) || mockup(h, activeColor, secondaryView))
        : (modelUrl(h, activeColor, primaryView) || mockup(h, activeColor, primaryView) || shopVarImg(p, activeColor) || mockup(h, activeColor, secondaryView));
      const heroFront = mockupPrimary
        ? (mockup(h, activeColor, secondaryView) || heroBack)
        : (modelUrl(h, activeColor, secondaryView) || mockup(h, activeColor, secondaryView) || heroBack);
      const mediaCls  = mockupPrimary ? 'card__media card__media--mockup' : 'card__media card__media--model';
      const viewLabel = frontPrimary ? 'FRONT · HOVER FOR BACK' : 'BACK · HOVER FOR FRONT';
      card.innerHTML = `
        <div class="${mediaCls}" data-color="${activeColor}" role="button" tabindex="0" aria-label="View ${p.title.replace(" — Women's","")}">
          <img class="front back-hero" src="${heroBack}" alt="${p.title} — ${activeColor}, ${mockupPrimary ? 'front logo' : 'worn back'}" loading="lazy" decoding="async">
          <img class="back" src="${heroFront}" alt="${p.title} — ${activeColor}, ${mockupPrimary ? 'back view' : 'worn front'}" loading="lazy" decoding="async">
          <span class="card__tag">${TAGLINES[h]||'FLYLYFE'}</span>
          <span class="card__view mono">${viewLabel}</span>
          <span class="card__quick mono">VIEW &amp; BUY →</span>
        </div>
        <div class="card__body">
          <div class="card__info">
            <div class="card__name">${p.title.replace(" — Women's","")}</div>
            <div class="card__sub">${SUBTITLE[h]||''}</div>
            <div class="card__colors">
              ${colors.map(c=>`<button type="button" class="dot${c===activeColor?' on':''}" data-color="${c}" title="${c}" aria-label="${c}" aria-pressed="${c===activeColor}" style="background:${COLOR_HEX[c]||'#888'};padding:0"></button>`).join('')}
            </div>
          </div>
          <div class="card__price">${money(price)}</div>
        </div>`;

      const media = card.querySelector('.card__media');
      media.addEventListener('click', ()=>openPDP(h, activeColor));
      media.addEventListener('keydown', e=>{ if(e.key==='Enter'||e.key===' '){ e.preventDefault(); openPDP(h, activeColor); } });
      card.querySelectorAll('.card__colors .dot').forEach(dot=>{
        dot.addEventListener('click', e=>{ e.stopPropagation(); activeColor = dot.dataset.color; build(); });
      });
      card.querySelector('.card__body').addEventListener('click', e=>{ if(!e.target.closest('.dot')) openPDP(h, activeColor); });
    }
    build();
    grid.appendChild(card);
  });
}

/* ===== POPUP MODAL PDP =====
   Gallery left: male model back (hero) + front thumbnails + printful mockup thumbnails
   Color swatch click → updates model photo + mockup thumbnails instantly */
const pdp = document.getElementById('pdp');
let pdpState = { handle:null, color:null, size:null };
let pdpReturnFocus = null;

function openPDP(handle, startColor) {
  const p = PRODUCTS[handle];
  if (!p) return;
  const colors = p.options.find(o=>o.name==='Color')?.values || [];
  const sizes  = p.options.find(o=>o.name==='Size')?.values  || [];
  pdpState = { handle, color: startColor || DEFAULT_COLOR[handle] || (colors.includes('Black')?'Black':colors[0]), size:null };

  function render() {
    const mockupPrimary = MOCKUP_PRIMARY_HANDLES.has(handle);
    const frontPrimary = FRONT_PRIMARY_HANDLES.has(handle);
    const modelShotForColor = mockupPrimary ? null : productModelShot(handle, pdpState.color, 'back');
    const sImg    = shopVarImg(p, pdpState.color);
    const mBack   = mockup(handle, pdpState.color, 'back');
    const mFront  = mockup(handle, pdpState.color, 'front');
    const back    = mockupPrimary ? (mBack || sImg) : (modelUrl(handle, pdpState.color, 'back') || mBack || sImg);
    const front   = mockupPrimary ? (mFront || sImg || back) : (modelUrl(handle, pdpState.color, 'front') || mFront || sImg || back);
    const price = p.variants.edges[0].node.price.amount;

    document.getElementById('pdpTitle').textContent = p.title;
    document.getElementById('pdpPrice').textContent = money(price);
    document.getElementById('pdpDesc').innerHTML = p.descriptionHtml;
    document.getElementById('pdpColorName').textContent = pdpState.color.toUpperCase();

    /* Gallery order: front-logo products show the accurate product front first; other tees keep model back first. */
    const _seen = new Set();
    const gallery = (frontPrimary ? [
      { url:front, label:'FRONT', isModel:!mockupPrimary && !!modelUrl(handle, pdpState.color, 'front') },
      { url:back,  label:'BACK',  isModel:!mockupPrimary && !!modelUrl(handle, pdpState.color, 'back') }
    ] : [
      { url:back,   label:modelShotForColor?.exact ? 'BACK — WORN' : 'BACK',  isModel: !!modelUrl(handle, pdpState.color, 'back') },
      { url:front,  label:modelShotForColor?.exact ? 'FRONT — WORN' : 'FRONT', isModel: !!modelUrl(handle, pdpState.color, 'front') },
      ...(mBack  ? [{url:mBack,  label:'BACK',  isModel:false}]  : []),
      ...(mFront ? [{url:mFront, label:'FRONT', isModel:false}] : [])
    ]).filter(x=>x.url && !_seen.has(x.url) && _seen.add(x.url));

    const mainImg = document.getElementById('pdpMain');
    function pdpImagePosition(url, isModel){
      /* On phones the PDP gallery is short; center model BACK photos around the shirt print
         instead of the model's head so the artwork is immediately visible. */
      if (!isModel) return 'center';
      const u = url || '';
      if (u.includes('-back.jpg') || u.includes('/black-back.jpg') || u.includes('/white-back.jpg') || u.includes('/cream-back.jpg') || u.includes('/cream-alt-back.jpg')) return 'center 42%';
      return 'top center';
    }
    function setMain(url, isModel, alt){
      mainImg.classList.add('switching');
      setTimeout(()=>{
        mainImg.src = url;
        if(alt) mainImg.alt = alt;
        mainImg.style.objectFit   = isModel ? 'cover'    : 'contain';
        mainImg.style.objectPosition = pdpImagePosition(url, isModel);
        mainImg.classList.remove('switching');
      }, 180);
    }
    setMain(gallery[0].url, gallery[0].isModel, `${p.title} — ${gallery[0].label}`);

    const thumbs = document.getElementById('pdpThumbs');
    thumbs.innerHTML = '';
    gallery.forEach((im, i)=>{
      const t = document.createElement('img');
      t.src = im.url; t.alt = im.label;
      t.className = 'pdp__thumb' + (i===0?' on':'');
      t.style.objectFit = im.isModel ? 'cover' : 'contain';
      t.style.objectPosition = im.isModel ? 'top center' : 'center';
      t.onclick = ()=>{
        setMain(im.url, im.isModel, `${p.title} — ${im.label}`);
        thumbs.querySelectorAll('.pdp__thumb').forEach(x=>x.classList.remove('on'));
        t.classList.add('on');
      };
      thumbs.appendChild(t);
    });

    /* Color swatches */
    const sw = document.getElementById('pdpSwatches');
    sw.innerHTML = '';
    colors.forEach(c=>{
      const b = document.createElement('button');
      b.className = 'pdp__swatch' + (c===pdpState.color?' on':'');
      b.style.background = COLOR_HEX[c]||'#888';
      b.title = c;
      b.setAttribute('aria-label', c);
      b.onclick = ()=>{ pdpState.color = c; pdpState.size = null; render(); };
      sw.appendChild(b);
    });

    /* Size buttons */
    const sz = document.getElementById('pdpSizes');
    sz.innerHTML = '';
    sizes.forEach(s=>{
      const v = findVariant(p, pdpState.color, s);
      const b = document.createElement('button');
      const avail = v && v.availableForSale;
      b.className = 'pdp__size' + (pdpState.size===s?' on':'') + (avail?'':' off');
      b.textContent = s;
      if (!avail){ b.disabled = true; b.setAttribute('aria-disabled','true'); b.setAttribute('aria-label', s+', sold out'); }
      if (avail) b.onclick = ()=>{
        pdpState.size = s;
        sz.querySelectorAll('.pdp__size').forEach(x=>x.classList.remove('on'));
        b.classList.add('on');
        updateATC();
      };
      sz.appendChild(b);
    });
    updateATC();
  }

  function updateATC(){
    const atc = document.getElementById('pdpATC');
    if (pdpState.size){
      atc.textContent = 'ADD TO CART · ' + document.getElementById('pdpPrice').textContent;
      atc.classList.remove('pdp__atc--wait');
    } else {
      atc.textContent = 'SELECT A SIZE';
      atc.classList.add('pdp__atc--wait');
    }
  }

  render();
  pdpReturnFocus = document.activeElement;
  pdp.hidden = false;
  document.body.style.overflow = 'hidden';
  setTimeout(()=>{ const b=document.getElementById('pdpBack'); if(b) b.focus(); }, 50);
}

function closePDP(){ pdp.hidden = true; document.body.style.overflow = ''; if(pdpReturnFocus){ try{pdpReturnFocus.focus();}catch(_){} pdpReturnFocus=null; } }

document.getElementById('pdpBack').onclick = closePDP;
/* click the dark backdrop behind the modal box closes it */
document.getElementById('pdpBackdrop').onclick = closePDP;
/* Escape + focus-trap handled globally in the a11y block below */

document.getElementById('pdpATC').onclick = async()=>{
  if (!pdpState.size){
    document.getElementById('pdpSizes').classList.add('shake');
    setTimeout(()=>document.getElementById('pdpSizes').classList.remove('shake'), 500);
    showToast('PICK A SIZE FIRST'); return;
  }
  const p = PRODUCTS[pdpState.handle];
  const v = findVariant(p, pdpState.color, pdpState.size);
  if (!v){ showToast('UNAVAILABLE'); return; }
  const atc = document.getElementById('pdpATC');
  atc.disabled = true; atc.textContent = 'ADDING…';
  try {
    await addToCart(v.id);
    closePDP();
    openCart();
  } catch (err) {
    console.error('ATC:', err);
    showToast('CART ERROR — TRY AGAIN');
  } finally {
    atc.disabled = false;
    if (!pdp.hidden) atc.textContent = 'ADD TO CART · ' + document.getElementById('pdpPrice').textContent;
  }
};

/* ---- Cart ---- */
const CART_FIELDS = `id checkoutUrl totalQuantity
  cost{ subtotalAmount{ amount } }
  lines(first:30){ edges{ node{ id quantity
    merchandise{ ... on ProductVariant{ id title price{ amount }
      product{ title handle } selectedOptions{ name value } } } } } }`;

async function ensureCart(){
  if (cartId){ const d = await gql(`query($id:ID!){ cart(id:$id){ ${CART_FIELDS} } }`,{id:cartId}); if(d?.cart) return d.cart; }
  const d = await gql(`mutation{ cartCreate{ cart{ ${CART_FIELDS} } } }`);
  const cart = d.cartCreate.cart; cartId = cart.id; localStorage.setItem('flylyfe_cart', cartId); return cart;
}
async function addToCart(vid){
  await ensureCart();
  const d = await gql(`mutation($cid:ID!,$lines:[CartLineInput!]!){ cartLinesAdd(cartId:$cid,lines:$lines){ cart{ ${CART_FIELDS} } } }`,{cid:cartId,lines:[{merchandiseId:vid,quantity:1}]});
  renderCart(d.cartLinesAdd.cart);
}
async function updateLine(id, qty){
  const d = await gql(`mutation($cid:ID!,$lines:[CartLineUpdateInput!]!){ cartLinesUpdate(cartId:$cid,lines:$lines){ cart{ ${CART_FIELDS} } } }`,{cid:cartId,lines:[{id,quantity:qty}]});
  renderCart(d.cartLinesUpdate.cart);
}

let CURRENT_CART = null;
function renderCart(cart){
  CURRENT_CART = cart;
  document.getElementById('cartCount').textContent = cart.totalQuantity;
  document.getElementById('cartTotal').textContent = money(cart.cost.subtotalAmount.amount);
  document.getElementById('checkoutBtn').textContent = cart.totalQuantity>0 ? `CHECKOUT · ${money(cart.cost.subtotalAmount.amount)} →` : 'CHECKOUT →';
  const wrap = document.getElementById('cartItems');
  const lines = cart.lines.edges;
  if (!lines.length){ wrap.innerHTML='<p class="drawer__empty mono">YOUR CART IS EMPTY.<br>GO FEEL SOMETHING.</p>'; return; }
  wrap.innerHTML = '';
  lines.forEach(e=>{
    const l = e.node, m = l.merchandise;
    const opts = m.selectedOptions.map(o=>o.value).join(' / ');
    const colorOpt = m.selectedOptions.find(o=>o.name==='Color');
    const cc = colorOpt ? colorOpt.value : 'Black';
    const img = modelUrl(m.product.handle, cc, 'back') || mockup(m.product.handle, cc, 'back') || shopVarImg(PRODUCTS[m.product.handle], cc);
    const div = document.createElement('div');
    div.className = 'citem';
    div.innerHTML = `
      <img src="${img}" alt="${m.product.title}" loading="lazy" style="object-fit:contain;background:#0d0d0d;">
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
    div.querySelector('.citem__rm').onclick = ()=>updateLine(l.id, 0);
    wrap.appendChild(div);
  });
}

const drawer = document.getElementById('drawer');
let cartReturnFocus = null;
async function openCart(){ cartReturnFocus=document.activeElement; drawer.hidden=false; document.body.style.overflow='hidden'; renderCart(await ensureCart()); setTimeout(()=>{ const c=drawer.querySelector('[data-closecart]'); if(c) c.focus(); }, 50); }
function closeCart(){ drawer.hidden=true; document.body.style.overflow=''; if(cartReturnFocus){ try{cartReturnFocus.focus();}catch(_){} cartReturnFocus=null; } }
document.getElementById('cartBtn').onclick = openCart;
document.querySelectorAll('[data-closecart]').forEach(el=>el.onclick=closeCart);
document.getElementById('checkoutBtn').onclick = ()=>{
  if (CURRENT_CART?.totalQuantity>0) window.location.href = CURRENT_CART.checkoutUrl;
  else showToast('CART IS EMPTY');
};

/* ---- Featured AFTER HOURS ---- */
function renderFeatured(){
  const strip = document.getElementById('featuredStrip');
  if (!strip) return;
  const picks = [
    {handle:'the-anthem-tee-womens',color:'Black'},
    {handle:'the-conga-tee',color:'Ivory'},
    {handle:'the-signature-tee',color:'Black'},
    {handle:'the-conga-tee-womens',color:'Natural'},
  ];
  strip.innerHTML = '';
  picks.forEach(pk=>{
    const p = PRODUCTS[pk.handle]; if (!p) return;
    const img = modelUrl(pk.handle, pk.color, 'back') || mockup(pk.handle, pk.color, 'back') || shopVarImg(p, pk.color);
    const price = p.variants.edges[0].node.price.amount;
    const cell = document.createElement('div');
    cell.className = 'fcell fcell--mockup';
    cell.innerHTML = `<img src="${img}" alt="${p.title}" loading="lazy">
      <div class="fcell__label"><div class="nm">${p.title.replace(" — Women's","")}</div><div class="pr mono">${money(price)}</div></div>`;
    const openCell = ()=>openPDP(pk.handle, pk.color);
    cell.onclick = openCell;
    cell.setAttribute('role','button'); cell.tabIndex = 0;
    cell.setAttribute('aria-label','View '+p.title.replace(" — Women's",""));
    cell.addEventListener('keydown', e=>{ if(e.key==='Enter'||e.key===' '){ e.preventDefault(); openCell(); } });
    strip.appendChild(cell);
  });
}

/* ---- Limited section → opens the Sanitary Code PDP (shoppable) ---- */
function wireLimited(){
  if (!PRODUCTS[LIMITED_HANDLE]) return;
  const open = ()=>openPDP(LIMITED_HANDLE, 'White');
  document.querySelectorAll('[data-shop-limited]').forEach(b=>b.addEventListener('click', open));
  const media = document.querySelector('#limited .limited__media');
  if (media){
    media.style.cursor='pointer'; media.setAttribute('role','button'); media.setAttribute('tabindex','0');
    media.setAttribute('aria-label','Shop the Sanitary Code Tee');
    media.addEventListener('click', open);
    media.addEventListener('keydown', e=>{ if(e.key==='Enter'||e.key===' '){ e.preventDefault(); open(); } });
  }
}

/* ---- Product structured data (SEO rich results) ---- */
function injectProductSchema(){
  const handles = MEN_HANDLES.concat(WOMEN_HANDLES, DROP_HANDLES, [LIMITED_HANDLE]);
  const items = handles.map(h=>PRODUCTS[h]).filter(Boolean).map(p=>{
    const v0 = p.variants.edges[0].node;
    const inStock = p.variants.edges.some(e=>e.node.availableForSale);
    const colors = (p.options.find(o=>o.name==='Color')?.values)||[];
    const img = modelUrl(p.handle, colors.includes('Black')?'Black':colors[0], 'back') || mockup(p.handle, colors.includes('Black')?'Black':colors[0], 'back') || '';
    const o = { "@context":"https://schema.org","@type":"Product","name":p.title,
      "description":(p.descriptionHtml||'').replace(/<[^>]+>/g,'').replace(/\s+/g,' ').trim().slice(0,300),
      "brand":{"@type":"Brand","name":"FLYLYFE"},
      "offers":{"@type":"Offer","price":parseFloat(v0.price.amount).toFixed(2),"priceCurrency":v0.price.currencyCode||"USD","availability":inStock?"https://schema.org/InStock":"https://schema.org/OutOfStock","url":"https://flylyfe.com/"} };
    if(img) o.image = ['https://flylyfe.com/'+img];
    return o;
  });
  if(!items.length) return;
  const s = document.createElement('script'); s.type='application/ld+json';
  s.textContent = JSON.stringify(items);
  document.head.appendChild(s);
}

/* ---- Utils ---- */
function findVariant(p, color, size){
  return p.variants.edges.map(e=>e.node).find(v=>{
    const so = Object.fromEntries(v.selectedOptions.map(o=>[o.name,o.value]));
    return so.Color===color && so.Size===size;
  });
}
let toastTimer;
function showToast(msg){ const t=document.getElementById('toast'); t.hidden=false; t.textContent=msg; clearTimeout(toastTimer); toastTimer=setTimeout(()=>{ t.hidden=true; t.textContent=''; },2200); }

/* ---- Hero carousel: model back shots ---- */
const HERO_SLIDES=[
  {img:'assets/hero/carousel-2-freedom.jpg', alt:'FLYLYFE — House Music Is Freedom tee on a New York City street'},
  {img:'assets/hero/carousel-1-black.jpg',   alt:'FLYLYFE — Feel the Music. Feel the Vibe. Live Your Lyfe. tee in NYC'},
  {img:'assets/hero/carousel-3-house.jpg',   alt:'FLYLYFE house music culture tee in New York City'},
];
function initHeroCarousel(){
  const wrap = document.getElementById('heroCarousel');
  const numsWrap = document.getElementById('heroNums');
  if (!wrap) return;
  HERO_SLIDES.forEach((s,i)=>{
    const slide = document.createElement('div');
    slide.className = 'hero__slide'+(i===0?' on':'');
    slide.innerHTML = `<img src="${s.img}" alt="${s.alt}" ${i===0?'fetchpriority="high"':'loading="lazy"'}>`;
    wrap.appendChild(slide);
    const num = document.createElement('button');
    num.className = 'hero__num'+(i===0?' on':'');
    num.textContent = '0'+(i+1);
    num.setAttribute('aria-label','Slide '+(i+1));
    num.onclick = ()=>goToSlide(i);
    numsWrap.appendChild(num);
  });
  let idx=0;
  const slides = wrap.querySelectorAll('.hero__slide');
  const nums   = numsWrap.querySelectorAll('.hero__num');
  window.goToSlide = n=>{
    slides[idx].classList.remove('on'); nums[idx].classList.remove('on');
    idx = (n+slides.length)%slides.length;
    slides[idx].classList.add('on'); nums[idx].classList.add('on');
  };
  const reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let timer = reduceMotion ? null : setInterval(()=>goToSlide(idx+1),4500);
  const stop  = ()=>clearInterval(timer);
  const start = ()=>{ if(!reduceMotion){ clearInterval(timer); timer=setInterval(()=>goToSlide(idx+1),4500); } };
  wrap.addEventListener('mouseenter',stop);
  wrap.addEventListener('mouseleave',start);
  wrap.addEventListener('focusin',stop);   /* pause when a control is focused */
  wrap.addEventListener('focusout',start);
}

function initScrollUX(){
  const nav = document.getElementById('nav');
  const heroBg = document.getElementById('heroBg');
  const links = document.querySelectorAll('.nav__links a');
  const sections = ['top','shop','after-hours','story','journal'];
  const reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let ticking = false;
  const onScroll = ()=>{
    const y = window.scrollY;
    nav.classList.toggle('shrink', y>60);
    if (!reduceMotion && heroBg && y<window.innerHeight && !ticking){
      ticking = true;
      requestAnimationFrame(()=>{ heroBg.style.transform=`translateY(${y*.18}px)`; ticking=false; });
    }
    let active='top';
    sections.forEach(id=>{ const el=document.getElementById(id); if(el&&el.getBoundingClientRect().top<=120) active=id; });
    links.forEach(a=>a.classList.toggle('active', a.getAttribute('href')==='#'+active));
  };
  window.addEventListener('scroll', onScroll, {passive:true}); onScroll();
}

function observeReveals(){
  if (!('IntersectionObserver' in window)){ document.querySelectorAll('.reveal').forEach(el=>el.classList.add('in')); return; }
  const io = new IntersectionObserver(es=>es.forEach(e=>{ if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target);} }),{threshold:.08,rootMargin:'0px 0px -40px 0px'});
  document.querySelectorAll('.reveal:not(.in)').forEach(el=>io.observe(el));
  setTimeout(()=>document.querySelectorAll('.reveal:not(.in)').forEach(el=>{ if(el.getBoundingClientRect().top<window.innerHeight) el.classList.add('in'); }),1200);
}

/* ================= a11y, mobile menu, info overlay, email capture ================= */

/* focus-trap helpers shared by every overlay */
function getFocusable(c){ return c ? [...c.querySelectorAll('a[href],button:not([disabled]),input:not([disabled]),select,textarea,[tabindex]:not([tabindex="-1"])')].filter(el=>el.offsetParent!==null) : []; }
function trapTab(c,e){ const f=getFocusable(c); if(!f.length) return; const first=f[0], last=f[f.length-1];
  if(e.shiftKey && document.activeElement===first){ e.preventDefault(); last.focus(); }
  else if(!e.shiftKey && document.activeElement===last){ e.preventDefault(); first.focus(); } }

/* ---- Mobile menu ---- */
const mobileMenu = document.getElementById('mobileMenu');
const navBurger  = document.getElementById('navBurger');
let menuReturnFocus = null;
function openMobileMenu(){ menuReturnFocus=document.activeElement; mobileMenu.hidden=false; navBurger.setAttribute('aria-expanded','true'); document.body.style.overflow='hidden'; setTimeout(()=>{ const a=mobileMenu.querySelector('a'); if(a) a.focus(); }, 50); }
function closeMobileMenu(){ mobileMenu.hidden=true; navBurger.setAttribute('aria-expanded','false'); document.body.style.overflow=''; if(menuReturnFocus){ try{menuReturnFocus.focus();}catch(_){} } }
if (navBurger) navBurger.onclick = ()=>{ mobileMenu.hidden ? openMobileMenu() : closeMobileMenu(); };
if (mobileMenu) mobileMenu.querySelectorAll('a').forEach(a=>a.addEventListener('click', closeMobileMenu));

/* ---- Info overlay: shipping / returns / size guide / policies ---- */
const info = document.getElementById('info');
const INFO = {
  shipping:{ title:'Shipping', html:`<p>Every FLYLYFE piece is printed-to-order in the USA.</p>
    <h4>Processing</h4><p>Orders are made and shipped within 3–5 business days.</p>
    <h4>Delivery</h4><p>US: 3–7 business days after processing. International: 10–20 business days. <strong>Free US shipping on orders over $75.</strong></p>
    <p>Tracking is emailed the moment your order ships.</p>` },
  returns:{ title:'Returns', html:`<p>We want you in the right fit.</p>
    <h4>30-Day Window</h4><p>Unworn, unwashed items with tags can be returned within 30 days of delivery.</p>
    <h4>How</h4><p>Email <a href="mailto:hello@flylyfe.com" style="color:var(--gold)">hello@flylyfe.com</a> with your order number and we'll send a label. Made-to-order pieces are eligible for exchange or store credit.</p>` },
  sizeguide:{ title:'Size Guide', html:`<p>Our heavyweight tees run true to size with a relaxed, slightly oversized drop. Between sizes? Size down for a classic fit.</p>
    <table><thead><tr><th>Size</th><th>Chest (in)</th><th>Length (in)</th></tr></thead><tbody>
    <tr><td>S</td><td>40</td><td>28</td></tr><tr><td>M</td><td>44</td><td>29</td></tr><tr><td>L</td><td>48</td><td>30</td></tr>
    <tr><td>XL</td><td>52</td><td>31</td></tr><tr><td>2XL</td><td>56</td><td>32</td></tr><tr><td>3XL</td><td>60</td><td>33</td></tr></tbody></table>
    <p>Measurements are approximate garment dimensions.</p>` },
  privacy:{ title:'Privacy', html:`<p>We collect only what's needed to process your order and send the updates you opt into. We never sell your data.</p>
    <p>Payments are handled securely by Shopify. Questions? <a href="mailto:hello@flylyfe.com" style="color:var(--gold)">hello@flylyfe.com</a>.</p>` },
  terms:{ title:'Terms', html:`<p>By using flylyfe.com you agree to our standard terms of sale. All artwork and the FLYLYFE name are property of FLYLYFE. Prices and availability may change without notice.</p>` }
};
let infoReturnFocus = null;
function openInfo(key){ const d=INFO[key]; if(!d) return; infoReturnFocus=document.activeElement;
  document.getElementById('infoTitle').textContent=d.title;
  document.getElementById('infoBody').innerHTML=d.html;
  info.hidden=false; document.body.style.overflow='hidden';
  setTimeout(()=>{ const b=info.querySelector('.info__close'); if(b) b.focus(); }, 50); }
function closeInfo(){ info.hidden=true;
  document.body.style.overflow = ((pdp&&!pdp.hidden)||(drawer&&!drawer.hidden)) ? 'hidden' : '';
  if(infoReturnFocus){ try{infoReturnFocus.focus();}catch(_){} } }
document.querySelectorAll('[data-info]').forEach(el=>el.addEventListener('click', e=>{ e.preventDefault(); openInfo(el.dataset.info); }));
if (info) info.querySelectorAll('[data-closeinfo]').forEach(el=>el.onclick=closeInfo);

/* drawer is a modal dialog */
const _drawerPanel = document.querySelector('.drawer__panel'); if(_drawerPanel) _drawerPanel.setAttribute('aria-modal','true');

/* ---- Global keyboard: Escape closes the top-most overlay; Tab is trapped inside it ---- */
document.addEventListener('keydown', e=>{
  if (e.key==='Escape'){
    if (info && !info.hidden) closeInfo();
    else if (pdp && !pdp.hidden) closePDP();
    else if (drawer && !drawer.hidden) closeCart();
    else if (mobileMenu && !mobileMenu.hidden) closeMobileMenu();
  } else if (e.key==='Tab'){
    if (info && !info.hidden) trapTab(info.querySelector('.info__panel'), e);
    else if (pdp && !pdp.hidden) trapTab(pdp.querySelector('.pdp__box'), e);
    else if (drawer && !drawer.hidden) trapTab(drawer.querySelector('.drawer__panel'), e);
    else if (mobileMenu && !mobileMenu.hidden) trapTab(mobileMenu, e);
  }
});

/* ---- Email / SMS capture (UI only) ----
   TODO: POST { email, phone } to your provider (Klaviyo / Shopify / Mailchimp) here. */
function initJoinForm(){
  const form = document.getElementById('joinForm'); if(!form) return;
  const msg = document.getElementById('joinMsg');
  form.addEventListener('submit', e=>{
    e.preventDefault();
    const email = (document.getElementById('joinEmail').value||'').trim();
    const phone = (document.getElementById('joinPhone').value||'').trim();
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)){ msg.textContent='ENTER A VALID EMAIL.'; msg.classList.add('err'); return; }
    msg.classList.remove('err');
    msg.textContent = "YOU'RE ON THE LIST — WELCOME TO FLYLYFE.";
    const signup = { email, phone };   /* captured payload */
    form.reset();
    /* TODO: forward `signup` ({ email, phone }) to your email/SMS backend (Klaviyo / Shopify / Mailchimp) */
  });
}
initJoinForm();

/* ---- Boot ---- */
document.body.classList.add('has-js');
document.getElementById('year').textContent = new Date().getFullYear();
initHeroCarousel();
initScrollUX();
observeReveals();
init();
