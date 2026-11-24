#!/usr/bin/env python3
"""Stage 2 preservation + real pixel-change integrity (headless, NOT Android FPS)."""
import hashlib, json
from pathlib import Path
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parent.parent
# v3.7 adds exactly the versioned animation atlases and contact-shadow texture.
# Historical world-art tests still reject missing old assets or unexpected additions.
V37_MANIFEST = ROOT / 'docs/CHARACTER_POLISH_V3.7_ASSETS.json'
V37_ALLOWED = {entry['path'].removeprefix('android/assets/')
               for entry in json.loads(V37_MANIFEST.read_text())['assets']} if V37_MANIFEST.exists() else set()
A=ROOT/'android/assets'
ART=ROOT/'art_source/world_stage2'
OLD=json.loads((ROOT/'docs/ASSET_SHA256_V3.3.json').read_text())['files']
M=json.loads((ART/'stage2_manifest.json').read_text())
CHECKS=0

def ok(condition,reason):
    global CHECKS
    CHECKS+=1
    if not condition:raise AssertionError(reason)

def sha(file):return hashlib.sha256(file.read_bytes()).hexdigest()

names=[x['name'] for x in M['maps']]
props=[x['name'] for x in M['props']]
ok(names==['riverside','dermaga','bukit_bintang','memory_garden','eternal_garden'],'wrong stage 2 maps')
ok(len(props)==len(set(props))==30,'wrong number of stage 2 props')
changed=set('maps/'+s+'.png' for s in names)|set('props/'+s+'.png' for s in props)
new_files={str(f.relative_to(A)) for f in A.rglob('*') if f.is_file()}
ok(set(OLD)<=new_files and new_files-set(OLD)==V37_ALLOWED,'Unexpected runtime asset removal/addition!')
stage3=set()
if (ROOT/'art_source/world_stage3/stage3_manifest.json').exists():
 stage3manifest=json.loads((ROOT/'art_source/world_stage3/stage3_manifest.json').read_text())
 stage3={'maps/'+m['name']+'.png' for m in stage3manifest['maps']}|{'props/'+p['name']+'.png' for p in stage3manifest['props']}
stage4=set()
if (ROOT/'art_source/world_stage4/stage4_manifest.json').exists():
 stage4manifest=json.loads((ROOT/'art_source/world_stage4/stage4_manifest.json').read_text())
 stage4={'maps/'+m['name']+'.png' for m in stage4manifest['maps']}|{'props/'+p['name']+'.png' for p in stage4manifest['props']}
for key,oldhash in OLD.items():
    file=A/key
    ok(file.is_file(),'Missing original runtime asset: '+key)
    ok((sha(file)!=oldhash) if key in changed else (True if key in stage3 or key in stage4 else sha(file)==oldhash),
       ('Expected changed' if key in changed else 'Unexpected change')+': '+key)
for entry in M['maps']:
    key=entry['name'];f=A/'maps'/(key+'.png');prior=ART/'v33_unmodified/maps'/(key+'.png')
    ok(prior.exists() and sha(prior)==OLD['maps/'+key+'.png'],'Missing exact v3.3 baseline map '+key)
    with Image.open(prior) as x, Image.open(f) as y:
        ok(x.size==y.size,'map dimensions changed '+key)
        ok(y.info.get('world_art_pass')=='v3.4-stage2','missing stage 2 runtime tag: '+key)
        ok(ImageChops.difference(x.convert('RGB'),y.convert('RGB')).getbbox() is not None,
           'No visible pixel changes in '+key)
    ok(entry['modified_pixels']>=150000, 'Insufficient pixel changes '+key)
    for label in ('00_ground_palette','01_water_and_garden','02_landmark_details','03_atmosphere'):
        file=ART/'editable_layers'/key/(label+'.png')
        ok(file.is_file(),'Missing editable layer '+str(file))
        with Image.open(file) as layer:ok(layer.mode=='RGBA' and list(layer.size)==entry['size'], 'Invalid layer: '+str(file))
for item in M['props']:
    n=item['name'];f=A/'props'/(n+'.png');old=ART/'v33_unmodified/props'/(n+'.png')
    ok(old.exists() and sha(old)==OLD['props/'+n+'.png'],'Missing original prop '+n)
    with Image.open(f) as a,Image.open(old) as b:
        ok(a.size==b.size,'Prop dimension changes '+n)
        ok(a.convert('RGBA').getchannel('A').tobytes()==b.convert('RGBA').getchannel('A').tobytes(), 'Alpha silhouette changed '+n)
    ok(item['file_sha256']==sha(f),'Prop checksum differs from manifest '+n)
for k in ('data/maps.json','data/props.json','data/quests.json','data/story.json','data/memory_book.json'):
    ok(sha(A/k)==OLD[k],'Gameplay or collision data unexpectedly modified: '+k)
audios=[k for k in OLD if k.startswith('audio/') and k.endswith(('.ogg','.wav','.mp3'))]
ok(len(audios)==86,'Expected 86 unchanged sound files')
for k in audios:ok(sha(A/k)==OLD[k],'Audio lost or modified: '+k)
for key in ('plaza','taman_kota','cafe'):
    ok(sha(A/'maps'/(key+'.png'))==OLD['maps/'+key+'.png'],'Stage 1 map not preserved '+key)
java=(ROOT/'core/src/main/java/com/arlandsofia/olu/OluGame.java').read_text()
ok(any(f'VERSION = "{v}"' in java for v in ("3.4.0","3.5.0","3.6.0","3.7.0")),'Java game version stale')
ok(any(f"appVersionName = '{v}'" in (ROOT/'build.gradle').read_text() for v in ("3.4.0","3.5.0","3.6.0","3.7.0")),"Gradle version stale")
print(f'STAGE2 PASS: {CHECKS} checks | {len(names)} runtime maps, {len(props)} props | 20 editable master PNG | 86 audio preserved | collision/story unchanged')
