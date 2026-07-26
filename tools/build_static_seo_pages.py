#!/usr/bin/env python3
from pathlib import Path
from html import escape, unescape
from datetime import date
import json, re

def E(s):
    return escape(unescape(str(s)))

ROOT = Path(__file__).resolve().parents[1]
TODAY = "2026-07-07"
ASSET_V = "20260707-print-parity"
BASE = "https://www.flylyfe.com"
PRICE = "49.99"

products = [
  {"handle":"the-anthem-tee","name":"The Anthem Tee","group":"mens","collection":"Men's","colors":"Black, White, Ivory","sizes":"S–3XL","image":"assets/products-seo/the-anthem-tee.jpg","short":"The mantra tee: Feel the Music. Feel the Vibe. Live Your Lyfe.","desc":"The Anthem Tee carries the FLYLYFE mantra across a premium cotton streetwear fit. Built for house-music fans, DJs, dancers, and late-night New York energy, it is the most direct expression of the brand: feel the music, feel the vibe, live your lyfe.","fit":"Men's premium cotton streetwear fit with a relaxed drop. True to size; size down for a cleaner classic fit.","style":"Wear it with black denim, cargos, or layered under a jacket for club nights, festivals, and everyday NYC streetwear.","related":["the-house-music-tee","the-conga-tee","the-signature-tee"]},
  {"handle":"the-conga-tee","name":"The Conga Tee","group":"mens","collection":"Men's","colors":"Black, White, Ivory","sizes":"S–3XL","image":"assets/products-seo/the-conga-tee.jpg","short":"Dancer and conga artwork — the rhythm on your back.","desc":"The Conga Tee is FLYLYFE's rhythm piece: dancer, percussion, movement, and nightlife culture translated into a wearable house-music graphic. It is built for people who understand the connection between the drum, the floor, and the city.","fit":"Men's premium cotton streetwear fit with a relaxed drop. True to size; size down for a cleaner classic fit.","style":"Best with dark denim, cargos, or layered overshirts. A strong choice for dance floors, DJ sets, and house-music events.","related":["the-anthem-tee","the-house-music-tee","the-conga-tee-womens"]},
  {"handle":"the-signature-tee","name":"The Signature Tee","group":"mens","collection":"Men's","colors":"Black, White, Ivory","sizes":"S–3XL","image":"assets/products-seo/the-signature-tee.jpg","short":"The clean FLYLYFE wordmark tee — minimal, sharp, and classic.","desc":"The Signature Tee is the clean brand essential: FLYLYFE geometry, premium cotton, and a minimal look that works in the city, at the lounge, or at the after-hours set. It is the easiest entry point into the FLYLYFE uniform.","fit":"Men's premium cotton streetwear fit with a relaxed drop. True to size; size down for a cleaner classic fit.","style":"The everyday piece: wear it solo, under a bomber, or with tailored streetwear basics.","related":["the-anthem-tee","the-token-tee","the-signature-tee-womens"]},
  {"handle":"the-house-music-tee","name":"The House Music Tee","group":"mens","collection":"Men's","colors":"Black, White, Ivory","sizes":"S–3XL","image":"assets/products-seo/the-house-music-tee.jpg","short":"Not everyone understands house music — a spiritual thing, a body thing, a soul thing.","desc":"The House Music Tee is FLYLYFE's signature statement piece. The front says what every house head knows — not everyone understands house music — while the back carries the manifesto: a spiritual thing, a body thing, a soul thing.","fit":"Men's premium cotton streetwear fit with a relaxed drop. True to size; size down for a cleaner classic fit.","style":"Made for house-music fans, DJs, dancers, club nights, festivals, and anyone who treats the dance floor like a second home.","related":["the-anthem-tee","the-spiritual-thing-tee","the-token-tee"]},
  {"handle":"the-soul-tee","name":"The Soul Tee","group":"mens","collection":"Men's","colors":"White, Ivory, Black","sizes":"S–3XL","image":"assets/products-seo/the-soul-tee.jpg","short":"House is a feeling — a soulful afro-silhouette back print: feel the music, feel the vibe, live your lyfe.","desc":"The Soul Tee is FLYLYFE's most soulful statement piece. A striking afro-silhouette with a gold hoop crowns the back over the words HOUSE IS A FEELING — feel the music, feel the vibe, live your lyfe — while a clean FLYLYFE mark sits up front. It is for the heads who feel house as something deeper than a genre.","fit":"Men's premium cotton streetwear fit with a relaxed drop. True to size; size down for a cleaner classic fit.","style":"Wear it with black denim, cargos, or layered under a jacket for club nights, festivals, and everyday NYC streetwear.","related":["the-house-music-tee","the-anthem-tee","the-spiritual-thing-tee"]},
  {"handle":"the-token-tee","name":"The Token Tee","group":"mens","collection":"Men's","colors":"Ivory, Black, White","sizes":"S–3XL","image":"assets/products-seo/the-token-tee.jpg","short":"NYC subway-token inspiration with FLYLYFE antique-bronze energy.","desc":"The Token Tee reimagines the New York subway token through the FLYLYFE lens. Antique-bronze print energy, NYC movement, and house-music culture come together in a premium graphic tee built for the city.","fit":"Men's premium cotton streetwear fit with a relaxed drop. True to size; size down for a cleaner classic fit.","style":"Pair with black denim, vintage sneakers, or layered outerwear for a city-forward streetwear look.","related":["the-signature-tee","the-coordinates-tee","the-house-music-tee"]},
  {"handle":"the-anthem-tee-womens","name":"The Anthem Tee — Women's","group":"womens","collection":"Women's","colors":"Black, White, Natural","sizes":"S–2XL","image":"assets/products-seo/the-anthem-tee-womens.jpg","short":"The FLYLYFE mantra in a women's relaxed cotton cut.","desc":"The women's Anthem Tee brings the FLYLYFE mantra to a relaxed cotton cut with the same dance-floor spirit: Feel the Music. Feel the Vibe. Live Your Lyfe.","fit":"Women's relaxed premium cotton fit with a softer drape. True to size for relaxed; size down for closer fit.","style":"Style it with denim, cargos, biker shorts, or layered under an oversized jacket.","related":["the-conga-tee-womens","the-signature-tee-womens","the-anthem-tee"]},
  {"handle":"the-conga-tee-womens","name":"The Conga Tee — Women's","group":"womens","collection":"Women's","colors":"Black, White, Natural","sizes":"S–2XL","image":"assets/products-seo/the-conga-tee-womens.jpg","short":"Dancer and conga artwork in a women's relaxed cotton cut.","desc":"The women's Conga Tee turns rhythm, percussion, and dance-floor movement into a relaxed-cut house-music graphic tee.","fit":"Women's relaxed premium cotton fit with a softer drape. True to size for relaxed; size down for closer fit.","style":"Made for movement — style with denim, cargos, skirts, or festival-ready layers.","related":["the-anthem-tee-womens","the-signature-tee-womens","the-conga-tee"]},
  {"handle":"the-signature-tee-womens","name":"The Signature Tee — Women's","group":"womens","collection":"Women's","colors":"Black, White, Natural","sizes":"S–2XL","image":"assets/products-seo/the-signature-tee-womens.jpg","short":"The clean FLYLYFE wordmark in a women's relaxed fit.","desc":"The women's Signature Tee is the clean everyday FLYLYFE piece: minimal wordmark, relaxed fit, and the same NYC house-music DNA.","fit":"Women's relaxed premium cotton fit with a softer drape. True to size for relaxed; size down for closer fit.","style":"A simple brand staple for everyday streetwear, nights out, and layered looks.","related":["the-anthem-tee-womens","the-conga-tee-womens","the-signature-tee"]},
  {"handle":"the-after-hours-tee","name":"The After Hours Tee","group":"drop-02","collection":"Drop 02","colors":"Black","sizes":"S–3XL","image":"assets/products-seo/the-after-hours-tee.jpg","short":"DROP 02 — the set that never stops.","desc":"The After Hours Tee is a DROP 02 piece inspired by the late set: midnight, basement rooms, sunrise rides, and last-train-home energy.","fit":"Premium cotton streetwear fit, sizes S–3XL. True to size with a relaxed drop.","style":"Built for the all-night uniform — black denim, cargos, sneakers, and a jacket after sunrise.","related":["the-tempo-tee","the-spiritual-thing-tee","the-coordinates-tee"]},
  {"handle":"the-tempo-tee","name":"The Tempo Tee","group":"drop-02","collection":"Drop 02","colors":"Black","sizes":"S–3XL","image":"assets/products-seo/the-tempo-tee.jpg","short":"DROP 02 — 124 BPM, the tempo of the city.","desc":"The Tempo Tee turns 124 BPM into a wearable signal for house heads: the city pulse, the club rhythm, and the movement that keeps going.","fit":"Premium cotton streetwear fit, sizes S–3XL. True to size with a relaxed drop.","style":"A clean graphic for DJs, producers, dancers, and fans who know the tempo by feel.","related":["the-after-hours-tee","the-coordinates-tee","the-house-music-tee"]},
  {"handle":"the-coordinates-tee","name":"The Coordinates Tee","group":"drop-02","collection":"Drop 02","colors":"Ivory","sizes":"S–3XL","image":"assets/products-seo/the-coordinates-tee.jpg","short":"DROP 02 — 40.7128° N, 74.0060° W: New York City.","desc":"The Coordinates Tee anchors FLYLYFE to New York City with 40.7128° N, 74.0060° W — the place, pulse, and nightlife energy behind the brand.","fit":"Premium cotton streetwear fit, sizes S–3XL. True to size with a relaxed drop.","style":"A lighter statement piece that pairs well with black denim, cargos, and neutral layers.","related":["the-token-tee","the-tempo-tee","the-after-hours-tee"]},
  {"handle":"the-spiritual-thing-tee","name":"The Spiritual Thing Tee","group":"drop-02","collection":"Drop 02","colors":"Ivory","sizes":"S–3XL","image":"assets/products-seo/the-spiritual-thing-tee.jpg","short":"DROP 02 — a body thing, a soul thing.","desc":"The Spiritual Thing Tee expands the house-music manifesto into a DROP 02 graphic: not just a sound, but a body thing, a soul thing, and a way of moving through the night.","fit":"Premium cotton streetwear fit, sizes S–3XL. True to size with a relaxed drop.","style":"A strong pick for house-music fans, dancers, and anyone who feels the culture beyond the playlist.","related":["the-house-music-tee","the-after-hours-tee","the-tempo-tee"]},
  {"handle":"the-sanitary-code-tee","name":"The Sanitary Code Tee","group":"limited","collection":"Limited Edition","colors":"White","sizes":"S–3XL","image":"assets/products-seo/the-sanitary-code-tee.jpg","short":"Limited edition — vintage New York No Smoking / No Spitting sign concept.","desc":"The Sanitary Code Tee is a limited-edition New York concept piece inspired by vintage city signage: No Smoking, No Spitting, Sanitary Code Sect. 216.","fit":"Premium cotton streetwear fit, sizes S–3XL. True to size with a relaxed drop.","style":"A conversation piece for NYC streetwear collectors and fans of vintage city graphics.","related":["the-token-tee","the-coordinates-tee","the-signature-tee"]},
]
by_handle={p['handle']:p for p in products}
SEO=json.load(open(Path(__file__).resolve().parent/'seo_packages.json'))  # keyword-optimized content per handle
BLOG_RAW=json.load(open(Path(__file__).resolve().parent/'blog_posts.json'))
BLOG_ORDER=['what-is-house-music','nyc-house-music-streetwear-guide','nyc-subway-token-history','what-to-wear-house-music-festival','how-to-style-heavyweight-graphic-tee']
blog=[BLOG_RAW[s] for s in BLOG_ORDER if s in BLOG_RAW]
LINK_RE=re.compile(r'\[([^\]]+)\]\(product:([a-z0-9-]+)\)')
def render_prose(text, pref):
    out=[]; last=0
    for m in LINK_RE.finditer(text):
        out.append(E(text[last:m.start()]))
        anchor,h=m.group(1),m.group(2)
        out.append(f'<a href="{pref}products/{h}/">{E(anchor)}</a>' if h in by_handle else E(anchor))
        last=m.end()
    out.append(E(text[last:]))
    return ''.join(out)
