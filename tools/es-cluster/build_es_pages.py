#!/usr/bin/env python3
"""Build the FLYLYFE /es/ cluster from workflow content packages.

Reads packages.json (drafts + kw from the es-cluster-and-social workflow, post-critic fixes),
emits es/<slug>/index.html pages cloned from the live EN skeletons, localizes the buy widget,
and patches EN counterparts (hreflang + cross-links), sitemap.xml and llms.txt.

Hand-built pages (the site generator is drifted and must NOT be run).
"""
import json, re, sys, html, os

ROOT = os.path.expanduser('~/flylyfe-site')
SC = os.path.dirname(os.path.abspath(__file__))
BASE = 'https://www.flylyfe.com'
TODAY = '2026-08-18'

P = json.load(open(f'{SC}/packages.json'))
KW = {p['page']: p for p in P['kw']['pages']}

# page key -> (package, EN counterpart path rel to root, EN counterpart URL, product handle or None)
PAGES = {
    'pdp-malvinas':  (P['drafts']['pdp-malvinas'],  'products/las-malvinas-tee/index.html',
                      f'{BASE}/products/las-malvinas-tee/', 'las-malvinas-tee'),
    'pdp-campeones': (P['drafts']['pdp-campeones'], 'products/las-malvinas-campeones-tee/index.html',
                      f'{BASE}/products/las-malvinas-campeones-tee/', 'las-malvinas-campeones-tee'),
    'article':       (P['drafts']['article'],       'blog/las-malvinas-son-argentinas-meaning/index.html',
                      f'{BASE}/blog/las-malvinas-son-argentinas-meaning/', None),
    'hub':           (P['drafts']['hub'],           None, None, None),
}

def esc(t):
    return html.escape(t, quote=False)

def slug_of(pkg):
    m = re.search(r'/es/([a-z0-9-]+)/?$', pkg['path'].rstrip('/') + '/')
    if m: return m.group(1)
    return pkg['path'].strip('/').split('/')[-1]

SLUGS = {k: (slug_of(pkg) if k != 'hub' else '') for k, (pkg, *_ ) in PAGES.items()}

def es_url(key):
    s = SLUGS[key]
    return f'{BASE}/es/{s}/' if s else f'{BASE}/es/'

def render_links(text, depth):
    """Escape text, then convert [anchor](product:handle) / [anchor](es:slug) tokens to links."""
    rel = '../' * depth
    t = esc(text)
    t = re.sub(r'\[([^\]]+)\]\(product:([a-z0-9-]+)\)', lambda m: f'<a href="{rel}products/{m.group(2)}/">{m.group(1)}</a>', t)
    def es_link(m):
        s = m.group(2)
        href = (('../' + s + '/') if depth == 2 else (s + '/')) if s else (rel + 'es/')
        return f'<a href="{href}">{m.group(1)}</a>'
    t = re.sub(r'\[([^\]]+)\]\(es:([a-z0-9-]*)\)', es_link, t)
    return t

def hreflang_block(key):
    en = PAGES[key][2]
    esu = es_url(key)
    if key == 'hub':
        return (f'<link rel="alternate" hreflang="es" href="{esu}">'
                f'<link rel="alternate" hreflang="x-default" href="{esu}">')
    return (f'<link rel="alternate" hreflang="en" href="{en}">'
            f'<link rel="alternate" hreflang="es" href="{esu}">'
            f'<link rel="alternate" hreflang="x-default" href="{en}">')

