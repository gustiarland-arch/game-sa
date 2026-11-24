#!/usr/bin/env python3
"""Validates Chapter-1 story overhaul independently of external Android runtime."""
import hashlib,json,subprocess
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
AS=ROOT/'android/assets'
D=AS/'data'
s=json.loads((D/'story.json').read_text(encoding='utf-8'))
q=json.loads((D/'quests.json').read_text(encoding='utf-8'))
b=json.loads((D/'memory_book.json').read_text(encoding='utf-8'))
steps={st['id']:st for st in q['steps']}
checks=0

def ok(cond,reason):
 global checks
 checks+=1
 if not cond:raise AssertionError('C01 ASSET #'+str(checks)+': '+reason)

for id in ('C01_NOTE','C01_MURAL','C01_PUZZLE','C01_LARAS2','C01_RIVERSIDE','C01_SUNSET'):
 ok(id in steps,'missing original quest step '+id)
ok(len([c for c in s['chapters'] if c['id']=='C01'])==1,'Chapter 1 title unique')
ok(s['meta']['chapter1Overhaul'].startswith('v4.6.7'),'chapter audit metadata')
sceneids=set(s['scenes'])
for id in ('C01-A01','C01-S01','C01-X01','C01-X02','C01-PIER@arland','C01-PIER@sofia'):
 ok(id in sceneids,'old scene retained '+id)
for route,prefix in [('arland','A'),('sofia','S')]:
 opening=s['scenes']['C01-'+prefix+'01']
 ok(len(opening['choices'])==2,'intro dialogue has two choices')
 for choice in opening['choices']:
  ok(len(choice['flags'])==1,'opening choice flag')
  ok(all(choice['byRoute'].get(r) for r in ['arland','sofia']),'opening responses are voiced')
scene=s['scenes']['C01-X02']
ok(len(scene['choices'])==3,'letter has exactly three real decisions')
ok(all(x['byRoute']['arland'] and x['byRoute']['sofia'] for x in scene['choices']),
   'letter decisions have route-specific responses')
for id in ('V467_C01_LISTEN','V467_C01_RECORD','V467_C01_TRACE'):
 st=steps[id]
 ok(st['chapter']=='C01','branch is in correct chapter')
 ok(len(st['interactables'])==1,'branch has one distinct playable interaction')
 it=st['interactables'][0]
 ok(it['area']=='perpustakaan','branch in reachable library')
 ok(any(a.get('do')=='item' for a in it['actions']),'branch rewards an authored memory item')
 ok(any(a.get('do')=='step' and a.get('id')=='C01_RIVERSIDE' for a in it['actions']),
    'branch rejoins canonical chapter progression')
 for route in ('arland','sofia'):
  name='V467-C01-'+id.rsplit('_',1)[-1]+'@'+route
  ok(name in sceneids and s['scenes'][name]['route']==route,'route-specific branch scene '+name)
  ok(len(s['scenes'][name]['lines'])>=4,'branch not just one line '+name)
  callback=name.replace('C01-','C01-PIER-')
  ok(callback in sceneids and s['scenes'][callback]['route']==route,'route-specific pier payoff')
# All original chapter-one story must use valid speakers, valid emotion codes,
# and nonempty meaningful lines rather than placeholder debug strings.
for id,sc in s['scenes'].items():
 if sc.get('chapter')!='C01':continue
 ok(sc.get('lines') and all(x['t'].strip() for x in sc['lines']),'nonempty C01 lines '+id)
 for ln in sc['lines']:
  ok(ln['s'] in s['speakers'],'registered speaker '+id+' '+ln['s'])
  ok(ln.get('e','neutral') in s['emotions'],'registered expression '+id+' '+ln.get('e','neutral'))
# Three original pixel-art memories, no external copyrighted assets.
for k in ('listening','double_page','fading_ink'):
 name='v467_c01_'+k
 fn=AS/'items'/(name+'.png')
 ok(fn.is_file(),'memory icon exists '+name)
 with Image.open(fn) as im:
  ok(im.size==(192,192) and im.mode=='RGBA','icon dimensions RGBA '+name)
  im.verify()
 ok(name in b['items'],'new item catalogued '+name)
 ok(b['items'][name]['icon']=='items/'+name+'.png','catalog icon points to actual png')
