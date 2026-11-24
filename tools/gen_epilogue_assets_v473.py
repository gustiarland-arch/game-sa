#!/usr/bin/env python3
"""Original editable pixel-art letter archive map and Epilogue memory icons (deterministic)."""
from pathlib import Path
from PIL import Image,ImageDraw
from random import Random
R=Path(__file__).resolve().parents[1];MAP=R/'android/assets/maps';ITEMS=R/'android/assets/items'; MAP.mkdir(exist_ok=True,parents=True);ITEMS.mkdir(exist_ok=True,parents=True)
r=Random(47309)
# 1:8 nearest-neighbor room backdrop, editable by regenerating from this source.
im=Image.new('RGB',(120,80),'#33415a');d=ImageDraw.Draw(im)
for y in range(80):
 if y<27: d.line((0,y,119,y),fill=(50+int(y*.48),58+int(y*.45),82+int(y*.25)))
 else:d.line((0,y,119,y),fill=(96+int((y-27)*.25),82+int((y-27)*.25),88+int((y-27)*.15)))
for x in range(0,120,12):d.line((x,28,x,78),fill='#78696e')
for y in range(28,79,10):d.line((0,y,119,y),fill='#8b7774')
# Archive shelves, two equal writing desks and a central book.
d.rectangle((8,7,111,25),fill='#554960',outline='#d2b4a4',width=2)
for x in range(11,109,9):
 d.rectangle((x,12,x+4,22),fill=r.choice(['#d9bea5','#b7b9ca','#8b9ebc','#ce91a6']))
 d.line((x,12,x,20),fill='#4c4d66')
for cx in (37,83):
 d.rectangle((cx-19,32,cx+19,51),fill='#624f60',outline='#dfb89c',width=2)
 d.rectangle((cx-14,35,cx+14,48),fill='#af9a8c',outline='#e4c8aa')
 d.polygon(((cx-9,38),(cx,41),(cx+9,38),(cx+9,47),(cx,49),(cx-9,47)),fill='#f3dfc6',outline='#b18d98')
 d.line((cx,41,cx,49),fill='#a8808b')
 d.ellipse((cx-4,27,cx+4,34),fill='#f4c9a4')
 d.rectangle((cx-1,22,cx+1,29),fill='#ddc3a7')
# warm pool of light in the middle / no collision on decorations.
d.ellipse((50,51,71,66),fill='#b5a087',outline='#e2c09f',width=2)
d.polygon(((53,54),(60,57),(67,54),(67,62),(60,65),(53,62)),fill='#f4e5cf')
d.line((60,57,60,65),fill='#927b90')
for cx,cy in ((25,62),(99,62),(60,29)):
 for _ in range(9):
  x=cx+r.randrange(-10,11);y=cy+r.randrange(-8,8)
  if 0<x<120 and 0<y<80:d.point((x,y),fill='#f3d2a0')
d.rectangle((52,71,68,79),fill='#383f56',outline='#e1c4ac')
im.resize((960,640),Image.Resampling.NEAREST).save(MAP/'ruang_dua_surat.png',optimize=True)
colors={'page':('#667991','#f4e2bf'),'letter':('#856f8c','#f5dbc0'),'chair':('#93687b','#f0c3b7'),'photo':('#668e96','#e9e0cf'),'sunset':('#bb8288','#f6dfac')}
for name,(base,detail) in colors.items():
 p=Image.new('RGBA',(48,48),(0,0,0,0));t=ImageDraw.Draw(p)
 t.rounded_rectangle((6,7,41,42),radius=5,fill=base,outline='#f3c9ac',width=2)
 if name=='page':
  t.polygon(((11,12),(22,15),(36,12),(36,36),(22,39),(11,36)),fill=detail,outline='#5c5772')
  t.line((22,15,22,39),fill='#9a7794',width=2)
  for y in (21,26,31):t.line((14,y,19,y+1),fill='#baa1a3',width=1);t.line((25,y,32,y-1),fill='#baa1a3',width=1)
 if name=='letter':
  t.polygon(((10,17),(36,17),(36,34),(10,34)),fill=detail,outline='#473d5d')
  t.line((10,18,23,27,36,18),fill='#936d8f',width=2)
 if name=='chair':
  t.rectangle((14,13,33,26),fill=detail,outline='#503d5c',width=2)
  t.rectangle((13,26,34,32),fill='#cd9e9a',outline='#503d5c')
  t.line((16,32,16,39),fill='#503d5c',width=2);t.line((31,32,31,39),fill='#503d5c',width=2)
 if name=='photo':
  t.rectangle((11,12,36,35),fill=detail,outline='#415871',width=2)
  t.polygon(((13,30),(20,21),(25,27),(30,22),(35,30)),fill='#94b3ae')
  t.ellipse((26,15,31,20),fill='#f0ba91')
 if name=='sunset':
  t.ellipse((17,13,32,28),fill=detail)
  for y in (30,34,38):t.line((12,y,36,y),fill='#e9b49b',width=1)
  t.line((10,28,36,28),fill='#735a86',width=2)
 p.resize((192,192),Image.Resampling.NEAREST).save(ITEMS/('v473_'+name+'.png'),optimize=True)
print('PASS: epilogue room + 5 original editable pixel memory icons')