def head_block(key, pkg, depth, ogtype, ogimage):
    rel = '../' * depth
    url = es_url(key)
    t, d = esc(pkg['title']), esc(pkg['metaDescription'])
    return (
        '<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
        f'<title>{t}</title><meta name="description" content="{d}">'
        f'<link rel="canonical" href="{url}">{hreflang_block(key)}'
        f'<meta property="og:type" content="{ogtype}"><meta property="og:site_name" content="FLYLYFE">'
        f'<meta property="og:title" content="{t}"><meta property="og:description" content="{d}">'
        f'<meta property="og:url" content="{url}"><meta property="og:image" content="{ogimage}">'
        f'<meta property="og:locale" content="es_AR">'
        '<meta name="twitter:card" content="summary_large_image">'
        f'<meta name="twitter:title" content="{t}"><meta name="twitter:description" content="{d}">'
        f'<meta name="twitter:image" content="{ogimage}">'
        f'<link rel="icon" type="image/png" href="{rel}assets/favicon.png">\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:ital,wght@0,400;0,600;0,700&family=Anton&family=JetBrains+Mono:wght@400;500&display=swap">\n'
        f'<link rel="stylesheet" href="{rel}css/style.css?v=20260818-es">\n'
        f'<link rel="stylesheet" href="{rel}css/product.css?v=20260818-es">\n'
        f'<link rel="stylesheet" href="{rel}css/seo-pages.css?v=20260818-es">'
    )

def faq_jsonld(pkg):
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": f['q'],
         "acceptedAnswer": {"@type": "Answer", "text": f['a']}} for f in pkg['faq']]}

def breadcrumb_jsonld(key, pkg):
    items = [{"@type": "ListItem", "position": 1, "name": "FLYLYFE", "item": f"{BASE}/"},
             {"@type": "ListItem", "position": 2, "name": "Español", "item": f"{BASE}/es/"}]
    if key != 'hub':
        items.append({"@type": "ListItem", "position": 3, "name": pkg['h1'], "item": es_url(key)})
    return {"@type": "BreadcrumbList", "itemListElement": items}

def product_jsonld(key, pkg, handle, ogimage):
    return {"@type": "Product", "@id": es_url(key) + '#product',
            "name": pkg['h1'], "brand": {"@type": "Brand", "name": "FLYLYFE"},
            "category": "Apparel & Accessories > Clothing > Shirts & Tops",
            "description": pkg['metaDescription'], "image": [ogimage], "url": es_url(key),
            "inLanguage": "es",
            "keywords": ", ".join(pkg['schemaKeywords']),
            "offers": {"@type": "Offer", "price": "39.99", "priceCurrency": "USD",
                       "availability": "https://schema.org/InStock", "url": es_url(key),
                       "itemCondition": "https://schema.org/NewCondition"}}

def article_jsonld(key, pkg, ogimage):
    return {"@type": "BlogPosting", "headline": pkg['h1'], "inLanguage": "es",
            "description": pkg['metaDescription'],
            "author": {"@type": "Organization", "name": "FLYLYFE", "url": f"{BASE}/"},
            "publisher": {"@type": "Organization", "name": "FLYLYFE",
                          "logo": {"@type": "ImageObject", "url": f"{BASE}/assets/print/flylyfe-wordmark-gold.png"}},
            "image": ogimage, "datePublished": TODAY, "dateModified": TODAY,
            "mainEntityOfPage": es_url(key)}

def jsonld_script(graph):
    return ('<script type="application/ld+json">' +
            json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False) +
            '</script>')

def faq_html(pkg):
    out = ['<section class="seo-section"><h2>Preguntas frecuentes</h2><div class="faq__list">']
    for f in pkg['faq']:
        out.append(f'<details class="faq__item"><summary>{esc(f["q"])}</summary><p>{esc(f["a"])}</p></details>')
    out.append('</div></section>')
    return ''.join(out)

def sections_html(pkg, depth):
    """Group flat sections: h2 opens a section; consecutive h3s inside become a seo-grid."""
    out, grid, open_sec = [], [], False
    def flush_grid():
        nonlocal grid
        if grid:
            out.append('<div class="seo-grid">' + ''.join(grid) + '</div>')
            grid = []
    for s in pkg['sections']:
        txt = render_links(s['text'], depth)
        if s['level'] == 'h2':
            flush_grid()
            if open_sec: out.append('</section>')
            out.append(f'<section class="seo-section"><h2>{esc(s["heading"])}</h2>')
            open_sec = True
            if txt: out.append(f'<p>{txt}</p>')
        else:
            grid.append(f'<article><h3>{esc(s["heading"])}</h3><p>{txt}</p></article>')
    flush_grid()
    if open_sec: out.append('</section>')
    return ''.join(out)

