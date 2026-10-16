#!/usr/bin/env python3
"""Build discovery/fit pages from checked-in product facts. Run from any directory.

Install tools/requirements-shopping.txt, then run this file (or --check).
Keep curated graphic notes here; names, prices and images come from product pages.
Measurements match the verified October 15, 2026 garment charts in product-page.js.
This never changes Shopify products, variants, inventory or checkout.
"""
from __future__ import annotations

import argparse
from decimal import Decimal
from html import escape
import json
from pathlib import Path
import re

from bs4 import BeautifulSoup
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://www.flylyfe.com"
VERSION = "20261015-audit-v1"
THEMES = {"house": "House music", "nyc": "NYC", "heritage": "Heritage"}
DESIGNS = [
    ("the-brownstone-dj-tee", "house nyc", "A turntable, a flight case, a Brooklyn stoop. Concrete Rhythm, worn out loud.", "dj vinyl records crate digger turntable brooklyn stoop concrete rhythm"),
    ("the-anthem-tee", "house", "Feel The Music. Feel the Vibe. Live Your Lyfe. The FLYLYFE mantra, worn out loud.", "feel music vibe mantra slogan"),
    ("the-soul-tee", "house", "House is a feeling. A soulful silhouette for the people who move to it.", "house is a feeling soul afro silhouette"),
    ("the-conga-tee", "house", "A dancer, a conga, and the percussion that makes you move.", "afro house dancer conga percussion drums"),
    ("the-house-music-tee", "house", "Not everyone understands house music. A front-and-back manifesto for those who do.", "not everyone understands house music manifesto"),
    ("the-after-hours-tee", "house nyc", "The late set lives on. A DJ set-list graphic built around after-hours culture.", "after hours late night setlist dj nightlife drop 02"),
    ("the-tempo-tee", "house", "124 BPM. A waveform that puts the rhythm front and center.", "124 bpm waveform rhythm drop 02"),
    ("the-spiritual-thing-tee", "house", "A body thing. A soul thing. The house-music mantra, in print.", "spiritual thing body soul house mantra drop 02"),
    ("the-coordinates-tee", "nyc", "40.7128°N, 74.0060°W. Carry a little New York wherever the night takes you.", "new york city coordinates latitude longitude drop 02"),
    ("the-token-tee", "nyc", "The NYC subway token, reimagined in antique bronze.", "new york subway token transit vintage bronze"),
    ("the-sanitary-code-tee", "nyc", "No Smoking. No Spitting. A familiar piece of vintage New York signage.", "new york subway sanitary code no smoking spitting vintage sign"),
    ("the-signature-tee", "house", "Keep it simple. The FLYLYFE wordmark, with room for your own style.", "signature minimal minimalist logo wordmark classic"),
    ("las-malvinas-tee", "heritage", "Las Malvinas Son Argentinas. Hand-painted lettering with a heritage message.", "argentina argentine las malvinas son argentinas heritage banner"),
    ("las-malvinas-campeones-tee", "heritage", "Three stars. 1978, 1986, 2022. Argentina’s champions, in gold.", "argentina argentine campeones champions three 3 stars 1978 1986 2022 heritage"),
]
RELAXED = [["S", "18.25", "26.625"], ["M", "20.25", "28"], ["L", "22", "29.375"], ["XL", "24", "30.75"], ["2XL", "26", "31.625"], ["3XL", "27.75", "32.5"]]
FITTED = [["S", "16", "26.25"], ["M", "16.75", "26.75"], ["L", "17.75", "27.375"], ["XL", "18.75", "28"], ["2XL", "19.75", "28.625"]]


def product(handle):
    source = BeautifulSoup((ROOT / "products" / handle / "index.html").read_text(), "html.parser")
    for script in source.select('script[type="application/ld+json"]'):
        data = json.loads(script.string)
        nodes = data if isinstance(data, list) else data.get("@graph", [data])
        for node in nodes:
            if node.get("@type") == "Product":
                return source, node
    raise ValueError(f"No Product facts for {handle}")


