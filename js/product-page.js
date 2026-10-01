
// Shopify Storefront API identifiers are intentionally client-side.
// This is not an Admin API secret; it is scoped for public storefront cart/product operations only.
const SHOP_DOMAIN='31zn52-zd.myshopify.com';
const STOREFRONT_TOKEN='5a0bb1dcf0c57b7764bbebf0cc40c898';
const API_URL=`https://${SHOP_DOMAIN}/api/2025-10/graphql.json`;
const handle = document.body.dataset.productHandle;
const WOMEN_FIT_FAMILIES = [[{"handle":"the-anthem-tee-womens","label":"Relaxed","es":"Holgada"},{"handle":"the-anthem-tee-womens-fitted","label":"Fitted","es":"Entallada"}],[{"handle":"the-conga-tee-womens","label":"Relaxed","es":"Holgada"},{"handle":"the-conga-tee-womens-fitted","label":"Fitted","es":"Entallada"}],[{"handle":"the-signature-tee-womens","label":"Relaxed","es":"Holgada"},{"handle":"the-signature-tee-womens-fitted","label":"Fitted","es":"Entallada"}],[{"handle":"the-house-music-tee-womens","label":"Relaxed","es":"Holgada"},{"handle":"the-house-music-tee-womens-fitted","label":"Fitted","es":"Entallada"}],[{"handle":"the-after-hours-tee-womens","label":"Relaxed","es":"Holgada"},{"handle":"the-after-hours-tee-womens-fitted","label":"Fitted","es":"Entallada"}],[{"handle":"the-tempo-tee-womens","label":"Relaxed","es":"Holgada"},{"handle":"the-tempo-tee-womens-fitted","label":"Fitted","es":"Entallada"}],[{"handle":"the-spiritual-thing-tee-womens","label":"Relaxed","es":"Holgada"},{"handle":"the-spiritual-thing-tee-womens-fitted","label":"Fitted","es":"Entallada"}],[{"handle":"the-coordinates-tee-womens","label":"Relaxed","es":"Holgada"},{"handle":"the-coordinates-tee-womens-fitted","label":"Fitted","es":"Entallada"}],[{"handle":"the-sanitary-code-tee-womens","label":"Relaxed","es":"Holgada"},{"handle":"the-sanitary-code-tee-womens-fitted","label":"Fitted","es":"Entallada"}],[{"handle":"the-token-tee-womens","label":"Relaxed","es":"Holgada"},{"handle":"the-token-tee-womens-fitted","label":"Fitted","es":"Entallada"}],[{"handle":"the-soul-tee-womens","label":"Relaxed","es":"Holgada"},{"handle":"the-soul-tee-womens-fitted","label":"Fitted","es":"Entallada"}],[{"handle":"las-malvinas-campeones-tee-womens","label":"Relaxed","es":"Holgada"},{"handle":"las-malvinas-campeones-tee-womens-fitted","label":"Fitted","es":"Entallada"}],[{"handle":"las-malvinas-tee-womens","label":"Relaxed","es":"Holgada"},{"handle":"las-malvinas-tee-womens-fitted","label":"Fitted","es":"Entallada"}],[{"handle":"the-brownstone-dj-tee-womens","label":"Relaxed","es":"Holgada"},{"handle":"the-brownstone-dj-tee-womens-fitted","label":"Fitted","es":"Entallada"}]];
const WOMEN_FITS = WOMEN_FIT_FAMILIES.flat();
const fitFamily = handle => WOMEN_FIT_FAMILIES.find(fits=>fits.some(f=>f.handle===handle)) || [];
const fitProducts={};
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
const FRONT_FIRST = new Set(['the-signature-tee','the-signature-tee-womens','the-signature-tee-womens-fitted','the-sanitary-code-tee','the-sanitary-code-tee-womens','the-sanitary-code-tee-womens-fitted']);
let cartId = localStorage.getItem('flylyfe_cart');
let product = null, imageManifest = {}, currentCart = null, busy = false;
const WOMEN_FEATURED_COLORS = {"the-anthem-tee-womens-fitted": "Black", "the-anthem-tee-womens": "White", "the-conga-tee-womens-fitted": "Soft Cream", "the-conga-tee-womens": "Black", "the-signature-tee-womens-fitted": "White", "the-signature-tee-womens": "Ivory", "the-house-music-tee-womens-fitted": "Black", "the-house-music-tee-womens": "White", "the-after-hours-tee-womens-fitted": "Soft Cream", "the-after-hours-tee-womens": "Black", "the-tempo-tee-womens-fitted": "White", "the-tempo-tee-womens": "Ivory", "the-spiritual-thing-tee-womens-fitted": "Black", "the-spiritual-thing-tee-womens": "White", "the-coordinates-tee-womens-fitted": "Soft Cream", "the-coordinates-tee-womens": "Black", "the-sanitary-code-tee-womens-fitted": "White", "the-sanitary-code-tee-womens": "Ivory", "the-token-tee-womens-fitted": "Black", "the-token-tee-womens": "White", "the-soul-tee-womens-fitted": "Soft Cream", "the-soul-tee-womens": "Black", "las-malvinas-campeones-tee-womens-fitted": "White", "las-malvinas-campeones-tee-womens": "Ivory", "las-malvinas-tee-womens-fitted": "Black", "las-malvinas-tee-womens": "White", "the-brownstone-dj-tee-womens-fitted": "Soft Cream", "the-brownstone-dj-tee-womens": "Black"};
const state = {color:null, size:null, view:!handle.includes('-womens') && FRONT_FIRST.has(handle) ? 'front' : 'back'};
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
  window.dispatchEvent(new CustomEvent('flylyfe:cart',{detail:{quantity:cart?.totalQuantity||0}}));
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
function chooseColor(color) {
  const previousSize=state.size;
  state.color=color;
  if(previousSize && !variant()?.availableForSale) state.size=null;
  render();
  if(previousSize && !state.size) status(ES ? `El talle ${previousSize} no está disponible en ${color}. Elegí otro talle.` : `Size ${previousSize} is unavailable in ${color}. Please choose another size.`);
}
function focusOption(selector,value) {
  [...root.querySelectorAll(selector)].find(b=>b.textContent===value)?.focus({preventScroll:true});
}
function sizeGuide() {
  const fitted=product.handle.endsWith('-fitted');
  const guide=document.createElement('details');guide.className='commerce-size-guide';
  const label=ES ? `Guía de talles — ${fitted?'entallada':'holgada'}` : `Size guide — ${fitted?'fitted':'relaxed'}`;
  const chart=fitted ? '<img src="https://blob.apliiq.com/sitestorage/BaseSizeChart/Chart_927.jpg?v=20240723" alt="Bella Canvas 6004 size chart" loading="lazy" style="width:100%;height:auto;background:white">' : `<table><thead><tr><th>${ES?'Talle':'Size'}</th><th>${ES?'Ancho (pulgadas)':'Width (in)'}</th><th>${ES?'Largo (pulgadas)':'Length (in)'}</th></tr></thead><tbody>${[['S','18.25','26.625'],['M','20.25','28'],['L','22','29.375'],['XL','24','30.75'],['2XL','26','31.625'],['3XL','27.75','32.5']].map(row=>'<tr>'+row.map(v=>'<td>'+v+'</td>').join('')+'</tr>').join('')}</tbody></table>`;
  const note=fitted ? (ES?'El corte es pequeño. Compará las medidas de la prenda con una remera que ya tengas.':'Runs small. Compare garment measurements with a tee you own.') : (ES?'Comfort Colors 1717: medidas de la prenda, no del cuerpo. Ancho en plano, una pulgada debajo de la sisa; largo desde el hombro alto hasta el dobladillo trasero. Compará con una remera que ya tengas.':'Comfort Colors 1717 garment measurements, not body measurements. Width is laid flat, one inch below the armhole; length is high shoulder to back hem. Compare a tee you own.');
  guide.innerHTML=`<summary>${label}</summary><p>${note}</p>${chart}`;
  return guide;
}
function gallery() {
  const media=document.querySelector('.seo-product__media'); if(!media) return;
  const images=imageManifest[product.handle]?.[state.color] || {};
  const chosen=variants().find(v=>option(v,'Color')===state.color && v.image?.url);
  const url=images[state.view] || images.back || images.front || chosen?.image?.url;
  const img=media.querySelector('img');
  if(url && img) {
    img.src=url.startsWith('assets/') ? '/'+url : url;
    img.removeAttribute('srcset');
    if(/womens-(?:fitted|relaxed)-models\//.test(url)) {img.style.objectFit='cover';img.style.objectPosition=state.view==='back'?'right center':'left center';} else if(WOMEN_FITS.some(f=>f.handle===product.handle)) {img.style.objectFit='contain';img.style.objectPosition='center';}
    img.alt=`${product.title} — ${state.color}, ${state.view==='front'?T.front:T.back}`;
    if(window.FlylyfeImages) window.FlylyfeImages.apply(img);
  }
  let controls=media.querySelector('[data-gallery-controls]');
  if(!controls) { controls=document.createElement('div'); controls.dataset.galleryControls=''; controls.className='seo-commerce__options'; media.appendChild(controls); }
  let swatches=media.querySelector('[data-gallery-colors]');
  if(!swatches) {
    swatches=document.createElement('div');swatches.dataset.galleryColors='';swatches.className='seo-gallery-colors';
    swatches.setAttribute('role','group');swatches.setAttribute('aria-label',ES?'Color de la camiseta':'Shirt color');
    media.insertBefore(swatches,controls);
  }
  swatches.replaceChildren();
  const colorHex={Black:'#202020',White:'#ffffff',Ivory:'#eee6cf','Soft Cream':'#f3ead6'};
  for(const color of optionValues('Color')) {
    const button=document.createElement('button');button.type='button';button.className='seo-gallery-swatch';
    button.title=color;button.setAttribute('aria-label',color);button.setAttribute('aria-pressed',String(color===state.color));
    button.style.setProperty('--swatch-color',colorHex[color]||color.toLowerCase());
    button.onclick=()=>{if(busy)return;chooseColor(color);
      [...swatches.children].find(b=>b.getAttribute('aria-label')===color)?.focus({preventScroll:true});};
    swatches.appendChild(button);
  }
  controls.replaceChildren();
  for(const view of ['front','back']) {
    if(!images[view]) continue;
    const button=document.createElement('button'); button.className='seo-option'; button.textContent=view==='front'?T.front:T.back;
    button.setAttribute('aria-pressed',String(state.view===view));
    button.dataset.view=view;
    button.onclick=()=>{if(busy)return;state.view=view;gallery();
      [...controls.children].find(b=>b.dataset.view===view)?.focus({preventScroll:true});}; controls.appendChild(button);
  }
}
function render() {
  const colors=optionValues('Color');
  const sizeOrder=['XS','S','M','L','XL','2XL','3XL','4XL'];
  const sizes=optionValues('Size').slice().sort((a,b)=>sizeOrder.indexOf(a)-sizeOrder.indexOf(b));
  if(!colors.includes(state.color)) state.color=colors.includes(WOMEN_FEATURED_COLORS[product.handle])?WOMEN_FEATURED_COLORS[product.handle]:colors.includes('Black')?'Black':colors[0];
  const selected=variant() || variants().find(v=>option(v,'Color')===state.color);
  root.innerHTML=`<div class="seo-commerce__group"><p class="seo-commerce__label mono" data-color-label></p><div class="seo-commerce__options" data-colors></div></div><div class="seo-commerce__group"><p class="seo-commerce__label mono" data-size-label></p><div class="seo-commerce__options" data-sizes></div></div><button type="button" class="seo-atc" data-atc></button><button type="button" class="seo-checkout" data-checkout>${T.checkout}</button><p class="seo-status mono" data-commerce-status role="status" aria-live="polite"></p><p class="mono" data-cart-summary></p><a class="seo-cart-link" href="/#cart">${T.viewCart}</a><p class="seo-placement-note">${T.placement}</p>`;
  root.querySelector('[data-color-label]').textContent=`${T.color} — ${state.color}`;
  root.querySelector('[data-size-label]').textContent=T.size+(state.size?' — '+state.size:'');
  if(WOMEN_FITS.some(f=>f.handle===product.handle)){
    const group=document.createElement('div');group.className='seo-commerce__group';
    const label=document.createElement('p');label.className='seo-commerce__label mono';label.textContent=ES?'CORTE':'FIT';group.appendChild(label);
    const buttons=document.createElement('div');buttons.className='seo-commerce__options';group.appendChild(buttons);
    fitFamily(product.handle).filter(f=>fitProducts[f.handle]).forEach(f=>{
      const b=document.createElement('button');b.type='button';b.className='seo-option';b.textContent=ES?f.es:f.label;b.setAttribute('aria-pressed',String(f.handle===product.handle));
      b.onclick=()=>{if(busy||f.handle===product.handle)return;window.location.assign('/products/'+f.handle+'/');};buttons.appendChild(b);
    });
    root.prepend(group);
    const heading=document.querySelector('.seo-product__hero h1');if(heading)heading.textContent=product.title;
    const lede=document.querySelector('.seo-lede');if(lede){const description=document.createElement('div');description.className='seo-lede';description.innerHTML=product.descriptionHtml;lede.replaceWith(description);}
    const specline=document.querySelector('.seo-specline');if(specline)specline.textContent='';

  }
  root.querySelector('[data-sizes]').after(sizeGuide());
  const policy=document.createElement('p');policy.className='commerce-policy';
  policy.innerHTML=ES ? 'Producción: 7–10 días hábiles, más envío. Envío calculado al finalizar la compra. Devoluciones dentro de 30 días de la entrega, sin uso ni lavado; el cliente paga el envío de devolución. <a href="/faq.html#shipping">Envíos</a> · <a href="/faq.html#returns">Devoluciones</a>' : 'Printed to order: 7–10 business days, plus delivery. Shipping calculated at checkout. 30-day returns on unworn, unwashed tees; customer pays return shipping. <a href="/faq.html#shipping">Shipping</a> · <a href="/faq.html#returns">Returns</a>';
  root.querySelector('[data-checkout]').after(policy);
  root.querySelector('[data-atc]').textContent=state.size?`${T.atc} · ${money(selected.price.amount,selected.price.currencyCode)}`:T.select;
  const price=document.querySelector('.seo-price'); if(price && selected) price.textContent=money(selected.price.amount,selected.price.currencyCode)+' USD';
  for(const color of colors) {
    const button=document.createElement('button');button.className='seo-option';button.textContent=color;
    button.setAttribute('aria-pressed',String(color===state.color));
    button.onclick=()=>{if(busy)return;chooseColor(color);focusOption('[data-colors] button',color);};root.querySelector('[data-colors]').appendChild(button);
  }
  for(const size of sizes) {
    const available=variants().some(v=>v.availableForSale && option(v,'Color')===state.color && option(v,'Size')===size);
    const button=document.createElement('button');button.className='seo-option';button.textContent=size;
    button.disabled=!available;button.dataset.unavailable=String(!available);button.setAttribute('aria-pressed',String(size===state.size));
    button.onclick=()=>{if(busy)return;state.size=size;render();focusOption('[data-sizes] button',size);};root.querySelector('[data-sizes]').appendChild(button);
  }
  root.querySelector('[data-atc]').onclick=addToCart;
  root.querySelector('[data-checkout]').onclick=checkout;
  showCart(currentCart);gallery();
}
async function initProductPage() {
  try {
    const [data,manifest]=await Promise.all([gql(PRODUCT_Q,{handle}),fetch('/assets/products-model/manifest.json?v=20261001-both-womens-fits-v3').then(r=>r.ok?r.json():{}).catch(()=>({}))]);
    product=data.product;imageManifest=manifest;
    if(!product || product.vendor!=='FLYLYFE') throw new Error('FLYLYFE product not found');
    if(WOMEN_FITS.some(f=>f.handle===handle)){
      fitProducts[handle]=product;
      await Promise.all(fitFamily(handle).filter(f=>f.handle!==handle).map(async f=>{try{const d=await gql(PRODUCT_Q,{handle:f.handle});if(d.product?.vendor==='FLYLYFE')fitProducts[f.handle]=d.product;}catch(error){console.error(error);}}));
    }
    render();
    try { await readCart(); } catch(error) { console.error(error); }
  } catch(error) {
    console.error(error);root.replaceChildren();
    const message=document.createElement('p');message.textContent=T.unavailable;root.appendChild(message);
    const button=document.createElement('button');button.className='seo-atc';button.textContent=T.retry;button.onclick=initProductPage;root.appendChild(button);
  }
}
initProductPage();