collections = {
  'mens': {'title': "Men's House Music Streetwear", 'label': "Men's Collection", 'desc': "Men's FLYLYFE tees: premium cotton streetwear fits for house-music fans, DJs, dancers, and NYC nights.", 'handles':['the-anthem-tee','the-conga-tee','the-signature-tee','the-house-music-tee','the-soul-tee','the-token-tee'], 'path':'collections/mens/index.html',
   'copy': "<p>FLYLYFE men's tees are $49.99 heavyweight graphic tees printed to order on the garment-dyed Comfort Colors 1717 blank — DTF transfer prints made in Los Angeles, a tagless printed neck label, and sizes S–3XL. The five core styles live here: the Anthem, Conga, Signature, House Music, and Token tees.</p><p>Four more unisex styles run in <a href=\"../drop-02/\">Drop 02</a>, and one collector's piece lives in <a href=\"../limited/\">Limited Edition</a>.</p>"},
  'womens': {'title': "Women's Relaxed Tees", 'label': "Women's Collection", 'desc': "Women's relaxed FLYLYFE tees with premium cotton drape, house-music graphics, and NYC streetwear energy.", 'handles':['the-anthem-tee-womens','the-conga-tee-womens','the-signature-tee-womens'], 'path':'collections/womens/index.html',
   'copy': "<p>FLYLYFE women's tees carry the same house-music graphics in a relaxed cut — printed to order on the garment-dyed Comfort Colors 1717 blank in White, Black, and Natural, sizes S–2XL, $49.99. Every tee is DTF-printed in Los Angeles with a tagless printed neck label.</p>"},
  'drop-02': {'title': "DROP 02 — After Hours Collection", 'label': "Drop 02", 'desc': "DROP 02 brings after-hours sets, 124 BPM tempo, NYC coordinates, and the house-music manifesto into new FLYLYFE graphic tees.", 'handles':['the-after-hours-tee','the-tempo-tee','the-coordinates-tee','the-spiritual-thing-tee'], 'path':'collections/drop-02/index.html',
   'copy': "<p>DROP 02 is FLYLYFE's after-hours capsule: four graphic tees — After Hours, Tempo, Coordinates, and Spiritual Thing — built around late sets, 124 BPM, New York coordinates, and the house-music manifesto. Each is printed to order on the heavyweight Comfort Colors 1717 at $49.99, sizes S–3XL.</p>"},
  'limited': {'title': "Limited Edition FLYLYFE Tees", 'label': "Limited Edition", 'desc': "Limited-run FLYLYFE pieces inspired by New York City graphics, nightlife, and street culture.", 'handles':['the-sanitary-code-tee'], 'path':'collections/limited/index.html',
   'copy': "<p>Limited Edition is where FLYLYFE's New York artifacts live. The Sanitary Code Tee reproduces a vintage NYC transit sign — No Smoking, No Spitting, Sanitary Code Sect. 216 — in aged, rusted color on a white Comfort Colors 1717 heavyweight tee. Printed to order at $49.99, sizes S–3XL, with the tagless FLYLYFE neck label.</p>"},
  'house-music-streetwear': {'title': "House Music Streetwear", 'label': "House Music Streetwear", 'desc': "FLYLYFE house-music streetwear connects dance-floor culture, New York nightlife, and premium graphic tees made for people who feel the music.", 'handles':['the-house-music-tee','the-soul-tee','the-spiritual-thing-tee','the-anthem-tee','the-conga-tee','the-tempo-tee'], 'path':'collections/house-music-streetwear/index.html',
   'copy': "<p>House-music streetwear is apparel built around dance-floor culture — DJs, dancers, late sets, and the cities that never let the record stop. It's FLYLYFE's core. These five tees carry the manifesto: not everyone understands house music — it's a spiritual thing, a body thing, a soul thing.</p><p>Every piece is printed to order on the Comfort Colors 1717 heavyweight blank, $49.99, sizes S–3XL.</p>"},
  'house-music-festival-shirts': {'title': "House Music Festival & Rave Shirts", 'label': "Festival & Rave", 'desc': "House music festival and rave shirts built to dance in: heavyweight graphic tees for club nights, warehouse parties, and festival weekends. $49.99, printed in the USA.", 'handles':['the-anthem-tee','the-conga-tee','the-after-hours-tee','the-tempo-tee','the-spiritual-thing-tee'], 'path':'collections/house-music-festival-shirts/index.html',
   'copy': "<p>A house music festival shirt has one job: survive a full night on the dancefloor and still look good in the morning. These are FLYLYFE's rave and festival picks — heavyweight, garment-dyed Comfort Colors 1717 tees that breathe, hold their shape through crowd-press, and read loud from across a warehouse floor. Every one is DTF-printed to order in Los Angeles, USA, at $49.99 in sizes S–3XL.</p><p>Not sure what to pack? Our guide on <a href=\"../../blog/what-to-wear-house-music-festival/\">what to wear to a house music festival</a> breaks down the full fit — layers, footwear, and the tees that anchor it.</p>"},
  'dj-tees': {'title': "DJ & Producer T-Shirts", 'label': "DJ & Producer", 'desc': "DJ and producer t-shirts for the booth, the studio, and the dancefloor — house-music graphic tees that read loud from behind the decks. $49.99, printed to order in the USA.", 'handles':['the-house-music-tee','the-anthem-tee','the-tempo-tee','the-signature-tee','the-conga-tee'], 'path':'collections/dj-tees/index.html',
   'copy': "<p>A good DJ t-shirt says what you're about before you drop the first record. These are FLYLYFE's picks for DJs, producers, and selectors — from the 124-BPM waveform of the Tempo Tee to the clean wordmark of the Signature Tee — all printed on the heavyweight, garment-dyed Comfort Colors 1717 blank at $49.99, sizes S–3XL, DTF-printed to order in Los Angeles.</p><p>New to the culture or explaining it to someone who is? Start with <a href=\"../../blog/what-is-house-music/\">what house music actually is</a> and where it came from.</p>"},
  'nyc-streetwear-tees': {'title': "NYC Streetwear Tees", 'label': "NYC Streetwear", 'desc': "NYC streetwear tees rooted in New York subway culture, coordinates, and nightlife — heavyweight garment-dyed graphic tees printed to order. $49.99, ships worldwide.", 'handles':['the-token-tee','the-coordinates-tee','the-sanitary-code-tee','the-signature-tee','the-house-music-tee'], 'path':'collections/nyc-streetwear-tees/index.html',
   'copy': "<p>New York City streetwear is about carrying the city with you — the subway token, the coordinates, the vintage signage, the late train home. These FLYLYFE tees translate that into wearable graphics on the heavyweight Comfort Colors 1717 blank, garment-dyed and DTF-printed to order in Los Angeles at $49.99, sizes S–3XL.</p><p>The <a href=\"../../products/the-token-tee/\">Token Tee</a> leads the set — read <a href=\"../../blog/nyc-subway-token-history/\">the story of the NYC subway token</a>, the 1953-to-2003 icon it's built on, then explore the full <a href=\"../house-music-streetwear/\">house music streetwear</a> range.</p>"},
}

