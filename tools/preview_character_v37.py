#!/usr/bin/env python3
"""Before/after contact sheet made strictly from project source PNGs; NOT in-game screenshot."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'docs/preview/v37_sprite_atlas_comparison.png'
OUT.parent.mkdir(parents=True,exist_ok=True)
W,H=1460,750
canvas=Image.new('RGB',(W,H),(22,23,40));d=ImageDraw.Draw(canvas)
try:
 font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',24)
 title=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',31)
except OSError:font=ImageFont.load_default();title=font

def T(p,s,fill=(240,232,228),big=False): d.text(p,s,font=title if big else font,fill=fill)
T((34,20),'ARLAND & SOFIA  /  ANIMASI v3.7',big=True)
T((34,62),'Perbandingan dari spritesheet nyata di source (bukan screenshot APK).',(186,191,207))
for rid,char in enumerate(('arland','sofia')):
 y=123+rid*295
 T((35,y),char.upper(),(255,203,176),True)
 for col,(name,n) in enumerate((('walk_v32.png',12),('walk_v37.png',16))):
  x=35+col*715
  T((x,y+45),('LAMA  /  12 frame' if col==0 else 'BARU  /  16 frame'),(180,202,222))
  with Image.open(ROOT/'android/assets/characters'/char/name) as img:
   img=img.convert('RGBA')
   # eight distributed front-facing frames, pixel perfect 2x
   indices=[round(i*(n-1)/7) for i in range(8)]
   for i,j in enumerate(indices):
    cell=img.crop((j*48,0,(j+1)*48,72)).resize((72,108),Image.Resampling.NEAREST)
    canvas.paste(cell,(x+i*86,y+105),cell)
 # minor separator
 d.line((34,y+254,1425,y+254), fill=(82,85,114),width=2)
T((35,715),'Alur karakter, collision, cerita, save, musik, dan peta v3.6 dipertahankan.',(169,195,181))
canvas.save(OUT,optimize=True)
print('PREVIEW:',OUT)
