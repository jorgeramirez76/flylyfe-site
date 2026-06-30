#!/usr/bin/env python3
"""8-at-a-time resumable Higgsfield GPT Image 2 runner for FlyLyfe product images."""
from pathlib import Path
import json, subprocess, os, time, urllib.request, sys

ROOT=Path('/Users/teddy/flylyfe-site')
sys.path.insert(0,str(ROOT/'scripts'))
import generate_higgsfield_product_images as gen
OUT=gen.OUT
MAX_ACTIVE=8
STATE=OUT/'higgsfield_throttled_state.json'


def all_tasks():
    tasks=[]
    for handle,cfg in gen.PRODUCTS.items():
        for color in cfg['colors']:
            for view in ['front','back']:
                out=OUT/handle/f'{handle}-{color}-{view}-higgsfield.png'
                tasks.append({'handle':handle,'cfg':cfg,'color':color,'view':view,'out':str(out)})
    return tasks

def parse_create(stdout):
    j=json.loads(stdout)
    if isinstance(j,str): return j
    if isinstance(j,list):
        first=j[0]
        return first if isinstance(first,str) else first.get('id')
    return j.get('id')

def create_job(t):
    handle,cfg,color,view=t['handle'],t['cfg'],t['color'],t['view']
    art_name=gen.print_for(cfg['design'],color,view)
    board=gen.make_board(handle,cfg,color,view)
    ptxt=gen.prompt(handle,cfg,color,view,art_name is not None)
    cmd=['higgsfield','generate','create','gpt_image_2','--prompt',ptxt,'--aspect_ratio','3:4','--quality','high','--resolution','2k','--image',str(board),'--json']
    r=subprocess.run(cmd,capture_output=True,text=True)
    if r.returncode:
        raise RuntimeError((r.stderr or r.stdout)[:1000])
    jid=parse_create(r.stdout)
    if not jid: raise RuntimeError('no id in '+r.stdout[:500])
    return jid

def get_job(jid):
    r=subprocess.run(['higgsfield','generate','get',jid,'--json'],capture_output=True,text=True)
    if r.returncode:
        return {'id':jid,'status':'unknown','error':r.stderr or r.stdout}
    return json.loads(r.stdout)

def save_state(active,completed,failed):
    clean_active=[]
    for a in active:
        b={k:v for k,v in a.items() if k!='cfg'}
        clean_active.append(b)
    STATE.write_text(json.dumps({'active':clean_active,'completed':completed,'failed':failed},indent=2))

def load_state():
    if not STATE.exists(): return [],[],[]
    s=json.loads(STATE.read_text())
    return s.get('active',[]),s.get('completed',[]),s.get('failed',[])

def rel(p): return str(Path(p).relative_to(ROOT))

def main():
    os.environ['PATH']='/Users/teddy/.hermes/node/bin:'+os.environ.get('PATH','')
    active,completed,failed=load_state()
    # Rehydrate cfg into active tasks if resuming.
    by_handle=gen.PRODUCTS
    for a in active:
        a['cfg']=by_handle[a['handle']]
    tasks=[]
    for t in all_tasks():
        out=Path(t['out'])
        if out.exists():
            continue
        # don't duplicate active saved in state
        if any(a['handle']==t['handle'] and a['color']==t['color'] and a['view']==t['view'] for a in active):
            continue
        tasks.append(t)
    print('START existing_files',sum(1 for t in all_tasks() if Path(t['out']).exists()),'to_create',len(tasks),'active',len(active),flush=True)
    while tasks or active:
        # Poll active first
        still=[]
        for a in active:
            info=get_job(a['id'])
            st=info.get('status')
            if st=='completed' and info.get('result_url'):
                out=Path(a['out']); out.parent.mkdir(parents=True,exist_ok=True)
                urllib.request.urlretrieve(info['result_url'],out)
                row={k:v for k,v in a.items() if k!='cfg'}; row.update({'status':'completed','url':info['result_url']})
                completed.append(row)
                print('DONE',rel(out),a['id'],flush=True)
            elif st=='failed':
                row={k:v for k,v in a.items() if k!='cfg'}; row.update({'status':'failed'})
                failed.append(row)
                print('REMOTE_FAILED',a['id'],a['handle'],a['color'],a['view'],flush=True)
            else:
                still.append(a)
        active=still
        # Submit until full
        while tasks and len(active)<MAX_ACTIVE:
            t=tasks.pop(0)
            try:
                print('SUBMIT',t['handle'],t['color'],t['view'],flush=True)
                jid=create_job(t)
                t['id']=jid
                active.append(t)
                print('JOB',jid,t['handle'],t['color'],t['view'],flush=True)
                time.sleep(3)
            except Exception as e:
                msg=str(e)
                print('SUBMIT_FAIL',t['handle'],t['color'],t['view'],msg,flush=True)
                # rate limit / transient: put it back and wait
                if 'rate_limit' in msg or '503' in msg or 'concurrent_jobs_limit' in msg:
                    tasks.insert(0,t)
                    time.sleep(30)
                    break
                else:
                    fail={k:v for k,v in t.items() if k!='cfg'}; fail.update({'status':'submit_failed','error':msg})
                    failed.append(fail)
        save_state(active,completed,failed)
        print('STATUS active',len(active),'remaining',len(tasks),'completed',len(completed),'failed',len(failed),'files',sum(1 for t in all_tasks() if Path(t['out']).exists()),flush=True)
        if active:
            time.sleep(20)
    # manifest
    manifest={}
    for t in all_tasks():
        out=Path(t['out'])
        if out.exists():
            manifest.setdefault(t['handle'],{}).setdefault(t['color'],{})[t['view']]=rel(out)
    (OUT/'higgsfield_manifest.json').write_text(json.dumps(manifest,indent=2))
    print('ALL_DONE files',sum(1 for t in all_tasks() if Path(t['out']).exists()),'failed',len(failed),flush=True)

if __name__=='__main__': main()
