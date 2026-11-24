#!/usr/bin/env python3
"""Arland & Sofia v3.4 — Romantic & Fantasy World Redesign, stage 2.

Editable, reproducible art pass over the untouched v3.3 runtime maps/props:
* 5 distinctive watercolor-pixel-art environment palettes
* masked water reflections, shoreline edges, path inlays, star diagrams
* artifact-specific wood/metal/flower/luminescent details for scene props
* preserve map dimensions, coordinate space, transparent prop alpha

Run in project root: python3 tools/world_redesign_stage2.py
Requires Pillow and NumPy, but no remote downloads.
"""
import hashlib, json, math, random, shutil
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageChops, PngImagePlugin

ROOT = Path(__file__).resolve().parent.parent
ASSET = ROOT/'android/assets'
ART = ROOT/'art_source/world_stage2'
BASE = ART/'v33_unmodified'
LAYERS = ART/'editable_layers'
MAPS = ('riverside', 'dermaga', 'bukit_bintang', 'memory_garden', 'eternal_garden')
PROPS = (
    'bridge_pier','bridge_dpier','bridge_dplat','pier_post','rowboat','rowboat_b',
    'rowboat_rv','fishing_hut','fence_bb','observatory','telescope','chest_bb',
    'stone_lantern_bb','stone_lantern_bb2','tree_dream','tree_lantern','crystal',
    'pedestal_book','arch_flowers','arch_flowers_e','arch_flowers_e2',
    'wishing_tree','gazebo_e','stone_bench','lantern_post','signpost_w3',
    'tree_oak','rock','mushrooms','bush_d',
)
# Props from stage 1 (lamp/bench/tree_cherry etc.) deliberately untouched.
SEED = 'arlandsofia-stage2-2026'


def rnd(key):
    n = int(hashlib.sha256((SEED+':'+key).encode()).hexdigest()[:16],16)
    return random.Random(n)


def original(kind, name):
    source = ASSET/kind/(name+'.png')
    dest = BASE/kind/(name+'.png')
    dest.parent.mkdir(parents=True,exist_ok=True)
    if not dest.exists():shutil.copy2(source,dest)
    return Image.open(dest).convert('RGBA')


def rgba(w,h):return Image.new('RGBA',(w,h),(0,0,0,0))


def masks_for(name,img):
    a=np.asarray(img.convert('RGB')).astype(np.int16)
    r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
    water=(b>g+12)&(g>r+10)&(b>100)
    plants=(g>r+13)&(g>b+2)&(g>72)
    path=(r>g+4)&(g>b+9)&(r>116)&(b>60)
    fantasy=(b>r+10)&(r>g+1)&(b>89)
    pale=(r>158)&(b>134)&(g>140)&(np.abs(r-b)<42)
    return {'water':water,'plants':plants,'path':path,'fantasy':fantasy,'pale':pale}


def paletted(img,mask,target,alpha=190,contrast=.28,temper=0):
    ar=np.asarray(img.convert('RGB'),dtype=np.float32)
    ref=np.sum(ar,axis=2)/3
    h,w=ref.shape
    x=np.arange(w,dtype=np.float32)[None,:]/w
    y=np.arange(h,dtype=np.float32)[:,None]/h
    lighting=(1-y)*7+np.cos(x*3.2)*5+temper
    out=np.zeros((h,w,4),dtype=np.uint8)
    for k,c in enumerate(target):
        val=np.clip(c+(ref-135)*contrast+lighting,0,255)
        out[:,:,k][mask]=val[mask].astype(np.uint8)
    out[:,:,3][mask]=alpha
    return Image.fromarray(out,'RGBA')


def clip_layer(layer,mask):
    ar=np.asarray(layer).copy()
    ar[:,:,3]=np.where(mask,ar[:,:,3],0)
    return Image.fromarray(ar,'RGBA')


