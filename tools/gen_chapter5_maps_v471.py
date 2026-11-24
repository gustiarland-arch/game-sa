#!/usr/bin/env python3
"""Editable original 240x160 pixel tile-map art, upscaled x8 for 1920x1280 LibGDX."""
from pathlib import Path
from PIL import Image,ImageDraw
from random import Random
ROOT=Path(__file__).resolve().parents[1]
DST=ROOT/'android/assets/maps';DST.mkdir(parents=True,exist_ok=True)
SZ=(240,160);S=8
COLS={
 'clockwork_station':['#212d46','#303952','#444963','#75697a','#ab91a0','#f1cf9f','#b2daeb'],
 'moonlight_lake':['#152a44','#23435b','#30566c','#3f7485','#89b5c0','#e2cfb1','#ffd2b6'],
 'memory_bridge':['#202a50','#354267','#536184','#7a82a2','#c0b5c5','#f1dbba','#b6dced']}
def pixel_cloud(d,r,cx,cy,colors):
 for w,h,dx,dy in [(17,7,-14,-3),(30,9,-2,0),(16,7,13,2)]:d.ellipse((cx+dx-w//2,cy+dy-h//2,cx+dx+w//2,cy+dy+h//2),fill=r.choice(colors))
def crystal(d,x,y,c):
 d.polygon([(x,y-8),(x+5,y-2),(x+3,y+6),(x,y+9),(x-4,y+5),(x-5,y-3)],fill=c[5],outline=c[3]);d.line((x,y-6,x,y+6),fill=c[6],width=1)
def glow(d,x,y,color):
 for radius,col in [(10,'#42516b'),(7,'#627187'),(4,color)]:d.ellipse((x-radius,y-radius/2,x+radius,y+radius/2),fill=col)
def base(name,seed):
 r=Random(seed);c=COLS[name];im=Image.new('RGB',SZ,c[0]);d=ImageDraw.Draw(im)
 for i in range(0,160,8):
  for j in range(0,240,8):
   if r.random()<.44:d.rectangle((j+r.randint(0,4),i+r.randint(0,4),j+7,i+7),fill=c[1])
 for _ in range(1500):
  x=r.randrange(240);y=r.randrange(160)
  d.point((x,y),fill=c[4] if r.random()<.10 else c[2])
 return im,d,r,c
def save(im,name):
 out=DST/(name+'.png');im.resize((1920,1280),Image.Resampling.NEAREST).save(out,optimize=True)
 print('generated',out.name,out.stat().st_size)
# Clockwork Station: physical tile path between 3 memory cog positions + 2 levers.
im,d,r,c=base('clockwork_station',47101)
d.rectangle((14,20,227,147),fill=c[1],outline=c[4],width=2)
for x in range(23,219,13):
 for y in range(26,140,12):
  if r.random()<.67:d.rectangle((x,y,x+10,y+9),outline=c[2],width=1)
d.polygon([(14,148),(22,110),(55,94),(83,81),(120,45),(161,79),(192,93),(216,112),(220,148)],fill=c[2])
d.rectangle((23,105,211,142),fill=c[2])
for x,y,rad in [(55,110,22),(120,43,28),(185,110,22)]:
 d.ellipse((x-rad,y-rad,x+rad,y+rad),fill=c[3],outline=c[5],width=3)
 d.ellipse((x-rad+7,y-rad+7,x+rad-7,y+rad-7),fill=c[1],outline=c[6],width=2)
 for a,b in [(0,-rad+4),(rad-4,0),(0,rad-4),(-rad+4,0)]:d.rectangle((x+a-2,y+b-2,x+a+2,y+b+2),fill=c[5])
 d.line((x,y,x+8,y-4),fill=c[5],width=2)
for x,y in [(85,76),(163,76)]:
 d.rectangle((x-7,y-7,x+7,y+8),fill=c[0],outline=c[5],width=2)
 d.ellipse((x-3,y-3,x+3,y+3),fill=c[6])
for cx,cy in [(36,28),(210,25),(28,136),(207,140)]:crystal(d,cx,cy,c)
for i in range(110):
 x=r.randrange(23,214);y=r.randrange(30,146)
 if r.random()<.22:d.point((x,y),fill=c[5])
save(im,'clockwork_station')
# Moonlight Lake: shallow water, walkable stepping-stone path, symmetrical reflectors.
im,d,r,c=base('moonlight_lake',47102)
d.ellipse((5,12,235,153),fill=c[1],outline=c[4],width=2)
d.ellipse((26,21,222,137),fill=c[2],outline=c[3],width=2)
d.polygon([(12,153),(33,127),(55,110),(75,96),(101,93),(122,74),(141,94),(174,111),(206,132),(234,152)],fill=c[3])
for x,y in [(22,135),(44,118),(72,103),(104,93),(122,79),(140,96),(163,110),(190,122),(218,135)]:
 d.ellipse((x-11,y-4,x+11,y+5),fill=c[4],outline=c[2],width=2)
 d.line((x-6,y,x+7,y-1),fill=c[5],width=1)
for x,y in [(77,65),(165,65),(111,97)]:
 for a in (15,11,7):d.arc((x-a,y-a/2,x+a,y+a/2),15,163,fill=c[4],width=1)
 d.ellipse((x-3,y-6,x+3,y+1),fill=c[6])
for _ in range(330):
 x=r.randrange(24,217);y=r.randrange(23,136)
 if r.random()<.4:d.line((x,y,x+4,y),fill=c[4],width=1)
for x,y in [(33,31),(204,30),(22,123),(222,119)]:crystal(d,x,y,c)
# Reflection mirrors show two different colored halves; center stays unfilled.
d.arc((95,40,119,66),100,270,fill=c[5],width=2)
d.arc((120,40,144,66),270,90,fill=c[6],width=2)
save(im,'moonlight_lake')
# Memory Bridge: fragmented but physically traversable stone weave; five star objects.
im,d,r,c=base('memory_bridge',47103)
for _ in range(22):pixel_cloud(d,r,r.randrange(20,226),r.randrange(16,143),[c[1],c[2]])
# long walkable central field represented as a broad ancient bridge with seams, not a lethal gap
d.polygon([(9,155),(27,131),(43,114),(86,99),(110,85),(143,99),(178,115),(206,138),(231,155)],fill=c[2],outline=c[4])
d.polygon([(38,159),(56,124),(88,99),(111,69),(136,97),(163,121),(184,156)],fill=c[3])
for x,y in [(46,128),(84,93),(120,66),(158,93),(196,128)]:
 d.ellipse((x-12,y-8,x+12,y+9),fill=c[1],outline=c[5],width=2)
 d.line((x-3,y-4,x,y-8),fill=c[6],width=1)
 glow(d,x,y,c[5]);crystal(d,x,y,c)
for x in range(18,218,12):
 y=139-int(50*(1-abs(x-120)/120))
 d.line((x,y,x+4,y+7),fill=c[4],width=1)
for x,y in [(120,32),(105,42),(140,42)]:
 d.ellipse((x-4,y-4,x+4,y+4),outline=c[6],width=1)
 d.point((x,y),fill=c[5])
save(im,'memory_bridge')