def rel_css(depth):
    prefix = '../'*depth
    return f'''<link rel="icon" type="image/png" href="{prefix}assets/favicon.png">\n<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:ital,wght@0,400;0,600;0,700&family=Anton&family=JetBrains+Mono:wght@400;500&display=swap">\n<link rel="stylesheet" href="{prefix}css/style.css?v={ASSET_V}">\n<link rel="stylesheet" href="{prefix}css/product.css?v={ASSET_V}">\n<link rel="stylesheet" href="{prefix}css/seo-pages.css?v={ASSET_V}">'''

def nav(depth):
    p='../'*depth
    home = f'{p}#top' if depth else 'index.html#top'
    shop = f'{p}#shop' if depth else 'index.html#shop'
    return f'''<header class="nav"><a class="nav__logo" href="{home}" aria-label="FLYLYFE home"><img src="{p}assets/print/flylyfe-wordmark-gold.png" alt="FLYLYFE" class="nav__logo-img" width="405" height="40"></a><nav class="nav__links" aria-label="Main"><a href="{shop}">Shop</a><a href="{p}collections/mens/">Men's</a><a href="{p}collections/womens/">Women's</a><a href="{p}collections/drop-02/">Drop 02</a><a href="{p}blog/">Blog</a><a href="{p}about.html">About</a><a href="{p}faq.html">FAQ</a></nav></header>'''

def footer(depth):
    p='../'*depth
    return f'''<footer class="footer"><div class="footer__top"><div class="footer__brandcol"><div class="footer__brand"><img src="{p}assets/print/flylyfe-wordmark-gold.png" alt="FLYLYFE" class="footer__brand-img" width="405" height="40"></div><p class="footer__tagline mono">FEEL THE MUSIC. FEEL THE VIBE. LIVE YOUR LYFE.</p><p class="footer__est mono">NEW YORK CITY · WORLDWIDE · EST. 2007</p></div><div class="footer__cols"><div class="footer__col"><p class="footer__heading mono">SHOP</p><a href="{p}collections/mens/">Men's</a><a href="{p}collections/womens/">Women's</a><a href="{p}collections/drop-02/">Drop 02</a><a href="{p}collections/limited/">Limited</a><a href="{p}collections/house-music-festival-shirts/">Festival &amp; Rave</a><a href="{p}collections/dj-tees/">DJ Tees</a><a href="{p}collections/nyc-streetwear-tees/">NYC Streetwear</a></div><div class="footer__col"><p class="footer__heading mono">BRAND</p><a href="{p}about.html">About</a><a href="{p}blog/">Blog</a><a href="{p}faq.html">FAQ</a><a href="{p}llms.txt">AI / LLM facts</a></div><div class="footer__col"><p class="footer__heading mono">HELP</p><a href="{p}faq.html#shipping">Shipping</a><a href="{p}faq.html#returns">Returns</a><a href="mailto:hello@flylyfe.com">Contact</a></div><div class="footer__col"><p class="footer__heading mono">LEGAL</p><a href="{p}privacy.html">Privacy</a><a href="{p}terms.html">Terms</a></div></div></div><div class="footer__bottom"><p class="footer__fine mono">© 2026 FLYLYFE. All rights reserved.</p><p class="footer__fine mono">Born on the dance floor — NYC.</p><p class="footer__fine mono">Website by <a href="https://clickmingo.com" target="_blank" rel="noopener">ClickMingo</a></p></div></footer>'''

def write(path, html):
    out=ROOT/path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding='utf-8')

def product_page(p):
    depth=2; pref='../../'
    sp=SEO[p['handle']]
    pk=sp['primaryKeyword']
    related=''.join(f'<a class="related-card" href="../{h}/"><img src="{pref}{by_handle[h]["image"]}" alt="{E(by_handle[h]["name"])} — FLYLYFE house music streetwear tee" loading="lazy"><span>{E(by_handle[h]["name"])}</span></a>' for h in p['related'] if h in by_handle)
    feat_html=''.join(f'<li><strong>{E(f["label"])}.</strong> {E(f["text"])}</li>' for f in sp['keyFeatures'])
    uc_html=''.join(f'<article><h3>{E(u["h3"])}</h3><p>{E(u["text"])}</p></article>' for u in sp['useCases'])
    faq_p_html=''.join(f'<details class="faq__item"><summary>{E(x["q"])}</summary><p>{E(x["a"])}</p></details>' for x in sp['faq'])
    links=[f'<a href="../{il["targetHandle"]}/">{E(il["anchor"])}</a>' for il in sp['internalLinks'] if il['targetHandle'] in by_handle]
    link_sentence=('Complete the fit — pair it with '+(", ".join(links[:-1])+", and "+links[-1] if len(links)>1 else links[0])+'.') if links else ''
    faq_schema_node={"@type":"FAQPage","@id":f"{BASE}/products/{p['handle']}/#faq","mainEntity":[{"@type":"Question","name":unescape(x["q"]),"acceptedAnswer":{"@type":"Answer","text":unescape(x["a"])}} for x in sp['faq']]}
    schema={"@context":"https://schema.org","@graph":[{"@type":"Product","@id":f"{BASE}/products/{p['handle']}/#product","name":p['name'],"brand":{"@type":"Brand","name":"FLYLYFE"},"category":"Apparel & Accessories > Clothing > Shirts & Tops","description":unescape(sp['metaDescription']),"image":[f"{BASE}/{p['image']}"],"url":f"{BASE}/products/{p['handle']}/","keywords":", ".join([pk]+sp['secondaryKeywords']),"material":"100% ring-spun cotton (Comfort Colors 1717, garment-dyed)","additionalProperty":[{"@type":"PropertyValue","name":"Sizes","value":p['sizes']},{"@type":"PropertyValue","name":"Colors","value":p['colors']},{"@type":"PropertyValue","name":"Blank","value":"Comfort Colors 1717 heavyweight"},{"@type":"PropertyValue","name":"Print method","value":"DTF transfer, printed to order in Los Angeles, USA"},{"@type":"PropertyValue","name":"Neck label","value":"Tagless printed inside-neck label"}],"audience":{"@type":"PeopleAudience","suggestedGender":"Unisex" if p['group'] not in ['mens','womens'] else ('Male' if p['group']=='mens' else 'Female')},"offers":{"@type":"Offer","price":PRICE,"priceCurrency":"USD","availability":"https://schema.org/InStock","itemCondition":"https://schema.org/NewCondition","url":f"{BASE}/products/{p['handle']}/"}},faq_schema_node,{"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":BASE+"/"},{"@type":"ListItem","position":2,"name":p['collection'],"item":BASE+"/collections/"+p['group']+"/"},{"@type":"ListItem","position":3,"name":p['name'],"item":f"{BASE}/products/{p['handle']}/"}]}]}
    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{E(sp['titleTag'])}</title><meta name="description" content="{E(sp['metaDescription'])}"><link rel="canonical" href="{BASE}/products/{p['handle']}/"><meta property="og:type" content="product"><meta property="og:site_name" content="FLYLYFE"><meta property="og:title" content="{E(sp['titleTag'])}"><meta property="og:description" content="{E(sp['metaDescription'])}"><meta property="og:url" content="{BASE}/products/{p['handle']}/"><meta property="og:image" content="{BASE}/{p['image']}"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{E(sp['titleTag'])}"><meta name="twitter:description" content="{E(sp['metaDescription'])}"><meta name="twitter:image" content="{BASE}/{p['image']}">{rel_css(depth)}<script type="application/ld+json">{json.dumps(schema,separators=(',',':'))}</script></head><body data-product-handle="{p['handle']}">{nav(depth)}<main class="seo-product"><section class="seo-product__hero"><div class="seo-product__media"><img src="{pref}{p['image']}" alt="{E(sp['imageAlt'])}" width="1100" height="1500" fetchpriority="high"></div><div class="seo-product__info"><p class="mono gold-text">{escape(p['collection'])} · FLYLYFE · EST. 2007</p><h1>{escape(p['name'])}</h1><p class="seo-product__descriptor mono">{E(sp['descriptor'])}</p><p class="seo-lede">{escape(p['desc'])}</p><p class="seo-price mono">$49.99 USD</p><p class="seo-specline mono">Colors: {escape(p['colors'])} · Sizes: {escape(p['sizes'])} · Comfort Colors 1717 heavyweight, garment-dyed · DTF-printed to order in Los Angeles, USA · Tagless printed neck label</p><div class="seo-commerce" data-commerce-root><p class="mono">LOADING LIVE COLOR, SIZE, ADD TO CART, AND CHECKOUT OPTIONS…</p><noscript><p class="mono">JavaScript is required for direct ADD TO CART and CHECKOUT on this product page. <a href="../../#shop">Shop on the main FLYLYFE storefront</a>.</p></noscript></div><div class="seo-trust mono"><span>✓ Printed in the USA</span><span>✓ Free US shipping on 2+ items</span><span>✓ Secure Shopify checkout</span></div></div></section><section class="seo-section"><h2>{E(pk)} — key features</h2><ul class="seo-features">{feat_html}</ul></section><section class="seo-section"><h2>Ways to wear this {E(pk)}</h2><div class="seo-grid">{uc_html}</div></section><section class="seo-section"><h2>Fit, feel, and styling</h2><div class="seo-grid"><article><h3>Fit</h3><p>{escape(p['fit'])}</p></article><article><h3>Material / feel</h3><p>Comfort Colors 1717 heavyweight, garment-dyed, 100% ring-spun cotton — chosen for streetwear structure, print clarity, and day-to-night wear. DTF transfer print made to order in Los Angeles, USA, with a tagless printed inside-neck label.</p></article><article><h3>How to wear it</h3><p>{escape(p['style'])}</p></article></div></section><section class="seo-section"><h2>{escape(p['name'])} — frequently asked questions</h2><div class="faq__list">{faq_p_html}</div></section><section class="seo-section"><h2>Shipping, returns, and care</h2><div class="seo-grid"><article><h3>Shipping</h3><p>FLYLYFE ships worldwide — international rates are shown at checkout. US shipping is a flat $4.75, and orders of 2 or more items ship free automatically. Every tee is printed to order; production typically takes 7–10 business days before it ships.</p></article><article><h3>Returns</h3><p>Every FLYLYFE tee is printed to order. Unworn, unwashed tees in original condition can be returned within 30 days of delivery for an exchange or refund — email hello@flylyfe.com to start a return.</p></article><article><h3>Care</h3><p>Wash cold inside-out and tumble dry low to preserve the print and garment color.</p></article></div></section><section class="seo-section"><h2>Related FLYLYFE pieces</h2>{f'<p class="seo-linkline">{link_sentence}</p>' if link_sentence else ''}<div class="related-grid">{related}</div></section></main>{footer(depth)}<script src="{pref}js/product-page.js?v={ASSET_V}" defer></script></body></html>'''

