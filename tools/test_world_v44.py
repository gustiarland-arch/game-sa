#!/usr/bin/env python3
"""Offline v4.4 visual/regression contract; independent of current workspace path."""
from pathlib import Path
import sys,json,hashlib
from PIL import Image, ImageChops
ROOT=Path(__file__).resolve().parent.parent
A=ROOT/'android/assets';SRC=ROOT/'art_source/world_v44'
m=json.loads((A/'data/maps.json').read_text())
d=json.loads((A/'data/props.json').read_text())['props']
b=json.loads((SRC/'v43_manifest.json').read_text())
manifest=json.loads((ROOT/'docs/V44_WORLD_MANIFEST.json').read_text())
from importlib.machinery import SourceFileLoader
mod=SourceFileLoader('w44',str(ROOT/'tools/world_redesign_v44.py')).load_module()
checks=0
def ok(condition,message):
 global checks
 checks+=1
 if not condition: raise AssertionError(message)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for file,hash0 in b['maps'].items():
 path=A/'maps'/file
 ok(path.exists(),'missing map '+file)
 with Image.open(path) as img:img.verify()
 ok((digest(path)==manifest['maps'][file[:-4]] if file[:-4] in mod.KEYS else digest(path)==hash0),'unexpected map change '+file)
for path0,h in b['audio'].items():
 path=A/path0
 ok(path.exists(),'missing audio '+path0)
 ok(digest(path)==h,'changed audio '+path0)
for area in mod.KEYS:
 original=b['geometry'][area];current=m['areas'][area]
 old_props=original['props'];new_props=current['props']
 ok(len(old_props)==len(new_props),'prop count '+area)
 for key in original.keys():
  if key=='props':continue
  ok(current.get(key)==original[key],f'changed geometry {area}:{key}')
 for old,new in zip(old_props,new_props):
  for key in old:
   if key!='type':ok(new.get(key)==old[key],f'changed anchor {area}:{key}')
  expected='v44_'+old['type'] if old['type'] in mod.SELECT[area] else old['type']
  ok(new['type']==expected,'prop type mismatch '+area)
  if expected!=old['type']:
   od=b['props'][old['type']];nd=d[expected]
   ok({k:v for k,v in od.items() if k!='image'}=={k:v for k,v in nd.items() if k!='image'},'prop collision changed '+expected)
   with Image.open(SRC/'baseline_props'/(old['type']+'.png')) as oi,Image.open(A/nd['image']) as ni:
    oi,ni=oi.convert('RGBA'),ni.convert('RGBA')
    ok(oi.size==ni.size,'size changed '+expected)
    ok(ImageChops.difference(oi.getchannel('A'),ni.getchannel('A')).getbbox() is None,'alpha mask changed '+expected)
 with Image.open(SRC/'baseline_maps'/(area+'.png')) as base,Image.open(A/'maps'/(area+'.png')) as image:
  base,image=base.convert('RGBA'),image.convert('RGBA')
  ok(base.size==image.size,'map image size '+area)
  ok(ImageChops.difference(base.convert('RGB'),image.convert('RGB')).getbbox() is not None,'no visual delta '+area)
  for layer in ('materials','landmarks','details','lighting'):
   with Image.open(SRC/'editable_layers'/(area+'_'+layer+'.png')) as im:
    ok(im.size==base.size,'bad editable layer '+area+layer)
    ok(im.mode=='RGBA','not RGBA layer')
for name,hash0 in manifest['active_data_sha'].items():
 ok(digest(A/name)==hash0,'unexpected data change '+name)
for typ,hash0 in manifest['prop_types'].items():
 ok(digest(A/'props'/f'{typ}.png')==hash0,'changed new prop '+typ)
ok(m['_maps_v44']['areas']==list(mod.KEYS),'missing v44 mapping')
print('WORLD V4.4 OK:',checks,'checks; 4 edited maps; 18 preserved; audio:',len(b['audio']))
