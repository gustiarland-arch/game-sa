#!/usr/bin/env python3
"""Stage-4 integrity gate. Checks exact v3.5 baselines, unchanged data/audio,
9 genuinely changed maps, 57 alpha-preserving props and 36 editor layers.
Tests source files only; does not assert Android runtime/graphics FPS.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[1];A=ROOT/'android/assets'
# v3.7 adds exactly the versioned animation atlases and contact-shadow texture.
# Historical world-art tests still reject missing old assets or unexpected additions.
V37_MANIFEST = ROOT / 'docs/CHARACTER_POLISH_V3.7_ASSETS.json'
V37_ALLOWED = {entry['path'].removeprefix('android/assets/')
               for entry in json.loads(V37_MANIFEST.read_text())['assets']} if V37_MANIFEST.exists() else set()
ART=ROOT/'art_source/world_stage4';BASE=ART/'v35_unmodified'
PRIOR=json.loads((ROOT/'docs/ASSET_SHA256_V3.5.json').read_text())['files']
CURRENT={str(p.relative_to(A)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(A.rglob('*')) if p.is_file()}
M=json.loads((ART/'stage4_manifest.json').read_text())
COUNT=0
def ok(v,msg):
 global COUNT
 COUNT+=1
 if not v:raise AssertionError(msg)
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
mapnames=[m['name'] for m in M['maps']];propnames=[p['name'] for p in M['props']]
EXPECTED=['jalan_kota','perumahan','perpustakaan','arcade','toko_bunga','arland_room','sofia_room','dapur','ruang_arsip']
ok(mapnames==EXPECTED,'9 unchanged map identifiers expected')
ok(len(propnames)==len(set(propnames))==57,'57 unique stage4 prop identifiers expected')
changed={f'maps/{n}.png' for n in mapnames}|{f'props/{n}.png' for n in propnames}
ok(set(PRIOR)<=set(CURRENT) and set(CURRENT)-set(PRIOR)==V37_ALLOWED,'Runtime asset inventory changed beyond explicitly catalogued v3.7 atlas additions')
for path,old in PRIOR.items():
 ok(CURRENT[path]!=old if path in changed else CURRENT[path]==old,
    ('Asset did not change: ' if path in changed else 'Unexpected old asset changed: ')+path)
for entry in M['maps']:
 name=entry['name'];old=BASE/'maps'/f'{name}.png';new=A/'maps'/f'{name}.png'
 ok(old.is_file() and sha(old)==PRIOR[f'maps/{name}.png'],'Missing exact v3.5 baseline map '+name)
 with Image.open(old) as b,Image.open(new) as a:
  ok(a.size==b.size,'Map size changed: '+name)
  ok(a.info.get('world_art_pass')=='v3.6-stage4','Missing stage4 tag: '+name)
  ok(ImageChops.difference(a.convert('RGB'),b.convert('RGB')).getbbox() is not None,'No pixel difference: '+name)
 ok(entry['modified_pixels']>40000,'Map pixel change too small '+name)
 ok(entry['current_sha256']==sha(new),'Map manifest mismatch '+name)
 for layer in entry['layers']:
  f=ART/'editable_layers'/name/(layer+'.png')
  ok(f.is_file(),'Missing editable layer '+str(f))
  with Image.open(f) as im:ok(im.mode=='RGBA' and list(im.size)==entry['size'], 'Layer size/mode incorrect '+str(f))
for entry in M['props']:
 name=entry['name'];old=BASE/'props'/f'{name}.png';new=A/'props'/f'{name}.png'
 ok(old.is_file() and sha(old)==PRIOR[f'props/{name}.png'],'Missing exact prop baseline '+name)
 with Image.open(old) as b,Image.open(new) as a:
  ok(a.size==b.size,'Prop dimensions changed '+name)
  ok(a.convert('RGBA').getchannel('A').tobytes()==b.convert('RGBA').getchannel('A').tobytes(), 'Prop alpha silhouette changed '+name)
 ok(entry['modified_pixels']>0,'No prop pixel change '+name)
 ok(entry['current_sha256']==sha(new),'Prop hash mismatch '+name)
for k in ('data/maps.json','data/props.json','data/quests.json','data/story.json','data/memory_book.json'):
 ok(CURRENT[k]==PRIOR[k],'Gameplay/quest/collision changed '+k)
all_music=[x for x in PRIOR if x.startswith('audio/') and x.endswith(('.ogg','.wav','.mp3'))]
ok(len(all_music)==86,'86 soundtrack assets expected')
for p in all_music:ok(CURRENT[p]==PRIOR[p],'Audio modified unexpectedly '+p)
for f in ROOT.glob('docs/preview/*'):
 ok(f.is_file(),'Unexpected broken preview directory')
java=(ROOT/'core/src/main/java/com/arlandsofia/olu/OluGame.java').read_text()
gradle=(ROOT/'build.gradle').read_text()
ok(any(f'VERSION = "{v}"' in java for v in ('3.6.0','3.7.0')),'Incorrect game version')
ok(any(f"appVersionName = '{v}'" in gradle and f'appVersionCode = {code}' in gradle for v,code in (('3.6.0',36),('3.7.0',37))),'Incorrect Gradle version')
cleanup=json.loads((ROOT/'docs/CLEANUP_AUDIT_V3.6.json').read_text())
ok(cleanup['applied'] and cleanup['files']>0,'Cleanup has not run')
for entry in cleanup['removed_or_proposed']:
 ok(not (ROOT/entry['file']).exists(),'Trash reappeared: '+entry['file'])
 ok(not entry['file'].startswith(('android/','art_source/','core/','gradle/')),'Unsafe cleanup location')
print(f'STAGE4 PASS: {COUNT} source assertions | 9 maps, 57 alpha-preserving prop sprites, 36 RGBA layers | 86 identical audio | all original asset paths retained')
