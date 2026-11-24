"""Arland & Sofia v3.2 — editable/reproducible art pass.
No map/collision/quest JSON mutations. Generate from art_source/visual_v32_base,
NOT from output, so repeated runs produce bitwise-identical PNG pixels.
Requires Pillow and NumPy. Run from project root: python3 tools/visual_overhaul_v32.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, PngImagePlugin
import numpy as np
import hashlib, json, math, random, shutil
ROOT=Path(__file__).resolve().parent.parent
ASSETS=ROOT/'android/assets'; BASE=ROOT/'art_source/visual_v32_base'
DATA=json.loads((ROOT/'tools/build/maps_base.json').read_text())
OUT=ROOT/'docs/preview'; OUT.mkdir(parents=True,exist_ok=True)

def seed(s): return int.from_bytes(hashlib.sha256(('OLU-visual-v32-'+s).encode()).digest()[:8],'big')
def backup(src, relative):
    dest=BASE/relative; dest.parent.mkdir(parents=True,exist_ok=True)
    if not dest.exists(): shutil.copy2(src,dest)
    return dest

def base_theme(area):
    if area in {'arland_room','sofia_room','cafe','toko_bunga','perpustakaan','ruang_arsip','dapur','arcade'}: return 'interior'
    if area=='gua_kristal': return 'cave'
    if area in {'star_path','starfall_village','memory_garden','eternal_garden','lantern_field'}: return 'magic'
    if area in {'riverside','dermaga'}: return 'waterside'
    if area in {'plaza','jalan_kota','perumahan'}: return 'urban'
    return 'nature'

PAL={
'urban': [(79,116,99),(249,208,153),(255,248,211),(190,129,152)],
'nature':[(42,108,84),(205,160,109),(250,222,152),(242,178,198)],
'waterside':[(65,125,142),(163,204,180),(255,237,176),(208,168,205)],
'magic':[(121,97,167),(173,148,227),(251,228,180),(243,184,220)],
'cave':[(86,91,148),(132,184,207),(206,221,255),(179,124,244)],
'interior':[(134,102,100),(213,175,128),(255,230,170),(218,160,193)],
}

def safe(meta,x,y,margin=34):
    w,h=meta['w'],meta['h']
    if x<margin or y<margin or x>w-margin or y>h-margin: return False
    if (x-meta['spawn'][0])**2+(y-meta['spawn'][1])**2<105**2: return False
    for rect in meta['walls']:
        xx,yy,ww,hh=rect
        if xx-12<x<xx+ww+12 and yy-12<y<yy+hh+12: return False
    for e in meta.get('examine',[]):
        if abs(x-e['x'])<42 and abs(y-e['y'])<36: return False
    for d in meta['doors']:
        xx,yy,ww,hh=d['rect']
        if xx-45<x<xx+ww+45 and yy-42<y<yy+hh+42: return False
    for p in meta['props']:
        if abs(x-p['x'])<38 and abs(y-p['y'])<38: return False
    return True

def alpha_box(d,x,y,s,color):
    d.rectangle((int(x),int(y),int(x+s),int(y+s)),fill=tuple(color))

def build_safe_mask(meta):
    """Precompute collision-safe decal pixels once; O(1) lookup instead of rescanning props."""
    w,h=meta['w'],meta['h']
    im=Image.new('1',(w,h),1);d=ImageDraw.Draw(im)
    d.rectangle((0,0,w-1,34),fill=0);d.rectangle((0,h-34,w-1,h-1),fill=0)
    d.rectangle((0,0,34,h-1),fill=0);d.rectangle((w-34,0,w-1,h-1),fill=0)
    sx,sy=meta['spawn'];d.ellipse((sx-105,sy-105,sx+105,sy+105),fill=0)
    for xx,yy,ww,hh in meta['walls']:
        d.rectangle((xx-12,yy-12,xx+ww+12,yy+hh+12),fill=0)
    for ex in meta.get('examine',[]):
        d.rectangle((ex['x']-42,ex['y']-36,ex['x']+42,ex['y']+36),fill=0)
    for door in meta['doors']:
        xx,yy,ww,hh=door['rect'];d.rectangle((xx-45,yy-42,xx+ww+45,yy+hh+42),fill=0)
    for prop in meta['props']:
        x,y=prop['x'],prop['y'];d.rectangle((x-38,y-38,x+38,y+38),fill=0)
    return im.load()

def motif(d,x,y,t,rng,pal):
    """Non-colliding pixel decals, different composition per biome."""
    c0,c1,c2,c3=pal
    if t in ('nature','waterside','urban'):
        k=rng.randrange(6)
        if k<=2: # small painterly flower/leaf cluster
            for j in range(rng.randint(4,9)):
                ox=rng.randrange(-20,21); oy=rng.randrange(-13,14)
                color=[c0,c1,c3][j%3]; d.rectangle((x+ox,y+oy,x+ox+3,y+oy+5),fill=color)
                if j%2==0: d.rectangle((x+ox+1,y+oy-3,x+ox+4,y+oy),fill=c2)
        elif k==3:
            for xx,yy in [(-12,0),(5,5),(-2,-7)]:
                d.polygon((x+xx-3,y+yy,x+xx,y+yy-5,x+xx+6,y+yy-2,x+xx+8,y+yy+3,x+xx,y+yy+5),fill=c1)
                d.line((x+xx-2,y+yy-1,x+xx+4,y+yy-1),fill=c2,width=2)
        elif k==4: # grass ridge
            for j in range(7):
                xx=x+j*5-18; h=rng.randrange(4,12)
                d.line((xx,y+3,xx+2,y-h),fill=c0,width=2)
                d.point((xx+1,y-h),fill=c2)
        else: # tiny decorative cobblestones
            for j in range(3):
                xx=x+j*11-14; d.rectangle((xx,y+j%2*3,xx+9,y+5+j%2*3),outline=c1,width=2)
    elif t=='interior':
        k=rng.randrange(4)
        if k==0: # parquet ornament
            d.line((x-13,y,x+13,y),fill=c1,width=2)
            d.line((x,y-7,x,y+7),fill=c0,width=2)
            for sx in (-10,10): d.rectangle((x+sx-2,y-2,x+sx+2,y+2),fill=c2)
        elif k==1:
            d.polygon([(x,y-12),(x+12,y),(x,y+12),(x-12,y)],outline=c1,width=2)
            d.rectangle((x-2,y-2,x+2,y+2),fill=c3)
        else:
            d.line((x-8,y-8,x+8,y+8),fill=c1,width=2)
            d.line((x-8,y+8,x+8,y-8),fill=c0,width=2)
            d.rectangle((x-2,y-2,x+2,y+2),fill=c2)
    elif t=='magic':
        r=rng.randrange(3)
        if r==0:
            d.line((x-22,y-13,x+20,y+11),fill=c1,width=2)
            for ox,oy in [(-22,-13),(20,11),(2,-1)]:
                d.line((x+ox-5,y+oy,x+ox+5,y+oy),fill=c2,width=2)
                d.line((x+ox,y+oy-5,x+ox,y+oy+5),fill=c2,width=2)
        elif r==1:
            d.ellipse((x-16,y-8,x+16,y+8),outline=c1,width=2)
            d.ellipse((x-6,y-6,x+6,y+6),outline=c2,width=2)
        else:
            for j in range(8):
                ang=j*math.pi/4; xx=int(x+math.cos(ang)*rng.randint(6,18)); yy=int(y+math.sin(ang)*rng.randint(6,18))
                d.rectangle((xx,yy,xx+3,yy+3),fill=[c1,c2,c3][j%3])
    else: # cave
        for j in range(rng.randint(3,7)):
            xx=x+rng.randrange(-20,21); yy=y+rng.randrange(-10,12)
            d.polygon([(xx-4,yy+4),(xx,yy-rng.randrange(5,14)),(xx+5,yy+4)],fill=c1)
            d.line((xx,yy-6,xx+1,yy+1),fill=c2,width=2)

def grade_ground(im,area,t):
    """Area-specific multi-scale lighting/color, with pixel-grid dithering."""
    w,h=im.size
    ar=np.asarray(im.convert('RGB'),dtype=np.float32)
    rr=random.Random(seed(area+'lighting'))
    grid=np.array([[rr.random() for _ in range(33)] for __ in range(23)],np.uint8)
    cloud=np.asarray(Image.fromarray(grid,'L').resize((w,h),Image.Resampling.BICUBIC),dtype=np.float32)/255.
    # Low-freq handcrafted light and shadows; no tile geometry altered.
    yy,xx=np.ogrid[:h,:w]
    sun_x=0.32*w if t in ('nature','urban') else .66*w
    sun_y=.24*h
    ray=np.exp(-((xx-sun_x)**2/(w*.62)**2+(yy-sun_y)**2/(h*.75)**2))
    var=(cloud-.5)*18+ray*9-3
    if t=='magic': tint=np.array([7,0,16]); brightness=4
    elif t=='cave': tint=np.array([1,4,14]);brightness=-3
    elif t=='interior': tint=np.array([8,3,0]);brightness=3
    elif t=='waterside': tint=np.array([0,7,9]);brightness=4
    else: tint=np.array([7,4,1]);brightness=3
    # Directional shadow/highlight on 4px blocks to keep pixel-art structure.
    ar=np.clip((ar-128)*1.09+128+var[:,:,None]+tint+brightness,0,255).astype('uint8')
    return Image.fromarray(ar,'RGB').convert('RGBA')

def maps():
    stats=[]
    for name,meta in DATA.items():
        path=ASSETS/meta['image']; raw=backup(path,Path('maps')/(name+'.png'))
        theme=base_theme(name); rng=random.Random(seed(name))
        im=grade_ground(Image.open(raw),name,theme); d=ImageDraw.Draw(im,'RGBA')
        w,h=im.size; pal=PAL[theme]
        # scenic radial pool lights in large repeated places, low alpha / ambience
        glow=Image.new('RGBA',(w,h)); gd=ImageDraw.Draw(glow,'RGBA')
        for k in range(4 if theme in ('magic','cave','interior') else 3):
            gx=rng.randrange(w//7,w*6//7); gy=rng.randrange(h//7,h*6//7)
            rad=rng.randrange(80,160) if theme in ('interior','cave') else rng.randrange(100,235)
            for radius in range(rad,20,-14):
                opacity=3 if theme in ('interior','nature') else 5
                gd.ellipse((gx-radius,gy-int(radius*.55),gx+radius,gy+int(radius*.55)),fill=(*pal[2],opacity))
        # source-over blend for light; do not change any collision geometry
        im=Image.alpha_composite(im,glow);d=ImageDraw.Draw(im)
        pixel_allowed=build_safe_mask(meta)
        target=min(370,max(65,int(w*h/6900)))
        placed=0; attempts=0
        while placed<target and attempts<target*38:
            attempts+=1
            x=rng.randrange(30,w-30); y=rng.randrange(30,h-30)
            if not pixel_allowed[x,y]: continue
            motif(d,x,y,theme,rng,pal); placed+=1
        # 22 distinct area stamps: scenic noninteractive floor mandala near an unoccupied location
        marks=0
        for _ in range(140):
            x=rng.randrange(90,w-90);y=rng.randrange(85,h-85)
            if pixel_allowed[x,y]:
                if theme in ('magic','cave'):
                    for r in (24,32,46): d.ellipse((x-r,y-r//2,x+r,y+r//2),outline=pal[1 if r==32 else 2],width=3)
                    for j in range(8):
                        a=j*math.pi/4; xx=int(x+40*math.cos(a));yy=int(y+20*math.sin(a))
                        d.rectangle((xx-3,yy-3,xx+3,yy+3),fill=pal[3])
                elif theme=='interior':
                    d.rounded_rectangle((x-44,y-22,x+44,y+22),radius=5,outline=pal[1],width=3)
                    d.rounded_rectangle((x-34,y-15,x+34,y+15),radius=4,outline=pal[2],width=2)
                else:
                    for r in (18,32,42): d.arc((x-r,y-r//2,x+r,y+r//2),0,350,fill=pal[1 if r%2 else 2],width=3)
                    for j in range(8):
                        a=j*math.pi/4; xx=int(x+45*math.cos(a));yy=int(y+23*math.sin(a))
                        d.rectangle((xx-3,yy-3,xx+3,yy+3),fill=pal[3])
                marks+=1
                if marks>=min(3,1+int(w*h>1000000)):break
        info=PngImagePlugin.PngInfo();info.add_text('world_polish_v23','1');info.add_text('world_polish_area',name)
        info.add_text('visual_overhaul_v32','repaint-v32');info.add_text('visual_original','art_source/visual_v32_base/maps/'+name+'.png')
        im.convert('RGB').save(path,pnginfo=info,optimize=True,compress_level=7)
        stats.append(dict(area=name,theme=theme,decals=placed,medallions=marks,original_bytes=raw.stat().st_size,new_bytes=path.stat().st_size))
        print(f'map {name:20s}: +{placed} details +{marks} ground patterns')
    return stats

# Make props more sculptural without modifying their PNG dimensions, anchor points, collision, or alpha boundary.
def props():
    total=0
    for path in sorted((ASSETS/'props').glob('*.png')):
        raw=backup(path,Path('props')/path.name)
        im=Image.open(raw).convert('RGBA');w,h=im.size
        if w<7 or h<7:continue
        arr=np.array(im); mask=arr[:,:,3]>90
        lum=arr[:,:,:3].astype(np.int16)
        # Color separation = stronger ink and highlight, preserve original alpha silhouette.
        lum=np.clip((lum-120)*1.14+120,0,255)
        arr[:,:,:3]=lum.astype('uint8')
        result=Image.fromarray(arr,'RGBA'); detail=Image.new('RGBA',(w,h));d=ImageDraw.Draw(detail,'RGBA')
        rng=random.Random(seed(path.stem));name=path.stem.lower()
        n=max(4,min(68,w*h//85))
        if any(x in name for x in ('tree','bush','flower','vine','wishing','hedge','grass')):
            colors=[(255,227,178,210),(249,169,200,220),(180,228,184,220),(110,188,150,160)]
            for i in range(n):
                xx=rng.randrange(1,w-1); yy=rng.randrange(1,max(2,int(h*.63)))
                if not mask[yy,xx]:continue
                r=rng.choice((1,1,2,2,3));d.rectangle((xx,yy,xx+r,yy+r),fill=colors[i%4])
        elif any(x in name for x in ('lamp','lantern','window','crystal','fountain','star','spark','moon','portal')):
            for i in range(n):
                xx=rng.randrange(1,w-1); yy=rng.randrange(1,h-1)
                if mask[yy,xx]:d.line((xx-2,yy,xx+2,yy),fill=(255,247,200,130),width=1)
        elif any(x in name for x in ('bld_','house','building','store','cafe','library')):
            for i in range(n):
                xx=rng.randrange(2,w-2); yy=rng.randrange(2,h-2)
                if not mask[yy,xx]:continue
                c=(254,219,154,95) if i%3==0 else (255,250,215,72)
                d.line((xx-3,yy,xx+3,yy),fill=c,width=1)
        else:
            for i in range(n):
                xx=rng.randrange(1,w-1); yy=rng.randrange(1,h-1)
                if mask[yy,xx] and i%2==0:d.line((xx-2,yy,xx+2,yy),fill=(255,233,202,86),width=1)
        # no alpha is allowed to leak outside the original prop's silhouette
        merged=Image.alpha_composite(result,detail)
        m=np.array(merged);m[:,:,3]=arr[:,:,3]
        # Original transparent pixels remain transparent (no extra geometry).
        Image.fromarray(m).save(path,optimize=True)
        total+=1
    print('Props upgraded:',total);return total

def sprite():
    total=0
    poses=0
    for directory in sorted((ASSETS/'characters').iterdir()):
        path=directory/'walk.png'
        if not path.exists():continue
        orig=Image.open(path).convert('RGBA')
        if orig.size!=(144,288):continue
        atlas=Image.new('RGBA',(48*12,72*4))
        idle=Image.new('RGBA',(48*6,72*4))
        for row in range(4):
            frames=[orig.crop((k*48,row*72,(k+1)*48,(row+1)*72)) for k in range(3)]
            for phase in range(12):
                # 12 distinct steps: unlike old 8 frame repeated sequence, weight shifts in torso and legs.
                swing=math.sin(phase*math.pi/6); stride=math.cos(phase*math.pi/6)
                f=0 if abs(swing)<.35 else (1 if swing>0 else 2)
                image=frames[f];cell=Image.new('RGBA',(48,72))
                feet=image.crop((0,52,48,72));torso=image.crop((0,30,48,54));head=image.crop((0,0,48,32))
                legx=int(round(stride*1.3)); bodyx=int(round(swing*.9))
                # stable foot anchor, no character hitbox changes
                cell.alpha_composite(feet,(legx,52))
                cell.alpha_composite(torso,(bodyx,30+int(abs(swing)>0.7)))
                cell.alpha_composite(head,(bodyx,max(0,int((1-stride)*.7))))
                # garment rim lighting + subtle movement crease
                dc=ImageDraw.Draw(cell,'RGBA')
                if phase in (2,3,8,9): dc.line((18,48,22,48),fill=(250,209,186,190),width=1)
                atlas.alpha_composite(cell,(phase*48,row*72))
            for phase in range(6):
                cell=frames[0].copy()
                dc=ImageDraw.Draw(cell,'RGBA')
                if row in (0,1,2):
                    # Blinking on two idle poses, only affect a couple pixels instead of face replacement.
                    if phase==4:
                        for xx in ((20,27) if row==0 else (26,)):
                            if cell.getpixel((xx,24))[3]>0:
                                dc.line((xx-2,24,xx+2,24),fill=(53,39,62,190),width=1)
                if phase in (1,2,3):
                    # subtle collar highlight breath
                    dc.line((21,34,26,34),fill=(240,218,205,145),width=1)
                idle.alpha_composite(cell,(phase*48,row*72))
        atlas.save(directory/'walk_v32.png',optimize=True)
        idle.save(directory/'idle_v32.png',optimize=True)
        total+=1
        # Keep poses.png untouched; already integrates with cutscenes and 16 poses.
        if (directory/'poses.png').exists(): poses+=1
    print('Actors upgraded:',total,'walk 12 frames + idle 6 frames, existing pose sheets:',poses)
    return total

def ninepatch(name,bg,frame,highlight,pressed=False):
    im=Image.new('RGBA',(64,64));d=ImageDraw.Draw(im)
    d.rounded_rectangle((0,0,63,63),radius=16,fill=(24,22,43,235))
    d.rounded_rectangle((2,2,61,61),radius=14,fill=frame)
    d.rounded_rectangle((5,5,58,58),radius=12,fill=bg)
    d.rounded_rectangle((9,9,54,54),radius=10,outline=highlight,width=2)
    d.line((16,6,48,6),fill=highlight,width=2)
    d.line((16,57,48,57),fill=highlight,width=2)
    for x,y in [(10,10),(53,10),(10,53),(53,53)]:
        d.polygon((x,y-4,x+4,y,x,y+4,x-4,y),fill=highlight)
    if pressed:d.line((19,53,45,53),fill=(247,207,169,230),width=2)
    im.save(ASSETS/'ui'/('v32_'+name+'.png'))

def menu():
    rng=random.Random(32032);w,h=1280,720
    img=Image.new('RGBA',(w,h)); d=ImageDraw.Draw(img)
    for y in range(720):
        t=y/720
        if t<.48:
            a=t/.48; col=(int(41+155*a),int(35+85*a),int(94+70*a),255)
        else:
            a=(t-.48)/.52;col=(int(196-110*a),int(120-50*a),int(164-70*a),255)
        d.line((0,y,1280,y),fill=col)
    # blocky distant sun + reflection gradients
    for r in range(155,38,-12):
        d.ellipse((925-r,315-r,925+r,315+r),fill=(243,174+int((155-r)/155*49),179,12))
    d.ellipse((868,257,982,371),fill=(255,217,159,255))
    # 4 layers of mountains/rooftops, pixel-stepped silhouettes
    for layer,(base,col) in enumerate([(415,(140,100,149)),(480,(104,81,127)),(544,(69,63,105)),(610,(44,48,80))]):
        pts=[(0,h)]
        for x in range(0,w+17,16):
            y=base+int(22*math.sin(x/155+layer)+11*math.cos(x/48+layer*2))
            pts.append((x,y));pts.append((x+15,y))
        pts.append((w,h));d.polygon(pts,fill=col)
    # windows and building silhouettes with lantern-lights
    for i in range(60):
        x=rng.randrange(0,w);bh=rng.randrange(25,105);yb=625
        d.rectangle((x,yb-bh,x+27,yb),fill=(48+rng.randrange(22),46,77,255))
        for dy in range(yb-bh+11,yb-5,17):
            for dx in (6,16):
                if rng.random()>.46:d.rectangle((x+dx,dy,x+dx+5,dy+7),fill=(255,193+rng.randrange(30),140,255))
    # falling petals stars
    for i in range(250):
        x=rng.randrange(10,w-10);y=rng.randrange(50,700)
        if rng.random()<.55:d.rectangle((x,y,x+2,y+2),fill=(250,204,207,rng.randrange(65,210)))
        else: d.line((x-3,y,x+3,y),fill=(255,238,185,rng.randrange(120,225)),width=1)
    img.save(ASSETS/'ui/v32_menu_far.png',optimize=True)
    near=Image.new('RGBA',(w,h));d=ImageDraw.Draw(near)
    d.polygon([(0,630),(200,625),(380,638),(630,624),(860,628),(1090,612),(1280,634),(1280,720),(0,720)],fill=(39,46,72,255))
    # Riverside bridge and candles; close vegetation
    for x in range(340,890,42):
        d.rectangle((x,585,x+6,680),fill=(48,37,66,255))
        d.rectangle((x-5,586,x+10,596),fill=(95,70,91,255))
    d.arc((330,548,905,657),180,360,fill=(40,38,68,255),width=10)
    for tx in (80,1185):
        d.rectangle((tx-11,422,tx+13,720),fill=(45,36,63,255))
        for cx,cy,r in [(tx-45,421,95),(tx+35,422,116),(tx,347,99),(tx-30,304,80)]:
            d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(54,69,89,255))
            d.arc((cx-r+10,cy-r+7,cx+r-8,cy+r-18),180,360,fill=(111,101,136,255),width=8)
            for i in range(20):
                px=cx+rng.randrange(-r+10,r-10);py=cy+rng.randrange(-r+10,r-10)
                if ((px-cx)**2+(py-cy)**2)<(r*.88)**2:d.rectangle((px,py,px+3,py+4),fill=(223,155,177,230))
    for x in (249,1019):
        d.rectangle((x,523,x+9,696),fill=(34,30,54,255))
        d.polygon([(x-13,532),(x+23,532),(x+16,503),(x-6,503)],fill=(101,72,94,255))
        d.rectangle((x-3,510,x+13,529),fill=(255,210,127,255))
        for r in (20,34,45): d.ellipse((x+5-r,518-r,x+5+r,518+r),outline=(253,205,143,100),width=2)
    for i in range(190):
        x=rng.randrange(w);y=rng.randrange(638,717)
        d.rectangle((x,y,x+rng.randrange(2,5),y+2),fill=rng.choice([(244,157,185,255),(226,187,215,255),(255,214,153,255)]))
    near.save(ASSETS/'ui/v32_menu_near.png',optimize=True)

def portraits():
    # Upgrade existing expression portraits without redrawing the subject or altering character likeness.
    count=0
    for ident in ('arland','sofia'):
        portrait_dir=ASSETS/'characters'/ident/'portraits'
        for path in sorted(portrait_dir.glob('*.png')):
            raw=backup(path,Path('portraits')/ident/path.name)
            im=Image.open(raw).convert('RGBA')
            # Preserve pixels that define the figure: a subtle graded light and art-book edge frame.
            im=ImageEnhance.Color(im).enhance(1.055)
            im=ImageEnhance.Contrast(im).enhance(1.045)
            overlay=Image.new('RGBA',im.size);d=ImageDraw.Draw(overlay,'RGBA')
            w,h=im.size
            accent=(231,151,184,255) if ident=='sofia' else (158,149,204,255)
            d.rectangle((1,1,w-2,h-2),outline=accent,width=2)
            d.rectangle((5,5,w-6,h-6),outline=(248,213,175,110),width=1)
            for x in (9,w-10):
                for y in (12,h-13):
                    d.line((x-4,y,x+4,y),fill=(252,218,178,170),width=2)
                    d.line((x,y-4,x,y+4),fill=(252,218,178,170),width=2)
            im=Image.alpha_composite(im,overlay)
            im.save(path,optimize=True)
            count+=1
    print('Expressive portraits reframed:',count)
    return count

def interface():
    variants={
      'panel':((252,240,226,255),(102,66,114,255),(253,207,177,255)),
      'panel_dark':((48,37,75,245),(184,143,175,255),(255,209,166,255)),
      'button':((253,234,220,255),(90,62,107,255),(249,190,192,255)),
      'button_down':((225,178,186,255),(90,62,107,255),(250,204,160,255)),
      'button_accent':((233,150,171,255),(97,58,105,255),(254,222,166,255)),
      'button_disabled':((207,204,211,255),(132,126,147,255),(233,222,230,255)),
    }
    for name,(bg,edge,hi) in variants.items():ninepatch(name,bg,edge,hi,name=='button_down')
    # Illustrated cinematic ribbon: keep 4:1 aspect so existing UI geometry works.
    im=Image.new('RGBA',(768,192));d=ImageDraw.Draw(im)
    for y in range(192):
        t=y/191;d.line((0,y,767,y),fill=(int(35+23*t),int(28+15*t),int(65+15*t),int(251-15*t)))
    d.rounded_rectangle((4,4,763,187),radius=19,outline=(235,172,191,255),width=6)
    d.rounded_rectangle((11,11,756,180),radius=15,outline=(246,214,172,240),width=2)
    for x in range(38,730,22):
        if x<280 or x>488:
            d.line((x,22,x+11,22),fill=(255,224,177,145),width=2)
            d.line((x,170,x+11,170),fill=(253,189,202,100),width=2)
    for cx in (39,727):
        for rad in (9,16,23):d.ellipse((cx-rad,96-rad,cx+rad,96+rad),outline=(250,191,197,225),width=2)
        d.polygon((cx,82,cx+10,96,cx,110,cx-10,96),fill=(252,213,164,235))
    im.save(ASSETS/'ui/v32_cinematic_ribbon.png',optimize=True)
    # Sophisticated bloom, color-faded alpha from radial falloff.
    n=384;yy,xx=np.mgrid[0:n,0:n];rr=np.sqrt(((xx-192)/192)**2+((yy-192)/192)**2)
    a=np.maximum(0,1-rr)**2.3*160
    arr=np.zeros((n,n,4),dtype='uint8');arr[:,:,:3]=[255,224,178];arr[:,:,3]=a.astype('uint8')
    Image.fromarray(arr,'RGBA').save(ASSETS/'ui/v32_bloom.png',optimize=True)
    # Extra transparent cutscene embellishments
    corners=Image.new('RGBA',(256,256));d=ImageDraw.Draw(corners)
    for i in range(8):
        s=22+i*11;d.arc((9,9,s,s),180,290,fill=(254,194,171,170-i*12),width=3)
    for i in range(22):
        a=i*.83;r=13+i*2
        x=int(43+math.cos(a)*r);y=int(40+math.sin(a)*r)
        if 0<=x<250 and 0<=y<250:d.rectangle((x,y,x+4,y+4),fill=(255,210,162,max(30,210-i*6)))
    corners.save(ASSETS/'ui/v32_scene_ornament.png')
    menu()
    return len(variants)+5

def preview(stats):
    # Honest asset preview: floor + background props composited at their real locations.
    specs=[]
    for id in ('plaza','taman_kota','cafe','gua_kristal','memory_garden','starfall_village'):
        meta=DATA[id];base=Image.open(ASSETS/meta['image']).convert('RGBA'); base.thumbnail((576,320),Image.Resampling.NEAREST)
        ratio=base.width/meta['w'];ratio_y=base.height/meta['h']
        # Original prop order, bottom-anchored just like GameScreen.drawProp()
        defs=json.loads((ASSETS/'data/props.json').read_text())['props']
        for pr in sorted(meta['props'],key=lambda o:o['y']):
            path=ASSETS/defs[pr['type']]['image']
            im=Image.open(path).convert('RGBA');im=im.resize((max(1,round(im.width*ratio)),max(1,round(im.height*ratio_y))),Image.Resampling.NEAREST)
            x=round(pr['x']*ratio-im.width/2);y=round(pr['y']*ratio_y-im.height)
            base.alpha_composite(im,(x,y)) if x>=0 and y>=0 and x+im.width<=base.width and y+im.height<=base.height else None
        specs.append((id,base))
    sheet=Image.new('RGB',(1200,1040),(28,25,46));d=ImageDraw.Draw(sheet)
    for n,(mid,im) in enumerate(specs):
        ox=20+(n%2)*600;oy=32+(n//2)*342
        box=im.copy();box.thumbnail((560,302));sheet.paste(box,(ox,oy));d.text((ox+4,oy+306),mid.replace('_',' ').title(),fill=(255,220,188))
    sheet.save(OUT/'v32_real_asset_composite.jpg',quality=94)

if __name__=='__main__':
    s=maps(); p=props();n=sprite();pt=portraits();u=interface();preview(s)
    report={'maps':s,'props':p,'actors':n,'ui_assets':u,'portraits':pt,'generated_assets':len(s)+p+2*n+pt+u}
    (ROOT/'docs/V32_VISUAL_ART_REPORT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print('DONE',len(s),'maps',p,'props',n,'characters',u,'UI/new cutscene assets')
