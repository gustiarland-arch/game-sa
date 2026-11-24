#!/usr/bin/env python3
"""Before/after composites of background+prop for the actual four playable areas, not emulator captures."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,math
R=Path(__file__).resolve().parent.parent;A=R/'android/assets';S=R/'art_source/world_v44';OUT=R/'docs/preview/v44_four_maps_before_after.jpg'
M=json.loads((A/'data/maps.json').read_text())['areas'];D=json.loads((A/'data/props.json').read_text())['props']
REF=json.loads((S/'v43_manifest.json').read_text())['geometry'];BASEDEF=json.loads((S/'v43_manifest.json').read_text())['props']
NAMES={'dermaga':'DERMAGA','bukit_bintang':'BUKIT BINTANG','memory_garden':'MEMORY GARDEN','eternal_garden':'ETERNAL GARDEN'}
CANVAS=(1550,1500);preview=Image.new('RGB',CANVAS,(29,31,48));dr=ImageDraw.Draw(preview)
try:
 font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',24)
 small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
except OSError:font=ImageFont.load_default();small=font
# Cached RGBA textures; paste all props to ensure previews reflect references in the game.
cache={}
def tex(path):
 path=str(path)
 if path not in cache:cache[path]=Image.open(path).convert('RGBA')
 return cache[path]
def scene(area,new):
 src=A/'maps'/f'{area}.png' if new else S/'baseline_maps'/f'{area}.png'
 image=tex(src).copy();items=M[area]['props'] if new else REF[area]['props']
 for p in sorted(items,key=lambda a:a['y']):
  typ=p['type']
  if not new and typ in BASEDEF: path=A/BASEDEF[typ]['image']
  elif not new and (S/'baseline_props'/(typ+'.png')).exists():path=S/'baseline_props'/(typ+'.png')
  else:path=A/D[typ]['image']
  if not path.exists():continue
  prop=tex(path)
  image.alpha_composite(prop,(int(p['x']-prop.width/2),int(p['y']-prop.height))) if (0<=p['x']-prop.width/2 and 0<=p['y']-prop.height and p['x']+prop.width/2<=image.width and p['y']<=image.height) else image.paste(prop,(int(p['x']-prop.width/2),int(p['y']-prop.height)),prop)
 return image.convert('RGB')
for i,area in enumerate(NAMES):
 rowtop=68+i*351
 dr.text((28,rowtop-39),NAMES[area]+'  |  SOURCE ASSET COMPOSITE',font=font,fill=(248,225,205))
 for j,new in enumerate((False,True)):
  im=scene(area,new)
  target=(715,301)
  im.thumbnail(target,Image.Resampling.LANCZOS)
  x=34+j*770+(target[0]-im.width)//2;y=rowtop+(target[1]-im.height)//2
  preview.paste(im,(x,y))
  dr.text((35+j*770,rowtop+306),'v4.4' if new else 'v4.3',font=small,fill=(245,204,180) if new else (180,190,211))
OUT.parent.mkdir(exist_ok=True,parents=True)
preview.save(OUT,quality=87,subsampling=0)
print(OUT,OUT.stat().st_size)