def shell(slug, title, description, body, schema=None, image="/assets/products-seo/the-brownstone-dj-tee.webp"):
    url = ORIGIN + "/" + slug + "/"
    label = "Find your vibe" if slug == "find-your-vibe" else "Fit guide"
    graph = [{"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": ORIGIN + "/"},
        {"@type": "ListItem", "position": 2, "name": label, "item": url},
    ]}] + (schema or [])
    nav = [("/#shop", "Shop"), ("/collections/mens/", "Men’s"), ("/collections/womens/", "Women’s"),
           ("/find-your-vibe/", "Find your vibe"), ("/fit-guide/", "Fit guide"), ("/blog/", "Journal"), ("/about.html", "About"), ("/faq.html", "FAQ")]
    links = "".join(f'<a href="{href}"'+(' aria-current="page"' if href == f'/{slug}/' else '')+f'>{text}</a>' for href, text in nav)
    return f'''<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escape(title)}</title><meta name="description" content="{escape(description, quote=True)}">
<link rel="canonical" href="{url}"><meta property="og:type" content="website"><meta property="og:site_name" content="FLYLYFE">
<meta property="og:title" content="{escape(title, quote=True)}"><meta property="og:description" content="{escape(description, quote=True)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{ORIGIN}{image}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{escape(title, quote=True)}"><meta name="twitter:description" content="{escape(description, quote=True)}"><meta name="twitter:image" content="{ORIGIN}{image}">
<meta name="theme-color" content="#080808"><link rel="icon" type="image/png" href="/assets/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:ital,wght@0,400;0,600;0,700&family=Anton&family=JetBrains+Mono:wght@400;500&display=swap" media="print" onload="this.media='all'"><noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:ital,wght@0,400;0,600;0,700&family=Anton&family=JetBrains+Mono:wght@400;500&display=swap"></noscript>
<link rel="stylesheet" href="/css/style.css?v={VERSION}"><link rel="stylesheet" href="/css/customer-experience.css?v={VERSION}"><link rel="stylesheet" href="/css/shopping-guides.css?v={VERSION}">
<script type="application/ld+json">{json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False, separators=(',', ':'))}</script>
<script defer src="/js/analytics.js?v={VERSION}"></script><script defer src="/js/site-shell.js?v={VERSION}"></script><script defer src="/js/shopping-guides.js?v={VERSION}"></script>
</head><body>
<a class="skip-link" href="#main-content">Skip to content</a>
<header class="nav"><a class="nav__logo" href="/" aria-label="FLYLYFE home"><img src="/assets/print/flylyfe-wordmark-gold-web.png" alt="FLYLYFE" class="nav__logo-img" width="405" height="40"></a><nav class="nav__links" aria-label="Main">{links}</nav></header>
<main id="main-content" tabindex="-1" class="shopping-guide">
<nav class="guide-breadcrumb mono" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span><span aria-current="page">{label}</span></nav>
{body}
</main>
<footer class="footer"><div class="footer__top"><div class="footer__brandcol"><div class="footer__brand"><img src="/assets/print/flylyfe-wordmark-gold-web.png" alt="FLYLYFE" class="footer__brand-img" width="405" height="40"></div><p class="footer__tagline mono">Feel The Music Feel the Vibe Live Your Lyfe</p><p class="footer__est mono">NEW YORK CITY · WORLDWIDE · EST. 2007</p></div><div class="footer__cols"><div class="footer__col"><p class="footer__heading mono">EXPLORE</p>{links}</div><div class="footer__col"><p class="footer__heading mono">HELP</p><a href="/faq.html#shipping">Shipping</a><a href="/faq.html#returns">Returns</a><a href="mailto:hello@flylyfe.com">Contact</a><a href="/privacy.html">Privacy</a><a href="/terms.html">Terms</a></div></div></div><div class="footer__bottom"><p class="footer__fine mono">© 2026 FLYLYFE. All rights reserved.</p><p class="footer__fine mono">Born on the dance floor — NYC.</p></div></footer>
</body></html>
'''


