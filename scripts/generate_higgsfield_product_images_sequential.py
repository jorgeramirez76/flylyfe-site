#!/usr/bin/env python3
"""Sequential/resumable Higgsfield GPT Image 2 product generation for FlyLyfe.
Respects Higgsfield concurrency limits by waiting for each image before creating the next.
"""
from pathlib import Path
import json, subprocess, os, time, urllib.request, sys

ROOT=Path('/Users/teddy/flylyfe-site')
sys.path.insert(0,str(ROOT/'scripts'))
import generate_higgsfield_product_images as gen

OUT=gen.OUT

def parse_wait_output(txt):
    j=json.loads(txt)
    if isinstance(j,list):
        item=j[0]
    else:
        item=j
    if isinstance(item,str):
        # Some create calls return just ids unless --wait shape changes; fetch it.
        r=subprocess.run(['higgsfield','generate','get',item,'--json'],capture_output=True,text=True)
        if r.returncode: raise RuntimeError(r.stderr or r.stdout)
        item=json.loads(r.stdout)
    return item

def generate_one(handle,cfg,color,view,max_attempts=3):
    out=OUT/handle/f'{handle}-{color}-{view}-higgsfield.png'
    if out.exists():
        print('SKIP',out.relative_to(ROOT),flush=True)
        return {'status':'skipped','out':str(out.relative_to(ROOT))}
    art_name=gen.print_for(cfg['design'],color,view)
    board=gen.make_board(handle,cfg,color,view)
    ptxt=gen.prompt(handle,cfg,color,view,art_name is not None)
    cmd=['higgsfield','generate','create','gpt_image_2','--prompt',ptxt,'--aspect_ratio','3:4','--quality','high','--resolution','2k','--image',str(board),'--wait','--wait-timeout','18m','--wait-interval','8s','--json']
    last=''
    for attempt in range(1,max_attempts+1):
        print('GENERATE',attempt,handle,color,view,flush=True)
        r=subprocess.run(cmd,capture_output=True,text=True)
        if r.returncode==0:
            try:
                item=parse_wait_output(r.stdout)
                if item.get('status')=='completed' and item.get('result_url'):
                    out.parent.mkdir(parents=True,exist_ok=True)
                    urllib.request.urlretrieve(item['result_url'],out)
                    print('DONE',out.relative_to(ROOT),item.get('id'),flush=True)
                    return {'status':'completed','id':item.get('id'),'url':item['result_url'],'out':str(out.relative_to(ROOT))}
                last='unexpected status '+json.dumps(item)[:500]
            except Exception as e:
                last='parse/download '+str(e)+' stdout='+r.stdout[:500]
        else:
            last=(r.stderr or r.stdout)[:800]
        print('FAIL_ATTEMPT',attempt,handle,color,view,last,flush=True)
        time.sleep(20*attempt)
    return {'status':'failed','error':last}

def main():
    os.environ['PATH']='/Users/teddy/.hermes/node/bin:'+os.environ.get('PATH','')
    manifest={}
    results=[]
    # Ensure the approved after-hours test becomes the final file.
    test3=OUT/'the-after-hours-tee/the-after-hours-tee-Black-back-higgsfield-gpt-image-2-test3.png'
    final=OUT/'the-after-hours-tee/the-after-hours-tee-Black-back-higgsfield.png'
    if test3.exists() and not final.exists():
        final.parent.mkdir(parents=True,exist_ok=True); final.write_bytes(test3.read_bytes())
    for handle,cfg in gen.PRODUCTS.items():
        manifest.setdefault(handle,{})
        for color in cfg['colors']:
            manifest[handle].setdefault(color,{})
            for view in ['front','back']:
                res=generate_one(handle,cfg,color,view)
                res.update({'handle':handle,'color':color,'view':view})
                results.append(res)
                out=OUT/handle/f'{handle}-{color}-{view}-higgsfield.png'
                if out.exists():
                    manifest[handle][color][view]=str(out.relative_to(ROOT))
                (OUT/'higgsfield_generation_results.json').write_text(json.dumps(results,indent=2))
                (OUT/'higgsfield_manifest.json').write_text(json.dumps(manifest,indent=2))
    print('SUMMARY total',len(results),'completed/skipped',sum(1 for r in results if r['status'] in ('completed','skipped')),'failed',sum(1 for r in results if r['status']=='failed'),flush=True)

if __name__=='__main__': main()
