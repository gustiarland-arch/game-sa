#!/usr/bin/env python3
"""Full source v4.2 regression: actual rendered image bytes and geometry safety."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent.parent
A=R/'android/assets';D=A/'data'
base=json.loads((R/'docs/V42_BASELINE_AUDIT.json').read_text())
manifest=json.loads((R/'docs/V42_WORLD_MANIFEST.json').read_text())
areas=json.loads((D/'maps.json').read_text())['areas']
v43manifest=json.loads((R/'docs/V43_WORLD_MANIFEST.json').read_text())
v43=v43manifest['areas']
v44manifest=json.loads((R/'docs/V44_WORLD_MANIFEST.json').read_text())
v43.update(v44manifest['maps'])
props=json.loads((D/'props.json').read_text())['props']
checks=0

def check(c,msg):
 global checks
 checks+=1
 if not c:raise AssertionError('v4.2 '+msg)

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
check(len(areas)==22,'22 game maps');check(len(manifest['areas'])==13,'13 new visual passes');check(len(base['protected_authored_maps'])==9,'9 authored maps protected')
for n,h in base['protected_authored_maps'].items():
 check(sha(A/areas[n]['image'])==h,'protected v4 map '+n)
for name,info in manifest['areas'].items():
 img=A/info['runtimeImage'];src=R/'art_source/world_v42/baseline_maps'/f'{name}.png'
 check(src.exists() and img.exists(),'baseline and active image '+name)
 check(sha(src)==base['original_13_map_sha'][name],name+' frozen v4.1 baseline')
 check(sha(img)==v43.get(name,manifest['sha256'][name]),name+' active illustration hash matches active version manifest')
 check(sha(img)!=sha(src),name+' real changed bytes')
 with Image.open(src) as before,Image.open(img) as after:
  check(before.size==after.size==tuple(info['nativeResolution']),name+' world dimensions unchanged')
  b=np.asarray(before.convert('RGB').resize((160,120),Image.Resampling.NEAREST)).astype(np.int16)
  c=np.asarray(after.convert('RGB').resize((160,120),Image.Resampling.NEAREST)).astype(np.int16)
  percent=(abs(c-b)>5).any(axis=2).mean()
  check(percent>0.018,name+' meaningful image difference %.3f'%(percent))
 for rel in info['layers']:
  p=R/rel
  check(p.exists(),name+' editable layer exists '+str(p))
  with Image.open(p) as im:check(im.size==tuple(info['nativeResolution']) and im.mode=='RGBA',name+' editable transparent layer')
for name,h in base['other_data_sha'].items():
 check(sha(A/name)==v44manifest.get('active_data_sha',{}).get(name,v43manifest.get('active_data_sha',{}).get(name,h)), 'authorized version data/unaltered story '+name)
for name,h in base['original_audio_sha'].items():check(sha(A/name)==h,'unmodified audio '+name)
for k,meta in base['original_prop_schema'].items():
 check(k in props and [props[k]['cw'],props[k]['ch'],props[k]['layer'],props[k]['image']]==meta,'prop collision metadata '+k)
changed=0
for rel,h in base['v41_landmark_sha'].items():
 p=A/rel;src=R/'art_source/world_v42/baseline_props'/Path(rel).name
 check(p.exists() and src.exists(),'original + cleaned prop '+rel)
 check(sha(src)==h,'correct old sprite backup '+rel)
 with Image.open(p) as clean,Image.open(src) as old:
  check(clean.size==old.size and clean.mode=='RGBA','unchanged sprite size '+rel)
  c=np.asarray(clean.getchannel('A'));o=np.asarray(old.getchannel('A'))
  check(np.all(c<=o),'no opaque expansion '+rel)
  if np.any(c!=o):changed+=1
check(changed>=20,'at least 20 real prop alpha improvements; got '+str(changed))
print('V4.2 WORLD TEST PASS',checks,'assertions; 13 active maps / 39 editable layers / 9 authored maps unchanged /',changed,'landmark alpha improvements /',len(base['original_audio_sha']),'audio files unchanged')