def finder():
    cards, items = [], []
    actual_handles = {p.parent.name for p in (ROOT / "products").glob("*/index.html") if "-womens" not in p.parent.name}
    if actual_handles != {row[0] for row in DESIGNS}:
        raise ValueError("Product catalog changed; update curated DESIGNS before rebuilding")
    for index, (handle, themes, note, keywords) in enumerate(DESIGNS, 1):
        _, data = product(handle)
        name = data["name"]
        choices = [(handle, "Men’s"), (handle + "-womens", "Women’s relaxed"), (handle + "-womens-fitted", "Women’s fitted")]
        prices = [Decimal(product(h)[1]["offers"]["price"]) for h, _ in choices]
        price = ("From " if len(set(prices)) > 1 else "") + f"${min(prices):.2f} USD"
        image = f"/assets/products-seo/{handle}.webp"
        width, height = Image.open(ROOT / image.lstrip("/")).size
        thumb = f"/assets/responsive/{handle}-480.webp"
        if not (ROOT / thumb.lstrip("/")).exists():
            raise ValueError(f"Missing responsive card image for {handle}")
        tags = " · ".join(THEMES[t] for t in themes.split())
        options = "".join(f'<a href="/products/{h}/" aria-label="{escape(name, quote=True)} — {label}">{label}<span aria-hidden="true"> ↗</span></a>' for h, label in choices)
        cards.append(f'''<article class="vibe-card" data-vibes="{themes}" data-search="{escape(name + ' ' + note + ' ' + keywords, quote=True)}">
<a class="vibe-card__image" href="/products/{handle}/" aria-label="View {escape(name, quote=True)}"><img src="{image}" srcset="{thumb} 480w, {image} {width}w" sizes="(max-width:620px) 90vw, (max-width:1000px) 44vw, 29vw" width="{width}" height="{height}" alt="{escape(name, quote=True)} — design shown in the men’s relaxed cut" loading="lazy" decoding="async"></a>
<div class="vibe-card__body"><p class="vibe-card__theme mono">{tags}</p><h2><a href="/products/{handle}/">{escape(name)}</a></h2><p class="vibe-card__note">{escape(note)}</p><p class="vibe-card__price mono">{price}</p><p class="vibe-card__label">Choose your collection</p><div class="vibe-card__choices">{options}</div></div></article>''')
        items.append({"@type": "ListItem", "position": index, "name": name, "url": ORIGIN + f"/products/{handle}/"})
    body = '''<header class="guide-hero">
<p class="guide-eyebrow mono">THE GRAPHIC COMES FIRST</p><h1>FIND YOUR <span>VIBE.</span></h1>
<p>For the house heads. The city kids. The ones who wear where they’re from. Explore all 14 designs, then choose your fit.</p>
<a class="guide-text-link" href="/fit-guide/">Two cuts. Three collection choices. Compare the fits <span aria-hidden="true">→</span></a>
</header>
<section class="vibe-finder" aria-label="Browse FLYLYFE designs" data-vibe-finder>
<form class="vibe-controls" role="search" hidden data-vibe-controls>
<div class="vibe-search"><label for="vibeSearch">Search designs</label><input type="search" id="vibeSearch" name="q" maxlength="200" placeholder="Try Brownstone, 124 BPM, Argentina…" autocomplete="off" aria-controls="vibeResults"></div>
<fieldset class="vibe-themes"><legend>Choose your vibe</legend><div class="guide-chips"><button type="button" data-theme="all" aria-pressed="true">All designs</button><button type="button" data-theme="house" aria-pressed="false">House music</button><button type="button" data-theme="nyc" aria-pressed="false">NYC</button><button type="button" data-theme="heritage" aria-pressed="false">Heritage</button></div></fieldset>
<div class="vibe-status-row"><p data-vibe-count role="status" aria-live="polite" aria-atomic="true">14 designs</p><button type="reset" class="guide-reset">Clear filters</button></div></form>
<noscript><p class="guide-note">All 14 designs are below. Each design links to men’s, women’s relaxed, and women’s fitted options.</p></noscript>
<p class="vibe-empty" data-vibe-empty hidden>No designs match yet. Try a name or graphic, or clear the filters to see the whole collection.</p>
<div class="vibe-grid" id="vibeResults">''' + "\n".join(cards) + '''</div>
</section>
<aside class="guide-bottom"><p class="guide-eyebrow mono">PRINTED FOR YOU</p><h2>Pick the graphic. Make it yours.</h2><p>Every design comes in men’s relaxed, women’s relaxed, and women’s fitted collections. Choose your color and size on the product page. Printed to order in 7–10 business days, plus delivery.</p><a class="guide-text-link" href="/faq.html#shipping">Shipping &amp; delivery <span aria-hidden="true">→</span></a></aside>'''
    return shell("find-your-vibe", "Find Your Vibe | Browse All 14 FLYLYFE Tee Designs", "Find your FLYLYFE graphic tee by name or vibe: house music, NYC and Argentina heritage. Explore 14 designs, then choose men’s, women’s relaxed or fitted.", body, [{"@type": "CollectionPage", "name": "Find your vibe", "url": ORIGIN + "/find-your-vibe/", "mainEntity": {"@type": "ItemList", "numberOfItems": len(items), "itemListElement": items}}])


