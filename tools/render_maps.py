"""Render pratinjau peta lengkap (tanah + props terurut-Y) ke folder output. Pemakaian: python3 tools/render_maps.py <assets> <maps.json> <outdir> [scale]"""
import sys, os, json
from PIL import Image
A, MJ, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
scale = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
maps = json.load(open(MJ)); maps = maps.get('areas', maps)
props = json.load(open(os.path.join(A, 'data', 'props.json')))['props']
os.makedirs(OUT, exist_ok=True)
for mid, m in maps.items():
    bg = Image.open(os.path.join(A, m['image'])).convert('RGBA')
    for p in sorted(m['props'], key=lambda p: (props[p['type']].get('layer') != 'floor', p['y'])):
        im = Image.open(os.path.join(A, props[p['type']]['image'])).convert('RGBA')
        bg.alpha_composite(im, (int(p['x'] - im.width / 2), int(p['y'] - im.height)))
    if scale != 1: bg = bg.resize((int(bg.width * scale), int(bg.height * scale)), Image.LANCZOS)
    bg.convert('RGB').save(os.path.join(OUT, mid + '.png'))
print('ok')
