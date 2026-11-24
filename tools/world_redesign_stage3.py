#!/usr/bin/env python3
"""v3.5: handcrafted-in-code, deterministic stage-3 fantasy/forest art pass.

Uses the exact v3.4 PNGs as immutable baselines. All design layers are editable
transparent PNG. No collision, game/map data, story, save, or audio changes.
Re-run: python3 tools/world_redesign_stage3.py
"""
from __future__ import annotations
import hashlib, json, math, random, shutil
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageChops, PngImagePlugin

ROOT=Path(__file__).resolve().parent.parent
A=ROOT/'android/assets'
ART=ROOT/'art_source/world_stage3'
BASE=ART/'v34_unmodified'
LAYERS=ART/'editable_layers'
MAPS=('starfall_village','star_path','gua_kristal','lantern_field','hutan_bisik')
# Avoid modifying stage 1 / stage 2 props: preserve their independent regression hashes.
PROPS=(
 'star_stone','bld_star_house0','bld_star_house1','bld_star_house2','pedestal_book_map',
 'crystal_big','stalagmite_s0','stalagmite_s1','stalagmite_s2','stalagmite_s3','stalagmite_s4','stalagmite_s5','carving_flower','chest_gk',
 'lantern_off','tree_dark','bush','bush_plain','bush_berry','stone_lantern',
 'waterfall_hb','bridge_broken_hb','cave_entrance','carving_moon','tent','campfire',
 'log_bench','log_bench_b','carving_star','mushroom_ring','chest','chest_hs',
 'stone_lantern_e','signpost_e2','signpost_s2','signpost_hx',
)
SEED='arland-sofia-3.5-fantasy-art-03'

def rng(key):return random.Random(int(hashlib.sha256((SEED+key).encode()).hexdigest()[:16],16))
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def blank(sz):return Image.new('RGBA',sz,(0,0,0,0))
def original(folder,stem):
    fp=A/folder/(stem+'.png');old=BASE/folder/(stem+'.png');old.parent.mkdir(parents=True,exist_ok=True)
    if not old.exists():shutil.copy2(fp,old)
    return Image.open(old).convert('RGBA')

def get_masks(im,key):
    a=np.asarray(im.convert('RGB'),dtype=np.int16);r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
    bright=(r+g+b)/3
    if key=='starfall_village':
        path=(r>122)&(g>110)&(b>168)&(np.abs(r-g)<52)
        ground=(b>r+17)&(r>g+4)&(bright<135)
        return path,ground
    if key=='star_path':
        path=(bright>133)&(r>g-15)&(b>150)
        ground=(b>r+35)&(bright<110)
        return path,ground
    if key=='gua_kristal':
        land=(r>21)&(b>r+12)&(bright>35)&(bright<145)
        water=(b>g+10)&(g>r+23)&(g>80)&(b>145)
        return water,land
    if key=='lantern_field':
        path=(r>157)&(r>g+4)&(g>b+9)&(b>102)
        ground=(b>r+23)&(g>r+8)&(bright<137)
        return path,ground
    # hutan_bisik
    path=(r>129)&(r>g+13)&(g>b+11)
    ground=(g>r+30)&(g>b+30)&(g>95)
    return path,ground

def clip(im,mask):
    arr=np.asarray(im).copy();arr[:,:,3]=np.where(mask,arr[:,:,3],0)
    return Image.fromarray(arr,'RGBA')

def tint(base,mask,target,amount,contrast=.24):
    a=np.asarray(base.convert('RGB'),dtype=np.float32);v=a.mean(2);h,w=v.shape
    yy=np.arange(h,dtype=np.float32)[:,None]/h
    xx=np.arange(w,dtype=np.float32)[None,:]/w
    light=6*np.cos(xx*math.pi*1.4)+6*(1-yy)
    arr=np.zeros((h,w,4),dtype=np.uint8)
    for c in range(3):
        val=np.clip(target[c]+(v-110)*contrast+light,0,255).astype('uint8');arr[:,:,c][mask]=val[mask]
    arr[:,:,3][mask]=amount
    return Image.fromarray(arr,'RGBA')

