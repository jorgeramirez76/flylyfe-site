#!/usr/bin/env python3
"""Build AI reference files from the current HTML, without rebuilding the storefront.

Install tools/requirements-seo.txt, then run:
  python3 tools/build_ai_exports.py --updated YYYY-MM-DD
Use --check with the same date to detect stale exports before deploying.
"""
import argparse
from datetime import date
import json
from pathlib import Path
import re
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup, Comment, NavigableString

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://www.flylyfe.com/'
SKIP = {'script', 'style', 'noscript', 'nav', 'footer', 'button', 'form', 'select'}
BLOCK = {'p', 'div', 'section', 'article', 'details', 'ul', 'ol', 'table', 'blockquote'}


def render(node, url):
    if isinstance(node, Comment):
        return ''
    if isinstance(node, NavigableString):
        return re.sub(r'\s+', ' ', str(node))
    if node.name in SKIP or node.has_attr('hidden') or node.get('aria-hidden') == 'true':
        return ''
    text = ''.join(render(child, url) for child in node.children)
    if re.fullmatch(r'h[1-6]', node.name or ''):
        return '\n\n' + '#' * int(node.name[1]) + ' ' + text.strip() + '\n\n'
    if node.name == 'summary':
        return '\n\n### ' + text.strip() + '\n\n'
    if node.name == 'a' and text.strip() and node.get('href'):
        target = urljoin(url, node['href'])
        if urlparse(target).scheme in {'http', 'https', 'mailto'}:
            return f'[{text.strip()}]({target})'
    if node.name == 'li':
        return '\n- ' + text.strip() + '\n'
    if node.name in {'td', 'th'}:
        return text.strip() + ' | '
    if node.name in {'br', 'tr'}:
        return text + '\n'
    if node.name in BLOCK:
        return '\n\n' + text.strip() + '\n\n'
    return text


def load_pages():
    pages = []
    urls = [n.text for n in ET.parse(ROOT / 'sitemap.xml').iter()
            if n.tag == '{http://www.sitemaps.org/schemas/sitemap/0.9}loc']
    for url in urls:
        path = urlparse(url).path.lstrip('/')
        file = ROOT / (path + 'index.html' if not path or path.endswith('/') else path)
        soup = BeautifulSoup(file.read_text(), 'html.parser')
        canonical = soup.find('link', rel='canonical')
        assert canonical and canonical['href'] == url, f'Canonical mismatch: {file}'
        main = soup.find('main')
        if not main:  # Homepage is represented by its metadata; other pages have main.
            assert url == BASE, f'Missing main: {file}'
        description = soup.find('meta', attrs={'name': 'description'})
        assert description and description.get('content'), f'Missing description: {file}'
        products = []
        for script in soup.select('script[type="application/ld+json"]'):
            data = json.loads(script.string)
            products.extend(n for n in data.get('@graph', [data]) if n.get('@type') == 'Product')
        if path.startswith('products/'):
            assert len(products) == 1, f'Missing/duplicate Product: {file}'
            assert products[0]['name'] == soup.h1.get_text(' ', strip=True), f'Product identity mismatch: {file}'
        body = render(main, url) if main else description['content']
        body = re.sub(r'\n[ \t]+', '\n', body)
        body = re.sub(r'\n{3,}', '\n\n', body).strip()
        body = '\n'.join(line.rstrip() for line in body.splitlines())
        pages.append(dict(url=url, path=path, title=soup.title.get_text(strip=True),
                          summary=description['content'], body=body, products=products))
    return pages


def build(updated):
    pages = load_pages()
    intro = f'''# FLYLYFE

> New York City house-music streetwear, established in 2007. Feel the Music. Feel the Vibe. Live Your Lyfe.

Last updated: {updated}
Canonical site: {BASE}
Sitemap: {BASE}sitemap.xml
Full page content: {BASE}llms-full.txt

These reference files are generated from the public site. Each entry links to its source.
Use the product page and checkout for current pricing, variants, availability, and shipping.

'''
    sections = [('', 'Homepage'), ('products/', 'Products'), ('collections/', 'Collections'),
                ('blog/', 'Journal'), ('es/', 'En español'), ('info', 'Brand and customer help')]
    brief = intro
    for prefix, title in sections:
        selected = [p for p in pages if (p['path'] == '' if prefix == '' else
                    '/' not in p['path'] and p['path'] != '' if prefix == 'info' else
                    p['path'].startswith(prefix))]
        brief += f'## {title}\n\n'
        for page in selected:
            brief += f"- [{page['title']}]({page['url']}): {page['summary']}\n"
        brief += '\n'
    brief += '## Product facts\n\n'
    for page in pages:
        if not page['path'].startswith('products/'):
            continue
        product = page['products'][0]
        offer = product['offers']
        facts = '; '.join(f"{p['name']}: {p['value']}" for p in product.get('additionalProperty', []))
        brief += f"- [{product['name']}]({page['url']}): {offer['price']} {offer['priceCurrency']}; {facts}.\n"
    full = f'# FLYLYFE — public page content\n\nLast updated: {updated}\nSource index: {BASE}llms.txt\n\n'
    for page in pages:
        full += f"---\nURL: {page['url']}\nTITLE: {page['title']}\nSUMMARY: {page['summary']}\n\n{page['body']}\n\n"
    return {'llms.txt': brief, 'llms-full.txt': full.rstrip() + '\n'}, pages


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--updated', required=True, type=date.fromisoformat)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    outputs, pages = build(args.updated.isoformat())
    for name, text in outputs.items():
        path = ROOT / name
        if args.check:
            assert path.read_text() == text, f'{name} is stale; regenerate exports'
        else:
            path.write_text(text)
    print(f'{"Checked" if args.check else "Generated"} both exports: {len(pages)} pages, '
          f'{sum(p["path"].startswith("products/") for p in pages)} English products')
