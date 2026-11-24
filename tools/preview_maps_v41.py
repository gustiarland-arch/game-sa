#!/usr/bin/env python3
"""Visual review from real runtime map PNG + prop atlas (not emulator screenshot)."""
from pathlib import Path
import json,math
from PIL import Image, ImageDraw, ImageFont, ImageOps
R=Path(__file__).resolve().parent.parent;AS=R/'android/assets';PRE=R/'docs/preview';PRE.mkdir(exist_ok=True)
M=json.loads((AS/'data/maps.json').read_text())['areas'];P=json.loads((AS/'data/props.json').read_text())['props']
D=R/'art_source/world_v41/baseline_maps'
ids=list(json.loads((R/'docs/MAPS_V41_MANIFEST.json').read_text())['areas'])

def paint(id,before=False):
    m=M[id]
    im=Image.open((D/(id+'.png')) if before else AS/m['image']).convert('RGBA')
    used={}
    refs= m.get('v41PropReplacementIndex',{})
    objects=m['props']
    for i,p in sorted(enumerate(objects),key=lambda it:it[1]['y']):
        t=refs.get(str(i),{}).get('was',p['type']) if before else p['type']
        imgref=P[t]['image'];asset=AS/imgref
        if not asset.is_file():raise FileNotFoundError(asset)
        if t not in used:used[t]=Image.open(asset).convert('RGBA')
        a=used[t];x=int(p['x']-a.width//2);y=int(p['y']-a.height)
        if x>=im.width or y>=im.height or x+a.width<0 or y+a.height<0:continue
        im.alpha_composite(a,(x,y))
    return im.convert('RGB')

def make_grid(ids,fn,mode='after'):
    W,H,HD=520,330,34;cols=3;rows=math.ceil(len(ids)/cols)
    dst=Image.new('RGB',(cols*W+40,rows*(H+HD)+25),(22,27,37));d=ImageDraw.Draw(dst)
    for n,id in enumerate(ids):
        im=paint(id,mode=='before');im.thumbnail((W-18,H-16),Image.Resampling.LANCZOS)
        x=20+(n%cols)*W+(W-im.width)//2;y=12+(n//cols)*(H+HD)+HD+(H-im.height)//2
        dst.paste(im,(x,y));d.text((22+(n%cols)*W,12+(n//cols)*(H+HD)),M[id]['name']+' — '+('SEBELUM' if mode=='before' else 'V4.1'),fill=(239,242,239))
    dst.save(PRE/fn,quality=87)
make_grid(ids,'v41_thirteen_maps_runtime_composite.jpg')
make_grid(ids,'v41_thirteen_before_composite.jpg','before')
# Larger side-by-side for 6 visually distinct maps.
selected=['plaza','taman_kota','cafe','bukit_bintang','starfall_village','gua_kristal']
W,H=550,355;dst=Image.new('RGB',(2*W+32,len(selected)*(H+35)+15),(24,28,38));d=ImageDraw.Draw(dst)
for i,id in enumerate(selected):
    for j,b in enumerate((True,False)):
        im=paint(id,b);im.thumbnail((W-18,H-8),Image.Resampling.LANCZOS);x=16+j*W+(W-im.width)//2;y=30+i*(H+35)+(H-im.height)//2
        dst.paste(im,(x,y))
        d.text((16+j*W,8+i*(H+35)),f'{M[id]["name"]} — '+('v4.0' if b else 'v4.1'),fill=(238,233,211))
dst.save(PRE/'v41_before_after_six_areas.jpg',quality=88)
print('Created map composites:',len(ids),'area previews')
