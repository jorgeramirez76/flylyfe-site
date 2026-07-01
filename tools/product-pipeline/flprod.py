#!/usr/bin/env python3
"""FLYLYFE production compositor v2 — geometry-driven, research-calibrated.
Places real transparent print-art PNGs onto the consistent Higgsfield blank-tee bases
using per-(gender,view) garment anchors. Per-design overrides tune size/position to
Jorge's feedback now that Apliiq prints bigger than Printful did."""
import os, json, numpy as np
from PIL import Image, ImageFilter

ROOT  = os.path.expanduser("~/flylyfe-site/assets")
BASE  = f"{ROOT}/generated-model-bases/higgsfield"
PRINT = f"{ROOT}/print"
OUT   = f"{ROOT}/products-model"
os.makedirs(OUT, exist_ok=True)
GEOM  = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"geometry.json")))
GEOM["wren-front"]["chest_w"] = 0.55

GC_FACTOR = 0.70
# Big-but-tasteful streetwear max (research): % of VISIBLE (bbox-cropped) art vs garment panel.
SIZE_W = {"chest_small":0.55, "chest_wide":0.68, "back_big":0.62, "back_med":0.72, "back_yoke":0.30}
CENTER_Y = {("male","front"):0.440, ("wren","front"):0.445,
            ("male","back"):0.470, ("wren","back"):0.470}
NUDGE_Y  = {"chest_small":0.0, "chest_wide":0.0, "back_big":0.0, "back_med":0.0}
# --- per-design width (% of panel) + vertical overrides, per research spec ---
# fronts: wordmark hit ~0.55, text statement ~0.60, graphic ~0.68
FRONT_W_OVR = {"the-token-tee":0.50, "the-house-music-tee":0.60, "the-signature-tee":0.56,
               "the-signature-tee-womens":0.56, "the-sanitary-code-tee":0.68}
# backs: big graphic ~0.72, emblem ~0.70, manifesto/text ~0.62, lockup ~0.58
BACK_W_OVR  = {"the-anthem-tee":0.62, "the-anthem-tee-womens":0.62, "the-signature-tee":0.72,
               "the-signature-tee-womens":0.72, "the-house-music-tee":0.62, "the-token-tee":0.70}
FRONT_Y_OVR = {"the-sanitary-code-tee":0.500}
BACK_Y_OVR  = {}
HEM        = {("male","back"):0.705, ("wren","back"):0.750}
CREAM = np.array([1.0, 0.965, 0.885])

def _blend(b,k,mode):
    b=b.astype(np.float32); k=k.astype(np.float32)
    if mode=="multiply": return b*k/255.0
    if mode=="screen":   return 255.0-(255.0-b)*(255.0-k)/255.0
    return k

def _realistic(reg_u8, pr_rgba, opacity, mode):
    """Displacement-warp the print to the garment folds + fold/shadow lighting => printed-on look."""
    import cv2
    th,tw=reg_u8.shape[:2]
    gray=cv2.cvtColor(reg_u8,cv2.COLOR_RGB2GRAY).astype(np.float32)
    folds=cv2.GaussianBlur(gray,(0,0),max(tw,th)*0.013)
    gx=cv2.Scharr(folds,cv2.CV_32F,1,0); gy=cv2.Scharr(folds,cv2.CV_32F,0,1)
    nrm=max(abs(float(gx.min())),abs(float(gx.max())),abs(float(gy.min())),abs(float(gy.max())),1e-5)
    amp=max(tw,th)*0.0   # no displacement warp -> letters keep STRAIGHT edges (Jorge)
    xx,yy=np.meshgrid(np.arange(tw,dtype=np.float32),np.arange(th,dtype=np.float32))
    warp=cv2.remap(pr_rgba,(xx+amp*gx/nrm).astype(np.float32),(yy+amp*gy/nrm).astype(np.float32),
                   cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0))
    reg=reg_u8.astype(np.float32)
    p=warp.astype(np.float32); ink=p[...,:3].copy(); al=(p[...,3:4]/255.0)*opacity
    # fold/shadow lighting + fine fabric-grain so the ink sits IN the weave
    shade=np.clip((gray/max(gray.mean(),1.0)),0.80,1.16)
    hi=gray-cv2.GaussianBlur(gray,(0,0),max(tw,th)*0.0045); s=float(hi.std()) or 1.0
    shade=(shade*np.clip(1.0+0.26*(hi/(3*s)),0.93,1.07))[...,None]
    # gentle fold-only shade for bright/colored ink (screen+emblem): NO high-freq grain,
    # tight range -> solid ink stays SOLID & clean (no cracked/mottled washout on dark fabric)
    shade_solid=np.clip(gray/max(gray.mean(),1.0),0.90,1.08)[...,None]
    if mode=="screen":
        ink=ink*CREAM; al=np.clip(al*1.07,0.0,1.0)   # near-opaque so dark weave can't bleed through
        out=reg*(1-al)+(ink*shade_solid)*al
    elif mode=="emblem":
        out=reg*(1-al)+(ink*shade_solid)*al
    else:  # multiply (dark ink on light): seat ink INTO the fabric folds (stronger fold range,
           # no high-freq grain) so it reads printed-in-cotton, not a flat pasted sticker
        fold=np.clip(gray/max(gray.mean(),1.0),0.72,1.28)[...,None]
        out=reg*(1-al)+(_blend(reg,ink,mode)*fold)*al
    return np.clip(out,0,255).astype(np.uint8)

