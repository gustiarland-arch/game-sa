#!/usr/bin/env python3
"""Generate editable original pixel-art terraces from tools/v50_terraces.json.
Only changes terrace metadata in maps.json; never regenerates old 29 maps or storyline.
Requires Pillow in the authoring environment (NOT required on Android runtime).
"""
import json,random,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
META=ROOT/'tools/v50_terraces.json'
ASSETS=ROOT/'android/assets'
PALETTES={
 'city': ('#bfa895','#e8d2b2','#8f796f','#5e5360','#f8e1b6'),
 'garden':('#b9a28c','#d8c6a4','#786a63','#514b51','#e9d9ab'),
 'wood':('#a87550','#d2a16f','#684a4f','#4c4146','#e6be83'),
 'cafe':('#a97772','#ead0b6','#705967','#503d43','#ffdcb8'),
 'star':('#8b85be','#c6bee8','#5e598a','#45446f','#e4dafa'),
 'memory':('#b8a3d7','#efdbfb','#756b9f','#504f78','#fff0cb'),
 'crystal':('#7191bb','#b4d5e8','#4b5f93','#334367','#c9ecff'),
 'forest':('#8aa479','#d0c69b','#566855','#3e594b','#d6e0b1'),
 'night':('#7d869e','#b8c4d4','#51566e','#343d59','#dfd3ff'),
 'future':('#a1a6b7','#e1d8d9','#69718f','#46465f','#fff1db'),
}

def color(s,alpha=255):return tuple(bytes.fromhex(s.lstrip('#')))+(alpha,)

