#!/usr/bin/env python3
"""v4.3 regressions: original layout, collision, quests, 9 handcrafted maps, 86 audio unchanged."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent;A=ROOT/'android/assets';D=A/'data';SOURCE=ROOT/'art_source/world_v43'
REF=Path('/mnt/data/ArlandSofia_v4.2_work/ArlandSofia')
# Reference packaged directly with project so the test remains portable.
REF=ROOT/'art_source/world_v43/source_v42_geometry.json'
expected=json.loads(REF.read_text());m=json.loads((D/'maps.json').read_text())['areas'];props=json.loads((D/'props.json').read_text())['props']
hashes=json.loads((ROOT/'docs/V43_WORLD_MANIFEST.json').read_text());n=0

def ck(flag,label):
 global n;n+=1
 if not flag:raise AssertionError('v4.3 '+label)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
ck(len(m)==22,'22 maps')
for area in ['plaza','taman_kota','cafe','riverside']:
 old=expected['areas'][area];new=m[area]
 for key in ('w','h','spawn','walls','ellipses','doors','gates','water','examine','animals'):
  ck(old.get(key)==new.get(key),area+' unchanged '+key)
 ck(len(old['props'])==len(new['props']),area+' prop count')
 for index,(o,v) in enumerate(zip(old['props'],new['props'])):
  ck((o['x'],o['y'])==(v['x'],v['y']),area+' prop anchor '+str(index))
  olddef=expected['prop_defs'][o['type']]
  newdef=props[v['type']]
  ck((olddef['cw'],olddef['ch'],olddef['layer'])==(newdef['cw'],newdef['ch'],newdef['layer']),area+' prop hitbox/depth '+str(index))
 img=A/'maps'/f'{area}.png';base=SOURCE/'baseline_maps'/f'{area}.png'
 ck(sha(img)==hashes['areas'][area] and sha(img)!=sha(base),area+' new art checksum')
 with Image.open(img) as x, Image.open(base) as b:
  ck(x.size==b.size==(new['w'],new['h']),area+' size')
  ck(x.verify() is None,area+' PNG CRC')
 for part in ('terrain','detail','decor','lighting'):
  with Image.open(SOURCE/'editable_layers'/f'{area}_{part}.png') as layer:
   ck(layer.size==(new['w'],new['h']) and layer.mode=='RGBA',area+' editable '+part)
# Future v4.4 intentionally paints four of the originally untouched v4.3 maps.
# Their new hashes are pinned in the v4.4 manifest, not silently exempted.
v44=ROOT/'docs/V44_WORLD_MANIFEST.json'
allowed=json.loads(v44.read_text())['maps'] if v44.exists() and '_maps_v44' in json.loads((D/'maps.json').read_text()) else {}
for name,h in expected['untouched_map_hashes'].items():
 ck(sha(A/'maps'/(name+'.png'))==allowed.get(name,h),'untouched/authorized newer map '+name)
for name,h in expected['audio_hashes'].items():ck(sha(A/'audio'/name)==h,'untouched audio '+name)
for fname,h in expected['content_hashes'].items():ck(sha(D/fname)==h,'unchanged story/save content '+fname)
for key in hashes['new_prop_types']:
 ck(key in props and (A/props[key]['image']).is_file(),'prop registered '+key)
 origin=SOURCE/'baseline_props'/(key[4:]+'.png')
 with Image.open(origin) as old, Image.open(A/props[key]['image']) as now:
  ck(old.size==now.size and old.getchannel('A').tobytes()==now.getchannel('A').tobytes(),'alpha silhouette preserved '+key)
print('V4.3 WORLD PASS:',n,'checks; 4 environments, 20 prop variants, 18 protected maps and 86 audio')
