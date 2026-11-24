#!/usr/bin/env python3
"""Visual/compatibility regression for stage 3. Does NOT test Android rendering."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parent.parent;A=ROOT/'android/assets';ART=ROOT/'art_source/world_stage3'
# v3.7 adds exactly the versioned animation atlases and contact-shadow texture.
# Historical world-art tests still reject missing old assets or unexpected additions.
V37_MANIFEST = ROOT / 'docs/CHARACTER_POLISH_V3.7_ASSETS.json'
V37_ALLOWED = {entry['path'].removeprefix('android/assets/')
               for entry in json.loads(V37_MANIFEST.read_text())['assets']} if V37_MANIFEST.exists() else set()
OLD=json.loads((ROOT/'docs/ASSET_SHA256_V3.4.json').read_text())['files']
M=json.loads((ART/'stage3_manifest.json').read_text())
CHECKS=0
def ok(v,msg):
 global CHECKS
 CHECKS+=1
 if not v:raise AssertionError(msg)
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
mapnames=[x['name'] for x in M['maps']];propnames=[x['name'] for x in M['props']]
ok(mapnames==['starfall_village','star_path','gua_kristal','lantern_field','hutan_bisik'],'Unexpected map shortlist')
ok(len(propnames)==len(set(propnames))==36,'Wrong prop shortlist')
changed={'maps/'+n+'.png' for n in mapnames}|{'props/'+n+'.png' for n in propnames}
actual={str(f.relative_to(A)) for f in A.rglob('*') if f.is_file()}
ok(set(OLD)<=actual and actual-set(OLD)==V37_ALLOWED,f'Runtime asset set changed: added={actual-set(OLD)-V37_ALLOWED} removed={set(OLD)-actual}')
stage4=set()
if (ROOT/'art_source/world_stage4/stage4_manifest.json').exists():
 stage4manifest=json.loads((ROOT/'art_source/world_stage4/stage4_manifest.json').read_text())
 stage4={'maps/'+m['name']+'.png' for m in stage4manifest['maps']}|{'props/'+p['name']+'.png' for p in stage4manifest['props']}
for name,oldhash in OLD.items():
 f=A/name;ok(f.is_file(),'Missing runtime asset '+name)
 ok(sha(f)!=oldhash if name in changed else (True if name in stage4 else sha(f)==oldhash),('Not modified: ' if name in changed else 'Unexpected modification: ')+name)
for entry in M['maps']:
 name=entry['name'];p=A/'maps'/f'{name}.png';baseline=ART/'v34_unmodified/maps'/f'{name}.png'
 ok(baseline.exists() and sha(baseline)==OLD['maps/'+name+'.png'],'Invalid baseline map '+name)
 with Image.open(p) as a, Image.open(baseline) as b:
  ok(a.size==b.size,'Map resized: '+name)
  ok(a.info.get('world_art_pass')=='v3.5-stage3','Missing runtime art tag '+name)
  ok(ImageChops.difference(a.convert('RGB'),b.convert('RGB')).getbbox() is not None,'No pixel differences '+name)
 ok(entry['modified_pixels']>300000,'Insufficient map art changes '+name)
 for label in ['00_art_direction','01_surface_materials','02_environment_landmarks','03_path_edges_and_reflections','04_local_light']:
  f=ART/'editable_layers'/name/(label+'.png');ok(f.exists(),'Missing editable layer '+str(f))
  with Image.open(f) as im:ok(im.mode=='RGBA' and list(im.size)==entry['dimensions'],'Wrong editable layer '+str(f))
for entry in M['props']:
 name=entry['name'];p=A/'props'/f'{name}.png';baseline=ART/'v34_unmodified/props'/f'{name}.png'
 ok(baseline.exists() and sha(baseline)==OLD['props/'+name+'.png'],'Invalid baseline prop '+name)
 with Image.open(p) as a,Image.open(baseline) as b:
  ok(a.size==b.size,'Prop resized '+name)
  ok(a.convert('RGBA').getchannel('A').tobytes()==b.convert('RGBA').getchannel('A').tobytes(),'Prop silhouette/collision art changed '+name)
 ok(entry['modified_pixels']>0,'No prop changes '+name)
 ok(sha(p)==entry['sha256'],'Manifest hash out of sync '+name)
for name in ['plaza','taman_kota','cafe','riverside','dermaga','bukit_bintang','memory_garden','eternal_garden']:
 ok(sha(A/'maps'/f'{name}.png')==OLD['maps/'+name+'.png'],'Previous stage map changed: '+name)
for file in ('data/maps.json','data/props.json','data/story.json','data/quests.json','data/memory_book.json'):
 ok(sha(A/file)==OLD[file],'Collision or story changed: '+file)
aud=[k for k in OLD if k.startswith('audio/') and k.endswith(('.ogg','.wav','.mp3'))]
ok(len(aud)==86,'Audio inventory changed')
for k in aud:ok(sha(A/k)==OLD[k],'Audio changed '+k)
java=(ROOT/'core/src/main/java/com/arlandsofia/olu/OluGame.java').read_text()
ok(any(f'VERSION = "{v}"' in java for v in ('3.6.0','3.7.0')),'Game version mismatch')
ok(any(f"appVersionName = '{v}'" in (ROOT/'build.gradle').read_text() for v in ('3.6.0','3.7.0')),'Gradle version mismatch')
print(f'STAGE3 PASS: {CHECKS} checks | 5 maps, 36 modified props, 25 transparent editable layers | 86 original audio preserved | full map/story/collision binary-identical')
