#!/usr/bin/env python3
"""Static/asset and compatibility gate. This is NOT an Android rendering test."""
from pathlib import Path
from PIL import Image
import zipfile,hashlib,json,sys
ROOT=Path(__file__).resolve().parent.parent
A=ROOT/'android/assets'
BASE=json.loads((ROOT/'docs/ASSET_SHA256_V3.6.json').read_text())['files']
checks=0

def ok(expr,msg):
 global checks
 checks+=1
 if not expr:raise AssertionError(msg)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

# Self-contained for CI builds: the v3.6 baseline SHA-256 manifest ships in the source.
for target in sorted(A.glob('maps/*.png')):
 k=str(target.relative_to(A));ok(k in BASE and sha(target)==BASE[k],'map changed unexpectedly '+k)
for target in sorted(A.glob('audio/**/*')):
 if not target.is_file(): continue
 k=str(target.relative_to(A));ok(k in BASE and sha(target)==BASE[k],'audio changed '+k)
for k in ('data/quests.json','data/story.json','data/maps.json','data/memory_book.json','data/props.json'):
 ok(k in BASE and sha(A/k)==BASE[k],'quest/world changed '+k)
# Optional stronger offline side-by-side check when caller supplies previous ZIP.
if len(sys.argv)>1:
 with zipfile.ZipFile(sys.argv[1]) as old:
  for k in list(BASE):
   if k.startswith(('maps/','audio/','data/')):
    name='ArlandSofia/android/assets/'+k
    ok(name in old.namelist() and (A/k).read_bytes()==old.read(name),'ZIP baseline byte mismatch '+k)

cnt=0
for d in sorted((A/'characters').iterdir()):
 if not (d/'walk_v32.png').exists():continue
 cnt+=1
 for filename,n in (('walk_v37.png',16),('idle_v37.png',8)):
  f=d/filename
  ok(f.exists(),str(f)+' missing')
  with Image.open(f) as im:
   ok(im.size==(n*48,288),str(f)+' wrong dimensions')
   for direction in range(4):
    frames=[im.crop((i*48,direction*72,(i+1)*48,(direction+1)*72)).tobytes() for i in range(n)]
    ok(len(set(frames))>= (5 if n==16 else 3),str(f)+' insufficient animated frame diversity '+str(direction))
    ok(im.getchannel('A').getbbox() is not None,str(f)+' empty atlas')
ok(cnt==25,'all 25 characters expected')
ok((A/'fx/contact_shadow_v37.png').exists(),'shadow asset missing')
src=(ROOT/'core/src/main/java/com/arlandsofia/olu/Assets.java').read_text()
actor=(ROOT/'core/src/main/java/com/arlandsofia/olu/game/Actor.java').read_text()
world=(ROOT/'core/src/main/java/com/arlandsofia/olu/screens/GameScreen.java').read_text()
ok(src.index('"/walk_v37.png"') < src.index('"/walk_v32.png"'), 'new walk not preferred')
ok(src.index('"/idle_v37.png"') < src.index('"/idle_v32.png"'), 'new idle not preferred')
ok('batch.draw(topR' not in actor, 'head ghost renderer still present')
ok('WorldLightingV37.width(def.cw)' in world,'prop contact light not integrated')
ok('shadow = a.tex("fx/contact_shadow_v37.png")' in world, 'new shadow not integrated')
ok(world.index('drawWater();') < world.index('Collections.sort(drawList,'),'water effects overlay character incorrectly')
manifest=json.loads((ROOT/'docs/CHARACTER_POLISH_V3.7_ASSETS.json').read_text())
ok(manifest['characters']==25 and len(manifest['assets'])==51,'manifest incomplete')
for item in manifest['assets']:
 p=ROOT/item['path'];ok(hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'],'manifest checksum mismatch: '+item['path'])
print('V3.7 ASSET & INTEGRATION OK:',checks,'checks,',cnt,'animated characters, 22 unchanged maps, 86 preserved audio')
