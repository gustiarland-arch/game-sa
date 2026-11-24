#!/usr/bin/env python3
"""V4.8.0 original pixel-art environmental detail pass for all 7 story-exclusive worlds.

Deterministic, source-editable RGBA layers. We draw fine decorations over archived
v4.7.4 backgrounds. Collision, warp coordinates and map metadata do not change.
Run from any cwd: python3 tools/remaster_story_world_v480.py
"""
from PIL import Image, ImageDraw
from pathlib import Path
import json, math, random, hashlib

ROOT=Path(__file__).resolve().parents[1]
MAPS=ROOT/'android/assets/maps'
SRC=ROOT/'art_source/story_v480'
BASE=SRC/'base_maps'; LAYERS=SRC/'editable_layers'
BASE.mkdir(parents=True,exist_ok=True);LAYERS.mkdir(parents=True,exist_ok=True)
NAMES=['galeri_komunitas','rain_garden','clockwork_station','memory_bridge','moonlight_lake','hall_of_tomorrow','ruang_dua_surat']


def box(d,x,y,w,h,color): d.rectangle((int(x),int(y),int(x+w),int(y+h)),fill=color)
def ring(d,cx,cy,r,col,w=1): d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=col,width=w)
def sparkle(d,x,y,col,sz=4):
 d.line((x-sz,y,x+sz,y),fill=col,width=1); d.line((x,y-sz,x,y+sz),fill=col,width=1)
 box(d,x,y,1,1,(255,245,211,240))
def halo(d,x,y,r,color):
 for rr,al in [(r,8),(int(r*.70),14),(int(r*.44),27),(int(r*.2),38)]:
  d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=tuple(color)+(al,))
def leaf(d,x,y,col):
 d.polygon([(x,y-3),(x+3,y-1),(x+2,y+2),(x-2,y+3),(x-3,y+1)], fill=col)
 d.line((x-2,y+2,x+2,y-2),fill=(217,239,213,125),width=1)
def flower(d,x,y,col):
 for dx,dy in [(0,-3),(-3,0),(3,0),(0,3)]:box(d,x+dx-1,y+dy-1,2,2,col)
 box(d,x-1,y-1,2,2,(253,216,161,250))
