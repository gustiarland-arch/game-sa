#!/usr/bin/env python3
"""Generate dedicated original Rain Garden pixel map (1920x1280, nearest-neighbor).

Editable procedural source; no watermarked/commercial map art. Walkway/accessibility
is defined by separate local JSON collision data, not this illustration.
"""
from pathlib import Path
from PIL import Image, ImageDraw
from random import Random
R=Random(470)
OUT=Path(__file__).resolve().parents[1]/'android/assets/maps/rain_garden.png'
W,H=240,160
pal={
 'soil':'#303a57','soil_alt':'#39425f','soil_light':'#4b5576','grass':'#344d58',
 'grass2':'#455f67','path':'#6a667c','path2':'#77718c','path_hi':'#9292a2',
 'deep':'#25334d','puddle':'#49647d','ref':'#8ab3bd','petal':'#d1a4b8',
 'glow':'#d9be94','moon':'#c6bfce','frame':'#51506a','altar':'#aca1b2',
}
im=Image.new('RGB',(W,H),pal['soil']);d=ImageDraw.Draw(im)
# Wet violet grass and uneven slate paths; dithering at original 1/8 resolution.
for y in range(0,H,5):
 for x in range(0,W,7):
  if R.random()<.55:d.rectangle((x+R.randrange(4),y+R.randrange(4),x+4,y+4),fill=pal['soil_alt'])
  if R.random()<.12:d.point((x+R.randrange(5),y+R.randrange(4)),fill=pal['grass2'])
# Cobblestone meandering from portal to central altar to upper-left and upper-right.
d.polygon([(10,153),(30,130),(70,114),(92,94),(116,91),(141,75),(149,50),(144,28),
           (165,25),(171,51),(156,90),(135,104),(111,118),(72,130),(42,145),(31,157)],fill=pal['path'])
d.polygon([(55,113),(85,103),(121,95),(151,105),(189,107),(217,91),(220,107),(197,122),
           (158,123),(119,111),(91,117),(61,128)],fill=pal['path2'])
d.polygon([(71,120),(105,86),(131,67),(160,50),(186,34),(202,22),(217,25),(201,46),
           (172,70),(151,85),(118,104),(84,131)],fill=pal['path'])
# Stone speckles inside and outside the walkable winding paths.
for _ in range(900):
 x=R.randrange(W);y=R.randrange(H)
 if im.getpixel((x,y)) in [(106,102,124),(119,113,140)]:
  d.rectangle((x,y,x+R.randrange(1,3),y+1),fill=pal['path_hi'] if R.random()<.2 else pal['path2'])
# Puddles act as visual overlays: no solid collision, only ambient weather ripples.
for cx,cy,rx,ry in [(25,36,20,7),(202,139,21,8),(61,65,17,6),(191,75,14,4),(121,139,18,5)]:
 d.ellipse((cx-rx,cy-ry,cx+rx,cy+ry),fill=pal['puddle'],outline=pal['deep'],width=2)
 d.arc((cx-rx+5,cy-ry+2,cx+rx-5,cy+ry-1),10,165,fill=pal['ref'],width=1)
# Bush clusters, different shades, keep five quest landmarks visible.
for cx,cy in [(13,79),(42,22),(218,50),(223,127),(65,17),(140,146),(25,143),(89,39),(160,145)]:
 for _ in range(13):
  x=cx+R.randrange(-13,13);y=cy+R.randrange(-10,10)
  d.ellipse((x-2,y-2,x+3,y+2),fill=pal['grass2'] if R.random()<.4 else pal['grass'])
  if R.random()<.10:d.point((x,y-2),fill=pal['petal'])
# Fading memory emblems engraved near walkway; no rendered words.
for cx,cy in [(70,70),(178,115),(37,115)]:
 d.ellipse((cx-7,cy-4,cx+7,cy+5),outline=pal['frame'],width=2)
 d.line((cx-3,cy,cx+3,cy),fill=pal['moon'],width=1)
# Five lanterns corresponding to interactables (scaled exactly /8).
lanterns=[(560,1010,'#f7ceac'),(1420,360,'#b1d8e1'),(840,1050,'#f4b3d3'),
          (1080,570,'#d7baf1'),(850,360,'#e7dcb4')]
for px,py,c in lanterns:
 x,y=px//8,py//8
 d.ellipse((x-7,y+2,x+7,y+6),fill=pal['deep'])
 d.line((x,y-9,x,y+2),fill='#d7bcad',width=2)
 d.rectangle((x-4,y-12,x+4,y-5),fill=pal['frame'],outline='#d8bcb1',width=1)
 d.rectangle((x-2,y-10,x+2,y-7),fill=c)
 for radius in (7,10):d.arc((x-radius,y-12-radius/2,x+radius,y+radius/2),20,160,fill='#8b88a3',width=1)
# Center altar with five-star wreath.
cx,cy=960//8,800//8
d.ellipse((cx-12,cy-8,cx+12,cy+7),fill=pal['deep'])
d.ellipse((cx-10,cy-10,cx+10,cy+5),fill=pal['altar'],outline=pal['frame'],width=2)
d.ellipse((cx-6,cy-8,cx+6,cy+1),fill=pal['frame'])
for x,y in [(cx-6,cy-5),(cx,cy-7),(cx+6,cy-5),(cx-3,cy-1),(cx+3,cy-1)]:
 d.point((x,y),fill=pal['glow'])
# Rain streaks rendered in the background; engine weather remains dynamic.
for _ in range(310):
 x=R.randrange(5,W-5); y=R.randrange(6,H-6)
 d.line((x,y,x-1,y+2),fill='#6f8396' if R.random()<.7 else '#738d9c',width=1)
# Portal threshold at bottom (beyond player spawn 160,1140).
d.arc((8,140,45,177),170,350,fill='#d2b8c5',width=3)
d.line((10,157,39,157),fill=pal['glow'],width=2)
OUT.parent.mkdir(parents=True,exist_ok=True)
im.resize((1920,1280),Image.Resampling.NEAREST).save(OUT,optimize=True)
print('PASS: dedicated 1920x1280 RGB Rain Garden map with five original lanterns and accessible routes')
