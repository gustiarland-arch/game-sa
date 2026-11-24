#!/usr/bin/env python3
"""Generate three editable pixel icons for the story's Chapter 6/epilogue."""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'android/assets/items'
OUT.mkdir(parents=True,exist_ok=True)

def frame(d,sky,soft):
    for i in range(5):
        d.rectangle((2+i,2+i,45-i,45-i),outline=soft if i==0 else sky)
    d.rectangle((5,5,42,42),fill=sky)
    for x,y in [(10,9),(35,8),(9,35),(39,34),(23,7)]:
        d.point((x,y),fill=soft)

def letter_arland():
    im=Image.new('RGBA',(48,48));d=ImageDraw.Draw(im)
    frame(d,'#2a3654','#bc9fba')
    d.rectangle((10,14,38,37),fill='#ebd9bd',outline='#987f8b',width=2)
    d.polygon([(10,14),(24,25),(38,14)],fill='#f5e6c9')
    d.line([(12,15),(24,27),(36,15)],fill='#c7a698',width=2)
    d.rectangle((14,29,31,30),fill='#b28c80')
    d.rectangle((16,33,29,34),fill='#b28c80')
    d.rectangle((15,8,25,18),fill='#e8a2ac')
    d.rectangle((19,6,23,15),fill='#e8a2ac')
    d.point((21,10),fill='#fff1d5')
    return im

def letter_sofia():
    im=Image.new('RGBA',(48,48));d=ImageDraw.Draw(im)
    frame(d,'#353b52','#cdb0aa')
    d.rectangle((11,9,36,39),fill='#f0e3ce',outline='#947e8d',width=2)
    d.rectangle((16,16,31,17),fill='#b7a39d')
    d.rectangle((16,20,28,21),fill='#b7a39d')
    d.rectangle((16,24,30,25),fill='#b7a39d')
    d.rectangle((16,28,25,29),fill='#b7a39d')
    d.rectangle((18,33,30,35),fill='#8e6b79')
    d.rectangle((21,30,27,33),fill='#a47d81')
    d.point((24,34),fill='#ffd7b2')
    return im

def gallery_return():
    im=Image.new('RGBA',(48,48));d=ImageDraw.Draw(im)
    frame(d,'#30425a','#e5b7ab')
    d.rectangle((10,10,37,35),fill='#80647c',outline='#dec3b5',width=2)
    d.rectangle((14,14,33,31),fill='#f2d6b8')
    d.rectangle((18,24,28,26),fill='#93667f')
    d.rectangle((17,21,29,23),fill='#b5898e')
    d.rectangle((19,26,21,30),fill='#6f5065')
    d.rectangle((26,26,28,30),fill='#6f5065')
    d.rectangle((15,32,32,33),fill='#b48b7f')
    d.rectangle((22,36,25,42),fill='#dec3b5')
    d.rectangle((15,42,32,43),fill='#dec3b5')
    d.rectangle((30,9,33,12),fill='#ffe0aa')
    return im

for name,fn in [('v466_letter_arland',letter_arland),('v466_letter_sofia',letter_sofia),('v466_gallery_revisit',gallery_return)]:
    fn().resize((192,192),Image.Resampling.NEAREST).save(OUT/(name+'.png'))
    print('Created',name)
