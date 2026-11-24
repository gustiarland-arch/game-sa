#!/usr/bin/env python3
"""Editable source generator for new Chapter-2 original pixel art at 192px."""
from pathlib import Path
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'android/assets/items'
OUT.mkdir(parents=True,exist_ok=True)

def new():return Image.new('RGBA',(48,48))
def save(im,name): im.resize((192,192),Image.Resampling.NEAREST).save(OUT/name)
# Two photo strips and strange lantern glow.
im=new();d=ImageDraw.Draw(im)
d.rounded_rectangle((8,3,35,45),radius=3,fill='#fff1d7',outline='#6f4e71',width=2)
for y in (8,20,32):
 d.rectangle((12,y,31,y+10),fill='#8a7fb0')
 d.rectangle((14,y+2,29,y+8),fill='#d7a4b5')
 d.rectangle((15,y+7,28,y+8),fill='#83a4a0')
 d.ellipse((16,y+2,21,y+7),fill='#ffe2bc')
 d.ellipse((23,y+2,28,y+7),fill='#f7d2b1')
 d.line((20,y+2,20,y+4),fill='#554565',width=1)
d.ellipse((26,10,43,27),fill='#ffeaa0')
d.ellipse((29,13,40,24),fill='#ffd16e')
d.line((34,17,34,29),fill='#fbffd0',width=2)
d.polygon(((33,20),(38,22),(35,32),(29,25)),fill='#fff9cc')
save(im,'v468_c02_lantern.png')
# Paper calendar for postponed invitation.
im=new();d=ImageDraw.Draw(im)
d.rounded_rectangle((7,8,41,41),radius=3,fill='#f5e9cf',outline='#534661',width=2)
d.rectangle((8,9,40,19),fill='#9f8ac2')
for x in (15,33):d.rectangle((x,5,x+3,12),fill='#e0cbab')
for y in (23,29,35):
 for x in (14,23,32):d.rectangle((x,y,x+3,y+3),fill='#bba9b1')
d.polygon(((19,29),(26,22),(33,29),(26,37)),fill='#f3b1b7')
d.line((22,30,25,33,30,27),fill='#f8eada',width=2)
save(im,'v468_c02_calendar.png')
# Sofia's sketch: negative space between two chairs.
im=new();d=ImageDraw.Draw(im)
d.polygon(((8,5),(36,7),(42,39),(11,43)),fill='#f1e0b9')
d.line((8,5,36,7,42,39,11,43,8,5),fill='#634d60',width=2)
d.line((14,34,36,33),fill='#b4a28e',width=2)
for x in (17,32):
 d.rectangle((x-4,19,x+2,24),fill='#af7a67')
 d.line((x-3,24,x-3,33),fill='#655064',width=2)
 d.line((x+1,24,x+1,32),fill='#655064',width=2)
d.line((23,21,27,20),fill='#d7b0a3',width=1)
d.arc((18,10,32,23),200,320,fill='#e69aac',width=2)
save(im,'v468_c02_sketch.png')
print('PASS: 3 editable, original Chapter-2 pixel assets 192px RGBA')