def composite(base_path, gender, view, print_path, size_class, mode, out_path, design=None, opacity=0.94):
    base=Image.open(base_path).convert("RGB"); W,H=base.size
    a=GEOM[f"{gender}-{view}"]
    GC=GC_FACTOR*a["chest_w"]*W
    cx=a["cx"]*W; collar=a["collar"]*H
    pr=Image.open(print_path).convert("RGBA")
    abox=pr.split()[3].getbbox()
    if abox: pr=pr.crop(abox)
    if size_class=="left_chest":            # small left-chest logo (image-left upper chest)
        tw=int(0.19*GC); th=int(pr.height*(tw/pr.width))
        x0=int(round(cx-0.30*GC)); y0=int(round(0.395*H))
    elif size_class=="back_yoke":
        tw=int(SIZE_W[size_class]*GC); th=int(pr.height*(tw/pr.width))
        x0=int(round(cx-tw/2)); y0=int(round(collar+0.05*GC))
    elif view=="back":
        tw=int(BACK_W_OVR.get(design,SIZE_W[size_class])*GC); th=int(pr.height*(tw/pr.width))
        x0=int(round(cx-tw/2)); y0=int(round(BACK_Y_OVR.get(design,CENTER_Y[(gender,view)])*H-th/2))
    else:  # front
        tw=int(FRONT_W_OVR.get(design,SIZE_W[size_class])*GC); th=int(pr.height*(tw/pr.width))
        x0=int(round(cx-tw/2)); y0=int(round((FRONT_Y_OVR.get(design,CENTER_Y[(gender,view)]+NUDGE_Y[size_class]))*H-th/2))
    pr=pr.resize((max(tw,1),max(th,1)),Image.LANCZOS)
    pr.putalpha(pr.split()[3].filter(ImageFilter.GaussianBlur(0.6)))
    x0=max(0,min(x0,W-tw)); y0=max(0,min(y0,H-th))
    reg_u8=np.asarray(base.crop((x0,y0,x0+tw,y0+th)).convert("RGB"))
    out=_realistic(reg_u8, np.asarray(pr), opacity, mode)
    base.paste(Image.fromarray(out),(x0,y0))
    base.save(out_path,"JPEG",quality=92); return out_path

P=lambda n:f"{PRINT}/{n}"
WORD_L=P("flylyfe-wordmark-only-BLACK.png"); WORD_D=P("flylyfe-wordmark-only-WHITE.png")
SIG_F=("left_chest", WORD_L, WORD_D,"multiply","screen")    # small logo, top-left chest
SIG_B=("back_med",   WORD_L, WORD_D,"multiply","screen")    # one large wordmark across the back
WORDF=("chest_small", WORD_L, WORD_D,"multiply","screen")
CONGA_B=("back_med", P("flylyfe-conga-OUTLINE-dark-ink-for-light-shirts.png"), P("flylyfe-conga-OUTLINE-white-ink-for-dark-shirts.png"),"multiply","screen")

