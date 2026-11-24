#!/usr/bin/env python3
"""No dead assets or missing refs for the v4.6.6 choice-reactive finale."""
from pathlib import Path
import json
from PIL import Image
from subprocess import run
import shutil

ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'android/assets';D=A/'data'
s=json.loads((D/'story.json').read_text(encoding='utf-8'))
q=json.loads((D/'quests.json').read_text(encoding='utf-8'))
b=json.loads((D/'memory_book.json').read_text(encoding='utf-8'))
checks=0
def ok(cond,why):
 global checks
 checks+=1
 if not cond:raise AssertionError(why)
for name in ('v466_letter_arland','v466_letter_sofia','v466_gallery_revisit'):
 f=A/'items'/f'{name}.png'
 ok(f.is_file(),f'icon missing {name}')
 with Image.open(f) as im:
  ok(im.size==(192,192),f'icon wrong size {name}')
  im.verify()
for key in ('V466-C06-A-LETTER','V466-C06-S-LETTER','V466-C06-SHARED-PAGE',
            'V466-EPI-A-GALLERY','V466-EPI-S-GALLERY','V466-EPI-OLD-CHAPTER'):
 ok(key in s['scenes'],f'new dialogue missing {key}')
steps={x['id']:x for x in q['steps']}
for id in ('C06_FINAL','EPI_FEST_LEPAS','EPI_FREE'):
 ok(id in steps,f'final step missing {id}')
for id in ('v466_letter_arland','v466_letter_sofia','v466_gallery_return'):
 entries=[e for e in b['entries'] if e.get('id')==id]
 ok(len(entries)==1,'Memory Book entry missing/duplicate '+id)
 ok((A/entries[0]['icon']).is_file(),'missing associated memory icon '+id)
finish=next(it for it in steps['C06_FINAL']['interactables'] if it['id']=='pages')
act=finish['actions']
ok(sum('v466' in x for x in act)==2,'letters inserted exactly once')
old_idx=next(i for i,x in enumerate(act) if x.get('id')=='C06-X01')
ok(any(x.get('v466') and x.get('do')=='if' for x in act[:old_idx]),'letters before old canon')
# v4.7.3 physically relocates the original coda from festival to the real lakeside finale.
ending=steps['V473_EPI_FINALE']['interactables'][0]
ok(any(x.get('id')=='V465-EPI-LAKE' for x in ending['actions']),'old epilogue remains at the lakeside finale')
release=next(it for it in steps['EPI_FEST_LEPAS']['interactables'] if it['id']=='fest_release')
ok(any(x.get('id')=='V473_EPI_PLAZA' for x in release['actions']),'festival leads into mandatory playable memory walk')
free=steps['EPI_FREE']['interactables']
ok(sum(x['id']=='v466_gallery_return' for x in free)==1,'postgame gallery present once')
audio=A/'audio/music/cinema_letter_tomorrow.ogg'
ok(audio.is_file() and audio.stat().st_size>20000,'missing original finale cue')
ok(audio.open('rb').read(4)==b'OggS','music must be Ogg Vorbis container')
if shutil.which('ffprobe'):
 p=run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(audio)],capture_output=True,text=True)
 ok(p.returncode==0 and 20<float(p.stdout.strip())<40,'unreadable music file')
plan=(ROOT/'core/src/main/java/com/arlandsofia/olu/logic/SoundscapePlan.java').read_text(encoding='utf-8')
ok('\"cinema_letter_tomorrow\"' in plan, 'soundtrack must be registered in game audio resolver')
print('PASS:',checks,'v4.6.6 narrative, memory, icon and audio asset assertions')
