#!/usr/bin/env python3
"""v4.4: four location-specific editable environment passes, original v4.3 map size/collision preserved.

Images and prop definitions are regenerated from frozen v4.3 baselines (never from their own outputs).
Only the four planned backgrounds and selected existing prop types are edited. --metadata-only reconnects
prop references after the canonical content generator, without repainting any pixels.
"""
from __future__ import annotations
import argparse, hashlib, json, math, os, random
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np
ROOT=Path(__file__).resolve().parent.parent
ASSET=ROOT/'android/assets'; DATA=ASSET/'data'
SRC=ROOT/'art_source/world_v44'; BM=SRC/'baseline_maps'; BP=SRC/'baseline_props'; LAY=SRC/'editable_layers'
KEYS=('dermaga','bukit_bintang','memory_garden','eternal_garden')
SELECT={
 'dermaga':('bridge_dpier','bridge_dplat','v41_rowboat_rowboat','v41_rowboat_b_rowboat','pier_post','fishing_hut','lantern_post'),
 'bukit_bintang':('v41_observatory_observatory','v41_telescope_telescope','picnic_blanket','stone_lantern_bb','fence_bb','chest_bb'),
 'memory_garden':('v41_tree_dream_memory_tree','v41_pedestal_book_crystal_shrine','v41_arch_flowers_arch','crystal','tree_dream','tree_lantern'),
 'eternal_garden':('v41_wishing_tree_memory_tree','v41_arch_flowers_e_arch','v41_arch_flowers_e2_arch','v41_gazebo_e_gazebo','stone_bench','flowerbed'),
}
def atomic_png(img,path):
 path.parent.mkdir(parents=True,exist_ok=True)
 tmp=path.with_name(path.name+'.tmp');img.save(tmp,format='PNG',compress_level=6);os.replace(tmp,path)
def flower(draw,x,y,color=(250,183,221,180),radius=3):
 for dx,dy in ((-5,0),(5,0),(0,-5),(0,5)):
  draw.rectangle((x+dx-radius,y+dy-radius,x+dx+radius,y+dy+radius),fill=color)
 draw.rectangle((x-2,y-2,x+2,y+2),fill=(255,238,159,240))
def rune(draw,x,y,r,c):
 draw.ellipse((x-r,y-r*.42,x+r,y+r*.42),outline=c,width=3)
 for k in range(8):
  a=k*math.tau/8
  xx=x+r*math.cos(a);yy=y+r*.42*math.sin(a)
  draw.line((xx,yy,xx+7*math.cos(a),yy+7*math.sin(a)),fill=c,width=3)
def draw_layers(name,w,h):
 rng=random.Random(443219+KEYS.index(name)*1229)
 layers={n:Image.new('RGBA',(w,h)) for n in ('materials','landmarks','details','lighting')}
 mat,lmk,det,lgt=[ImageDraw.Draw(layers[n],'RGBA') for n in layers]
 sx=w/1920; sy=h/1280
 if name=='dermaga':
  # Water is the bottom part of the old map; no added physical dock geometry.
  for i in range(500):
   x=rng.randrange(20,w-80);y=rng.randrange(int(h*.43),h-15)
   length=rng.choice((15,24,37,58)); alpha=rng.randrange(65,150)
   mat.line((x,y,x+length,y),fill=(173,237,245,alpha),width=2)
   if i%6==0:mat.line((x+6,y-5,x+22,y-5),fill=(255,230,166,110),width=2)
  for i in range(80):
   x=rng.randrange(30,w-30);y=int(h*.45+math.sin(x*.017)*16)
   mat.arc((x-36,y-11,x+38,y+24),0,170,fill=(253,237,197,100),width=2)
  for x in range(180,w-180,85):
   y=int(h*.35+12*math.sin(x/180))
   det.ellipse((x-10,y-4,x+12,y+5),fill=(100,171,127,90))
  # Gentle warm haze toward the real river horizon.
  for x,y in ((180,int(h*.40)),(1640,int(h*.40))):
   lgt.ellipse((x-135,y-65,x+135,y+55),fill=(255,231,172,14))
 elif name=='bukit_bintang':
  # Astronomical ground engravings and dusk gold stars; low-alpha to preserve walkability cues.
  for x,y,r in ((int(w*.48),int(h*.48),155),(int(w*.69),int(h*.33),86),(int(w*.31),int(h*.67),103)):
   rune(lmk,x,y,r,(242,208,161,96))
   for i in range(14):
    t=i*math.tau/14
    det.rectangle((x+r*.83*math.cos(t)-3,y+r*.34*math.sin(t)-3,x+r*.83*math.cos(t)+3,y+r*.34*math.sin(t)+3),fill=(255,231,173,132))
  for i in range(160):
   x=rng.randrange(30,w-30);y=rng.randrange(20,h-20)
   if i%3==0:flower(det,x,y,(177,164,248,135),2)
   else:det.rectangle((x,y,x+3,y+3),fill=(241,219,177,90))
  lgt.ellipse((w*.42,h*.22,w*.58,h*.43),fill=(178,148,247,15))
 elif name=='memory_garden':
  # Memory wheel and tiny luminous blossoms; the landmark props remain at their original anchors.
  cx=int(w*.5);cy=int(h*.52)
  for radius in (160,208,257,308):
   lmk.ellipse((cx-radius,cy-radius*.58,cx+radius,cy+radius*.58),outline=(216,195,255,86),width=4)
  for i in range(28):
   a=i*math.tau/28;x=int(cx+291*math.cos(a));y=int(cy+162*math.sin(a))
   lmk.polygon([(x,y-9),(x+8,y),(x,y+9),(x-8,y)],fill=(231,219,251,113))
  for i in range(280):
   x=rng.randrange(30,w-30);y=rng.randrange(30,h-30)
   if rng.random()<.18:flower(det,x,y,(230,160,244,155),2)
   else:det.ellipse((x,y,x+4,y+2),fill=(191,246,246,110))
  lgt.ellipse((cx-330,cy-260,cx+330,cy+260),fill=(209,174,247,22))
 elif name=='eternal_garden':
  # Romantic ring, petal paving and evening lanterns (no obstructing new props).
  cx,cy=int(w*.49),int(h*.55)
  for radius in (175,222,267,326):
   lmk.ellipse((cx-radius,cy-radius*.52,cx+radius,cy+radius*.52),outline=(239,202,162,80),width=4)
  for i in range(550):
   x=rng.randrange(25,w-25);y=rng.randrange(25,h-25)
   c=rng.choice(((255,198,214,140),(247,218,157,110),(228,192,244,120)))
   det.rectangle((x,y,x+7,y+3),fill=c)
   if i%15==0:flower(det,x,y,(250,194,228,150),3)
  for x,y in ((int(w*.16),int(h*.32)),(int(w*.81),int(h*.34)),(int(w*.58),int(h*.75))):
   lgt.ellipse((x-170,y-170,x+170,y+170),fill=(255,226,177,18))
 return layers

