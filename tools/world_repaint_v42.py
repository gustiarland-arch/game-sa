#!/usr/bin/env python3
"""v4.2 directed environment illustration pass for 13 legacy maps.

This paints *walkable surface and scenic details* without changing geometry.
It is intentionally independent of the old v3.x generators: baseline images
are frozen in art_source/world_v42/baseline_maps. Output is deterministic and
written atomically. By default never modifies 9 user-supplied v4 map images.

Usage:
  python3 tools/world_repaint_v42.py
  python3 tools/world_repaint_v42.py --verify-only
  python3 tools/world_repaint_v42.py --restore  # restore original v4.1 maps
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import json, math, random, hashlib, argparse, shutil, os
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / 'android/assets'; D=ASSETS/'data'; SRC=ROOT/'art_source/world_v42'
BASE=SRC/'baseline_maps'; LAY=SRC/'editable_layers'; MAPS=ASSETS/'maps'; DOCS=ROOT/'docs'
NINE=set('jalan_kota perumahan perpustakaan arcade toko_bunga arland_room sofia_room dapur ruang_arsip'.split())
THEMES={
 'plaza':('Hearth of the City','cobblestone','sunny'),
 'taman_kota':('Blossom Pavilion','grass','pond'),
 'riverside':('Blue Riverbank','water','shore'),
 'dermaga':('Lighthouse Pier','water','dock'),
 'cafe':('Sunset Parlour','wood','warm'),
 'bukit_bintang':('Celestial Overlook','grass','stars'),
 'memory_garden':('Garden of Recollections','magic','arch'),
 'eternal_garden':('Garden of Promises','grass','memories'),
 'star_path':('Road Between Stars','magic','stars'),
 'starfall_village':('Lantern Village','cobblestone','village'),
 'lantern_field':('Festival of Wishes','magic','lantern'),
 'hutan_bisik':('Whispering Canopy','grass','forest'),
 'gua_kristal':('Crystal Reverie','crystal','cavern'),
}

def color(rgb,alpha=255):return (*rgb,alpha)
def ring(dr,box,outer,inner=None,w=4):
 dr.ellipse(box,outline=outer,width=w)
 if inner:dr.ellipse(tuple((p+int(w*2) if i<2 else p-int(w*2)) for i,p in enumerate(box)),outline=inner,width=max(1,w//2))

def glow_gradient(w,h,tint,strength=0.17,centers=None):
 """Small stylized warm/cool bounce light; keeps pixel art sharp."""
 y,x=np.mgrid[0:h:1,0:w:1]
 fx=x.astype(np.float32)/w;fy=y.astype(np.float32)/h
 centers=centers or [(0.25,0.14,0.62),(0.83,0.20,0.72)]
 weight=np.zeros((h,w),np.float32)
 for cx,cy,r in centers:
  weight += np.maximum(0,1.0 - np.sqrt((fx-cx)**2+(fy-cy)**2)/r)**2
 a=np.clip(weight*255*strength,0,70).astype('uint8')
 rgba=np.empty((h,w,4),dtype='uint8');rgba[:,:,:3]=tint;rgba[:,:,3]=a
 return Image.fromarray(rgba,'RGBA')

def pixel_material(w,h,seed,style):
 """Coherent pixel clusters rather than high-frequency random noise."""
 rng=random.Random(seed)
 im=Image.new('RGBA',(w,h),(0,0,0,0));dr=ImageDraw.Draw(im,'RGBA')
 # Clustered stone stipples, atmospheric lichen and warm gold specks
 density={'cobblestone':280,'grass':310,'water':510,'wood':240,'magic':350,'crystal':200}[style]
 specs={
 'grass':[(27,99,67,56),(203,226,157,60),(222,187,124,50)],
 'cobblestone':[(251,218,160,69),(117,86,71,45),(237,197,173,40)],
 'water':[(230,255,255,75),(72,140,174,60),(189,222,255,50)],
 'wood':[(255,208,161,63),(103,66,44,55)],
 'magic':[(235,195,255,70),(235,238,196,74),(147,196,247,60)],
 'crystal':[(115,222,255,70),(236,164,245,70)],
 }[style]
 for _ in range(density):
  x=rng.randrange(40,max(w-40,41));y=rng.randrange(38,max(h-38,39))
  c=rng.choice(specs);rx=rng.randint(3,10);ry=rng.randint(2,5)
  if style in ('water','crystal'):
   dr.line((x-2*rx,y,x+2*rx,y),fill=c,width=rng.choice([1,2,3]));
   if rng.randrange(8)==0:dr.line((x-rx,y-4,x+rx,y-4),fill=c,width=1)
  elif style=='cobblestone':
   dr.line((x-2*rx,y,x+2*rx,y),fill=c,width=2)
   dr.line((x+rx//2,y,x+rx//2,y+ry),fill=(97,69,71,45),width=2)
  else:
   dr.polygon([(x-rx,y),(x-rx//2,y-ry),(x+rx,y-ry//2),(x+rx+3,y+ry)],fill=c)
 return im

def pixel_line(dr,points,col,w=6):dr.line(points,fill=col,width=w,joint='curve')
def shrine(dr,x,y,r,colors):
 # radial mandala laid on the floor, not a blocking object
 rim,light,dark=colors
 ring(dr,(x-r,y-int(r*.62),x+r,y+int(r*.62)),rim,light,7)
 ring(dr,(x-int(.7*r),y-int(.46*r),x+int(.7*r),y+int(.46*r)),dark,light,4)
 for i in range(16):
  a=i*math.tau/16
  xx=x+int(math.cos(a)*r*.80); yy=y+int(math.sin(a)*r*.48)
  dr.polygon([(xx,yy-10),(xx+8,yy),(xx,yy+10),(xx-8,yy)],fill=light)

def string_lights(dr,a,b,drop=15,palette=None):
 palette=palette or [(255,213,106,180),(255,150,185,150),(137,235,250,155)]
 x0,y0=a;x1,y1=b
 pixel_line(dr,[(x0,y0),(x0+(x1-x0)//2,(y0+y1)//2+drop),(x1,y1)],(106,75,73,116),3)
 for i in range(1,10):
  t=i/10;x=int(x0+t*(x1-x0));y=int((1-t)*y0+t*y1+drop*math.sin(math.pi*t))
  dr.ellipse((x-5,y-4,x+5,y+7),fill=palette[i%len(palette)])
  dr.rectangle((x-3,y-9,x+3,y-4),fill=(102,68,63,155))

def pixel_petal(dr,x,y,col,size=4):
 dr.polygon([(x-size,y),(x,y-size//2),(x+size,y),(x+1,y+size//2)],fill=col)

def water_caustics(dr,w,h,rng,water_zone,mode):
 x0,y0,x1,y1=water_zone
 for _ in range(290 if mode!='pond' else 125):
  x=rng.randrange(x0,x1);y=rng.randrange(y0,y1)
  dx=rng.choice((8,14,22,33));col=(175,228,246,rng.randrange(60,115))
  pixel_line(dr,[(x,y),(x+dx,y)],col,rng.choice([2,3,4]))
  if rng.randrange(9)==0:pixel_line(dr,[(x+4,y-4),(x+dx//2,y-4)],(244,253,233,120),2)

def draw_location(name,w,h,seed):
 rng=random.Random(seed)
 im=Image.new('RGBA',(w,h),(0,0,0,0));dr=ImageDraw.Draw(im,'RGBA');X=lambda p:int(w*p);Y=lambda p:int(h*p)
 gold=(237,197,126,134);warm=(255,232,180,140);dark=(92,71,67,100)
 petals=lambda count,tint: [pixel_petal(dr,rng.randrange(20,w-20),rng.randrange(30,h-30),rng.choice(tint),rng.randrange(3,7)) for _ in range(count)]
 if name=='plaza':
  shrine(dr,X(.5),Y(.59),min(w,h)//4,((146,94,72,130),(255,223,162,145),(178,123,93,100)))
  for i in range(24):
   a=i*math.tau/24;x=X(.5)+int(290*math.cos(a));y=Y(.59)+int(160*math.sin(a))
   dr.ellipse((x-8,y-5,x+8,y+6),fill=(238,193,130,128))
  for cx in [X(.18),X(.82)]:shrine(dr,cx,Y(.55),72,((167,111,89,96),(236,214,149,160),(122,91,66,95)))
  string_lights(dr,(X(.15),Y(.29)),(X(.85),Y(.29)),25)
  petals(380,[(248,179,188,95),(248,221,159,90)])
 elif name=='taman_kota':
  # pond occupies middle left: soften shoreline with reed fans, lilies, and water highlights
  water_caustics(dr,w,h,rng,(X(.23),Y(.40),X(.59),Y(.69)),'pond')
  for i in range(42):
   a=i*math.tau/42;cx=X(.38)+int(w*.18*math.cos(a));cy=Y(.57)+int(h*.15*math.sin(a));
   for j in range(3):
    xx=cx+j*4;pixel_line(dr,[(xx,cy),(xx+2,cy-rng.randrange(9,22))],(90,156,100,180),2)
  for i in range(36):
   x=rng.randrange(X(.25),X(.55));y=rng.randrange(Y(.42),Y(.65))
   dr.ellipse((x-9,y-4,x+9,y+5),fill=(119,162,95,135),outline=(68,116,76,160),width=2)
   if i%5==0:dr.ellipse((x-2,y-4,x+4,y+2),fill=(255,215,234,200))
  petals(500,[(252,163,191,130),(255,232,177,115)])
 elif name in ('riverside','dermaga'):
  water_caustics(dr,w,h,rng,(X(.02),Y(.73),X(.98),Y(.99)),'shore')
  for i in range(55):
   xx=int(w*i/55);yy=int(h*(.72+.015*math.sin(i/4.2)))
   dr.arc((xx-50,yy-7,xx+50,yy+19),190,340,fill=(246,236,196,98),width=2)
  string_lights(dr,(X(.16),Y(.68)),(X(.84),Y(.68)),30)
  if name=='dermaga':
   # dock board joints follow current wood walkway (texture only)
   for y in range(Y(.48),Y(.98),22):
    for x in range(X(.42),X(.58),90):
     pixel_line(dr,[(x,y),(x+61,y)],(90,56,48,77),2)
   for i in range(12):
    xx=X(.46)+i*10;yy=Y(.58)+i*2
    dr.ellipse((xx-3,yy-3,xx+3,yy+3),fill=(219,169,102,128))
  else:petals(245,[(255,177,200,95),(238,216,154,80)])
 elif name=='cafe':
  # wall paneling, wood inlays and warm cone cast onto floor
  for xx in range(50,w-20,120):
   dr.rounded_rectangle((xx,30,xx+82,182),radius=8,outline=(125,73,51,130),width=5)
   pixel_line(dr,[(xx+41,37),(xx+41,173)],(255,217,147,75),3)
  for yy in range(210,h-10,46):
   for xx in range(22+(yy//46%2)*35,w-20,76):
    dr.line((xx,yy,xx+54,yy),fill=(252,211,156,90),width=2)
  shrine(dr,X(.48),Y(.70),min(w,h)//5,((180,116,79,99),(252,220,168,138),(122,76,60,96)))
  for i in range(5):
   x=X(.12+.18*i)
   dr.polygon([(x,173),(x+26,173),(x+145,h-28),(x-10,h-28)],fill=(255,223,160,26))
 elif name=='memory_garden':
  shrine(dr,X(.5),Y(.52),250,((224,178,248,135),(248,219,255,150),(137,126,200,92)))
  for r in (300,336):ring(dr,(X(.5)-r,Y(.52)-r*.56,X(.5)+r,Y(.52)+r*.56),(245,195,241,103),None,5)
  petals(750,[(255,195,246,115),(239,225,255,114),(188,241,253,105)])
 elif name=='eternal_garden':
  shrine(dr,X(.5),Y(.39),185,((217,149,188,128),(250,224,167,160),(160,134,111,90)))
  for i in range(17):
   y=Y(.3)+i*38
   dr.arc((X(.44),y,X(.56),y+56),0,180,fill=(250,216,191,96),width=4)
  petals(620,[(253,188,217,125),(255,235,160,88)])
 elif name=='lantern_field':
  shrine(dr,X(.5),Y(.53),180,((226,173,135,130),(255,232,165,155),(159,99,111,108)))
  for yy in (Y(.2),Y(.78)):
   string_lights(dr,(X(.1),yy),(X(.9),yy),40)
  petals(560,[(255,179,173,122),(255,220,156,126)])
 elif name=='star_path':
  for i in range(1,15):
   x=X(i/15);y=int(h*(.5+.095*math.sin(i*.91)))
   ring(dr,(x-12,y-12,x+12,y+12),(255,233,164,185),None,3)
   if i<14:pixel_line(dr,[(x,y-20),(x+60,y-30)],(185,217,247,72),3)
  for _ in range(75):
   x=rng.randrange(w);y=rng.randrange(h)
   dr.line((x-9,y,x+9,y),fill=(248,229,168,136),width=3)
   dr.line((x,y-9,x,y+9),fill=(248,229,168,136),width=3)
 elif name=='starfall_village':
  shrine(dr,X(.50),Y(.55),190,((185,139,190,125),(244,209,171,140),(133,107,175,95)))
  for cx in (.19,.5,.81):
   dr.arc((X(cx)-80,Y(.24)-25,X(cx)+80,Y(.24)+28),0,180,fill=(253,217,159,143),width=5)
  petals(240,[(228,198,248,125),(248,223,185,105)])
 elif name=='bukit_bintang':
  shrine(dr,X(.78),Y(.53),205,((174,151,177,125),(249,218,160,138),(117,112,155,98)))
  for i in range(22):
   a=i*math.tau/22;x=X(.78)+int(240*math.cos(a));y=Y(.53)+int(140*math.sin(a))
   dr.ellipse((x-5,y-3,x+5,y+4),fill=(252,234,168,170))
  petals(180,[(220,191,229,100),(251,229,182,130)])
 elif name=='hutan_bisik':
  # forest floor roots and firefly trails; river occupies the vertical eastern corridor
  water_caustics(dr,w,h,rng,(X(.68),Y(.03),X(.79),Y(.95)),'shore')
  for i in range(120):
   x=rng.randrange(80,w-80);y=rng.randrange(90,h-100)
   dr.arc((x-28,y-15,x+28,y+11),200,345,fill=(75,119,79,98),width=4)
   if i%4==0:
    dr.ellipse((x-4,y-5,x+4,y+3),fill=(230,248,171,130))
  petals(550,[(170,224,151,90),(212,231,153,80)])
 elif name=='gua_kristal':
  # cave fissures and magical mineral glyphs on the floor, no new collision
  shrine(dr,X(.52),Y(.43),153,((107,197,236,118),(209,171,255,143),(125,102,174,112)))
  for cx,cy in ((.21,.27),(.72,.29),(.35,.71),(.80,.67)):
   x,y=X(cx),Y(cy)
   for i in range(8):
    theta=i*math.tau/8;xx=x+int(math.cos(theta)*55);yy=y+int(math.sin(theta)*34)
    dr.polygon(((xx,yy-12),(xx+8,yy),(xx,yy+15),(xx-8,yy)),fill=(125,224,252,112) if i%2 else (230,167,254,100))
  for i in range(100):
   x=rng.randrange(w);y=rng.randrange(h)
   dr.line((x,y+10,x+7,y-10),fill=(139,237,251,88),width=3)
 return im

def compose(name,base,w,h):
 style,atmos=THEMES[name][1:];seed=int(hashlib.sha256(name.encode('utf-8')).hexdigest()[:8],16)
 paint=pixel_material(w,h,seed,style)
 # Separate raster layers are editable, generated at original dimensions.
 loc=draw_location(name,w,h,seed+751)
 light=glow_gradient(w,h,{'sunny':(255,228,157),'pond':(255,235,183),'shore':(235,215,169),
  'dock':(235,212,159),'warm':(255,184,106),'stars':(187,194,255),'arch':(217,176,255),
  'memories':(254,201,222),'lantern':(255,187,120),'village':(248,200,140),
  'forest':(154,209,171),'cavern':(137,168,250)}[atmos],0.23)
 return [paint,loc,light]

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def atomic_png(im,path):
 path.parent.mkdir(parents=True,exist_ok=True)
 temp=path.with_suffix(path.suffix+'.tmp')
 im.save(temp,format='PNG',compress_level=4)
 os.replace(temp,path)

def run(args):
 M=json.loads((D/'maps.json').read_text())['areas'];assert (set(THEMES)|NINE).issubset(set(M)), 'All 22 baseline areas must remain after story expansions'
 for d in [BASE,LAY,DOCS]:d.mkdir(parents=True,exist_ok=True)
 summary={};hashes={}
 for name in THEMES:
  m=M[name];p=ASSETS/m['image'];basefile=BASE/f'{name}.png'
  if args.verify_only:
   assert p.is_file() and basefile.is_file()
   assert p.stat().st_size>10000
   with Image.open(p) as x:assert x.size==(m['w'],m['h']) and x.verify() is None
   print('verify',name,sha(p)[:12]);continue
  if args.restore:
   if basefile.exists():shutil.copy2(basefile,p)
   continue
  if not basefile.is_file():shutil.copy2(p,basefile)
  with Image.open(basefile) as b:base=b.convert('RGBA')
  assert base.size==(m['w'],m['h'])
  overlays=compose(name,base,m['w'],m['h'])
  final=base
  for key,layer in zip(('material','scenery','illumination'),overlays):
   atomic_png(layer,LAY/f'{name}_{key}.png')
   final=Image.alpha_composite(final,layer)
  atomic_png(final,p)
  summary[name]={'nativeResolution':[m['w'],m['h']],'visualStyle':THEMES[name][0],
   'collisionSpawnPortalsUnchanged':True,'runtimeImage':m['image'],
   'layers':[str((LAY/f'{name}_{k}.png').relative_to(ROOT)) for k in ('material','scenery','illumination')]}
  hashes[name]=sha(p)
  print('art',name,final.size, p.stat().st_size)
 if not (args.verify_only or args.restore):
  (DOCS/'V42_WORLD_MANIFEST.json').write_text(json.dumps({'version':'4.2.0','areas':summary,'sha256':hashes},ensure_ascii=False,indent=2)+'\n')
  print('DONE',len(summary),'area renders; 39 editable layers')

if __name__=='__main__':
 par=argparse.ArgumentParser();par.add_argument('--verify-only',action='store_true');par.add_argument('--restore',action='store_true')
 run(par.parse_args())
