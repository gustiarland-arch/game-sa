#!/usr/bin/env python3
"""v4.1 source-art + runtime collision + data-preservation regression audit."""
from pathlib import Path
from PIL import Image,ImageChops
import hashlib,json,sys
ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT/'art_source/world_v41/baseline_data'
MANIFEST=json.loads((ROOT/'docs/V41_BASELINE_SHA256.json').read_text())
A=ROOT/'android/assets';D=A/'data';R=json.loads((ROOT/'docs/MAPS_V41_MANIFEST.json').read_text())
M=json.loads((D/'maps.json').read_text());P=json.loads((D/'props.json').read_text())['props']
checks=0

def ck(c,msg):
 global checks
 checks+=1
 if not c:raise AssertionError('V4.1: '+msg)
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
areas=M['areas'];ids=set(R['areas']);nine=set(R['nine_v4_authored_maps_untouched'])
ck(len(ids)==13,'13 areas');ck(len(nine)==9 and ids.isdisjoint(nine),'9 authored maps disjoint');ck(len(areas)==22,'22 existing areas')
for n in nine:
 ck(sha(A/'maps'/f'{n}.png')==MANIFEST['authored_map_sha'][n],n+' original authored map unchanged')
refjson=json.loads((BASE/'v40_maps.json').read_text());ref=refjson['areas'];propsref=json.loads((BASE/'v40_props.json').read_text())['props']
replaced=0
for name in sorted(ids):
 old=ref[name];m=areas[name];im=A/m['image'];baseline=ROOT/'art_source/world_v41/baseline_maps'/f'{name}.png';overlay=ROOT/'art_source/world_v41/editable_layers'/f'{name}_atmosphere.png'
 ck(im.is_file() and baseline.is_file() and overlay.is_file(),name+' art + baseline + editable layer files')
 ck(sha(baseline)==MANIFEST['other_map_sha'][name],name+' unchanged source baseline')
 ck(sha(im)!=sha(baseline),name+' real runtime background edited')
 with Image.open(im) as r,Image.open(baseline) as b, Image.open(overlay) as layer:
  ck(r.size==b.size==layer.size==(old['w'],old['h']),name+' unchanged world resolution')
  ck(layer.mode=='RGBA',name+' editable RGBA overlay')
  bbox=ImageChops.difference(r.convert('RGB'),b.convert('RGB')).getbbox()
  ck(bbox is not None,name+' raster differs beyond metadata')
 for k in ('w','h','spawn','walls','ellipses','doors','gates','water','examine','animals'):
  ck(old.get(k)==m.get(k),name+' unchanged '+k)
 ck(len(old['props'])==len(m['props']),name+' same number of runtime props')
 changes=m['v41PropReplacementIndex'];ck(len(changes)==R['areas'][name]['legacyPropsReplaced'],name+' manifest matches')
 for idx,(o,n) in enumerate(zip(old['props'],m['props'])):
  ck(o['x']==n['x'] and o['y']==n['y'],name+' anchor retained at prop '+str(idx))
  po=propsref[o['type']];pn=P[n['type']]
  ck(po['cw']==pn['cw'] and po['ch']==pn['ch'] and po['layer']==pn['layer'],name+' prop collision+depth preserved '+str(idx))
  if str(idx) in changes:
   ck(n['type']!=o['type'] and (n['type'].startswith('v41_') or (name in ('plaza','taman_kota','cafe','riverside') and n['type'].startswith('v43_')) or (name in ('dermaga','bukit_bintang','memory_garden','eternal_garden') and n['type'].startswith('v44_'))),name+' expected art replaced '+str(idx))
   ck((A/pn['image']).is_file(), name+' new sprite exists '+str(idx));replaced+=1
  else:ck(o['type']==n['type'] or (name in ('plaza','taman_kota','cafe','riverside') and n['type']=='v43_'+o['type']) or (name in ('dermaga','bukit_bintang','memory_garden','eternal_garden') and n['type']=='v44_'+o['type']),name+' old art/authorized v43 variant retained at prop '+str(idx))
 ck(m['visualStyle']=='v4.1_romantic_scenery',name+' v41 style metadata')
ck(replaced==R['newPropReplacements'],'all prop instances accounted')
for name in ['quests.json','story.json','memory_book.json']:
 ck(sha(D/name)==MANIFEST['old_data_sha'][name],name+' storyline/quest data untouched')
audio=MANIFEST['audio_sha'];newaudio=A/'audio'
ck(len(audio)==86,'legacy 86 audio recorded')
for rel,digest in audio.items():
 ck((newaudio/rel).is_file() and sha(newaudio/rel)==digest,'untouched audio '+str(rel))
# Verify environment artwork crop atlas exists for repeatable regeneration.
ck((ROOT/'art_source/world_v41/pixel_landmarks_atlas.png').is_file(),'source atlas present')
print('V4.1 AUDIT PASS:',checks,'assertions;',len(ids),'newly designed map backgrounds;',replaced,'Y-sorted prop replacements;',len(audio),'audio retained')
