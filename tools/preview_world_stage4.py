#!/usr/bin/env python3
"""Visual comparison built ONLY from actual source map + prop assets (not a running APK screenshot)."""
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent.parent
A=ROOT/'android/assets';BASE=ROOT/'art_source/world_stage4/v35_unmodified'
OUT=ROOT/'docs/preview';OUT.mkdir(parents=True,exist_ok=True)
MAPS=['jalan_kota','perumahan','perpustakaan','arcade','toko_bunga','arland_room','sofia_room','dapur','ruang_arsip']
D=json.loads((A/'data/maps.json').read_text())['areas']
P=json.loads((A/'data/props.json').read_text())['props']
def font(size):
 try:return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',size)
 except OSError:return ImageFont.load_default()
TITLE=font(21);SUB=font(14)
def draw_area(name,old=False):
    im=Image.open((BASE if old else A)/'maps'/f'{name}.png').convert('RGBA')
    props=sorted(D[name]['props'],key=lambda x:(P[x['type']].get('layer')!='floor',x['y']))
    for obj in props:
        rel=Path(P[obj['type']]['image']);f=(BASE/rel) if old and (BASE/rel).exists() else A/rel
        with Image.open(f) as pic:
            overlay=pic.convert('RGBA')
        x=round(obj['x']-overlay.width/2);y=round(obj['y']-overlay.height)
        im.alpha_composite(overlay,(x,y))
    return im.convert('RGB')

W=1440;rows=[]
for name in MAPS:
    old=draw_area(name,True);new=draw_area(name,False)
    canvasw=692;h=round(canvasw*old.height/old.width)
    pair=[im.resize((canvasw,h),Image.Resampling.LANCZOS) for im in (old,new)]
    row=Image.new('RGB',(W,h+65),'#171b28');d=ImageDraw.Draw(row)
    d.text((20,7),name.replace('_',' ').upper(),font=TITLE,fill='#f9deb5')
    d.text((20,35),'v3.5 SEBELUM',font=SUB,fill='#d5d7e6');d.text((748,35),'v3.6 SESUDAH',font=SUB,fill='#ffd2a0')
    for i,im in enumerate(pair):row.paste(im,(12+728*i,61))
    rows.append(row)
result=Image.new('RGB',(W,sum(i.height for i in rows)+7*len(rows)),'#101522');y=0
for row in rows:result.paste(row,(0,y));y+=row.height+7
beforeafter=OUT/'v36_stage4_before_after.jpg';result.save(beforeafter,quality=84,optimize=True)
summary=Image.new('RGB',(1560,3*365),'#111724');d=ImageDraw.Draw(summary)
for i,name in enumerate(MAPS):
    im=draw_area(name,False);im.thumbnail((490,313),Image.Resampling.LANCZOS)
    x=i%3*520+15;y=i//3*365+40
    summary.paste(im,(x+(490-im.width)//2,y+(313-im.height)//2))
    d.text((x+3,y-31),name.replace('_',' ').upper(),font=TITLE,fill='#ffdeb2')
board=OUT/'v36_nine_areas_actual_assets.jpg';summary.save(board,quality=87,optimize=True)
print('Stage4 preview:',beforeafter.stat().st_size,board.stat().st_size)
