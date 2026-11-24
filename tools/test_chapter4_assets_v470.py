#!/usr/bin/env python3
"""Sound, media, flag and scene reference audit for C04, with legacy preservation."""
from pathlib import Path
from PIL import Image
import json,wave,subprocess,re
ROOT=Path(__file__).resolve().parents[1];ASSETS=ROOT/'android/assets';D=ASSETS/'data'
s=json.loads((D/'story.json').read_text());q=json.loads((D/'quests.json').read_text());b=json.loads((D/'memory_book.json').read_text());n=0
STEPS={x['id'] for x in q['steps']};SCENES=set(s['scenes'])
def check(v,msg):
 global n
 n+=1
 if not v:raise AssertionError(msg)
check(s['meta'].get('chapter4Overhaul','').startswith('v4.7.0'),'missing patch meta')
for k in ('V470_C04_S_PREP','V470_C04_A_WARN','V470_C04_A_SILENT','V470_C04_A_HELP','V470_C04_S_AFTER','V470_C04_A_AFTER','V470_C04_A_PROOF','V470_C04_S_PROOF'):
 check(k in STEPS,'missing C04 branch step '+k)
for k,v in s['scenes'].items():
 if v.get('chapter')!='C04':continue
 check(len(v.get('lines',[]))>0,'empty lines '+k)
 for l in v.get('lines',[]):check(bool(l.get('t','')),'empty dialogue '+k)
 for ch in v.get('choices',[]):
  check(bool(ch.get('flags')),'choice flag missing '+k)
  for rt in ('arland','sofia'):check(bool(ch.get('byRoute',{}).get(rt)),'choice response missing '+k)
for step in q['steps']:
 if step.get('chapter')!='C04':continue
 check(bool(step.get('interactables')),'empty interactables '+step['id'])
 for it in step['interactables']:
  if it.get('sprite'):check((ASSETS/it['sprite']['image']).exists(),'missing interactable sprite '+it['id'])
  def acts(actions):
   for a in actions:
    if a['do']=='scene':check(a['id'] in SCENES or ('$ROUTE' in a['id'] and all(a['id'].replace('$ROUTE', rt) in SCENES for rt in ('arland','sofia'))),'missing scene '+a['id'])
    if a['do']=='step':check(a['id'] in STEPS,'missing step '+a['id'])
    if a['do']=='music':check((ASSETS/'audio/music'/(a['id']+'.ogg')).exists() or a['id'] in ('town','rain'),'missing music '+a['id'])
    if a['do']=='if':
     acts(a.get('then',[]));acts(a.get('else',[]))
  acts(it.get('actions',[]))
  if it.get('when'):check(isinstance(it['when'],dict),'invalid conditional')
 for a in step.get('complete',{}).get('actions',[]):
  if a['do']=='step':check(a['id'] in STEPS,'invalid completion step')
for item in b['entries']:
 if not item.get('id','').startswith('v470_c04_'):continue
 check(item['chapter']=='C04','bad memory chapter')
 check((ASSETS/item['icon']).exists(),'missing memory art '+item['id'])
for key in ['seat','letter','lantern','promise','projector']:
 f=ASSETS/'items'/f'v470_c04_{key}.png'
 with Image.open(f) as im:check(im.size==(192,192) and im.mode=='RGBA', 'bad pixel icon '+key)
for music in ['cinema_empty_seat_v470','cinema_rain_five_lights_v470','cinema_listen_again_v470']:
 f=ASSETS/'audio/music'/(music+'.ogg');check(f.is_file() and f.stat().st_size>12000,'bad original track '+music)
 result=subprocess.run(['ffprobe','-v','error','-show_entries','stream=codec_name','-of','default=noprint_wrappers=1:nokey=1',str(f)],capture_output=True,text=True)
 check('vorbis' in result.stdout,'bad codec '+music)
check((ASSETS/'audio/sfx/v470_paper_note.wav').is_file(),'missing sfx')
with wave.open(str(ASSETS/'audio/sfx/v470_paper_note.wav')) as w:check(w.getnchannels()==1 and w.getframerate()==22050,'bad sfx format')
registry=(ROOT/'core/src/main/java/com/arlandsofia/olu/logic/SoundscapePlan.java').read_text()
for name in ('cinema_empty_seat_v470','cinema_rain_five_lights_v470','cinema_listen_again_v470','v470_paper_note'):
 check(name in registry,'sound not registered '+name)
check(next(x for x in q['steps'] if x['id']=='C04_LIGHTS')['complete']['count']==5,'five lights not required')
# Rain Garden is an actual original area and ALL C04 lantern objectives are there.
world=json.loads((D/'maps.json').read_text())
check(len(world['areas'])>=24 and {'galeri_komunitas','rain_garden','lantern_field','star_path','starfall_village'}<=set(world['areas']),'24 original/earlier maps must survive, later chapters can add more')
check('rain_garden' in world['areas'],'Rain Garden map record missing')
rain=world['areas']['rain_garden']
check(rain['w']==1920 and rain['h']==1280,'Rain Garden coordinate bounds')
with Image.open(ASSETS/'maps/rain_garden.png') as im:
 check(im.size==(1920,1280) and im.mode in ('RGB','RGBA'),'Rain Garden original image missing')
check(all(it['area']=='rain_garden' for key in ('C04_LIGHTS','C04_PUZZLE') for it in next(x for x in q['steps'] if x['id']==key)['interactables']),'all five lanterns in Rain Garden')
check(any(d.get('to')=='rain_garden' for d in world['areas']['taman_kota']['doors']),'missing portal entrance')
check(any(d.get('to')=='taman_kota' for d in rain['doors']),'missing portal exit')
print('PASS: '+str(n)+' Chapter4 media, story, quest, dialogue, 5-lantern and audio references verified')