def lights(w,h,spots):
    """One array, several broad quantized focal glows, near-zero per-pixel heap allocation."""
    result=np.zeros((h,w,4),dtype=np.uint8)
    for cx,cy,rx,ry,color,power in spots:
        x0=max(0,int(cx-rx));x1=min(w,int(cx+rx+1))
        y0=max(0,int(cy-ry));y1=min(h,int(cy+ry+1))
        if x0>=x1 or y0>=y1:continue
        yy,xx=np.ogrid[y0:y1,x0:x1]
        dist=((xx-cx)/rx)**2+((yy-cy)/ry)**2
        alpha=(np.maximum(0,1-dist)**2*power).astype(np.uint8)
        view=result[y0:y1,x0:x1]
        replace=alpha>view[:,:,3]
        for c in range(3):view[:,:,c][replace]=color[c]
        view[:,:,3]=np.maximum(view[:,:,3],alpha)
    return Image.fromarray(result,'RGBA')


def grass_texture(w,h,mask,name):
    layer=rgba(w,h);d=ImageDraw.Draw(layer,'RGBA');r=rnd(name+':ground')
    palette = {'riverside':((232,166,192,167),(250,228,179,164),(126,197,166,160)),
      'dermaga':((241,204,152,171),(185,220,178,148),(252,163,161,159)),
      'bukit_bintang':((217,209,254,164),(242,211,170,164),(170,209,227,165)),
      'memory_garden':((241,197,255,164),(255,229,244,168),(165,214,255,147)),
      'eternal_garden':((255,235,224,175),(234,183,236,158),(243,231,160,164))}[name]
    amount=int(w*h/3400)
    for i in range(amount):
        x=r.randrange(12,w-15);y=r.randrange(12,h-15)
        if i%7==0:
            # Delicate asters grouped in a small ring, not uniformly distributed confetti.
            for j in range(4):
                dx,dy=((0,-7),(7,0),(0,7),(-7,0))[j]
                c=palette[(i+j)%len(palette)]
                d.rectangle((x+dx-2,y+dy-2,x+dx+3,y+dy+3),fill=c)
            d.rectangle((x-2,y-2,x+2,y+2),fill=(255,241,183,178))
        elif i%5==0:
            c=palette[i%3]
            d.line((x,y+6,x+2,y-5),fill=(50,99,71,120),width=2)
            d.polygon([(x-3,y-5),(x+1,y-10),(x+5,y-5),(x+1,y-2)],fill=c)
        else:
            d.line((x,y+3,x-2,y-4),fill=(43,93,73,77),width=2)
            d.line((x+4,y+3,x+5,y-1),fill=(188,224,154,85),width=2)
    return clip_layer(layer,mask)


def water_texture(w,h,mask,name):
    layer=rgba(w,h);d=ImageDraw.Draw(layer,'RGBA');r=rnd(name+':water')
    dark=(49,82,132,112);bright=(206,243,234,136)
    for i in range(int(w*h/3100)):
        x=r.randrange(15,w-15);y=r.randrange(15,h-15)
        if i%9==0:
            d.arc((x-25,y-8,x+25,y+10),15,155,fill=bright,width=2)
            d.arc((x-14,y-2,x+15,y+8),24,147,fill=(222,252,249,82),width=2)
        elif i%7==0:
            # Two-tone dappled reflections pixel stepped.
            d.rectangle((x,y,x+20,y+2),fill=(232,255,248,113))
            d.rectangle((x+8,y+6,x+30,y+7),fill=(96,190,201,91))
        else:
            length=r.randrange(9,35)
            d.line((x,y,x+length,y),fill=bright if i%3 else dark,width=2)
            if i%4==0:d.line((x+7,y+5,x+length-3,y+5),fill=(229,255,242,74),width=2)
    if name in ('riverside','dermaga'):
        # Water reflection bands near pier and riverside landmarks; no new collision.
        for i in range(34):
            x=960+r.randrange(-420,420);y=int(h*.66)+r.randrange(-40,260)
            d.line((x,y,x+r.randrange(13,48),y),fill=(255,217,165,86),width=3)
    else:
        for i in range(65):
            x=r.randrange(20,w-20);y=r.randrange(20,h-20)
            d.rectangle((x-2,y-5,x+2,y+5),fill=(244,223,255,83))
            d.rectangle((x-5,y-2,x+5,y+2),fill=(244,223,255,83))
    return clip_layer(layer,mask)