def size_table(rows, label, garment):
    cells = []
    for size, width, length in rows:
        cells.append(f'<tr><th scope="row">{size}</th><td data-inches="{width}">{width}</td><td data-inches="{length}">{length}</td></tr>')
    return f'''<div class="guide-table-wrap"><table><caption>{label} — {garment}</caption><thead><tr><th scope="col">Size</th><th scope="col">Chest width (<span data-unit-label>in</span>)</th><th scope="col">Body length (<span data-unit-label>in</span>)</th></tr></thead><tbody>{''.join(cells)}</tbody></table></div>'''


def fit_guide():
    # Guard against silently diverging from product purchasing controls.
    source = (ROOT / "js/product-page.js").read_text()
    match = re.search(r"const rows=fitted\s*\?\s*(\[\[.*?\]\])\s*:\s*(\[\[.*?\]\]);", source)
    if not match or json.loads(match[1]) != FITTED or json.loads(match[2]) != RELAXED:
        raise ValueError("Verified product size charts changed; reconcile guide measurements first")
    body = '''<header class="guide-hero"><p class="guide-eyebrow mono">SAME ENERGY. YOUR FIT.</p><h1>FIND YOUR <span>FIT.</span></h1><p>Two cuts. Three collection choices. Men’s and women’s relaxed tees share the same heavyweight unisex blank. Women’s fitted tees use a different, slimmer lightweight blank.</p><nav class="guide-jumps" aria-label="Fit guide sections"><a href="#compare-cuts">Compare the cuts ↓</a><a href="#size-charts">Jump to size charts ↓</a></nav></header>
<section class="fit-visual" aria-label="Compare the relaxed and fitted silhouettes"><div class="fit-visual__grid"><figure><img src="/assets/responsive/womens-relaxed-models/anthem-black-768.webp" srcset="/assets/responsive/womens-relaxed-models/anthem-black-768.webp 768w, /assets/responsive/womens-relaxed-models/anthem-black-1152.webp 1152w" sizes="(max-width:620px) 90vw, 680px" width="1536" height="1024" alt="Illustrative mockup of the Anthem Tee in Black, women’s relaxed cut, front view" decoding="async"><figcaption>Relaxed · Comfort Colors 1717</figcaption></figure><figure><img src="/assets/responsive/womens-fitted-models/anthem-black-768.webp" srcset="/assets/responsive/womens-fitted-models/anthem-black-768.webp 768w, /assets/responsive/womens-fitted-models/anthem-black-1152.webp 1152w" sizes="(max-width:620px) 90vw, 680px" width="1536" height="1024" alt="Illustrative mockup of the Anthem Tee in Black, women’s fitted cut, front view" decoding="async"><figcaption>Fitted · Bella + Canvas 6004</figcaption></figure></div><p class="guide-note">Same design, same color: The Anthem Tee in Black. These product mockups illustrate the cuts; use the garment measurements below to choose your size.</p></section>
<section class="fit-comparison" id="compare-cuts" aria-label="Compare the two cuts">
<article class="fit-panel"><p class="guide-eyebrow mono">01 — RELAXED</p><h2>Room to move.</h2><p class="fit-panel__intro">An easy drape in heavyweight, garment-dyed cotton.</p><dl><div><dt>Garment</dt><dd>Comfort Colors 1717</dd></div><div><dt>Feel</dt><dd>Heavyweight, 100% ring-spun cotton</dd></div><div><dt>Cut</dt><dd>Relaxed unisex</dd></div><div><dt>Sizes</dt><dd>S–3XL</dd></div><div><dt>Colors</dt><dd>Black, White, Ivory</dd></div></dl><p>Choose this cut for a roomier shape. Men’s and women’s relaxed use the same garment measurements.</p><div class="fit-panel__links"><a href="/collections/mens/">Shop men’s relaxed <span aria-hidden="true">↗</span></a><a href="/collections/womens/#relaxed">Shop women’s relaxed <span aria-hidden="true">↗</span></a></div></article>
<article class="fit-panel fit-panel--fitted"><p class="guide-eyebrow mono">02 — FITTED</p><h2>Closer to you.</h2><p class="fit-panel__intro">A slimmer silhouette in soft, lightweight cotton.</p><dl><div><dt>Garment</dt><dd>Bella + Canvas 6004</dd></div><div><dt>Feel</dt><dd>Lightweight Airlume cotton</dd></div><div><dt>Cut</dt><dd>Women’s fitted</dd></div><div><dt>Sizes</dt><dd>S–2XL</dd></div><div><dt>Colors</dt><dd>Black, White, Soft Cream</dd></div></dl><p><strong>Runs small.</strong> Check the measurements below against a tee you own; the same size letter has different measurements in the relaxed cut.</p><div class="fit-panel__links"><a href="/collections/womens/#fitted">Shop women’s fitted <span aria-hidden="true">↗</span></a></div></article>
</section>
<section class="fit-measure" aria-labelledby="measureTitle"><div><p class="guide-eyebrow mono">START WITH A TEE YOU LOVE</p><h2 id="measureTitle">Measure. Compare. Choose.</h2><p>These are garment measurements, not body measurements. Lay a tee flat without stretching it, then compare it with the right chart. The same size letter can feel very different between cuts.</p></div><ol><li><strong>Lay it flat.</strong> Smooth out a tee that fits how you like.</li><li><strong>Measure the width.</strong> Measure straight across the chest. For the relaxed chart, measure one inch below the armhole. This is the flat width, not a chest circumference.</li><li><strong>Measure the length.</strong> Measure from the high point of the shoulder to the hem; the relaxed chart uses the back hem.</li></ol></section>
<section class="fit-charts" id="size-charts" aria-labelledby="chartsTitle" data-fit-charts><div class="fit-charts__heading"><div><p class="guide-eyebrow mono">GARMENT MEASUREMENTS</p><h2 id="chartsTitle">Check your size.</h2></div><div class="guide-chips" role="group" aria-label="Measurement units" data-unit-controls hidden><button type="button" data-unit="in" aria-pressed="true">Inches</button><button type="button" data-unit="cm" aria-pressed="false">Centimeters</button></div></div><p class="guide-note" data-unit-note role="status">Measurements in inches. Compare the garment dimensions with a tee you own.</p><div class="fit-charts__grid">''' + size_table(RELAXED, "Men’s & women’s relaxed", "Comfort Colors 1717") + size_table(FITTED, "Women’s fitted", "Bella + Canvas 6004") + '''</div><p class="guide-note">Garment dimensions are approximate. Centimeters are converted from the inch chart and rounded to one decimal. Fit is personal; these charts help you compare, rather than predict a guaranteed fit.</p></section>
<aside class="guide-bottom"><p class="guide-eyebrow mono">NOW FIND YOUR GRAPHIC</p><h2>Fourteen designs. Your kind of energy.</h2><p>Explore house music, NYC, and heritage graphics. Every design comes in all three collection choices.</p><a class="guide-solid-link" href="/find-your-vibe/">Find your vibe <span aria-hidden="true">→</span></a><p class="guide-note">Printed to order in 7–10 business days, plus delivery. <a href="/faq.html#shipping">Shipping</a> · <a href="/faq.html#returns">30-day returns</a> on unworn, unwashed tees; customer pays return shipping.</p></aside>'''
    return shell("fit-guide", "FLYLYFE Fit & Size Guide | Relaxed vs Fitted Tees", "Compare FLYLYFE’s relaxed heavyweight and women’s fitted lightweight tees. See garment measurements in inches or centimeters and learn how to measure your tee.", body, [{"@type": "WebPage", "name": "FLYLYFE fit and size guide", "url": ORIGIN + "/fit-guide/", "about": {"@type": "Thing", "name": "FLYLYFE relaxed and fitted tee measurements"}}])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if generated pages differ")
    args = parser.parse_args()
    failures = []
    for slug, content in [("find-your-vibe", finder()), ("fit-guide", fit_guide())]:
        path = ROOT / slug / "index.html"
        if args.check:
            if not path.exists() or path.read_text() != content:
                failures.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(exist_ok=True)
            path.write_text(content)
            print(f"Built {path.relative_to(ROOT)}")
    if failures:
        raise SystemExit("Shopping pages need rebuilding: " + ", ".join(failures))
    if args.check:
        print("Shopping pages match product facts and verified size charts.")


if __name__ == "__main__":
    main()
