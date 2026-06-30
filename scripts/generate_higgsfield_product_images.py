#!/usr/bin/env python3
"""Generate high-quality FlyLyfe product images in Higgsfield only.

Method:
- No local compositing for final images.
- Build a reference board per output: style/model reference(s) + exact print art.
- Ask Higgsfield GPT Image 2 to generate the final realistic model-worn image.
- Save outputs under assets/higgsfield-product-images and a manifest JSON.
"""
from __future__ import annotations

import json, subprocess, time, urllib.request, sys, os
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path('/Users/teddy/flylyfe-site')
PRINT = ROOT/'assets/print'
BASE = ROOT/'assets/generated-model-bases/higgsfield'
EXISTING = ROOT/'assets/products'
OUT = ROOT/'assets/higgsfield-product-images'
REFS = OUT/'reference-boards'
OUT.mkdir(parents=True, exist_ok=True)
REFS.mkdir(parents=True, exist_ok=True)

PRODUCTS = {
  'the-anthem-tee':              {'gender':'male','colors':['Black','White','Ivory'],'design':'anthem','title':'The Anthem Tee'},
  'the-conga-tee':               {'gender':'male','colors':['Black','White','Ivory'],'design':'conga','title':'The Conga Tee'},
  'the-signature-tee':           {'gender':'male','colors':['Black','White','Ivory'],'design':'signature','title':'The Signature Tee'},
  'the-house-music-tee':         {'gender':'male','colors':['Black','White','Ivory'],'design':'housemusic','title':'The House Music Tee'},
  'the-token-tee':               {'gender':'male','colors':['Black','White','Ivory'],'design':'token','title':'The Token Tee'},
  'the-after-hours-tee':         {'gender':'male','colors':['Black'],'design':'afterhours','title':'The After Hours Tee'},
  'the-tempo-tee':               {'gender':'male','colors':['Black'],'design':'tempo','title':'The Tempo Tee'},
  'the-coordinates-tee':         {'gender':'male','colors':['Ivory'],'design':'coordinates','title':'The Coordinates Tee'},
  'the-spiritual-thing-tee':     {'gender':'male','colors':['Ivory'],'design':'spiritual','title':'The Spiritual Thing Tee'},
  'the-sanitary-code-tee':       {'gender':'male','colors':['White'],'design':'sanitary','title':'The Sanitary Code Tee'},
  'the-anthem-tee-womens':       {'gender':'wren','colors':['Black','White','Natural'],'design':'anthem','title':"The Anthem Tee — Women's"},
  'the-conga-tee-womens':        {'gender':'wren','colors':['Black','White','Natural'],'design':'conga','title':"The Conga Tee — Women's"},
  'the-signature-tee-womens':    {'gender':'wren','colors':['Black','White','Natural'],'design':'signature','title':"The Signature Tee — Women's"},
}

def ink(color:str, dark_file:str, light_file:str):
    return light_file if color == 'Black' else dark_file