def shoreline(w,h,mask):
    # Pixel-wide water/land interface, rendered as material boundary. Static art only.
    edge=mask & (~np.roll(mask,5,axis=0) | ~np.roll(mask,-5,axis=0))
    edge[:5,:]=False;edge[-5:,:]=False
    a=np.zeros((h,w,4),dtype=np.uint8)
    a[:,:,0][edge]=211;a[:,:,1][edge]=240;a[:,:,2][edge]=226;a[:,:,3][edge]=82
    return Image.fromarray(a,'RGBA')


def landmark_riverside(w,h):
    im=rgba(w,h);d=ImageDraw.Draw(im,'RGBA')
    # Low-profile wooden boardwalk footnote and shoreline runic medallions.
    for x,y in [(860,424),(1515,442),(1095,449)]:
        d.ellipse((x-48,y-25,x+48,y+25),outline=(231,208,153,120),width=4)
        d.ellipse((x-40,y-20,x+40,y+20),outline=(94,144,130,115),width=2)
        d.polygon([(x,y-16),(x+9,y),(x,y+16),(x-9,y)],outline=(246,227,182,127))
    for x in range(310,1640,74):
        # Reeds/shoreline art only in a narrow bank band.
        d.arc((x,702,x+68,724),0,180,fill=(209,238,208,107),width=3)
        d.line((x+24,690,x+27,676),fill=(125,180,139,111),width=2)
    return im


def landmark_dermaga(w,h):
    im=rgba(w,h);d=ImageDraw.Draw(im,'RGBA')
    # Nautical decorative compass on the LAND above the jetty, all lines are flat texture.
    cx,cy=957,316
    d.ellipse((cx-92,cy-54,cx+92,cy+54),outline=(245,217,154,115),width=4)
    d.ellipse((cx-69,cy-42,cx+69,cy+42),outline=(63,131,121,128),width=2)
    for t in range(0,360,45):
        a=math.radians(t)
        d.line((cx+math.cos(a)*12,cy+math.sin(a)*7,cx+math.cos(a)*75,cy+math.sin(a)*44),fill=(248,227,183,129),width=3)
    d.polygon([(cx,cy-36),(cx+8,cy),(cx,cy+36),(cx-8,cy)],fill=(223,177,117,95))
    for x in (430,730,1210,1590):
        d.arc((x-43,421,x+43,442),4,173,fill=(244,229,183,103),width=3)
    return im


def landmark_bukit(w,h):
    im=rgba(w,h);d=ImageDraw.Draw(im,'RGBA')
    # Star-map engravings beside the observatory; faint orbital paths are ground art.
    cx,cy=1590,520
    for rx,ry in [(152,88),(118,65),(72,42)]:d.ellipse((cx-rx,cy-ry,cx+rx,cy+ry),outline=(237,227,181,99),width=3)
    stars=[(cx-108,cy+34),(cx-38,cy-28),(cx+28,cy+7),(cx+90,cy-33),(cx+119,cy+27)]
    d.line(stars,fill=(251,231,181,131),width=3)
    for x,y in stars:
        d.line((x-6,y,x+6,y),fill=(251,248,211,174),width=2)
        d.line((x,y-6,x,y+6),fill=(251,248,211,174),width=2)
    # Low-level lighting at edges of the observatory path (no prop footprints changed).
    for x in (660,850,1050,1230,1420):
        for dy in (-1,1):
            y=735+dy*40
            d.polygon([(x,y-7),(x+7,y),(x,y+7),(x-7,y)],fill=(243,204,164,100))
    return im


