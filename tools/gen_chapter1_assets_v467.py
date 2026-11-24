#!/usr/bin/env python3
"""Reproducible, editable-code original pixel-art item icons (192px PNG)."""
from pathlib import Path
from PIL import Image, ImageDraw

PROJECT=Path(__file__).resolve().parents[1]
OUT=PROJECT/'android/assets/items'
OUT.mkdir(parents=True,exist_ok=True)
SCALE=4

def new():
    return Image.new('RGBA',(48,48),(0,0,0,0))

def save(im,name):
    im.resize((192,192),resample=Image.Resampling.NEAREST).save(OUT/name)

# Soft lavender speech ribbons: each character has one voice.
im=new();d=ImageDraw.Draw(im)
d.rounded_rectangle([5,9,31,28],radius=5,fill='#463757',outline='#382d4d',width=2)
d.rounded_rectangle([7,10,29,26],radius=4,fill='#e5cbee')
d.polygon([(13,25),(10,34),(20,26)],fill='#e5cbee')
d.rounded_rectangle([18,20,43,40],radius=4,fill='#504a77',outline='#38375b',width=2)
d.rounded_rectangle([20,21,41,38],radius=3,fill='#b7c5ef')
d.polygon([(37,37),(42,46),(31,38)],fill='#b7c5ef')
for x,y in [(13,17),(18,17),(23,17)]:d.ellipse([x,y,x+2,y+2],fill='#78547e')
for x,y in [(25,29),(30,29),(35,29)]:d.ellipse([x,y,x+2,y+2],fill='#6675ac')
d.line([(15,39),(18,36),(22,39),(26,35)],fill='#ffe6bd',width=2)
save(im,'v467_c01_listening.png')

# Double-page notebook, flower and star coexisting.
im=new();d=ImageDraw.Draw(im)
d.polygon([(7,8),(24,11),(25,42),(7,39)],fill='#f7e2b9')
d.polygon([(24,11),(41,8),(41,39),(25,42)],fill='#e8dbef')
d.line([(24,10),(25,42)],fill='#7c6186',width=2)
d.line([(7,8),(24,11),(41,8)],fill='#76617a',width=2)
d.line([(7,39),(25,42),(41,39)],fill='#76617a',width=2)
for x,y in [(9,30),(10,35),(28,30),(29,35)]:d.line([(x,y),(x+8,y)],fill='#d7b0a1',width=1)
d.line([(15,18),(15,28)],fill='#658b69',width=2)
d.ellipse([11,16,17,22],fill='#f5a4b3');d.ellipse([14,13,20,19],fill='#ed94a6');d.ellipse([17,17,23,22],fill='#f3b6ca')
d.ellipse([15,18,18,21],fill='#f7d885')
d.polygon([(34,14),(36,19),(42,20),(37,23),(38,29),(33,26),(29,28),(30,22),(26,19),(32,18)],fill='#ffd58b')
save(im,'v467_c01_double_page.png')

# Old letter with subtle fading ink, not a full reveal of The Quiet.
im=new();d=ImageDraw.Draw(im)
d.polygon([(9,6),(36,7),(40,38),(12,42)],fill='#fbdfa7')
d.line([(9,6),(36,7),(40,38),(12,42),(9,6)],fill='#8b6a6a',width=2)
d.line([(15,14),(34,14)],fill='#9f7a81',width=2)
d.line([(15,19),(30,19)],fill='#a68c91',width=2)
d.line([(15,24),(24,24)],fill='#b5a8a2',width=2)
d.line([(27,24),(35,24)],fill='#d5beb5',width=1)
d.line([(15,29),(21,29)],fill='#a68c91',width=2)
d.line([(23,29),(28,29)],fill='#d6bdb2',width=1)
d.line([(31,29),(35,29)],fill='#f4dbbb',width=1)
d.polygon([(31,2),(33,8),(39,10),(34,13),(35,19),(30,16),(25,18),(27,11),(23,8),(29,8)],fill='#e5c7ff')
save(im,'v467_c01_fading_ink.png')
print('PASS: three original chapter-one icons generated at 192x192 (pixel scaling).')
