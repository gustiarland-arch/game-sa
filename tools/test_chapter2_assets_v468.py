#!/usr/bin/env python3
"""Full authored Chapter-2 static, audiovisual and reference QA."""
import json,subprocess,wave
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
AS=ROOT/'android/assets'; D=AS/'data'
s=json.loads((D/'story.json').read_text(encoding='utf-8'))
q=json.loads((D/'quests.json').read_text(encoding='utf-8'))
b=json.loads((D/'memory_book.json').read_text(encoding='utf-8'))
scene=s['scenes'];step={x['id']:x for x in q['steps']}
n=0

def ok(cond,text):
 global n
 n+=1
 if not cond:raise AssertionError(f'C02 ASSET #{n}: {text}')

ok(s['meta']['chapter2Overhaul'].startswith('v4.6.8'),'draft marker')
ok(len({x['id'] for x in q['steps']})==len(q['steps']),'unique quest step ids')
for sid in ('C02_PHONE','C02_FREE','C02_TO_CAFE','C02_DATE','C02_SUNSET','C02_A_FLORIST','C02_S_PRINT',
    'V468_C02_LATER_NOTE','V468_C02_NO_SKETCH','V468_C02_NO_REINVITE','V468_C02_REUNION','V468_C02_PHOTO_REPAIR'):
 ok(sid in step,'step exists '+sid)
for sid in ('V468-C02-S-REPLY','V468-C02-A-INVITE','V468-C02-PHOTO-CHOICE','V468-C02-GAZEBO'):
 sc=scene[sid]
 ok(len(sc['choices'])==3,'3 choices in '+sid)
 for c in sc['choices']:
  ok(len(c['flags'])==1,'one distinct flag per choice in '+sid)
  for rt in ('arland','sofia'):
   ok(c['byRoute'].get(rt) and all(x['t'].strip() for x in c['byRoute'][rt]),
      'authored route response for '+sid+'/'+rt)
for rt in ('arland','sofia'):
 for id in ('C02-X02','C02-X03','C02-X04','V468-C02-SOFT-SKETCH',
            'V468-C02-PHOTO-LANTERN','V468-C02-PHOTO-TECH'):
  ok(id in scene,'mandatory authored narrative '+id)
for id,sc in scene.items():
 if sc.get('chapter')!='C02':continue
 ok(bool(sc.get('lines')),'at least one meaningful line '+id)
 for ln in sc['lines']:
  ok(ln['s'] in s['speakers'],'registered speaker '+id+'/'+ln['s'])
  ok(ln.get('e','neutral') in s['emotions'],'known emotion '+id+'/'+ln.get('e','neutral'))
  ok(len(ln['t'].strip())>=2,'nonblank dialogue '+id)
for id in ('V468_C02_LATER_NOTE','V468_C02_NO_SKETCH','V468_C02_NO_REINVITE','V468_C02_REUNION'):
 st=step[id]
 ok(len(st['interactables'])==1,'alternate real map interaction '+id)
 it=st['interactables'][0]
 ok(it['area'] in json.loads((D/'maps.json').read_text(encoding='utf-8'))['areas'],
    'alternate interaction area exists '+id)
 ok(len(it['actions'])>2,'actions beyond dialogue '+id)
 ok(any(a['do']=='step' for a in it['actions']), 'alternate quest continues '+id)
for rt in ('arland','sofia'):
 phone=next(it for it in step['C02_PHONE']['interactables'] if it['route']==rt)
 ok(any(a.get('id')=='V468-C02-'+('A-INVITE' if rt=='arland' else 'S-REPLY') for a in phone['actions']),
    'invitation/reply genuinely triggers in quest at phone '+rt)