def rail(d,points,col):d.line(points,fill=col,width=2,joint='curve')
def gear(d,x,y,r,palette,teeth=12):
 dark,light=palette
 ring(d,x,y,r,dark,3);ring(d,x,y,max(1,r-4),light,1)
 ring(d,x,y,max(2,r//3),light,2)
 for k in range(teeth):
  a=k*2*math.pi/teeth
  x1=x+int((r-1)*math.cos(a));y1=y+int((r-1)*math.sin(a))
  x2=x+int((r+4)*math.cos(a));y2=y+int((r+4)*math.sin(a))
  d.line((x1,y1,x2,y2),fill=light,width=3)
 box(d,x-1,y-1,2,2,(247,238,207,240))

def render(name,d,rng):
 if name=='galeri_komunitas':
  # Glass reflections, fine painterly frames, old wooden floor, floral garlands.
  for cy in range(65,304,11):
   for cx in range(39+(cy%19),440,24):
    box(d,cx,cy,8,1,(251,218,177,19));box(d,cx+13,cy+6,3,1,(30,26,55,55))
  for x0,y0,w0,h0 in [(60,48,95,80),(194,48,89,80),(324,48,97,80)]:
   d.rectangle((x0+2,y0+2,x0+w0-2,y0+h0-3),outline=(242,201,133,185),width=2)
   for yy in (y0+5,y0+h0-8):
    for xx in (x0+5,x0+w0-8):
     box(d,xx-1,yy-1,3,3,(255,235,173,220));box(d,xx,yy,1,1,(126,92,97,230))
   d.line((x0+9,y0+9,x0+28,y0+9),fill=(255,244,212,120),width=1)
  # Velvet carpet embroidered with subtle double borders, away from walk hit-boxes.
  for x0,y0,x1,y1 in [(91,186,217,251),(261,185,381,250)]:
   d.rectangle((x0,y0,x1,y1),outline=(246,218,166,115),width=1)
   for xx in range(x0+11,x1-3,12):
    for yy in (y0+3,y1-4):
     box(d,xx,yy,2,1,(245,206,153,120))
  for k in range(16):
   x=46+k*24
   leaf(d,x,144+(k%3), (107,174,141,185));flower(d,x+5,146,(235,156,173,195))
  # The symbolic chair has a solitary pool of light and a small folded program.
  halo(d,147,213,29,(255,216,167));box(d,143,177,11,2,(255,235,201,180))
  box(d,139,174,15,2,(237,215,175,240));d.line((143,176,149,176),fill=(98,67,93,230))
  for x,y in [(258,164),(358,155),(118,164),(200,153),(418,199)]:sparkle(d,x,y,(255,227,179,155),2)
  for x in (74,384):
   d.line((x,134,x,156),fill=(115,68,88,180),width=2)
   flower(d,x,140,(249,203,158,220))
 elif name=='rain_garden':
  # Petal-strewn wet paths and individual raindrop rings around the five lanterns.
  for k in range(175):
   x=rng.randrange(35,450); y=rng.randrange(24,297)
   c=(139,202,190,130) if k%3==0 else (112,155,180,96)
   if (x<220 and y<115) or (x>275 and y>200):
    leaf(d,x,y,c)
   elif k%4==0: box(d,x,y,1,2,(240,210,213,145))
  for cx,cy in [(65,268),(93,230),(125,196),(192,143),(260,111)]:
   halo(d,cx,cy,18,(224,193,159))
   ring(d,cx,cy+5,8,(161,215,218,144));ring(d,cx,cy+5,13,(117,180,194,93))
   for p in range(5):sparkle(d,cx-10+p*5,cy-14+(p%2)*4,(248,224,186,165),1)
  # Rain lines, thinner near the traversable path to keep targets legible.
  for k in range(65):
   x=rng.randint(30,455);y=rng.randint(14,310)
   d.line((x,y,x-2,y+6),fill=(172,211,230,65),width=1)
  for cx,cy in [(75,120),(119,177),(357,235),(413,90),(390,176)]:
   for rr in (5,10,15):d.arc((cx-rr,cy-rr//2,cx+rr,cy+rr//2),30,150,fill=(142,202,212,125),width=1)
  for p in range(18):
   x=34+p*24;y=300+(p%2)*3;leaf(d,x,y,(106,143,129,152))
 elif name=='clockwork_station':
  # Clock hall industrial filigree, rivets, radial mechanics and aged rail strips.
  for x in range(20,465,24):
   for y in range(35,285,24):
    box(d,x,y,2,2,(220,188,134,95));box(d,x+2,y+1,1,1,(47,63,87,220))
  for gx,gy,r in [(85,85,21),(406,86,25),(116,246,16),(373,250,18),(247,271,23)]:
   gear(d,gx,gy,r,((65,82,117,215),(208,172,133,193)),12)
  for x in range(65,441,18):
   box(d,x,31,5,2,(247,206,154,150));box(d,x+2,287,4,2,(217,178,132,180))
  for cx,cy in [(230,70),(149,184),(323,180)]:
   halo(d,cx,cy,20,(241,184,117));sparkle(d,cx,cy,(255,226,184,200),3)
  # Rail gauge not crossing gameplay geometry.
  for y in (295,300,305):d.line((68,y,412,y),fill=(213,175,135,115),width=1)
  for x in range(83,408,17):box(d,x,295,3,11,(102,123,149,150))
  for ang in range(0,360,30):
   a=ang*math.pi/180;x=244+int(27*math.cos(a));y=70+int(27*math.sin(a))
   box(d,x,y,2,3,(255,223,171,165))
 elif name=='memory_bridge':
  # Vast starfield and connected constellation lines; walkway motifs remain decorative.
  stars=[]
  for _ in range(180):
   x=rng.randint(18,465);y=rng.randint(12,290)
   if 282<x<393 and y>50:continue
   stars.append((x,y));box(d,x,y,rng.choice((1,1,2)),1,rng.choice(((191,206,244,160),(255,226,175,235),(177,201,255,115))))
  for k in range(0,len(stars)-1,4):
   a=stars[k];b=stars[k+1]
   if abs(a[0]-b[0])<105 and abs(a[1]-b[1])<60:d.line((*a,*b),fill=(139,173,242,57),width=1)
  for cx,cy in [(333,71),(295,116),(375,143),(270,180),(407,191)]:
   halo(d,cx,cy,20,(241,194,150));sparkle(d,cx,cy,(253,239,209,213),4)
  # The bridge itself carries five memory tessellations.
  for j in range(5):
   y=73+j*41;x=337
   for dx in range(-j-1,j+2):
    box(d,x+dx*13-4,y,8,2,(255,233,187,88))
   for off in (-25,25):
    d.polygon([(x+off,y-6),(x+off+5,y),(x+off,y+6),(x+off-5,y)],outline=(253,226,165,157))
  for j in range(16):
   x=303+(j%4)*21;y=201+(j//4)*18
   box(d,x,y,3,2,(214,219,247,75))
 elif name=='moonlight_lake':
  # A ring of quiet water, lily leaves, reflected constellations and reed silhouettes.
  for k in range(290):
   x=rng.randrange(49,431);y=rng.randrange(31,297)
   if ((x-239)/211)**2+((y-168)/151)**2<0.98:
    col=(170,229,221,95) if k%3==0 else (194,219,239,65)
    d.line((x,y,x+rng.randint(1,6),y),fill=col,width=1)
  for cx,cy,r in [(132,212,12),(377,211,10),(218,250,11),(310,90,10),(94,154,8)]:
   d.ellipse((cx-r,cy-r//2,cx+r,cy+r//2),fill=(101,172,157,180),outline=(203,224,188,125))
   d.polygon([(cx,cy),(cx+r+3,cy-2),(cx+r+1,cy+2)],fill=(60,114,122,200))
   flower(d,cx-2,cy-1,(243,194,204,211))
  for cx,cy in [(191,138),(264,148),(325,166),(256,112)]:
   halo(d,cx,cy,11,(204,222,233));ring(d,cx,cy,17,(172,212,218,100))
   d.line((cx-13,cy+11,cx+10,cy+11),fill=(216,239,230,130))
  for a in range(0,360,30):
   x=241+int(60*math.cos(math.radians(a)));y=125+int(31*math.sin(math.radians(a)))
   box(d,x,y,2,2,(255,233,187,185))
  for i in range(20):
   x=32+i*23;y=287+(i%3)*4
   d.line((x,y,x-3,y-rng.randint(8,18)),fill=(111,172,151,142),width=2)
 elif name=='hall_of_tomorrow':
  # Three futures with individual mosaic auras (success / comfort / certainty).
  for cx,color in [(113,(255,199,164)),(241,(191,222,249)),(368,(230,196,242))]:
   halo(d,cx,86,51,color)
   for j in range(26):
    a=j*math.pi/13;r=41+(j%4)
    xx=cx+int(math.cos(a)*r); yy=80+int(math.sin(a)*24)
    box(d,xx,yy,2,3,tuple(color)+(140,))
   for ang in range(0,360,45):
    a=math.radians(ang);xx=cx+int(25*math.cos(a));yy=81+int(24*math.sin(a))
    sparkle(d,xx,yy,tuple(color)+(162,),2)
  # Cracks in the predicted futures: the perfection is too symmetrical.
  for cx in (113,241,368):
   d.line((cx-7,100,cx-2,106,cx-4,115,cx+2,119,cx-1,128),fill=(205,224,240,125),width=1)
  for y in range(211,319,16):
   for x in range(23+(y%21),475,26):
    box(d,x,y,1,4,(243,220,188,77));box(d,x+6,y+5,5,1,(189,201,234,87))
  for x in range(72,429,18):
   d.line((x,295,x+9,304),fill=(186,180,212,85),width=1)
  for x,y in [(89,186),(379,185),(242,173)]:
   sparkle(d,x,y,(255,238,193,220),4)
 elif name=='ruang_dua_surat':
  # An intimate library where Arland/Sofia have separate visual timelines.
  for x in range(60,425,11):
   c=rng.choice(((205,171,157,205),(155,171,206,200),(195,154,188,215),(227,195,158,213)))
   box(d,x,27,5,rng.randint(21,35),c)
   box(d,x+1,32,1,14,(247,226,194,140))
   box(d,x+3,49,2,2,(81,75,104,230))
  d.line((54,67,427,67),fill=(255,222,172,230),width=3)
  for cx in (145,333):
   halo(d,cx,136,40,(245,206,155))
   for j in range(5):
    d.line((cx-29+j*5,116,cx-25+j*5,116),fill=(254,238,208,197),width=1)
   for y in range(164,182,6):
    d.line((cx-20,y,cx+17,y),fill=(91,79,112,170),width=1)
  # Two lines of tiny paper relics and gently lit petals in the archive.
  for x in range(62,430,27):
   for y in (204,238,279):
    box(d,x,y,7,5,(250,219,188,80));box(d,x+3,y+2,2,1,(101,85,101,120))
  for i in range(45):
   x=rng.randint(40,440);y=rng.randint(85,300)
   if 200<x<278 and 275<y:continue
   box(d,x,y,1,2,(250,215,170,rng.randint(55,170)))
  sparkle(d,241,217,(255,232,191,210),3)


def main():
 manifest={'version':'4.8.0','notes':'Only rendered backgrounds changed; metadata/collision/spawn coordinates are not touched.','maps':{}}
 for name in NAMES:
  old=MAPS/(name+'.png');original=BASE/(name+'.png')
  if not original.exists():original.write_bytes(old.read_bytes())
  src=Image.open(original).convert('RGBA');w,h=src.size
  scale=2 if w==960 else 4
  tiny=src.resize((w//scale,h//scale),Image.Resampling.NEAREST)
  over=Image.new('RGBA',tiny.size,(0,0,0,0)); dr=ImageDraw.Draw(over,'RGBA')
  render(name,dr,random.Random('story-world-4.8.0/'+name))
  layer=over.resize((w,h),Image.Resampling.NEAREST)
  layer.save(LAYERS/(name+'_detail.png'),optimize=True)
  out=Image.alpha_composite(src,layer).convert('RGB')
  out.save(old,optimize=True,compress_level=6)
  manifest['maps'][name]={'size':[w,h],'layer':'art_source/story_v480/editable_layers/'+name+'_detail.png','before_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),'after_sha256':hashlib.sha256(old.read_bytes()).hexdigest()}
 (SRC/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('PASS: original v4.8 detail pass installed on 7 distinct map backgrounds')

if __name__=='__main__':main()