def landmark_memory(w,h):
    im=rgba(w,h);d=ImageDraw.Draw(im,'RGBA')
    cx,cy=w//2,h//2
    # Four concentric sacred rings reinforcing established cross-shaped memory path.
    for rad in (91,125,155):
        d.ellipse((cx-rad,cy-rad*.7,cx+rad,cy+rad*.7),outline=(244,222,255,115),width=3)
    for i in range(16):
        a=i*2*math.pi/16;x=cx+int(174*math.cos(a));y=cy+int(120*math.sin(a))
        d.polygon([(x,y-7),(x+6,y),(x,y+7),(x-6,y)],fill=(231,205,255,117))
    for x,y in [(390,600),(1200,600),(800,235),(800,974)]:
        d.ellipse((x-43,y-25,x+43,y+25),outline=(254,234,248,146),width=3)
        d.polygon([(x,y-18),(x+11,y),(x,y+18),(x-11,y)],fill=(253,219,230,67),outline=(252,244,251,124))
    return im


def landmark_eternal(w,h):
    im=rgba(w,h);d=ImageDraw.Draw(im,'RGBA');r=rnd('eternal:motifs')
    for cx,cy,rad in [(960,340,176),(960,600,95),(960,1020,126)]:
        for rr in (rad,rad-22):
            d.ellipse((cx-rr,cy-rr*.46,cx+rr,cy+rr*.46),outline=(251,232,244,129),width=4)
        for i in range(12):
            a=i*math.pi/6;x=int(cx+rad*.81*math.cos(a));y=int(cy+rad*.35*math.sin(a))
            d.ellipse((x-5,y-5,x+5,y+5),fill=(244,173,190,144))
            d.rectangle((x-2,y-2,x+2,y+2),fill=(255,235,169,142))
    for _ in range(38):
        x=r.randrange(230,1700);y=r.randrange(220,1270)
        d.arc((x-25,y-12,x+25,y+12),195,340,fill=(244,237,211,70),width=2)
    return im


def map_layers(name,img):
    w,h=img.size; m=masks_for(name,img)
    palette=rgba(w,h)
    specs={
      'riverside': [('plants',(80,144,99),175),('water',(43,133,169),214),('path',(210,171,130),130)],
      'dermaga': [('plants',(82,135,103),185),('water',(39,113,157),222),('path',(203,165,123),155)],
      'bukit_bintang': [('plants',(74,115,105),207),('path',(172,150,130),161)],
      'memory_garden': [('fantasy',(127,101,177),175),('pale',(229,199,238),120)],
      'eternal_garden': [('plants',(108,172,144),153),('water',(63,140,194),183)],
    }[name]
    for key,col,a in specs:palette=Image.alpha_composite(palette,paletted(img,m[key],col,a))
    material=rgba(w,h)
    if name in ('riverside','dermaga','eternal_garden'):
        material=Image.alpha_composite(material,water_texture(w,h,m['water'],name))
        material=Image.alpha_composite(material,shoreline(w,h,m['water']))
    material=Image.alpha_composite(material,grass_texture(w,h,m['plants'] if name!='memory_garden' else m['fantasy'],name))
    landmark={'riverside':landmark_riverside,'dermaga':landmark_dermaga,
              'bukit_bintang':landmark_bukit,'memory_garden':landmark_memory,
              'eternal_garden':landmark_eternal}[name](w,h)
    glow_spec={
     'riverside':[(1215,744,355,245,(250,205,141),34),(915,420,335,225,(255,230,180),37)],
     'dermaga':[(970,690,345,285,(250,186,131),46),(950,330,360,205,(255,223,158),27)],
     'bukit_bintang':[(1510,520,365,285,(237,205,175),41),(970,690,295,195,(255,220,182),26)],
     'memory_garden':[(800,592,440,355,(244,193,248),48),(800,170,460,190,(208,177,255),32)],
     'eternal_garden':[(960,336,470,320,(255,221,213),46),(945,1060,440,330,(224,207,255),29)],
    }[name]
    glow=lights(w,h,glow_spec)
    return {'00_ground_palette':palette,'01_water_and_garden':material,
            '02_landmark_details':landmark,'03_atmosphere':glow}


def clipped_prop(base,over):
    before=base.getchannel('A')
    over.putalpha(ImageChops.multiply(over.getchannel('A'),before))
    result=Image.alpha_composite(base,over)
    result.putalpha(before)
    return result