def norm_href(href, depth):
    rel = '../' * depth
    m = re.match(r'^product:([a-z0-9-]+)$', href)
    if m: return f'{rel}products/{m.group(1)}/'
    m = re.match(r'^es:([a-z0-9-]*)/?$', href)
    if m:
        slug = m.group(1)
        if not slug: return rel + 'es/' if depth == 2 else './'
        return ('../' + slug + '/') if depth == 2 else (slug + '/')
    m = re.match(r'^/es/([a-z0-9-]+)/?$', href)
    if m: return (('../' + m.group(1) + '/') if depth == 2 else (m.group(1) + '/'))
    return href

def related_html(pkg, depth):
    rel = '../' * depth
    links, cards = [], []
    for l in pkg['internalLinks']:
        href = norm_href(l['href'], depth)
        m = re.search(r'products/([a-z0-9-]+)/?$', href)
        links.append(f'<a href="{href}">{esc(l["anchor"])}</a>')
        if m:
            cards.append(f'<a class="related-card" href="{href}"><img src="{rel}assets/products-seo/{m.group(1)}.jpg" '
                         f'alt="{esc(l["anchor"])}" loading="lazy"><span>{esc(l["anchor"])}</span></a>')
    line = ' · '.join(links)
    grid = f'<div class="related-grid">{"".join(cards)}</div>' if cards else ''
    return (f'<section class="seo-section"><h2>Más de FLYLYFE</h2>'
            f'<p class="seo-linkline">{line}</p>{grid}</section>')

NAV = ('<header class="nav"><a class="nav__logo" href="{rel}#top" aria-label="FLYLYFE home">'
       '<img src="{rel}assets/print/flylyfe-wordmark-gold.png" alt="FLYLYFE" class="nav__logo-img" width="405" height="40"></a>'
       '<nav class="nav__links" aria-label="Main"><a href="{rel}#shop">Shop</a><a href="{rel}collections/mens/">Men\'s</a>'
       '<a href="{rel}collections/womens/">Women\'s</a><a href="{rel}collections/heritage/">Heritage</a>'
       '<a href="{rel}blog/">Blog</a><a href="{esrel}">Español</a><a href="{rel}faq.html">FAQ</a></nav></header>')

def footer_and_scripts(depth, with_product_js):
    """Clone the live EN PDP footer, depth-adjusted."""
    h = open(f'{ROOT}/products/las-malvinas-tee/index.html').read()
    j = h.find('<footer')
    k = h.find('</body>')
    foot = h[j:k]
    if not with_product_js:
        foot = re.sub(r'<script src="[^"]*product-page\.js[^"]*" defer></script>', '', foot)
    else:
        foot = foot.replace('product-page.js?v=20260726-signup', 'product-page.js?v=20260818-es')
    if depth == 1:
        foot = foot.replace('../../', '../')
    return foot + '</body></html>'

