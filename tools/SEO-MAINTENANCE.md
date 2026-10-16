# SEO content maintenance

The checked-in HTML is the source for the published storefront and AI reference files.
After changing product copy, prices, FAQs, policy text, or adding sitemap pages:

```sh
python3 -m pip install -r tools/requirements-seo.txt
python3 tools/link_product_fits.py
python3 tools/normalize_product_metadata.py
python3 tools/build_ai_exports.py --updated YYYY-MM-DD
python3 tools/link_product_fits.py --check
python3 tools/normalize_product_metadata.py --check
python3 tools/audit_discovery.py
python3 tools/build_ai_exports.py --updated YYYY-MM-DD --check
```

The exporter checks sitemap/canonical agreement and product identity, then renders each page independently. It preserves FAQ questions, size tables and source links; it does not copy one product's text into another. Review the generated diff before deploying. These files are supplementary references, not a guarantee of AI citations or rankings.

Keep one main landmark with `id="main-content"` and the keyboard skip link on each page. Give local images their actual intrinsic width and height; CSS controls their displayed size and crop. Card styles explicitly retain their existing 3:4 display ratio.

The product fit linker groups existing product slugs by design and links their current page titles. It does not infer availability, sizes, prices, or fabric. Run it after catalog changes so shoppers can compare cuts. The GitHub SEO check verifies these links and reference exports on pull requests and main-branch pushes. It checks against the recorded export date rather than forcing a daily freshness date.

The product metadata normalizer aligns social previews with each page's title, description and product image. It preserves the verified 30-day US return policy with customer-paid return shipping. If the actual policy changes, update the policy text and this source together. Shipping varies by weight and destination; maintain that in Merchant Center rather than declaring the minimum visible “from” price as a flat schema rate. Do not add a price expiry unless there is a real announced end date.

The discovery audit checks indexable pages against the sitemap, verifies canonical URLs and local page links, and reports the products outside the Google feed. A clean source audit is not a confirmation of indexing, live stock, rich results or feed acceptance. Product price/availability and feed images still need checking against Shopify and Merchant Center.

For the merchant feed, save a fresh public Shopify `products.json?limit=250` response and run:

```sh
python3 tools/repair_merchant_feed.py /path/to/products.json --expand-reviewed --coverage-report /path/to/feed-coverage.json
python3 tools/repair_merchant_feed.py /path/to/products.json --expand-reviewed --check
```

Expansion preserves every existing offer ID and adds only current product/color combinations in `merchant-feed-images.json`. New offers use the stable Shopify variant ID with a `flylyfe-` prefix. Unrelated Shopify products without site product pages are excluded. Inspect the coverage report: variants without reviewed images stay pending. Review the exact product, fit, color, artwork, primary angle, live image URL and synthetic-image provenance before adding a mapping. Historical supplier CDN images may have been removed even if an old record lists them. The source audit verifies feed image mappings and unique variant links, but it does not replace visual review or current Merchant Center diagnostics.

The older `build_static_seo_pages.py` has a catalog safety guard because its data does not contain every current product and article. Do not bypass that guard to refresh the AI files; use the dedicated exporter above.
