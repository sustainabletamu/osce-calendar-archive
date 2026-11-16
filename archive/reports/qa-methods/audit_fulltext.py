import json,subprocess,time,hashlib,datetime,pathlib
for i,eid in enumerate(['379688','377642']):
 out=pathlib.Path('/tmp/osce-qa')/(eid+'-individual.json');hp=out.with_suffix('.headers');url='https://calendar.tamu.edu/live/events/'+eid+'@JSON';stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
 r=subprocess.run(['curl','--silent','--show-error','--location','--max-time','40','--dump-header',str(hp),'--output',str(out),'--write-out','%{json}',url],capture_output=True,text=True)
 try:info=json.loads(r.stdout)
 except Exception:info={}
 b=out.read_bytes() if out.exists() else b'';m={'event_id':eid,'url':url,'acquired_at_utc':stamp,'status':info.get('http_code'),'effective_url':info.get('url_effective'),'content_type':info.get('content_type'),'byte_size':len(b),'sha256':hashlib.sha256(b).hexdigest(),'curl_exit_code':r.returncode,'error':r.stderr or None,'path':str(out),'headers_path':str(hp)}
 out.with_suffix('.meta.json').write_text(json.dumps(m,indent=2)+'\n');print(eid,m['status'],len(b),flush=True)
 if i==0:time.sleep(1)
