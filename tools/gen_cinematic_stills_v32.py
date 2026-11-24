"""Twelve story-specific original in-engine composite stills, no externally licensed art.
Run after tools/visual_overhaul_v32.py. Source is existing game map raster + original frame art.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance
import random, hashlib, math
P=Path(__file__).resolve().parents[1]
A=P/'android/assets'
O=A/'ui/v32_cinema';O.mkdir(parents=True,exist_ok=True)
SCENES={
 'arland_morning':'arland_room','sofia_morning':'sofia_room','plaza_intro':'plaza',
 'garden_portal':'memory_garden','library':'perpustakaan','archive':'ruang_arsip',
 'pier':'dermaga','rain':'jalan_kota','reunion':'taman_kota','sky':'bukit_bintang',
 'quiet':'eternal_garden','lantern':'lantern_field',
}
for sid,mid in SCENES.items():
 rng=random.Random(int.from_bytes(hashlib.sha256(sid.encode()).digest()[:8],'big'))
 img=Image.open(A/'maps'/f'{mid}.png').convert('RGB')
 # Canonical 768x432 with cover-crop, preserve crisp pixel-grid geometry.
 w,h=img.size;s=max(768/w,432/h)
 nw,nh=round(w*s),round(h*s)
 img=img.resize((nw,nh),Image.Resampling.NEAREST)
 sx=(nw-768)//2;sy=(nh-432)//2
 img=img.crop((sx,sy,sx+768,sy+432)).convert('RGBA')
 # Story mood color grade: remain clearly different for each chapter.
 grade=Image.new('RGBA',(768,432),(0,0,0,0))
 g=ImageDraw.Draw(grade,'RGBA')
 if sid in ('rain','quiet','archive'): tint=(49,39,87,105)
 elif sid in ('lantern','reunion','pier'): tint=(245,150,93,62)
 elif sid in ('garden_portal','sky'): tint=(124,87,181,65)
 else:tint=(229,153,135,32)
 g.rectangle((0,0,768,432),fill=tint)
 img=Image.alpha_composite(img,grade)
 fx=Image.new('RGBA',(768,432));d=ImageDraw.Draw(fx,'RGBA')
 # Widescreen artbook frame, gradient lines, 4 star/flower corner accents.
 d.rectangle((7,7,760,424),outline=(248,217,168,226),width=4)
 d.rectangle((14,14,753,417),outline=(241,176,198,184),width=2)
 for cx,cy in ((29,29),(739,29),(29,403),(739,403)):
    d.line((cx-12,cy,cx+12,cy),fill=(255,234,182,232),width=3)
    d.line((cx,cy-12,cx,cy+12),fill=(255,234,182,232),width=3)
    d.polygon((cx,cy-7,cx+7,cy,cx,cy+7,cx-7,cy),fill=(255,211,164,238))
 for i in range(155):
    x=rng.randrange(30,740);y=rng.randrange(30,400)
    if rng.random()<.72:d.rectangle((x,y,x+rng.randrange(1,4),y+rng.randrange(1,4)),fill=(253,221,187,rng.randrange(70,220)))
    else:d.line((x-4,y,x+4,y),fill=(251,180,208,190),width=1)
 if sid in ('lantern','reunion','pier'):
    for i in range(12):
      x=rng.randrange(30,738);y=rng.randrange(50,335)
      d.polygon((x-7,y,x+7,y,x+4,y+15,x-4,y+15),fill=(255,194,102,204))
      d.line((x-3,y+3,x+3,y+3),fill=(255,239,185,255),width=2)
 if sid in ('rain',):
    for i in range(75):
        x=rng.randrange(50,715);y=rng.randrange(40,385)
        d.line((x,y,x-7,y+22),fill=(194,215,255,155),width=2)
 if sid in ('quiet','garden_portal','sky'):
    for i in range(16):
        x=rng.randrange(80,675);y=rng.randrange(55,360)
        d.ellipse((x-12,y-12,x+12,y+12),outline=(226,188,250,135),width=2)
 img=Image.alpha_composite(img,fx)
 img.convert('RGB').save(O/(sid+'.png'),optimize=True)
 print(sid,mid)
print('v3.2 cinema stills:',len(SCENES))