def print_for(design:str, color:str, view:str):
    # Use exact production print files as reference art. For back-graphic shirts, front = small chest wordmark.
    if design == 'anthem':
        return ink(color,'flylyfe-wordmark-only-BLACK.png','flylyfe-wordmark-only-WHITE.png') if view=='front' else ink(color,'flylyfe-feel-music-stack-BLACK-INK-for-light-shirts-transparent.png','flylyfe-feel-music-stack-transparent-print.png')
    if design == 'conga':
        return ink(color,'flylyfe-wordmark-only-BLACK.png','flylyfe-wordmark-only-WHITE.png') if view=='front' else ink(color,'flylyfe-music-dancer-conga-transparent-print.png','flylyfe-music-dancer-conga-WHITE-INK-for-dark-shirts-transparent.png')
    if design == 'signature':
        return ink(color,'flylyfe-logo-tagline-wide-BLACK-INK-for-light-shirts-transparent.png','flylyfe-logo-tagline-wide-transparent-print.png') if view=='front' else None
    if design == 'housemusic':
        return ink(color,'flylyfe-housemusic-front-dark-for-light-shirts.png','flylyfe-housemusic-front-light-for-dark-shirts.png') if view=='front' else ink(color,'flylyfe-housemusic-back-dark-for-light-shirts.png','flylyfe-housemusic-back-light-for-dark-shirts.png')
    if design == 'token':
        return ink(color,'flylyfe-token-front-dark.png','flylyfe-token-front-light.png') if view=='front' else 'flylyfe-token-back.png'
    if design == 'afterhours':
        return ink(color,'flylyfe-wordmark-only-BLACK.png','flylyfe-wordmark-only-WHITE.png') if view=='front' else 'drop02-after-hours-back.png'
    if design == 'tempo':
        return ink(color,'flylyfe-wordmark-only-BLACK.png','flylyfe-wordmark-only-WHITE.png') if view=='front' else 'drop02-tempo-back.png'
    if design == 'coordinates':
        return ink(color,'flylyfe-wordmark-only-BLACK.png','flylyfe-wordmark-only-WHITE.png') if view=='front' else 'drop02-coordinates-back.png'
    if design == 'spiritual':
        return ink(color,'flylyfe-wordmark-only-BLACK.png','flylyfe-wordmark-only-WHITE.png') if view=='front' else 'drop02-spiritual-thing-back.png'
    if design == 'sanitary':
        return 'limited-sanitary-print.png' if view=='front' else 'limited-sanitary-back.png'
    raise ValueError(design)

def expected_text(design:str, view:str):
    if view == 'front' and design not in ('housemusic','token','sanitary','signature'):
        return 'small FLYLYFE chest wordmark only'
    return {
      'anthem':'FEEL THE MUSIC / FEEL THE VIBE / LIVE YOUR LYFE plus FLYLYFE branding',
      'conga':'FLYLYFE dancer/conga artwork exactly as reference',
      'signature':'FLYLYFE logo/tagline exactly as reference' if view=='front' else 'blank back with no print',
      'housemusic':'front: NOT EVERYONE UNDERSTANDS HOUSE MUSIC / back: house music manifesto exactly as reference',
      'token':'front token wordmark / back NYC subway token exactly as reference',
      'afterhours':'AFTER HOURS; 01 MIDNIGHT; 02 THE BASEMENT; 03 SUNRISE SET; 04 LAST TRAIN HOME; FLYLYFE; NEW YORK CITY · EST. 2007',
      'tempo':'124 BPM tempo/waveform design exactly as reference',
      'coordinates':'40.7128° N; 74.0060° W; NEW YORK CITY; ESTABLISHED 2007; FLYLYFE exactly as reference',
      'spiritual':'IT’S A SPIRITUAL THING; A BODY THING; A SOUL THING; HOUSE MUSIC SINCE 2007 exactly as reference',
      'sanitary':'NO SMOKING / NO SPITTING / Sanitary Code design exactly as reference',
    }[design]

def color_desc(color:str, gender:str):
    if color == 'Black': return 'black'
    if color == 'White': return 'white'
    if color == 'Ivory': return 'warm ivory / cream'
    if color == 'Natural': return 'warm natural cream'
    return color.lower()

def base_path(gender:str, color:str, view:str):
    return BASE/f'{gender}-{color.lower()}-{view}-base.png'

def style_candidates(handle:str, color:str, view:str):
    # Prefer approved existing style/product photos when present; then base.
    names=[]
    if handle == 'the-after-hours-tee' and view=='back': names.append('drop02-after-hours-model.jpg')
    if handle == 'the-tempo-tee' and view=='back': names.append('drop02-tempo-model.jpg')
    if handle == 'the-coordinates-tee' and view=='back': names.append('drop02-coordinates-model.jpg')
    if handle == 'the-spiritual-thing-tee' and view=='back': names.append('drop02-spiritual-thing-model.jpg')
    if handle == 'the-conga-tee' and color=='Black' and view=='back': names.append('the-conga-tee-model-back.jpg')
    if handle == 'the-signature-tee' and color=='Black' and view=='back': names.append('the-signature-tee-model-back.jpg')
    if handle == 'the-token-tee' and color=='Ivory': names.append(f'the-token-tee-model-{view}.jpg')
    if handle == 'the-sanitary-code-tee': names.append('limited-sanitary-front-model.jpg' if view=='front' else 'limited-sanitary-back.jpg')
    names.append(f'{handle}-{color}-{view}.jpg')
    names.append(f'generated/{handle}-{color}-{view}-matched-mockup.jpg')
    return [EXISTING/n for n in names if (EXISTING/n).exists()]

