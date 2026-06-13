#!/usr/bin/env python3
"""Pull accurate Printful mockups (front+back, all colors) for all 6 products into local assets,
keyed by handle+color+view, for a back-first product display."""
import json, os, urllib.request, time

ENV = {}
for line in open(os.path.expanduser("~/.hermes/secrets/flylyfe.env")):
    line=line.strip()
    if "=" in line and not line.startswith("#"): k,v=line.split("=",1); ENV[k]=v
SH = {"X-Shopify-Access-Token": ENV["SHOPIFY_ADMIN_FULL_TOKEN"]}
STORE = ENV["SHOPIFY_STORE"]

PRODUCTS = {
    "the-anthem-tee":        8779549343897,
    "the-conga-tee":         8779549376665,
    "the-signature-tee":     8779549409433,
    "the-anthem-tee-womens": 8779549442201,
    "the-conga-tee-womens":  8779549474969,
    "the-signature-tee-womens":8779549507737,
}

OUT = "/Users/teddy/flylyfe-site/assets/products"
os.makedirs(OUT, exist_ok=True)

def req(url):
    r = urllib.request.Request(url, headers=SH)
    with urllib.request.urlopen(r, timeout=60) as resp:
        return json.loads(resp.read().decode())

manifest = {}
for handle, pid in PRODUCTS.items():
    data = req(f"https://{STORE}/admin/api/2025-10/products/{pid}/images.json")
    manifest[handle] = {}
    for im in data["images"]:
        alt = (im.get("alt") or "").lower()
        # alt format: "FLYLYFE <title> <Color> <front|back>"
        parts = alt.split()
        if not parts: continue
        view = "back" if "back" in parts else ("front" if "front" in parts else None)
        color = None
        for c in ["white","black","ivory","natural"]:
            if c in parts: color = c.capitalize(); break
        if not view or not color: continue
        src = im["src"].split("?")[0]
        fn = f"{handle}-{color}-{view}.jpg"
        urllib.request.urlretrieve(src, f"{OUT}/{fn}")
        manifest[handle].setdefault(color, {})[view] = f"assets/products/{fn}"
        print("saved", fn, flush=True)
        time.sleep(0.3)

json.dump(manifest, open(f"{OUT}/manifest.json","w"), indent=1)
print("\nMANIFEST:")
print(json.dumps(manifest, indent=1))
