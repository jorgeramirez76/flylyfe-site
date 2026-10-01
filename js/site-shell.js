/* Shared navigation and a read-only cart badge on every storefront page. */
(() => {
  const header = document.querySelector('header.nav');
  if (!header) return;
  const isHome = Boolean(document.getElementById('cartBtn'));
  const links = [ ['/#shop','Shop'], ['/collections/mens/',"Men’s"], ['/collections/womens/',"Women’s"], ['/collections/concrete-rhythm/','Concrete Rhythm'], ['/collections/heritage/','Heritage'], ['/collections/drop-02/','Drop 02'], ['/blog/','Blog'], ['/about.html','About'], ['/faq.html','FAQ'], ['mailto:hello@flylyfe.com','Contact'] ];
  const linkMarkup = links.map(([href,label]) => `<a href="${href}"${location.pathname===href ? ' aria-current="page"' : ''}>${label}</a>`).join('');
  if (!isHome) {
    header.id = 'nav';
    header.querySelector('.nav__links').innerHTML = linkMarkup;
    const right = document.createElement('div');
    right.className = 'nav__right';
    right.innerHTML = '<a class="nav__cart" href="/#cart" aria-label="View cart"><span class="nav__cart-label mono">CART</span><span class="nav__cart-paren mono">(<span data-site-cart-count>0</span>)</span></a><button class="nav__burger" aria-label="Open menu" aria-expanded="false" aria-controls="siteMobileMenu"><span></span><span></span><span></span></button>';
    header.append(right);
    const menu = document.createElement('div');
    menu.id = 'siteMobileMenu'; menu.className = 'mobilemenu'; menu.hidden = true;
    menu.setAttribute('role','dialog'); menu.setAttribute('aria-modal','true'); menu.setAttribute('aria-label','Navigation');
    menu.innerHTML = `<button class="site-menu-close" aria-label="Close menu">Close ×</button><nav class="mobilemenu__links" aria-label="Mobile navigation">${linkMarkup}</nav>`;
    document.body.append(menu);
    const toggle = right.querySelector('button');
    const pageRegions=[...document.querySelectorAll('main,footer,header')];
    const close = () => { pageRegions.forEach(el=>el.inert=false); menu.hidden=true; toggle.setAttribute('aria-expanded','false'); document.body.style.overflow=''; toggle.focus(); };
    toggle.onclick = () => { pageRegions.forEach(el=>el.inert=true); menu.hidden=false; toggle.setAttribute('aria-expanded','true'); document.body.style.overflow='hidden'; menu.querySelector('button').focus(); };
    menu.querySelector('button').onclick=close;
    menu.addEventListener('click',e => { if(e.target.closest('a')) close(); });
    menu.addEventListener('keydown',e => {
      if(e.key==='Escape'){ e.preventDefault(); close(); }
      if(e.key==='Tab'){
        const focusables=[...menu.querySelectorAll('a,button')];
        const first=focusables[0],last=focusables.at(-1);
        if(e.shiftKey && document.activeElement===first){e.preventDefault();last.focus();}
        else if(!e.shiftKey && document.activeElement===last){e.preventDefault();first.focus();}
      }
    });
    matchMedia('(min-width: 1501px)').addEventListener('change', e=>{ if(e.matches&&!menu.hidden)close(); });
  }
  const updateCount = quantity => {
    document.querySelectorAll('[data-site-cart-count]').forEach(el=>{
      el.textContent = Number(quantity)||0;
      el.closest('a').setAttribute('aria-label',`View cart, ${Number(quantity)||0} items`);
    });
  };
  window.addEventListener('flylyfe:cart',e => updateCount(e.detail.quantity));
  async function refreshCount(){
    if(isHome)return;
    const id=localStorage.getItem('flylyfe_cart');
    if(!id){updateCount(0);return;}
    try{
      const response=await fetch('https://31zn52-zd.myshopify.com/api/2025-10/graphql.json',{
        method:'POST',headers:{'Content-Type':'application/json','X-Shopify-Storefront-Access-Token':'5a0bb1dcf0c57b7764bbebf0cc40c898'},
        body:JSON.stringify({query:'query($id:ID!){cart(id:$id){totalQuantity}}',variables:{id}})
      });
      const result=await response.json();
      if(response.ok&&!result.errors)updateCount(result.data?.cart?.totalQuantity||0);
    }catch(_){/* Cart remains available when its badge cannot refresh. */}
  }
  refreshCount();
  window.addEventListener('storage',e=>{if(e.key==='flylyfe_cart')refreshCount();});
  const info=document.querySelector('.seo-product__info');
  if(info){
    const fit=document.createElement('p'); fit.className='seo-fit-summary';
    const h=document.body.dataset.productHandle||'';
    fit.textContent=h.includes('womens-fitted')?'Women’s fitted · Lightweight cotton · Runs small · S–2XL':h.includes('womens')?'Women’s relaxed · Heavyweight cotton · S–3XL':'Heavyweight cotton · Relaxed unisex fit';
    info.querySelector('h1').after(fit);
  }
})();