def collection_page(slug,c):
    depth=2; pref='../../'
    cards=''.join(f'<a class="collection-card" href="{pref}products/{h}/"><img src="{pref}{by_handle[h]["image"]}" alt="{escape(by_handle[h]["name"])}" loading="lazy"><span class="mono">$49.99</span><h2>{escape(by_handle[h]["name"])}</h2><p>{escape(by_handle[h]["short"])}</p></a>' for h in c['handles'])
    schema={"@context":"https://schema.org","@graph":[{"@type":"CollectionPage","@id":f"{BASE}/collections/{slug}/#collection","name":c['title'],"description":c['desc'],"url":f"{BASE}/collections/{slug}/","isPartOf":{"@type":"WebSite","name":"FLYLYFE","url":BASE+"/"},"mainEntity":{"@type":"ItemList","itemListElement":[{"@type":"ListItem","position":i+1,"url":f"{BASE}/products/{h}/","name":by_handle[h]['name']} for i,h in enumerate(c['handles'])]}}]}
    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{escape(c['title'])} | FLYLYFE</title><meta name="description" content="{escape(c['desc'])}"><link rel="canonical" href="{BASE}/collections/{slug}/"><meta property="og:type" content="website"><meta property="og:site_name" content="FLYLYFE"><meta property="og:title" content="{escape(c['title'])} | FLYLYFE"><meta property="og:description" content="{escape(c['desc'])}"><meta property="og:url" content="{BASE}/collections/{slug}/"><meta property="og:image" content="{BASE}/{by_handle[c['handles'][0]]['image']}"><meta name="twitter:card" content="summary_large_image">{rel_css(depth)}<script type="application/ld+json">{json.dumps(schema,separators=(',',':'))}</script></head><body>{nav(depth)}<main class="collection-page"><section class="collection-hero"><p class="mono gold-text">{escape(c['label'])} · FLYLYFE</p><h1>{escape(c['title'])}</h1><p>{escape(c['desc'])}</p></section><section class="collection-grid">{cards}</section><section class="seo-section"><h2>About the {escape(c['label'])}</h2>{c['copy']}</section></main>{footer(depth)}</body></html>'''

# --- DRIFT GUARD (added 2026-07-26) -----------------------------------------
# The LIVE site has pages hand-added after this generator was last authoritative:
# products las-malvinas-tee + the-brownstone-dj-tee, and collections concrete-rhythm
# + heritage. They are NOT in products/collections/seo_packages.json here, and footer()/
# nav() also omit concrete-rhythm + heritage + house-music-streetwear. A blind rebuild
# would DELETE these from sitemap.xml, llms.txt, and page footers/nav, silently de-indexing
# live revenue pages. Reconcile first (see project_flylyfe_pipeline_snapshot memory).
_PROT_P = {'las-malvinas-tee', 'the-brownstone-dj-tee'}
_PROT_C = {'concrete-rhythm', 'heritage'}
_miss = (_PROT_P - set(by_handle)) | (_PROT_C - set(collections))
if _miss:
    raise SystemExit("ABORT: generator drifted from live site; a rebuild would de-index " +
        str(sorted(_miss)) + ". Reconcile products/collections/seo_packages.json + footer()/nav() "
        "before regenerating, or delete this guard to override intentionally.")
# ---------------------------------------------------------------------------

for p in products:
    write(Path('products')/p['handle']/'index.html', product_page(p))
for slug,c in collections.items():
    write(Path(c['path']), collection_page(slug,c))

faq_items=[
("What is FLYLYFE?","FLYLYFE is a New York City house-music streetwear brand founded in 2007. It makes premium graphic tees inspired by house music, NYC nightlife, dance-floor culture, and the phrase Feel the Music. Feel the Vibe. Live Your Lyfe."),
("Is FLYLYFE one word?","Yes. FLYLYFE is always one word — not Fly Lyfe, FlyLife, or Flylife."),
("Where is FLYLYFE based?","FLYLYFE is based in New York City and ships worldwide through flylyfe.com."),
("What does FLYLYFE sell?","FLYLYFE sells premium cotton graphic tees including men's tees, women's relaxed tees, DROP 02 designs, and limited-edition New York-inspired pieces."),
("How much are FLYLYFE tees?","FLYLYFE tees are currently listed at $49.99 USD. Pricing and availability can change on the live storefront."),
("How do FLYLYFE tees fit?","Men's and DROP 02 tees have a relaxed streetwear fit in S–3XL. Women's tees have a relaxed softer drape in S–2XL. If between sizes, size down for a cleaner classic fit."),
("Does FLYLYFE ship worldwide?","Yes. FLYLYFE ships worldwide, with international rates shown at checkout. US shipping is a flat $4.75, and orders of 2 or more tees ship free automatically."),
("What is the return policy?","Every FLYLYFE tee is printed to order. Unworn, unwashed tees in original condition can be returned within 30 days of delivery for an exchange or refund. Email hello@flylyfe.com to start a return."),
("What are FLYLYFE tees printed on?","FLYLYFE tees are printed on the Comfort Colors 1717 — a heavyweight, garment-dyed, 100% ring-spun cotton blank known for its structured streetwear drape and soft washed feel."),
("How are FLYLYFE tees printed?","Every tee is made to order using DTF (direct-to-film) transfer printing in Los Angeles, USA — full-color, flexible prints that hold detail wash after wash."),
("How long does production take?","Because every tee is printed to order, production typically takes 7–10 business days. US delivery usually adds 1–5 business days after the order ships."),
("Do FLYLYFE tees have tags?","No. FLYLYFE tees are tagless — each one has a printed inside-neck FLYLYFE label instead of a sewn-in tag."),
("What is house-music streetwear?","House-music streetwear is apparel built around dance-floor culture, DJs, club nights, late sets, and the movement of cities like New York."),
("Is FLYLYFE affiliated with any sports tournament?","No. FLYLYFE is independent and is not affiliated with, sponsored by, or endorsed by any tournament, organizer, governing body, stadium, league, or team."),
]
faq_schema={"@context":"https://schema.org","@type":"FAQPage","dateModified":TODAY,"mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faq_items]}
def faq_id(q):
    if 'ship' in q.lower(): return ' id="shipping"'
    if 'return' in q.lower(): return ' id="returns"'
    return ''
faq_html=''.join(f'<details class="faq__item"{faq_id(q)}><summary>{escape(q)}</summary><p>{escape(a)}</p></details>' for q,a in faq_items)
write(Path('faq.html'), f'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>FLYLYFE FAQ | Shipping, Fit, Returns & House Music Streetwear</title><meta name="description" content="Answers about FLYLYFE sizing, shipping, returns, and pricing: $49.99 heavyweight tees, flat $4.75 US shipping, free US shipping on 2+ items, 30-day returns."><link rel="canonical" href="{BASE}/faq.html"><meta property="og:type" content="website"><meta property="og:site_name" content="FLYLYFE"><meta property="og:title" content="FLYLYFE FAQ | Shipping, Fit, Returns & House Music Streetwear"><meta property="og:description" content="Answers about FLYLYFE sizing, shipping, returns, pricing, house-music streetwear, and the NYC brand founded in 2007."><meta property="og:url" content="{BASE}/faq.html"><meta property="og:image" content="{BASE}/assets/lifestyle/lifestyle-2-black-slogan.jpg"><meta name="twitter:card" content="summary_large_image">{rel_css(0)}<script type="application/ld+json">{json.dumps(faq_schema,separators=(',',':'))}</script></head><body>{nav(0)}<main class="info-page"><section class="collection-hero"><p class="mono gold-text">FAQ · FLYLYFE</p><h1>FLYLYFE FAQ</h1><p>Short, direct answers about sizing, shipping, returns, and the brand.</p><p class="mono" style="font-size:.7rem;letter-spacing:.1em;color:var(--ink-dim);margin-top:1rem">LAST UPDATED: JULY 7, 2026</p></section><section class="faq standalone"><div class="faq__list">{faq_html}</div></section></main>{footer(0)}</body></html>''' )

