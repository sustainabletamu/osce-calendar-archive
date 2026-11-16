import json,subprocess,time,hashlib,datetime,pathlib
root=pathlib.Path('/Users/eliottelin/Desktop/projects/calendar-archive/osce-calendar-archive-briefs/archive')
E={e['event_id']:e for e in json.loads((root/'data/events.json').read_text())}
ids=['359400','363287','379688','362803','386913','377642','386908','374684']
for i,eid in enumerate(ids):
 e=E[eid]; out=pathlib.Path('/tmp/osce-qa')/(eid+'.html'); hp=out.with_suffix('.headers'); mp=out.with_suffix('.meta.json'); url=e['original_url']; stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
 r=subprocess.run(['curl','--silent','--show-error','--location','--max-time','40','--dump-header',str(hp),'--output',str(out),'--write-out','%{json}',url],capture_output=True,text=True)
 try: info=json.loads(r.stdout)
 except Exception: info={'http_code':None,'error':r.stderr}
 b=out.read_bytes() if out.exists() else b''
 m={'event_id':eid,'url':url,'acquired_at_utc':stamp,'status':info.get('http_code'),'effective_url':info.get('url_effective'),'content_type':info.get('content_type'),'byte_size':len(b),'sha256':hashlib.sha256(b).hexdigest(),'curl_exit_code':r.returncode,'error':r.stderr or None,'path':str(out),'headers_path':str(hp)}
 mp.write_text(json.dumps(m,indent=2)+'\n'); print(eid,m['status'],len(b),flush=True)
 if i+1<len(ids):time.sleep(1)
