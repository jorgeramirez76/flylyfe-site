#!/usr/bin/env python3
"""FLYLYFE — DROP 02 design generator (local, free, exact typography via Pillow).
Renders 4 new on-brand back-print designs as premium 4:5 'plates' on the tee color
(for the site product display) + transparent white/ink print PNGs (for Printful later).
No AI, no external accounts."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, math

OUT_PLATE = "assets/products"
OUT_PRINT = "assets/print"
os.makedirs(OUT_PLATE, exist_ok=True)

# palette
GOLD=(242,201,76); INK=(28,28,30); CREAM=(241,232,210); WHITE=(245,242,234); DIM=(150,150,150)
F = "/System/Library/Fonts/Supplemental/"
def font(name, size):
    paths={"black":F+"Arial Bold.ttf","bold":F+"Arial Bold.ttf","reg":F+"Arial.ttf",
           "serif":F+"Georgia.ttf","serifb":F+"Georgia Bold.ttf","times":F+"Times New Roman.ttf"}
    p=paths.get(name,paths["reg"])
    if not os.path.exists(p): p=F+"Arial.ttf"
    return ImageFont.truetype(p, size)

WM_GOLD=Image.open(OUT_PRINT+"/flylyfe-wordmark-gold.png").convert("RGBA")
WM_WHITE=Image.open(OUT_PRINT+"/flylyfe-wordmark-only-WHITE.png").convert("RGBA")
WM_BLACK=Image.open(OUT_PRINT+"/flylyfe-wordmark-only-BLACK.png").convert("RGBA")

def tracked(draw, cx, y, txt, fnt, fill, ls=0, anchor_center=True):
    """draw letter-spaced text; returns width. centered on cx if anchor_center."""
    widths=[draw.textlength(c, font=fnt) for c in txt]
    total=sum(widths)+ls*(len(txt)-1)
    x = cx-total/2 if anchor_center else cx
    for c,w in zip(txt,widths):
        draw.text((x,y), c, font=fnt, fill=fill); x+=w+ls
    return total

def paste_wm(base, wm, cx, y, w):
    h=int(wm.height*(w/wm.width)); r=wm.resize((w,h), Image.LANCZOS)
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

W,Hh=1080,1350
def plate(bg, transparent=False):
    return Image.new("RGBA",(W,Hh),(0,0,0,0)) if transparent else Image.new("RGBA",(W,Hh),bg+(255,))

# ---------- DESIGN 1: AFTER HOURS (black tee) ----------
def d1(transparent=False):
    im=plate(INK,transparent); d=ImageDraw.Draw(im); cx=W/2
    tracked(d,cx,150,"AFTER",font("black",200),WHITE,4)
    tracked(d,cx,350,"HOURS",font("black",200),WHITE,4)
    d.line([(cx-300,610),(cx+300,610)],fill=GOLD,width=3)
    rows=[("01","MIDNIGHT"),("02","THE BASEMENT"),("03","SUNRISE SET"),("04","LAST TRAIN HOME")]
    fy=700; fn=font("bold",46); fr=font("reg",46)
    for num,title in rows:
        d.text((cx-330,fy),num,font=fn,fill=GOLD)
        d.text((cx-220,fy),title,font=fr,fill=WHITE); fy+=78
    paste_wm(im,WM_GOLD,cx,1130,360)
    tracked(d,cx,1230,"NEW YORK CITY  ·  EST. 2007",font("reg",26),DIM,8)
    return im,"after-hours","Ink"

# ---------- DESIGN 2: TEMPO 124 BPM (black tee) ----------
def d2(transparent=False):
    im=plate(INK,transparent); d=ImageDraw.Draw(im); cx=W/2
    tracked(d,cx,150,"FEEL THE RHYTHM",font("reg",40),WHITE,14)
    d.text((cx-330,230),"124",font=font("black",360),fill=WHITE)
    tracked(d,cx+250,560,"BPM",font("bold",70),GOLD,6,anchor_center=False)
    # waveform bars
    import random; random.seed(7); n=29; bw=20; gap=14; total=n*bw+(n-1)*gap; x=cx-total/2; midy=790
    for i in range(n):
        hh=40+int(140*abs(math.sin(i*0.5))*random.uniform(.5,1))
        d.rounded_rectangle([x,midy-hh,x+bw,midy+hh],radius=6,fill=GOLD if i%3 else WHITE); x+=bw+gap
    tracked(d,cx,1010,"THE TEMPO OF THE CITY",font("reg",30),DIM,8)
    paste_wm(im,WM_GOLD,cx,1160,340)
    return im,"tempo","Ink"

# ---------- DESIGN 3: COORDINATES (cream tee) ----------
def d3(transparent=False):
    im=plate(CREAM,transparent); d=ImageDraw.Draw(im); cx=W/2
    # globe
    gy=250; gr=70
    d.ellipse([cx-gr,gy-gr,cx+gr,gy+gr],outline=INK,width=4)
    d.line([cx-gr,gy,cx+gr,gy],fill=INK,width=3)
    for off in (-38,0,38): d.arc([cx-abs(off if off else gr),gy-gr,cx+abs(off if off else gr),gy+gr],90,270 if off<0 else -90,fill=INK,width=3) if off else d.line([cx,gy-gr,cx,gy+gr],fill=INK,width=3)
    d.line([cx-gr,gy-26,cx+gr,gy-26],fill=INK,width=2); d.line([cx-gr,gy+26,cx+gr,gy+26],fill=INK,width=2)
    f=font("serif",118)
    def coord(y,a,b):
        wa=d.textlength(a,font=f); wb=d.textlength(b,font=f); tot=wa+wb
        x=cx-tot/2; d.text((x,y),a,font=f,fill=INK); d.text((x+wa,y),b,font=f,fill=(176,140,40))
    coord(420,"40.7128","° N"); coord(560,"74.0060","° W")
    d.line([(cx-260,740),(cx+260,740)],fill=INK,width=2)
    tracked(d,cx,790,"NEW YORK CITY",font("serif",70),INK,10)
    tracked(d,cx,900,"ESTABLISHED 2007",font("reg",30),(176,140,40),12)
    paste_wm(im,WM_BLACK,cx,1120,330)
    return im,"coordinates","Cream"

# ---------- DESIGN 4: SPIRITUAL THING manifesto (cream tee) ----------
def d4(transparent=False):
    im=plate(CREAM,transparent); d=ImageDraw.Draw(im); cx=W/2
    tracked(d,cx,210,"IT'S A",font("reg",48),INK,16)
    tracked(d,cx,290,"SPIRITUAL THING",font("serif",112),INK,0)
    def goldword(y,pre,gold,size):
        f=font("serif",size); wp=d.textlength(pre+" ",font=f); wg=d.textlength(gold,font=f); tot=wp+wg
        x=cx-tot/2; d.text((x,y),pre+" ",font=f,fill=INK); d.text((x+wp,y),gold,font=f,fill=(176,140,40))
    goldword(470,"A","BODY THING",92); goldword(600,"A","SOUL THING",92)
    d.line([(cx-240,780),(cx+240,780)],fill=INK,width=2)
    tracked(d,cx,830,"HOUSE MUSIC SINCE 2007",font("reg",30),INK,8)
    paste_wm(im,WM_BLACK,cx,1120,330)
    return im,"spiritual-thing","Cream"

for fn in (d1,d2,d3,d4):
    # site plate (design on tee-color background)
    im,slug,color=fn(transparent=False)
    im=vignette(im,0.5); im=grain(im)
    im.convert("RGB").save(f"{OUT_PLATE}/drop02-{slug}.jpg",quality=88)
    # transparent print file for Printful (upscaled to ~1800w = ~150dpi on a 12in back placement)
    pim,_,_=fn(transparent=True)
    pim=pim.resize((1800,int(Hh*1800/W)),Image.LANCZOS)
    pim.save(f"{OUT_PRINT}/drop02-{slug}-back.png")
    print("wrote plate + print:",slug,f"({color} ink)")
print("DROP 02 plates + transparent prints done")
