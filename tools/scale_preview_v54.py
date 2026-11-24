#!/usr/bin/env python3
"""Static (non-runtime) scale preview: map art + y-sorted props + Arland/Sofia
at spawn using the same 1:1 world-pixel rules as GameScreen.drawProp and
Actor (frame 48x72 * 0.85). Labelled as a preview, never as a runtime screenshot."""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw
R = Path(__file__).resolve().parents[1]; A = R / 'android/assets'
areas = json.loads((A / 'data/maps.json').read_text(encoding='utf-8'))['areas']
defs = json.loads((A / 'data/props.json').read_text(encoding='utf-8'))['props']

import os, re
SCALE = float(os.environ.get('OLU_ACTOR_SCALE') or re.search(r'SCALE = ([0-9.]+)f',
    (R / 'core/src/main/java/com/arlandsofia/olu/game/Actor.java').read_text(encoding='utf-8')).group(1))

def char(name):
    im = Image.open(A / f'characters/{name}/walk_v53.png').convert('RGBA').crop((0, 0, 48, 72))
    return im.resize((round(48 * SCALE), round(72 * SCALE)), Image.NEAREST)

def render(aid, out, crop=900):
    a = areas[aid]; base = Image.open(A / a['image']).convert('RGBA')
    W, H = base.size
    sx, sy = a.get('spawn', [W / 2, H / 2])
    items = [(p['y'], 'p', p) for p in a.get('props', []) if p['type'] in defs]
    items += [(sy, 'c', ('arland', sx - 22, sy)), (sy, 'c', ('sofia', sx + 22, sy))]
    floor = [i for i in items if i[1] == 'p' and defs[i[2]['type']].get('layer') == 'floor']
    for _, _, p in floor:
        t = Image.open(A / defs[p['type']]['image']).convert('RGBA')
        base.alpha_composite(t, (round(p['x'] - t.width / 2), round(p['y'] - t.height)))
    for _, kind, it in sorted([i for i in items if i not in floor], key=lambda i: i[0]):
        if kind == 'p':
            t = Image.open(A / defs[it['type']]['image']).convert('RGBA')
            base.alpha_composite(t, (round(it['x'] - t.width / 2), round(it['y'] - t.height)))
        else:
            c = char(it[0]); base.alpha_composite(c, (round(it[1] - c.width / 2), round(it[2] - c.height)))
    if os.environ.get('OLU_PREVIEW_FULL'):
        img = base
        d = ImageDraw.Draw(img); d.rectangle([0, 0, 420, 16], fill=(0, 0, 0, 180))
        d.text((4, 3), f'{aid} {W}x{H} - static preview, not runtime', fill=(255, 255, 255, 255))
        img.convert('RGB').save(out); return
    half = crop // 2
    x0 = int(max(0, min(W - crop, sx - half))); y0 = int(max(0, min(H - crop * 0.6, sy - crop * 0.3)))
    img = base.crop((x0, y0, min(W, x0 + crop), min(H, y0 + int(crop * 0.6))))
    img = img.resize((img.width * 2, img.height * 2), Image.NEAREST)
    d = ImageDraw.Draw(img); d.rectangle([0, 0, 520, 22], fill=(0, 0, 0, 180))
    d.text((6, 5), f'{aid} - actor scale {SCALE} - static preview (not a runtime screenshot)', fill=(255, 255, 255, 255))
    img.convert('RGB').save(out)

if __name__ == '__main__':
    od = Path(sys.argv[1]) if len(sys.argv) > 1 else R / 'docs/v54/scale_preview'
    od.mkdir(parents=True, exist_ok=True)
    for aid in sys.argv[2:] or ['arland_room', 'sofia_room', 'cafe', 'perpustakaan', 'plaza', 'galeri_komunitas']:
        render(aid, od / f'{aid}.png', 640 if areas[aid].get('w', 960) <= 960 else 900)
        print('wrote', od / f'{aid}.png')
