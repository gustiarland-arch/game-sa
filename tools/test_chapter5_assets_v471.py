#!/usr/bin/env python3
"""Static C05 art/audio/scene references, asset & warp consistency."""
from pathlib import Path
import json,subprocess,wave
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];ASSETS=ROOT/'android/assets';DATA=ASSETS/'data'
s=json.loads((DATA/'story.json').read_text());q=json.loads((DATA/'quests.json').read_text());m=json.loads((DATA/'maps.json').read_text());b=json.loads((DATA/'memory_book.json').read_text());
steps={x['id'] for x in q['steps']};scenes=set(s['scenes']);checks=0
def ok(v,msg):
 global checks
 checks+=1
 if not v:raise AssertionError(msg)
for key in ('clockwork_station','moonlight_lake','memory_bridge'):
 ok(key in m['areas'],'missing playable new map '+key)
 a=m['areas'][key];ok(a['w']==1920 and a['h']==1280,'bad map dimension '+key)
 with Image.open(ASSETS/a['image']) as im:ok(im.size==(1920,1280),'image size wrong '+key)
for k,area in m['areas'].items():
 for door in area.get('doors',[]):
  ok(door['to'] in m['areas'],'missing destination '+k+' '+door['to'])
  target=m['areas'][door['to']]
  ok(0<=door['tx']<target['w'] and 0<=door['ty']<target['h'],'bad destination '+door['id'])
for x in q['steps']:
 if x.get('chapter')!='C05':continue
 ok(bool(x.get('interactables')) or x.get('enterArea') is not None,'empty route stage '+x['id'])
 for item in x.get('interactables',[]):
  ok(item['area'] in m['areas'],'unknown area '+item['id'])
  area=m['areas'][item['area']]
  ok(0<item['x']<area['w'] and 0<item['y']<area['h'],'out-of-bounds object '+item['id'])
  if 'sprite' in item:ok((ASSETS/item['sprite']['image']).is_file(),'no sprite '+item['id'])
  def acts(actions):
   for a in actions:
    if a['do']=='scene':
     key=a['id'];ok(key in scenes or ('$ROUTE' in key and all(key.replace('$ROUTE',r) in scenes for r in ('arland','sofia'))),'no scene '+key)
    if a['do']=='step':ok(a['id'] in steps,'no step '+a['id'])
    if a['do']=='warp':ok(a['area'] in m['areas'] or a['area'] in ('$ROOM','$PARTNER_ROOM'),'bad warp '+a['area'])
    if a['do']=='item':ok(a['id'] in b['items'] or '$' in a['id'],'item not catalogued '+a['id'])
    if a['do']=='if':acts(a.get('then',[]));acts(a.get('else',[]))
    if a['do']=='music':ok((ASSETS/'audio/music'/(a['id']+'.ogg')).is_file(),'missing music '+a['id'])
  acts(item.get('actions',[]))
 if x.get('complete'):acts(x['complete']['actions'])
for k,v in s['scenes'].items():
 if v.get('chapter')!='C05':continue
 ok(len(v.get('lines',[]))>0,'empty scene '+k)
 for a in v['lines']:ok(bool(a.get('t')),'empty line '+k)
 for c in v.get('choices',[]):
  ok(bool(c['flags']),'choice without consequence '+k)
  for rt in ('arland','sofia'):ok(bool(c['byRoute'][rt]),'missing response '+k)
for x in b['entries']:
 if not x['id'].startswith('v471_c05_'):continue
 ok(x['chapter']=='C05','wrong memory chapter')
 ok((ASSETS/x['icon']).exists(),'memory icon missing '+x['id'])
for key in ('clock','mirror','star','book','bridge'):
 f=ASSETS/'items'/('v471_c05_'+key+'.png')
 with Image.open(f) as im:ok(im.size==(192,192) and im.mode=='RGBA','icon format '+key)
sound=(ROOT/'core/src/main/java/com/arlandsofia/olu/logic/SoundscapePlan.java').read_text()
for key in ('cinema_clockwork_v471','cinema_two_sides_v471','cinema_quiet_reveal_v471'):
 ok(key in sound,'unregistered music '+key)
 f=ASSETS/'audio/music'/(key+'.ogg')
 ok(f.stat().st_size>12000,'tiny audio '+key)
 result=subprocess.run(['ffprobe','-v','error','-show_entries','stream=codec_name','-of','default=noprint_wrappers=1:nokey=1',str(f)],capture_output=True,text=True)
 ok('vorbis' in result.stdout,'bad audio codec '+key)
ok('v471_memory_chime' in sound,'chime not registered')
with wave.open(str(ASSETS/'audio/sfx/v471_memory_chime.wav')) as w:ok(w.getframerate()==22050 and w.getnchannels()==1,'bad wav')
ok('V471_C05_CLOCK_ENTRY' in steps and 'V471_C05_FINAL_WALK' in steps,'missing major quest')
ok(len(m['areas'])>=27 and {'clockwork_station','moonlight_lake','memory_bridge'}<=set(m['areas']),'three original C05 maps preserved when later chapters add areas')
ok(len([it for it in next(x for x in q['steps'] if x['id']=='V471_C05_BRIDGE_FRAGMENTS')['interactables']])==5,'five distinct fragments')
ok(len(next(x for x in q['steps'] if x['id']=='V471_C05_BRIDGE_SEQUENCE')['interactables'])==4,'4-stage bridge alignment')
print(f'PASS V471 chapter5: {checks} static map, music, asset, story and reference checks')
