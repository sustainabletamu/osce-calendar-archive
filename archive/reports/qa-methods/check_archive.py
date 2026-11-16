from pathlib import Path
import json,hashlib,collections,datetime
from zoneinfo import ZoneInfo
R=Path('/Users/eliottelin/Desktop/projects/calendar-archive/osce-calendar-archive-briefs/archive');E=json.loads((R/'data/events.json').read_text());O=json.loads((R/'data/occurrences.json').read_text());A=json.loads((R/'data/assets.json').read_text());M=json.loads((R/'raw/manifest.json').read_text())
errors=[];raw=[];months=[]
for p in M['pages']:
 b=(R/p['path']).read_bytes();j=json.loads(b);d=j['data'];raw+=d
 if len(b)!=p['byte_size'] or hashlib.sha256(b).hexdigest()!=p['sha256']:errors.append(['raw_hash',p['path']])
 if len(d)!=j['meta']['total_results'] or j['links']['next'] is not None:errors.append(['pagination',p['path']])
 months.append({'month':p['path'].split('/')[-2],'raw_rows':len(d),'meta_total':j['meta']['total_results'],'meta_pages':j['meta']['total_pages'],'http_status':p['http_status']})
rawkeys={(str(r['id']),r['date_iso'],r.get('date2_iso')) for r in raw};cankeys={(o['event_id'],o['start_iso_original'],o['end_iso_original']) for o in O}
if rawkeys!=cankeys:errors.append(['occurrence_key_difference',len(rawkeys-cankeys),len(cankeys-rawkeys)])
if {str(r['id']) for r in raw}!={e['event_id'] for e in E}:errors.append(['event_id_difference'])
for o in O:
 if datetime.datetime.fromisoformat(o['start_iso_original']).astimezone(ZoneInfo('America/Chicago')).isoformat()!=o['display_start_local']:errors.append(['timezone',o['occurrence_id']])
 if o['end_iso_original'] is None and o['display_end_local'] is not None:errors.append(['inferred_end',o['occurrence_id']])
for e in E:
 rows=[r for r in raw if str(r['id'])==e['event_id']]
 for f in ['summary','description']:
  if e[f+'_html_original']!=rows[0].get(f):errors.append(['html_changed',e['event_id'],f])
 if e['occurrence_count']!=sum(o['event_id']==e['event_id'] for o in O):errors.append(['occurrence_count',e['event_id']])
 for aid in e['image_asset_ids']:
  if aid not in {a['asset_id'] for a in A}:errors.append(['bad_asset_ref',e['event_id'],aid])
for a in A:
 b=(R/a['local_path']).read_bytes()
 if len(b)!=a['byte_size'] or hashlib.sha256(b).hexdigest()!=a['sha256']:errors.append(['asset_hash',a['asset_id']])
caption_ok=all(any(c['event_id']==e['event_id'] and c['caption']==e['thumbnail_caption'] and c['alt_text']==e['thumbnail_alt'] for a in A if a['asset_id'] in e['image_asset_ids'] for c in a['claims']) for e in E if e['image_asset_ids'])
result={'months':months,'events':len(E),'raw_rows':len(raw),'occurrences':len(O),'unique_raw_occurrence_keys':len(rawkeys),'assets':len(A),'asset_bytes':sum(a['byte_size'] for a in A),'events_with_media':sum(bool(e['image_asset_ids']) for e in E),'events_without_media':sum(not e['image_asset_ids'] for e in E),'null_description':sum(e['description_html_original'] is None for e in E),'null_summary':sum(e['summary_html_original'] is None for e in E),'ownership_counts':dict(collections.Counter(str(r['gid']) for r in raw)),'caption_alt_preservation':caption_ok,'errors':errors}
Path('/tmp/osce-qa/archive_checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='months'},indent=2))