def build_pdp(key):
    pkg, _, en_url, handle = PAGES[key]
    depth = 2
    rel = '../' * depth
    ogimage = f'{BASE}/assets/products-seo/{handle}.jpg'
    graph = [product_jsonld(key, pkg, handle, ogimage), faq_jsonld(pkg), breadcrumb_jsonld(key, pkg)]
    head = head_block(key, pkg, depth, 'product', ogimage) + jsonld_script(graph) + '</head>'
    lede = ''.join(f'<p class="seo-lede">{render_links(p, depth)}</p>' for p in pkg['intro'][:1])
    more_intro = ''.join(f'<p>{render_links(p, depth)}</p>' for p in pkg['intro'][1:])
    hero = (
        f'<main class="seo-product"><section class="seo-product__hero">'
        f'<div class="seo-product__media"><img src="{rel}assets/products-seo/{handle}.jpg" '
        f'alt="{esc(pkg["imageAlts"]["back"])}" width="1100" height="1500" fetchpriority="high"></div>'
        f'<div class="seo-product__info"><p class="mono gold-text">Heritage · FLYLYFE · EST. 2007</p>'
        f'<h1>{esc(pkg["h1"])}</h1>'
        f'<p class="seo-product__descriptor mono">{esc(pkg["descriptorLine"])}</p>'
        f'{lede}'
        f'<p class="mono seo-lang-switch"><a href="{en_url}">Read this page in English</a></p>'
        '<div class="seo-commerce" data-commerce-root><p class="mono">CARGANDO COLOR, TALLE Y COMPRA EN VIVO…</p>'
        f'<noscript><p class="mono">Necesitás JavaScript para comprar directo en esta página. '
        f'<a href="{rel}#shop">Comprá en la tienda principal de FLYLYFE</a>.</p></noscript></div>'
        '<div class="seo-trust mono"><span>✓ Impresa en USA</span><span>✓ Envíos a todo el mundo</span>'
        '<span>✓ Pago seguro con Shopify</span></div></div></section>'
    )
    feats = ''.join(f'<li><strong>{esc(f["label"])}.</strong> {render_links(f["text"], depth)}</li>'
                    for f in pkg['keyFeatures'])
    features = (f'<section class="seo-section"><h2>{esc(KW[pkg_kw_key(key)]["primaryKeyword"].title())} — características</h2>'
                f'{more_intro}<ul class="seo-features">{feats}</ul></section>') if feats else more_intro
    body = hero + features + sections_html(pkg, depth) + faq_html(pkg) + related_html(pkg, depth) + '</main>'
    nav = NAV.format(rel=rel, esrel='../')
    return head + f'<body data-product-handle="{handle}">' + nav + body + footer_and_scripts(depth, True)

def pkg_kw_key(key):
    # map draft key -> kw page entry by normalized slug
    for name, entry in KW.items():
        if entry['slug'].strip('/').split('/')[-1] == (SLUGS.get(key) or 'es'):
            return name
    for name, entry in KW.items():
        if entry['slug'].rstrip('/').endswith('/es') and key == 'hub':
            return name
    raise KeyError(f'no kw entry for {key}')

def build_article():
    key = 'article'
    pkg, _, en_url, _ = PAGES[key]
    depth = 2
    rel = '../' * depth
    ogimage = f'{BASE}/assets/products-seo/las-malvinas-tee.jpg'
    graph = [article_jsonld(key, pkg, ogimage), faq_jsonld(pkg), breadcrumb_jsonld(key, pkg)]
    head = head_block(key, pkg, depth, 'article', ogimage) + jsonld_script(graph) + '</head>'
    dek = ''.join(f'<p class="blog-dek">{render_links(p, depth)}</p>' for p in pkg['intro'][:1])
    more = ''.join(f'<p>{render_links(p, depth)}</p>' for p in pkg['intro'][1:])
    hero = (f'<main class="info-page blog-post"><article><section class="collection-hero">'
            f'<p class="mono gold-text">FLYLYFE JOURNAL · EN ESPAÑOL</p><h1>{esc(pkg["h1"])}</h1>{dek}'
            f'<p class="mono" style="font-size:.68rem;letter-spacing:.1em;color:var(--ink-dim);margin-top:1rem">FLYLYFE · {TODAY}</p>'
            f'<p class="mono seo-lang-switch"><a href="{en_url}">Read this article in English</a></p>'
            f'{more}</section>')
    body = hero + sections_html(pkg, depth) + faq_html(pkg) + '</article>' + related_html(pkg, depth) + '</main>'
    nav = NAV.format(rel=rel, esrel='../')
    return head + '<body>' + nav + body + footer_and_scripts(depth, False)