def paste_fit(board, im, box):
    x,y,w,h=box
    im=im.copy()
    im.thumbnail((w,h))
    board.paste(im,(x+(w-im.width)//2,y+(h-im.height)//2))

def make_board(handle, cfg, color, view):
    gender=cfg['gender']; design=cfg['design']
    bpath=base_path(gender,color,view)
    if not bpath.exists():
        raise FileNotFoundError(bpath)
    art_name=print_for(design,color,view)
    art_path=PRINT/art_name if art_name else None
    board=Image.new('RGB',(2200,1200),(15,15,15))
    d=ImageDraw.Draw(board)
    x=40
    styles=style_candidates(handle,color,view)[:1]
    if styles:
        im=Image.open(styles[0]).convert('RGB')
        d.text((x,35),'STYLE REF: realistic product/photo feel',fill=(255,255,255)); paste_fit(board,im,(x,90,500,1000)); x+=540
    im=Image.open(bpath).convert('RGB')
    d.text((x,35),'MODEL REF: identity / pose / view / garment fit',fill=(255,255,255)); paste_fit(board,im,(x,90,500,1000)); x+=540
    if art_path:
        art=Image.open(art_path).convert('RGBA')
        bbox=art.getbbox(); art=art.crop(bbox) if bbox else art
        bg_color=(4,4,4,255) if color=='Black' else (242,238,226,255)
        art_bg=Image.new('RGBA',(740,1000),bg_color)
        art.thumbnail((650,850))
        art_bg.alpha_composite(art,((740-art.width)//2,(1000-art.height)//2))
        d.text((x,35),'EXACT PRINT ART — copy text/layout/colors',fill=(255,255,255)); board.paste(art_bg.convert('RGB'),(x,90)); x+=780
    else:
        d.text((x,35),'NO BACK PRINT — generate blank shirt back only',fill=(255,255,255))
    d.text((40,1135),f'{handle} | {color} | {view} | {cfg["title"]}',fill=(255,255,255))
    out=REFS/f'{handle}-{color}-{view}-reference-board.jpg'
    board.save(out,quality=96)
    return out

def prompt(handle,cfg,color,view,has_art):
    gender=cfg['gender']; design=cfg['design']
    person = 'same curly-haired male streetwear model' if gender=='male' else 'same Wren Blake female streetwear model persona, long dark wavy hair'
    garment = 'oversized heavyweight tee' if gender=='male' else "women's relaxed tee"
    desc=color_desc(color,gender)
    exp=expected_text(design,view)
    base = f"QUALITY CRITICAL FLYLYFE ecommerce product photograph. Use the reference board carefully: style reference (if present) = realism and fabric/print integration; model reference = exact person identity, pose, view, garment fit, and camera angle; print-art reference = exact design to reproduce. Generate a photorealistic premium streetwear lookbook image of the {person}, {view} view, wearing a {desc} {garment}, downtown NYC urban background, commercial ecommerce quality, 3:4 vertical. "
    if has_art:
        base += f"The shirt print must match the print-art reference exactly. Expected design/text: {exp}. Preserve exact spelling, line order, number order, logo, colors, scale, placement, and proportions. Do not invent text, do not omit words, do not duplicate words, do not change FLYLYFE to FLYLIFE, and do not use gibberish letters. "
        base += "The print must look like real screen-printed ink absorbed into cotton: fabric grain visible through ink, natural slight distortion from folds and body curvature, realistic edge softness, shadows and folds passing through the ink, NOT a flat pasted sticker. "
    else:
        base += "This is a blank back view: no print, no logo, no text, no graphics on the shirt back. "
    base += "Keep the model realistic with correct anatomy and hands, no extra fingers, no broken limbs, no readable background signage, no watermarks, sharp high-end Kith / Aimé Leon Dore / Stüssy editorial streetwear vibe."
    return base

def run(cmd, **kw):
    return subprocess.run(cmd, text=True, capture_output=True, **kw)

def create_job(board, prompt_text):
    cmd=['higgsfield','generate','create','gpt_image_2','--prompt',prompt_text,'--aspect_ratio','3:4','--quality','high','--resolution','2k','--image',str(board),'--json']
    r=run(cmd)
    if r.returncode:
        raise RuntimeError((r.stderr or r.stdout)[:1000])
    j=json.loads(r.stdout)
    return j[0] if isinstance(j,list) else j

def get_job(jid):
    r=run(['higgsfield','generate','get',jid,'--json'])
    if r.returncode:
        return {'id':jid,'status':'unknown','error':r.stderr or r.stdout}
    return json.loads(r.stdout)

def download(url,out):
    out.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url,out)


def main():
    os.environ['PATH']='/Users/teddy/.hermes/node/bin:'+os.environ.get('PATH','')
    manifest={}
    jobs=[]
    # Reuse the already-good after-hours test3 as final to avoid wasting a duplicate credit.
    test3=OUT/'the-after-hours-tee/the-after-hours-tee-Black-back-higgsfield-gpt-image-2-test3.png'
    final_after=OUT/'the-after-hours-tee/the-after-hours-tee-Black-back-higgsfield.png'
    if test3.exists() and not final_after.exists():
        final_after.parent.mkdir(parents=True,exist_ok=True)
        final_after.write_bytes(test3.read_bytes())
    for handle,cfg in PRODUCTS.items():
        manifest.setdefault(handle,{})
        for color in cfg['colors']:
            manifest[handle].setdefault(color,{})
            for view in ['front','back']:
                out=OUT/handle/f'{handle}-{color}-{view}-higgsfield.png'
                if out.exists():
                    manifest[handle][color][view]=str(out.relative_to(ROOT))
                    print('SKIP existing', out.relative_to(ROOT), flush=True)
                    continue
                art_name=print_for(cfg['design'],color,view)
                board=make_board(handle,cfg,color,view)
                ptxt=prompt(handle,cfg,color,view,art_name is not None)
                print('CREATE',handle,color,view, flush=True)
                try:
                    job=create_job(board,ptxt)
                    jobs.append({'id':job['id'],'handle':handle,'color':color,'view':view,'out':str(out),'board':str(board)})
                    print('JOB',job['id'],handle,color,view, flush=True)
                    time.sleep(2)
                except Exception as e:
                    print('CREATE_FAIL',handle,color,view,str(e), flush=True)
    (OUT/'higgsfield_jobs_pending.json').write_text(json.dumps(jobs,indent=2))
    print('CREATED_JOBS',len(jobs), flush=True)
    pending=jobs[:]
    completed=[]; failed=[]
    while pending:
        nxt=[]
        for j in pending:
            info=get_job(j['id'])
            st=info.get('status')
            if st=='completed' and info.get('result_url'):
                try:
                    download(info['result_url'],Path(j['out']))
                    rel=str(Path(j['out']).relative_to(ROOT))
                    manifest.setdefault(j['handle'],{}).setdefault(j['color'],{})[j['view']]=rel
                    completed.append({**j,'url':info['result_url']})
                    print('DONE',rel, flush=True)
                except Exception as e:
                    failed.append({**j,'error':'download '+str(e)})
                    print('DOWNLOAD_FAIL',j,str(e), flush=True)
            elif st=='failed':
                failed.append({**j,'error':'job failed'})
                print('FAILED',j['id'],j['handle'],j['color'],j['view'], flush=True)
            else:
                nxt.append(j)
        pending=nxt
        (OUT/'higgsfield_manifest.json').write_text(json.dumps(manifest,indent=2))
        (OUT/'higgsfield_jobs_completed.json').write_text(json.dumps(completed,indent=2))
        (OUT/'higgsfield_jobs_failed.json').write_text(json.dumps(failed,indent=2))
        if pending:
            print('PENDING',len(pending),'COMPLETED',len(completed),'FAILED',len(failed), flush=True)
            time.sleep(15)
    print('ALL_DONE completed',len(completed),'failed',len(failed), flush=True)
    (OUT/'higgsfield_manifest.json').write_text(json.dumps(manifest,indent=2))

if __name__=='__main__':
    main()
