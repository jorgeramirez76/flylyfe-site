"""Refresh existing offers from a public Shopify products.json snapshot.

Usage: python3 tools/repair_merchant_feed.py /path/to/products.json [--check]
Images are deliberately curated in merchant-feed-images.json, never generated or
inferred during refresh. This preserves offer IDs and does not expand the catalog.
"""
import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape

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
        for name, value in updates.items():
            block = re.sub(fr'<g:{name}>.*?</g:{name}>',
                           lambda _: f'<g:{name}>{escape(value)}</g:{name}>', block)
        extra = ''.join('\n    <g:additional_image_link>' + escape(u) + '</g:additional_image_link>' for u in urls[1:])
        return block.replace('</g:image_link>', '</g:image_link>' + extra)

    result = re.sub(r'<item>.*?</item>', item, source, flags=re.S)
    ET.fromstring(result)
    return result, removed


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('catalog', type=Path)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    feed = ROOT / 'feed/google-products.xml'
    before = feed.read_text()
    result, removed = repair(before, json.loads(args.catalog.read_text()),
                             json.loads((ROOT / 'tools/merchant-feed-images.json').read_text()))
    if args.check:
        assert result == before, 'Feed differs from current catalog and curated images'
    else:
        feed.write_text(result)
    print(f'{len(ET.fromstring(result).findall(".//item"))} verified offers; removed {len(removed)} obsolete variants')
    for offer in removed:
        print('Removed:', offer)