def build_hub():
    key = 'hub'
    pkg = PAGES[key][0]
    depth = 1
    rel = '../' * depth
    ogimage = f'{BASE}/assets/products-seo/las-malvinas-tee.jpg'
    graph = [{"@type": "WebPage", "name": pkg['h1'], "url": es_url(key), "inLanguage": "es",
              "description": pkg['metaDescription']}, faq_jsonld(pkg), breadcrumb_jsonld(key, pkg)]
    head = head_block(key, pkg, depth, 'website', ogimage) + jsonld_script(graph) + '</head>'
    intro = ''.join(f'<p>{render_links(p, depth)}</p>' for p in pkg['intro'])
    hero = (f'<main class="info-page"><section class="collection-hero">'
            f'<p class="mono gold-text">{esc(pkg["descriptorLine"])}</p><h1>{esc(pkg["h1"])}</h1>{intro}</section>')
    feats = ''.join(f'<li><strong>{esc(f["label"])}.</strong> {render_links(f["text"], depth)}</li>' for f in pkg['keyFeatures'])
    features = (f'<section class="seo-section"><h2>Por qué FLYLYFE</h2><ul class="seo-features">{feats}</ul></section>') if feats else ''
    body = hero + features + sections_html(pkg, depth) + faq_html(pkg) + related_html(pkg, depth) + '</main>'
    nav = NAV.format(rel=rel, esrel='./')
    return head + '<body>' + nav + body + footer_and_scripts(depth, False)

def localize_product_js():
    p = f'{ROOT}/js/product-page.js'
    s = open(p).read()
    if "const ES=" in s:
        print('product-page.js already localized'); return
    loc = ("const ES=document.documentElement.lang==='es';"
           "const T=ES?{color:'COLOR',size:'TALLE',atc:'AGREGAR AL CARRITO',select:'ELEGÍ TU TALLE',"
           "checkout:'FINALIZAR COMPRA',adding:'AGREGANDO…',added:'AGREGADO AL CARRITO',"
           "selectAvail:'ELEGÍ UN TALLE DISPONIBLE',loaded:'OPCIONES EN VIVO DE SHOPIFY',"
           "cartErr:'ERROR DE CARRITO — PROBÁ DE NUEVO',coErr:'ERROR AL PAGAR — PROBÁ DE NUEVO',"
           "unavail:'OPCIONES EN VIVO NO DISPONIBLES POR AHORA. ',shopMain:'COMPRÁ EN LA TIENDA PRINCIPAL'}"
           ":{color:'COLOR',size:'SIZE',atc:'ADD TO CART',select:'SELECT SIZE',checkout:'CHECKOUT',"
           "adding:'ADDING…',added:'ADDED TO CART',selectAvail:'SELECT AN AVAILABLE SIZE',"
           "loaded:'LIVE SHOPIFY OPTIONS LOADED',cartErr:'CART ERROR — TRY AGAIN',"
           "coErr:'CHECKOUT ERROR — TRY AGAIN',unavail:'LIVE OPTIONS TEMPORARILY UNAVAILABLE. ',"
           "shopMain:'SHOP ON MAIN SITE'};\n")
    s = s.replace("const handle=document.body.dataset.productHandle;",
                  "const handle=document.body.dataset.productHandle;\n" + loc, 1)
    subs = [
        ("status('SELECT AN AVAILABLE SIZE')", "status(T.selectAvail)"),
        ("status('ADDING…')", "status(T.adding)"),
        ("status('ADDED TO CART')", "status(T.added)"),
        ("`<div class=\"seo-commerce__group\"><p class=\"seo-commerce__label mono\">COLOR — ${state.color||''}</p>",
         "`<div class=\"seo-commerce__group\"><p class=\"seo-commerce__label mono\">${T.color} — ${state.color||''}</p>"),
        ("<p class=\"seo-commerce__label mono\">SIZE${state.size?' — '+state.size:''}</p>",
         "<p class=\"seo-commerce__label mono\">${T.size}${state.size?' — '+state.size:''}</p>"),
        ("${state.size?'ADD TO CART · '+money(price):'SELECT SIZE'}", "${state.size?T.atc+' · '+money(price):T.select}"),
        ("data-checkout>CHECKOUT</button>", "data-checkout>${T.checkout}</button>"),
        ("data-commerce-status>LIVE SHOPIFY OPTIONS LOADED</p>", "data-commerce-status>${T.loaded}</p>"),
        ("status('CART ERROR — TRY AGAIN')", "status(T.cartErr)"),
        ("status('CHECKOUT ERROR — TRY AGAIN')", "status(T.coErr)"),
        ("'<p class=\"mono\">LIVE OPTIONS TEMPORARILY UNAVAILABLE. <a href=\"../../#shop\">SHOP ON MAIN SITE</a></p>'",
         "'<p class=\"mono\">'+T.unavail+'<a href=\"../../#shop\">'+T.shopMain+'</a></p>'"),
    ]
    for old, new in subs:
        assert s.count(old) == 1, f'product-page.js sub not unique: {old[:50]}'
        s = s.replace(old, new)
    open(p, 'w').write(s)
    print('product-page.js localized (lang=es aware)')

