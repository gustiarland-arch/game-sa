#!/usr/bin/env python3
"""Editable original pixel-art icons for C03: no embedded/baked UI text."""
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'android/assets/items';OUT.mkdir(parents=True,exist_ok=True)
def save(im,id):
    im.resize((192,192),Image.Resampling.NEAREST).save(OUT/('v469_c03_'+id+'.png'))
def canvas():
    im=Image.new('RGBA',(48,48));return im,ImageDraw.Draw(im)
# Tender wooden frame; deliberate tiny repaired crack.
im,d=canvas()
d.rounded_rectangle((5,6,43,42),radius=3,fill='#9b795c',outline='#554361',width=3)
d.rectangle((11,12,37,36),fill='#e7d6be')
d.rectangle((13,14,35,34),fill='#8e9db4')
d.rectangle((14,14,34,24),fill='#eac4bc')
d.rectangle((14,25,34,33),fill='#668e85')
d.ellipse((18,18,24,24),fill='#f4d4b6');d.ellipse((27,18,32,24),fill='#f3cdae')
d.line((14,38,18,34,22,39,26,36),fill='#e0c3a5',width=2)
d.line((38,8,37,14,40,17),fill='#f6d6a8',width=1)
save(im,'frame')
# Hand-filled scrapbook with one intentionally blank page.
im,d=canvas()
d.polygon(((7,7),(24,9),(24,42),(7,39)),fill='#ecd6af');d.polygon(((25,9),(42,6),(42,39),(25,42)),fill='#ffebd2')
d.line((24,8,24,42),fill='#604c68',width=2)
d.rectangle((10,12,21,26),fill='#b28aa9');d.rectangle((12,14,19,24),fill='#eed1b8')
d.ellipse((14,16,17,19),fill='#f7b3b9');d.line((10,31,20,29),fill='#896a85',width=2)
d.rectangle((29,14,39,17),fill='#e3b2ad');d.arc((30,22,38,31),0,180,fill='#7e668d',width=1)
d.rectangle((29,33,38,35),fill='#e5d9be')
save(im,'scrapbook')
# Torn letter with vanished half of sentence, subtle ink loss.
im,d=canvas();d.polygon(((8,5),(39,7),(40,40),(32,43),(25,39),(18,43),(9,40)),fill='#f2dfc1')
d.line((8,5,39,7,40,40,32,43,25,39,18,43,9,40,8,5),fill='#655167',width=2)
for y in (13,19,25):d.line((14,y,34 if y<25 else 26,y+1),fill='#7d6d80',width=2)
d.line((14,32,21,33),fill='#bcacb5',width=2)
d.rectangle((27,30,35,32),fill='#ddcbb8');d.rectangle((25,34,33,35),fill='#e9d6c1')
save(im,'letter')
# Exhibition invitation with tiny easel and single empty seat.
im,d=canvas();d.rounded_rectangle((7,5,41,42),radius=2,fill='#f5e8d0',outline='#67506a',width=2)
d.rectangle((11,9,37,15),fill='#be98b3');d.line((14,20,35,20),fill='#8b7990',width=1)
d.rectangle((15,24,30,29),fill='#bca7c9');d.rectangle((18,29,28,32),fill='#977f9e')
d.line((17,32,15,37),fill='#63526d',width=2);d.line((29,32,31,37),fill='#63526d',width=2)
d.line((16,39,34,39),fill='#d0b594',width=1)
save(im,'invitation')
print('PASS: 4 original 192x192 RGBA source-generated C03 memory assets')
