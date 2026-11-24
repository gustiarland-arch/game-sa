#!/usr/bin/env python3
"""Arland & Sofia v5.1 — handmade-layout, regenerable procedural pixel art environment.

Coordinates and semantic anchor notes are in tools/v51_environment_sites.json.
Keeps old base map textures, assets, scene IDs, save-schema, and route data.
Requires Pillow only during content authoring; Android runtime stays offline/native.
"""
from __future__ import annotations
from pathlib import Path
import json, math, hashlib, random, colorsys
from PIL import Image, ImageDraw, ImageFilter
R=Path(__file__).resolve().parents[1]
A=R/'android/assets'; DATA=A/'data'; EN=A/'maps/environment_v51'; PDIR=A/'props/environment_v51'; EN.mkdir(parents=True,exist_ok=True);PDIR.mkdir(parents=True,exist_ok=True)
SPECS=json.loads((R/'tools/v51_environment_sites.json').read_text(encoding='utf-8'))
THEMES={
 'city':('b8a98d','e0d0ad','988675','504e56','f3e4bb','638978'),
 'garden':('aaa68b','dbcfaa','777e6d','494f58','f3db9f','789a76'),
 'wood':('a17757','d2a177','735243','473c44','e8be83','7a9d86'),
 'cafe':('93665e','ddbd9a','674647','4f393e','efd2ac','9c7973'),
 'night':('6c6686','b1a8c9','4b476b','34354b','f4d2ab','7b7b99'),
 'memory':('9d8abd','ddc4e4','71618f','514c74','f5e8be','8a8fc0'),
 'star':('7574ac','b7b4d8','545488','353d64','f6dfc2','8992c4'),
 'forest':('799173','adb38a','506b55','374f44','d9c89c','779e7c'),
 'crystal':('6989a6','b4d4e0','4d6694','334361','dcf2f6','8fb5c7'),
 'future':('777b9b','c5bcd4','5d6285','343953','fae9d9','989bb6')
}
def rgba(hexstr,a=255):return (*bytes.fromhex(hexstr),a)
def interp(a,b,t):return tuple(int(a[i]*(1-t)+b[i]*t) for i in range(3))+(255,)
def rounded(draw, xy, fill, outline=None, radius=4, width=2):draw.rounded_rectangle(tuple(map(int,xy)),radius=radius,fill=fill,outline=outline,width=width)
def seed_for(s):return int.from_bytes(hashlib.sha256(s.encode('utf-8')).digest()[:8],'big')

