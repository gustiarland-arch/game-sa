#!/usr/bin/env python3
"""Original editable pixel-art map/collectible generator for Chapter6 hall."""
from pathlib import Path
from PIL import Image,ImageDraw
from random import Random
ROOT=Path(__file__).resolve().parents[1]
MD=ROOT/'android/assets/maps';ID=ROOT/'android/assets/items';MD.mkdir(parents=True,exist_ok=True);ID.mkdir(parents=True,exist_ok=True)
r=Random(47206);im=Image.new('RGB',(240,160),'#202849');d=ImageDraw.Draw(im)
# Midnight vault, warm archway outlines, three future windows.
for y in range(160):
 c=(31+int(y*.11),39+int(y*.08),70+int(y*.12))
 d.line((0,y,239,y),fill=c)
for x in range(0,240,12):
 for y in range(0,160,12):
  if r.random()<.7:d.rectangle((x,y,x+11,y+11),outline='#344263',width=1)
# gold floor perspective and the three projected futures
d.polygon([(14,159),(36,107),(80,89),(117,58),(159,91),(202,109),(228,159)],fill='#405676',outline='#b8a1ae')
d.rectangle((18,125,222,155),fill='#4d607e',outline='#d8bca5',width=2)
for x in range(25,226,23):
 d.line((x,126,x-8,155),fill='#7682a0')
for y in range(129,154,10):d.line((21,y,219,y),fill='#65718d')
# Door arches: mirror scenes at (51,110),(120,58),(189,110)
for cx,cy,glass,sign in [(51,110,'#9dc4d2','#f0bb8e'),(120,57,'#dab8b6','#f1d5ae'),(189,110,'#b8c5df','#a8d7db')]:
 w=19;h=27
 d.rectangle((cx-w,cy-14,cx+w,cy+23),fill='#23314e',outline='#d9ba95',width=3)
 d.pieslice((cx-w,cy-h,cx+w,cy+1),180,360,fill='#23314e',outline='#d9ba95',width=3)
 d.ellipse((cx-13,cy-17,cx+13,cy+18),outline=glass,width=2)
 d.line((cx,cy-18,cx,cy+15),fill=glass,width=2)
 d.line((cx-12,cy,cx+12,cy),fill=glass,width=1)
 for j in range(4):
  xx=cx+r.randrange(-10,11);yy=cy+r.randrange(-14,16)
  d.point((xx,yy),fill=sign)
# Existing memory four stands, not walls: space stays passable.
for x,y,col in [(55,77,'#e8ba95'),(92,51,'#cbb5ce'),(151,51,'#dcd4af'),(189,77,'#b8d3dc')]:
 d.ellipse((x-9,y-4,x+9,y+4),fill='#344966',outline=col)
 d.rectangle((x-4,y-10,x+4,y-3),fill='#dbcdaf',outline='#fbe2b7')
 d.line((x-5,y+1,x+5,y+1),fill='#8a95b5')
# Center memory book and trace vines; right and left writing seats.
d.rectangle((110,103,130,118),fill='#4d3f54',outline='#e3c7a8',width=2)
d.polygon([(114,104),(120,107),(126,104),(126,115),(120,117),(114,115)],fill='#f6e0ba')
d.line((120,107,120,117),fill='#8f6790')
for x,y in [(40,126),(168,126),(21,152),(219,152)]:
 d.arc((x-13,y-10,x+13,y+10),200,350,fill='#9ac7b4',width=2)
 d.ellipse((x-2,y-3,x+2,y+1),fill='#f4c6b5')
for _ in range(230):
 x=r.randrange(12,229);y=r.randrange(12,148)
 if r.random()<.65:d.point((x,y),fill='#e7d0b4' if r.random()<.4 else '#97b4c8')
# outer frame and an inviting return passage
for x in (9,230):d.line((x,9,x,153),fill='#6b7191',width=2)
d.arc((5,3,234,92),185,355,fill='#a0a3b5',width=2)
im.resize((1920,1280),Image.Resampling.NEAREST).save(MD/'hall_of_tomorrow.png',optimize=True)
print('generated map',MD/'hall_of_tomorrow.png')
# Render themed icons with separate editable pixel shapes.
icons=['hall','mirror','flower','sketch','page']
palette={'hall':('#776388','#f3d5a4'),'mirror':('#587c9c','#c1e1ee'),'flower':('#b46c86','#fbe5b0'),'sketch':('#726d92','#e5c7ab'),'page':('#707a92','#f5e4ca')}
for key in icons:
 B=48;tile=Image.new('RGBA',(B,B),(0,0,0,0));p=ImageDraw.Draw(tile)
 a,b=palette[key]
 p.rounded_rectangle((6,7,41,42),radius=5,fill=a,outline='#ead1b2',width=2)
 if key=='hall':
  p.pieslice((11,6,36,34),180,360,fill=b,outline='#413f6c',width=2);p.rectangle((13,20,34,39),fill='#26365e',outline=b,width=2)
  p.line((23,20,23,37),fill=b,width=2)
 if key=='mirror':
  p.ellipse((12,10,36,35),fill='#37516b',outline=b,width=3);p.line((18,18,31,16),fill='#bbdfea',width=2);p.line((15,27,25,20),fill='#f6dfbd',width=2)
 if key=='flower':
  for x,y in [(23,16),(15,23),(31,23),(23,31)]:p.ellipse((x-6,y-6,x+6,y+6),fill='#f3bed1')
  p.ellipse((20,20,26,26),fill='#f7d99c');p.line((24,29,25,38),fill='#76b995',width=2)
 if key=='sketch':
  p.polygon([(12,12),(34,13),(34,37),(12,35)],fill=b,outline='#4d4a65')
  p.line((18,27,28,18),fill='#c2878c',width=3);p.line((18,31,30,22),fill='#769da7',width=2)
 if key=='page':
  p.polygon([(12,12),(29,12),(37,20),(37,38),(12,38)],fill=b,outline='#4d5175');p.line((29,12,29,20,37,20),fill='#8f87a4',width=2)
  p.line((17,26,32,26),fill='#c8a39c',width=2);p.line((17,32,29,32),fill='#c8a39c',width=2)
 tile.resize((192,192),Image.Resampling.NEAREST).save(ID/('v472_c06_'+key+'.png'),optimize=True)
 print('generated icon',key)
