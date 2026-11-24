"""Source-asset comparison image, NOT an emulator screenshot.
Run after visual_overhaul_v32.py; use identical prop coordinates and sprite anchors.
"""
from pathlib import Path
import json
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];A=R/'android/assets'; OLD=R/'art_source/visual_v32_base'
M=json.loads((R/'tools/build/maps_base.json').read_text())
P=json.loads((A/'data/props.json').read_text())['props']
W,H=560,330
out=Image.new('RGB',(W*2+48,H*3+110),(26,25,44));d=ImageDraw.Draw(out)
def render(mid,legacy):
 m=M[mid]
 root=OLD/'maps'/f'{mid}.png' if legacy else A/m['image']
 im=Image.open(root).convert('RGBA')
 scale=min(W/im.width,H/im.height)
 im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.NEAREST)
 for obj in sorted(m['props'],key=lambda p:p['y']):
  name=obj['type']; orig=P[name]['image'].replace('props/','')
  pf=OLD/'props'/orig if legacy else A/P[name]['image']
  if not pf.exists():continue
  prop=Image.open(pf).convert('RGBA')
  prop=prop.resize((max(1,round(prop.width*scale)),max(1,round(prop.height*scale))),Image.Resampling.NEAREST)
  px=round(obj['x']*scale-prop.width/2);py=round(obj['y']*scale-prop.height)
  if 0<=px and 0<=py and px+prop.width<=im.width and py+prop.height<=im.height: im.alpha_composite(prop,(px,py))
 return im
for i,area in enumerate(('plaza','cafe','memory_garden')):
 y=32+i*(H+24)
 for j,legacy in enumerate((True,False)):
  im=render(area,legacy)
  out.paste(im,(14+j*(W+20),y))
  d.text((17+j*(W+20),y+H-17),f'{area} | '+('v3.0 asli' if legacy else 'v3.2 updated'),fill=(255,227,196))
out.save(R/'docs/preview/v32_before_after_actual_assets.jpg',quality=94)
print('Preview before-after source assets generated')
