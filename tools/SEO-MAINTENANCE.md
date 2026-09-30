# SEO content maintenance

The checked-in HTML is the source for the published storefront and AI reference files.
After changing product copy, prices, FAQs, policy text, or adding sitemap pages:

```sh
python3 -m pip install -r tools/requirements-seo.txt
python3 tools/build_ai_exports.py --updated YYYY-MM-DD
python3 tools/build_ai_exports.py --updated YYYY-MM-DD --check
```

The exporter checks sitemap/canonical agreement and product identity, then renders each page independently. It preserves FAQ questions, size tables and source links; it does not copy one product's text into another. Review the generated diff before deploying. These files are supplementary references, not a guarantee of AI citations or rankings.

Keep one main landmark with `id="main-content"` and the keyboard skip link on each page. Give local images their actual intrinsic width and height; CSS controls their displayed size and crop. Card styles explicitly retain their existing 3:4 display ratio.

The older `build_static_seo_pages.py` has a catalog safety guard because its data does not contain every current product and article. Do not bypass that guard to refresh the AI files; use the dedicated exporter above.
