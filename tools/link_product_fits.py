#!/usr/bin/env python3
"""Link existing cuts of the same design; never infer sizes, stock or prices.

Run after adding product pages and before build_ai_exports.py. --check is read-only.
"""
import argparse
import html
import re
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
START = '<!-- related-product-fits:start -->'
END = '<!-- related-product-fits:end -->'
PATTERN = re.compile(re.escape(START) + r'.*?' + re.escape(END), re.S)


def run(check=False):
    groups = {}
    for path in sorted((ROOT / 'products').glob('*/index.html')):
        slug = path.parent.name
        base = re.sub(r'-womens(?:-fitted)?$', '', slug)
        soup = BeautifulSoup(path.read_text(), 'html.parser')
        canonical = soup.select_one('link[rel="canonical"]')
        robots = soup.select_one('meta[name="robots"]')
        if not canonical or not soup.h1 or (robots and 'noindex' in robots.get('content', '')):
            continue
        groups.setdefault(base, []).append((path, canonical['href'], soup.h1.get_text(' ', strip=True)))
    changed = []
    for members in groups.values():
        if len(members) < 2:
            continue
        for path, url, title in members:
            links = ''.join(f'<li><a href="{html.escape(other_url, quote=True)}">{html.escape(other_title)}</a></li>'
                            for other_path, other_url, other_title in members if other_path != path)
            block = (START + '<section class="seo-section" aria-labelledby="related-fits-heading">'
                     '<h2 id="related-fits-heading">Explore this design in other fits</h2>'
                     '<p>Compare the fit and size information on each product page before choosing.</p>'
                     '<ul>' + links + '</ul></section>' + END)
            original = path.read_text()
            if START in original:
                updated = PATTERN.sub(lambda _: block, original)
            else:
                if original.count('</main>') != 1:
                    raise ValueError(f'Expected one main landmark: {path}')
                updated = original.replace('</main>', block + '</main>')
            if updated != original:
                changed.append(path.relative_to(ROOT).as_posix())
                if not check:
                    path.write_text(updated)
    if check and changed:
        raise SystemExit('Stale product fit links: ' + ', '.join(changed))
    print(f'Product fit links: {len(groups)} design groups; {len(changed)} pages ' + ('need updates' if check else 'updated'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    run(parser.parse_args().check)
