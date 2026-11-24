#!/usr/bin/env python3
"""Arland & Sofia v3.7: regenerate enhanced 16-step walk + 8-phase idle sprites.

Uses actual v3.2 atlas pixels as *source* (not procedural stick figures). Each
animation variant is derived from an immutable base; re-running is deterministic.
No edits to the original walk/pose/portrait sheets. Requires Pillow.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import hashlib, json, math

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / 'android' / 'assets'
FRAME_W, FRAME_H = 48, 72
FRAMES_WALK, FRAMES_IDLE = 16, 8


def put(dst, source, phase, direction, idle):
    """Animate head, upper cloth and foot pixels with discrete pixel offset.

    Pieces preserve original antialias-free palette; small offsets create actual
    pixel changes in addition to newly retimed base walking frames.
    """
    w, h = source.size
    assert (w, h) == (FRAME_W, FRAME_H)
    t = phase / (FRAMES_IDLE if idle else FRAMES_WALK)
    # 1px front-back lean, with no cumulative shift/blur.
    lean = int(round(math.sin(t * 2 * math.pi) * (0.7 if idle else 1.2)))
    hair_dy = int(round(math.cos(t * math.pi * 4) * (0.75 if idle else 0.5)))
    if direction == 3:  # back of head: less sway
        lean = int(round(lean * 0.45))
    # Draw base completely: avoid gaps in the silhouette at sprite joins.
    dst.alpha_composite(source, (0, 0))
    # Repaint an exact pixel region with shifted hair, retaining original ink.
    head = source.crop((4, 4, 44, 31))
    dst.alpha_composite(head, (4 + lean, 4 + hair_dy))
    # Sleeves/torso lower move only during walking; source legs remain detailed.
    if not idle:
        sway = int(round(math.sin(t * 4 * math.pi) * 0.85))
        body = source.crop((6, 40, 42, 56))
        dst.alpha_composite(body, (6 + sway, 40))
        # Foot highlights vary by stride; keeps the sole readable on all 4 sides.
        shoe = (37, 30, 48, 220) if direction in (0, 3) else (32, 26, 46, 190)
        d = ImageDraw.Draw(dst)
        for side in (0, 1):
            if (phase // 4 + side) % 2 == 0:
                x = 18 + side * 11 + (1 if direction == 2 else 0)
                y = 65 - (1 if phase % 4 in (1, 2) else 0)
                if dst.getpixel((min(FRAME_W-1,x), y))[3] > 160:
                    d.point((x,y), fill=shoe)


def create_atlas(base, phases, idle):
    assert base.size == ((6 if idle else 12) * FRAME_W, FRAME_H * 4), base.size
    nbase = base.width // FRAME_W
    atlas = Image.new('RGBA', (phases * FRAME_W, FRAME_H * 4))
    for direction in range(4):
        for phase in range(phases):
            source_idx = (phase * nbase // phases) % nbase
            source = base.crop((source_idx * FRAME_W, direction * FRAME_H,
                                (source_idx + 1) * FRAME_W, (direction + 1) * FRAME_H))
            frame = Image.new('RGBA', (FRAME_W, FRAME_H))
            put(frame, source, phase, direction, idle)
            atlas.alpha_composite(frame, (phase * FRAME_W, direction * FRAME_H))
    return atlas


def create_contact_shadow():
    """Soft dark contact-shadow mask for feet and standing props, independent of collision."""
    w, h = 96, 36
    im = Image.new('RGBA', (w,h))
    px = im.load()
    for y in range(h):
        for x in range(w):
            dx = (x-(w-1)/2) / (w * 0.5)
            dy = (y-(h-1)/2) / (h * 0.5)
            r2=dx*dx + dy*dy
            a=max(0, int(155 * math.exp(-3.2 * r2) * max(0, 1-r2)))
            px[x,y] = (20, 19, 32, a)
    path=ASSETS/'fx'/'contact_shadow_v37.png';path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, optimize=True)
    return path


def main():
    count=0; checks=[]
    for directory in sorted((ASSETS/'characters').iterdir()):
        walk=directory/'walk_v32.png'; idle=directory/'idle_v32.png'
        if not walk.is_file() or not idle.is_file(): continue
        with Image.open(walk) as f: wp=f.convert('RGBA')
        with Image.open(idle) as f: ip=f.convert('RGBA')
        for name, base, phases, isidle in [('walk_v37.png',wp,FRAMES_WALK,False),
                                            ('idle_v37.png',ip,FRAMES_IDLE,True)]:
            result=create_atlas(base,phases,isidle)
            target=directory/name; result.save(target,optimize=True)
            for direction in range(4):
                frames=[result.crop((k*FRAME_W,direction*FRAME_H,(k+1)*FRAME_W,(direction+1)*FRAME_H)).tobytes() for k in range(phases)]
                if len(set(frames)) < (5 if not isidle else 3):
                    raise RuntimeError('insufficient animation diversity: '+str(target)+' row '+str(direction))
                if not any(result.getchannel('A').getbbox()):
                    raise RuntimeError('empty sprite: '+str(target))
            checks.append({'path':str(target.relative_to(ROOT)), 'sha256':hashlib.sha256(target.read_bytes()).hexdigest(), 'size':list(result.size)})
        count+=1
    if count!=25:raise RuntimeError('expected 25 characters, got '+str(count))
    shadow=create_contact_shadow()
    checks.append({'path':str(shadow.relative_to(ROOT)),'sha256':hashlib.sha256(shadow.read_bytes()).hexdigest(), 'size':[96,36]})
    manifest=ROOT/'docs/CHARACTER_POLISH_V3.7_ASSETS.json'
    manifest.write_text(json.dumps({'characters':count,'walk_phases':16,'idle_phases':8,'assets':checks},indent=2)+'\n')
    print('CHARACTER V3.7:',count,'characters,',len(checks),'new assets,',FRAMES_WALK,'walk and',FRAMES_IDLE,'idle frames/direction')

if __name__=='__main__':main()
