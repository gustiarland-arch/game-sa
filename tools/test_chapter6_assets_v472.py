#!/usr/bin/env python3
"""Ensure every new quest scene, asset, audio and physical portal is real."""
import json,hashlib,subprocess,wave
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1];D=R/'android/assets/data';A=R/'android/assets'
s=json.loads((D/'story.json').read_text());q=json.loads((D/'quests.json').read_text());m=json.loads((D/'maps.json').read_text());b=json.loads((D/'memory_book.json').read_text())
assert 'hall_of_tomorrow' in m['areas']
ids={st['id'] for st in q['steps']};checks=0
for st in q['steps']:
 if not st['id'].startswith('V472_C06_'):continue
 for it in st['interactables']:
  assert it['area'] in m['areas'],it
  sprite=it.get('sprite',{}).get('image')
  if sprite:assert (A/sprite).is_file(),sprite
  checks+=1
  todo=list(it['actions'])
  while todo:
   a=todo.pop()
   if a['do']=='scene':assert a['id'] in s['scenes'],a
   if a['do']=='step':assert a['id'] in ids,a
   if a['do']=='if':todo.extend(a.get('then',[]));todo.extend(a.get('else',[]))
   if a['do']=='item':assert a['id'] in b['items'],a
   checks+=1
for key,sc in s['scenes'].items():
 if not key.startswith('V472-'):continue
 assert sc['lines'],key
 assert sc['chapter'] in ('C06','EPI'),key
 assert sc['location'] in m['areas'],key
 for c in sc.get('choices',[]):
  assert c.get('flags'),(key,c)
  assert c.get('byRoute',{}).get('arland') and c.get('byRoute',{}).get('sofia'),key
  checks+=2
 checks+=1
assert len([e for e in b['entries'] if e['id'].startswith('v472_c06_')])>=14
for icon in ('hall','mirror','flower','sketch','page'):
 p=A/'items'/('v472_c06_'+icon+'.png');assert p.exists()
 with Image.open(p) as im:assert im.size==(192,192) and im.mode=='RGBA'
 checks+=1
with Image.open(A/'maps/hall_of_tomorrow.png') as im:assert im.size==(1920,1280);checks+=1
for path in [A/'audio/music/cinema_hall_v472.ogg',A/'audio/music/cinema_unwritten_v472.ogg',A/'audio/sfx/v472_memory_glint.wav']:
 assert path.is_file() and path.stat().st_size>2000,path
 checks+=1
for key in ('cinema_hall_v472','cinema_unwritten_v472'):
 f=A/'audio/music'/(key+'.ogg')
 codec=subprocess.run(['ffprobe','-v','error','-show_entries','stream=codec_name','-of','default=noprint_wrappers=1:nokey=1',str(f)],capture_output=True,text=True)
 assert 'vorbis' in codec.stdout,('invalid OGG music',key);checks+=1
with wave.open(str(A/'audio/sfx/v472_memory_glint.wav')) as wav:
 assert wav.getnchannels()==1 and wav.getframerate()==22050;checks+=1
assert sum(1 for k in s['scenes'] if k.startswith('V472-'))==55;checks+=1
assert len([st for st in q['steps'] if st['id'].startswith('V472_C06_')])==6;checks+=1
assert len(m['areas'])>=28;checks+=1 # Epilogue adds more areas but must preserve every C06 map

sound=(R/'core/src/main/java/com/arlandsofia/olu/logic/SoundscapePlan.java').read_text()
for id in ('cinema_hall_v472','cinema_unwritten_v472','v472_memory_glint'):
 assert '"'+id+'"' in sound,id;checks+=1
for d in m['areas']['hall_of_tomorrow']['doors']:
 assert d['to'] in m['areas'];checks+=1
assert any(d['id']=='v472_garden_to_hall' for d in m['areas']['eternal_garden']['doors']);checks+=1
print('PASS C06 assets: %d checks; new original map, five icons, three audio, 55 scenes, 6 quests, 2-way portal'%checks)