def glow(size,spots):
    w,h=size;ar=np.zeros((h,w,4),dtype=np.uint8)
    for x,y,rx,ry,col,power in spots:
        x0=max(0,int(x-rx));x1=min(w,int(x+rx)+1);y0=max(0,int(y-ry));y1=min(h,int(y+ry)+1)
        yy,xx=np.ogrid[y0:y1,x0:x1];t=np.maximum(0,1-((xx-x)/rx)**2-((yy-y)/ry)**2)
        alpha=np.minimum(255,(t*t*power)).astype('uint8');view=ar[y0:y1,x0:x1];m=alpha>view[:,:,3]
        for c in range(3):view[:,:,c][m]=col[c]
        view[:,:,3]=np.maximum(view[:,:,3],alpha)
    return Image.fromarray(ar,'RGBA')

def star(d,x,y,r,c,halo=False):
    x=int(x);y=int(y);r=int(r)
    if halo:
        d.ellipse((x-r*3,y-r*3,x+r*3,y+r*3),fill=(c[0],c[1],c[2],min(28,c[3]//4)))
    d.polygon([(x,y-r),(x+max(2,r//3),y-max(2,r//3)),(x+r,y),(x+max(2,r//3),y+max(2,r//3)),(x,y+r),(x-max(2,r//3),y+max(2,r//3)),(x-r,y),(x-max(2,r//3),y-max(2,r//3))],fill=c)

def material_layer(name,base,walk,ground):
    im=blank(base.size);d=ImageDraw.Draw(im,'RGBA');w,h=base.size;r=rng(name+':material')
    if name=='starfall_village':
        # Distinct old-town star-mosaic roadwork with inset marquetry, not random noise.
        for y in range(0,h,28):
            for x in range(0,w,52):
                j=0 if (y//28)%2==0 else 24
                xx=x+j;d.line((xx,y,xx+45,y),fill=(87,64,139,64),width=2)
                if (x//52+y//28)%7==0:d.polygon([(xx+22,y+7),(xx+29,y+14),(xx+22,y+21),(xx+15,y+14)],outline=(245,224,173,118),width=2)
        for k in range(1250):
            x=r.randrange(w);y=r.randrange(h)
            if k%4==0:star(d,x,y,r.randint(2,4),(242,222,183,108))
            else:d.line((x,y,x+4,y-3),fill=(199,178,244,66),width=2)
        return clip(im,walk|ground)
    if name=='star_path':
        for k in range(390):
            x=r.randrange(15,w-15);y=r.randrange(15,h-15)
            if k%4==0:
                star(d,x,y,r.randint(4,8),(202,220,255,137),True)
            else:
                d.ellipse((x-2,y-2,x+2,y+2),fill=(192,185,244,85))
        # silver road tile joints and specks restricted to illuminated walkable strip
        for y in range(0,h,24):
            for x in range((y//24%2)*17,w,38):
                d.line((x,y,x+21,y),fill=(143,131,212,98),width=2)
                if (x+y)%5==0:d.rectangle((x+9,y+4,x+11,y+6),fill=(255,246,211,122))
        return clip(im,walk|ground)
    if name=='gua_kristal':
        # cool chiseled strata / fine mineral veins. Always clipped to island terrain.
        for k in range(820):
            x=r.randrange(w);y=r.randrange(h)
            if k%11==0:
                d.line((x-16,y+8,x,y-8,x+16,y-2),fill=(139,191,221,127),width=3)
                d.line((x-12,y+4,x,y-11),fill=(212,243,255,96),width=2)
            elif k%4==0:star(d,x,y,3,(134,213,249,125))
            else:d.line((x,y,x+8,y-3),fill=(121,145,198,68),width=2)
        return clip(im,ground)
    if name=='lantern_field':
        # floral patches in blue meadow + warm gold engraved walkway pattern.
        for k in range(1120):
            x=r.randrange(8,w-8);y=r.randrange(8,h-8)
            if k%9==0:
                for dx,dy in [(-5,0),(5,0),(0,-5),(0,5)]:d.ellipse((x+dx-2,y+dy-2,x+dx+2,y+dy+2),fill=(248,205,157,137))
                d.rectangle((x-2,y-2,x+2,y+2),fill=(255,246,198,164))
            elif k%3==0:d.line((x,y,x+2,y-7),fill=(122,184,184,81),width=2)
        return clip(im,ground)
    if name=='hutan_bisik':
        # Three-leaf clusters and fallen bark; clipped to the original green terrain.
        for k in range(2600):
            x=r.randrange(10,w-10);y=r.randrange(10,h-10)
            if k%11==0:
                c=r.choice([(252,212,149,140),(218,155,109,112),(232,180,123,121)])
                d.polygon([(x-8,y-3),(x-3,y-9),(x+2,y-5),(x+5,y+4),(x,y+8)],fill=c)
                d.line((x-4,y-5,x+3,y+7),fill=(115,85,58,120),width=1)
            elif k%3==0:
                for dx,dy in [(0,-3),(4,1),(-4,1)]:d.ellipse((x+dx-3,y+dy-3,x+dx+3,y+dy+3),fill=(165,208,136,77))
            else:d.line((x,y,x+7,y-3),fill=(56,102,64,67),width=2)
        return clip(im,ground)

def focal_layer(name,size,walk,ground):
    w,h=size;im=blank(size);d=ImageDraw.Draw(im,'RGBA');r=rng(name+':focal')
    if name=='starfall_village':
        # Cobblestone rings around village meeting square + embedded starmap. Ground-only.
        cx,cy=960,665
        for rx,ry in [(315,193),(270,165),(219,132)]:
            d.ellipse((cx-rx,cy-ry,cx+rx,cy+ry),outline=(244,220,180,139),width=4)
        for i in range(24):
            a=i*math.tau/24;x=cx+int(286*math.cos(a));y=cy+int(170*math.sin(a))
            star(d,x,y,8,(255,215,152,155))
        for i in range(5):
            x=530+i*213;y=680+int(math.sin(i*1.4)*75)
            star(d,x,y,11,(247,232,199,145))
            if i>0:d.line((530+(i-1)*213,680+int(math.sin((i-1)*1.4)*75),x,y),fill=(244,214,153,93),width=3)
        return clip(im,walk)
    if name=='star_path':
        # A trail of constellation emblems, threaded precisely around the established road.
        points=[(180,590),(450,540),(780,665),(1030,450),(1310,610),(1610,455),(1890,550)]
        for i,(x,y) in enumerate(points):
            rr=24 if i%2 else 34
            d.ellipse((x-rr,y-rr*.58,x+rr,y+rr*.58),outline=(239,216,255,114),width=3)
            star(d,x,y,13,(242,228,186,140))
        for a,b in zip(points,points[1:]):
            # Deliberately decorative silver dashed lines, no traversable bridge created.
            x1,y1=a;x2,y2=b
            for t in np.linspace(0,1,22):
                x=x1*(1-t)+x2*t;y=y1*(1-t)+y2*t
                d.ellipse((x-1,y-1,x+1,y+1),fill=(177,186,235,90))
        return clip(im,ground) # keep markings off the white zigzag walkway
    if name=='gua_kristal':
        # Carved runes on existing stone with thin mineral filigree.
        for x,y in [(255,360),(411,650),(980,260),(1030,630),(640,720)]:
            for rx,ry in [(32,21),(22,14)]:d.ellipse((x-rx,y-ry,x+rx,y+ry),outline=(143,224,246,132),width=3)
            star(d,x,y,11,(220,242,255,166))
        for x,y in [(420,275),(920,370),(335,650),(820,840)]:
            d.line((x-26,y+26,x-10,y-21,x+8,y+9,x+25,y-32),fill=(127,205,226,143),width=4)
            d.line((x-26,y+22,x-10,y-23),fill=(237,251,255,121),width=2)
        return clip(im,ground)
    if name=='lantern_field':
        # Central festival seal inset into paved circle and hand-laid border lantern petals.
        cx,cy=960,632
        for rx,ry in [(155,108),(131,88),(95,65)]:d.ellipse((cx-rx,cy-ry,cx+rx,cy+ry),outline=(248,216,156,123),width=4)
        for i in range(16):
            a=i*math.tau/16;x=cx+int(133*math.cos(a));y=cy+int(88*math.sin(a))
            d.ellipse((x-6,y-4,x+6,y+4),fill=(237,156,110,153))
            d.rectangle((x-2,y-2,x+2,y+2),fill=(255,247,190,184))
        for x,y in [(960,609),(939,632),(982,633),(960,655)]:star(d,x,y,11,(246,209,163,149))
        return clip(im,walk)
    if name=='hutan_bisik':
        # Foreground details: woodland waymarks on roads, river banks along x≈1350.
        for x,y in [(1180,1650),(1080,1180),(660,1120),(1530,630),(1730,1090),(2060,620)]:
            d.ellipse((x-29,y-20,x+29,y+20),outline=(238,219,166,114),width=3)
            star(d,x,y,8,(221,210,154,124))
        for y in range(70,h-50,49):
            x=int(1390+20*math.sin(y/180))
            d.arc((x-26,y-6,x+32,y+14),4,152,fill=(221,247,245,129),width=3)
        return im
    return im

def atmosphere(name,size):
    w,h=size
    if name=='starfall_village':spots=[(310,420,480,410,(230,166,255),38),(960,640,550,390,(255,205,153),39),(1510,400,420,380,(156,189,255),31)]
    elif name=='star_path':spots=[(790,480,600,440,(131,151,242),41),(1575,520,580,450,(234,192,255),33)]
    elif name=='gua_kristal':spots=[(430,490,340,350,(86,220,244),60),(975,340,330,355,(155,115,250),59),(620,600,320,240,(113,199,243),36)]
    elif name=='lantern_field':spots=[(960,650,510,390,(255,181,113),66),(1550,430,340,260,(255,202,148),35),(320,930,330,320,(217,175,232),38)]
    else:spots=[(700,600,500,480,(255,218,148),28),(1750,650,440,450,(134,211,177),30),(1320,1230,390,530,(115,217,228),33)]
    return glow(size,spots)

def boundary_layer(name,base,walk,ground):
    w,h=base.size;layer=blank(base.size);d=ImageDraw.Draw(layer,'RGBA');r=rng(name+':edge')
    # Gently edge the original pathways with color, preserving exact geometry.
    if name!='gua_kristal':
        # Mask derivative (not a new walkable path).
        edge=walk & (~np.roll(walk,4,axis=0)|~np.roll(walk,-4,axis=0)|~np.roll(walk,4,axis=1)|~np.roll(walk,-4,axis=1))
        edge[:4,:]=False;edge[-4:,:]=False;edge[:,:4]=False;edge[:,-4:]=False
        arr=np.zeros((h,w,4),dtype='uint8')
        col=(252,225,164,101) if name in ('starfall_village','lantern_field') else (170,209,248,91)
        arr[edge]=col
        layer=Image.fromarray(arr,'RGBA')
    else:
        # existing central water: horizontally dappled reflections only in detected water mask.
        for i in range(95):
            x=r.randrange(285,1050);y=r.randrange(395,860)
            d.line((x,y,x+r.randint(9,37),y),fill=(184,239,255,119),width=2)
        layer=clip(layer,walk)
    return layer

def prop_details(name,base):
    w,h=base.size;r=rng(name+':prop');im=blank(base.size);d=ImageDraw.Draw(im,'RGBA');cx=w//2
    if name.startswith('bld_star_house'):
        # Painted ceramic roof shingle rhythms and lit windows, retained building contours.
        for y in range(7,max(8,h//2),10):
            for x in range(7,w-7,18):
                k=(y//10)%2*8;d.line((x+k,y,x+k+12,y),fill=(255,226,204,113),width=2)
                d.line((x+k+4,y+4,x+k+14,y+4),fill=(96,89,163,107),width=2)
        for x in (w//3,2*w//3):
            d.rectangle((x-10,h//2+5,x+11,h//2+24),fill=(255,208,130,127))
            d.rectangle((x-5,h//2+9,x+6,h//2+18),fill=(255,243,183,136))
        d.line((4,h-13,w-5,h-13),fill=(239,207,195,118),width=3)
    elif name=='star_stone':
        d.ellipse((2,2,w-3,h-3),outline=(232,208,251,132),width=2)
        star(d,cx,h//2,max(3,min(w,h)//5),(249,224,165,199))
    elif name=='pedestal_book_map':
        d.line((4,5,w-5,5),fill=(255,225,178,150),width=3)
        star(d,cx,h//3,4,(246,226,176,156))
    elif name=='crystal_big' or name.startswith('stalagmite_s'):
        for dx in (-w//5,0,w//6):
            d.line((cx+dx,6,cx+dx-2,h-9),fill=(220,251,255,128),width=2)
        for yy in range(9,h-9,13):d.line((w//3,yy,cx,yy-4),fill=(146,189,253,79),width=2)
        star(d,cx,h//3,max(3,min(w,h)//9),(199,248,255,173))
    elif name in ('carving_flower','carving_moon','carving_star'):
        d.ellipse((3,3,w-4,h-4),outline=(226,218,255,134),width=2)
        star(d,cx,h//2,max(3,min(w,h)//7),(246,240,189,147))
    elif name.startswith('chest'):
        d.line((4,7,w-4,7),fill=(251,229,173,158),width=2)
        d.line((4,h//2,w-4,h//2),fill=(119,83,66,141),width=2)
        d.rectangle((cx-3,h//2-4,cx+3,h//2+5),fill=(255,229,145,180))
    elif name in ('tree_dark',):
        for _ in range(max(18,w*h//880)):
            x=r.randrange(max(1,w//8),max(3,w-w//8));y=r.randrange(6,max(7,int(h*.67)))
            d.rectangle((x,y,x+4,y+3),fill=r.choice([(133,176,146,117),(95,147,145,117),(205,184,149,78)]))
    elif name.startswith('bush'):
        for _ in range(max(7,w*h//310)):
            x=r.randrange(3,max(4,w-3));y=r.randrange(3,max(4,h-3))
            d.ellipse((x-2,y-2,x+3,y+2),fill=(172,211,153,107))
    elif name in ('lantern_off','stone_lantern','stone_lantern_e'):
        d.rectangle((cx-5,max(3,h//4),cx+5,max(6,h//4+11)),fill=(255,205,115,168))
        d.rectangle((cx-2,max(5,h//4+2),cx+2,max(8,h//4+7)),fill=(255,241,162,185))
        d.line((3,h-8,w-4,h-8),fill=(219,207,191,107),width=2)
    elif name=='waterfall_hb':
        for x in range(7,w-7,10):
            d.line((x,7,x+4,h-13),fill=(236,249,252,119),width=2)
            d.line((x+2,15,x+3,h-8),fill=(115,187,217,112),width=2)
    elif name=='bridge_broken_hb':
        for x in range(8,w-7,14):
            d.line((x,4,x+4,h-7),fill=(242,207,145,138),width=2)
            d.rectangle((x+3,h//2,x+5,h//2+3),fill=(74,52,48,115))
    elif name=='cave_entrance':
        d.arc((4,2,w-6,h-7),190,350,fill=(193,227,198,155),width=3)
        for x in range(7,w-7,13):d.rectangle((x,7,x+3,11),fill=(132,183,155,111))
    elif name in ('tent','campfire'):
        for x in range(5,w-6,12):d.line((x,5,x+6,15),fill=(247,224,169,104),width=2)
        star(d,cx,h//3,4,(255,228,143,143))
    elif name in ('log_bench','log_bench_b'):
        for x in range(5,w-4,12):d.line((x,4,x+2,h-4),fill=(249,210,139,117),width=2)
    elif name=='mushroom_ring':
        for i in range(12):
            a=i*math.tau/12;x=int(cx+math.cos(a)*(w*.33));y=int(h*.56+math.sin(a)*(h*.24))
            d.ellipse((x-3,y-3,x+3,y+3),fill=(251,214,147,151))
    elif name.startswith('signpost'):
        for y in (8,16):d.line((5,y,w-5,y),fill=(253,227,182,145),width=2)
        star(d,cx,max(4,h//4),3,(239,216,156,154))
    # Never extend silhouettes or collision: every output alpha exactly matches baseline.
    a=base.getchannel('A');im.putalpha(ImageChops.multiply(im.getchannel('A'),a))
    out=Image.alpha_composite(base,im);out.putalpha(a)
    return out

def main():
    entries=[];props=[]
    for name in MAPS:
        base=original('maps',name);walk,ground=get_masks(base,name);size=base.size
        # Five fully editable per-area pixel-art PNG layers.
        if name=='starfall_village':p=tint(base,walk,(204,184,218),142);p=Image.alpha_composite(p,tint(base,ground,(62,65,143),101))
        elif name=='star_path':p=tint(base,walk,(216,202,255),99);p=Image.alpha_composite(p,tint(base,ground,(23,26,100),83))
        elif name=='gua_kristal':p=tint(base,ground,(55,59,101),104);p=Image.alpha_composite(p,tint(base,walk,(53,148,177),81))
        elif name=='lantern_field':p=tint(base,walk,(233,196,161),89);p=Image.alpha_composite(p,tint(base,ground,(42,82,111),106))
        else:p=tint(base,walk,(207,164,112),84);p=Image.alpha_composite(p,tint(base,ground,(64,122,76),95))
        layers={'00_art_direction':p,
                '01_surface_materials':material_layer(name,base,walk,ground),
                '02_environment_landmarks':focal_layer(name,size,walk,ground),
                '03_path_edges_and_reflections':boundary_layer(name,base,walk,ground),
                '04_local_light':atmosphere(name,size)}
        final=base
        dest=LAYERS/name;dest.mkdir(parents=True,exist_ok=True)
        for k,lay in layers.items():
            lay.save(dest/(k+'.png'),optimize=True)
            final=Image.alpha_composite(final,lay)
        meta=PngImagePlugin.PngInfo();meta.add_text('visual_overhaul_v32','repaint-v32')
        meta.add_text('world_art_pass','v3.5-stage3')
        meta.add_text('visual_source','v3.4-stage2; 5 layers in art_source/world_stage3')
        target=A/'maps'/(name+'.png');final.save(target,optimize=True,pnginfo=meta)
        changed=int(np.count_nonzero(np.any(np.asarray(final)!=np.asarray(base),axis=2)))
        entries.append({'name':name,'dimensions':list(size),'layers':list(layers),'modified_pixels':changed,'sha256':sha(target)})
        print('MAP',name,changed,'pixels')
    for name in PROPS:
        before=original('props',name);new=prop_details(name,before);target=A/'props'/(name+'.png')
        new.save(target,optimize=True)
        changed=int(np.count_nonzero(np.any(np.asarray(new)!=np.asarray(before),axis=2)))
        props.append({'name':name,'dimensions':list(before.size),'modified_pixels':changed,'sha256':sha(target)})
    manifest={'version':'3.5.0','source':'3.4.0','maps':entries,'props':props,'purpose':'Fantasy forest stage3, visual changes only; all map/collision/story/save/audio untouched'}
    ART.mkdir(parents=True,exist_ok=True)
    (ART/'stage3_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print('STAGE 3 OK:',len(entries),'maps',len(props),'props',sum(x['modified_pixels'] for x in entries),'map pixels changed')
if __name__=='__main__':main()