about_schema={"@context":"https://schema.org","@graph":[{"@type":"AboutPage","name":"About FLYLYFE","url":BASE+"/about.html","description":"FLYLYFE is a New York City house-music streetwear brand established in 2007."},{"@type":"Organization","@id":BASE+"/#org","name":"FLYLYFE","url":BASE+"/","foundingDate":"2007","slogan":"Feel the Music. Feel the Vibe. Live Your Lyfe.","description":"New York City house-music streetwear brand making premium graphic tees inspired by dance-floor culture.","sameAs":["https://instagram.com/flylyfeofficial","https://tiktok.com/@flylyfe"]}]}
write(Path('about.html'), f'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>About FLYLYFE | NYC House Music Streetwear Since 2007</title><meta name="description" content="FLYLYFE is a New York City house-music streetwear brand founded in 2007. Feel the Music. Feel the Vibe. Live Your Lyfe."><link rel="canonical" href="{BASE}/about.html"><meta property="og:type" content="website"><meta property="og:site_name" content="FLYLYFE"><meta property="og:title" content="About FLYLYFE | NYC House Music Streetwear Since 2007"><meta property="og:description" content="FLYLYFE is a New York City house-music streetwear brand founded in 2007. Feel the Music. Feel the Vibe. Live Your Lyfe."><meta property="og:url" content="{BASE}/about.html"><meta property="og:image" content="{BASE}/assets/lifestyle/lifestyle-2-black-slogan.jpg">{rel_css(0)}<script type="application/ld+json">{json.dumps(about_schema,separators=(',',':'))}</script></head><body>{nav(0)}<main class="info-page"><section class="about-hero"><p class="mono gold-text">ABOUT FLYLYFE · EST. 2007</p><h1>Born in New York. Built for the dance floor.</h1><p>FLYLYFE is a New York City house-music streetwear brand for the people who understand the late set, the subway ride home, the basement room, the rooftop speaker, and the feeling that keeps going after the lights come up.</p></section><section class="seo-section"><h2>The brand story</h2><p>Founded in 2007, FLYLYFE connects house music, nightlife, movement, and NYC streetwear. The phrase is simple: <strong>Feel the Music. Feel the Vibe. Live Your Lyfe.</strong> Every tee carries that energy through premium cotton, bold graphics, and a dark New York visual language with gold accents.</p><p>FLYLYFE is always spelled as one word. The brand sells through its official site at <a href="{BASE}/">flylyfe.com</a> and ships worldwide.</p></section><section class="seo-section"><h2>What FLYLYFE makes</h2><div class="seo-grid"><article><h3>House music tees</h3><p>Graphic tees for house heads, DJs, dancers, producers, and fans who treat the dance floor like a second home.</p></article><article><h3>NYC streetwear</h3><p>Designs rooted in subway rides, after-hours culture, city coordinates, vintage signage, and New York nightlife.</p></article><article><h3>Premium cotton</h3><p>Printed-to-order pieces selected for streetwear fit, durability, and clear graphic execution.</p></article></div></section><section class="seo-section"><h2>Shop the collections</h2><div class="related-grid"><a class="related-card" href="collections/mens/"><span>Men's Collection</span></a><a class="related-card" href="collections/womens/"><span>Women's Collection</span></a><a class="related-card" href="collections/drop-02/"><span>DROP 02</span></a><a class="related-card" href="collections/house-music-streetwear/"><span>House Music Streetwear</span></a></div></section></main>{footer(0)}</body></html>''')

# ---- BLOG (internal-linking + informational-keyword layer) ----
def blog_post(post):
    depth=2; pref='../../'
    slug=post['slug']
    body=''
    for sec in post['sections']:
        paras=''.join(f'<p>{render_prose(par,pref)}</p>' for par in sec['paragraphs'])
        body+=f'<section class="seo-section"><h2>{E(sec["h2"])}</h2>{paras}</section>'
    faq=post.get('faq') or []
    faq_block=''
    if faq:
        acc=''.join(f'<details class="faq__item"><summary>{E(x["q"])}</summary><p>{E(x["a"])}</p></details>' for x in faq)
        faq_block=f'<section class="seo-section"><h2>Frequently asked questions</h2><div class="faq__list">{acc}</div></section>'
    used=[]
    for h in post.get('productLinksUsed',[]):
        if h in by_handle and h not in used: used.append(h)
    shop=''
    if used:
        cards=''.join(f'<a class="related-card" href="{pref}products/{h}/"><img src="{pref}{by_handle[h]["image"]}" alt="{E(by_handle[h]["name"])} — FLYLYFE house music streetwear tee" loading="lazy"><span>{E(by_handle[h]["name"])}</span></a>' for h in used)
        shop=f'<section class="seo-section"><h2>Shop the story</h2><div class="related-grid">{cards}</div></section>'
    node_faq=[{"@type":"FAQPage","mainEntity":[{"@type":"Question","name":unescape(x["q"]),"acceptedAnswer":{"@type":"Answer","text":unescape(x["a"])}} for x in faq]}] if faq else []
    schema={"@context":"https://schema.org","@graph":[{"@type":"Article","@id":f"{BASE}/blog/{slug}/#article","headline":post['h1'],"description":unescape(post['metaDescription']),"about":post['keyword'],"datePublished":TODAY,"dateModified":TODAY,"author":{"@type":"Organization","name":"FLYLYFE"},"publisher":{"@type":"Organization","name":"FLYLYFE","url":BASE+"/"},"mainEntityOfPage":f"{BASE}/blog/{slug}/","url":f"{BASE}/blog/{slug}/"}]+node_faq+[{"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":BASE+"/"},{"@type":"ListItem","position":2,"name":"Blog","item":BASE+"/blog/"},{"@type":"ListItem","position":3,"name":post['h1'],"item":f"{BASE}/blog/{slug}/"}]}]}
    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{E(post['titleTag'])}</title><meta name="description" content="{E(post['metaDescription'])}"><link rel="canonical" href="{BASE}/blog/{slug}/"><meta property="og:type" content="article"><meta property="og:site_name" content="FLYLYFE"><meta property="og:title" content="{E(post['titleTag'])}"><meta property="og:description" content="{E(post['metaDescription'])}"><meta property="og:url" content="{BASE}/blog/{slug}/"><meta property="og:image" content="{BASE}/assets/lifestyle/lifestyle-2-black-slogan.jpg"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{E(post['titleTag'])}"><meta name="twitter:description" content="{E(post['metaDescription'])}"><meta name="twitter:image" content="{BASE}/assets/lifestyle/lifestyle-2-black-slogan.jpg">{rel_css(depth)}<script type="application/ld+json">{json.dumps(schema,separators=(',',':'))}</script></head><body>{nav(depth)}<main class="info-page blog-post"><article><section class="collection-hero"><p class="mono gold-text">FLYLYFE JOURNAL · {E(post['keyword'].upper())}</p><h1>{E(post['h1'])}</h1><p class="blog-dek">{E(post['dek'])}</p><p class="mono" style="font-size:.68rem;letter-spacing:.1em;color:var(--ink-dim);margin-top:1rem">FLYLYFE · UPDATED {TODAY}</p></section>{body}{faq_block}{shop}</article></main>{footer(depth)}</body></html>'''

