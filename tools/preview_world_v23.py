"""Build a contact sheet using ACTUAL v2.3 map PNGs + layered game prop PNGs.
It is an asset composite, NOT a screenshot of a running Android game.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, sys
ROOT=Path(__file__).resolve().parent.parent
ASSETS=ROOT/'android'/'assets'
OUT=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'docs/preview/v23_world_asset_preview.png'
MAPS=json.loads((ASSETS/'data/maps.json').read_text())['areas']
PROPS=json.loads((ASSETS/'data/props.json').read_text())['props']
AREAS=['plaza','taman_kota','hutan_bisik','cafe','starfall_village','gua_kristal']
CW,CH=566,342
im=Image.new('RGB',(1200,1230),(20,19,36)); d=ImageDraw.Draw(im)
try:
    font=ImageFont.truetype('DejaVuSans.ttf',23)
    small=ImageFont.truetype('DejaVuSans.ttf',15)
except OSError:
    font=ImageFont.load_default()
    small=ImageFont.load_default()
d.text((34,22),'ARLAND & SOFIA  /  WORLD VISUAL v2.3',font=font,fill=(250,231,219))
d.text((34,60),'Preview komposit dari aset peta + props (bukan screenshot game Android)',font=small,fill=(195,179,196))
for idx,name in enumerate(AREAS):
    m=MAPS[name]
    base=Image.open(ASSETS/m['image']).convert('RGBA')
    for pr in sorted(m['props'],key=lambda pr:(PROPS[pr['type']].get('layer')!='floor',pr['y'])):
        icon=Image.open(ASSETS/PROPS[pr['type']]['image']).convert('RGBA')
        # same object coords as native renderer: centered x, foot y.
        x=int(pr['x']-icon.width/2); y=int(pr['y']-icon.height)
        if x>=base.width or y>=base.height or x+icon.width<0 or y+icon.height<0: continue
        base.alpha_composite(icon,(x,y))
    base=base.convert('RGB')
    base.thumbnail((CW,CH),Image.Resampling.LANCZOS)
    col,row=idx%2,idx//2
    x=34+col*600; y=105+row*362
    d.rounded_rectangle((x-8,y-8,x+CW+8,y+CH+42),radius=15,fill=(48,41,67),outline=(107,86,116),width=2)
    # Center artwork in card without upscaling small interiors.
    ox=x+(CW-base.width)//2; oy=y+(CH-base.height)//2
    im.paste(base,(ox,oy))
    d.text((x+8,y+CH+10),m['name']+' — '+name,font=small,fill=(255,232,222))
OUT.parent.mkdir(parents=True,exist_ok=True)
im.save(OUT,optimize=True)
print('Preview made:',OUT,im.size)
