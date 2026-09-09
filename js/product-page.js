
// Shopify Storefront API identifiers are intentionally client-side.
// This is not an Admin API secret; it is scoped for public storefront cart/product operations only.
const SHOP_DOMAIN='31zn52-zd.myshopify.com';
const STOREFRONT_TOKEN='5a0bb1dcf0c57b7764bbebf0cc40c898';
const API_URL=`https://${SHOP_DOMAIN}/api/2025-10/graphql.json`;
const handle = document.body.dataset.productHandle;
const ES = document.documentElement.lang === 'es';
const T = ES ? {
  color:'COLOR', size:'TALLE', atc:'AGREGAR AL CARRITO', select:'ELEGÍ TU TALLE', checkout:'FINALIZAR COMPRA',
  adding:'AGREGANDO…', added:'AGREGADO AL CARRITO', selectAvail:'ELEGÍ UN TALLE DISPONIBLE',
  empty:'EL CARRITO ESTÁ VACÍO. AGREGÁ UNA REMERA PRIMERO.', error:'NO SE PUDO ACTUALIZAR EL CARRITO. PROBÁ DE NUEVO.',
  unavailable:'No pudimos cargar las opciones. Volvé a intentarlo.', retry:'REINTENTAR', front:'FRENTE', back:'DORSO',
  viewCart:'VER O EDITAR CARRITO', items:'artículos en el carrito', placement:'Las imágenes muestran el diseño y el color; la ubicación de la impresión puede variar ligeramente.'
} : {
  color:'COLOR', size:'SIZE', atc:'ADD TO CART', select:'SELECT SIZE', checkout:'CHECKOUT',
  adding:'ADDING…', added:'ADDED TO CART', selectAvail:'SELECT AN AVAILABLE SIZE',
  empty:'YOUR CART IS EMPTY. ADD A TEE FIRST.', error:'COULD NOT UPDATE YOUR CART. PLEASE TRY AGAIN.',
  unavailable:'We couldn’t load the options. Please try again.', retry:'TRY AGAIN', front:'FRONT', back:'BACK',
  viewCart:'VIEW OR EDIT CART', items:'items in your cart', placement:'Product mockups show the artwork and color; print placement may vary slightly.'
};
const FRONT_FIRST = new Set(['the-signature-tee','the-signature-tee-womens','the-sanitary-code-tee']);
let cartId = localStorage.getItem('flylyfe_cart');
let product = null, imageManifest = {}, currentCart = null, busy = false;
const state = {color:null, size:null, view:FRONT_FIRST.has(handle) ? 'front' : 'back'};
const root = document.querySelector('[data-commerce-root]');
const money = (a, currency='USD') => new Intl.NumberFormat(ES?'es-AR':'en-US', {style:'currency',currency}).format(Number(a));
const PRODUCT_Q = `query($handle:String!){product(handle:$handle){id handle title vendor descriptionHtml options{name values} featuredImage{url altText} variants(first:100){edges{node{id title availableForSale price{amount currencyCode} image{url altText} selectedOptions{name value}}}}}}`;
const CART_FIELDS = `id checkoutUrl totalQuantity cost{subtotalAmount{amount currencyCode}}`;
async function gql(query, variables={}) {
  const res = await fetch(API_URL,{method:'POST',headers:{'Content-Type':'application/json','X-Shopify-Storefront-Access-Token':STOREFRONT_TOKEN},body:JSON.stringify({query,variables})});
  if (!res.ok) throw new Error(`Shopify HTTP ${res.status}`);
  const result = await res.json();
  if (result.errors?.length) throw new Error(result.errors.map(e=>e.message).join('; '));
  if (!result.data) throw new Error('Missing Shopify response');
  for (const payload of Object.values(result.data)) {
    if (payload?.userErrors?.length) throw new Error(payload.userErrors.map(e=>e.message).join('; '));
  }
  return result.data;
}
const variants = () => product.variants.edges.map(e=>e.node);
const option = (v,name) => v.selectedOptions.find(o=>o.name===name)?.value;
const optionValues = name => product.options.find(o=>o.name===name)?.values || [];
function variant() { return variants().find(v=>option(v,'Color')===state.color && option(v,'Size')===state.size); }
function status(message) { const el=root.querySelector('[data-commerce-status]'); if(el) el.textContent=message; }
function showCart(cart) {
  currentCart=cart;
  const el=root.querySelector('[data-cart-summary]');
  if(el) el.textContent=cart?.totalQuantity ? `${cart.totalQuantity} ${T.items} · ${money(cart.cost.subtotalAmount.amount,cart.cost.subtotalAmount.currencyCode)}` : '';
}
async function readCart() {
  cartId=localStorage.getItem('flylyfe_cart');
  if(!cartId) return null;
  const {cart}=await gql(`query($id:ID!){cart(id:$id){${CART_FIELDS}}}`,{id:cartId});
  if(!cart) { cartId=null; localStorage.removeItem('flylyfe_cart'); }
  showCart(cart); return cart;
}
async function ensureCart() {
  const existing=await readCart(); if(existing) return existing;
  const {cartCreate}=await gql(`mutation{cartCreate{cart{${CART_FIELDS}} userErrors{field message}}}`);
  if(!cartCreate.cart) throw new Error('Cart creation failed');
  cartId=cartCreate.cart.id; localStorage.setItem('flylyfe_cart',cartId);
  showCart(cartCreate.cart); return cartCreate.cart;
}
function setBusy(value) {
  busy=value;
  root.querySelectorAll('button').forEach(b=>{b.disabled=value || b.dataset.unavailable==='true';});
  root.setAttribute('aria-busy',String(value));
}
async function addToCart() {
  if(busy) return;
  const selected=variant();
  if(!selected?.availableForSale) { status(T.selectAvail); return; }
  setBusy(true); status(T.adding);
  try {
    const cart=await ensureCart();
    const {cartLinesAdd}=await gql(`mutation($id:ID!,$lines:[CartLineInput!]!){cartLinesAdd(cartId:$id,lines:$lines){cart{${CART_FIELDS}} userErrors{field message}}}`,{id:cart.id,lines:[{merchandiseId:selected.id,quantity:1}]});
    if(!cartLinesAdd.cart) throw new Error('Cart update failed');
    showCart(cartLinesAdd.cart); status(T.added);
  } catch(error) { console.error(error); status(T.error); }
  finally { setBusy(false); }
}
async function checkout() {
  if(busy) return;
  setBusy(true);
  try {
    // Checkout reads the shared cart; it must never add the selection again.
    const cart=await readCart();
    if(!cart?.totalQuantity) { status(T.empty); return; }
    if(!cart.checkoutUrl) throw new Error('Missing checkout URL');
    window.location.assign(cart.checkoutUrl);
  } catch(error) { console.error(error); status(T.error); }
  finally { setBusy(false); }
}
function gallery() {
  const media=document.querySelector('.seo-product__media'); if(!media) return;
  const images=imageManifest[handle]?.[state.color] || {};
  const chosen=variants().find(v=>option(v,'Color')===state.color && v.image?.url);
  const url=images[state.view] || images.back || images.front || chosen?.image?.url;
  const img=media.querySelector('img');
  if(url && img) {
    img.src=url.startsWith('assets/') ? '/'+url : url;
    img.removeAttribute('srcset');
    img.alt=`${product.title} — ${state.color}, ${state.view==='front'?T.front:T.back}`;
    if(window.FlylyfeImages) window.FlylyfeImages.apply(img);
  }
  let controls=media.querySelector('[data-gallery-controls]');
  if(!controls) { controls=document.createElement('div'); controls.dataset.galleryControls=''; controls.className='seo-commerce__options'; media.appendChild(controls); }
  controls.replaceChildren();
  for(const view of ['front','back']) {
    if(!images[view]) continue;
    const button=document.createElement('button'); button.className='seo-option'; button.textContent=view==='front'?T.front:T.back;
    button.setAttribute('aria-pressed',String(state.view===view));
    button.onclick=()=>{state.view=view;gallery();}; controls.appendChild(button);
  }
}
function render() {
  const colors=optionValues('Color');
  const sizeOrder=['XS','S','M','L','XL','2XL','3XL','4XL'];
  const sizes=optionValues('Size').slice().sort((a,b)=>sizeOrder.indexOf(a)-sizeOrder.indexOf(b));
  if(!colors.includes(state.color)) state.color=colors.includes('Black')?'Black':colors[0];
  const selected=variant() || variants().find(v=>option(v,'Color')===state.color);
  root.innerHTML=`<div class="seo-commerce__group"><p class="seo-commerce__label mono" data-color-label></p><div class="seo-commerce__options" data-colors></div></div><div class="seo-commerce__group"><p class="seo-commerce__label mono" data-size-label></p><div class="seo-commerce__options" data-sizes></div></div><button type="button" class="seo-atc" data-atc></button><button type="button" class="seo-checkout" data-checkout>${T.checkout}</button><p class="seo-status mono" data-commerce-status role="status" aria-live="polite"></p><p class="mono" data-cart-summary></p><a class="seo-cart-link" href="/#cart">${T.viewCart}</a><p class="seo-placement-note">${T.placement}</p>`;
  root.querySelector('[data-color-label]').textContent=`${T.color} — ${state.color}`;
  root.querySelector('[data-size-label]').textContent=T.size+(state.size?' — '+state.size:'');
  root.querySelector('[data-atc]').textContent=state.size?`${T.atc} · ${money(selected.price.amount,selected.price.currencyCode)}`:T.select;
  const price=document.querySelector('.seo-price'); if(price && selected) price.textContent=money(selected.price.amount,selected.price.currencyCode)+' USD';
  for(const color of colors) {
    const button=document.createElement('button');button.className='seo-option';button.textContent=color;
    button.setAttribute('aria-pressed',String(color===state.color));
    button.onclick=()=>{if(busy)return;state.color=color;state.size=null;render();};root.querySelector('[data-colors]').appendChild(button);
  }
  for(const size of sizes) {
    const available=variants().some(v=>v.availableForSale && option(v,'Color')===state.color && option(v,'Size')===size);
    const button=document.createElement('button');button.className='seo-option';button.textContent=size;
    button.disabled=!available;button.dataset.unavailable=String(!available);button.setAttribute('aria-pressed',String(size===state.size));
    button.onclick=()=>{if(busy)return;state.size=size;render();};root.querySelector('[data-sizes]').appendChild(button);
  }
  root.querySelector('[data-atc]').onclick=addToCart;
  root.querySelector('[data-checkout]').onclick=checkout;
  showCart(currentCart);gallery();
}
async function initProductPage() {
  try {
    const [data,manifest]=await Promise.all([gql(PRODUCT_Q,{handle}),fetch('/assets/products-model/manifest.json?v=20260909').then(r=>r.ok?r.json():{}).catch(()=>({}))]);
    product=data.product;imageManifest=manifest;
    if(!product || product.vendor!=='FLYLYFE') throw new Error('FLYLYFE product not found');
    render();
    try { await readCart(); } catch(error) { console.error(error); }
  } catch(error) {
    console.error(error);root.replaceChildren();
    const message=document.createElement('p');message.textContent=T.unavailable;root.appendChild(message);
    const button=document.createElement('button');button.className='seo-atc';button.textContent=T.retry;button.onclick=initProductPage;root.appendChild(button);
  }
}
initProductPage();
