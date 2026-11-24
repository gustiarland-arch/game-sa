#!/usr/bin/env python3
"""v3.4 stage-2 preview built from ACTUAL map+prop PNGs, never game screenshots."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parent.parent
A=ROOT/'android/assets'
BASE=ROOT/'art_source/world_stage2/v33_unmodified'
OUT=ROOT/'docs/preview'
OUT.mkdir(exist_ok=True,parents=True)
D=json.loads((A/'data/maps.json').read_text())['areas']
P=json.loads((A/'data/props.json').read_text())['props']
MAPS=[('riverside','RIVERSIDE'),('dermaga','DERMAGA'),('bukit_bintang','BUKIT BINTANG'),('memory_garden','MEMORY GARDEN'),('eternal_garden','ETERNAL GARDEN')]
try:
 FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',24)
 SMALL=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
except OSError:FONT=ImageFont.load_default();SMALL=FONT

def render(name,old=False):
    d=D[name]
    file=BASE/'maps'/f'{name}.png' if old else A/'maps'/f'{name}.png'
    image=Image.open(file).convert('RGBA')
    for prop in sorted(d['props'],key=lambda p:(P[p['type']].get('layer')!='floor',p['y'])):
        rel=P[prop['type']]['image']
        f=BASE/rel if old and (BASE/rel).exists() else A/rel
        overlay=Image.open(f).convert('RGBA')
        x=int(prop['x']-overlay.width/2);y=int(prop['y']-overlay.height)
        image.alpha_composite(overlay,(x,y))
    return image

ROWS=[];W=1600
for name,title in MAPS:
    pair=[render(name,True),render(name,False)]
    pair=[i.resize((755,round(i.height*755/i.width)),Image.Resampling.LANCZOS) for i in pair]
    height=max(i.height for i in pair)+80
    row=Image.new('RGB',(W,height),'#1a1e2c');d=ImageDraw.Draw(row)
    d.text((35,8),title,fill='#fff3db',font=FONT)
    d.text((32,47),'v3.3 — SEBELUM',fill='#cdd1e0',font=SMALL)
    d.text((823,47),'v3.4 — SESUDAH',fill='#ffd49d',font=SMALL)
    for idx,im in enumerate(pair):row.paste(im.convert('RGB'),(20+idx*800,73))
    ROWS.append(row)
result=Image.new('RGB',(W,sum(i.height for i in ROWS)+14*(len(ROWS)+1)),'#121624')
y=14
for r in ROWS:result.paste(r,(0,y));y+=r.height+14
f=OUT/'v34_stage2_before_after.jpg';result.save(f,quality=87,optimize=True)
# Wide compact summary, source asset composites.
board=Image.new('RGB',(1500,780),'#1c2030');b=ImageDraw.Draw(board)
for idx,(name,title) in enumerate(MAPS):
    im=render(name)
    im.thumbnail((472,320),Image.Resampling.LANCZOS)
    x=(idx%3)*500+(500-im.width)//2
    y=(idx//3)*390+47
    board.paste(im.convert('RGB'),(x,y));b.text((idx%3*500+22,(idx//3)*390+10),title,fill='#ffdbb1',font=FONT)
board.save(OUT/'v34_stage2_five_areas.jpg',quality=88,optimize=True)
print('PREVIEW OK',f.stat().st_size,'bytes')