def blog_index():
    depth=1; pref='../'
    cards=''.join(f'<a class="collection-card blog-card" href="{pref}blog/{post["slug"]}/"><span class="mono">JOURNAL</span><h2>{E(post["h1"])}</h2><p>{E(post["dek"])}</p></a>' for post in blog)
    schema={"@context":"https://schema.org","@graph":[{"@type":"Blog","@id":BASE+"/blog/#blog","name":"The FLYLYFE Journal","description":"House music culture, NYC streetwear, and style guides from FLYLYFE.","url":BASE+"/blog/","publisher":{"@type":"Organization","name":"FLYLYFE","url":BASE+"/"},"blogPost":[{"@type":"BlogPosting","headline":p['h1'],"url":f"{BASE}/blog/{p['slug']}/","description":unescape(p['metaDescription']),"datePublished":TODAY} for p in blog]},{"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":BASE+"/"},{"@type":"ListItem","position":2,"name":"Blog","item":BASE+"/blog/"}]}]}
    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>The FLYLYFE Journal | House Music &amp; NYC Streetwear Guides</title><meta name="description" content="House music culture, NYC streetwear history, and style guides from FLYLYFE — what to wear to a festival, the story of the subway token, and more."><link rel="canonical" href="{BASE}/blog/"><meta property="og:type" content="website"><meta property="og:site_name" content="FLYLYFE"><meta property="og:title" content="The FLYLYFE Journal | House Music &amp; NYC Streetwear Guides"><meta property="og:description" content="House music culture, NYC streetwear history, and style guides from FLYLYFE."><meta property="og:url" content="{BASE}/blog/"><meta property="og:image" content="{BASE}/assets/lifestyle/lifestyle-2-black-slogan.jpg"><meta name="twitter:card" content="summary_large_image">{rel_css(depth)}<script type="application/ld+json">{json.dumps(schema,separators=(',',':'))}</script></head><body>{nav(depth)}<main class="collection-page"><section class="collection-hero"><p class="mono gold-text">FLYLYFE JOURNAL</p><h1>The FLYLYFE Journal</h1><p>House-music culture, NYC streetwear history, and honest style guides — written for house heads, DJs, dancers, and everyone who lives the lyfe.</p></section><section class="collection-grid blog-grid">{cards}</section></main>{footer(depth)}</body></html>'''

for post in blog:
    write(Path(f'blog/{post["slug"]}/index.html'), blog_post(post))
write(Path('blog/index.html'), blog_index())

# CSS
(ROOT/'css/seo-pages.css').write_text('''
.collection-page,.info-page,.seo-product{background:var(--bg);min-height:100vh}.collection-hero,.about-hero{padding:8rem 6vw 3.5rem;border-bottom:1px solid var(--line);background:radial-gradient(circle at 70% 10%,#171717,var(--bg) 65%)}.collection-hero h1,.about-hero h1,.seo-product h1{font-family:var(--font-display);font-size:clamp(3rem,7vw,6.4rem);line-height:.92;text-transform:uppercase;margin:.5rem 0 1rem;max-width:1050px}.collection-hero p,.about-hero p,.seo-lede{color:var(--ink-dim);font-size:1.05rem;line-height:1.75;max-width:760px}.collection-grid{padding:3rem 6vw 6rem;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:1.25rem}.collection-card,.related-card{border:1px solid var(--line);background:#0d0d0d;color:var(--ink);display:block;transition:transform .25s,border-color .25s}.collection-card:hover,.related-card:hover{transform:translateY(-4px);border-color:var(--gold)}.collection-card img,.related-card img{width:100%;aspect-ratio:3/4;object-fit:cover;display:block}.collection-card span{display:block;color:var(--gold);font-size:.7rem;letter-spacing:.14em;margin:1rem 1rem .4rem}.collection-card h2{font-size:1rem;text-transform:uppercase;letter-spacing:.04em;margin:0 1rem .5rem}.collection-card p{color:var(--ink-dim);font-size:.86rem;line-height:1.55;margin:0 1rem 1.2rem}.seo-product__hero{padding:7rem 6vw 4rem;display:grid;grid-template-columns:minmax(280px,520px) 1fr;gap:clamp(2rem,5vw,5rem);align-items:center;background:radial-gradient(circle at 70% 10%,#171717,var(--bg) 65%)}.seo-product__media{border:1px solid var(--line);background:#0d0d0d;aspect-ratio:3/4;overflow:hidden}.seo-product__media img{width:100%;height:100%;object-fit:cover;object-position:top center}.seo-price{font-size:1.3rem;color:var(--gold);margin:1.2rem 0}.seo-specline{color:var(--ink-dim);font-size:.72rem;letter-spacing:.06em;line-height:1.7;margin:-.6rem 0 1rem;max-width:520px}.seo-product__descriptor{color:var(--gold);font-size:.78rem;letter-spacing:.16em;text-transform:uppercase;margin:.1rem 0 1.1rem}.seo-features{list-style:none;margin:1.4rem 0 0;padding:0;display:grid;grid-template-columns:1fr 1fr;gap:.9rem;max-width:900px}.seo-features li{border-left:2px solid var(--gold);padding:.2rem 0 .2rem 1rem;color:var(--ink-dim);line-height:1.6;font-size:.95rem}.seo-features strong{color:var(--ink)}.seo-linkline{color:var(--ink-dim);line-height:1.8;max-width:900px;margin-bottom:1.3rem}.seo-linkline a{color:var(--gold);border-bottom:1px solid rgba(200,164,90,.4)}@media(max-width:620px){.seo-features{grid-template-columns:1fr}}.seo-section{padding:3.5rem 6vw;border-top:1px solid var(--line)}.seo-section h2{font-family:var(--font-display);font-size:clamp(2.2rem,4vw,4rem);line-height:1;text-transform:uppercase;margin-bottom:1rem}.seo-section p{color:var(--ink-dim);line-height:1.75;max-width:900px}.seo-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-top:1.5rem}.seo-grid article{border:1px solid var(--line);background:#0d0d0d;padding:1.3rem}.seo-grid h3{color:var(--gold);text-transform:uppercase;font-size:.9rem;letter-spacing:.08em;margin-bottom:.6rem}.seo-commerce{border:1px solid var(--line);background:#0b0b0b;padding:1rem;margin:1.2rem 0}.seo-commerce__group{margin-bottom:1rem}.seo-commerce__label{font-size:.68rem;letter-spacing:.14em;color:var(--ink-dim);margin-bottom:.55rem}.seo-commerce__options{display:flex;gap:.5rem;flex-wrap:wrap}.seo-option{border:1px solid var(--line);background:transparent;color:var(--ink);padding:.65rem .8rem;cursor:pointer;font-family:var(--font-mono);font-size:.72rem}.seo-option[aria-pressed="true"]{background:var(--gold);border-color:var(--gold);color:#000}.seo-option:disabled{opacity:.35;text-decoration:line-through;cursor:not-allowed}.seo-atc,.seo-checkout{display:inline-flex;justify-content:center;align-items:center;margin:.35rem .5rem .35rem 0;padding:1rem 1.2rem;border:none;background:var(--gold);color:#000;font-family:var(--font-mono);letter-spacing:.12em;text-transform:uppercase;cursor:pointer}.seo-checkout{background:transparent;color:var(--ink);border:1px solid var(--line)}.seo-status{color:var(--gold);font-size:.75rem;letter-spacing:.1em;margin-top:.7rem}.seo-trust{display:flex;gap:1rem;flex-wrap:wrap;color:var(--ink-dim);font-size:.65rem}.related-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-top:1.3rem}.related-card{padding-bottom:1rem}.related-card span{display:block;padding:1rem;text-transform:uppercase;font-weight:700}.faq.standalone{padding-top:1rem}.blog-grid{grid-template-columns:repeat(3,1fr)}.blog-card{padding:1.6rem;min-height:220px;display:flex;flex-direction:column}.blog-card span{margin:0 0 .8rem}.blog-card h2{margin:0 0 .7rem;font-size:1.2rem;line-height:1.15;text-transform:none}.blog-card p{margin:0;font-size:.9rem;color:var(--ink-dim)}.blog-dek{color:var(--ink);font-size:1.15rem;line-height:1.6;max-width:780px;margin-top:1rem}.blog-post .seo-section{border-top:none;padding-top:1.5rem;padding-bottom:1.5rem}.blog-post .seo-section h2{font-size:clamp(1.6rem,3vw,2.6rem);margin-bottom:.8rem}.blog-post .seo-section p{max-width:780px;font-size:1.04rem;margin-bottom:1rem}.blog-post .seo-section p a{color:var(--gold);border-bottom:1px solid rgba(200,164,90,.45)}@media(max-width:980px){.collection-grid,.related-grid{grid-template-columns:repeat(2,1fr)}.seo-grid{grid-template-columns:1fr}.seo-product__hero{grid-template-columns:1fr}}@media(max-width:620px){.collection-hero,.about-hero{padding:6rem 1.4rem 2.5rem}.collection-grid,.seo-section{padding-left:1.4rem;padding-right:1.4rem}.collection-grid,.related-grid{grid-template-columns:1fr}.seo-product__hero{padding:5.5rem 1.4rem 3rem}.seo-atc,.seo-checkout{width:100%;margin-right:0}}
''', encoding='utf-8')

# product JS
(ROOT/'js/product-page.js').write_text(r'''
// Shopify Storefront API identifiers are intentionally client-side.
// This is not an Admin API secret; it is scoped for public storefront cart/product operations only.
const SHOP_DOMAIN='31zn52-zd.myshopify.com';
const STOREFRONT_TOKEN='5a0bb1dcf0c57b7764bbebf0cc40c898';
const API_URL=`https://${SHOP_DOMAIN}/api/2025-10/graphql.json`;
const handle=document.body.dataset.productHandle;
let cartId=localStorage.getItem('flylyfe_cart');
let product=null,state={color:null,size:null};
const money=a=>'$'+parseFloat(a).toFixed(2);
async function gql(query,variables={}){const res=await fetch(API_URL,{method:'POST',headers:{'Content-Type':'application/json','X-Shopify-Storefront-Access-Token':STOREFRONT_TOKEN},body:JSON.stringify({query,variables})});const j=await res.json();if(j.errors)throw new Error(j.errors.map(e=>e.message).join('; '));return j.data;}
const PRODUCT_Q=`query($handle:String!){ product(handle:$handle){ id handle title descriptionHtml options{name values} featuredImage{url} variants(first:100){edges{node{id title availableForSale price{amount currencyCode} image{url} selectedOptions{name value}}}}}}`;
const CART_FIELDS=`id checkoutUrl totalQuantity cost{subtotalAmount{amount currencyCode}} lines(first:30){edges{node{id quantity merchandise{... on ProductVariant{id title product{title handle} selectedOptions{name value} price{amount}}}}}}`;
function optionValues(name){return (product.options.find(o=>o.name===name)?.values)||[]}
function variant(){return product.variants.edges.map(e=>e.node).find(v=>v.selectedOptions.some(o=>o.name==='Color'&&o.value===state.color)&&v.selectedOptions.some(o=>o.name==='Size'&&o.value===state.size));}
async function ensureCart(){if(cartId){const d=await gql(`query($id:ID!){cart(id:$id){${CART_FIELDS}}}`,{id:cartId});if(d.cart)return d.cart;}const d=await gql(`mutation{cartCreate{cart{${CART_FIELDS}}}}`);cartId=d.cartCreate.cart.id;localStorage.setItem('flylyfe_cart',cartId);return d.cartCreate.cart;}
async function addToCart(){const v=variant();if(!v){status('SELECT AN AVAILABLE SIZE');return null;}status('ADDING…');const c=await ensureCart();const d=await gql(`mutation($cid:ID!,$lines:[CartLineInput!]!){cartLinesAdd(cartId:$cid,lines:$lines){cart{${CART_FIELDS}}}}`,{cid:c.id,lines:[{merchandiseId:v.id,quantity:1}]});status('ADDED TO CART');return d.cartLinesAdd.cart;}
function status(t){const el=document.querySelector('[data-commerce-status]');if(el)el.textContent=t;}
function render(){const root=document.querySelector('[data-commerce-root]');const colors=optionValues('Color');const sizes=optionValues('Size').sort((a,b)=>['S','M','L','XL','2XL','3XL'].indexOf(a)-['S','M','L','XL','2XL','3XL'].indexOf(b));state.color=state.color||colors[0];const price=product.variants.edges[0]?.node.price.amount||'49.99';root.innerHTML=`<div class="seo-commerce__group"><p class="seo-commerce__label mono">COLOR — ${state.color||''}</p><div class="seo-commerce__options" data-colors></div></div><div class="seo-commerce__group"><p class="seo-commerce__label mono">SIZE${state.size?' — '+state.size:''}</p><div class="seo-commerce__options" data-sizes></div></div><button class="seo-atc" data-atc>${state.size?'ADD TO CART · '+money(price):'SELECT SIZE'}</button><button class="seo-checkout" data-checkout>CHECKOUT</button><p class="seo-status mono" data-commerce-status>LIVE SHOPIFY OPTIONS LOADED</p>`;
const cwrap=root.querySelector('[data-colors]');colors.forEach(c=>{const b=document.createElement('button');b.className='seo-option';b.textContent=c;b.setAttribute('aria-pressed',String(c===state.color));b.onclick=()=>{state.color=c;state.size=null;render()};cwrap.appendChild(b);});
const swrap=root.querySelector('[data-sizes]');sizes.forEach(s=>{const available=product.variants.edges.map(e=>e.node).some(v=>v.availableForSale&&v.selectedOptions.some(o=>o.name==='Color'&&o.value===state.color)&&v.selectedOptions.some(o=>o.name==='Size'&&o.value===s));const b=document.createElement('button');b.className='seo-option';b.textContent=s;b.disabled=!available;b.setAttribute('aria-pressed',String(s===state.size));b.onclick=()=>{state.size=s;render()};swrap.appendChild(b);});
root.querySelector('[data-atc]').onclick=async()=>{try{await addToCart();}catch(e){console.error(e);status('CART ERROR — TRY AGAIN');}};
root.querySelector('[data-checkout]').onclick=async()=>{try{const cart=await addToCart()||await ensureCart();if(cart.checkoutUrl) location.href=cart.checkoutUrl;}catch(e){console.error(e);status('CHECKOUT ERROR — TRY AGAIN');}};
}
(async()=>{try{const d=await gql(PRODUCT_Q,{handle});product=d.product;if(!product)throw new Error('Product not found');render();}catch(e){console.error(e);document.querySelector('[data-commerce-root]').innerHTML='<p class="mono">LIVE OPTIONS TEMPORARILY UNAVAILABLE. <a href="../../#shop">SHOP ON MAIN SITE</a></p>';}})();
''', encoding='utf-8')

# patch index nav/footer and versions/schema URLs
idx=ROOT/'index.html'
s=idx.read_text(encoding='utf-8')
for asset in (r'css/style\.css', r'css/product\.css', r'css/seo-pages\.css', r'js/app\.js'):
    s=re.sub('('+asset+r'\?v=)[A-Za-z0-9-]+', r'\g<1>'+ASSET_V, s)
s=s.replace('<link rel="stylesheet" href="css/product.css?v='+ASSET_V+'">','<link rel="stylesheet" href="css/product.css?v='+ASSET_V+'">\n<link rel="stylesheet" href="css/seo-pages.css?v='+ASSET_V+'">')
# Keep this generator idempotent: collapse accidental duplicate seo-pages.css lines from repeated runs.
s=re.sub(r'(?:<link rel="stylesheet" href="css/seo-pages\.css\?v='+re.escape(ASSET_V)+r'">\n?)+', '<link rel="stylesheet" href="css/seo-pages.css?v='+ASSET_V+'">\n', s)
s=s.replace('<a href="#after-hours">Collections</a>\n    <a href="#story">About</a>\n    <a href="#journal">Journal</a>', '<a href="collections/mens/">Men\'s</a>\n    <a href="collections/womens/">Women\'s</a>\n    <a href="collections/drop-02/">Drop 02</a>\n    <a href="about.html">About</a>\n    <a href="faq.html">FAQ</a>')
s=s.replace('<a href="#after-hours">Collections</a>\n    <a href="#story">About</a>\n    <a href="#journal">Journal</a>', '<a href="collections/mens/">Men\'s</a>\n    <a href="collections/womens/">Women\'s</a>\n    <a href="collections/drop-02/">Drop 02</a>\n    <a href="about.html">About</a>\n    <a href="faq.html">FAQ</a>')
s=s.replace('<a href="#shop">Men\'s</a>\n        <a href="#shop-women">Women\'s</a>\n        <a href="#after-hours">After Hours</a>', '<a href="collections/mens/">Men\'s</a>\n        <a href="collections/womens/">Women\'s</a>\n        <a href="collections/drop-02/">Drop 02</a>\n        <a href="collections/limited/">Limited</a>')
s=s.replace('<a href="#story">About</a>\n        <a href="#journal">Journal</a>\n        <a href="privacy.html">Privacy</a>\n        <a href="terms.html">Terms</a>', '<a href="about.html">About</a>\n        <a href="faq.html">FAQ</a>\n        <a href="collections/house-music-streetwear/">House Music Streetwear</a>\n        <a href="privacy.html">Privacy</a>\n        <a href="terms.html">Terms</a>')
# Update ItemList offer URLs from anchors to canonical product pages.
for p in products:
    # Not reliable exact text for every existing schema, do broad product name URL fix later if needed.
    pass
# Add a Blog link to the homepage nav (desktop + mobile) and footer, once (idempotent).
if 'href="blog/"' not in s:
    s=s.replace('<a href="about.html">About</a>\n    <a href="faq.html">FAQ</a>', '<a href="blog/">Blog</a>\n    <a href="about.html">About</a>\n    <a href="faq.html">FAQ</a>')
    s=s.replace('<a href="collections/house-music-streetwear/">House Music Streetwear</a>', '<a href="blog/">Blog</a>\n        <a href="collections/house-music-streetwear/">House Music Streetwear</a>')
# Add the use-case / audience landing pages to the homepage footer, once (independent guard).
if 'collections/dj-tees/' not in s:
    s=s.replace('<a href="collections/house-music-streetwear/">House Music Streetwear</a>', '<a href="collections/house-music-festival-shirts/">Festival &amp; Rave Shirts</a>\n        <a href="collections/dj-tees/">DJ Tees</a>\n        <a href="collections/nyc-streetwear-tees/">NYC Streetwear Tees</a>\n        <a href="collections/house-music-streetwear/">House Music Streetwear</a>')
idx.write_text(s, encoding='utf-8')

# sitemap
urls=[('/', '1.0'),('/about.html','0.7'),('/faq.html','0.7'),('/privacy.html','0.4'),('/terms.html','0.4')]
urls += [(f'/collections/{slug}/', '0.75') for slug in collections]
urls += [(f'/products/{p["handle"]}/','0.8') for p in products]
urls += [('/blog/','0.6')]
urls += [(f'/blog/{post["slug"]}/','0.6') for post in blog]
sitemap=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u,prio in urls:
    cf='weekly' if prio!='0.4' else 'yearly'
    sitemap += ['  <url>',f'    <loc>{BASE}{u}</loc>',f'    <lastmod>{TODAY}</lastmod>',f'    <changefreq>{cf}</changefreq>',f'    <priority>{prio}</priority>','  </url>']
sitemap.append('</urlset>')
(ROOT/'sitemap.xml').write_text('\n'.join(sitemap)+'\n', encoding='utf-8')

# llms.txt — regenerate the AI/answer-engine facts file from the same data used for pages.
# This avoids stale anchor links, duplicate sections, and mismatches between sitemap, schema, and LLM facts.
product_lines = '\n'.join(
    f"- {p['name']} — {p['short']} — {BASE}/products/{p['handle']}/"
    for p in products
)
section_lines = '\n'.join([
    f"- Canonical site: {BASE}/",
    f"- Main shop: {BASE}/#shop",
    f"- About / brand story: {BASE}/about.html",
    f"- FAQ: {BASE}/faq.html",
    f"- Privacy Policy: {BASE}/privacy.html",
    f"- Terms of Sale: {BASE}/terms.html",
] + [
    f"- {c['label']}: {BASE}/collections/{slug}/" for slug, c in collections.items()
])
collection_lines = '\n'.join(
    f"- {c['label']} — {c['desc']} — {BASE}/collections/{slug}/"
    for slug, c in collections.items()
)
blog_lines = '\n'.join(
    f"- {unescape(post['h1'])} — {unescape(post['metaDescription'])} — {BASE}/blog/{post['slug']}/"
    for post in blog
)
(ROOT/'llms.txt').write_text(f'''# FLYLYFE

> FLYLYFE is a New York City house-music streetwear brand, established in 2007. The brand makes premium graphic tees inspired by house music, NYC culture, nightlife, dance-floor movement, and the motto: "Feel the Music. Feel the Vibe. Live Your Lyfe."

Last updated: {TODAY}
Canonical site: {BASE}/
Sitemap: {BASE}/sitemap.xml

## About
- Brand name: FLYLYFE. Always one word — not "Fly Lyfe", "FlyLife", or "Flylife".
- Founded: 2007 in New York City.
- Category: premium streetwear / house-music culture apparel.
- Tagline: Feel the Music. Feel the Vibe. Live Your Lyfe.
- Aesthetic: NYC, house music, underground nightlife, editorial fashion, dark palette, gold accents.
- Contact: hello@flylyfe.com
- Instagram: https://instagram.com/flylyfeofficial (@flylyfeofficial)
- TikTok: https://tiktok.com/@flylyfe (@flylyfe)

## Current products and canonical product pages
All products are currently listed at $49.99 USD on the live Shopify storefront. Product availability can change.

{product_lines}

## Crawlable collection pages
{collection_lines}

## Guides and articles (FLYLYFE Journal)
- Blog index: {BASE}/blog/
{blog_lines}

## Fabric, fit, and fulfillment
- Blank: Comfort Colors 1717 — heavyweight, garment-dyed, 100% ring-spun cotton.
- Print method: DTF (direct-to-film) transfer, printed to order in Los Angeles, USA.
- Neck: tagless — printed inside-neck FLYLYFE label instead of a sewn-in tag.
- Men's and DROP 02 tees: streetwear fit, sizes S–3XL.
- Women's tees: relaxed fit on the same 1717 blank, sizes S–2XL.
- Fit guidance: true to size with a relaxed drop; size down for a more classic fit if between sizes.

## Shipping and policies
- Ships worldwide; international rates are shown at checkout and delivery times vary by destination.
- US shipping: flat $4.75; orders of 2 or more items ship free automatically (US).
- Made to order: production typically takes 7–10 business days, then US delivery is usually 1–5 business days.
- Returns: unworn, unwashed tees in original condition within 30 days of delivery for exchange or refund — email hello@flylyfe.com.
- Privacy Policy: {BASE}/privacy.html
- Terms of Sale: {BASE}/terms.html

## Primary site sections
{section_lines}

## FAQ-style answers for AI search

### What is FLYLYFE?
FLYLYFE is a New York City house-music streetwear brand founded in 2007. It makes premium graphic tees inspired by house music, NYC nightlife, dance-floor culture, and the phrase "Feel the Music. Feel the Vibe. Live Your Lyfe."

### Where is FLYLYFE based?
FLYLYFE is based in New York City and sells worldwide through {BASE}/.

### What does FLYLYFE sell?
FLYLYFE sells premium graphic tees, including men's streetwear tees, women's relaxed tees, DROP 02 designs, and limited-edition New York-inspired releases.

### What is the House Music Tee?
The House Music Tee is a FLYLYFE graphic tee with the phrase "not everyone understands house music" on the front and the house-music manifesto "a spiritual thing, a body thing, a soul thing" on the back.

### How much are FLYLYFE tees?
FLYLYFE tees are currently listed at $49.99 USD on the live storefront. Prices and availability can change.

### Does FLYLYFE ship worldwide?
Yes. FLYLYFE ships worldwide, with international rates shown at checkout. US shipping is a flat $4.75, and orders of 2 or more items ship free automatically.

### What are FLYLYFE tees made of?
FLYLYFE tees are printed to order on the Comfort Colors 1717 — a heavyweight, garment-dyed, 100% ring-spun cotton blank — using DTF transfer printing in Los Angeles, USA, with a tagless printed inside-neck label.

### Is FLYLYFE affiliated with any sports tournament or governing body?
No. Any summer 2026 New York / New Jersey cultural references are editorial context only. FLYLYFE is not affiliated with, sponsored by, or endorsed by any tournament, organizer, governing body, stadium, league, or team.

## Key facts for citation
- FLYLYFE has been making house-music streetwear in New York City since 2007.
- The brand connects house music, dance-floor culture, and New York City heritage.
- FLYLYFE is always spelled as one word.
- Signature phrase: "Not everyone understands house music — it's a spiritual thing, a body thing, a soul thing."
- Current canonical product pages are under {BASE}/products/.
- Collection pages are under {BASE}/collections/.
- Current listed tee price: $49.99 USD.
- Product pages include live color and size selection, add-to-cart, and Shopify checkout actions.
''', encoding='utf-8')
print('generated', len(products), 'product pages,', len(collections), 'collection pages, about/faq, css/js/sitemap/llms')
