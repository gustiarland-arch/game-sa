#!/usr/bin/env python3
"""v4 map integration regression tests: real image bytes, doors, walls, quest, old assets."""
from pathlib import Path
from PIL import Image
import hashlib, json, sys, math
ROOT=Path(__file__).resolve().parent.parent;A=ROOT/'android/assets';D=A/'data'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def get(name):return json.loads((D/name).read_text())
maps=get('maps.json')['areas'];qs=get('quests.json');props=get('props.json')['props']
ref=json.loads((ROOT/'docs/MAPS_V4_BASELINE_SHA256.json').read_text())
cnt=0

def ck(flag,desc):
 global cnt;cnt+=1
 if not flag:raise AssertionError('v4 map check '+desc)

targets=list(ref['new_images']);
ck(len(targets)==9,'nine maps mapped');ck(len(maps)==22,'all 22 maps available')
ck(len(qs['steps'])==93,'93 story steps')
for a in targets:
 v=maps[a];img=A/v['image'];old=ROOT/'art_source/maps_v37_baseline'/f'{a}.png'
 ck(img.exists(),f'{a} runtime image exists');ck(old.exists(),f'{a} old background preserved')
 ck(sha(img)==sha(ROOT/'art_source/maps_v4_input'/f'{a}.png'),f'{a} new art copied unaltered')
 ck(sha(img)!=sha(old),f'{a} art actually changed')
 ck(v['w']==1200 and v['h']==896,f'{a} 1200x896 native dimensions')
 ck(Image.open(img).size==(1200,896),f'{a} readable image and dimensions')
 ck(len(v['walls'])>=5,f'{a} custom collision rectangles')
 ck(v['v4Layout']=='handcrafted_16bit',f'{a} marked V4')
 ck(v['props'] and all(x['type'].startswith('maps_v4_') for x in v['props']),f'{a} old duplicate props removed')
 ck(not any(x['type'] in ('door','bed_blue','flower_shelf','stove') for x in v['props']),f'{a} no old props double draw')
 sp=v['spawn'];ck(0<sp[0]<1200 and 0<sp[1]<896,f'{a} spawn in bounds')
 for p in v['props']:
  definition=props[p['type']];ck(definition['layer']=='sort' and definition['cw']==0 and definition['ch']==0, f'{a} image overlay is Y-sorted and noncolliding')
  with Image.open(A/definition['image']) as im:
   ck(im.mode=='RGBA' and im.getchannel('A').getextrema()[1]==255, f'{a} silhouette alpha overlay')
 for dr in v['doors']:
  x,y,w,h=dr['rect'];ck(0<=x<1200 and 0<=y<896 and x+w<=1200 and y+h<=896,f'{a} door region in image')
  ck(dr['to'] in maps,f'{a} exit destination exists')
  ck(dr['id'] in ref['doors'][a],f'{a} old portal id maintained')
 for z in v['examine']:
  ck(0<=z['x']<1200 and 0<=z['y']<896, f'{a} examine in bounds')
# v4.1 deliberately gives a new artistic pass to the other 13 backgrounds.
# All other previously protected assets, including all 9 supplied authored maps,
# remain SHA-identical. v4.1's separate test checks each intentional change.
v41areas=set(get('maps.json').get('_maps_v41',{}).get('areas',[]))
if not v41areas: v41areas=set(a for a,v in maps.items() if v.get('visualStyle')=='v4.1_romantic_scenery')
for name,expected in ref['untouched_asset_sha256'].items():
 if name.startswith('maps/') and Path(name).stem in v41areas:
  ck(sha(A/name)!=expected, f'new v4.1 art pass {name}')
 else:
  ck(sha(A/name)==expected,f'unchanged asset {name}')
for k,expected in ref['data_sha256'].items():ck(sha(D/k)==expected, f'unchanged data {k}')
ck(len(list((A/'audio/music').glob('*.ogg')))+len(list((A/'audio/ambience').glob('*.ogg')))+len(list((A/'audio/sfx').glob('*.wav')))==86,'all 86 audio preserved')
ck(qs.get('_maps_v4')=='maps_v4_upgrade.py','quest coordinate patch applied')
ck(qs['worldEvents'] and len(qs['worldEvents'])==14,'14 old events preserved')
# Every targeted event must use the same foot point as its interactable marker.
for e in qs['worldEvents']:
 if e['area'] not in targets:continue
 match=[t for t in qs['side'] if t['id']=='WE27_'+e['id'].upper()]
 ck(len(match)==1, 'world event marker '+e['id'])
 ck((e['x'],e['y'])==(match[0]['x'],match[0]['y']), 'world event/marker alignment '+e['id'])
print('V4 MAP AUDIT PASSED:',cnt,'assertions across 9 maps; 13 additional maps intentionally redesigned + 86 audio unchanged')
