"""Generated, editable visual FX atlas fragments (no external licensed assets).
Usage: python3 tools/gen_visual_fx.py android/assets
Outputs PNGs in android/assets/fx. Runtime never needs Python.
"""
from pathlib import Path
import sys
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

root = Path(sys.argv[1] if len(sys.argv)>1 else 'android/assets') / 'fx'
root.mkdir(parents=True, exist_ok=True)


def save(name, image):
    image.save(root / name)

# Subtle edge shading, transparent in the central ~60% of the view.
n=256
y,x=np.mgrid[0:n,0:n]
dx=np.abs(x-(n-1)/2)/((n-1)/2)
dy=np.abs(y-(n-1)/2)/((n-1)/2)
rad=np.sqrt((dx*0.77)**2+(dy*0.96)**2)
a=np.clip((rad-0.37)/0.82,0,1)**1.6
z=np.empty((n,n,4),dtype=np.uint8)
z[:,:,:3]=(23,13,32)
z[:,:,3]=np.uint8(a*150)
save('vignette.png',Image.fromarray(z,'RGBA'))

# Character feet: dispersed dust puff (diffuse, small, low opacity).
n=32
y,x=np.mgrid[:n,:n]
r=np.sqrt(((x-15.5)/15.5)**2+((y-15.5)/15.5)**2)
a=(np.clip(1-r,0,1)**2.6*160).astype('uint8')
z=np.zeros((n,n,4),dtype='uint8')
z[:,:,:3]=(255,236,201);z[:,:,3]=a
save('dust.png',Image.fromarray(z,'RGBA'))

# Animated water surface ripples and a small splash.
im=Image.new('RGBA',(48,20)); d=ImageDraw.Draw(im)
d.ellipse((1,8,46,18),outline=(191,234,255,150),width=2)
d.arc((9,10,38,17),0,180,fill=(249,255,255,185),width=2)
save('ripple.png',im.filter(ImageFilter.GaussianBlur(0.25)))
im=Image.new('RGBA',(28,28));d=ImageDraw.Draw(im)
d.ellipse((3,18,24,24),outline=(191,232,255,155),width=2)
for x0,y0 in [(7,10),(14,4),(21,13)]:
    d.ellipse((x0,y0,x0+3,y0+5),fill=(239,251,255,185))
save('splash.png', im)

# Foreground sakura-style petals (original, not a stock sprite).
im=Image.new('RGBA',(32,24)); d=ImageDraw.Draw(im)
d.polygon([(3,13),(8,6),(21,2),(30,7),(23,15),(11,20)], fill=(255,195,219,230),outline=(212,125,170,230))
d.polygon([(4,13),(14,10),(23,7),(12,17)],fill=(255,225,232,205))
d.line([(7,15),(21,7)],fill=(221,149,181,160),width=1)
save('petal.png',im)

# Floating heart for rare high-affection companion idle cues.
im=Image.new('RGBA',(28,28)); d=ImageDraw.Draw(im)
d.ellipse((2,5,16,19),fill=(248,168,195,235));d.ellipse((12,5,26,19),fill=(248,168,195,235))
d.polygon([(2,13),(26,13),(14,27)], fill=(248,168,195,235))
d.line([(7,8),(11,6)],fill=(255,241,250,180),width=2)
save('heart.png',im)

print('Visual FX: 6 PNGs generated ->',root)
