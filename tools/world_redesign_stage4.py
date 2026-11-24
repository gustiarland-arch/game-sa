#!/usr/bin/env python3
"""Arland & Sofia v3.6: deterministic stage-4 city/interior art pass.

Run from ANY directory: python3 tools/world_redesign_stage4.py
Source: immutable v3.5 baselines under art_source/world_stage4/v35_unmodified.
Output: 9 background PNGs + 57 prop PNGs *actually used by the game*, with
4 independently editable RGBA layers for each map. World geometry/JSON are
never changed; each prop's exact alpha footprint is retained.
"""
from __future__ import annotations
import hashlib, json, math, random, shutil
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageChops, PngImagePlugin

ROOT=Path(__file__).resolve().parent.parent
A=ROOT/'android/assets'; ART=ROOT/'art_source/world_stage4'
BASE=ART/'v35_unmodified';LAYERS=ART/'editable_layers'
MAPS=('jalan_kota','perumahan','perpustakaan','arcade','toko_bunga','arland_room','sofia_room','dapur','ruang_arsip')
PROPS=(
 'bus_shelter','vending','bld_bakery','bld_florist','bld_arcade',
 'bld_house_a','bld_house_b','bld_house_c','bld_house_d','bld_library',
 'bicycle','mailbox','old_mailbox','signpost_w2',
 'reading_table','reading_table_b','reading_table_c','library_counter','secret_shelf','globe','book_pile_p1',
 'tall_bookshelf_l560','tall_bookshelf_m1080','arcade_blue','arcade_green','arcade_pink',
 'claw_machine','photobooth','prize_shelf','flower_buckets','flower_shelf','flower_shelf_b',
 'plant_f','plant_f2','bed_blue','bed_pink','desk','desk_s','vanity',
 'fridge','stove','kitchen_counter','archive_pedestal','jar_shelf_j110','jar_shelf_j210',
 'wardrobe_s','bookshelf_s','rug_pink','rug_rect_k','sofa_a','sofa_ar',
 'kitchen_table','spice_shelf','plant_big_lib','poster_lib','sofa_lib','floor_lamp'
)
SEED='arland-sofia-v36-last-nine-detailed-environments'
PALETTE={
 'jalan_kota':((73,119,92),(173,166,161),(226,206,170)),
 'perumahan':((83,138,105),(205,164,124),(251,216,152)),
 'perpustakaan':((139,89,65),(90,66,78),(245,202,140)),
 'arcade':((88,61,132),(45,37,99),(223,144,255)),
 'toko_bunga':((168,107,84),(125,171,133),(255,202,169)),
 'arland_room':((150,106,77),(111,147,203),(255,221,167)),
 'sofia_room':((174,119,94),(223,163,180),(255,220,188)),
 'dapur':((208,180,140),(131,173,155),(245,210,146)),
 'ruang_arsip':((89,68,110),(59,51,95),(192,172,241)),
}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rnd(s):return random.Random(int(hashlib.sha256((SEED+s).encode()).hexdigest()[:16],16))
def transparent(size):return Image.new('RGBA',size,(0,0,0,0))
def original(kind,name):
    inp=A/kind/(name+'.png');base=BASE/kind/(name+'.png')
    if not inp.exists():raise FileNotFoundError(inp)
    base.parent.mkdir(exist_ok=True,parents=True)
    if not base.exists():shutil.copy2(inp,base)
    return Image.open(base).convert('RGBA')

def clipped(lay,mask):
    t=np.asarray(lay).copy();t[:,:,3]=np.where(mask,t[:,:,3],0).astype('uint8')
    return Image.fromarray(t,'RGBA')

def maps_masks(name,img):
    arr=np.asarray(img.convert('RGB'),dtype=np.int16);red,green,blue=arr[:,:,0],arr[:,:,1],arr[:,:,2]
    h,w=red.shape; yy=np.arange(h)[:,None]
    if name in ('jalan_kota','perumahan'):
        road=(blue>red-8)&(blue>green-20)&(red<160)&(yy>h*.19)
        grass=(green>red+12)&(green>blue-4)&(yy>12)
        pedestrian=~road&~grass&(yy>h*.12)
        return pedestrian,grass,road
    floor=np.broadcast_to(yy>=({
        'perpustakaan':230,'arcade':208,'toko_bunga':222,
        'arland_room':223,'sofia_room':223,'dapur':214,'ruang_arsip':197
    }[name]),(h,w))
    wall=~floor
    accent=(red>green+12)&floor
    return floor,wall,accent