def metadata():
 m=json.loads((DATA/'maps.json').read_text(encoding='utf8'))
 defs=json.loads((DATA/'props.json').read_text(encoding='utf8'))
 changed=0; alltypes={}
 for area in KEYS:
  for p in m['areas'][area]['props']:
   current=p['type']
   original=current[4:] if current.startswith('v44_') else current
   target='v44_'+original
   if original not in SELECT[area]: continue
   if original not in alltypes:
    source=defs['props'][original]['image']
    if not (BP/(original+'.png')).exists():raise RuntimeError('Missing frozen v4.3 prop: '+original)
    pic=Image.open(BP/(original+'.png')).convert('RGBA')
    arr=np.array(pic,dtype=np.uint8)
    rgb=arr[:,:,:3].astype(np.int16)
    alpha=arr[:,:,3].copy() # preserve transparent collision/outline exactly
    h,w=alpha.shape
    ys,xs=np.mgrid[0:h,0:w]
    light=np.sin(xs/9+ys/15)*5+np.cos(ys/13)*4
    rgb[:,:,0]=np.clip(rgb[:,:,0]+light+8,0,255)
    rgb[:,:,1]=np.clip(rgb[:,:,1]+light*.5+5,0,255)
    rgb[:,:,2]=np.clip(rgb[:,:,2]+light*.2+5,0,255)
    out=Image.fromarray(np.dstack((rgb.astype('uint8'),alpha)),'RGBA')
    atomic_png(out,ASSET/'props'/f'{target}.png')
    newdef=dict(defs['props'][original]);newdef['image']='props/'+target+'.png'
    defs['props'][target]=newdef
    alltypes[original]=target
   p['type']=target;changed+=1
 m['_maps_v44']={'id':'v4.4.0','areas':list(KEYS),'propTypes':len(alltypes),'placements':changed,'collision':'unchanged'}
 (DATA/'maps.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 (DATA/'props.json').write_text(json.dumps(defs,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 return changed,len(alltypes)

def run(full):
 if full:
  for name in KEYS:
   original=Image.open(BM/(name+'.png')).convert('RGBA')
   layers=draw_layers(name,*original.size)
   result=original.copy()
   for key,layer in layers.items():
    atomic_png(layer,LAY/(name+'_'+key+'.png'))
    result=Image.alpha_composite(result,layer)
   atomic_png(result,ASSET/'maps'/f'{name}.png')
   print('map',name,original.size,hashlib.sha256((ASSET/'maps'/f'{name}.png').read_bytes()).hexdigest()[:12])
 n,k=metadata();print('props: placements',n,'unique types',k)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--metadata-only',action='store_true');args=p.parse_args();run(not args.metadata_only)
