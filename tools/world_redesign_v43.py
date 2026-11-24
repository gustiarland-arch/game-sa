#!/usr/bin/env python3
"""Visual art-pass v4.3 for the FOUR benchmark areas, deterministic and atomically written.

Layers are editable PNGs and imported from frozen v4.2 source backups. Never use
this script to regenerate unrelated maps or remove collision/quest data.
"""
import argparse, hashlib, json, math, os, random, shutil
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT=Path(__file__).resolve().parent.parent
ASSETS=ROOT/'android/assets'; DATA=ASSETS/'data'
SRC=ROOT/'art_source/world_v43'
BASE=SRC/'baseline_maps'; BASP=SRC/'baseline_props'; LAY=SRC/'editable_layers'
KEYS=('plaza','taman_kota','cafe','riverside')
# Existing prop anchors & hitboxes are preserved exactly for safe gameplay migration.
SELECT={
 'plaza':('v41_fountain_fountain','v41_bld_arland_house_house_blue','v41_bld_sofia_house_house_brick','bld_cafe','lamp','bench','v41_flowerbed_flower'),
 'taman_kota':('v41_gazebo_gazebo','bridge_park','v41_tree_cherry_cherry','v41_flowerbed_flower','lamp','bench'),
 'cafe':('v41_counter_cafe_counter','v41_display_case_cafe_display','v41_cafe_table_cafe_table','bookshelf_c','frame_photo','wall_clock'),
 'riverside':('bridge_pier','v41_tree_green_willow','v41_rowboat_rv_rowboat','pier_post','lamp','bench'),
}
PALETTES={
 'plaza':((171,117,71),(254,216,144),(117,92,71)),
 'taman_kota':((86,141,91),(245,207,170),(79,123,111)),
 'cafe':((124,74,56),(241,186,131),(93,57,52)),
 'riverside':((71,138,171),(217,220,179),(61,98,112)),
}

def atomic(im,path):
 path.parent.mkdir(parents=True,exist_ok=True)
 tmp=path.with_name(path.name+'.tmp');im.save(tmp,format='PNG',compress_level=6);os.replace(tmp,path)