def build_terrace(name,s):
 w,h,st,rise=[int(s[k]) for k in ('w','h','stair','rise')]; W,H=w+40,h+st+64
 theme=s['style']; f,c,side,dark,accent,green=[rgba(x) for x in THEMES[theme]]
 rng=random.Random(seed_for('v51/'+name)); im=Image.new('RGBA',(W,H));d=ImageDraw.Draw(im)
 # Surface starts at y=40-rise: elevation has real sidewall thickness and visible shadow.
 L,R=20,20+w;T=40-rise;B=T+h;foot=40+h+st;cx=(L+R)//2;sw=int(s['stairWidth']);sx=cx-sw//2
 shadow=(int(L-8),int(T+h+rise-3),int(R+10),int(T+h+rise+14))
 rounded(d,shadow,(24,30,36,72),radius=12)
 # Natural support: retaining wall, angled face and protruding stone/wood border
 d.polygon([(L-4,T+9),(R+4,T+9),(R+7,40+h+1),(L-6,40+h+1)], fill=dark)
 d.polygon([(L,T+h-2),(R,T+h-2),(R,40+h),(L,40+h)],fill=side)
 d.polygon([(L,T+9),(L+6,T),(R-6,T),(R,T+9),(R,T+h-9),(R-6,T+h),(L+6,T+h),(L,T+h-9)],fill=f)
 rounded(d,(L+5,T+5,R-5,B-6),c,side,6,2)
 # Texture doesn't float: human-scale pavers, timber planks, grass patches & stone chipping
 if theme in ('wood','cafe'):
  for yy in range(T+12,B-8,13):
   d.line((L+10,yy,R-10,yy),fill=side,width=2)
   for xx in range(L+14+(7*(yy%3)),R-12,41):d.line((xx,yy-11,xx,yy-1),fill=f,width=2)
 elif theme in ('city','future','night','star','memory','crystal'):
  for yy in range(T+13,B-8,19):
   d.line((L+9,yy,R-9,yy),fill=side,width=1)
   for xx in range(L+9+(yy%2)*22,R-10,44):d.line((xx,yy,xx,yy+16),fill=f,width=1)
 else:
  for i in range(56):
   px=rng.randrange(L+10,R-9);py=rng.randrange(T+9,B-9)
   d.ellipse((px,py,px+2,py+3),fill=green if i%3 else accent)
 # Hue-coherent pixel grain, enough detail without replacing existing source texture.
 for i in range(70):
  xx=rng.randrange(L+11,R-10);yy=rng.randrange(T+10,B-10)
  col=accent if i%7==0 else f
  d.rectangle((xx,yy,xx+(i%3),yy+1),fill=col)
 # Low masonry/wood terrace support, with real stair slot in front elevation
 for y in range(B,40+h,5):
  d.line((L,y,sx-5,y),fill=f if y%2 else dark,width=1)
  d.line((sx+sw+5,y,R,y),fill=f if y%2 else dark,width=1)
 d.line((L+2,B,R-2,B),fill=accent,width=3)
 # Walkable symmetrical tread from upper deck towards natural landing
 iswood=theme in ('wood','cafe')
 steps=max(5,st//12)
 for n in range(steps):
  yy=round(B+(40+h-B+st)*(n+.14)/steps)
  wid=sw+round(n*8/steps);left=cx-wid//2
  d.rectangle((left-4,yy-1,left+wid+4,yy+11),fill=dark)
  d.rectangle((left,yy,left+wid,yy+7),fill=c if n%2==0 else f)
  d.line((left+4,yy+2,left+wid-4,yy+2),fill=accent,width=2)
  if iswood:
   for tick in range(left+12,left+wid-4,21):d.line((tick,yy+2,tick,yy+7),fill=side,width=1)
 # On-ground landing at the bottom + tapered path joint
 d.polygon([(cx-sw//2-8,foot-6),(cx+sw//2+8,foot-6),(cx+sw//2+13,foot+11),(cx-sw//2-13,foot+11)],fill=side)
 d.line((cx-sw//2-5,foot-2,cx+sw//2+5,foot-2),fill=accent,width=3)
 # Lateral retaining stone, root ledges, balustrade pillars. Do NOT cover central stair width.
 for sideflag in (-1,1):
  xx=(L+8 if sideflag<0 else R-8)
  if theme in ('city','future','cafe','wood'):
   d.rectangle((xx-5,T-9,xx+5,T+25),fill=dark)
   d.rectangle((xx-3,T-14,xx+3,T-10),fill=accent)
  else:
   d.polygon([(xx-9,T+5),(xx-3,T-10),(xx+4,T-8),(xx+12,T+7)],fill=side)
   d.point((xx-2,T-8),fill=accent)
 # rails aligned along sides of stair, making the cause of height visible
 for sideflag in (-1,1):
  xx=sx-10 if sideflag<0 else sx+sw+10
  for n in range(4):
   yy=round(B+n*(foot-B)/3)
   d.rectangle((xx-3,yy-7,xx+3,yy+11),fill=dark)
   d.rectangle((xx-3,yy-10,xx+3,yy-7),fill=accent)
  d.line((xx,B-10,xx,foot+4),fill=side,width=3)
 # scenic-specific relief naturally connecting the stairs to the terrain
 if theme in ('garden','forest'):
  for xx in [L-1,R+1]:
   for i in range(5):
    yy=B-3+i*4;d.ellipse((xx-10,yy-3,xx+9,yy+4),fill=green)
 if theme in ('star','memory','crystal','night','future'):
  for xx,yy in [(L+13,T+23),(R-18,T+19),(L+27,B-24),(R-26,B-26)]:
   d.polygon([(xx,yy-4),(xx+3,yy),(xx,yy+4),(xx-3,yy)],fill=accent)
 fore=Image.new('RGBA',(W,H));fdraw=ImageDraw.Draw(fore)
 # The near-side parapet is rendered in world-depth order, stairs remain fully clear.
 fdraw.line((L+2,B-4,sx-7,B-4),fill=dark,width=5)
 fdraw.line((sx+sw+7,B-4,R-2,B-4),fill=dark,width=5)
 for x_ in [L+11,sx-7,sx+sw+7,R-11]:
  fdraw.rectangle((x_-3,B-20,x_+3,B+9),fill=side)
  fdraw.rectangle((x_-3,B-23,x_+3,B-18),fill=accent)
 return im,fore

def make_approach(name,s):
 rng=random.Random(seed_for(name+'approach'))
 W,H=144,168; im=Image.new('RGBA',(W,H));d=ImageDraw.Draw(im)
 base,top,side,dark,accent,green=[rgba(x) for x in THEMES[s['style']]]
 # Soft-edged approach path below stairs, not an isolated black/opaque plaque.
 for row in range(H):
  t=row/(H-1);alpha=int(195*(1-abs(t-.33)/.85)**1.8) if abs(t-.33)<.85 else 0
  w=52+int(15*t);l=W//2-w//2
  if alpha<=0:continue
  color=(*top[:3],alpha)
  for col in range(l,l+w):
   edge=min(col-l,l+w-1-col)
   aa=int(alpha*max(.12,min(1,edge/7)))
   d.point((col,row),fill=(*color[:3],aa))
 for i in range(135):
  xx=rng.randint(48,94);yy=rng.randint(4,151)
  d.rectangle((xx,yy,xx+rng.randint(1,3),yy+1),fill=(*side[:3],int(110*max(.3,1-yy/H))))
 return im

# Pixel-art props: each transparent RGBA asset is independent, documented, freely replaceable.
def prop_image(kind,variant):
 k=kind;w,h={
 'planter':(42,52),'planter_flowers':(50,56),'lantern':(36,74),'lamp_street':(46,114),
 'bench_wood':(112,62),'bench_stone':(110,59),'signpost':(76,88),'signboard':(88,75),
 'railing_wood':(108,40),'railing_stone':(108,39),'railing_metal':(112,35),
 'stone_wall':(110,50),'cliff_edge':(114,47),'bridge':(140,81),'wood_ramp':(128,80),
 'stone_step':(100,55),'boulder_moss':(85,62),'boulder_crystal':(87,72),
 'bush':(88,66),'flowers':(96,42),'reeds':(96,58),'banner':(52,105),
 'column':(44,105),'arch':(140,125),'fountain':(120,100),'viewpoint':(125,86),
 'dock_pile':(42,74),'stone_pillar':(50,85),'lamp_garden':(38,78),
 'mushroom':(88,52),'birdbath':(92,71),'trim':(128,35),
 }.get(k,(80,75))
 # Work at half-res to preserve deliberate blocky pixel edges, not vector clipart.
 W,H=w//2,h//2
 i=Image.new('RGBA',(W,H));d=ImageDraw.Draw(i)
 pal=THEMES.get(variant,THEMES['garden']); base,top,side,dark,gold,green=[rgba(v) for v in pal]
 def box(l,t,r,b,col,outline=None):rounded(d,(l,t,r,b),col,outline,radius=2,width=1)
 if k in ('planter','planter_flowers'):
  d.ellipse((W*.24,H*.35,W*.83,H*.73),fill=green)
  for x,y in [(.29,.38),(.55,.23),(.72,.39),(.53,.49)]:
   d.ellipse((W*x-5,H*y-5,W*x+5,H*y+5),fill=green,outline=side,width=1)
  d.polygon([(W*.22,H*.54),(W*.78,H*.54),(W*.69,H*.94),(W*.33,H*.94)],fill=base)
  d.rectangle((W*.21,H*.53,W*.8,H*.61),fill=gold)
  if k=='planter_flowers':
   for x,y in [(8,12),(W-11,15),(W//2,7),(W//2+8,13)]:d.ellipse((x-3,y-3,x+3,y+3),fill=gold,outline=side,width=1)
 elif k in ('lantern','lamp_street','lamp_garden'):
  if k=='lamp_street':
   d.rectangle((W//2-2,9,W//2+2,H-4),fill=dark)
   d.line((W//2,11,W//2+11,11),fill=dark,width=2)
   d.rectangle((W//2+7,10,W//2+14,18),fill=gold)
   d.rectangle((W//2+6,9,W//2+15,19),outline=base,width=2)
  else:
   d.rectangle((W//2-2,H*.37,W//2+2,H-3),fill=dark)
   d.polygon([(W//2-8,H*.36),(W//2-11,H*.23),(W//2+11,H*.23),(W//2+8,H*.36)],fill=base)
   d.rectangle((W//2-7,H*.26,W//2+7,H*.36),fill=gold)
   d.rectangle((W//2-9,H*.21,W//2+9,H*.24),fill=side)
 elif k.startswith('bench'):
  if k.endswith('wood'):
   d.rectangle((9,18,W-9,22),fill=base);d.rectangle((6,25,W-6,30),fill=top)
   d.line((11,16,W-11,16),fill=gold,width=2)
   for x in (14,W-14):d.rectangle((x-2,28,x+2,H-3),fill=dark)
  else:
   box(10,14,W-10,23,side,dark); box(8,25,W-8,31,top,side)
   for x in (15,W-15):d.rectangle((x-4,22,x+4,H-3),fill=dark)
 elif k in ('signpost','signboard'):
  box(W//2-2,18,W//2+2,H-3,dark)
  if k=='signpost':
   d.polygon([(4,13),(W-4,13),(W-10,28),(4,28)],fill=base)
   d.line((9,18,W-12,18),fill=gold,width=2)
  else:
   box(6,5,W-6,34,base,dark)
   for yy in (12,18,24):d.line((12,yy,W-13,yy),fill=gold if yy==12 else side,width=1)
 elif k.startswith('railing'):
  cc=base if k!='railing_metal' else side
  d.rectangle((3,15,W-3,20),fill=cc);d.rectangle((3,23,W-3,26),fill=dark)
  for x in range(8,W-2,13):d.rectangle((x-2,9,x+2,H-2),fill=dark);d.rectangle((x-2,7,x+2,10),fill=gold)
 elif k in ('stone_wall','cliff_edge','trim'):
  box(2,10,W-3,H-3,base,dark)
  for yy in range(16,H-4,8):
   d.line((7,yy,W-8,yy),fill=side,width=1)
   for xx in range(9+(yy%3)*5,W-6,18):d.line((xx,yy,xx,yy+7),fill=dark,width=1)
  d.line((3,9,W-4,9),fill=top,width=3)
  if k=='cliff_edge':
   for xx in (8,25,46):d.polygon([(xx,H-11),(xx+10,H-9),(xx+6,H-1)],fill=side)
 elif k in ('bridge','wood_ramp','stone_step'):
  box(3,17,W-4,H-4,top,side)
  for yy in range(21,H-2,8):d.line((5,yy,W-7,yy),fill=side,width=2)
  if k in ('bridge','wood_ramp'):
   for xx in (6,W-7):d.line((xx,5,xx,H-6),fill=dark,width=3)
   d.line((5,6,W-6,6),fill=gold,width=2)
 elif k in ('boulder_moss','boulder_crystal'):
  pts=[(3,H*.72),(W*.16,H*.4),(W*.37,H*.18),(W*.77,H*.23),(W-3,H*.65),(W*.82,H-2),(W*.19,H-2)]
  d.polygon(pts,fill=side)
  d.polygon([(W*.37,H*.18),(W*.77,H*.23),(W*.6,H*.45),(W*.3,H*.52)],fill=top)
  if k=='boulder_crystal':
   for xx in (.28,.55,.72):d.polygon([(W*xx,H*.48),(W*(xx+.09),H*.2),(W*(xx+.18),H*.5),(W*(xx+.12),H*.77)],fill=gold)
  else:
   for xx in (9,W//2,W-13):d.ellipse((xx,H*.37,xx+11,H*.46),fill=green)
 elif k in ('bush','flowers','reeds','mushroom'):
  if k=='mushroom':
   for xx in (13,W//2,W-12):
    d.rectangle((xx-3,18,xx+3,H-5),fill=gold)
    d.ellipse((xx-9,11,xx+9,23),fill=side)
    d.point((xx,14),fill=top)
  elif k=='reeds':
   for xx in range(7,W-5,7):
    height=int(H*(.28+(xx%4)*.15));d.line((xx,H-2,xx,H-height),fill=green,width=2)
    d.ellipse((xx-2,H-height-5,xx+1,H-height+3),fill=base)
  else:
   for xx in range(9,W-6,8):
    yy=H*.56+((xx%4)-2)*3
    d.ellipse((xx-7,yy-9,xx+7,yy+10),fill=green if xx%3 else side)
    if k=='flowers':d.ellipse((xx-2,yy-6,xx+2,yy-2),fill=gold)
 elif k=='banner':
  for xx in (W*.14,W*.86):d.rectangle((xx-2,3,xx+2,H-3),fill=dark)
  d.line((W*.14,7,W*.86,7),fill=gold,width=2)
  d.polygon([(W*.21,12),(W*.79,12),(W*.75,H*.7),(W*.49,H*.59),(W*.24,H*.7)],fill=side)
  d.polygon([(W*.49,19),(W*.55,25),(W*.49,31),(W*.43,25)],fill=gold)
 elif k in ('column','stone_pillar','dock_pile'):
  box(W*.27,H*.23,W*.73,H*.94,base,side)
  box(W*.14,H*.15,W*.86,H*.29,top,dark)
  box(W*.19,H*.85,W*.83,H*.96,side,dark)
  if k=='dock_pile':d.line((W*.22,H*.55,W*.79,H*.55),fill=gold,width=2)
 elif k=='arch':
  for xx in (W*.18,W*.82):box(xx-5,H*.18,xx+5,H-3,side,dark)
  d.arc((W*.15,1,W*.85,H*.52),180,360,fill=gold,width=5)
  d.arc((W*.15,7,W*.85,H*.54),180,360,fill=side,width=3)
 elif k=='fountain':
  d.ellipse((8,H*.67,W-8,H-3),fill=side,outline=dark,width=2)
  d.ellipse((13,H*.65,W-13,H*.82),fill=top)
  d.rectangle((W*.45,H*.30,W*.55,H*.68),fill=base)
  d.ellipse((W*.39,H*.25,W*.61,H*.39),fill=gold)
  for xx in (W*.3,W*.7):d.arc((xx-9,H*.27,xx+9,H*.63),20,155,fill=top,width=1)
 elif k=='viewpoint':
  d.polygon([(5,H*.55),(W-5,H*.55),(W-13,H-3),(13,H-3)],fill=side)
  d.ellipse((W*.3,H*.14,W*.70,H*.69),fill=base,outline=dark,width=3)
  d.ellipse((W*.42,H*.26,W*.58,H*.54),fill=gold)
  for xx in (12,W-12):d.line((xx,H*.2,xx,H-2),fill=dark,width=3)
 elif k=='birdbath':
  d.ellipse((10,H*.45,W-10,H*.7),fill=base,outline=dark,width=2)
  d.ellipse((15,H*.47,W-15,H*.59),fill=top)
  d.rectangle((W*.43,H*.62,W*.57,H-.04*H),fill=side)
 # a tiny non-neon grounding shadow for objects, never a giant colored rectangle
 if k not in ('flowers','reeds','trim','bridge','stone_step','wood_ramp'):
  d.line((W*.21,H-2,W*.79,H-2),fill=(18,25,28,52),width=1)
 return i.resize((w,h),Image.Resampling.NEAREST)

ASSET_TYPES={
 'planter_terracotta':('planter','city'),'planter_lavender':('planter_flowers','memory'),
 'planter_woodland':('planter','forest'),'lantern_gold':('lantern','night'),
 'street_lamp':('lamp_street','city'),'garden_lamp':('lamp_garden','garden'),
 'bench_wood':('bench_wood','wood'),'bench_stone':('bench_stone','city'),
 'signpost':('signpost','garden'),'information_board':('signboard','city'),
 'rail_wood':('railing_wood','wood'),'rail_stone':('railing_stone','garden'),
 'rail_metal':('railing_metal','night'),'wall_stone':('stone_wall','city'),
 'cliff_moss':('cliff_edge','forest'),'bridge_wood':('bridge','wood'),
 'ramp_wood':('wood_ramp','wood'),'step_stone':('stone_step','garden'),
 'rock_moss':('boulder_moss','forest'),'rock_crystal':('boulder_crystal','crystal'),
 'bush_lush':('bush','garden'),'wildflowers':('flowers','garden'),
 'reeds':('reeds','wood'),'banner_cafe':('banner','cafe'),
 'column_stone':('column','city'),'arch_memory':('arch','memory'),
 'fountain_tiered':('fountain','city'),'viewpoint':('viewpoint','star'),
 'dock_pile':('dock_pile','wood'),'pillar_crystal':('stone_pillar','crystal'),
 'mushroom_glow':('mushroom','memory'),'birdbath':('birdbath','garden'),
 'trim_terrain':('trim','garden')
}
THEME_PROPS={
 'city':['planter_terracotta','street_lamp','bench_stone','signpost','rail_stone','column_stone','information_board','fountain_tiered'],
 'garden':['planter_woodland','garden_lamp','bench_wood','bush_lush','rail_stone','wildflowers','birdbath','rock_moss'],
 'wood':['reeds','dock_pile','bench_wood','rail_wood','signpost','bridge_wood','ramp_wood','rock_moss'],
 'cafe':['planter_terracotta','bench_wood','banner_cafe','rail_wood','information_board','street_lamp','column_stone'],
 'night':['lantern_gold','bench_wood','rail_metal','banner_cafe','rock_crystal','mushroom_glow','viewpoint'],
 'memory':['planter_lavender','arch_memory','rail_stone','mushroom_glow','rock_crystal','bench_stone','pillar_crystal'],
 'star':['viewpoint','lantern_gold','rail_metal','rock_crystal','banner_cafe','pillar_crystal'],
 'forest':['rock_moss','mushroom_glow','bush_lush','cliff_moss','wildflowers','bench_wood','signpost'],
 'crystal':['rock_crystal','pillar_crystal','rail_stone','arch_memory','viewpoint','lantern_gold'],
 'future':['column_stone','rail_metal','viewpoint','arch_memory','bench_stone','planter_lavender']
}
# Extra areas are renewed with environment dressing but NO bogus stairs placed in cramped rooms.
OTHER_THEMES={
 'arland_room':'cafe','sofia_room':'cafe','dapur':'cafe','ruang_arsip':'memory',
 'clockwork_station':'future','moonlight_lake':'star','memory_bridge':'memory','ruang_dua_surat':'memory'
}

def main():
 mapping=json.loads((DATA/'maps.json').read_text(encoding='utf-8'))
 props=json.loads((DATA/'props.json').read_text(encoding='utf-8'))
 quests=json.loads((DATA/'quests.json').read_text(encoding='utf-8'))
 # Prevent duplicate decorations if rebuild script runs again.
 for area in mapping['areas'].values():
  area['props']=[v for v in area.get('props',[]) if not v['type'].startswith('v51_')]
 for key in list(props['props']):
  if key.startswith('v51_'): del props['props'][key]
 for name,(kind,theme) in ASSET_TYPES.items():
  path=PDIR/(name+'.png'); prop_image(kind,theme).save(path,optimize=True)
  # Small solid footprints for furniture and stone supports; floor & slender ornaments do not block quest routes.
  collision={'bench_wood':(52,9),'bench_stone':(54,11),'rock_moss':(24,13),
             'rock_crystal':(22,12),'planter_terracotta':(14,8),'planter_lavender':(14,8),
             'planter_woodland':(14,8),'column_stone':(14,10),'fountain_tiered':(48,18),
             'pillar_crystal':(12,12),'birdbath':(22,12)}.get(name,(0,0))
  # Mostly visually layered; collision-positive pieces placed only outside existing walk corridors.
  props['props']['v51_'+name]={'image':'props/environment_v51/'+name+'.png',
                             'cw':collision[0],'ch':collision[1],'layer':'sort'}
 for name,s in SPECS.items():
  area=mapping['areas'][name]; base,front=build_terrace(name,s)
  base_file='maps/environment_v51/'+name+'_platform.png'; front_file='maps/environment_v51/'+name+'_foreground.png'
  base.save(A/base_file,optimize=True); front.save(A/front_file,optimize=True)
  pth=make_approach(name,s);path_file='maps/environment_v51/'+name+'_approach.png';pth.save(A/path_file,optimize=True)
  area['elevationPlatforms']=[dict(id='terrace_'+name,x=s['x'],y=s['y'],w=s['w'],h=s['h'],rise=s['rise'],
         stairLength=s['stair'],stairWidth=s['stairWidth'],image=base_file,front=front_file,style=s['style'])]
  key='v51_approach_'+name
  props['props'][key]={'image':path_file,'cw':0,'ch':0,'layer':'floor'}
  foot=s['y']+s['h']+s['stair'];mid=s['x']+s['w']//2
  area['props'].append({'type':key,'x':mid,'y':foot+92})
  # Environment dressing uses the clear edges of planned structure rather than scatter on map.
  theme=s['style'];things=THEME_PROPS[theme];w=s['w'];h=s['h'];x=s['x'];y=s['y']
  # Decorative entries: purpose, relative coordinate (map y-down); verified for doors & quest footprint below.
  placements=[
   (things[0],x-28,y+h*.45),
   (things[1],x+w+30,y+h*.38),
   (things[2],x+w*.24,y+28),
   (things[3],x+w*.77,y+28),
   (things[4],x-22,y+h+22),
   (things[5],x+w+22,y+h+28),
   (things[6%len(things)],x+w+58,foot+32),
  ]
  # Position visually relevant props at the perimeter; no NPC or quest collision from new v5.1 furniture.
  for prop,xp,yp in placements:
   # keep props inside map; for positive collision definitions, guard against old main-story markers & obstacles.
   if xp<35 or yp<40 or xp>area['w']-35 or yp>area['h']-30:continue
   near_scene=False
   for marker in quests['side']:
    if marker.get('area')!=name or marker['id'].startswith('V50_VIEW_'):continue
    if abs(xp-marker.get('x',-9999))<60 and abs(yp-marker.get('y',-9999))<60:near_scene=True;break
   for door in area.get('doors',[]):
    rx,ry,rw,rh=door['rect']
    if abs(xp-(rx+rw/2))<100 and abs(yp-(ry+rh/2))<100:near_scene=True;break
   if not near_scene:
    for npc in quests.get('townNpcs',[]):
     places=[{'area':npc.get('area'),'x':npc.get('x',-99999),'y':npc.get('y',-99999)}] + npc.get('schedule',[])
     for loc in places:
      if loc.get('area')==name and abs(xp-loc.get('x',-99999))<59 and abs(yp-loc.get('y',-99999))<55:
       near_scene=True;break
     if near_scene:break
   if not near_scene:
    area['props'].append({'type':'v51_'+prop,'x':int(xp),'y':int(yp)})
  # Existing interactive panorama remains on the upper deck, preserving route scenes and unique IDs.
  it=next((v for v in quests['side'] if v['id']=='V50_VIEW_'+name.upper()),None)
  if it:
   it['x']=int(x+w/2);it['y']=int(y+h*.46)
   # Align optional scene point to the platform; no step/flag change.
  area['environmentV51']={'landmark':s['reason'],'theme':theme,'approach':path_file,
                          'design':'Hand-guided map landmark placement, walkable entry, bridge/deck/retaining-wall art, no randomized coordinates at runtime.'}
 # Contextual landmark details: use additional assets as integrated features, not just files in an asset folder.
 SPECIAL={
   'plaza':[('fountain_tiered',.34,.68),('wall_stone',.31,.34)],
   'taman_kota':[('step_stone',.70,.41),('trim_terrain',.64,.37)],
   'riverside':[('reeds',.57,.78),('bridge_wood',.61,.67)],
   'dermaga':[('dock_pile',.54,.54),('ramp_wood',.42,.40)],
   'hutan_bisik':[('cliff_moss',.37,.44),('rock_moss',.39,.49)],
   'star_path':[('rock_crystal',.70,.53)],
   'eternal_garden':[('arch_memory',.54,.40)],
   'memory_garden':[('arch_memory',.43,.41)],
   'cafe':[('banner_cafe',.79,.50)],
   'perpustakaan':[('information_board',.36,.45)],
   'rain_garden':[('pillar_crystal',.52,.51)]
 }
 for key,details in SPECIAL.items():
  a=mapping['areas'][key]
  for kind,fx,fy in details:
   x=int(a['w']*fx);y=int(a['h']*fy)
   near_story=False
   for mark in quests['side']:
    if mark.get('area')==key and abs(mark.get('x',-9999)-x)<70 and abs(mark.get('y',-9999)-y)<65:
     near_story=True;break
   if not near_story:
    a['props'].append({'type':'v51_'+kind,'x':x,'y':y})
 # Add real editable environment art for remaining eight locations, without cramming in fake stairs.
 for name,theme in OTHER_THEMES.items():
  area=mapping['areas'][name];palette=THEME_PROPS[theme]
  # Place near area's visible landmarks but farther than quest entries and old collision.
  locs=[(0.17,0.35),(0.83,0.30),(0.22,0.77),(0.79,0.78)]
  for j,(fx,fy) in enumerate(locs):
   obj=palette[(j+2)%len(palette)]
   # choose nonblocking small props near corners only
   if obj in ('bench_wood','bench_stone','rock_moss','rock_crystal','fountain_tiered'):
    obj=palette[(j+3)%len(palette)]
   x=int(area['w']*fx);y=int(area['h']*fy)
   area['props'].append({'type':'v51_'+obj,'x':x,'y':y})
  area['environmentV51']={'landmark':'Ambient decoration without forced staircase', 'theme':theme}
 mapping['_v51EnvironmentOverhaul']='21 hand-guided connected viewpoints, 29 dressed areas, 33 reusable editable props + 21 approaches. v5.0 assets preserved.'
 (DATA/'maps.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (DATA/'props.json').write_text(json.dumps(props,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (DATA/'quests.json').write_text(json.dumps(quests,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(f'v5.1 generated {len(SPECS)} sets of terrace art and approach paths, {len(ASSET_TYPES)} independent original prop PNG files, {len(mapping["areas"])} dressed areas')
if __name__=='__main__':main()