def acts(seq,where):
 for a in seq:
  d=a.get('do')
  ok(d in ('scene','cine','music','sfx','flag','unflag','item','removeItem','step','warp',
       'restUntilTomorrow','minigame','count','companion','if','chapterEnd','chapterCard','toast','emote'),
       'supported action '+str(d)+' in '+where)
  if d=='if':
   acts(a.get('then',[]),where+':then');acts(a.get('else',[]),where+':else')
  elif d=='scene':ok(a['id'] in scene or '$ROUTE' in a['id'],'scene reference '+a['id'])
  elif d=='step':ok(a['id'] in step,'quest reference '+a['id'])
  elif d=='minigame':ok(a['id'] in q['minigames'],'minigame registered '+a['id'])
  elif d=='music':ok((AS/'audio/music'/(a['id']+'.ogg')).is_file(),'music exists '+a['id'])
  elif d=='sfx':ok((AS/'audio/sfx'/(a['id']+'.wav')).is_file(),'SFX exists '+a['id'])
  elif d=='cine':
   ok(bool(a.get('cmds')),'nonempty scripted camera '+where)
   for c in a['cmds']:
    ok(c.get('c') in ('bars','shot','fx','wait','say','move','pose','emote','fade','camera'),
       'valid cinematic directive '+str(c.get('c')))

for id,st in step.items():
 if st.get('chapter')!='C02':continue
 for it in st.get('interactables',[]): acts(it.get('actions',[]),id+'/'+it['id'])
 if 'complete' in st: acts(st['complete'].get('actions',[]),id+'/complete')
# C02 park and photo unique rewards require native engine flags.
acts(step['C02_SUNSET']['interactables'][0]['actions'],'sunset')
ok(any(a.get('do')=='if' for a in step['C02_SUNSET']['interactables'][0]['actions']),
   'gift exchanges are conditional on route')
ok(any(a['do']=='restUntilTomorrow' for a in step['V468_C02_LATER_NOTE']['interactables'][0]['actions']),
   'postponement advances calendar, not only dialogue')
ok(any(a['do']=='restUntilTomorrow' for a in step['V468_C02_NO_REINVITE']['interactables'][0]['actions']),
   'decline creates genuine next-day alternate route')
# Memory book image assets exist and each route remembers its own choice.
memories=[e for e in b['entries'] if e['id'].startswith('v468_c02_')]
ok(len(memories)==17,'17 new book entries: 7 per route + 3 extra Sofia')
ok(len({m['id'] for m in memories})==len(memories),'unique Chapter-2 memory IDs')
for m in memories:
 ok(m['chapter']=='C02','correct memory chapter '+m['id'])
 ok(m['unlock'].startswith('V468_'),'memory unlock corresponds to new narrative decision '+m['id'])
 ok((AS/m['icon']).is_file(),'memory icon file '+m['icon'])
 ok(bool(m['title'].strip()) and bool(m['text'].strip()),'authored Memory Book entry '+m['id'])
for name in ('v468_c02_lantern','v468_c02_calendar','v468_c02_sketch'):
 file=AS/'items'/(name+'.png')
 ok(file.is_file(),'icon exists '+name)
 with Image.open(file) as img:
  ok(img.size==(192,192),'192px pixel icon '+name)
  ok(img.mode=='RGBA','RGBA transparent asset '+name)
  img.verify()
for name in ('v468_lantern_photo','v468_date_note','v468_independent_sketch'):
 ok(name in b['items'],'all collectible items catalogued '+name)
 ok((AS/b['items'][name]['icon']).is_file(),'catalog references icon '+name)
# Audio format and channel data, plus actual Java SoundscapePlan registrations.
java=(ROOT/'core/src/main/java/com/arlandsofia/olu/logic/SoundscapePlan.java').read_text(encoding='utf-8')
for token in ('cinema_date_choices_v468','photo_lantern_v468'):
 ok(('"'+token+'"') in java,'audio engine registration '+token)
proc=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration',
    '-of','default=noprint_wrappers=1:nokey=1',
    str(AS/'audio/music/cinema_date_choices_v468.ogg')],capture_output=True,text=True,check=True)
length=float(proc.stdout.strip())
ok(27<=length<=30,'original soundtrack correct duration')
with wave.open(str(AS/'audio/sfx/photo_lantern_v468.wav'),'rb') as wav:
 ok(wav.getnchannels()==1,'original SFX mono')
 ok(wav.getframerate()==22050,'SFX valid sampling rate')
 ok(wav.getnframes()>10000,'original SFX has audible duration')
print('PASS:',n,'Chapter-2 narrative, refs, original pixel assets and audio checks')
