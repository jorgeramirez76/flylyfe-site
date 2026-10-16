"""Refresh existing offers from a public Shopify products.json snapshot.

Usage: python3 tools/repair_merchant_feed.py /path/to/products.json [--check]
Images are deliberately curated in merchant-feed-images.json, never generated or
inferred during refresh. Existing offer IDs are preserved. --expand-reviewed can
add current variants only when their exact product/color has a curated image.
Use --coverage-report to see variants awaiting image review. A successful check
does not confirm Merchant Center acceptance or certify image-policy compliance.
"""
import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
NS = {"g": "http://base.google.com/ns/1.0"}


def repair(source, catalog, images):
    products = {p["handle"]: p for p in catalog["products"]}
    curated = {(r["handle"], r["color"]): r["urls"] for r in images}
    removed = []

    def item(match):
        block = match.group()
        node = ET.fromstring('<root xmlns:g="' + NS['g'] + '">' + block + '</root>')[0]
        get = lambda name: node.findtext('g:' + name, namespaces=NS)
        handle, color, size = get('item_group_id'), get('color'), get('size')
        product = products[handle]  # Missing products must be investigated, not silently removed.
        positions = {o['name']: o['position'] for o in product['options']}
        variants = [v for v in product['variants']
                    if v['option' + str(positions['Color'])] == color
                    and v['option' + str(positions['Size'])] == size]
        if not variants:
            removed.append(get('id'))
            return ''
        assert len(variants) == 1, (handle, color, size)
        variant = variants[0]
        grams = variant['grams']
        assert isinstance(grams, (int, float)) and grams > 0, (handle, color, size, grams)
        urls = curated[(handle, color)]
        assert 1 <= len(urls) <= 11 and len(urls) == len(set(urls))
        assert all(u.startswith('https://') for u in urls)
        updates = {
            'link': f'https://www.flylyfe.com/products/{handle}/?variant={variant["id"]}',
            'image_link': urls[0],
            'price': variant['price'] + ' USD',
            'availability': 'in_stock' if variant['available'] else 'out_of_stock',
        }
        block = re.sub(r'\s*<g:additional_image_link>.*?</g:additional_image_link>', '', block)
        block = re.sub(r'\s*<g:shipping_weight>.*?</g:shipping_weight>', '', block)
        block = block.replace('</g:availability>', '</g:availability>'
                              + f'\n    <g:shipping_weight>{grams:g} g</g:shipping_weight>')
        for name, value in updates.items():
            block = re.sub(fr'<g:{name}>.*?</g:{name}>',
                           lambda _: f'<g:{name}>{escape(value)}</g:{name}>', block)
        extra = ''.join('\n    <g:additional_image_link>' + escape(u) + '</g:additional_image_link>' for u in urls[1:])
        return block.replace('</g:image_link>', '</g:image_link>' + extra)

    result = re.sub(r'<item>.*?</item>', item, source, flags=re.S)
    ET.fromstring(result)
    return result, removed


def expand_reviewed(source, catalog, images):
    """Add only current site variants with an explicitly reviewed color image."""
    products = {p['handle']: p for p in catalog['products']}
    curated = {(row['handle'], row['color']): row['urls'] for row in images}
    current = ET.fromstring(source).findall('.//item')
    existing_ids = {node.findtext('g:id', namespaces=NS) for node in current}
    existing_variants = {re.search(r'[?&]variant=(\d+)', node.findtext('g:link', namespaces=NS)).group(1) for node in current}
    additions, pending = [], []
    for page in sorted((ROOT / 'products').glob('*/index.html')):
        handle = page.parent.name
        product = products[handle]
        positions = {option['name']: option['position'] for option in product['options']}
        soup = BeautifulSoup(page.read_text(), 'html.parser')
        facts = [node for tag in soup.select('script[type="application/ld+json"]')
                 for node in json.loads(tag.string).get('@graph', [json.loads(tag.string)])
                 if node.get('@type') == 'Product']
        assert len(facts) == 1, handle
        facts = facts[0]
        for variant in product['variants']:
            if str(variant['id']) in existing_variants:
                continue
            color = variant['option' + str(positions['Color'])]
            size = variant['option' + str(positions['Size'])]
            urls = curated.get((handle, color))
            if not urls:
                pending.append({'handle': handle, 'variant_id': variant['id'], 'color': color, 'size': size,
                                'reason': 'No reviewed image mapping for this product/color'})
                continue
            assert 1 <= len(urls) <= 11 and len(urls) == len(set(urls))
            assert all(url.startswith('https://') for url in urls)
            grams = variant['grams']
            assert isinstance(grams, (int, float)) and grams > 0, (handle, variant['id'])
            offer_id = f'flylyfe-{variant["id"]}'
            assert offer_id not in existing_ids, offer_id
            existing_ids.add(offer_id)
            values = {
                'id': offer_id, 'item_group_id': handle,
                'title': f'{facts["name"]} — {color}, {size}',
                'description': facts['description'],
                'link': f'https://www.flylyfe.com/products/{handle}/?variant={variant["id"]}',
                'image_link': urls[0],
                'availability': 'in_stock' if variant['available'] else 'out_of_stock',
                'shipping_weight': f'{grams:g} g', 'price': variant['price'] + ' USD',
                'brand': 'FLYLYFE', 'condition': 'new', 'identifier_exists': 'false',
                'google_product_category': '212',
                'product_type': 'Apparel & Accessories > Clothing > Shirts & Tops > Graphic Tees',
                'color': color, 'size': size,
                'gender': 'female' if '-womens' in handle else 'male', 'age_group': 'adult',
                'material': facts['material'], 'size_type': 'regular', 'size_system': 'US',
            }
            lines = ['  <item>']
            for name, value in values.items():
                lines.append(f'    <g:{name}>{escape(str(value))}</g:{name}>')
                if name == 'image_link':
                    lines.extend(f'    <g:additional_image_link>{escape(url)}</g:additional_image_link>' for url in urls[1:])
            additions.append('\n'.join(lines + ['  </item>']))
    if additions:
        source = source.replace('</channel>', '\n'.join(additions) + '\n</channel>')
    ET.fromstring(source)
    return source, {'added_variants': len(additions), 'pending_image_review': pending,
                    'covered_variants': len(current) + len(additions)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('catalog', type=Path)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--expand-reviewed', action='store_true', help='Add current site variants with curated product/color images')
    parser.add_argument('--coverage-report', type=Path, help='Write pending image-review coverage as JSON')
    args = parser.parse_args()
    feed = ROOT / 'feed/google-products.xml'
    before = feed.read_text()
    catalog = json.loads(args.catalog.read_text())
    images = json.loads((ROOT / 'tools/merchant-feed-images.json').read_text())
    result, removed = repair(before, catalog, images)
    coverage = None
    if args.expand_reviewed or args.coverage_report:
        expanded, coverage = expand_reviewed(result, catalog, images)
        if args.expand_reviewed:
            result = expanded
        if args.coverage_report:
            args.coverage_report.write_text(json.dumps(coverage, indent=2) + '\n')
    if args.check:
        assert result == before, 'Feed differs from current catalog and curated images'
    else:
        feed.write_text(result)
    print(f'{len(ET.fromstring(result).findall(".//item"))} verified offers; removed {len(removed)} obsolete variants')
    if coverage:
        print(f'{coverage["added_variants"]} reviewed variants {"added" if args.expand_reviewed else "available to add"}; '
              f'{len(coverage["pending_image_review"])} variants await image review')
    for offer in removed:
        print('Removed:', offer)
