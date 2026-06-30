#!/usr/bin/env python3
"""Regenerate flagged FlyLyfe Higgsfield images with stricter logo/text instructions."""
from pathlib import Path
import json, subprocess, os, time, urllib.request, sys
ROOT=Path('/Users/teddy/flylyfe-site')
sys.path.insert(0,str(ROOT/'scripts'))
import generate_higgsfield_product_images as gen
OUT=gen.OUT
MAX_ACTIVE=8

FLAGGED=[
 ('the-anthem-tee','Black','front'),('the-anthem-tee','Black','back'),('the-anthem-tee','Ivory','back'),('the-anthem-tee','White','back'),
 ('the-anthem-tee-womens','Black','back'),('the-anthem-tee-womens','Natural','back'),('the-anthem-tee-womens','White','back'),
 ('the-conga-tee','Black','back'),('the-conga-tee','Ivory','back'),('the-conga-tee','White','back'),
 ('the-house-music-tee','Black','front'),('the-house-music-tee','Ivory','front'),('the-house-music-tee','White','front'),
 ('the-signature-tee','White','front'),('the-signature-tee-womens','Natural','front'),
 ('the-tempo-tee','Black','front'),('the-token-tee','Black','front'),('the-token-tee','White','front'),
]

def prompt(handle,cfg,color,view,has_art):
    p=gen.prompt(handle,cfg,color,view,has_art)
    strict="""
ABSOLUTE LOGO/TEXT QUALITY OVERRIDE: the brand word must read exactly FLYLYFE, seven letters: F L Y L Y F E. The two Y letters must be real Y letters, never V, never I, never L, never abstract marks. Do not render FLYLIFE, FLYLVFE, FLVLYFE, ELYLYFE, CLVLUCE, or any gibberish. If the design includes a small chest logo, make it clean and slightly larger/closer so FLYLYFE is readable and correctly spelled. For slogan shirts, the bottom/hem brand mark must also be exact FLYLYFE or omitted only if the reference shows no mark; never hallucinate a fake word. Treat the print reference as a product artwork proof, not inspiration. Exact typography fidelity matters more than creative variation.
"""
    return p + strict

def parse_create(stdout):
    j=json.loads(stdout)
    if isinstance(j,str): return j
    if isinstance(j,list):
        first=j[0]
        return first if isinstance(first,str) else first.get('id')
    return j.get('id')

def create(t):
    handle,color,view=t
    cfg=gen.PRODUCTS[handle]
    art=gen.print_for(cfg['design'],color,view)
    board=gen.make_board(handle,cfg,color,view)
    ptxt=prompt(handle,cfg,color,view,art is not None)
    cmd=['higgsfield','generate','create','gpt_image_2','--prompt',ptxt,'--aspect_ratio','3:4','--quality','high','--resolution','2k','--image',str(board),'--json']
    r=subprocess.run(cmd,capture_output=True,text=True)
    if r.returncode: raise RuntimeError((r.stderr or r.stdout)[:1000])
    return parse_create(r.stdout)

def get(jid):
    r=subprocess.run(['higgsfield','generate','get',jid,'--json'],capture_output=True,text=True)
    if r.returncode: return {'id':jid,'status':'unknown','error':r.stderr or r.stdout}
    return json.loads(r.stdout)

def main():
    os.environ['PATH']='/Users/teddy/.hermes/node/bin:'+os.environ.get('PATH','')
    tasks=FLAGGED[:]
    active=[]; done=[]; failed=[]
    print('FLAGGED',len(tasks),flush=True)
    while tasks or active:
        still=[]
        for a in active:
            info=get(a['id']); st=info.get('status')
            if st=='completed' and info.get('result_url'):
                handle,color,view=a['task']
                out=OUT/handle/f'{handle}-{color}-{view}-higgsfield.png'
                backup=OUT/handle/f'{handle}-{color}-{view}-higgsfield-pre-regen.png'
                if out.exists() and not backup.exists(): backup.write_bytes(out.read_bytes())
                urllib.request.urlretrieve(info['result_url'],out)
                done.append({**a,'url':info['result_url'],'out':str(out.relative_to(ROOT))})
                print('REGEN_DONE',out.relative_to(ROOT),a['id'],flush=True)
            elif st=='failed':
                failed.append(a); print('REGEN_FAILED',a,flush=True)
            else:
                still.append(a)
        active=still
        while tasks and len(active)<MAX_ACTIVE:
            t=tasks.pop(0)
            try:
                print('REGEN_SUBMIT',t,flush=True)
                jid=create(t)
                active.append({'task':t,'id':jid})
                print('REGEN_JOB',jid,t,flush=True)
                time.sleep(3)
            except Exception as e:
                msg=str(e); print('REGEN_SUBMIT_FAIL',t,msg,flush=True)
                if 'rate_limit' in msg or '503' in msg or 'concurrent_jobs_limit' in msg:
                    tasks.insert(0,t); time.sleep(30); break
                failed.append({'task':t,'error':msg})
        (OUT/'higgsfield_regen_flagged_state.json').write_text(json.dumps({'active':active,'done':done,'failed':failed,'remaining':tasks},indent=2))
        print('REGEN_STATUS active',len(active),'remaining',len(tasks),'done',len(done),'failed',len(failed),flush=True)
        if active: time.sleep(20)
    print('REGEN_ALL_DONE',len(done),'failed',len(failed),flush=True)

if __name__=='__main__': main()
