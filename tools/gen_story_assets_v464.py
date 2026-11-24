#!/usr/bin/env python3
"""Deterministic, original, editable pixel-art gallery and six memory icon assets."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from random import Random

ROOT=Path(__file__).resolve().parents[1] / 'android/assets'
DEST=ROOT/'maps/galeri_komunitas.png'
C={
 'wall':'#332b48','wallshade':'#272238','trim':'#83677d',
 'floor':'#766076','flooralt':'#79647b','floorlight':'#806a80',
 'gold':'#d6ae76','highlight':'#fff0c8','brown':'#51364c','wood':'#704956',
 'pink':'#e8a4ad','rose':'#bb6f83','window':'#9bb4ca','cream':'#eddbc3',
 'shadow':'#49384e','ink':'#292337','green':'#789682'
}
R=Random(464)
im=Image.new('RGB',(240,160),C['floor']);d=ImageDraw.Draw(im)
# Wood-plank/tile texture: low-frequency, sparse, purposeful dithering.
for y in range(15,155,9):
 for x in range(17,222,11):
  col=C['flooralt'] if (x//11+y//9)%3==0 else C['floorlight'] if (x+y)%7==0 else C['floor']
  d.rectangle((x,y,x+10,y+8),fill=col)
  d.line((x,y,x+10,y), fill='#695369',width=1)
  if R.random()<0.3:d.point((x+R.randrange(3,9),y+R.randrange(3,7)),fill='#998199')
# architectural silhouette: interior perimeter and crown molding
d.rectangle((0,0,240,22),fill=C['wall'])
d.rectangle((0,0,18,160),fill=C['wallshade'])
d.rectangle((220,0,240,160),fill=C['wallshade'])
d.rectangle((0,153,108,160),fill=C['wallshade'])
d.rectangle((132,153,240,160),fill=C['wallshade'])
d.rectangle((19,20,220,24),fill=C['trim'])
d.rectangle((19,24,220,25),fill=C['gold'])
d.rectangle((17,151,108,153),fill=C['trim'])
d.rectangle((132,151,220,153),fill=C['trim'])
# Spotlights and illuminated gallery paintings
for cx in [48,110,178]:
 d.polygon([(cx-4,22),(cx+4,22),(cx+26,67),(cx-26,67)],fill='#816e81')
 d.ellipse((cx-3,19,cx+3,25),fill=C['highlight'])
# paintings with frames & unique original symbolic imagery
for x,kind in [(33,'flower'),(98,'water'),(164,'sunset')]:
 y=27;w=43;h=35
 d.rectangle((x-3,y-3,x+w+3,y+h+3),fill=C['ink'])
 d.rectangle((x-2,y-2,x+w+2,y+h+2),fill=C['gold'])
 d.rectangle((x,y,x+w,y+h),fill=('#89ad9e' if kind=='flower' else '#8c9cbf' if kind=='water' else '#e2a98e'))
 if kind=='flower':
  for px,py in [(x+13,y+17),(x+28,y+24),(x+25,y+13)]:
   d.line((px,py+11,px,py),fill=C['green'],width=2)
   for ax,ay in [(-3,0),(3,0),(0,-3),(0,3)]:d.ellipse((px+ax-2,py+ay-2,px+ax+2,py+ay+2),fill=C['pink'])
   d.ellipse((px-1,py-1,px+1,py+1),fill=C['gold'])
 elif kind=='water':
  d.polygon([(x,y+19),(x+12,y+13),(x+26,y+17),(x+43,y+9),(x+43,y+35),(x,y+35)],fill='#638bad')
  d.line((x+4,y+26,x+39,y+25),fill='#b9d7d0',width=2)
  d.ellipse((x+25,y+2,x+36,y+13),fill=C['highlight'])
 else:
  d.ellipse((x+23,y+5,x+36,y+18),fill=C['highlight'])
  d.polygon([(x,y+22),(x+13,y+17),(x+25,y+26),(x+43,y+18),(x+43,y+35),(x,y+35)],fill='#9e6e89')
  d.line((x+4,y+31,x+36,y+31),fill='#c9979c',width=2)
# gallery art pedestals and rugs
for x in [25,182]:
 d.ellipse((x,100,x+28,112),fill=C['shadow'])
 d.rectangle((x+4,88,x+25,102), fill=C['wood'])
 d.rectangle((x+7,85,x+22,90), fill=C['gold'])
 d.rectangle((x+8,81,x+21,84),fill=C['cream'])
# Two rugs, one small with poignant empty chair
for x,y,w,h in [(45,96,66,30),(130,93,59,33)]:
 d.rounded_rectangle((x,y,x+w,y+h),radius=3,fill='#a17a88',outline=C['gold'],width=2)
 for yy in range(y+7,y+h-5,7):d.line((x+7,yy,x+w-7,yy),fill='#b8919c')
# Empty chair with one gold card; center around (72,102)
d.ellipse((57,111,87,120),fill=C['shadow'])
d.rectangle((64,95,80,108),fill=C['brown'],outline=C['gold'],width=2)
d.rectangle((62,94,82,99),fill=C['wood'],outline=C['gold'],width=1)
d.rectangle((65,108,68,117),fill=C['ink']);d.rectangle((78,108,81,117),fill=C['ink'])
d.rectangle((67,89,78,93),fill=C['cream']);d.line((69,91,76,91),fill=C['ink'])
# projector cart on right at (176,101)
d.ellipse((162,113,194,122),fill=C['shadow'])
d.rectangle((169,101,186,111),fill='#3e415e',outline=C['gold'],width=2)
d.rectangle((166,91,190,101),fill='#4c5369',outline='#b6c2c9',width=2)
d.ellipse((174,94,181,99),fill=C['highlight']);d.rectangle((171,112,173,118),fill=C['ink']);d.rectangle((183,112,185,118),fill=C['ink'])
# Exhibition platform in middle upper room, behind interactive stage
stage=(104,69,150,86)
d.rounded_rectangle(stage,radius=3,fill=C['wood'],outline=C['gold'],width=2)
d.rectangle((107,72,147,78),fill='#815767')
d.line((113,83,140,83),fill='#bc90a0',width=2)
# Hanging string with small flowers & gold bulbs
for x in range(24,220,8):
 yy=70+(x//8)%3
 d.ellipse((x-1,yy-1,x+1,yy+1),fill=C['gold'] if (x//8)%2 else C['pink'])
# exit door at map bottom
for dx,dc in [(108,C['gold']),(109,C['cream']),(131,C['gold']),(132,C['cream'])]:d.line((dx,151,dx,160),fill=dc)
d.rectangle((110,153,130,160),fill='#ad8b85'); d.rectangle((112,155,128,159),fill='#d1ad96')
# Small visitor benches, leave clear line for foot collision
for bx in (35,187):
 d.rectangle((bx-6,132,bx+6,136),fill=C['wood'],outline=C['gold'])
 d.line((bx-4,137,bx-4,143),fill=C['ink'],width=2);d.line((bx+4,137,bx+4,143),fill=C['ink'],width=2)
# Warm vignette only at borders; nearest-neighbor upscale is exact alignment with map coords.
DEST.parent.mkdir(parents=True,exist_ok=True)
im.resize((960,640),resample=Image.Resampling.NEAREST).save(DEST,optimize=True)

# Distinct 64px editable pixel icons (16px tile drawing scaled 4).
def icon(name,which):
    canvas=Image.new('RGBA',(16,16),(0,0,0,0));g=ImageDraw.Draw(canvas)
    g.rounded_rectangle((1,1,14,14),radius=3,fill='#3d354f',outline='#d7af84',width=1)
    if which=='ticket':
        g.rectangle((3,5,12,11),fill='#f3d0bd');g.line((5,7,10,7),fill='#995a73');g.line((5,9,10,9),fill='#995a73')
    if which=='chair':
        g.rectangle((5,5,10,9),fill='#c78b81');g.rectangle((4,9,11,11),fill='#e2ad87');g.line((5,11,5,13),fill='#d5b5a1');g.line((10,11,10,13),fill='#d5b5a1')
    if which=='projector':
        g.rectangle((3,5,12,10),fill='#8d9bb0');g.ellipse((6,6,9,9),fill='#fff4c8');g.line((4,11,4,13),fill='#9a7d9c')
    if which=='sketch':
        g.rectangle((4,3,11,12),fill='#eee1ca');g.line((5,8,8,5,10,7),fill='#be768d',width=2);g.line((5,10,10,10),fill='#a89b86')
    if which=='both':
        g.rectangle((3,4,7,12),fill='#b4a9bf');g.rectangle((8,4,12,12),fill='#edd1bc');g.line((4,6,6,6),fill='#866d9e');g.line((9,9,11,9),fill='#c77885')
    if which=='healed':
        g.rectangle((3,5,6,11),fill='#d8af99');g.rectangle((9,5,12,11),fill='#e8b6bf');g.line((6,9,9,9),fill='#ffe2a5',width=2)
    path=ROOT/'items'/f'v464_{name}.png'
    canvas.resize((64,64),Image.Resampling.NEAREST).save(path,optimize=True)
for name,which in [('gallery_ticket','ticket'),('empty_seat','chair'),('projector','projector'),('sketch','sketch'),('two_sides','both'),('seat_healed','healed')]:
    icon(name,which)
print('Created gallery map + 6 original icons:',DEST)