def patch_en_pages():
    for key in ('pdp-malvinas', 'pdp-campeones', 'article'):
        pkg, relpath, en_url, handle = PAGES[key]
        p = f'{ROOT}/{relpath}'
        s = open(p).read()
        if 'hreflang' in s:
            print(f'{relpath}: hreflang already present, skipping'); continue
        canon = f'<link rel="canonical" href="{en_url}">'
        assert s.count(canon) == 1, relpath
        s = s.replace(canon, canon + hreflang_block(key))
        # visible cross-link
        esu = es_url(key)
        if handle:
            anchor = '</h1><p class="seo-product__descriptor mono">'
            i = s.find(anchor)
            assert i > 0, relpath
            j = s.find('</p>', i + len(anchor)) + 4
            s = s[:j] + f'<p class="mono seo-lang-switch"><a href="{esu}">Leé esta página en español</a></p>' + s[j:]
        else:
            m = re.search(r'(FLYLYFE · UPDATED [0-9-]+</p>)', s)
            assert m, relpath
            s = s.replace(m.group(1), m.group(1) + f'<p class="mono seo-lang-switch"><a href="{esu}">Leé esta nota en español</a></p>', 1)
        open(p, 'w').write(s)
        print(f'{relpath}: hreflang + cross-link added')
    # homepage footer Español link
    p = f'{ROOT}/index.html'
    s = open(p).read()
    if 'href="es/"' not in s:
        old = '<a href="llms.txt">AI / LLM facts</a>'
        assert s.count(old) == 1
        s = s.replace(old, '<a href="es/">Español</a>' + old)
        open(p, 'w').write(s)
        print('homepage footer: Español link added')

def patch_sitemap():
    p = f'{ROOT}/sitemap.xml'
    s = open(p).read()
    urls = [es_url('hub')] + [es_url(k) for k in ('pdp-malvinas', 'pdp-campeones', 'article')]
    add = ''.join(f'<url><loc>{u}</loc><lastmod>{TODAY}</lastmod></url>' for u in urls if f'<loc>{u}</loc>' not in s)
    assert '</urlset>' in s
    s = s.replace('</urlset>', add + '</urlset>')
    open(p, 'w').write(s)
    print(f'sitemap: +{add.count("<url>")} ES urls')

def patch_llms():
    p = f'{ROOT}/llms.txt'
    s = open(p).read()
    if '## En español' in s:
        print('llms.txt already has ES section'); return
    block = ['\n## En español (Spanish pages)',
             f'- Página principal en español: {es_url("hub")}']
    for k in ('pdp-malvinas', 'pdp-campeones', 'article'):
        pkg = PAGES[k][0]
        block.append(f'- {pkg["h1"]} — {pkg["metaDescription"]} — {es_url(k)}')
    block.append('- Las remeras Las Malvinas y Las Malvinas Campeones cuestan USD $39.99 y se envían a Argentina (producción 7–10 días hábiles; envío internacional se calcula al pagar).')
    s = s.rstrip('\n') + '\n' + '\n'.join(block) + '\n'
    open(p, 'w').write(s)
    print('llms.txt: ES section added')

if __name__ == '__main__':
    for key, builder in [('pdp-malvinas', build_pdp), ('pdp-campeones', build_pdp), ('article', build_article), ('hub', build_hub)]:
        out = builder(key) if builder is build_pdp else builder()
        slug = SLUGS[key]
        d = f'{ROOT}/es/{slug}' if slug else f'{ROOT}/es'
        os.makedirs(d, exist_ok=True)
        open(f'{d}/index.html', 'w').write(out)
        print(f'WROTE {d}/index.html ({len(out)} bytes)')
    localize_product_js()
    patch_en_pages()
    patch_sitemap()
    patch_llms()
    print('DONE')
