#!/usr/bin/env python3
"""FLYLYFE — DROP 02 design generator (local, free, exact typography via Pillow).
Renders 4 on-brand back-print designs NATIVELY at 3x = ~3240x4050 px (true ~300 DPI on an
~11in back placement) as transparent Printful-ready prints, plus downscaled 1080-wide site plates.
No AI, no external accounts. S = supersample / DPI scale."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, math

OUT_PLATE = "assets/products"
OUT_PRINT = "assets/print"
os.makedirs(OUT_PLATE, exist_ok=True)

S = 3  # 1 = 150dpi(1080w) preview; 3 = ~300dpi native print (3240w)

# palette
GOLD=(242,201,76); INK=(28,28,30); CREAM=(241,232,210); WHITE=(245,242,234); DIM=(150,150,150)
GOLD_DK=(176,140,40)
F = "/System/Library/Fonts/Supplemental/"
def font(name, size):
    paths={"black":F+"Arial Bold.ttf","bold":F+"Arial Bold.ttf","reg":F+"Arial.ttf",
           "serif":F+"Georgia.ttf","serifb":F+"Georgia Bold.ttf","times":F+"Times New Roman.ttf"}
    p=paths.get(name,paths["reg"])
    if not os.path.exists(p): p=F+"Arial.ttf"
    return ImageFont.truetype(p, int(size*S))   # fonts scale with S

WM_GOLD=Image.open(OUT_PRINT+"/flylyfe-wordmark-gold.png").convert("RGBA")
WM_WHITE=Image.open(OUT_PRINT+"/flylyfe-wordmark-only-WHITE.png").convert("RGBA")
WM_BLACK=Image.open(OUT_PRINT+"/flylyfe-wordmark-only-BLACK.png").convert("RGBA")

def tracked(draw, cx, y, txt, fnt, fill, ls=0, anchor_center=True):
    widths=[draw.textlength(c, font=fnt) for c in txt]
    total=sum(widths)+ls*(len(txt)-1)
    x = cx-total/2 if anchor_center else cx
    for c,w in zip(txt,widths):
        draw.text((x,y), c, font=fnt, fill=fill); x+=w+ls
    return total

def paste_wm(base, wm, cx, y, w):
    w=int(w); h=int(wm.height*(w/wm.width)); r=wm.resize((w,h), Image.LANCZOS)
    base.alpha_composite(r,(int(cx-w/2),int(y)))
    return h

def vignette(img, strength=0.55):
    w,h=img.size; mask=Image.new("L",(w,h),0); d=ImageDraw.Draw(mask)
    d.ellipse([-w*0.25,-h*0.25,w*1.25,h*1.25], fill=255)
    mask=mask.filter(ImageFilter.GaussianBlur(w*0.18))
    dark=Image.new("RGBA",(w,h),(0,0,0,int(255*strength)))
    inv=Image.eval(mask, lambda p:255-p); img.paste(dark,(0,0),inv); return img

def grain(img, amt=7):
    import random; w,h=img.size
    n=Image.effect_noise((w,h),amt).convert("L").point(lambda p:p).convert("RGBA")
    n.putalpha(14); img.alpha_composite(n); return img

W,Hh=1080*S,1350*S
def plate(bg, transparent=False):
    return Image.new("RGBA",(W,Hh),(0,0,0,0)) if transparent else Image.new("RGBA",(W,Hh),bg+(255,))

# ---------- DESIGN 1: AFTER HOURS (black tee) ----------
def d1(transparent=False):
    im=plate(INK,transparent); d=ImageDraw.Draw(im); cx=W/2
    tracked(d,cx,150*S,"AFTER",font("black",200),WHITE,4*S)
    tracked(d,cx,350*S,"HOURS",font("black",200),WHITE,4*S)
    d.line([(cx-300*S,610*S),(cx+300*S,610*S)],fill=GOLD,width=int(3*S))
    rows=[("01","MIDNIGHT"),("02","THE BASEMENT"),("03","SUNRISE SET"),("04","LAST TRAIN HOME")]
    fy=700*S; fn=font("bold",46); fr=font("reg",46)
    for num,title in rows:
        d.text((cx-330*S,fy),num,font=fn,fill=GOLD)
        d.text((cx-220*S,fy),title,font=fr,fill=WHITE); fy+=78*S
    paste_wm(im,WM_GOLD,cx,1130*S,360*S)
    tracked(d,cx,1230*S,"NEW YORK CITY  ·  EST. 2007",font("reg",26),DIM,8*S)
    return im,"after-hours","Ink"

# ---------- DESIGN 2: TEMPO 124 BPM (black tee) ----------
def d2(transparent=False):
    im=plate(INK,transparent); d=ImageDraw.Draw(im); cx=W/2
    tracked(d,cx,150*S,"FEEL THE RHYTHM",font("reg",40),WHITE,14*S)
    d.text((cx-330*S,230*S),"124",font=font("black",360),fill=WHITE)
    tracked(d,cx+250*S,560*S,"BPM",font("bold",70),GOLD,6*S,anchor_center=False)
    import random; random.seed(7); n=29; bw=20*S; gap=14*S; total=n*bw+(n-1)*gap; x=cx-total/2; midy=790*S
    for i in range(n):
        hh=40*S+int(140*S*abs(math.sin(i*0.5))*random.uniform(.5,1))
        d.rounded_rectangle([x,midy-hh,x+bw,midy+hh],radius=int(6*S),fill=GOLD if i%3 else WHITE); x+=bw+gap
    tracked(d,cx,1010*S,"THE TEMPO OF THE CITY",font("reg",30),DIM,8*S)
    paste_wm(im,WM_GOLD,cx,1160*S,340*S)
    return im,"tempo","Ink"

# ---------- DESIGN 3: COORDINATES (cream tee) ----------
def d3(transparent=False):
    im=plate(CREAM,transparent); d=ImageDraw.Draw(im); cx=W/2
    gy=int(250*S); gr=int(70*S)
    d.ellipse([cx-gr,gy-gr,cx+gr,gy+gr],outline=INK,width=int(4*S))
    d.line([cx-gr,gy,cx+gr,gy],fill=INK,width=int(3*S))            # equator
    d.line([cx,gy-gr,cx,gy+gr],fill=INK,width=int(3*S))            # central meridian
    o=int(38*S)
    d.arc([cx-o,gy-gr,cx+o,gy+gr],90,270,fill=INK,width=int(3*S))  # side meridians
    d.arc([cx-o,gy-gr,cx+o,gy+gr],-90,90,fill=INK,width=int(3*S))
    d.line([cx-gr,gy-int(26*S),cx+gr,gy-int(26*S)],fill=INK,width=int(2*S))
    d.line([cx-gr,gy+int(26*S),cx+gr,gy+int(26*S)],fill=INK,width=int(2*S))
    f=font("serif",118)
    def coord(y,a,b):
        wa=d.textlength(a,font=f); wb=d.textlength(b,font=f); tot=wa+wb
        x=cx-tot/2; d.text((x,y),a,font=f,fill=INK); d.text((x+wa,y),b,font=f,fill=GOLD_DK)
    coord(420*S,"40.7128","° N"); coord(560*S,"74.0060","° W")
    d.line([(cx-260*S,740*S),(cx+260*S,740*S)],fill=INK,width=int(2*S))
    tracked(d,cx,790*S,"NEW YORK CITY",font("serif",70),INK,10*S)
    tracked(d,cx,900*S,"ESTABLISHED 2007",font("reg",30),GOLD_DK,12*S)
    paste_wm(im,WM_BLACK,cx,1120*S,330*S)
    return im,"coordinates","Cream"

# ---------- DESIGN 4: SPIRITUAL THING manifesto (cream tee) ----------
def d4(transparent=False):
    im=plate(CREAM,transparent); d=ImageDraw.Draw(im); cx=W/2
    tracked(d,cx,210*S,"IT'S A",font("reg",48),INK,16*S)
    tracked(d,cx,290*S,"SPIRITUAL THING",font("serif",112),INK,0)
    def goldword(y,pre,gold,size):
        f=font("serif",size); wp=d.textlength(pre+" ",font=f); wg=d.textlength(gold,font=f); tot=wp+wg
        x=cx-tot/2; d.text((x,y),pre+" ",font=f,fill=INK); d.text((x+wp,y),gold,font=f,fill=GOLD_DK)
    goldword(470*S,"A","BODY THING",92); goldword(600*S,"A","SOUL THING",92)
    d.line([(cx-240*S,780*S),(cx+240*S,780*S)],fill=INK,width=int(2*S))
    tracked(d,cx,830*S,"HOUSE MUSIC SINCE 2007",font("reg",30),INK,8*S)
    paste_wm(im,WM_BLACK,cx,1120*S,330*S)
    return im,"spiritual-thing","Cream"

for fn in (d1,d2,d3,d4):
    # site plate (downscaled to 1080w, light)
    im,slug,color=fn(transparent=False)
    im=vignette(im,0.5); im=grain(im)
    im.resize((1080,1350),Image.LANCZOS).convert("RGB").save(f"{OUT_PLATE}/drop02-{slug}.jpg",quality=88)
    # transparent print file — NATIVE 3x = ~300 DPI for Printful
    pim,_,_=fn(transparent=True)
    pim.save(f"{OUT_PRINT}/drop02-{slug}-back.png")
    dpi = round(pim.size[0]/11, 0)
    print(f"wrote {slug}: print {pim.size[0]}x{pim.size[1]}px (~{int(dpi)} DPI @ 11in) + 1080 plate")
print("DROP 02 — native 300 DPI prints done")