DESIGNS = {
 "the-anthem-tee":{"gender":"male","colors":["White","Black","Ivory"],"front":WORDF,
    "back":("back_big",P("flylyfe-feel-music-stack-BLACK-INK-for-light-shirts-transparent.png"),P("flylyfe-feel-music-stack-transparent-print.png"),"multiply","screen")},
 "the-conga-tee":{"gender":"male","colors":["White","Black","Ivory"],"front":WORDF,"back":CONGA_B},
 "the-signature-tee":{"gender":"male","colors":["White","Black","Ivory"],"front":SIG_F,"back":SIG_B},
 "the-house-music-tee":{"gender":"male","colors":["White","Black","Ivory"],
    "front":("chest_wide",P("flylyfe-housemusic-front-dark-for-light-shirts.png"),P("flylyfe-housemusic-front-light-for-dark-shirts.png"),"multiply","screen"),
    "back":("back_med",P("flylyfe-housemusic-back-dark-for-light-shirts.png"),P("flylyfe-housemusic-back-light-for-dark-shirts.png"),"multiply","screen")},
 "the-token-tee":{"gender":"male","colors":["White","Black","Ivory"],
    "front":("chest_small",P("flylyfe-token-front-dark.png"),P("flylyfe-token-front-light.png"),"multiply","screen"),
    "back":("back_med",P("flylyfe-token-back-FINAL.png"),P("flylyfe-token-back-FINAL.png"),"emblem","emblem")},
 "the-anthem-tee-womens":{"gender":"wren","colors":["White","Black","Natural"],"front":WORDF,
    "back":("back_big",P("flylyfe-feel-music-stack-BLACK-INK-for-light-shirts-transparent.png"),P("flylyfe-feel-music-stack-transparent-print.png"),"multiply","screen")},
 "the-conga-tee-womens":{"gender":"wren","colors":["White","Black","Natural"],"front":WORDF,"back":CONGA_B},
 "the-signature-tee-womens":{"gender":"wren","colors":["White","Black","Natural"],"front":SIG_F,"back":SIG_B},
 "the-after-hours-tee":{"gender":"male","colors":["Black"],"front":WORDF,
    "back":("back_med",None,P("drop02-after-hours-back.png"),"screen","screen")},
 "the-tempo-tee":{"gender":"male","colors":["Black"],"front":WORDF,
    "back":("back_med",None,P("drop02-tempo-back.png"),"screen","screen")},
 "the-coordinates-tee":{"gender":"male","colors":["Ivory"],"front":WORDF,
    "back":("back_med",P("drop02-coordinates-back.png"),None,"multiply","multiply")},
 "the-spiritual-thing-tee":{"gender":"male","colors":["Ivory"],"front":WORDF,
    "back":("back_med",P("drop02-spiritual-thing-back.png"),None,"multiply","multiply")},
 "the-sanitary-code-tee":{"gender":"male","colors":["White"],
    "front":("chest_wide",P("limited-sanitary-print.png"),None,"emblem","emblem"),
    "back":("back_med",P("limited-sanitary-back.png"),None,"emblem","emblem")},
}

def tone(c): return "dark" if c=="Black" else "light"
def base_path(gender,color,view):
    cmap={"White":"white","Black":"black","Ivory":"ivory","Natural":"natural"}
    pfx="wren" if gender=="wren" else "male"
    return f"{BASE}/{pfx}-{cmap[color]}-{view}-base.png"

if __name__=="__main__":
    import sys
    only=set(sys.argv[1:])  # optional: regenerate only specified handles
    manifest=json.load(open(f"{OUT}/manifest.json")) if os.path.exists(f"{OUT}/manifest.json") else {}
    made=[]; skipped=[]
    for design,cfg in DESIGNS.items():
        if only and design not in only:
            continue
        g=cfg["gender"]; manifest.setdefault(design,{})
        for color in cfg["colors"]:
            t=tone(color); manifest[design].setdefault(color,{})
            for view in ("front","back"):
                spec=cfg.get(view)
                if not spec: continue
                size_class,pl,pd,bl,bd=spec
                pr=pd if t=="dark" else pl; blend=bd if t=="dark" else bl
                if pr is None: skipped.append((design,color,view)); continue
                bp=base_path(g,color,view)
                if not os.path.exists(bp): skipped.append((design,color,view,"NOBASE")); continue
                outp=f"{OUT}/{design}-{color}-{view}.jpg"
                composite(bp,g,view,pr,size_class,blend,outp,design=design)
                manifest[design][color][view]=f"assets/products-model/{design}-{color}-{view}.jpg"
                made.append(f"{design}-{color}-{view}")
    json.dump(manifest,open(f"{OUT}/manifest.json","w"),indent=1)
    print(f"MADE {len(made)} images, skipped {len(skipped)}")
