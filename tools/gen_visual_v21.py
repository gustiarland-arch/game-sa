"""Original and editable v2.1 pixel-art environment, full UI skin, and eight-frame walking atlases.
Usage: python3 tools/gen_visual_v21.py android/assets
Built atop existing sprite walk.png files. It NEVER overwrites the source/legacy sheets.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import math, random, sys
A = Path(sys.argv[1] if len(sys.argv)>1 else 'android/assets')
UI=A/'ui'; UI.mkdir(parents=True, exist_ok=True)
rng=random.Random(21021)
W,H=1280,720
# Far skyline: deliberately block-pixelated rather than a blurry stock photo.
far=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(far)
for y in range(H):
    t=y/H
    if t<0.56:
        u=t/.56
        col=(int(45+138*u),int(32+82*u),int(82+53*u),255)
    else:
        u=(t-.56)/.44
        col=(int(183-98*u),int(114-54*u),int(135-29*u),255)
    d.line([(0,y),(W,y)],fill=col)
# sun/moon halo in blocky rings
cx,cy=940,315
for r in range(148,26,-12):
    a=(148-r)/148
    d.ellipse([cx-r,cy-r,cx+r,cy+r], fill=(int(212+40*a),int(146+67*a),int(149+67*a),int(14+45*a)))
d.ellipse([cx-52,cy-52,cx+52,cy+52],fill=(255,216,166,255))
# Stylized horizontal clouds: stepped horizontal highlights rather than giant circular stock shapes.
for x,y,sz in [(-35,128,1.0),(280,175,.83),(700,118,.78),(1102,180,.91)]:
    x=int(x);y=int(y);s=int(85*sz)
    col=(226,151,172,255); rim=(194,124,155,255); shine=(247,190,189,255)
    d.rectangle((x,y+18,x+int(2.5*s),y+40),fill=rim)
    d.rectangle((x+int(.2*s),y+10,x+int(2.15*s),y+30),fill=col)
    d.rectangle((x+int(.55*s),y,x+int(1.75*s),y+23),fill=col)
    d.rectangle((x+int(.75*s),y+4,x+int(1.6*s),y+7),fill=shine)
    d.rectangle((x+int(.3*s),y+15,x+int(.75*s),y+18),fill=shine)
# distant hills as successive silhouette bands
for idx,(yy,col) in enumerate([(450,(102,75,124,255)),(501,(73,60,107,255)),(553,(49,44,79,255))]):
    pts=[(0,H)]
    pts += [(x, int(yy+18*math.sin(x/115+idx)+12*math.sin(x/37+idx*1.7))) for x in range(0,W+15,15)]
    pts.append((W,H)); d.polygon(pts,fill=col)
for x in range(150,1250,42):
    base=round(545+math.sin(x/85)*12)
    height=round(24+18*abs(math.sin(x*.053)))
    d.rectangle((x,base-height,x+26,base+35),fill=(65,52,91,255))
    for xx in range(x+5,x+24,9):
        for yy in range(base-height+6,base+20,13):
            if rng.random()<.5: d.rectangle((xx,yy,xx+4,yy+5),fill=(233,172,135,185))
far.save(UI/'v21_skyline.png')
# Mid silhouette transparent: park bridge, trees, lanterns, flowers, a bench
mid=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(mid)
d.polygon([(0,618),(260,602),(520,621),(800,610),(1090,592),(1280,619),(1280,720),(0,720)],fill=(34,39,65,255))
# a pavilion/bridge silhouette, riverfront
for x in [375, 405, 435, 465, 495, 525, 555, 585, 615, 645, 675]:
    d.rectangle((x,570,x+5,645),fill=(32,36,61,255))
d.line((375,575,680,575),fill=(24,29,54,255),width=12)
d.arc((365,529,680,633),180,360,fill=(27,29,58,255),width=7)
# large foreground trees
for x,base,sc in [(76,677,1.13),(1205,675,1.28)]:
    tr=int(26*sc); d.rectangle((x-tr//2,base-205*sc,x+tr//2,720),fill=(39,30,60,255))
    for ox,oy,rad in [(-50,-205,93),(45,-216,108),(-12,-280,88),(66,-286,74)]:
        xx=x+ox*sc; yy=base+oy*sc;rr=rad*sc
        d.ellipse((xx-rr,yy-rr,xx+rr,yy+rr),fill=(51,55,91,255))
        d.ellipse((xx-rr+11,yy-rr+10,xx+rr-17,yy+rr-23),fill=(69,65,110,255))
# wooden park bench
bx=812; d.rectangle((bx,594,bx+130,608),fill=(64,47,78,255)); d.rectangle((bx,624,bx+130,636),fill=(64,47,78,255))
for x in (bx+16,bx+112): d.rectangle((x,629,x+8,686),fill=(35,35,59,255))
# streetlamps with warm micro-glows drawn as geometric rings
for x in (260,1026):
    d.rectangle((x,514,x+9,687),fill=(32,30,56,255))
    d.polygon([(x-12,516),(x+20,516),(x+14,492),(x-6,492)],fill=(51,44,72,255))
    d.rectangle((x-4,500,x+13,518),fill=(255,201,120,255))
# blossom clusters and floating petals
for i in range(170):
    x=rng.randrange(W); y=rng.randint(580,716)
    d.rectangle((x,y,x+rng.choice([2,3,4]),y+2),fill=rng.choice([(198,115,157,255),(247,177,193,255),(245,206,154,255)]))
mid.save(UI/'v21_foreground.png')
# New unified ninepatch-style UI skin; 48x48, 18px margins remain stable under NinePatch.
def skin(name, bg, rim, shadow, accent):
    img=Image.new('RGBA',(48,48),(0,0,0,0)); di=ImageDraw.Draw(img)
    di.rounded_rectangle((0,0,47,47),radius=13,fill=rim)
    di.rounded_rectangle((3,3,44,44),radius=10,fill=shadow)
    di.rounded_rectangle((5,5,42,42),radius=9,fill=bg)
    di.line((12,6,35,6),fill=accent,width=2)
    di.line((10,41,37,41),fill=accent,width=1)
    for a,b in [(8,14),(39,14),(8,34),(39,34)]: di.point((a,b),fill=accent)
    img.save(UI/name)
skin('panel_v21.png',(250,235,232,255),(72,50,91,255),(217,183,200,255),(255,255,239,255))
skin('panel_dark_v21.png',(45,36,65,235),(181,137,182,255),(72,56,99,245),(242,192,181,255))
skin('button_v21.png',(255,239,225,255),(70,52,90,255),(225,189,194,255),(255,255,242,255))
skin('button_down_v21.png',(237,193,200,255),(70,52,90,255),(195,139,168,255),(255,225,235,255))
skin('button_accent_v21.png',(236,157,182,255),(77,49,94,255),(191,100,157,255),(255,216,210,255))
skin('button_disabled_v21.png',(210,204,213,255),(138,124,150,255),(186,181,191,255),(230,227,235,255))
# Detail ribbons for message dialogue and cinematic chapter captions.
img=Image.new('RGBA',(512,128),(0,0,0,0)); di=ImageDraw.Draw(img)
for y in range(128):
    u=y/127
    di.line((0,y,511,y),fill=(int(45+15*u),int(32+8*u),int(68+16*u),int(244-22*u)))
di.rounded_rectangle((3,3,508,124),radius=13,outline=(231,165,191,255),width=4)
di.line((19,15,493,15),fill=(255,225,173,220),width=2)
for x in (27,485):
    di.polygon([(x,8),(x+7,17),(x,26),(x-7,17)],fill=(255,211,142,255))
img.save(UI/'v21_dialog_ribbon.png')
# Bloom halo for significant cutscenes, alpha faded texture.
n=256; im=Image.new('RGBA',(n,n),(0,0,0,0)); px=im.load()
for y in range(n):
    for x in range(n):
        dist=((x-127.5)**2+(y-127.5)**2)**.5/128
        a=int(max(0,1-dist)**2.3*140)
        px[x,y]=(255,226,180,a)
im.save(UI/'v21_bloom.png')
# EIGHT-frame sprites (4 directional rows). Legs and body offset in different phases;
# original 3-frame atlases remain editable and are never overwritten.
actors=[]
for walk in sorted((A/'characters').glob('*/walk.png')):
    source=Image.open(walk).convert('RGBA')
    if source.size != (144,288): continue
    atlas=Image.new('RGBA',(48*8,72*4),(0,0,0,0))
    seq=[0,1,1,0,0,2,2,0]
    for direction in range(4):
        for frame, srcindex in enumerate(seq):
            src=source.crop((srcindex*48,direction*72,(srcindex+1)*48,(direction+1)*72))
            body=src.crop((0,0,48,49)); legs=src.crop((0,49,48,72))
            # step phases keep visible foot contact near the existing player foot anchor
            offx=[0,-1,0,0,0,1,0,0][frame]
            offy=[0,0,-1,-1,0,-1,-1,0][frame]
            cell=Image.new('RGBA',(48,72),(0,0,0,0))
            cell.alpha_composite(legs,(0,49))
            cell.alpha_composite(body,(offx,max(0,offy)))
            # add a subtle shine pixel near the hem on peak steps, if image exists
            atlas.alpha_composite(cell,(frame*48,direction*72))
    atlas.save(walk.parent/'walk_plus.png')
    actors.append(walk.parent.name)
print('Visual v2.1 generated: 2 illustrated layers, 6 UI skins, dialogue ribbon, bloom,',len(actors),'walking atlases')
