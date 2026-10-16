#!/usr/bin/env python3
"""Audit crawlable page identity, links, product facts, and feed coverage.

This checks local files. It does not certify indexing, rich-result eligibility,
live inventory, rankings, or externally managed Merchant Center settings.
"""
from collections import Counter
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
from urllib.parse import parse_qs, unquote, urljoin, urlparse
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup
from normalize_product_metadata import product_metadata

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://www.flylyfe.com/'
SITEMAP_NS = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
GOOGLE_NS = {'g': 'http://base.google.com/ns/1.0'}


def local_path(url):
    path = unquote(urlparse(url).path).lstrip('/')
    return ROOT / (path + 'index.html' if not path or path.endswith('/') else path)


def main():
    errors, pages, products, titles, descriptions = [], [], [], [], []
    sitemap = ET.parse(ROOT / 'sitemap.xml')
    sitemap_urls = [node.text for node in sitemap.findall('s:url/s:loc', SITEMAP_NS)]
    if len(sitemap_urls) != len(set(sitemap_urls)):
        errors.append('Duplicate sitemap page URL')
    for path in sorted(ROOT.rglob('*.html')):
        if any(part.startswith('.') or part in {'node_modules', 'test-results', 'playwright-report'} for part in path.relative_to(ROOT).parts):
            continue
        name = str(path.relative_to(ROOT))
        source = path.read_text()
        soup = BeautifulSoup(source, 'html.parser')
        robots = soup.find('meta', attrs={'name': 'robots'})
        if robots and 'noindex' in robots.get('content', ''):
            continue
        canonical = soup.find('link', rel='canonical')
        url = canonical.get('href') if canonical else None
        if not url or not url.startswith(BASE) or local_path(url) != path:
            errors.append(f'{name}: missing or inconsistent canonical')
            continue
        pages.append(url)
        if len(soup.find_all('h1')) != 1:
            errors.append(f'{name}: expected one H1')
        if len(soup.find_all('main')) != 1:
            errors.append(f'{name}: expected one main landmark')
        title = soup.title.get_text(strip=True) if soup.title else ''
        description = soup.find('meta', attrs={'name': 'description'})
        if not title or not description or not description.get('content'):
            errors.append(f'{name}: missing title or description')
        titles.append(title)
        descriptions.append(description.get('content', '') if description else '')
        for anchor in soup.select('a[href]'):
            target = urljoin(url, anchor['href'])
            parsed = urlparse(target)
            if parsed.scheme in {'http', 'https'} and parsed.netloc == 'www.flylyfe.com' and not local_path(target).exists():
                errors.append(f'{name}: missing internal target {target}')
        try:
            after, is_product = product_metadata(source)
            if is_product:
                products.append(url)
                if after != source:
                    errors.append(f'{name}: product metadata or policy needs normalization')
            for tag in soup.select('script[type="application/ld+json"]'):
                data = json.loads(tag.string)
                for node in data.get('@graph', [data]):
                    if node.get('@type') == 'ClothingStore':
                        errors.append(f'{name}: physical-store type requires a verified physical store')
        except (AssertionError, KeyError, TypeError, json.JSONDecodeError) as exc:
            errors.append(f'{name}: schema error: {exc}')
    for label, values in [('title', titles), ('description', descriptions)]:
        for value, count in Counter(values).items():
            if value and count > 1:
                errors.append(f'Duplicate {label}: {value}')
    for url in sorted(set(pages) - set(sitemap_urls)):
        errors.append(f'Page absent from sitemap: {url}')
    for url in sorted(set(sitemap_urls) - set(pages)):
        errors.append(f'Sitemap URL is not an indexable local page: {url}')
    items = ET.parse(ROOT / 'feed/google-products.xml').findall('.//item')
    feed_urls = {item.findtext('g:link', namespaces=GOOGLE_NS).split('?')[0] for item in items}
    curated = {(row['handle'], row['color']): row['urls'] for row in json.loads((ROOT / 'tools/merchant-feed-images.json').read_text())}
    offer_ids, variant_ids = [], []
    for item in items:
        get = lambda name: item.findtext('g:' + name, namespaces=GOOGLE_NS)
        offer_id, handle, color = get('id'), get('item_group_id'), get('color')
        offer_ids.append(offer_id)
        url = get('link')
        variant = parse_qs(urlparse(url).query).get('variant', [''])[0]
        variant_ids.append(variant)
        if not variant.isdigit() or url.split('?')[0] not in products:
            errors.append(f'Feed {offer_id}: missing product page or exact variant URL')
        urls = [get('image_link')] + [node.text for node in item.findall('g:additional_image_link', GOOGLE_NS)]
        if urls != curated.get((handle, color)):
            errors.append(f'Feed {offer_id}: images differ from reviewed product/color mapping')
        try:
            assert get('price').endswith(' USD') and Decimal(get('price').split()[0]) > 0
            assert get('shipping_weight').endswith(' g') and Decimal(get('shipping_weight').split()[0]) > 0
        except (AssertionError, AttributeError, InvalidOperation, IndexError):
            errors.append(f'Feed {offer_id}: invalid price or shipping weight')
    if len(offer_ids) != len(set(offer_ids)) or len(variant_ids) != len(set(variant_ids)):
        errors.append('Duplicate feed offer or variant identifier')
    omitted = sorted(url for url in products if '/products/' in url and url not in feed_urls)
    report = {
        'indexable_pages': len(pages), 'sitemap_pages': len(sitemap_urls),
        'product_pages_including_translations': len(products),
        'merchant_feed_offers': len(items), 'merchant_feed_product_pages': len(feed_urls),
        'products_outside_merchant_feed': omitted,
        'errors': sorted(set(errors)),
    }
    print(json.dumps(report, indent=2))
    raise SystemExit(bool(errors))


if __name__ == '__main__':
    main()
