#!/usr/bin/env python3
"""FLYLYFE: generate Printful mockups for all products/colors and attach to Shopify."""
import json, time, subprocess, os, sys, urllib.request

ENV = {}
for line in open(os.path.expanduser("~/.hermes/secrets/flylyfe.env")):
    line = line.strip()
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1); ENV[k] = v

PF = {"Authorization": f"Bearer {ENV['PRINTFUL_TOKEN']}", "X-PF-Store-Id": ENV["PRINTFUL_STORE_ID"], "Content-Type": "application/json"}
SH = {"X-Shopify-Access-Token": ENV["SHOPIFY_ADMIN_FULL_TOKEN"], "Content-Type": "application/json"}
STORE = ENV["SHOPIFY_STORE"]

def req(url, headers, data=None, method=None):
    r = urllib.request.Request(url, headers=headers, method=method or ("POST" if data else "GET"),
                               data=json.dumps(data).encode() if data else None)
    for attempt in range(5):
        try:
            with urllib.request.urlopen(r, timeout=60) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode()[:300]
            if e.code == 429:
                time.sleep(35); continue
            return {"_error": e.code, "_body": body}
        except Exception as e:
            time.sleep(10)
    return {"_error": "retries exhausted"}

vmap = {tuple(k.split("|")): v for k, v in json.load(open("/tmp/flylyfe_vmap.json")).items()}
prods = json.load(open("/tmp/shopify_products.json"))  # [(title, id, handle)]
pid_by_title = {t: i for t, i, h in prods}

BASE = "https://raw.githubusercontent.com/jorgeramirez76/flylyfe-site/main/assets/print/"
F = {
 "logo_black":  BASE+"flylyfe-logo-tagline-wide-BLACK-INK-for-light-shirts-transparent.png",
 "logo_white":  BASE+"flylyfe-logo-tagline-wide-transparent-print.png",
 "stack_black": BASE+"flylyfe-feel-music-stack-BLACK-INK-for-light-shirts-transparent.png",
 "stack_color": BASE+"flylyfe-feel-music-stack-transparent-print.png",
 "dancer_black":BASE+"flylyfe-music-dancer-conga-transparent-print.png",
 "dancer_white":BASE+"flylyfe-music-dancer-conga-WHITE-INK-for-dark-shirts-transparent.png",
}
CHEST = dict(area_width=1800, area_height=2400, width=550, height=140, top=240, left=1050)
BACK_STACK  = dict(area_width=1800, area_height=2400, width=1650, height=2299, top=60, left=75)
BACK_DANCER = dict(area_width=1800, area_height=2400, width=1700, height=1235, top=320, left=50)
FRONT_LOGO_BIG = dict(area_width=1800, area_height=2400, width=1700, height=431, top=480, left=50)

def files_for(design, color):
    dark = color == "Black"
    logo = F["logo_white"] if dark else F["logo_black"]
    if design == "logo":
        return [{"placement": "front", "image_url": logo, "position": FRONT_LOGO_BIG}]
    back = (F["stack_color"] if dark else F["stack_black"]) if design == "stack" else (F["dancer_white"] if dark else F["dancer_black"])
    pos = BACK_STACK if design == "stack" else BACK_DANCER
    return [{"placement": "front", "image_url": logo, "position": CHEST},
            {"placement": "back", "image_url": back, "position": pos}]

JOBS = [
 ("men",586,"The Anthem Tee","stack",["White","Black","Ivory"]),
 ("men",586,"The Conga Tee","dancer",["White","Black","Ivory"]),
 ("men",586,"The Signature Tee","logo",["White","Black","Ivory"]),
 ("women",360,"The Anthem Tee — Women's","stack",["White","Black","Natural"]),
 ("women",360,"The Conga Tee — Women's","dancer",["White","Black","Natural"]),
 ("women",360,"The Signature Tee — Women's","logo",["White","Black","Natural"]),
]

# Phase 1: queue tasks (paced for rate limit)
tasks = []
for gender, cat_id, title, design, colors in JOBS:
    for color in colors:
        vid, _ = vmap[(gender, color, "M")]
        payload = {"variant_ids": [vid], "format": "jpg", "files": files_for(design, color)}
        r = req(f"https://api.printful.com/mockup-generator/create-task/{cat_id}", PF, payload)
        if r.get("code") == 200:
            tasks.append({"title": title, "color": color, "key": r["result"]["task_key"]})
            print(f"queued {title} / {color}", flush=True)
        else:
            print(f"QUEUE-ERR {title} / {color}: {str(r)[:200]}", flush=True)
        json.dump(tasks, open("/tmp/mockup_tasks.json", "w"))
        time.sleep(32)

# Phase 2: poll results
results = []
for t in tasks:
    for _ in range(20):
        r = req(f"https://api.printful.com/mockup-generator/task?task_key={t['key']}", PF)
        st = r.get("result", {}).get("status")
        if st == "completed":
            for m in r["result"]["mockups"]:
                results.append({**t, "placement": m.get("placement", "front"), "url": m["mockup_url"]})
                for ex in m.get("extra", []):
                    results.append({**t, "placement": ex.get("option", ""), "url": ex["url"]})
            break
        if st == "failed":
            print(f"TASK-FAILED {t['title']} {t['color']}: {str(r)[:200]}", flush=True)
            break
        time.sleep(10)
json.dump(results, open("/tmp/mockup_results.json", "w"))
print(f"{len(results)} mockup images generated", flush=True)

# Phase 3: attach to Shopify products (front+back per color)
order = {"front": 0, "back": 1}
by_product = {}
for m in results:
    if m["placement"].lower() not in ("front", "back"): continue
    by_product.setdefault(m["title"], []).append(m)

for title, imgs in by_product.items():
    pid = pid_by_title.get(title)
    if not pid: continue
    imgs.sort(key=lambda m: ({"Black": 0, "White": 1, "Ivory": 2, "Natural": 2}.get(m["color"], 3), order.get(m["placement"].lower(), 2)))
    for i, m in enumerate(imgs):
        r = req(f"https://{STORE}/admin/api/2025-10/products/{pid}/images.json", SH,
                {"image": {"src": m["url"], "position": i + 1, "alt": f"FLYLYFE {title} {m['color']} {m['placement']}"}})
        ok = "image" in r
        print(f"attach {title} {m['color']} {m['placement']}: {'OK' if ok else str(r)[:150]}", flush=True)
        time.sleep(1)

print("ALL DONE", flush=True)