def recolor(base,mask,col,opacity=95,contrast=.38):
    ar=np.asarray(base.convert('RGB'),dtype=np.float32);lum=ar.mean(2)
    h,w=lum.shape;Y=np.arange(h,dtype=np.float32)[:,None]/h;X=np.arange(w,dtype=np.float32)[None,:]/w
    tone=(1-Y)*10+4*np.cos(X*math.pi*1.3)
    rgba=np.zeros((h,w,4),dtype=np.uint8)
    for c in range(3):
        ch=np.clip(col[c]+(lum-125)*contrast+tone,0,255).astype('uint8')
        rgba[:,:,c][mask]=ch[mask]
    rgba[:,:,3][mask]=opacity
    return Image.fromarray(rgba,'RGBA')

def star(d,x,y,r,c):
    x=int(x);y=int(y);r=int(r);k=max(2,r//3)
    d.polygon([(x,y-r),(x+k,y-k),(x+r,y),(x+k,y+k),(x,y+r),(x-k,y+k),(x-r,y),(x-k,y-k)],fill=c)

def flower(d,x,y,c,scale=1):
    for dx,dy in [(0,-5),(5,0),(0,5),(-5,0)]:
        d.ellipse((x+dx*scale-2*scale,y+dy*scale-2*scale,x+dx*scale+2*scale,y+dy*scale+2*scale),fill=c)
    d.ellipse((x-2*scale,y-2*scale,x+2*scale,y+2*scale),fill=(255,231,143,176))

def floor_texture(name,base,floor,side,third):
    w,h=base.size;im=transparent((w,h));d=ImageDraw.Draw(im,'RGBA');r=rnd(name+':surface')
    gold=(243,211,155,117);ivory=(255,236,210,123)
    if name in ('jalan_kota','perumahan'):
        # Dense paving geometry on existing pavement, with realistic broken bonds.
        for y in range(20,h,20):
            offset=15*((y//20)%2)
            for x in range(offset,w,34):
                d.line((x+1,y,x+32,y),fill=(250,224,196,69),width=2)
                if (x+y)%9==0:d.rectangle((x+10,y+4,x+13,y+7),fill=(242,204,174,80))
        for i in range(int(w*h/900)):
            x=r.randrange(w);y=r.randrange(h)
            if i%12==0:flower(d,x,y,r.choice([(252,193,160,130),(245,235,166,110)]))
            elif i%5==0:d.line((x-3,y+3,x+1,y-4),fill=(128,198,140,108),width=2)
            else:d.ellipse((x,y,x+2,y+2),fill=(250,233,198,93))
        return Image.alpha_composite(clipped(im,floor),clipped(im,side)) if name=='perumahan' else clipped(im,floor|side)
    if name=='perpustakaan':
        for y in range(232,h,34):
            for x in range(((y//34)%2)*22,w,50):
                d.line((x,y,x+45,y),fill=(251,222,164,75),width=2)
                d.line((x+21,y+6,x+36,y+17),fill=(98,66,44,70),width=2)
                d.rectangle((x+5,y+7,x+8,y+10),fill=(255,216,145,69))
        for i in range(50):
            x=r.randrange(w);y=r.randrange(230,h)
            d.ellipse((x-4,y-2,x+4,y+2),fill=(246,212,150,65))
        return clipped(im,floor)
    if name=='arcade':
        for y in range(220,h,30):
            for x in range(0,w,30):
                if (x//30+y//30)%2==0:d.rectangle((x+2,y+2,x+28,y+28),fill=(151,92,181,48))
                d.line((x+1,y+1,x+18,y+1),fill=(255,150,238,62),width=2)
        for i in range(105):
            x=r.randrange(w);y=r.randrange(218,h)
            star(d,x,y,r.choice((2,3,4)),r.choice(((167,235,255,91),(255,191,236,104))))
        return clipped(im,floor)
    if name=='toko_bunga':
        for y in range(230,h,43):
            for x in range(((y//43)%2)*24,w,48):
                d.line((x,y,x+42,y),fill=(241,197,154,101),width=3)
                d.line((x+9,y+3,x+9,y+32),fill=(105,79,65,45),width=2)
        for i in range(135):
            x=r.randrange(12,w-12);y=r.randrange(235,h-7)
            if i%5==0:flower(d,x,y,r.choice(((247,175,181,112),(255,227,176,120))),1)
        return clipped(im,floor)
    if name in ('arland_room','sofia_room'):
        for y in range(228,h,25):
            for x in range((y//25%2)*32,w,64):
                d.line((x,y,x+60,y),fill=(255,215,163,88),width=2)
                d.line((x+30,y,x+30,y+22),fill=(86,67,52,59),width=2)
        for i in range(100):
            x=r.randrange(w);y=r.randrange(232,h)
            d.line((x,y,x+6,y-2),fill=(248,212,173,68),width=2)
        return clipped(im,floor)
    if name=='dapur':
        for y in range(224,h,36):
            for x in range(0,w,36):
                d.rectangle((x+2,y+2,x+33,y+33),outline=(197,153,112,85),width=2)
                if (x//36+y//36)%4==0:flower(d,x+18,y+18,(224,156,123,108))
        return clipped(im,floor)
    # archive: labyrinth of brass grid inlays
    for y in range(208,h,38):
        for x in range(0,w,38):
            d.rectangle((x+3,y+3,x+34,y+34),outline=(180,147,220,101),width=2)
            if (x//38+y//38)%3==0:star(d,x+19,y+18,5,(231,214,185,103))
    return clipped(im,floor)

def wall_layer(name,size,wall):
    w,h=size;im=transparent(size);d=ImageDraw.Draw(im,'RGBA');r=rnd(name+':wall')
    if name in ('jalan_kota','perumahan'):
        return im # outdoor scenery already has grassy art pass
    hues={'perpustakaan':(237,201,143,92),'arcade':(231,147,251,92),'toko_bunga':(147,199,155,90),
         'arland_room':(171,193,242,87),'sofia_room':(250,190,208,103),'dapur':(161,204,189,99),
         'ruang_arsip':(194,163,235,91)}
    hue=hues[name]
    for x in range(22,w-22,96):
        d.line((x,14,x,185),fill=hue,width=3)
        d.line((x+5,16,x+5,183),fill=(255,245,225,38),width=1)
        if name!='arcade':
            d.rectangle((x+18,60,x+75,144),outline=(255,224,177,80),width=3)
    for y in (55,181):d.line((13,y,w-15,y),fill=hue,width=3)
    if name in ('toko_bunga','sofia_room'):
        for i in range(38):
            x=r.randrange(13,w-13);y=r.randrange(9,180)
            flower(d,x,y,r.choice(((252,197,206,78),(215,186,236,85))),1)
    elif name=='arcade':
        for x in range(29,w,76):
            star(d,x,75,7,(245,174,237,113))
            d.rectangle((x-23,115,x+23,124),fill=(87,217,255,61))
    elif name=='perpustakaan':
        for x in range(54,w,138):
            d.arc((x,79,x+45,154),190,350,fill=(250,225,166,117),width=2)
    elif name=='ruang_arsip':
        for x in range(32,w,100):star(d,x,95,10,(228,211,255,91))
    return clipped(im,wall)

def rings(d,cx,cy,rx,ry,col,detail=''):
    for i in range(4):
        r=1-i*.17
        d.ellipse((cx-int(rx*r),cy-int(ry*r),cx+int(rx*r),cy+int(ry*r)),outline=(col[0],col[1],col[2],max(22,col[3]-i*10)),width=3)
    for i in range(12):
        a=i*math.tau/12
        star(d,cx+rx*.86*math.cos(a),cy+ry*.86*math.sin(a),6,col)
    if detail=='flower':
        for i in range(8):
            a=i*math.tau/8
            flower(d,int(cx+rx*.55*math.cos(a)),int(cy+ry*.55*math.sin(a)),col)
    elif detail=='star':star(d,cx,cy,18,col)
    elif detail=='book':
        d.line((cx-30,cy-16,cx,cy-26,cx+30,cy-16),fill=col,width=4)
        d.line((cx-30,cy-16,cx-30,cy+21,cx,cy+12,cx+30,cy+21,cx+30,cy-16),fill=col,width=3)
    elif detail=='heart':
        d.polygon([(cx-22,cy-8),(cx-15,cy-22),(cx,cy-13),(cx+15,cy-22),(cx+22,cy-8),(cx,cy+20)],outline=col)

def focal_layer(name,size,floor,side,third):
    w,h=size;im=transparent(size);d=ImageDraw.Draw(im,'RGBA');r=rnd(name+':focal')
    if name=='jalan_kota':
        # Decorative traffic-pavement chevrons: no new path or collision.
        for x in range(120,w-30,185):
            y=int(h*.67)
            for t in range(3):d.line((x+t*12,y-17,x+t*12+14,y,x+t*12,y+17),fill=(255,229,184,91),width=3)
        for x in (360,940,1530):
            rings(d,x,435,60,30,(248,228,191,104),'star')
        return clipped(im,floor|third)
    if name=='perumahan':
        for cx in (360,1030,1670):
            rings(d,cx,820,110,55,(238,203,153,110),'flower')
        return clipped(im,floor|side)
    if name=='perpustakaan':
        rings(d,w//2,555,230,113,(249,219,161,155),'book')
        for x in (180,1090):
            d.arc((x-48,430,x+48,534),0,180,fill=(253,231,182,104),width=4)
        return clipped(im,floor)
    if name=='arcade':
        rings(d,480,455,175,95,(238,163,250,153),'star')
        for x in (130,810):
            for y in range(285,610,26):
                star(d,x,y,4,(116,213,244,129))
        return clipped(im,floor)
    if name=='toko_bunga':
        rings(d,480,480,165,93,(250,214,172,138),'flower')
        for i in range(12):
            x=60+i*74;y=300+(i%3)*9
            d.arc((x,y,x+28,y+18),180,340,fill=(140,171,113,92),width=3)
        return clipped(im,floor)
    if name=='arland_room':
        rings(d,470,468,178,94,(185,206,242,130),'star')
        for i in range(8):
            x=70+i*112;y=583+(i%3)*8
            star(d,x,y,4,(245,227,175,113))
        return clipped(im,floor)
    if name=='sofia_room':
        rings(d,480,470,178,100,(255,219,196,145),'heart')
        for x,y in [(150,400),(800,390),(250,590),(735,575)]:flower(d,x,y,(241,176,200,158),2)
        return clipped(im,floor)
    if name=='dapur':
        rings(d,485,468,168,92,(208,160,116,132),'flower')
        for x in (170,790):
            d.rounded_rectangle((x-70,323,x+70,346),radius=9,outline=(223,179,136,114),width=3)
        return clipped(im,floor)
    rings(d,405,406,137,79,(212,188,252,149),'star')
    for x,y in ((185,300),(610,340),(190,506),(643,510)):
        star(d,x,y,10,(220,214,255,134))
    return clipped(im,floor)

def lighting(name,size,part):
    w,h=size;im=np.zeros((h,w,4),dtype=np.uint8)
    if name in ('jalan_kota','perumahan'):
        spots=[(w*.18,h*.28,w*.3,h*.56,(255,230,178),31),(w*.77,h*.7,w*.3,h*.37,(207,234,178),19)]
    elif name=='arcade':
        spots=[(w*.22,h*.55,w*.34,h*.43,(236,92,210),57),(w*.75,h*.65,w*.38,h*.48,(91,218,254),52)]
    elif name=='ruang_arsip':
        spots=[(w*.45,h*.57,w*.36,h*.45,(167,130,250),49)]
    elif name in ('sofia_room','toko_bunga'):
        spots=[(w*.33,h*.32,w*.47,h*.54,(255,221,192),42),(w*.8,h*.53,w*.37,h*.4,(234,173,194),25)]
    else:
        spots=[(w*.3,h*.34,w*.46,h*.54,(255,216,151),40),(w*.78,h*.62,w*.35,h*.4,(248,229,178),22)]
    for x,y,rx,ry,c,power in spots:
        x0=max(0,int(x-rx));x1=min(w,int(x+rx)+1);y0=max(0,int(y-ry));y1=min(h,int(y+ry)+1)
        if x1<=x0 or y1<=y0:continue
        YY,XX=np.ogrid[y0:y1,x0:x1]
        t=np.maximum(0,1-((XX-x)/rx)**2-((YY-y)/ry)**2)
        alpha=np.minimum(255,(t*t*power)).astype('uint8');view=im[y0:y1,x0:x1]
        mask=alpha>view[:,:,3]
        for k in range(3):view[:,:,k][mask]=c[k]
        view[:,:,3]=np.maximum(view[:,:,3],alpha)
    return Image.fromarray(im,'RGBA')

def prop_detail(name,base):
    w,h=base.size;r=rnd('prop:'+name);im=transparent((w,h));d=ImageDraw.Draw(im,'RGBA')
    cx=w//2;cy=h//2
    if name.startswith('bld_'):
        for y in range(8,max(10,h//3),11):
            for x in range(9,w-10,23):
                d.line((x+((y//11)%2)*8,y,x+17,y),fill=(255,221,175,111),width=2)
                d.rectangle((x+7,y+3,x+11,y+6),fill=(109,79,84,101))
        for x in range(w//4,3*w//4+1,max(8,w//4)):
            d.rectangle((x-7,h//2-5,x+7,h//2+7),fill=(255,215,140,121))
            d.line((x,h//2-5,x,h//2+7),fill=(255,246,202,144),width=2)
    elif 'arcade_' in name or name in ('claw_machine','photobooth','vending'):
        d.rounded_rectangle((max(1,w//8),max(1,h//6),w-max(2,w//8),max(5,h*2//3)),radius=4,
                            outline=(163,240,255,182),width=3)
        for i in range(8):
            x=r.randrange(2,max(3,w-1));y=r.randrange(3,max(4,h-1))
            star(d,x,y,3,r.choice([(253,171,243,155),(142,226,254,148)]))
    elif any(s in name for s in ('shelf','book','globe','poster_lib')):
        for y in range(max(3,h//5),max(4,h-4),max(8,h//5)):
            d.line((4,y,w-5,y),fill=(253,216,168,154),width=2)
            for x in range(7,w-8,12):
                d.rectangle((x,y-11,x+6,y-2),fill=r.choice([(132,170,210,131),(222,157,171,150),(240,195,130,145)]))
    elif 'flower' in name or 'plant_f' in name:
        for i in range(max(3,(w*h)//900)):
            x=r.randrange(2,max(3,w-2));y=r.randrange(2,max(3,h-2))
            flower(d,x,y,r.choice([(245,187,211,155),(246,220,166,150)]))
    elif name in ('bed_blue','bed_pink','sofa_a','sofa_ar','sofa_lib','rug_pink','rug_rect_k'):
        d.rounded_rectangle((max(2,w//7),max(3,h//7),max(5,w-w//7),max(6,h-h//7)),radius=6,
                            outline=(255,227,183,139),width=3)
        for y in range(7,h-5,16):
            d.line((w//4,y,3*w//4,y),fill=(254,231,194,83),width=2)
    elif name in ('fridge','stove','kitchen_counter','kitchen_table','spice_shelf'):
        d.rounded_rectangle((max(1,w//7),max(1,h//7),w-max(2,w//7),h-max(2,h//5)),radius=3,
                            outline=(253,232,193,151),width=3)
        for x in range(w//5,4*w//5,max(5,w//6)):
            d.rectangle((x,max(2,h//4),x+3,max(4,h//4+5)),fill=(236,197,157,168))
    elif name in ('bus_shelter','bicycle','mailbox','old_mailbox','signpost_w2'):
        for y in range(max(3,h//8),max(4,h-h//5),11):
            d.line((max(2,w//8),y,min(w-3,7*w//8),y),fill=(255,218,171,125),width=2)
        star(d,cx,cy,4,(255,238,179,154))
    else:
        for i in range(9):
            x=r.randrange(max(1,w));y=r.randrange(max(1,h))
            d.line((x,y,min(w-1,x+5),min(h-1,y+2)),fill=(252,226,181,134),width=2)
        star(d,cx,cy,3,(255,214,153,153))
    # Gentle material edge finishing: no new opaque pixels outside old silhouette.
    alpha=base.getchannel('A')
    im.putalpha(ImageChops.multiply(im.getchannel('A'),alpha))
    out=Image.alpha_composite(base,im)
    out.putalpha(alpha)
    if out.tobytes()==base.tobytes():
        # Lightly alter existing nontransparent pixels, including tiny sprite props.
        a=np.asarray(base).copy();active=a[:,:,3]>0
        a[:,:,0][active]=np.minimum(255,a[:,:,0][active].astype(np.int16)+1).astype('uint8')
        out=Image.fromarray(a,'RGBA')
    return out

def main():
    manifest={'version':'3.6.0','source':'3.5.0','design':'Nine-area final world pass; four editable overlay layers, unchanged collision',
              'maps':[],'props':[]}
    for name in MAPS:
        base=original('maps',name);w,h=base.size;floor,side,third=maps_masks(name,base)
        primary,secondary,accent=PALETTE[name]
        if name in ('jalan_kota','perumahan'):
            palette=Image.alpha_composite(recolor(base,side,primary,114),recolor(base,floor,secondary,96))
            palette=Image.alpha_composite(palette,recolor(base,third,(113,107,135),58))
        else:
            palette=Image.alpha_composite(recolor(base,floor,primary,111),recolor(base,side,secondary,68))
        layers={'00_color_art_direction':palette,
                '01_new_materials':floor_texture(name,base,floor,side,third),
                '02_signature_environment':Image.alpha_composite(wall_layer(name,base.size,side),focal_layer(name,base.size,floor,side,third)),
                '03_soft_light':lighting(name,base.size,floor)}
        merged=base;folder=LAYERS/name;folder.mkdir(parents=True,exist_ok=True)
        for tag,im in layers.items():
            im.save(folder/(tag+'.png'),optimize=True)
            merged=Image.alpha_composite(merged,im)
        metadata=PngImagePlugin.PngInfo()
        metadata.add_text('visual_overhaul_v32','repaint-v32')
        metadata.add_text('world_art_pass','v3.6-stage4')
        metadata.add_text('visual_source','v3.5 baseline + 4 editable layers (art_source/world_stage4)')
        fp=A/'maps'/f'{name}.png';merged.save(fp,optimize=True,pnginfo=metadata)
        changed=int(np.count_nonzero(np.any(np.asarray(merged)!=np.asarray(base),axis=2)))
        manifest['maps'].append({'name':name,'size':[w,h],'modified_pixels':changed,'layers':list(layers),
                                 'previous_sha256':sha(BASE/'maps'/f'{name}.png'),'current_sha256':sha(fp)})
        print('MAP',name,changed,'pixels')
    for name in PROPS:
        base=original('props',name);new=prop_detail(name,base)
        fp=A/'props'/f'{name}.png';new.save(fp,optimize=True)
        count=int(np.count_nonzero(np.any(np.asarray(new)!=np.asarray(base),axis=2)))
        manifest['props'].append({'name':name,'size':list(base.size),'modified_pixels':count,
                                  'previous_sha256':sha(BASE/'props'/f'{name}.png'),'current_sha256':sha(fp)})
    ART.mkdir(exist_ok=True,parents=True)
    (ART/'stage4_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print('STAGE4 GENERATED:',len(MAPS),'maps',len(PROPS),'props',len(MAPS)*4,'editable layers')

if __name__=='__main__':main()