def prop_detail(name,base):
    w,h=base.size;r=rnd('prop:'+name)
    layer=rgba(w,h);d=ImageDraw.Draw(layer,'RGBA')
    if name.startswith('bridge_'):
        # Every plank individually lit; joins, iron bolts and warm wood texture.
        if 'dplat' in name or 'pier'==name.split('_')[-1] and name=='bridge_pier':
            step=18 if name=='bridge_dplat' else 17
            for x in range(6,w-6,step):
                d.line((x,5,x,h-6),fill=(80,57,60,123),width=3)
                d.line((x+4,7,x+4,h-8),fill=(252,217,161,86),width=2)
                for y in [max(8,h//5),h//2,max(10,h-20)]:
                    d.ellipse((x+8,y,x+11,y+3),fill=(82,62,59,139))
        else:
            for y in range(8,h-7,16):
                d.line((6,y,w-7,y),fill=(76,55,54,139),width=3)
                d.line((8,y+4,w-10,y+4),fill=(253,212,152,82),width=2)
                for x in (12,w-16):d.rectangle((x,y+7,x+3,y+10),fill=(70,57,53,161))
    elif name.startswith('rowboat'):
        for x in range(14,w-8,14):
            d.line((x,5,x-2,h-7),fill=(246,209,155,118),width=2)
            d.rectangle((x,h//2,x+3,h//2+3),fill=(78,59,55,162))
        d.line((6,h//2,w-8,h//2),fill=(255,240,192,96),width=2)
    elif name=='pier_post':
        d.line((2,3,w-4,3),fill=(246,207,157,157),width=2)
        for y in range(12,h-4,9):d.line((1,y,w-2,y+1),fill=(72,51,54,133),width=2)
    elif name=='fishing_hut':
        for y in range(8,51,12):
            for x in range(9,w-8,21):d.line((x,y,x+12,y),fill=(252,223,163,100),width=2)
        for x in range(11,w-8,20):d.line((x,63,x,99),fill=(86,58,53,78),width=2)
        for x in (28,94):d.rectangle((x,65,x+16,81),fill=(250,221,157,87))
    elif name=='observatory':
        cx=w//2
        for rx,ry in [(87,67),(71,53),(47,38)]:
            d.arc((cx-rx,5,cx+rx,5+2*ry),191,346,fill=(227,216,252,160),width=3)
        for x in (42,75,146,181):
            d.rectangle((x,124,x+12,149),outline=(147,120,171,130),width=2)
            d.line((x+2,128,x+9,128),fill=(238,228,253,140),width=2)
        d.line((30,163,w-31,163),fill=(186,149,195,138),width=4)
    elif name=='telescope':
        d.line((2,7,27,21),fill=(226,201,254,174),width=3)
        d.ellipse((0,5,8,13),outline=(249,232,252,156),width=2)
        d.line((20,30,31,45),fill=(144,123,202,114),width=2)
    elif name in ('stone_lantern_bb','stone_lantern_bb2','lantern_post'):
        cx=w//2
        for y in range(7,h-8,12):d.line((3,y,w-3,y),fill=(248,227,199,82),width=2)
        d.rectangle((cx-7,20,cx+7,28),fill=(255,217,132,178))
        d.rectangle((cx-4,21,cx+4,25),fill=(255,249,188,196))
    elif name in ('tree_dream','tree_lantern','wishing_tree','tree_oak'):
        n=60 if name=='wishing_tree' else 26
        roof=int(h*.65)
        for _ in range(n):
            x=r.randrange(max(3,w//12),max(5,w-w//12));y=r.randrange(7,max(8,roof))
            c=r.choice([(255,232,252,129),(216,199,255,141),(255,226,176,119)]) if name!='tree_oak' else r.choice([(205,243,178,131),(250,217,156,111),(97,170,124,93)])
            d.rectangle((x,y,x+r.randint(2,5),y+r.randint(2,4)),fill=c)
        for x in range(10,w-12,19):d.line((x,15,x+5,20),fill=(242,224,255,75),width=2)
    elif name.startswith('arch_flowers'):
        for i in range(28):
            a=math.pi+i*math.pi/27
            x=w/2+math.cos(a)*(w*.43);y=h*.52+math.sin(a)*(h*.45)
            d.ellipse((x-3,y-3,x+4,y+4),fill=r.choice([(255,211,229,158),(253,237,174,142),(220,212,255,155)]))
        for x in (7,w-8):d.line((x,60,x,112),fill=(241,232,225,104),width=3)
    elif name=='gazebo_e':
        for x in range(14,w-12,17):
            d.line((x,20,x+8,35),fill=(232,192,215,111),width=2)
            d.rectangle((x,140,x+3,144),fill=(205,171,187,119))
        d.line((8,148,w-8,148),fill=(253,229,224,155),width=4)
    elif name=='stone_bench':
        d.line((7,8,w-8,8),fill=(255,236,228,161),width=2)
        for x in range(10,w-10,12):d.rectangle((x,13,x+4,16),fill=(200,173,188,114))
    elif name in ('crystal','pedestal_book'):
        for y in range(8,h-8,9):
            d.line((w//2-3,y,w//2+1,y-4),fill=(246,240,254,135),width=2)
        d.line((w//3,12,w//3,h-12),fill=(255,219,250,109),width=2)
    elif name=='fence_bb':
        for y in (5,h//2,h-7):d.line((2,y,w-3,y),fill=(254,230,210,127),width=2)
    elif name=='signpost_w3':
        d.line((8,13,w-12,13),fill=(255,219,180,127),width=2)
        d.line((10,28,w-13,28),fill=(102,62,62,125),width=2)
    elif name=='chest_bb':
        d.line((3,9,w-4,9),fill=(255,231,159,158),width=2)
        d.rectangle((w//2-4,h//2-3,w//2+3,h//2+6),fill=(249,225,151,154))
    elif name in ('rock','mushrooms','bush_d'):
        for i in range(7):
            x=r.randrange(3,w-3);y=r.randrange(3,h-3)
            d.rectangle((x,y,x+2,y+2),fill=(232,221,250,133))
    return clipped_prop(base,layer)


def sha(file):return hashlib.sha256(file.read_bytes()).hexdigest()


def main():
    records=[];props=[]
    for name in MAPS:
        base=original('maps',name)
        layer_set=map_layers(name,base)
        dest=LAYERS/name;dest.mkdir(parents=True,exist_ok=True)
        done=base
        for label,layer in layer_set.items():
            layer.save(dest/(label+'.png'),optimize=True)
            done=Image.alpha_composite(done,layer)
        meta=PngImagePlugin.PngInfo();meta.add_text('visual_overhaul_v32','repaint-v32');meta.add_text('world_art_pass','v3.4-stage2')
        meta.add_text('visual_source','v3.3-stage1; 4 layers in art_source/world_stage2')
        target=ASSET/'maps'/(name+'.png');done.save(target,optimize=True,pnginfo=meta)
        changed=int(np.count_nonzero(np.any(np.asarray(base)!=np.asarray(done),axis=2)))
        records.append({'name':name,'size':list(base.size),'layers':list(layer_set),
                        'modified_pixels':changed,'file_sha256':sha(target)})
    for name in PROPS:
        base=original('props',name)
        final=prop_detail(name,base)
        target=ASSET/'props'/(name+'.png');final.save(target,optimize=True)
        props.append({'name':name,'size':list(base.size),
                      'alpha_preserved':base.getchannel('A').tobytes()==final.getchannel('A').tobytes(),
                      'file_sha256':sha(target)})
    manifest={'version':'v3.4.0-stage2','source':'v3.3.0',
              'maps':records,'props':props,'notes':'Art-only changes; maps.json/props.json/save/audio unchanged.'}
    (ART/'stage2_manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    print('STAGE2',len(records),'areas',len(props),'props',sum(m['modified_pixels'] for m in records),'map pixels modified')
    print({x['name']:x['modified_pixels'] for x in records})

if __name__=='__main__':main()
