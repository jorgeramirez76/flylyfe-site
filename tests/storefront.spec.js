const {test,expect}=require('@playwright/test');
const product=require('./fixtures/anthem.json');

async function storefront(page,{failCart=false,initialQuantity=0}={}){
  const operations=[];
  let quantity=initialQuantity;
  const merchandise={...product.variants.edges[0].node,product:{title:product.title,handle:product.handle},image:{url:'http://127.0.0.1:8765/assets/products-seo/the-anthem-tee.webp',altText:product.title}};
  const cart=()=>({id:'gid://shopify/Cart/test-cart',checkoutUrl:'https://shop.flylyfe.com/checkouts/test',totalQuantity:quantity,cost:{subtotalAmount:{amount:String(quantity*49.99),currencyCode:'USD'}},lines:{edges:quantity?[{node:{id:'test-line',quantity,merchandise}}]:[]}});
  await page.route('**/api/*/graphql.json',async route=>{
    const request=route.request().postDataJSON();operations.push(request);
    if(request.query.includes('product(handle:'))return route.fulfill({json:{data:{product}}});
    if(failCart)return route.fulfill({status:503,json:{error:'Offline fixture'}});
    let data;
    if(request.query.includes('cartCreate'))data={cartCreate:{cart:cart(),userErrors:[]}};
    else if(request.query.includes('cartLinesAdd')){quantity++;data={cartLinesAdd:{cart:cart(),userErrors:[]}};}
    else if(request.query.includes('cartLinesUpdate')){quantity=request.variables.lines[0].quantity;data={cartLinesUpdate:{cart:cart(),userErrors:[]}};}
    else data={cart:cart()};
    await route.fulfill({json:{data}});
  });
  return operations;
}

test('homepage starts without catalog calls and empty cart never creates a cart',async({page})=>{
  const ops=await storefront(page);
  await page.goto('/');
  await expect(page.locator('.home-discovery a')).toHaveCount(2);
  expect(ops).toHaveLength(0);
  await page.locator('#cartBtn').click();
  await expect(page.locator('button[data-closecart]')).toBeFocused();
  await expect(page.getByText('Your cart is empty. Start with a graphic')).toBeVisible();
  await expect(page.locator('#checkoutBtn')).toBeDisabled();
  expect(ops).toHaveLength(0);
  await page.keyboard.press('Escape');
  await expect(page.locator('#cartBtn')).toBeFocused();
  await expect(page.locator('main')).not.toHaveAttribute('inert','');
});

test('navigation closes by button and Escape, restoring focus',async({page},testInfo)=>{
  await storefront(page);await page.goto('/');
  if(testInfo.project.name==='desktop')await expect(page.locator('#nav .nav__links a')).toHaveCount(5);
  const menuButton=page.locator('#navBurger');
  await menuButton.click();
  const close=page.locator('#mobileMenu .site-menu-close');
  await expect(close).toBeFocused();
  await close.click();
  await expect(menuButton).toBeFocused();
  await menuButton.click();await page.keyboard.press('Escape');
  await expect(menuButton).toBeFocused();
});

test('cart failure offers recovery without an uncaught exception',async({page})=>{
  await page.addInitScript(()=>localStorage.setItem('flylyfe_cart','gid://shopify/Cart/test-cart'));
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  const ops=await storefront(page,{failCart:true});await page.goto('/#cart');
  await expect(page.getByRole('button',{name:'TRY AGAIN',exact:true})).toBeVisible();
  await page.getByRole('button',{name:'TRY AGAIN',exact:true}).click();
  await expect(page.getByRole('alert')).toContainText('saved cart has not been changed');
  expect(ops.every(o=>!o.query.includes('mutation'))).toBeTruthy();
  expect(errors).toEqual([]);
});

test('size chart stays in centimeters and open through size and color changes',async({page})=>{
  await storefront(page);await page.goto('/products/the-anthem-tee/');
  const guide=page.locator('.commerce-size-guide');
  await guide.locator('summary').click();await guide.getByRole('button',{name:'cm',exact:true}).click();
  await expect(guide).toContainText('46.4');
  await page.locator('[data-sizes]').getByRole('button',{name:'M',exact:true}).click();
  await expect(guide).toHaveAttribute('open','');
  await expect(guide.getByRole('button',{name:'cm',exact:true})).toHaveAttribute('aria-pressed','true');
  await expect(page.locator('[data-sizes]').getByRole('button',{name:'M',exact:true})).toBeFocused();
  await page.locator('[data-colors]').getByRole('button',{name:'White',exact:true}).click();
  await expect(guide).toHaveAttribute('open','');
  await expect(guide).toContainText('46.4');
  await expect(page.locator('[data-sizes]').getByRole('button',{name:'M',exact:true})).toHaveAttribute('aria-pressed','true');
});

