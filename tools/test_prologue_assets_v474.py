#!/usr/bin/env python3
"""Check prologue asset references and narrative continuity without Android SDK."""
from pathlib import Path
import json,subprocess,hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];ASSETS=ROOT/'android/assets';DATA=ASSETS/'data'
story=json.loads((DATA/'story.json').read_text(encoding='utf8'))
q=json.loads((DATA/'quests.json').read_text(encoding='utf8'))
m=json.loads((DATA/'maps.json').read_text(encoding='utf8'))
book=json.loads((DATA/'memory_book.json').read_text(encoding='utf8'))
checks=0
def ck(value,msg):
 global checks
 checks+=1
 assert value,msg
keys={x['id'] for x in q['steps']}
ck('PRO_PHONE' in keys and 'V474_PRO_CRAFT' in keys and 'V474_PRO_FINISH' in keys,'new prologue steps')
ck(len([x for x in q['steps'] if x['id']=='V474_PRO_CRAFT'])==1,'no duplicated stages')
for route in ('arland','sofia'):
 room=route+'_room';areas=m['areas'];locks=[lock for door in areas[room]['doors'] for lock in door.get('locked',[])]
 ck(any({'V474_PRO_CRAFT','V474_PRO_FINISH'}<=set(lock.get('steps',[])) for lock in locks),'new steps must lock outgoing door '+room)
 for id in ('V474_PRO_CRAFT','V474_PRO_FINISH'):
  step=next(x for x in q['steps'] if x['id']==id)
  items=[x for x in step['interactables'] if x.get('route')==route]
  ck(len(items)==1,'each route has one accessible task at '+id)
  it=items[0];ck(it['area']==room,'task stays in own room')
  ck((ASSETS/it['sprite']['image']).is_file(),'icon reference exists '+it['id'])
  ck(not any(x0<=it['x']<=x0+w and y0<=it['y']<=y0+h for x0,y0,w,h in areas[room]['walls']),'task not placed on collision wall')
for name in ('v474_folded_flower.png','v474_postcard.png','v474_ribbon.png','v474_shard.png'):
 file=ASSETS/'items'/name;ck(file.is_file(),'pixel icon file '+name)
 im=Image.open(file);ck(im.size==(192,192) and im.mode=='RGBA','editable pixel RGBA 192x192 '+name)
for cue in ('cinema_prologue_promise_v474','cinema_prologue_memory_v474'):
 path=ASSETS/'audio/music'/(cue+'.ogg');ck(path.exists() and path.stat().st_size>10000,'music exists '+cue)
 proc=subprocess.run(['ffprobe','-v','error','-show_entries','stream=codec_name:format=duration','-of','json',str(path)],capture_output=True,text=True,check=True)
 meta=json.loads(proc.stdout);ck(meta['streams'][0]['codec_name']=='vorbis','music valid Vorbis '+cue)
 ck(float(meta['format']['duration'])>20,'meaningful original audio duration '+cue)
 ck(cue in (ROOT/'core/src/main/java/com/arlandsofia/olu/logic/SoundscapePlan.java').read_text(),'registered soundtrack '+cue)
for name,scene in story['scenes'].items():
 if name.startswith('V474-'):
  ck(scene['chapter'] in ('PRO','C01','EPI'),'new scene chapter recognized '+name)
  ck(len(scene['lines'])>=2,'new scene substantial '+name)
  for c in scene.get('choices',[]):
   ck(c['flags'] and all(c['byRoute'][r] for r in ('arland','sofia')),'choice has two route responses '+name)
for s in q['steps']:
 for it in s.get('interactables',[]):
  for act in it['actions']:
   if act.get('do')=='scene':
    ref=act['id'];ck((ref in story['scenes']) or ('$ROUTE' in ref and all(ref.replace('$ROUTE',r) in story['scenes'] for r in ('arland','sofia'))),'scene linked '+ref)
  # Nested conditional references used by prologue.
  if s['chapter']=='PRO':
   for ac in it['actions']:
    for branch in ('then','else'):
     for nested in ac.get(branch,[]):
      if nested.get('do')=='scene':ck(nested['id'] in story['scenes'],'nested scene '+nested['id'])
for entry in book['entries']:
 if entry['id'].startswith('v474_pro_'):
  ck((ASSETS/entry['icon']).is_file(),'memory reference '+entry['id'])
  ck(entry['type']=='optional_story_branch','mutually exclusive memory choices stay optional')
ck(len({x['id'] for x in book['entries']})==len(book['entries']),'memory IDs unique')
print('PASS prologue assets v474:',checks,'checks; 4 icons, 2 OGG, map locks, scenes, memory')