for route in ('arland','sofia'):
 for key in ('listen','record','trace'):
  id=f'v467_c01_{route}_{key}'
  matches=[e for e in b['entries'] if e['id']==id]
  ok(len(matches)==1 and matches[0]['route']==route,'unique route memory '+id)
  ok((AS/matches[0]['icon']).is_file(),'memory references valid icon '+id)
  ok(matches[0]['unlock']=='V467_C01_RESULT_'+key.upper(),'memory unlock matches real branch')
# Explicit Story Bible C01-A03/S03 tasks: actually playable, not decorative.
for route,ask,find,flag in (
 ('arland','V467-C01-A03-ASK','V467-C01-A03-FOUND','V467_C01_A03_DONE'),
 ('sofia','V467-C01-S03-ASK','V467-C01-S03-FOUND','V467_C01_S03_DONE')):
 for scene_id in (ask,find):
  ok(scene_id in sceneids,'route-specific cafe chapter scene present '+scene_id)
  ok(s['scenes'][scene_id]['route']==route,'route locked to correct protagonist')
  ok(len(s['scenes'][scene_id]['lines'])>=5,'full cafe conversation rather than filler')
 ok(any(e.get('unlock')==flag and e.get('route')==route for e in b['entries']),
    'memory book records cafe quest outcome')
cafe_actions=steps['C01_CAFE']['enterArea']['actions']
ok(any(a.get('do')=='step' and a.get('id')=='V467_C01_CAFE_HELP' for a in cafe_actions),
   'cafe errand inserted into actual story before puzzle')
for id in ('V467_C01_CAFE_HELP','V467_C01_CAFE_A_FIND','V467_C01_CAFE_S_FIND'):
 ok(id in steps,'route-specific cafe step actually exists')

for actor_id,route in (('raka','arland'),('rara','sofia')):
 npc=next(n for n in q['townNpcs'] if n['id']==actor_id)
 overrides=[e for e in npc['schedule'] if e.get('v467')=='C01-cafe-personal']
 ok(len(overrides)==1,'exactly one conditional NPC schedule '+actor_id)
 ok(overrides[0]['when']['route']==route,'NPC schedule bound to correct route')
 ok(overrides[0]['area']=='cafe','story actor actually appears in cafe')

# Old intro, shared story, canon, and puzzle orders remain exactly as agreed.
ok(s['puzzle_orders']['arland']==['BUNGA','BUKU','BINTANG'],
   'Arland flower-book-star order preserved')
ok(s['puzzle_orders']['sofia']==['BINTANG','BUKU','BUNGA'],
   'Sofia star-book-flower order preserved')
ok(any(x.get('do')=='chapterEnd' and x.get('chapter')=='C01'
       for it in steps['C01_SUNSET']['interactables'] for x in it['actions']),
   'C01 canon completion retained')
# The new cinematic music is playable OGG/Vorbis and is registered in Java.
cue=AS/'audio/music/cinema_two_sides_v467.ogg'
ok(cue.is_file() and cue.stat().st_size>15000,'cinematic audio exists')
ok(cue.open('rb').read(4)==b'OggS','cinematic audio has OggS signature')
plan=(ROOT/'core/src/main/java/com/arlandsofia/olu/logic/SoundscapePlan.java').read_text(encoding='utf-8')
ok('"cinema_two_sides_v467"' in plan,'new cue registered in audio resolver')
cinema_actions=next(it for it in steps['C01_PUZZLE']['interactables'] if it['id']=='symbols')['actions']
ok(any(a.get('do')=='music' and a.get('id')=='cinema_two_sides_v467' for a in cinema_actions),
   'music triggered in actual puzzle reveal')
ok(any(a.get('do')=='cine' and a.get('v467')=='letter-reveal' for a in cinema_actions),
   'original letter reveal uses actual cutscene')
probe=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration',
                      '-of','default=nokey=1:noprint_wrappers=1',str(cue)],
                     capture_output=True,text=True)
ok(probe.returncode==0 and 15<float(probe.stdout.strip())<30,
   'Vorbis cue decodes and has expected duration')
print('PASS:',checks,'Chapter 1 story/icon/audio/reference assertions')
