#!/usr/bin/env python3
"""Validate all updated story/quest IDs plus new art/audio in the offline Android assets."""
import json
from pathlib import Path
from PIL import Image
BASE=Path(__file__).resolve().parents[1]
A=BASE/'android/assets';D=A/'data'
S=json.loads((D/'story.json').read_text(encoding='utf-8'))
Q=json.loads((D/'quests.json').read_text(encoding='utf-8'))
M=json.loads((D/'maps.json').read_text(encoding='utf-8'))
B=json.loads((D/'memory_book.json').read_text(encoding='utf-8'))
checked=0
def ck(flag,why):
 global checked
 checked+=1
 if not flag:raise AssertionError(why)

sceneids=set(S['scenes']);steps={st['id'] for st in Q['steps']};areas=set(M['areas'])
ck(len(steps)==len(Q['steps']),'no duplicate quest step IDs')
ck(len(areas)>=24 and {'galeri_komunitas','rain_garden','star_path','lantern_field','starfall_village','eternal_garden'}<=areas,'22 original maps + gallery + Rain Garden')
ck('v465_second_chance' in {b['id'] for b in B['entries']},'memory collectible included')
for name,sc in S['scenes'].items():
 ck(isinstance(sc.get('lines'),list) and sc['lines'],'story scene empty '+name)
 ck(sc.get('route') in ('arland','sofia','shared'),'bad route '+name)
 for line in sc['lines']:
  ck(line.get('s') in S['speakers'],'unknown speaker '+name+'/'+str(line.get('s')))
  ck(isinstance(line.get('t'),str) and bool(line['t'].strip()),'empty text '+name)
 for c in sc.get('choices',[]):
  ck(bool(c.get('text','').strip()),'empty choice '+name)
  for route in ('arland','sofia'):
   ck(bool(c['byRoute'][route]),'missing choice response '+name+'/'+route)

# Runtime scene IDs include tokens @${ROUTE}; check both resolved route variants.
def check_action(act,context):
 d=act.get('do')
 if d=='scene':
  name=str(act.get('id',''))
  for route in ('arland','sofia'):
   target=name.replace('@$ROUTE','@'+route).replace('$ROUTE',route)
   ck(target in sceneids,'missing scene '+target+' at '+context)
 elif d=='step':ck(act.get('id') in steps,'unknown quest step '+str(act.get('id'))+' at '+context)
 elif d=='warp':
  area=act.get('area','')
  ck(area in areas or area in ('$ROOM','$AREA','$CURRENT'),
     'unknown warp target '+str(area)+' at '+context)
 elif d=='if':
  for key in ('then','else'):
   for nested in act.get(key,[]):check_action(nested,context+'/if')
 elif d=='music':
  tune=str(act.get('id'))
  if tune.startswith('cinema_gallery_'):
   ck((A/'audio/music'/f'{tune}.ogg').is_file(),'missing cinematic tune '+tune)
 elif d=='cine':
  for command in act.get('cmds',[]):
   if command.get('c')=='music':
    tune=str(command.get('id'))
    if tune.startswith('cinema_gallery_'):
     ck((A/'audio/music'/f'{tune}.ogg').is_file(),'missing music in cinema '+tune)

for st in Q['steps']:
 for action in st.get('onStart',[]):check_action(action,st['id']+'/onStart')
 for it in st.get('interactables',[]):
  ck(it.get('area') in areas or it.get('area') in ('$ROOM','$AREA'),'unknown area of interaction '+st['id'])
  for act in it.get('actions',[]):check_action(act,st['id']+'/'+it['id'])
 for act in st.get('complete',{}).get('actions',[]):check_action(act,st['id']+'/complete')
 for act in st.get('enterArea',{}).get('actions',[]):check_action(act,st['id']+'/enterArea')

for id in ('galeri_komunitas',):
 info=M['areas'][id];f=A/info['image']
 ck(f.exists(),'gallery picture absent')
 with Image.open(f) as im:
  ck(im.size==(info['w'],info['h']),'gallery dimensions invalid');im.verify()
 for door in info.get('doors',[]):ck(door.get('to') in areas,'gallery portal unknown')
for file in ['items/v464_gallery_ticket.png','items/v464_empty_seat.png','items/v464_projector.png',
             'items/v464_seat_healed.png','items/v464_sketch.png','items/v464_two_sides.png',
             'items/v465_bench_memory.png']:
 p=A/file;ck(p.exists(),file+' missing')
 with Image.open(p) as im:im.verify();ck(True,file+' decoded')
for id in ('cinema_gallery_empty','cinema_gallery_repair'):
 ck((A/'audio/music'/f'{id}.ogg').stat().st_size>2000,'missing valid track '+id)
print('PASS:',checked,'story / quest / asset reference assertions')
