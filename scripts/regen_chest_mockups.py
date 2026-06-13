#!/usr/bin/env python3
"""Regenerate FRONT chest mockups with wordmark-only logo, lower placement; replace Shopify front images."""
import json, time, os, urllib.request

ENV = {}
for line in open(os.path.expanduser("~/.hermes/secrets/flylyfe.env")):
    line=line.strip()
    if "=" in line and not line.startswith("#"): k,v=line.split("=",1); ENV[k]=v
PF = {"Authorization": f"Bearer {ENV['PRINTFUL_TOKEN']}", "X-PF-Store-Id": ENV["PRINTFUL_STORE_ID"], "Content-Type":"application/json"}
SH = {"X-Shopify-Access-Token": ENV["SHOPIFY_ADMIN_FULL_TOKEN"], "Content-Type":"application/json"}
STORE = ENV["SHOPIFY_STORE"]

def req(url, headers, data=None, method=None):
    r = urllib.request.Request(url, headers=headers, method=method or ("POST" if data else "GET"),
                               data=json.dumps(data).encode() if data else None)
    for _ in range(5):
        try:
            with urllib.request.urlopen(r, timeout=60) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429: time.sleep(35); continue
            return {"_error": e.code, "_body": e.read().decode()[:200]}
        except Exception:
            time.sleep(10)
    return {"_error":"exhausted"}

vmap = {tuple(k.split("|")): v for k,v in json.load(open("/tmp/flylyfe_vmap.json")).items()}
BASE = "https://raw.githubusercontent.com/jorgeramirez76/flylyfe-site/main/assets/print/"
WM_B = BASE+"flylyfe-wordmark-only-BLACK.png"
WM_W = BASE+"flylyfe-wordmark-only-WHITE.png"
# 5in wide on 1800px/12in canvas = 750px? print area 1800px wide = 12in -> 150dpi. 5in=750px? No: CC1717 front area 1800x2400 px at 150dpi = 12x16in. 4.5in = 675px.
CHEST = dict(area_width=1800, area_height=2400, width=620, height=61, top=380, left=1000)

JOBS = [
 ("men",586,"The Anthem Tee",8779549343897,["White","Black","Ivory"]),
 ("men",586,"The Conga Tee",8779549376665,["White","Black","Ivory"]),
 ("women",360,"The Anthem Tee — Women's",8779549442201,["White","Black","Natural"]),
 ("women",360,"The Conga Tee — Women's",8779549474969,["White","Black","Natural"]),
]

tasks=[]
for gender,cat,title,pid,colors in JOBS:
    for color in colors:
        vid,_ = vmap[(gender,color,"M")]
        logo = WM_W if color=="Black" else WM_B
        payload={"variant_ids":[vid],"format":"jpg",
                 "files":[{"placement":"front","image_url":logo,"position":CHEST}]}
        r = req(f"https://api.printful.com/mockup-generator/create-task/{cat}", PF, payload)
        if r.get("code")==200:
            tasks.append({"title":title,"pid":pid,"color":color,"key":r["result"]["task_key"]})
            print("queued",title,color,flush=True)
        else:
            print("ERR",title,color,str(r)[:150],flush=True)
        time.sleep(32)

results=[]
for t in tasks:
    for _ in range(20):
        r = req(f"https://api.printful.com/mockup-generator/task?task_key={t['key']}", PF)
        st = r.get("result",{}).get("status")
        if st=="completed":
            for m in r["result"]["mockups"]:
                results.append({**t,"url":m["mockup_url"]}); break
            break
        if st=="failed": print("FAILED",t["title"],t["color"],flush=True); break
        time.sleep(10)
print(len(results),"new front mockups",flush=True)

# replace front images per product
for gender,cat,title,pid,colors in JOBS:
    imgs = req(f"https://{STORE}/admin/api/2025-10/products/{pid}/images.json", SH)["images"]
    for im in imgs:
        if "front" in (im.get("alt") or "").lower():
            req(f"https://{STORE}/admin/api/2025-10/products/{pid}/images/{im['id']}.json", SH, method="DELETE")
            time.sleep(0.5)
    order={"Black":1,"White":3,"Ivory":5,"Natural":5}
    for m in [x for x in results if x["pid"]==pid]:
        req(f"https://{STORE}/admin/api/2025-10/products/{pid}/images.json", SH,
            {"image":{"src":m["url"],"position":order.get(m["color"],6),
                      "alt":f"FLYLYFE {title} {m['color']} front"}})
        print("attached",title,m["color"],flush=True)
        time.sleep(1)
print("DONE",flush=True)
