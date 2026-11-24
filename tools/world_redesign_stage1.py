#!/usr/bin/env python3
"""Arland & Sofia v3.3 / World Art Direction Pass 01.

Three landmark-specific editable art layers for Plaza, Taman Kota and Kafe Senja.
Each output is built over immutable v3.2 source images. All modifications are
visual only, and the original alpha silhouette of each revised prop is retained.

Usage: python3 tools/world_redesign_stage1.py
Re-running is deterministic. Pillow + numpy required.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageEnhance, PngImagePlugin
import numpy as np
import hashlib
import random
import math
import shutil
import json

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / 'android/assets'
ART = ROOT / 'art_source/world_stage1'
BASE = ART / 'v32_unmodified'
LAYERS = ART / 'editable_layers'
MAPS = ('plaza', 'taman_kota', 'cafe')
PROPS = ('fountain', 'bld_arland_house', 'bld_sofia_house', 'bld_cafe',
         'tree_cherry','tree_green','tree_autumn','tree_pine',
         'gazebo','bridge_park','bench','lamp','flowerbed', 'hedge_tk',
         'garden_plot_tk','garden_plot_tk2','picnic_blanket','cafe_table',
         'cafe_table_c2','counter','display_case','bookshelf_c','rug_round',
         'plant_big','plant_big_c','sofa_c','cafe_umbrella_table','door','door_k')
SEED = 33021

def rng_for(k):
    return random.Random(int.from_bytes(hashlib.sha256(f'olu-v33:{k}'.encode()).digest()[:8], 'big'))

def original(kind, name):
    dest = BASE/kind/(name+'.png')
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        shutil.copy2(ASSETS/kind/(name+'.png'), dest)
    return Image.open(dest).convert('RGBA')

def nearest_mask(a):
    return Image.fromarray(np.where(a,255,0).astype('uint8'),'L')

def draw_clipped(dst, painter, mask, alpha=255):
    """Alpha composites the colored painter only inside map material category."""
    p = painter.copy()
    if alpha != 255:
        p.putalpha(ImageChops.multiply(p.getchannel('A'), Image.new('L',p.size, alpha)))
    p.putalpha(ImageChops.multiply(p.getchannel('A'), mask))
    return Image.alpha_composite(dst, p)

def material_masks(bg, kind):
    ar = np.asarray(bg.convert('RGB')).astype(np.int16)
    r,g,b = ar[:,:,0],ar[:,:,1],ar[:,:,2]
    grass = (g>r+16)&(g>b+10)&(g>85)
    stone = (r>g+6)&(g>b+8)&(r>146)&(b>83)
    water = (b>g+21)&(g>r+20)&(b>105)
    if kind=='cafe':
        stone = np.zeros_like(grass, dtype=bool)
        stone[228:] = True
        grass[:] = False
        water[:] = False
    return nearest_mask(grass),nearest_mask(stone),nearest_mask(water)

def repaint_ground(bg, name):
    """Repaint complete ground material *inside its original geometry*.
    Retains original local texture/luminance while replacing the generic palette
    with a warmer storybook material palette. No image silhouettes are moved.
    """
    arr=np.asarray(bg.convert('RGB'),dtype=np.float32)
    h,w=arr.shape[:2]
    out=np.zeros((h,w,4),dtype=np.uint8)
    r,g,b=arr[:,:,0],arr[:,:,1],arr[:,:,2]
    yy,xx=np.ogrid[:h,:w]
    # Slow tonal gradients: warm sun at top left, distant shadow at bottom.
    sun=5*np.cos((xx/w)*math.pi*.95)+6*(1-yy/h)
    grass=(g>r+16)&(g>b+10)&(g>85)
    path=(r>g+6)&(g>b+8)&(r>146)&(b>83)
    water=(b>g+21)&(g>r+20)&(b>105)
    if name=='plaza':
        targets=[(grass,(72,145,106),g,185,.47,180),
                 (path,(207,167,122),r,216,.55,178)]
    elif name=='taman_kota':
        targets=[(grass,(71,142,105),g,185,.46,167),
                 (path,(193,158,120),r,215,.49,171),
                 (water,(48,120,153),b,173,.45,188)]
    else:
        wall=(yy<216)*np.ones((1,w),bool)
        floor=(yy>=229)*np.ones((1,w),bool)
        targets=[(wall,(248,216,179),r,250,.35,105),
                 (floor,(154,95,65),r,178,.53,152)]
    for mask,center,intensity,origin,contrast,opacity in targets:
        for ch in range(3):
            v=np.clip(center[ch]+(intensity-origin)*contrast+sun,0,255)
            out[:,:,ch][mask]=v[mask].astype('uint8')
        out[:,:,3][mask]=opacity
    return Image.fromarray(out,'RGBA')

def line_rays(d, origin, W, H, color, gap=160):
    for k in range(-2,6):
        x=origin[0]+k*gap
        d.polygon([(origin[0],origin[1]), (x,H),(x+35,H)],fill=color)

def stone_mosaic(dest, cx, cy, rx, ry, colors, line_w=3):
    d=ImageDraw.Draw(dest,'RGBA')
    # Elliptical medallion, fine concentric inlay; flat paving, not an obstacle.
    for index,col in enumerate(colors):
        frac = 1.0-index*.13
        xx,yy=round(rx*frac),round(ry*frac)
        d.ellipse((cx-xx,cy-yy,cx+xx,cy+yy),outline=col,width=line_w+index%2)
    for t in range(0,360,30):
        ang=math.radians(t)
        px=cx+math.cos(ang)*(rx*.83);py=cy+math.sin(ang)*(ry*.83)
        w,h=9,5
        d.polygon([(px,py-h),(px+w,py),(px,py+h),(px-w,py)],fill=colors[(t//30)%len(colors)])
    for v in range(8):
        a=v*math.pi/4
        px=cx+math.cos(a)*rx*.44;py=cy+math.sin(a)*ry*.44
        d.line((px-6,py,px+6,py),fill=(245,218,151,115),width=2)
        d.line((px,py-6,px,py+6),fill=(245,218,151,115),width=2)

def rose_window(d,x,y,rad,col):
    for t in range(0,360,45):
        a=math.radians(t)
        px=x+int(math.cos(a)*rad*.64);py=y+int(math.sin(a)*rad*.64)
        d.polygon([(px,py-7),(px+7,py),(px,py+7),(px-7,py)],fill=col)
    d.ellipse((x-9,y-9,x+9,y+9),outline=(250,218,154,155),width=3)

def grass_flowers(d, w, h, rng, amount, mode):
    for i in range(amount):
        x=rng.randrange(35,w-35);y=rng.randrange(35,h-35)
        col=('#ffdbb6','#fff1d1','#e49db0','#f6b9d4','#e1a8c3')[(i+3)%5]
        if mode=='park' and i%3==0:
            # flower clumps: clustered blossoms and grass blades
            for j in range(5):
                xx=x+rng.randrange(-13,14);yy=y+rng.randrange(-8,9)
                d.rectangle((xx,yy,xx+4,yy+4),fill=col)
                d.rectangle((xx+1,yy+4,xx+2,yy+10),fill='#517a4f')
        else:
            d.line((x,y+5,x+2,y-4),fill='#326c51',width=2)
            d.rectangle((x-3,y-6,x+5,y),fill=col)
            d.point((x+1,y-3),fill='#fff3bd')

def subtle_light_spot(layer,x,y,rx,ry, rgb, strength=55):
    # Baked broad illumination with quantized 6px falloff to retain pixel-art style.
    ar=np.asarray(layer).copy()
    H,W=ar.shape[:2]
    xa=max(0,int(x-rx));xb=min(W,int(x+rx+1))
    ya=max(0,int(y-ry));yb=min(H,int(y+ry+1))
    if xa>=xb or ya>=yb:return layer
    yy,xx=np.ogrid[ya:yb,xa:xb]
    dist=((xx-x)/rx)**2+((yy-y)/ry)**2
    glow=np.clip((1-dist)**2,0,1)
    mask=np.minimum(255,np.round(glow*strength)).astype(np.uint8)
    sub=ar[ya:yb,xa:xb]
    # max used for isolated light sources (no overdraw alpha summation artifacts)
    keep=mask>sub[:,:,3]
    for z in range(3): sub[:,:,z][keep]=rgb[z]
    sub[:,:,3]=np.maximum(sub[:,:,3],mask)
    return Image.fromarray(ar,'RGBA')

def map_plaza(bg):
    W,H=bg.size
    grass,stone,water=material_masks(bg,'plaza')
    rng=rng_for('plaza');material=Image.new('RGBA',bg.size)
    # Cobblestone grout: handcrafted modular offset rows and warm stone facets.
    d=ImageDraw.Draw(material,'RGBA')
    for y in range(0,H,34):
        shift=17 if (y//34)%2 else 0
        for x in range(-50+shift,W,48):
            variant=rng.randrange(5)
            if variant in (0,3):
                d.rectangle((x+3,y+3,x+42,y+28),fill=(246,213,166,22))
            if variant==2:
                d.polygon([(x+7,y+27),(x+39,y+25),(x+35,y+31)],fill=(90,65,63,16))
            d.line((x,y+31,x+46,y+31),fill=(78,70,75,52),width=2)
            d.line((x+46,y+1,x+46,y+31),fill=(81,72,76,40),width=2)
            d.line((x+4,y+2,x+35,y+2),fill=(255,245,202,45),width=2)
    # Less uniform lawn; painterly garden patches beneath unchanged tree silhouettes.
    flowers=Image.new('RGBA',bg.size);fd=ImageDraw.Draw(flowers,'RGBA')
    grass_flowers(fd,W,H,rng,420,'plaza')
    material=draw_clipped(Image.new('RGBA',bg.size),material,stone,165)
    material=Image.alpha_composite(material,draw_clipped(Image.new('RGBA',bg.size),flowers,grass,160))
    # Gravel paths are edged with alternating handmade sandstone joints.
    accents=Image.new('RGBA',bg.size); d=ImageDraw.Draw(accents,'RGBA')
    # Hero medallion and radial lines centered on fountain footprint.
    stone_mosaic(accents,960,806,346,260,[(113,77,77,130),(255,242,203,153),(178,124,99,130),(250,204,142,122)],3)
    for cx,cy,rx,ry in [(500,730,85,51),(1420,730,85,51),(960,1050,80,57)]:
        stone_mosaic(accents,cx,cy,rx,ry,[(118,76,73,138),(255,215,140,155)],3)
        rose_window(d,cx,cy,23,(222,136,111,100))
    # Route-leading decorative mosaic lines, all 100% walkable.
    for y in [514,937]:
        d.line((310,y,1605,y),fill=(137,93,80,112),width=5)
        d.line((310,y+7,1605,y+7),fill=(255,229,169,115),width=3)
    for x in (370,960,1550):
        d.line((x,475,x,510),fill=(207,160,110,130),width=7)
        for px in range(x-24,x+28,13):
            d.rectangle((px,493,px+4,502),fill=(251,228,166,127))
    # Stone-only clipping keeps existing path, grass and doorway geography intact.
    accents=draw_clipped(Image.new('RGBA',bg.size),accents,stone,245)
    # Mixed old-world plaza motifs at the edges of grass, purely flat ground art.
    gacc=Image.new('RGBA',bg.size);gd=ImageDraw.Draw(gacc,'RGBA')
    for x,y in [(475,340),(1400,337),(500,1120),(1425,1135),(780,270),(1120,270)]:
        gd.ellipse((x-50,y-26,x+50,y+26),outline=(53,122,91,133),width=6)
        gd.ellipse((x-39,y-19,x+39,y+19),outline=(255,218,151,124),width=4)
        for ang in range(0,360,45):
            a=math.radians(ang)
            xx=x+math.cos(a)*31;yy=y+math.sin(a)*12
            gd.ellipse((xx-4,yy-4,xx+4,yy+4),fill=(237,150,161,168))
    accents=Image.alpha_composite(accents,draw_clipped(Image.new('RGBA',bg.size),gacc,grass,192))
    light=Image.new('RGBA',bg.size)
    for x in (360,960,1560):
        light=subtle_light_spot(light,x,442,170,158,(255,197,117),32)
    light=subtle_light_spot(light,960,780,350,240,(255,229,176),26)
    return material,accents,light

def map_taman(bg):
    W,H=bg.size;grass,stone,water=material_masks(bg,'taman_kota');rng=rng_for('park')
    material=Image.new('RGBA',bg.size);d=ImageDraw.Draw(material,'RGBA')
    # Distinct irregular old sandstone stepping stones on paths, not flat yellow paths.
    for y in range(0,H,27):
        offset=29 if (y//27)%2 else 0
        for x in range(-40+offset,W,60):
            shade=rng.choice([(248,219,157,36),(104,95,68,23),(220,182,113,34)])
            d.rounded_rectangle((x+3,y+4,x+52,y+21),radius=3,fill=shade,outline=(111,86,71,33),width=2)
            d.line((x+7,y+6,x+41,y+6),fill=(255,242,190,46),width=2)
    material=draw_clipped(Image.new('RGBA',bg.size),material,stone,200)
    wild=Image.new('RGBA',bg.size);wd=ImageDraw.Draw(wild,'RGBA')
    grass_flowers(wd,W,H,rng,850,'park')
    # ornamental lavender-like clusters in existing open grass
    for x,y in [(1150,580),(1390,630),(1650,790),(480,330),(1050,1040),(1660,1190)]:
        for t in range(28):
            xx=x+rng.randint(-65,65);yy=y+rng.randint(-45,45)
            wd.line((xx,yy+5,xx+2,yy-11),fill=(65,126,93,135),width=3)
            wd.rectangle((xx-4,yy-12,xx+5,yy-5),fill=rng.choice([(203,163,225,168),(242,178,199,170),(255,226,176,160)]))
    material=Image.alpha_composite(material,draw_clipped(Image.new('RGBA',bg.size),wild,grass,160))
    # Hand-layered shoreline highlighting and faint cast shadows. Bound to current water bitmap.
    accents=Image.new('RGBA',bg.size)
    wd=ImageDraw.Draw(accents,'RGBA')
    water_arr=np.asarray(water)>127
    # Open water glints: tiny diagonal highlights and reeds; enforce water mask afterwards.
    for idx in range(410):
        x=rng.randrange(270,1230);y=rng.randrange(410,1200)
        v=rng.randrange(3)
        if v==0:
            wd.line((x,y,x+14,y-2),fill=(208,240,239,105),width=2)
            wd.line((x+21,y+3,x+29,y+2),fill=(180,227,239,96),width=2)
        elif v==1:
            wd.arc((x-24,y-7,x+24,y+9),15,145,fill=(200,242,243,96),width=2)
        else:
            # floating lily leaf with reflective midrib
            wd.ellipse((x-10,y-5,x+10,y+6),fill=(51,115,87,210),outline=(166,198,116,190),width=2)
            wd.line((x,y,x+10,y-4),fill=(212,223,163,195),width=2)
    accents=draw_clipped(Image.new('RGBA',bg.size),accents,water,222)
    shore=Image.new('RGBA',bg.size);sd=ImageDraw.Draw(shore,'RGBA')
    for idx in range(550):
        x=rng.randint(195,1250); y=rng.randint(330,1290)
        if idx%4==0:
            sd.arc((x-24,y-9,x+24,y+10),-150,-20,fill=(251,236,193,120),width=3)
        else:
            sd.line((x,y,x+rng.randint(4,19),y),fill=(250,241,211,85),width=2)
    accents=Image.alpha_composite(accents,draw_clipped(Image.new('RGBA',bg.size),shore,water,140))
    # Stone mandala under gazebo; round medallion is a walkable painted motif.
    mosaic=Image.new('RGBA',bg.size);md=ImageDraw.Draw(mosaic,'RGBA')
    stone_mosaic(mosaic,1500,450,225,102,[(91,98,99,120),(254,213,156,135),(251,241,204,145),(209,147,132,100)],4)
    for x,y in [(1410,450),(1590,450),(1500,525)]:
        rose_window(md,x,y,30,(248,202,137,142))
    accents=Image.alpha_composite(accents,draw_clipped(Image.new('RGBA',bg.size),mosaic,grass,205))
    # The water and path masks are also saved for validation; no new collisions.
    light=Image.new('RGBA',bg.size)
    light=subtle_light_spot(light,1500,450,310,230,(253,207,159),40)
    light=subtle_light_spot(light,580,760,660,415,(205,230,231),27)
    return material,accents,light

def map_cafe(bg):
    W,H=bg.size;_,floor,_=material_masks(bg,'cafe');rng=rng_for('cafe')
    material=Image.new('RGBA',bg.size);d=ImageDraw.Draw(material,'RGBA')
    # Herringbone parquet inlay on original walkable wooden floor.
    for y in range(224,H,24):
        for x in range(0,W,48):
            off=(y//24%2)*24
            xx=x+off
            d.line((xx,y+2,xx+22,y+18),fill=(240,179,104,85),width=4)
            d.line((xx+23,y+18,xx+45,y+2),fill=(72,47,57,63),width=3)
            d.line((xx+5,y+1,xx+25,y+14),fill=(255,219,152,53),width=2)
    # Gold inlay diamonds spaced outside central furniture; clipped to base floor.
    for y in range(268,H,64):
        for x in range(32,W,96):
            if 290<x<680 and 380<y<590: continue
            d.polygon([(x,y-10),(x+13,y),(x,y+10),(x-13,y)],outline=(255,211,135,140),width=2)
            d.rectangle((x-2,y-2,x+2,y+2),fill=(126,65,68,130))
    material=draw_clipped(Image.new('RGBA',bg.size),material,floor,220)
    accents=Image.new('RGBA',bg.size);d=ImageDraw.Draw(accents,'RGBA')
    # Detailed wall paneling and ceiling line work, behind old wall-mounted props.
    d.rectangle((8,0,W-8,13),fill=(89,54,66,190))
    d.rectangle((8,13,W-8,20),fill=(245,192,126,205))
    d.line((12,111,W-12,111),fill=(165,86,83,74),width=3)
    d.rectangle((8,216,W-8,229),fill=(88,49,52,210))
    d.line((8,231,W-8,231),fill=(244,185,121,150),width=5)
    for x in range(35,920,125):
        if abs(x-160)<76 or abs(x-640)<76: continue  # don't paint across windows
        d.rectangle((x,34,x+90,108),outline=(163,96,83,110),width=3)
        d.line((x+7,44,x+83,44),fill=(255,241,204,110),width=2)
        d.rectangle((x+15,60,x+75,75),outline=(214,167,120,70),width=2)
    for x in range(22,W,160):
        d.rectangle((x,120,x+128,205),outline=(86,50,54,124),width=4)
        d.rectangle((x+5,125,x+123,199),outline=(249,188,128,110),width=2)
        d.line((x+12,185,x+116,185),fill=(104,57,57,85),width=3)
    # Painted ceiling pendant fixtures; flat wall decoration (no collision).
    for x in (370,610,895):
        d.line((x,18,x,53),fill=(74,53,64,170),width=4)
        d.polygon([(x-17,54),(x+17,54),(x+24,71),(x-24,71)],fill=(175,116,79,170))
        d.line((x-12,61,x+12,61),fill=(255,225,159,200),width=4)
        d.ellipse((x-9,68,x+9,79),fill=(255,221,151,165))
    # Large central floor border frames seating area, not a new obstacle.
    d.rounded_rectangle((250,345,707,617),radius=20,outline=(100,62,60,135),width=7)
    d.rounded_rectangle((263,358,695,607),radius=16,outline=(255,210,149,146),width=3)
    for x in range(287,693,34):
        for y in (362,604):
            d.polygon((x,y-5,x+5,y,x,y+5,x-5,y),fill=(249,225,169,132))
    # Window sunbeams on the floor and wall; physically baked behind furniture.
    light=Image.new('RGBA',bg.size)
    for x in (170,640):
        light=subtle_light_spot(light,x,160,190,170,(253,217,172),38)
        light=subtle_light_spot(light,x+38,380,220,205,(255,212,145),31)
    light=subtle_light_spot(light,480,330,320,280,(255,198,141),20)
    # Widened soft colored floor tile under lower right reading corner.
    return material,accents,light

def map_art_pass():
    out=[]
    for name in MAPS:
        bg=original('maps',name)
        repaint=repaint_ground(bg,name)
        material,accents,light={'plaza':map_plaza,'taman_kota':map_taman,'cafe':map_cafe}[name](bg)
        folder=LAYERS/name;folder.mkdir(parents=True,exist_ok=True)
        for key,layer in [('00_ground_palette',repaint),('01_materials',material),('02_landmarks',accents),('03_lighting',light)]:
            layer.save(folder/(key+'.png'), optimize=True)
        done=Image.alpha_composite(Image.alpha_composite(Image.alpha_composite(Image.alpha_composite(bg,repaint),material),accents),light)
        info=PngImagePlugin.PngInfo()
        info.add_text('visual_overhaul_v32','repaint-v32')
        info.add_text('world_art_pass','v3.3-stage1')
        done.save(ASSETS/'maps'/ (name+'.png'),optimize=True,pnginfo=info)
        out.append({'map':name,'dimensions':list(bg.size),'layers':4,'changed_pixels':int(np.count_nonzero(np.any(np.asarray(done)!=np.asarray(bg),axis=2)))})
    return out

def clipped(base, painter):
    a=base.getchannel('A')
    painter.putalpha(ImageChops.multiply(painter.getchannel('A'),a))
    out=Image.alpha_composite(base,painter)
    out.putalpha(a)
    return out

def paint_prop(name,base):
    rng=rng_for(name);w,h=base.size
    # Artist-directed palette substitution inside original transparent footprint.
    if name=='gazebo':
        ar=np.asarray(base).copy();h0,w0=ar.shape[:2]
        yy=np.arange(h0)[:,None]
        roof=(yy<78)&(ar[:,:,3]>0)&(ar[:,:,0]>150)&(ar[:,:,1]>150)&(ar[:,:,2]>150)
        for z,val in enumerate((159,93,79)):
            ar[:,:,z][roof]=(val+np.clip((ar[:,:,z][roof].astype(int)-235)*.23,-24,20)).clip(0,255).astype('uint8')
        poles=(yy>=78)&(ar[:,:,3]>0)&(ar[:,:,0]>165)&(ar[:,:,1]>165)&(ar[:,:,2]>160)
        for z,val in enumerate((180,127,91)):
            ar[:,:,z][poles]=(val+np.clip((ar[:,:,z][poles].astype(int)-225)*.24,-26,23)).clip(0,255).astype('uint8')
        base=Image.fromarray(ar,'RGBA')
    elif name=='bld_cafe':
        ar=np.asarray(base).copy();h0,w0=ar.shape[:2]
        yy=np.arange(h0)[:,None]
        roof=(yy<70)&(ar[:,:,3]>0)&(ar[:,:,0]>90)&(ar[:,:,1]>70)&(ar[:,:,2]>70)
        for z,val in enumerate((184,101,74)):
            ar[:,:,z][roof]=(val+np.clip((ar[:,:,z][roof].astype(int)-170)*.22,-22,23)).clip(0,255).astype('uint8')
        base=Image.fromarray(ar,'RGBA')
    p=Image.new('RGBA',base.size);d=ImageDraw.Draw(p,'RGBA')
    if name.startswith('bld_'):
        # Architectural restoration: shaded roof slates, lintels, ornate details.
        for y in range(9,59,12):
            for x in range(8+(y//12%2)*9,w-8,21):
                d.line((x,y,x+13,y),fill=(251,217,172,108),width=2)
                d.line((x+13,y+1,x+13,y+8),fill=(75,55,94,83),width=2)
        d.line((9,67,w-9,67),fill=(75,58,64,147),width=4)
        d.line((13,74,w-13,74),fill=(255,230,178,135),width=3)
        for x in (int(w*.24),int(w*.75)):
            d.rectangle((x-22,99,x+22,145),outline=(111,79,65,100),width=3)
            d.line((x-18,104,x+16,104),fill=(255,240,177,135),width=3)
            # flower boxes beneath windows
            d.rectangle((x-22,149,x+22,154),fill=(108,67,61,132))
            for j in range(6):
                xx=x-19+j*7
                d.rectangle((xx,143-rng.randint(0,4),xx+4,147),fill=rng.choice([(246,144,167,122),(252,215,144,134),(167,211,155,118)]))
        for x in range(18,w-18,30):
            d.line((x,177,x+12,177),fill=(107,75,65,73),width=2)
    elif name.startswith('tree_'):
        # Dappled foliage highlights and cool in-canopy shade, trunk remains legible.
        if name=='tree_pine':
            for k in range(10,95,13):
                yy=k
                width=min(27,max(7,int((yy/100)*37)))
                for t in range(4):
                    xx=w//2+rng.randrange(-width,width+1)
                    d.rectangle((xx,yy,xx+5,yy+3),fill=rng.choice([(194,232,185,130),(69,118,107,97),(255,225,175,70)]))
        else:
            for j in range(52):
                x=rng.randint(12,w-12);y=rng.randint(8,94)
                col=rng.choice([(255,235,191,82),(245,195,208,122),(69,117,83,73)]) if name=='tree_cherry' else rng.choice([(194,231,151,108),(40,101,93,83),(255,229,155,70)])
                d.rectangle((x,y,x+rng.randint(2,6),y+rng.randint(2,5)),fill=col)
            for x in (28,48,67):
                d.line((x,32,x+9,37),fill=(255,248,208,75),width=2)
    elif name=='fountain':
        # Visible scalloped carved stone, light on water, gilded inlay and rings.
        for t in range(0,360,18):
            a=math.radians(t);x=round(w/2+math.cos(a)*91);y=round(113+math.sin(a)*35)
            d.ellipse((x-4,y-3,x+4,y+3),fill=(255,229,184,145))
        for x in range(43,182,16):
            y=112+rng.randint(-12,14)
            d.line((x,y,x+7,y-2),fill=(219,249,244,137),width=2)
        d.ellipse((68,80,162,112),outline=(255,248,204,135),width=3)
        for y in (45,66,84):
            d.line((w//2-5,y,w//2+5,y),fill=(253,231,181,185),width=3)
    elif name=='gazebo':
        for k in range(10,77,9):
            x1=max(9,int(85-(k/78)*80));x2=min(w-9,int(85+(k/78)*80))
            d.line((x1,k,x2,k),fill=(249,213,176,95),width=2)
        for x in (19,44,85,125,151):
            d.line((x,82,x,130),fill=(181,114,103,70),width=3)
        d.line((5,131,w-5,131),fill=(238,198,139,142),width=5)
        for x in range(7,w-7,16):
            d.rectangle((x,143,x+6,146),fill=(123,87,77,102))
    elif name=='bridge_park':
        for x in range(6,w-5,15):
            d.line((x,5,x,58),fill=(95,63,51,83),width=3)
            d.line((x+4,5,x+4,58),fill=(253,213,152,91),width=2)
            d.rectangle((x,51,x+4,56),fill=(240,185,111,113))
        d.line((6,9,w-6,9),fill=(255,217,172,133),width=4)
    elif name in ('bench','lamp'):
        for y in range(7,h-6,12):
            d.line((2,y,w-4,y),fill=(255,209,151,110),width=2)
        if name=='lamp':
            d.ellipse((w//2-6,8,w//2+6,23),fill=(255,233,174,145))
    elif name in ('counter','display_case','bookshelf_c'):
        for x in range(6,w-5,20):
            d.line((x,h//2,x+9,h//2),fill=(245,201,141,115),width=2)
            if name=='counter':
                d.rectangle((x,h-20,x+12,h-5),outline=(88,59,56,105),width=2)
        d.line((3,5,w-5,5),fill=(253,223,169,136),width=3)
    elif name.startswith('cafe_table'):
        d.ellipse((11,5,w-11,29),outline=(245,190,146,125),width=2)
        for x in (w//2-10,w//2,w//2+10):
            d.rectangle((x,16,x+3,18),fill=(240,167,164,137))
    elif name.startswith(('garden_plot','hedge','flowerbed')):
        for j in range(14):
            x=rng.randrange(4,w-5); y=rng.randrange(3,max(5,h-8))
            d.rectangle((x,y,x+3,y+3),fill=rng.choice([(255,239,187,170),(230,165,204,150),(73,133,94,125)]))
    elif name in ('rug_round','picnic_blanket'):
        for j in range(15):
            t=j/15*math.pi*2;x=w/2+math.cos(t)*w*.37;y=h/2+math.sin(t)*h*.31
            d.polygon((x,y-3,x+4,y,x,y+3,x-4,y),fill=(237,186,124,145))
        d.ellipse((w*.16,h*.24,w*.84,h*.77),outline=(169,111,151,82),width=3)
    elif name.startswith('plant'):
        for j in range(18):
            x=rng.randrange(6,w-5);y=rng.randrange(6,h//2+5)
            d.rectangle((x,y,x+3,y+3),fill=rng.choice([(216,240,168,120),(246,204,174,80),(73,136,92,100)]))
    elif name=='sofa_c':
        for x in range(12,w-10,13):
            d.line((x,12,x+3,18),fill=(255,232,198,96),width=2)
        d.line((8,35,w-8,35),fill=(114,81,118,90),width=4)
    elif name=='cafe_umbrella_table':
        for x in range(8,w-9,12):
            d.line((x,10,x+10,38),fill=(250,212,173,96),width=3)
    elif name in ('door','door_k'):
        d.rectangle((6,6,w-8,h-6),outline=(255,214,145,113),width=3)
        d.rectangle((13,17,w-14,h-27),outline=(99,55,48,105),width=2)
    else:
        # Preserve existing details on less important props; subtle ink treatment.
        d.line((2,h-4,w-2,h-4),fill=(255,221,169,80),width=2)
    return clipped(base,p)

def prop_pass():
    stats=[]
    for name in PROPS:
        bg=original('props',name)
        done=paint_prop(name,bg)
        done.save(ASSETS/'props'/(name+'.png'), optimize=True)
        stats.append({'name':name,'size':list(bg.size),'alpha_preserved':bg.getchannel('A').tobytes()==done.getchannel('A').tobytes()})
    return stats

def main():
    maps=map_art_pass();props=prop_pass()
    meta={'version':'3.3.0-stage-1','areas':maps,'props_reworked':len(props),'props':props,
          'source':'v3.2.0','note':'No changes to maps.json, props.json, story/save/audio or collisions.'}
    (ART/'world_stage1_manifest.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
    print('WORLD STAGE 1:',[(m['map'],m['changed_pixels']) for m in maps],len(props),'props')

if __name__=='__main__':main()