for(const storageFailure of ['read','write'])test(`shopping retains its current cart when storage ${storageFailure} fails`,async({page})=>{
  await page.addInitScript(kind=>{Storage.prototype[kind==='read'?'getItem':'setItem']=()=>{throw new DOMException('Blocked','SecurityError');};},storageFailure);
  const ops=await storefront(page);await page.goto('/products/the-anthem-tee/');
  await page.locator('[data-sizes]').getByRole('button',{name:'M',exact:true}).click();
  await page.locator('[data-atc]').click();
  await expect(page.locator('[data-commerce-status]')).toHaveText('ADDED TO CART');
  await page.locator('[data-atc]').click();
  await expect(page.locator('[data-cart-summary]')).toContainText('2 items');
  expect(ops.filter(o=>o.query.includes('cartCreate'))).toHaveLength(1);
  expect(ops.filter(o=>o.query.includes('cartLinesAdd'))).toHaveLength(2);
  await page.route('https://shop.flylyfe.com/checkouts/test',route=>route.fulfill({contentType:'text/html',body:'<h1>Isolated checkout fixture</h1>'}));
  await page.locator('[data-checkout]').click();
  await expect(page).toHaveURL('https://shop.flylyfe.com/checkouts/test');
  expect(ops.filter(o=>o.query.includes('cartLinesAdd'))).toHaveLength(2);
});

test('mobile shopping CTA is above the fold and video waits for play',async({page},testInfo)=>{
  test.skip(testInfo.project.name!=='mobile');
  await storefront(page);const videos=[];page.on('request',r=>{if(r.url().endsWith('.mp4'))videos.push(r.url());});
  await page.goto('/');
  await expect(page.locator('.hero__mobile-cta')).toBeInViewport();
  expect(await page.locator('#heroVideo').evaluate(v=>v.paused)).toBeTruthy();
  expect(videos).toEqual([]);
});

test('main shopping pages have no automated WCAG A/AA findings or overflow',async({page})=>{
  // Inspect settled content, not the transparent frames of scroll-reveal animations.
  await page.emulateMedia({reducedMotion:'reduce'});
  await storefront(page);
  for(const path of ['/','/collections/womens/','/products/the-anthem-tee/','/find-your-vibe/','/fit-guide/']){
    await page.goto(path);await page.addScriptTag({path:require.resolve('axe-core/axe.min.js')});
    const result=await page.evaluate(async()=>({overflow:document.documentElement.scrollWidth>innerWidth,violations:(await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}})).violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))}));
    expect(result,{message:path}).toEqual({overflow:false,violations:[]});
  }
});

test('vibe filters, empty results, reset and shareable URL work together',async({page})=>{
  await storefront(page);await page.goto('/find-your-vibe/');
  await expect(page.locator('.vibe-card:visible')).toHaveCount(14);
  await page.locator('[data-theme="heritage"]').click();
  await expect(page.locator('.vibe-card:visible')).toHaveCount(2);
  await expect(page).toHaveURL(/theme=heritage/);
  await page.reload();await expect(page.locator('.vibe-card:visible')).toHaveCount(2);
  await page.locator('input[type="search"]').fill('no-matching-design');
  await expect(page.locator('[data-vibe-empty]')).toBeVisible();
  await page.locator('[data-vibe-controls] button[type="reset"]').click();
  await expect(page.locator('.vibe-card:visible')).toHaveCount(14);
  await expect(page.locator('input[type="search"]')).toBeFocused();
  await page.locator('input[type="search"]').fill('124 BPM');
  await expect(page.locator('.vibe-card:visible')).toHaveCount(1);
  await expect(page.locator('.vibe-card:visible')).toContainText('Tempo');
});

test('fit guide converts both cuts and retains the original inch values',async({page})=>{
  await storefront(page);await page.goto('/fit-guide/');
  await page.locator('[data-unit="cm"]').click();
  await expect(page.locator('[data-inches="16"]')).toHaveText('40.6');
  await expect(page.locator('[data-inches="26.625"]')).toHaveText('67.6');
  await page.locator('[data-unit="in"]').click();
  await expect(page.locator('[data-inches="26.625"]')).toHaveText('26.625');
});

test('discovery and measurements remain available without JavaScript',async({browser})=>{
  const context=await browser.newContext({javaScriptEnabled:false});const page=await context.newPage();
  await page.goto('http://127.0.0.1:8765/find-your-vibe/');
  await expect(page.locator('.vibe-card')).toHaveCount(14);
  await expect(page.locator('.nav__links')).toBeVisible();
  const destinations=await page.locator('.vibe-card a[href^="/products/"]').evaluateAll(links=>[...new Set(links.map(a=>a.pathname))]);
  expect(destinations).toHaveLength(42);
  await page.goto('http://127.0.0.1:8765/fit-guide/');
  await expect(page.locator('[data-inches="26.625"]')).toHaveText('26.625');
  await context.close();
});

test('occupied cart works while images are delayed and keeps quantity focus',async({page})=>{
  await page.addInitScript(()=>localStorage.setItem('flylyfe_cart','gid://shopify/Cart/test-cart'));
  await storefront(page,{initialQuantity:1});
  let release;
  const imageGate=new Promise(resolve=>{release=resolve;});
  await page.route('**/assets/products-model/manifest.json',async route=>{await imageGate;await route.abort();});
  await page.goto('/#cart');
  await expect(page.locator('.citem__name')).toHaveText('The Anthem Tee');
  await expect(page.locator('button[data-closecart]')).toBeFocused();
  await expect(page.locator('.citem img')).toHaveAttribute('src',/the-anthem-tee.webp/);
  await page.getByRole('button',{name:'Increase quantity of The Anthem Tee'}).click();
  await expect(page.locator('#cartCount')).toHaveText('2');
  await expect(page.getByRole('button',{name:'Increase quantity of The Anthem Tee'})).toBeFocused();
  await page.getByRole('button',{name:'Remove The Anthem Tee'}).click();
  await expect(page.locator('#checkoutBtn')).toBeDisabled();
  await expect(page.locator('button[data-closecart]')).toBeFocused();
  release();
});