def texture(area, spec):
    w=int(spec['w']);h=int(spec['h']);rise=int(spec['rise']);length=int(spec['stair']);
    # local top-left corresponds (area.x-20,area.y-40), map coordinates y-down
    padX,padY=20,40; W=w+padX*2;H=h+length+64
    base,top,side,dark,accent=PALETTES[spec['style']]
    base=color(base);top=color(top);side=color(side);dark=color(dark);accent=color(accent)
    rng=random.Random(int.from_bytes(hashlib.sha256(area.encode()).digest()[:8],'big'))
    im=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(im)
    L=padX;R=L+w; T=padY-rise; B=T+h;surfaceBottom=padY+h
    # Dirt under a raised deck, translucent shadow rather than solid painted rectangle
    d.rounded_rectangle((L-9,padY+h-4,R+12,padY+h+15),radius=5,fill=(27,27,43,51))
    d.polygon([(L+2,T+5),(R+5,T+5),(R+8,surfaceBottom+1),(L-1,surfaceBottom+1)],fill=dark)
    d.rectangle((L-1,T+4,R+2,B+rise),fill=side)
    d.rectangle((L,T,R,B),fill=base,outline=dark,width=3)
    d.rectangle((L+5,T+5,R-5,B-4),fill=top)
    # deck inlay + pixel trims
    d.line((L+10,T+10,R-10,T+10),fill=accent,width=3)
    for y in range(T+19,B-3,23):
        d.line((L+9,y,R-9,y),fill=base,width=2)
    for i in range(22):
        xx=rng.randrange(L+9,R-9);yy=rng.randrange(T+15,B-8)
        if rng.random()<.4:d.rectangle((xx,yy,xx+3,yy+1),fill=accent)
        else:d.rectangle((xx,yy,xx+2,yy+1),fill=base)
    # stepped retaining wall interrupted by central stair opening
    sw=int(spec.get('stairWidth',60));center=(L+R)//2
    sx=center-sw//2
    d.rectangle((L,B,R,surfaceBottom),fill=side)
    for i in range(0,rise,6):
        d.line((L,B+i,R,B+i),fill=dark if i%12==0 else base,width=2)
    d.rectangle((sx-2,B-2,sx+sw+2,surfaceBottom+4),fill=(0,0,0,0)) # painted later with stair top
    d.rectangle((L,B,sx-5,surfaceBottom),fill=side)
    d.rectangle((sx+sw+5,B,R,surfaceBottom),fill=side)
    d.line((L,B,L,surfaceBottom),fill=dark,width=4)
    d.line((R,B,R,surfaceBottom),fill=dark,width=4)
    # stone/wood/astral stair treads: physical world transition from raised deck to ground
    steps=max(6,length//12)
    for n in range(steps):
        yy=int(B+n*(length+rise)/steps)
        width=int(sw + n*8/steps)
        left=center-width//2
        d.rectangle((left-4,yy-1,left+width+4,yy+10),fill=dark)
        d.rectangle((left,yy,left+width,yy+6),fill=top if n%2==0 else base)
        d.line((left+3,yy+2,left+width-3,yy+2),fill=accent,width=2)
        if spec['style']=='wood':
            d.line((left+width//2,yy+2,left+width//2,yy+6),fill=side,width=1)
    # neat foot landing
    foot=B+length+rise
    d.rounded_rectangle((sx-10,foot-5,sx+sw+10,foot+11),radius=4,fill=side,outline=dark,width=2)
    d.line((sx-2,foot-3,sx+sw+3,foot-3),fill=accent,width=2)
    # posts and raised side balustrades
    for xx in (L+9,R-10):
        d.rectangle((xx-4,T-10,xx+5,T+21),fill=dark)
        d.rectangle((xx-2,T-15,xx+3,T-10),fill=accent)
        d.rectangle((xx-2,T+21,xx+2,T+25),fill=base)
    d.line((L+12,T-4,R-12,T-4),fill=side,width=5)
    # Side stairs rail has a staircase profile (visible without blocking path)
    for sideX in (-1,1):
        xx=sx-10 if sideX<0 else sx+sw+10
        for n in range(5):
            y=int(B+ n*(foot-B)/4)
            d.rectangle((xx-4,y-9+n*2,xx+4,y+12),fill=dark)
            d.rectangle((xx-2,y-11+n*2,xx+2,y-8+n*2),fill=accent)
        # cascading handrail edges
        d.line([(xx,B-12),(xx,foot+3)],fill=side,width=2)
    # decorative lanterns; color-coded per biome
    for xx in (L+27,R-27):
        d.rectangle((xx-3,T+16,xx+3,T+26),fill=dark)
        d.rectangle((xx-5,T+11,xx+5,T+18),fill=accent)
        d.point((xx,T+13),fill=(255,255,245,245))
    # separate occlusion rail: foreground when player stands behind front edge
    fore=Image.new('RGBA',(W,H),(0,0,0,0));f=ImageDraw.Draw(fore)
    f.line((L+1,B-3,sx-6,B-3),fill=dark,width=5)
    f.line((sx+sw+6,B-3,R-1,B-3),fill=dark,width=5)
    for xx in (L+12,sx-7,sx+sw+7,R-12):
        f.rectangle((xx-3,B-18,xx+3,B+8),fill=side)
        f.rectangle((xx-3,B-20,xx+3,B-17),fill=accent)
    return im,fore

def main():
    specs=json.loads(META.read_text(encoding='utf-8'))
    p=ASSETS/'data/maps.json';mapping=json.loads(p.read_text(encoding='utf-8'))
    if '_v51EnvironmentOverhaul' in mapping:
        raise RuntimeError('Project ini sudah v5.1. Pakai tools/v51_environment_overhaul.py, jangan generator v5.0 yang menghapus koordinat baru.')
    out=ASSETS/'maps/elevation';out.mkdir(parents=True,exist_ok=True)
    for area,spec in specs.items():
        if area not in mapping['areas']:raise ValueError('Area missing: '+area)
        for n in ('x','y','w','h','rise','stair'):assert spec[n]>0,(area,n)
        im,fore=texture(area,spec)
        base='v50_'+area+'_terrace'
        im.save(out/(base+'.png'),optimize=True)
        fore.save(out/(base+'_front.png'),optimize=True)
        mapping['areas'][area]['elevationPlatforms']=[{
            'id':'terrace_'+area,
            'x':spec['x'],'y':spec['y'],'w':spec['w'],'h':spec['h'],
            'rise':spec['rise'],'stairLength':spec['stair'],'stairWidth':spec.get('stairWidth',60),
            'image':'maps/elevation/'+base+'.png','front':'maps/elevation/'+base+'_front.png',
            'style':spec['style']
        }]
    mapping['_v50VerticalWorld']='21 original 2.5D walkable terraces, stairs, elevation + occlusion; source: tools/v50_terraces.json'
    p.write_text(json.dumps(mapping,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Generated',len(specs),'pairs of editable world art; added 2.5D metadata to maps.json')

if __name__=='__main__':main()
