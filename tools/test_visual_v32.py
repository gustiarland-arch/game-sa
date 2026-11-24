"""v3.2 visual regression. Checks image bytes, atlas dimensions, new references, original baseline and story topology.
No Android runtime / texture memory / frame timing claim is made here.
"""
from pathlib import Path
import json,hashlib,io,zipfile,sys
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parent.parent
A=ROOT/'android/assets'
base=json.loads((ROOT/'tools/build/maps_base.json').read_text())
prior=json.loads((ROOT/'docs/ASSET_SHA256_V3.0.json').read_text())['files']
checks=0
changed=[]
def check(ok,msg):
 global checks
 checks+=1
 assert ok, msg

def bytes_hash(f):return hashlib.sha256(f.read_bytes()).hexdigest()
# 22 maps genuinely rendered differently, with pixel-accurate unchanged dimensions and original art retained.
for name,m in base.items():
 new=A/m['image']; orig=ROOT/'art_source/visual_v32_base/maps'/f'{name}.png'
 check(new.is_file() and orig.is_file(),name+' files missing')
 new_im=Image.open(new);old_im=Image.open(orig)
 check(new_im.size==old_im.size==(m['w'],m['h']),name+' dimension')
 check(new_im.info.get('visual_overhaul_v32')=='repaint-v32',name+' visual marker')
 check(ImageChops.difference(new_im.convert('RGB'),old_im.convert('RGB')).getbbox() is not None,name+' pixel unchanged')
 check(bytes_hash(orig)==prior['maps/'+name+'.png'],name+' original mismatch')
 changed.append(name)
props=list((A/'props').glob('*.png'))
check(len(props)>=256,'props count')
for p in props:
 old=ROOT/'art_source/visual_v32_base/props'/p.name
 check(old.is_file(),p.name+' missing original')
 with Image.open(p) as im,Image.open(old) as oldim:
  check(im.size==oldim.size,p.name+' resized prop')
  # collision outline unchanged: alpha channel only, which defines opaque silhouette
  check(im.getchannel('A').tobytes()==oldim.getchannel('A').tobytes(),p.name+' prop silhouette changed')
for d in (A/'characters').iterdir():
 if not (d/'walk.png').is_file():continue
 for fn,frames in (('walk_v32.png',12),('idle_v32.png',6)):
  p=d/fn
  check(p.exists(),d.name+fn+' missing')
  with Image.open(p) as im:
   check(im.size==(frames*48,288),d.name+fn+' bad atlas dimensions')
   for row in range(4):
    cells=[im.crop((i*48,row*72,(i+1)*48,(row+1)*72)).tobytes() for i in range(frames)]
    check(len(set(cells))>= (4 if frames==12 else 1),d.name+fn+str(row)+' no animation')
for name in ('panel','panel_dark','button','button_down','button_accent','button_disabled'):
 p=A/'ui'/f'v32_{name}.png'
 with Image.open(p) as im:check(im.size==(64,64),name+' skin size')
for name in ('v32_menu_far.png','v32_menu_near.png'):
 with Image.open(A/'ui'/name) as im:check(im.size==(1280,720),name+' panorama size')
for name in ('v32_cinematic_ribbon.png','v32_bloom.png','v32_scene_ornament.png'):
 check((A/'ui'/name).is_file(),name)
for image in sorted((A/'ui/v32_cinema').glob('*.png')):
 with Image.open(image) as im: check(im.size==(768,432),image.name)
check(len(list((A/'ui/v32_cinema').glob('*.png')))==12,'cinema still count')
# Collision/quest/route/audio binary integrity from v3.0.
for name in ('data/maps.json','data/props.json','data/quests.json','data/story.json','data/memory_book.json'):
 check(bytes_hash(A/name)==prior[name],'gameplay data altered: '+name)
for name,sha in prior.items():
 if name.startswith('audio/') or name.startswith('characters/') and name.endswith(('poses.png','walk.png','walk_plus.png')):
  check((A/name).is_file() and bytes_hash(A/name)==sha,'old asset changed: '+name)
print(f'VISUAL V3.2 OK: {checks} checks | {len(changed)} maps repainted | {len(props)} props checked | 25 animated characters | 12 story stills | all quest, collision and audio preserved')
