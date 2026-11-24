#!/usr/bin/env python3
"""Non-runtime composite for reviewing original map background + edited PNG layers."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
R=Path(__file__).resolve().parents[1]
A=R/'android/assets'; D=A/'data';areas=json.loads((D/'maps.json').read_text(encoding='utf-8'))['areas'];props=json.loads((D/'props.json').read_text(encoding='utf-8'))['props']
locs=[('plaza','PLAZA KOTA'),('taman_kota','TAMAN KOTA'),('riverside','TEPI DANAU'),('cafe','KAFE SENJA'),('star_path','STAR PATH'),('memory_garden','MEMORY GARDEN')]
W=1170; cell_w=540; cell_h=266; margin=26; rowgap=66; head=76; total_h=head+len(locs)*(cell_h+rowgap)+42
res=Image.new('RGB',(W,total_h),'#101720');d=ImageDraw.Draw(res)
fonts=['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf']
f=next((p for p in fonts if Path(p).exists()),None)
fnt=ImageFont.truetype(f,19) if f else ImageFont.load_default();sm=ImageFont.truetype(f,12) if f else ImageFont.load_default();title=ImageFont.truetype(f,27) if f else ImageFont.load_default()
d.text((24,15),'ARLAND & SOFIA — v5.1',font=title,fill='#f0e1ca');d.text((24,47),'PERBANDINGAN DARI ASET PETA • BUKAN SCREENSHOT APK',font=sm,fill='#aabcc7')
for i,(key,label) in enumerate(locs):
 a=areas[key];t=a['elevationPlatforms'][0];base=Image.open(A/a['image']).convert('RGBA');after=base.copy()
 for p in a['props']:
  if p['type'].startswith('v51_') and props[p['type']]['layer']=='floor':
   im=Image.open(A/props[p['type']]['image']).convert('RGBA');after.alpha_composite(im,(int(p['x']-im.width*.5),int(p['y']-im.height)))
 for terrace in a['elevationPlatforms']:
  im=Image.open(A/terrace['image']).convert('RGBA');after.alpha_composite(im,(int(terrace['x']-20),int(terrace['y']-40)))
 for p in a['props']:
  if p['type'].startswith('v51_') and props[p['type']]['layer']!='floor':
   im=Image.open(A/props[p['type']]['image']).convert('RGBA');after.alpha_composite(im,(int(p['x']-im.width*.5),int(p['y']-im.height)))
 for terrace in a['elevationPlatforms']:
  im=Image.open(A/terrace['front']).convert('RGBA');after.alpha_composite(im,(int(terrace['x']-20),int(terrace['y']-40)))
 # Focus on exact environment rather than misleading full-map thumbnail.
 focusx=t['x']+t['w']//2;focusy=t['y']+(t['h']+t['stairLength'])//2
 rect=(int(focusx-380),int(focusy-192),int(focusx+380),int(focusy+192))
 for j,pic in enumerate((base,after)):
  pic=pic.crop(rect).convert('RGB');pic=pic.resize((cell_w,cell_h),Image.Resampling.LANCZOS)
  x=margin+j*(cell_w+18); y=head+i*(cell_h+rowgap)
  res.paste(pic,(x,y+24)); d.rounded_rectangle((x-2,y+22,x+cell_w+2,y+cell_h+27),radius=6,outline='#53606d',width=2)
  d.text((x,y+1),'SEBELUM — MAP ASLI' if j==0 else 'SESUDAH — LAPISAN V5.1',font=fnt,fill='#d9dce5')
 d.text((margin,head+i*(cell_h+rowgap)+cell_h+29),label,font=fnt,fill='#e5d0b4')
res.save(R/'docs/preview/v51_environment_before_after.png',optimize=True)
print(R/'docs/preview/v51_environment_before_after.png')
