#!/usr/bin/env python3
"""Validate Epilogue data references, files, original audio, room, and no source scene/step collisions."""
import json,subprocess,wave
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1];A=R/'android/assets';D=A/'data'
s=json.loads((D/'story.json').read_text());q=json.loads((D/'quests.json').read_text());m=json.loads((D/'maps.json').read_text());b=json.loads((D/'memory_book.json').read_text())
checks=0
assert len(m['areas'])==29
assert len([v for v in s['scenes'] if v.startswith('V473-')])==29
assert len([v for v in q['steps'] if v['id'].startswith('V473_EPI_')])==7
assert len({v['id'] for v in q['steps']})==len(q['steps'])
assert len({v['id'] for v in b['entries']})==len(b['entries'])
checks+=5
sceneids=set(s['scenes']);stepids={x['id'] for x in q['steps']};areas=m['areas'];items=b['items']
def visit(acts):
 global checks
 for act in acts:
  op=act['do'];checks+=1
  if op=='scene': assert act['id'] in sceneids,act
  if op=='step': assert act['id'] in stepids,act
  if op=='item': assert act['id'] in items,act
  if op=='music':assert (A/'audio/music'/(act['id']+'.ogg')).exists(),act
  if op=='sfx':assert (A/'audio/sfx'/(act['id']+'.wav')).exists(),act
  if op=='if':visit(act.get('then',[]));visit(act.get('else',[]))
for st in q['steps']:
 if not st['id'].startswith('V473_EPI_'):continue
 for it in st['interactables']:
  assert it['area'] in areas,it
  assert it['id'] and 0<=it['x']<areas[it['area']]['w'] and 0<=it['y']<areas[it['area']]['h'],it
  image=it.get('sprite',{}).get('image')
  if image:assert (A/image).is_file(),image
  visit(it['actions']);checks+=1
for key,v in s['scenes'].items():
 if not key.startswith('V473-'):continue
 assert v['chapter']=='EPI' and v['location'] in areas and v['lines']
 for c in v.get('choices',[]):
  assert len(c['flags'])==1
  assert c['byRoute'].get('arland') and c['byRoute'].get('sofia')
  checks+=2
 checks+=1
for icon in ['page','letter','chair','photo','sunset']:
 p=A/'items'/('v473_'+icon+'.png');assert p.is_file()
 with Image.open(p) as im:assert im.size==(192,192) and im.mode=='RGBA'
 checks+=1
with Image.open(A/'maps/ruang_dua_surat.png') as im: assert im.size==(960,640)
checks+=1
for cue in ['cinema_homecoming_v473','cinema_dual_letters_v473']:
 p=A/'audio/music'/(cue+'.ogg');assert p.exists() and p.stat().st_size>1500
 codec=subprocess.run(['ffprobe','-v','error','-show_entries','stream=codec_name','-of','default=noprint_wrappers=1:nokey=1',str(p)],capture_output=True,text=True)
 assert 'vorbis' in codec.stdout,(cue,codec.stdout,codec.stderr)
 checks+=1
with wave.open(str(A/'audio/sfx/v473_letter_fold.wav')) as f:assert f.getnchannels()==1 and f.getframerate()==22050
checks+=1
register=(R/'core/src/main/java/com/arlandsofia/olu/logic/SoundscapePlan.java').read_text()
for id in ('cinema_homecoming_v473','cinema_dual_letters_v473','v473_letter_fold'):
 assert '"'+id+'"' in register;checks+=1
finale=next(x for x in q['steps'] if x['id']=='V473_EPI_FINALE')['interactables'][0]['actions']
assert len([a for a in finale if a['do']=='chapterEnd'])==1
assert len([a for a in finale if a['do']=='step' and a['id']=='EPI_FREE'])==1
assert any(a.get('id')=='V465-EPI-LAKE' for a in finale)
assert any(a.get('id')=='V472-EPI-A_FUTURE_LISTEN' for a in (x.get('then',[{}])[0] for x in finale if x.get('do')=='if'))
checks+=4
print('PASS EPI assets: ',checks,'real references, 29 scenes, 7 playable steps, original map, 5 pixel icons, 3 sound assets, legacy ending relocated')
