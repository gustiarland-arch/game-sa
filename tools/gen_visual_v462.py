#!/usr/bin/env python3
"""Regenerate v4.6.2 8-facing pixel-art strips & atmosphere overlays (Pillow).

All source v4.6.1 atlases remain intact. Diagonal frames are pixel-preserving
procedural adaptations, NOT independently hand-painted diagonal artwork.
Use: python3 tools/gen_visual_v462.py (from project root).
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import math

ROOT = Path(__file__).resolve().parents[1]
ASSET = ROOT / 'android/assets'
FW,FH=48,72

def warp_diagonal(frame, skew, side_offset):
    """Nearest-neighbor horizontal pixel shift per height, with foot anchored.
    Head gets subtle diagonal perspective while keeping sprite transparent and sharp.
    """
    out = Image.new('RGBA', (FW,FH), (0,0,0,0))
    pix = frame.load(); dst=out.load()
    for y in range(FH):
        # Sprite head is high on source sheet; anchor feet at 0 displacement.
        shift = round(skew * (1.0 - y / (FH-1)))
        for x in range(FW):
            tx=x+shift+side_offset
            if 0<=tx<FW: dst[tx,y]=pix[x,y]
    return out

def diagonals(path, dest, is_idle=False):
    sheet=Image.open(path).convert('RGBA')
    phase=sheet.width//FW
    assert sheet.height==FH*4 and phase in (8,16), (path,sheet.size)
    atlas=Image.new('RGBA',(phase*FW,8*FH),(0,0,0,0))
    # Output rows: down, down-left, left, up-left, up, up-right, right, down-right.
    for f in range(phase):
        for d,source,skew,offset in [
            (0,0,0,0),(1,0,-3,0),(2,1,0,0),(3,3,-3,0),
            (4,3,0,0),(5,3,3,0),(6,2,0,0),(7,0,3,0)]:
            cell=sheet.crop((f*FW,source*FH,(f+1)*FW,(source+1)*FH))
            if skew: cell=warp_diagonal(cell,skew,offset)
            atlas.paste(cell,(f*FW,d*FH))
    dest.parent.mkdir(parents=True,exist_ok=True)
    atlas.save(dest,optimize=True)
    return phase

def tile_effects():
    d=ASSET/'fx';d.mkdir(exist_ok=True)
    # Pixelated fog, edge-faded to avoid obvious rectangle seams; RGBA, tile-friendly.
    fog=Image.new('RGBA',(256,64));p=fog.load()
    for y in range(0,64,4):
        for x in range(0,256,4):
            f=(1-abs((x+2)-128)/128)**.4
            h=(1-abs((y+2)-32)/32)**.7
            v=(math.sin((x+2)*.067)+math.cos((x+2)*.021+(y+2)*.051)+2)/4
            a=round(max(0,35*f*h*v))
            for dy in range(4):
                for dx in range(4):p[x+dx,y+dy]=(205,224,240,a)
    fog.save(d/'v462_mist.png')
    # Sun shafts with broad warm transparent edges, no procedural GPU shaders.
    beam=Image.new('RGBA',(64,192));p=beam.load()
    for y in range(0,192,4):
        for x in range(0,64,4):
            rel=abs((x+2-32)/32)
            spread=.45+(y+2)/192*.55
            a=round(52*max(0,1-rel/spread)**1.8*(.38+.62*(y+2)/192))
            for dy in range(4):
                for dx in range(4):p[x+dx,y+dy]=(255,225,153,a)
    beam.save(d/'v462_sunbeam.png')
    leaf=Image.new('RGBA',(16,16));dr=ImageDraw.Draw(leaf)
    dr.polygon([(2,10),(4,6),(10,2),(13,3),(11,8),(6,12)],fill=(102,169,79,255))
    dr.line([(4,11),(11,4)],fill=(55,114,55,255),width=1)
    leaf.save(d/'v462_leaf.png')
    petal=Image.new('RGBA',(16,16));dr=ImageDraw.Draw(petal)
    dr.polygon([(2,7),(5,3),(10,4),(13,8),(10,12),(5,11)],fill=(255,172,202,244))
    dr.polygon([(5,4),(10,4),(12,8),(7,8)],fill=(255,218,231,255))
    petal.save(d/'v462_blossom.png')
    fly=Image.new('RGBA',(32,32));p=fly.load()
    for y in range(32):
        for x in range(32):
            dist=((x-15.5)**2+(y-15.5)**2)**.5
            alpha=round(46*math.exp(-(dist/8)**2))
            if dist<2.4: p[x,y]=(255,244,151,244)
            else:p[x,y]=(252,240,152,alpha)
    fly.save(d/'v462_firefly.png')
    glint=Image.new('RGBA',(24,12));dr=ImageDraw.Draw(glint)
    dr.line((2,6,21,6),fill=(200,243,255,235),width=2)
    dr.point((11,4),fill=(255,255,255,255));dr.point((12,8),fill=(212,249,255,200))
    glint.save(d/'v462_water_glint.png')
    rain=Image.new('RGBA',(8,24));dr=ImageDraw.Draw(rain)
    dr.line((5,1,2,18),fill=(173,220,255,158),width=2)
    dr.point((1,20),fill=(215,246,255,130))
    rain.save(d/'v462_raindrop.png')

if __name__=='__main__':
    count=0
    for folder in sorted((ASSET/'characters').iterdir()):
        if not folder.is_dir() or folder.name not in ('arland','sofia'):continue
        wp=folder/'walk_v37.png';ip=folder/'idle_v37.png'
        if not (wp.exists() and ip.exists()): continue
        assert diagonals(wp,folder/'walk_8dir_v462.png')==16
        assert diagonals(ip,folder/'idle_8dir_v462.png',True)==8
        count+=1
    assert count==2,count
    tile_effects()
    print('Generated 8-facing walk/idle for',count,'characters + 7 atmosphere textures')
