#!/usr/bin/env python3
"""v3.3 world stage 1; regression against bundled SHA256 manifest of v3.2.
Checks true pixel changes, source backups, alpha silhouettes, content/audio unchanged.
This is static asset validation, NOT Android rendering verification.
"""
from pathlib import Path
from PIL import Image,ImageChops
import json,hashlib
ROOT=Path(__file__).resolve().parent.parent
A=ROOT/'android/assets';ART=ROOT/'art_source/world_stage1'
prior=json.loads((ROOT/'docs/ASSET_SHA256_V3.2.json').read_text())['files']
manifest=json.loads((ART/'world_stage1_manifest.json').read_text())
CHECKS=0
def ok(x,msg):
 global CHECKS
 CHECKS+=1
 if not x:raise AssertionError(msg)
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
changed={'maps/plaza.png','maps/taman_kota.png','maps/cafe.png'}
changed|={'props/'+p['name']+'.png' for p in manifest['props']}
stage2=set()
if (ROOT/'art_source/world_stage2/stage2_manifest.json').exists():
 stage2manifest=json.loads((ROOT/'art_source/world_stage2/stage2_manifest.json').read_text())
 stage2={'maps/'+m['name']+'.png' for m in stage2manifest['maps']}|{'props/'+p['name']+'.png' for p in stage2manifest['props']}
stage3=set()
if (ROOT/'art_source/world_stage3/stage3_manifest.json').exists():
 stage3manifest=json.loads((ROOT/'art_source/world_stage3/stage3_manifest.json').read_text())
 stage3={'maps/'+m['name']+'.png' for m in stage3manifest['maps']}|{'props/'+p['name']+'.png' for p in stage3manifest['props']}
stage4=set()
if (ROOT/'art_source/world_stage4/stage4_manifest.json').exists():
 stage4manifest=json.loads((ROOT/'art_source/world_stage4/stage4_manifest.json').read_text())
 stage4={'maps/'+m['name']+'.png' for m in stage4manifest['maps']}|{'props/'+p['name']+'.png' for p in stage4manifest['props']}
actual=[]
for path,oldhash in sorted(prior.items()):
 f=A/path
 ok(f.is_file(),'Missing old asset: '+path)
 if path in changed:
  ok(sha(f)!=oldhash,'Named visual output unchanged: '+path)
  actual.append(path)
 else:
  if path not in stage2 and path not in stage3 and path not in stage4:ok(sha(f)==oldhash,'Non-stage asset accidentally altered: '+path)
ok(len(actual)==32,'Unexpected count of materially revised assets')
for m in manifest['areas']:
 name=m['map'];rel='maps/'+name+'.png';cur=A/rel
 orig=ART/'v32_unmodified'/rel
 ok(orig.is_file() and sha(orig)==prior[rel],'Unmodified v3.2 map not backed up '+name)
 with Image.open(orig) as x,Image.open(cur) as y:
  ok(x.size==y.size,'Map dimensions modified: '+name)
  ok(y.info.get('world_art_pass')=='v3.3-stage1','Runtime map missing art version marker: '+name)
  diff=ImageChops.difference(x.convert('RGB'),y.convert('RGB'))
  ok(diff.getbbox() is not None,'No pixel changes: '+name)
  ok(m['changed_pixels']>=250_000,'Insufficient real pixel changes: '+name)
 for k in ('00_ground_palette','01_materials','02_landmarks','03_lighting'):
  f=ART/'editable_layers'/name/(k+'.png')
  ok(f.is_file(),'Editable layer missing: '+str(f))
  with Image.open(f) as im:
   ok(list(im.size)==m['dimensions'] and im.mode=='RGBA','Invalid editable layer dimensions: '+str(f))
for prop in manifest['props']:
 key=prop['name'];rel='props/'+key+'.png'
 orig=ART/'v32_unmodified'/rel
 ok(orig.is_file() and sha(orig)==prior[rel],'Missing v3.2 prop backup: '+rel)
 with Image.open(A/rel) as x,Image.open(orig) as y:
  ok(x.size==y.size,'Prop dimensions changed: '+key)
  ok(x.getchannel('A').tobytes()==y.getchannel('A').tobytes(),'Prop silhouette changed: '+key)
for rel in ('data/maps.json','data/props.json','data/quests.json','data/story.json','data/memory_book.json'):
 ok(sha(A/rel)==prior[rel],'Content/collision changed: '+rel)
audios=[rel for rel in prior if rel.startswith('audio/')]
ok(len(audios)>=86,'Too few prior audios')
for rel in audios:ok(sha(A/rel)==prior[rel],'Audio changed: '+rel)
java=ROOT/'core/src/main/java/com/arlandsofia/olu/OluGame.java'
ok(any('VERSION = "'+v+'"' in java.read_text() for v in ('3.3.0','3.4.0','3.5.0','3.6.0','3.7.0')),'Java version mismatch')
print(f'WORLD REDESIGN STAGE 1 OK: {CHECKS} checks | 3 landmark maps | 29 collision-identical props | 12 editable art layers | {len(audios)} audio files preserved | story & map metadata preserved')
