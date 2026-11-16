from pathlib import Path
import json,struct,hashlib
R=Path('/Users/eliottelin/Desktop/projects/calendar-archive/osce-calendar-archive-briefs/archive')
A=json.loads((R/'data/assets.json').read_text())
def inspect(b):
 if b[:8]==b'\x89PNG\r\n\x1a\n':return 'image/png',*struct.unpack('>II',b[16:24])
 if b[:2]==b'\xff\xd8':
  p=2
  while p<len(b):
   if b[p]!=255:p+=1;continue
   while p<len(b) and b[p]==255:p+=1
   marker=b[p];p+=1
   if marker in [0xd8,0xd9,0x01] or 0xd0<=marker<=0xd7:continue
   n=struct.unpack('>H',b[p:p+2])[0]
   if marker in [0xc0,0xc1,0xc2,0xc3,0xc5,0xc6,0xc7,0xc9,0xca,0xcb,0xcd,0xce,0xcf]:
    h,w=struct.unpack('>HH',b[p+3:p+7]);return 'image/jpeg',w,h
   p+=n
 raise ValueError('unsupported image')
results=[]
for a in A:
 b=(R/a['local_path']).read_bytes();mime,w,h=inspect(b);match=(mime,w,h)==(a['mime_type'],a['width_px'],a['height_px']);results.append({'asset_id':a['asset_id'],'mime':mime,'width':w,'height':h,'match':match,'hash_match':hashlib.sha256(b).hexdigest()==a['sha256'],'bytes_match':len(b)==a['byte_size']})
Path('/tmp/osce-qa/media_checks.json').write_text(json.dumps(results,indent=2)+'\n');print({'images':len(results),'mime_dimension_matches':sum(r['match'] for r in results),'hashes_match':sum(r['hash_match'] for r in results),'bytes_match':sum(r['bytes_match'] for r in results)})
