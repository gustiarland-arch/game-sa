#!/usr/bin/env python3
"""Original editable-source pixel art for Chapter4. No rasterized interface text."""
from pathlib import Path
from PIL import Image,ImageDraw
OUT=Path(__file__).resolve().parents[1]/'android/assets/items';OUT.mkdir(parents=True,exist_ok=True)
def save(im,name):
 im.resize((192,192),Image.Resampling.NEAREST).save(OUT/('v470_c04_'+name+'.png'))
def blank():
 im=Image.new('RGBA',(48,48));return im,ImageDraw.Draw(im)
# Empty seat with gallery window and warm auditorium light.
im,d=blank();d.rounded_rectangle((5,5,43,43),radius=3,fill='#504960',outline='#302e43',width=2)
d.rectangle((9,8,39,25),fill='#cca49c');d.rectangle((11,10,37,23),fill='#f5d1af')
d.rectangle((14,13,16,18),fill='#fff0c6');d.line((26,9,26,24),fill='#9c8193',width=2)
d.rectangle((14,27,35,31),fill='#ad7c91');d.rectangle((12,24,38,29),fill='#b38b93')
d.rectangle((15,31,18,40),fill='#dfb9ae');d.rectangle((32,31,35,40),fill='#dfb9ae')
d.line((13,41,36,41),fill='#3c354b',width=2);save(im,'seat')
# Readable hand-written letter with visible folds and spaces for writing.
im,d=blank();d.polygon([(5,10),(35,6),(43,16),(38,40),(10,43)],fill='#f7e6d2')
d.line([(5,10),(35,6),(43,16),(38,40),(10,43),(5,10)],fill='#65536b',width=2)
d.line([(35,6),(33,17),(43,16)],fill='#d9bfae',width=2)
for y,x2 in [(17,31),(23,35),(29,26),(35,31)]:d.line((12,y,x2,y-1),fill='#8f7891',width=2)
d.polygon([(8,40),(15,36),(24,40),(18,44)],fill='#cf9caf');save(im,'letter')
# Enchanted five-lantern memory.
im,d=blank();d.ellipse((3,4,44,45),fill='#5b5275',outline='#b8a1c8',width=2)
for x,y,c in [(11,16,'#f4bb94'),(24,10,'#f6e6ae'),(36,17,'#a7d4d4'),(15,33,'#f2adc4'),(33,33,'#e8d0a3')]:
 d.ellipse((x-5,y-4,x+5,y+5),fill='#766c91');d.polygon([(x-3,y),(x,y-4),(x+3,y),(x,y+4)],fill=c)
 d.rectangle((x-1,y+5,x+1,y+9),fill='#d8c4a8')
d.line((10,24,37,24),fill='#a78cae',width=1);save(im,'lantern')
# Personal promise with two notes, slight crease and sprig of green.
im,d=blank();d.rounded_rectangle((7,8,41,41),radius=2,fill='#e9d8c5',outline='#61516e',width=2)
d.polygon([(11,11),(33,11),(33,31),(11,33)],fill='#fff0d8')
d.line((15,17,29,17),fill='#99869a',width=2);d.line((15,22,26,22),fill='#99869a',width=1)
d.line((15,27,23,27),fill='#99869a',width=1)
d.line((27,35,34,28,35,25),fill='#649c86',width=3)
d.ellipse((23,29,29,33),fill='#88b49a');save(im,'promise')
# Small projector with original graphic geometry, not brand logos.
im,d=blank();d.polygon([(5,18),(38,14),(42,36),(8,40)],fill='#5c566a')
d.rounded_rectangle((7,12,40,33),radius=3,fill='#8c8294',outline='#47415a',width=2)
d.ellipse((22,15,36,29),fill='#f1d2ab',outline='#474158',width=2)
d.ellipse((27,19,32,24),fill='#fff3c9');d.rectangle((12,16,19,20),fill='#61586f')
d.rectangle((11,35,36,39),fill='#49475e');save(im,'projector')
print('PASS: 5 generated 192px pixel art items for C04')
