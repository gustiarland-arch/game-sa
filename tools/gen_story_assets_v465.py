#!/usr/bin/env python3
"""Original editable low-resolution memory icon for completed relationship growth."""
from pathlib import Path
from PIL import Image, ImageDraw
BASE=Path(__file__).resolve().parents[1]
OUT=BASE/'android/assets/items/v465_bench_memory.png'
OUT.parent.mkdir(parents=True,exist_ok=True)
im=Image.new('RGBA',(48,48),(0,0,0,0));d=ImageDraw.Draw(im)
# Pixel art bench and second written page: simple symbolic collectible.
d.rounded_rectangle((4,4,43,43),radius=6,fill='#2d304d',outline='#e8b8aa',width=2)
d.rectangle((9,10,37,37), fill='#f7e8d3');d.rectangle((32,12,38,36),fill='#edcaba')
d.rectangle((14,22,34,26),fill='#8d5c62');d.rectangle((13,18,35,21),fill='#ab7781')
d.rectangle((15,26,18,33),fill='#4c3b54');d.rectangle((30,26,33,33),fill='#4c3b54')
d.rectangle((11,9,16,12),fill='#eab8ad');d.rectangle((22,11,26,15),fill='#eab8ad')
d.rectangle((10,34,23,35),fill='#c9aa8f');d.rectangle((10,37,29,38),fill='#c9aa8f')
d.point((18,9),fill='#f5d9aa');d.point((35,7),fill='#f5d9aa')
im.resize((192,192),Image.Resampling.NEAREST).save(OUT)
print('Generated original v4.6.5 memory icon:',OUT)
