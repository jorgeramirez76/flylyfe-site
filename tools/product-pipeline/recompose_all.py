#!/usr/bin/env python3
"""Master recompose: all 58 FLYLYFE product images with current art + fixed _realistic
(solid clean ink on dark shirts). Light shirts unchanged (multiply). Reusable + targetable."""
import os, sys, json, numpy as np, importlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import flprod; importlib.reload(flprod)
from PIL import Image, ImageFilter

SCR=os.path.dirname(os.path.abspath(__file__))
PR=os.path.expanduser("~/flylyfe-site/assets/print")
XL=f"{SCR}/xl"
OUT=os.path.expanduser("~/flylyfe-site/assets/products-model")
GEO=json.load(open(f"{SCR}/geom_cache.json"))

def P(n): return f"{PR}/{n}"
def X(n): return f"{XL}/{n}"
# art
WORD=(P("flylyfe-wordmark-only-BLACK.png"), P("flylyfe-wordmark-only-WHITE.png"))
CONGA=(P("flylyfe-conga-OUTLINE-dark-ink-for-light-shirts.png"), P("flylyfe-conga-OUTLINE-white-ink-for-dark-shirts.png"))
FEEL=(X("fm-final-light.png"), X("fm-final-dark.png"))
HMF=(P("flylyfe-housemusic-front-spaced-light.png"), P("flylyfe-housemusic-front-spaced-dark.png"))
HMB=(P("flylyfe-housemusic-back-dark-for-light-shirts.png"), P("flylyfe-housemusic-back-light-for-dark-shirts.png"))
TOKF=(P("flylyfe-token-front-dark.png"), P("flylyfe-token-front-light.png"))
TOKB=(P("flylyfe-token-back-XL.png"), P("flylyfe-token-back-XL.png"))
SIGLOCK=(P("flylyfe-signature-back-lockup-light.png"), P("flylyfe-signature-back-lockup-dark.png"))
AFTERH=(None, P("drop02-after-hours-back.png"))
TEMPO =(None, P("drop02-tempo-back.png"))
COORD =(P("drop02-coordinates-back-XL.png"), None)
SPIRIT=(P("drop02-spiritual-thing-back.png"), None)
SANIF =(P("limited-sanitary-print-XL.png"), None)
SANIB =(P("limited-sanitary-back-XL.png"), None)

def blanks(gender,color,view):
    cmap={"White":"white","Black":"black","Ivory":"ivory","Natural":"ivory"}
    return f"{SCR}/blanks/{gender}_{cmap[color]}_{view}.png"

# spec: art(L,D), size, cy, xo, left_chest?  ; mode auto: Black->screen, light->multiply (override per design)
# (art, size, cy, xo, mode_light, mode_dark, left_chest)
def F(art,size,cy,xo=0.0,ml="multiply",md="screen",lc=False): return (art,size,cy,xo,ml,md,lc)

M_WORD_F = F(WORD,0.80,0.45)            # men's chest wordmark
W_WORD_F = F(WORD,0.72,0.46)            # women's chest wordmark (fitted)
SIG_F    = F(WORD,0.26,0.41,-0.20,lc=True)
DESIGNS={
 "the-conga-tee":        ("male",["White","Black","Ivory"], M_WORD_F, F(CONGA,0.72,0.50)),
 "the-anthem-tee":       ("male",["White","Black","Ivory"], M_WORD_F, F(FEEL,0.70,0.50,0.03)),
 "the-signature-tee":    ("male",["White","Black","Ivory"], SIG_F,    F(SIGLOCK,0.84,0.47)),
 "the-house-music-tee":  ("male",["White","Black","Ivory"], F(HMF,0.68,0.45), F(HMB,0.72,0.50,0.03)),
 "the-token-tee":        ("male",["White","Black","Ivory"], F(TOKF,0.42,0.43), F(TOKB,0.80,0.50,0.0,"emblem","emblem")),
 "the-anthem-tee-womens":   ("female",["White","Black","Natural"], W_WORD_F, F(FEEL,0.64,0.51,0.03)),
 "the-conga-tee-womens":    ("female",["White","Black","Natural"], W_WORD_F, F(CONGA,0.66,0.50)),
 "the-signature-tee-womens":("female",["White","Black","Natural"], F(WORD,0.24,0.42,-0.20,lc=True), F(SIGLOCK,0.78,0.48)),
 "the-after-hours-tee":  ("male",["Black"], M_WORD_F, F(AFTERH,0.74,0.50)),
 "the-tempo-tee":        ("male",["Black"], M_WORD_F, F(TEMPO,0.74,0.50)),
 "the-coordinates-tee":  ("male",["Ivory"], M_WORD_F, F(COORD,0.74,0.50)),
 "the-spiritual-thing-tee":("male",["Ivory"], M_WORD_F, F(SPIRIT,0.74,0.50)),
 "the-sanitary-code-tee":("male",["White"], F(SANIF,0.62,0.46,0.0,"emblem","emblem"), F(SANIB,0.78,0.50,0.0,"emblem","emblem")),
}

def comp(blank,art,size,cy,xo,mode,out,lc=False):
    g=GEO[os.path.basename(blank)]; base=Image.open(blank).convert("RGB"); W,H=base.size
    GC=flprod.GC_FACTOR*g['chest_w']*W; cx=g['cx']*W
    pr=Image.open(art).convert("RGBA"); bb=pr.split()[3].getbbox(); pr=pr.crop(bb)
    tw=int(size*GC); th=int(pr.height*(tw/pr.width))
    if lc: x0=int(cx+xo*GC-tw/2)
    else:  x0=int(cx+xo*GC-tw/2)
    y0=int(cy*H-th/2)
    pr=pr.resize((max(tw,1),max(th,1)),Image.LANCZOS)
    pr.putalpha(pr.split()[3].filter(ImageFilter.GaussianBlur(0.4)))
    x0=max(0,min(x0,W-tw)); y0=max(0,min(y0,H-th))
    reg=np.asarray(base.crop((x0,y0,x0+tw,y0+th)).convert("RGB"))
    res=flprod._realistic(reg,np.asarray(pr),0.96,mode)
    base.paste(Image.fromarray(res),(x0,y0)); base.save(out,"JPEG",quality=95)

def run(only=None):
    n=0
    for design,(gender,colors,fspec,bspec) in DESIGNS.items():
        if only and design not in only: continue
        for color in colors:
            dark = (color=="Black")
            for view,spec in (("front",fspec),("back",bspec)):
                artLD,size,cy,xo,ml,md,lc=spec
                art = artLD[1] if dark else artLD[0]
                if art is None: continue
                mode = md if dark else ml
                bp=blanks(gender,color,view)
                if not os.path.exists(bp): print("NOBASE",bp); continue
                comp(bp,art,size,cy,xo,mode,f"{OUT}/{design}-{color}-{view}.jpg",lc)
                n+=1
    print("composited",n,"images")

if __name__=="__main__":
    run(set(sys.argv[1:]) or None)
