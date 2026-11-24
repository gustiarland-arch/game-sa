#!/usr/bin/env python3
"""Original editable pixel-art generator for Prologue v4.7.4 (4x nearest)."""
from pathlib import Path
from PIL import Image, ImageDraw
OUT=Path(__file__).resolve().parents[1]/'android/assets/items';OUT.mkdir(exist_ok=True,parents=True)
INK='#53415c';PAPER='#fff0d5';PINK='#e9a4b7';LILAC='#ab91ca';GOLD='#efc878';GREEN='#6c9c75'
def canvas():
 im=Image.new('RGBA',(48,48),(0,0,0,0));return im,ImageDraw.Draw(im)
def save(im,name):im.resize((192,192),Image.Resampling.NEAREST).save(OUT/name)
# Handmade flower with not-quite-perfect petals (distinguished from base gift)
im,d=canvas();d.ellipse((7,39,41,46),fill='#493e57');d.line([(24,41),(22,30),(23,20)],fill=GREEN,width=3)
for box in [(13,15,28,28),(18,8,32,26),(24,14,38,30),(12,23,29,35),(23,25,38,36)]:
 d.ellipse(box,fill=PINK,outline=INK,width=1)
d.ellipse((19,20,28,28),fill=GOLD,outline=INK,width=1)
d.line([(21,34),(27,38),(24,42)],fill=LILAC,width=3);d.line([(24,38),(31,36)],fill=LILAC,width=3)
d.line([(8,10),(11,7),(14,10)],fill='#fff8e1',width=2)
save(im,'v474_folded_flower.png')
# Personal postcard; handmade corner symbol and ruled letter
im,d=canvas();d.polygon([(7,7),(39,5),(43,40),(10,43)],fill=PAPER);d.line([(7,7),(39,5),(43,40),(10,43),(7,7)],fill=INK,width=2)
d.line([(15,15),(32,14)],fill=LILAC,width=2)
for y in (22,27,32):d.line([(14,y),(30+(2 if y==22 else 0),y-1)],fill='#bd8b84',width=1)
d.polygon([(34,25),(36,29),(41,30),(37,33),(38,38),(34,35),(30,36),(32,32),(29,29),(33,29)],fill=GOLD)
save(im,'v474_postcard.png')
# Ribbon choices that are drawn rather than hard-coded graphic text
im,d=canvas();d.ellipse((5,32,43,44),fill='#55465b')
d.polygon([(24,23),(6,12),(8,4),(25,18)],fill='#dcc79a',outline=INK)
d.polygon([(24,23),(41,7),(39,3),(23,17)],fill=LILAC,outline=INK)
d.ellipse((17,15,29,29),fill=GOLD,outline=INK,width=2)
d.polygon([(22,27),(17,44),(24,39),(32,45),(28,26)],fill=LILAC,outline=INK)
save(im,'v474_ribbon.png')
# Two halves of an unfinished memory fragment
im,d=canvas();d.polygon([(10,8),(23,10),(23,38),(8,41)],fill='#eac0bd',outline=INK)
d.polygon([(25,12),(40,5),(42,37),(26,41)],fill='#b8b2e5',outline=INK)
d.polygon([(24,4),(27,12),(36,13),(29,19),(31,29),(23,23),(16,29),(19,19),(12,13),(21,12)],fill='#ffe4a3')
d.line([(23,10),(25,14),(23,20),(25,28),(23,38)],fill='#735c83',width=2)
save(im,'v474_shard.png')
print('PASS: four editable-source pixel icons, 192px RGBA')
