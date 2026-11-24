#!/usr/bin/env python3
"""Compare actual v3.2 vs v3.3 *source assets* (flattened props + map) side-by-side.
Not an emulator screenshot. All inputs ship inside the ZIP.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
ROOT=Path(__file__).resolve().parent.parent
A=ROOT/'android/assets';ART=ROOT/'art_source/world_stage1/v32_unmodified'
OUT=ROOT/'docs/preview';OUT.mkdir(parents=True,exist_ok=True)
D=json.loads((A/'data/maps.json').read_text())['areas']
P=json.loads((A/'data/props.json').read_text())['props']

def one(name,old=False):
 m=D[name];bg=(ART/'maps'/f'{name}.png') if old else (A/'maps'/f'{name}.png')
 im=Image.open(bg).convert('RGBA')
 for p in sorted(m['props'],key=lambda p:(P[p['type']].get('layer')!='floor',p['y'])):
  rel=P[p['type']]['image']
  path=ART/rel if old and (ART/rel).exists() else A/rel
  prop=Image.open(path).convert('RGBA')
  im.alpha_composite(prop,(round(p['x']-prop.width/2),round(p['y']-prop.height)))
 return im

def font(n):
 for name in ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf','/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf'):
  if Path(name).is_file():return ImageFont.truetype(name,n)
 return ImageFont.load_default()

W=1700;rows=[]
for name,label in [('plaza','PLAZA KOTA'),('taman_kota','TAMAN KOTA'),('cafe','KAFE SENJA')]:
 before=one(name,True);after=one(name,False)
 target=820; scale=target/before.width
 h=round(before.height*scale)
 before=before.resize((target,h),Image.Resampling.LANCZOS)
 after=after.resize((target,h),Image.Resampling.LANCZOS)
 row=Image.new('RGB',(W,h+87),'#191d2c');d=ImageDraw.Draw(row)
 d.text((30,12),label,fill='#fff1dd',font=font(22))
 d.text((30,47),'v3.2 — SEBELUM',fill='#c9cdd5',font=font(15))
 d.text((864,47),'v3.3 — SESUDAH',fill='#ffd295',font=font(15))
 row.paste(before.convert('RGB'),(25,75));row.paste(after.convert('RGB'),(860,75))
 rows.append(row)
img=Image.new('RGB',(W,sum(x.height for x in rows)+16*(len(rows)+1)),'#131825')
y=16
for row in rows:img.paste(row,(0,y));y+=row.height+16
img.save(OUT/'v33_stage1_before_after.jpg',quality=90,optimize=True)
# A single triptych with current runtime asset flattening (not pretending to be a running build).
mini=Image.new('RGB',(1400,650),'#181b2a');draw=ImageDraw.Draw(mini)
for i,(mid,title) in enumerate([('plaza','PLAZA'),('taman_kota','TAMAN'),('cafe','KAFE')]):
 m=one(mid).convert('RGB');m.thumbnail((440,555),Image.Resampling.LANCZOS)
 x=15+i*466;y=55
 mini.paste(m,(x+(440-m.width)//2,y))
 draw.text((x+15,15),title,fill='#ffe4c0',font=font(23))
mini.save(OUT/'v33_three_areas.jpg',quality=89,optimize=True)
print('Preview generated:',(OUT/'v33_stage1_before_after.jpg').stat().st_size,'bytes')
