"""v2.3 WORLD POLISH: enrich 22 existing tilemaps with deterministic hand-pixelled microdetails.

Run after tools/build_maps.py and BEFORE tools/build_content.py.  No map dimensions,
props, doors, spawn positions or collision JSON change.  Will not reapply twice to the
same PNG (tEXt metadata: world_polish_v23).  Reset/rebuild originals by running
`python3 tools/build_maps.py` first.  All visuals are local PNG, no downloaded art.
"""
from pathlib import Path
from PIL import Image, ImageDraw, PngImagePlugin
import hashlib, json, random, sys

ROOT = Path(__file__).resolve().parent.parent
ASSETS = Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'android'/'assets'
BASE = json.loads((ROOT/'tools'/'build'/'maps_base.json').read_text(encoding='utf-8'))
WORLD = {'plaza','jalan_kota','taman_kota','riverside','perumahan','dermaga','hutan_bisik','bukit_bintang'}
MAGIC = {'memory_garden','lantern_field','star_path','starfall_village','eternal_garden','ruang_arsip','gua_kristal'}
INDOOR = set(BASE) - WORLD - MAGIC
PAL = {
    'grass': ((116,161,93,255),(167,207,112,255),(240,202,167,255),(249,225,161,255)),
    'realm': ((196,147,213,255),(252,217,233,255),(255,233,157,255),(244,248,255,255)),
    'cave': ((105,126,183,255),(132,205,238,255),(216,233,255,255),(246,252,255,255)),
    'indoor': ((122,98,115,255),(170,139,142,255),(218,177,148,255),(247,220,179,255)),
}

# Minimal hand-authored motifs. Alpha/translucency is avoided to preserve crisp pixel edges.
def flower(d,x,y,p):
    d.point([(x-3,y),(x+3,y),(x,y-3),(x,y+3)],fill=p[1]); d.rectangle((x-1,y-1,x+1,y+1),fill=p[2]); d.point((x,y),fill=p[3]);
    d.point((x+1,y+5),fill=p[0])

def clover(d,x,y,p):
    for dx,dy in ((-3,-1),(2,-1),(-1,-4),(0,3)):
        d.rectangle((x+dx,y+dy,x+dx+2,y+dy+2),fill=p[0])
    d.rectangle((x,y,x+1,y+2),fill=p[1]); d.line((x,y+4,x+1,y+7),fill=p[0])

def stone(d,x,y,p):
    d.polygon([(x-4,y+1),(x-2,y-2),(x+4,y-2),(x+6,y+1),(x+3,y+3),(x-4,y+3)],fill=p[0]);
    d.line((x-2,y-1,x+2,y-1),fill=p[1]); d.point((x+4,y+1),fill=p[2])

def petals(d,x,y,p):
    d.polygon([(x,y-4),(x+4,y-1),(x+3,y+3),(x,y+5),(x-3,y+1)],fill=p[1]);
    d.point((x+1,y),fill=p[3]); d.point((x+9,y+5),fill=p[2]); d.point((x+11,y+3),fill=p[1])

def star(d,x,y,p):
    d.line((x-4,y,x+4,y),fill=p[1]); d.line((x,y-4,x,y+4),fill=p[3]);
    d.point((x-2,y-2),fill=p[2]); d.point((x+2,y+2),fill=p[2]);

def mark(d,x,y,p):
    d.line((x-6,y+2,x-2,y+2),fill=p[0]); d.point((x+2,y),fill=p[2]); d.point((x+7,y-1),fill=p[1]);

def blocked(m,x,y):
    for a,b in m.get('anchors',{}).values():
        if abs(a-x)<78 and abs(b-y)<68: return True
    sx,sy = m.get('spawn',[0,0]);
    if abs(x-sx)<90 and abs(y-sy)<78: return True
    for door in m.get('doors',[]):
        rx,ry,rw,rh=door['rect']
        if rx-35 < x < rx+rw+35 and ry-30 < y < ry+rh+30: return True
    return False

def ground_ok(rgb, theme, area):
    r,g,b=rgb[:3]
    if theme=='grass':
        return (g>r+8 and g>b+5 and 65<g<215) or (area in ('riverside','dermaga') and r>g and g>b+3 and 80<g<200)
    if theme=='realm':
        return 30<max(r,g,b)<230 and (b>r-50 or r>b-25)
    if theme=='cave':
        return 20<max(r,g,b)<180 and b>g-15 and b>=r
    return 45<max(r,g,b)<235 and min(r,g,b)>30

def build(area,m):
    fn=ASSETS/m['image']
    im=Image.open(fn).convert('RGBA')
    old=Image.open(fn)
    if old.info.get('world_polish_v23')=='1': return 0,'already polished'
    w,h=im.size
    assert (w,h)==(m['w'],m['h']), f'{area} changed dimensions'
    theme='grass' if area in WORLD else 'cave' if area=='gua_kristal' else 'realm' if area in MAGIC else 'indoor'
    pal=PAL[theme]
    d=ImageDraw.Draw(im)
    pix=im.load()
    # Equally stable between machines & Python processes; no global random state.
    seed=int.from_bytes(hashlib.sha256(('OLU-v23-'+area).encode()).digest()[:8],'big')
    rng=random.Random(seed)
    # Floor accents at measured density.  Fewer marks on tiled interior floors.
    target = int((w*h)/(4400 if theme in ('grass','realm') else 6400))
    count=0
    for _ in range(target*5):
        if count>=target: break
        x=rng.randrange(35,w-35); y=rng.randrange(35,h-35)
        if blocked(m,x,y) or not ground_ok(pix[x,y],theme,area): continue
        # Avoid strongly contrasting/stylized patterns through local colour consistency.
        a,b= pix[max(0,x-10),y][:3], pix[min(w-1,x+10),y][:3]
        if sum(abs(u-v) for u,v in zip(a,b))>110: continue
        p=rng.random()
        if theme=='grass':
            if p<0.40: flower(d,x,y,pal)
            elif p<0.70: clover(d,x,y,pal)
            elif p<0.88: petals(d,x,y,pal)
            else: stone(d,x,y,pal)
        elif theme=='realm':
            if p<0.38: petals(d,x,y,pal)
            elif p<0.80: star(d,x,y,pal)
            else: flower(d,x,y,pal)
        elif theme=='cave':
            if p<0.7: star(d,x,y,pal)
            else: stone(d,x,y,pal)
        else:
            if p<0.72: mark(d,x,y,pal)
            else: star(d,x,y,pal)
        count+=1
    assert count >= max(12, target//6), f'{area}: insufficient safe visual details {count}'
    info=PngImagePlugin.PngInfo(); info.add_text('world_polish_v23','1'); info.add_text('world_polish_area',area)
    im.save(fn, pnginfo=info, optimize=True)
    return count,theme

if __name__=='__main__':
    assert len(BASE)==22, 'Expected 22 preserved areas; review changed map list before polishing'
    total=0
    for name,m in BASE.items():
        n,kind=build(name,m); total+=n
        print(f'{name:19s} {n:4d} ground accents  [{kind}]')
    print(f'v2.3 world polish: {len(BASE)} maps, {total} new pixel-art details, no gameplay geometry edits')
