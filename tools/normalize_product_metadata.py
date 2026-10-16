#!/usr/bin/env python3
"""Keep product previews and supported return facts aligned with public pages.

Run after catalog changes, then regenerate AI references. --check never writes.
Shipping is weight/destination-dependent and belongs in the maintained Merchant
Center shipping configuration; do not encode a starting rate as a flat rate.
"""
import argparse
from html import escape
import json
from pathlib import Path
import re

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
JSON_LD = re.compile(r'(<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>)(.*?)(</script>)', re.S | re.I)
RETURN_POLICY = {
    '@type': 'MerchantReturnPolicy',
    'applicableCountry': 'US',
    'returnPolicyCategory': 'https://schema.org/MerchantReturnFiniteReturnWindow',
    'merchantReturnDays': 30,
    'returnMethod': 'https://schema.org/ReturnByMail',
    'returnFees': 'https://schema.org/ReturnFeesCustomerResponsibility',
    'merchantReturnLink': 'https://www.flylyfe.com/faq.html#returns',
}


def nodes(data):
    return data.get('@graph', [data])


def product_metadata(source):
    soup = BeautifulSoup(source, 'html.parser')
    products = [node for tag in soup.select('script[type="application/ld+json"]')
                for node in nodes(json.loads(tag.string)) if node.get('@type') == 'Product']
    if not products:
        return source, False
    assert len(products) == 1, 'Expected one primary product per page'
    product = products[0]
    canonical = soup.find('link', rel='canonical')['href']
    assert product['url'] == canonical, 'Product/canonical URL mismatch'
    title = soup.title.get_text()
    description = soup.find('meta', attrs={'name': 'description'})['content']
    image = product['image'][0] if isinstance(product['image'], list) else product['image']
    assert image.startswith('https://'), 'Product preview must use an absolute HTTPS image'

    def update_schema(match):
        data = json.loads(match[2])
        changed = False
        for node in nodes(data):
            if node.get('@type') != 'Product':
                continue
            offer = node['offers']
            before = json.dumps(offer, sort_keys=True)
            offer['hasMerchantReturnPolicy'] = RETURN_POLICY.copy()
            offer.setdefault('itemCondition', 'https://schema.org/NewCondition')
            # No announced price expiry; no single flat shipping rate.
            offer.pop('priceValidUntil', None)
            offer.pop('shippingDetails', None)
            changed = before != json.dumps(offer, sort_keys=True)
        return match[1] + json.dumps(data, ensure_ascii=True) + match[3] if changed else match[0]

    source = JSON_LD.sub(update_schema, source)
    tags = {
        'og:type': 'product', 'og:site_name': 'FLYLYFE', 'og:title': title,
        'og:description': description, 'og:url': canonical, 'og:image': image,
        'og:image:alt': product['name'], 'twitter:card': 'summary_large_image',
        'twitter:title': title, 'twitter:description': description,
        'twitter:image': image, 'twitter:image:alt': product['name'],
    }
    additions = []
    for key, value in tags.items():
        attr = 'property' if key.startswith('og:') else 'name'
        existing = soup.find_all('meta', attrs={attr: key})
        assert len(existing) <= 1, f'Duplicate {key}'
        tag = f'<meta {attr}="{key}" content="{escape(value, quote=True)}">'
        if existing:
            if existing[0].get('content') == value:
                continue
            pattern = re.compile(r'<meta\b(?=[^>]*\b' + attr + r'=["\']' + re.escape(key) + r'["\'])[^>]*>', re.I)
            source, count = pattern.subn(lambda _: tag, source)
            assert count == 1, f'Could not update {key}'
        else:
            additions.append(tag)
    if additions:
        source = source.replace('</head>', ''.join(additions) + '</head>', 1)
    return source, True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    count, stale = 0, []
    for path in sorted(ROOT.rglob('*.html')):
        if any(part.startswith('.') or part in {'node_modules', 'test-results', 'playwright-report'} for part in path.relative_to(ROOT).parts):
            continue
        before = path.read_text()
        after, is_product = product_metadata(before)
        count += is_product
        if before != after:
            stale.append(str(path.relative_to(ROOT)))
            if not args.check:
                path.write_text(after)
    if args.check and stale:
        raise SystemExit('Product metadata needs refresh:\n' + '\n'.join(stale))
    print(f'{count} product pages checked; {len(stale)} pages {"need updates" if args.check else "updated"}')


if __name__ == '__main__':
    main()