def checksum(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def color(alpha):return tuple(alpha)
def pathline(dr,coords,col,width):dr.line(coords,fill=col,width=width,joint='curve')
def flower(dr,x,y,seed,variant=0):
 r=random.Random(seed);c=[(245,174,197,180),(248,220,168,190),(189,178,247,175),(255,239,219,180)][variant%4]
 for dx,dy in ((-6,0),(6,0),(0,-6),(0,6)):
  dr.rectangle((x+dx-4,y+dy-3,x+dx+4,y+dy+3),fill=c)
 dr.rectangle((x-3,y-3,x+3,y+3),fill=(244,211,114,230))
def tile_patch(dr,x,y,stone,glint):
 dr.polygon([(x+3,y+4),(x+36,y+4),(x+43,y+17),(x+39,y+29),(x+5,y+29),(x,y+15)],outline=stone)
 dr.line((x+5,y+6,x+28,y+6),fill=glint,width=2)
def create(name,w,h):
 rng=random.Random(43017+KEYS.index(name)*917)
 pal,highlight,shade=PALETTES[name]
 terrain=Image.new('RGBA',(w,h)); td=ImageDraw.Draw(terrain,'RGBA')
 details=Image.new('RGBA',(w,h)); dd=ImageDraw.Draw(details,'RGBA')
 decor=Image.new('RGBA',(w,h)); od=ImageDraw.Draw(decor,'RGBA')
 light=Image.new('RGBA',(w,h));ld=ImageDraw.Draw(light,'RGBA')
 # 16-bit tiles drawn into matching pathways/terrain; ornamental markings do not block feet.
 if name=='plaza':
  # Prominent central plaza (fountain prop stays anchored in the middle).
  for y in range(500,1050,46):
   for x in range(290+(y//46%2)*30,1640,70):
    if 410<y<1065: tile_patch(td,x,y,(132,91,68,36),(255,222,162,55))
  cx,cy=960,790
  for radius in (220,258,294,333):
   dd.ellipse((cx-radius,cy-int(radius*.49),cx+radius,cy+int(radius*.49)),outline=(118,79,60,100),width=4)
   dd.ellipse((cx-radius+8,cy-int(radius*.49)+8,cx+radius-8,cy+int(radius*.49)-8),outline=(249,214,153,115),width=3)
  for i in range(24):
   th=i*math.tau/24; x=cx+int(math.cos(th)*300);y=cy+int(math.sin(th)*152)
   od.polygon([(x,y-11),(x+10,y),(x,y+11),(x-10,y)],fill=(245,209,155,140))
  for i in range(230):
   x=rng.randrange(60,w-60);y=rng.randrange(115,h-80)
   if abs(x-960)>440 or y<460:flower(od,x,y,i,variant=i%4)
  for ax,ay in ((260,555),(1640,555),(260,1100),(1630,1100)):
   for yy in range(3):
    for xx in range(4):
     x=ax+xx*23;y=ay+yy*24
     flower(od,x,y,xx+yy*6,yy%3)
  for cx,cy in ((230,290),(1690,290)):
   ld.ellipse((cx-180,cy-100,cx+180,cy+240),fill=(255,210,130,17))
 elif name=='taman_kota':
  # Lily leaves & pond shoreline; no new physical obstruction or relocated bridges.
  px,py=770,830
  for i in range(115):
   a=rng.random()*math.tau;r=(rng.random()**0.5)*260
   x=int(px+math.cos(a)*r*1.2);y=int(py+math.sin(a)*r*.65)
   if x<375 or y<585 or x>1190 or y>1050:continue
   od.ellipse((x-10,y-5,x+11,y+5),fill=(91,144,109,145),outline=(200,237,184,70),width=2)
   if i%7==0: flower(od,x,y,i,variant=0)
  for i in range(190):
   x=rng.randrange(110,w-110);y=rng.randrange(160,h-110)
   if 360<x<1130 and 560<y<1090:continue
   flower(od,x,y,i,variant=i%4)
  for i in range(0,31):
   th=i*math.tau/30
   x=px+int(480*math.cos(th));y=py+int(255*math.sin(th))
   pathline(dd,[(x,y),(x+4,y-14)],(90,133,79,110),2)
  for x in range(100,1850,82):
   y=int(370+42*math.sin(x/215.0))
   if x<1100 or x>1800:
    td.ellipse((x-8,y-4,x+8,y+4),fill=(242,214,162,75))
  for cx,cy in ((330,280),(1620,1000)):
   ld.ellipse((cx-220,cy-160,cx+220,cy+160),fill=(251,228,165,18))
 elif name=='cafe':
  # Hand-authored interior material: wood plank and checkerboard insets.
  for y in range(232,h,38):
   for x in range(12+(y//38%2)*32,w,72):
    td.line((x,y,x+61,y),fill=(97,60,46,92),width=3)
    td.line((x,y+3,x+56,y+3),fill=(243,186,135,60),width=2)
    td.line((x+12,y,x+12,y+37),fill=(90,58,45,42),width=2)
  for y in (246,320,410,514):
   dd.line((42,y,w-44,y),fill=(255,215,151,40),width=2)
  # ornate central inlay rug, drawing only into floor below preexisting table sprites
  for r in (120,151,167):
   dd.ellipse((480-r,int(461-r*.60),480+r,int(461+r*.60)),outline=(228,181,122,135),width=4)
  for i in range(16):
   a=math.tau*i/16;x=480+int(147*math.cos(a));y=461+int(85*math.sin(a))
   od.polygon([(x,y-8),(x+8,y),(x,y+8),(x-8,y)],fill=(240,206,165,170))
  for x in (76,222,368,514,660,806):
   od.rectangle((x,130,x+54,150),fill=(126,77,57,140))
   od.rectangle((x+10,137,x+43,143),fill=(243,191,125,90))
  for x in (128,448,820):
   ld.polygon([(x,180),(x+28,180),(x+235,620),(x-110,620)],fill=(255,204,131,15))
 elif name=='riverside':
  # Water covers bottom portion; bright river ripples and bank vegetation.
  for i in range(650):
   x=rng.randrange(16,w-26);y=rng.randrange(734,h-14)
   width=rng.choice((16,22,30,45))
   dd.line((x,y,x+width,y),fill=(171,229,245,rng.randrange(85,145)),width=rng.choice((2,3)))
   if i%7==0:dd.line((x+8,y-4,x+16,y-4),fill=(232,247,211,175),width=2)
  for i in range(0,37):
   xx=i*54;yy=int(730+14*math.sin(i*.5))
   td.arc((xx-45,yy-11,xx+50,yy+22),0,175,fill=(232,224,188,150),width=4)
  for i in range(180):
   x=rng.randrange(80,w-80);y=rng.randrange(90,697)
   if i%2:
    od.line((x,y,x-4,y-13),fill=(79,124,74,137),width=3)
    od.line((x,y,x+4,y-9),fill=(117,154,91,145),width=2)
   else:flower(od,x,y,i,variant=i%4)
  for cx,cy in ((260,200),(1650,240)):
   ld.ellipse((cx-230,cy-100,cx+230,cy+320),fill=(252,225,167,16))
 return {'terrain':terrain,'detail':details,'decor':decor,'lighting':light}

def import_props():
 m=json.loads((DATA/'maps.json').read_text(encoding='utf8'))
 defs=json.loads((DATA/'props.json').read_text(encoding='utf8'))
 updated=0; types=set(); active=[]
 for area in KEYS:
  for ob in m['areas'][area]['props']:
   original=ob['type']
   if original not in SELECT[area]:continue
   target='v43_'+original
   if original not in types:
    src=ASSETS/defs['props'][original]['image']
    dst=ASSETS/'props'/ (target+'.png')
    if not src.exists():raise RuntimeError(f'prop missing: {src}')
    image=Image.open(BASP/(original+'.png')).convert('RGBA')
    arr=np.array(image,dtype=np.uint8)
    a=arr[:,:,3].astype(np.float32)/255
    rgb=arr[:,:,:3].astype(np.float32)
    h,w=arr.shape[:2]
    # Fidelity-first pixel art polish: retain EXACT alpha mask & hitbox.
    ys,xs=np.mgrid[0:h,0:w];wave=np.sin((xs+ys*.6)/11.0)*7+np.cos(ys/7.0)*4
    rgb[:,:,0]=np.clip(rgb[:,:,0]*1.055+wave+5,0,255)
    rgb[:,:,1]=np.clip(rgb[:,:,1]*1.018+wave*.4+3,0,255)
    rgb[:,:,2]=np.clip(rgb[:,:,2]*.985-wave*.2+1,0,255)
    out=np.dstack((rgb.astype(np.uint8),arr[:,:,3]))
    atomic(Image.fromarray(out,'RGBA'),dst)
    defs['props'][target]=dict(defs['props'][original]);defs['props'][target]['image']='props/'+target+'.png'
    types.add(original)
   ob['type']=target;updated+=1
  active.append(area)
 m['_maps_v43']={'id':'v4.3.0','areas':list(KEYS),'propTypeCount':20,'notes':'layout/collision/spawn/door data unchanged from v4.2'}
 (DATA/'maps.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 (DATA/'props.json').write_text(json.dumps(defs,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 return updated,len(types)

def run():
 SRC.mkdir(parents=True,exist_ok=True);LAY.mkdir(exist_ok=True)
 for name in KEYS:
  base=Image.open(BASE/(name+'.png')).convert('RGBA');w,h=base.size
  layers=create(name,w,h)
  result=base.copy()
  for key,layer in layers.items():
   atomic(layer,LAY/(name+'_'+key+'.png'))
   result=Image.alpha_composite(result,layer)
  atomic(result,ASSETS/'maps'/(name+'.png'))
  print('rendered',name,(w,h),checksum(ASSETS/'maps'/(name+'.png'))[:12])
 count,types=import_props()
 print('updated placements',count,'unique new prop types',types)

if __name__=='__main__':
 parser=argparse.ArgumentParser(description='v4.3 map/prop visual art pass')
 parser.add_argument('--metadata-only',action='store_true',help='Restore prop definitions after content regeneration without touching images')
 args=parser.parse_args()
 if args.metadata_only:
  count,types=import_props()
  print('v4.3 metadata reconnected:',count,'placements,',types,'prop types')
 else:run()
