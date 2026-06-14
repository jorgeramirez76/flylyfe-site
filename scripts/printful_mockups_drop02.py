#!/usr/bin/env python3
"""Generate real Printful tee mockups for DROP 02 (back placement, design on the actual blank).
Shopify-platform Printful store => product API is disabled; this uses the mockup-generator
(which works) to produce product-quality images. Saves to assets/products + Hermes/DROP02."""
import json, os, time, urllib.request, urllib.error
ENV={}
for ln in open(os.path.expanduser("~/.hermes/secrets/flylyfe.env")):
    ln=ln.strip()
    if "=" in ln and not ln.startswith("#"): k,v=ln.split("=",1); ENV[k]=v
TOK=ENV["PRINTFUL_TOKEN"]; SID=ENV["PRINTFUL_STORE_ID"]
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
def call(u, data=None, store=False):
    h={"Authorization":f"Bearer {TOK}","Content-Type":"application/json","User-Agent":UA}
    if store: h["X-PF-Store-Id"]=SID
    r=urllib.request.Request(u, headers=h, data=json.dumps(data).encode() if data else None,
                             method="POST" if data else "GET")
    for _ in range(6):
        try:
            with urllib.request.urlopen(r, timeout=90) as resp: return resp.getcode(), json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            if e.code==429: time.sleep(30); continue
            return e.code, json.loads(e.read().decode() or "{}")
        except Exception: time.sleep(8)
    return 0, {}

# 1) catalog variant ids via v2 (Black + Ivory, size L) for product 586 (Comfort Colors 1717)
code,j=call("https://api.printful.com/v2/catalog-products/586/catalog-variants?limit=120")
variants={}
for v in j.get("data",[]):
    if v.get("size")=="L" and v.get("color") in ("Black","Ivory"): variants[v["color"]]=v["id"]
print("variant ids (L):", variants, "(http", code, ")", flush=True)

BASE="https://raw.githubusercontent.com/jorgeramirez76/flylyfe-site/main/assets/print/"
JOBS=[("after-hours","Black"),("tempo","Black"),("coordinates","Ivory"),("spiritual-thing","Ivory")]
DEST=os.path.expanduser("~/Desktop/FLYLYFE/Hermes/DROP02")

tasks=[]
for slug,color in JOBS:
    vid=variants.get(color)
    if not vid: print("SKIP",slug,"- no",color,"variant",flush=True); continue
    payload={"variant_ids":[vid],"format":"jpg",
             "files":[{"placement":"back","image_url":BASE+f"drop02-{slug}-back.png"}]}
    code,r=call("https://api.printful.com/mockup-generator/create-task/586", payload, store=True)
    key=r.get("result",{}).get("task_key")
    if key: tasks.append((slug,key)); print("queued",slug,color,flush=True)
    else: print("ERR queue",slug,"http",code,str(r)[:220],flush=True)
    time.sleep(33)

for slug,key in tasks:
    ok=False
    for _ in range(24):
        code,r=call(f"https://api.printful.com/mockup-generator/task?task_key={key}", store=True)
        st=r.get("result",{}).get("status")
        if st=="completed":
            url=r["result"]["mockups"][0]["mockup_url"]
            for outdir in ("assets/products", DEST):
                try:
                    urllib.request.urlretrieve(url, os.path.join(outdir, f"drop02-{slug}-tee.jpg"))
                except Exception as e:
                    print("dl err",slug,e,flush=True)
            print("MOCKUP done:",slug,flush=True); ok=True; break
        if st=="failed": print("FAILED",slug,str(r)[:220],flush=True); break
        time.sleep(10)
    if not ok and st!="failed": print("TIMEOUT",slug,flush=True)
print("DONE",flush=True)
