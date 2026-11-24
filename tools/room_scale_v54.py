#!/usr/bin/env python3
"""v5.4 interior scale rebalance (one-time, idempotent).

The v4 handcrafted interiors (Arland/Sofia rooms, kitchen, archive) were painted
at roughly twice the scale of the 48x72 characters: stools as tall as a person,
wardrobes 3x the body height. This shrinks those four areas uniformly by 0.5 -
map art, their room-specific prop sprites, walls, doors, props, examine spots,
quest interactables/NPC spots/cutscene marks, and doors leading into them - so
furniture-to-character proportions match the rest of the world. Characters,
foot hitbox and every other map are untouched. Originals are archived in
art_source/v54_room_scale/. Saves migrate via MapLayoutV54 (mapLayoutVersion 5).
"""
import json, shutil
from pathlib import Path
from PIL import Image

R = Path(__file__).resolve().parents[1]
A = R / 'android/assets'
ARCH = R / 'art_source/v54_room_scale'
S = 0.5
ROOMS = ['arland_room', 'sofia_room', 'dapur', 'ruang_arsip']
MIN_R = 40  # interaction radius floor: the character (and its reach) is not scaled
# Legacy hard-coded bed spots from GameScreen (route room, bed centre).
BEDS = {'arland_room': [830, 380], 'sofia_room': [130, 380]}
# Cutscene commands that carry room coordinates without an 'area' key.
ROOM_CUTSCENE_STEPS = {'PRO_PHONE'}

def sc(v): return int(round(v * S))
def rect(r): return [sc(v) for v in r]

def shrink_image(rel):
    src = A / rel; arch = ARCH / rel
    if not arch.exists():
        arch.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(src, arch)
    im = Image.open(arch).convert('RGBA')
    out = im.resize((max(1, sc(im.width)), max(1, sc(im.height))), Image.LANCZOS)
    out.save(src, optimize=True)

def is_pt(v): return isinstance(v, list) and len(v) == 2 and all(isinstance(n, (int, float)) for n in v)

def scale_xy(o, keep_r=False):
    """Scale every position a quest/cutscene dict carries: x/y, move 'to' and 'path'."""
    hit = False
    if isinstance(o.get('x'), (int, float)) and isinstance(o.get('y'), (int, float)):
        o['x'] = sc(o['x']); o['y'] = sc(o['y']); hit = True
        if 'r' in o and not keep_r: o['r'] = max(MIN_R, sc(o['r']))
    if is_pt(o.get('to')): o['to'] = [sc(v) for v in o['to']]; hit = True
    if isinstance(o.get('path'), list) and o['path'] and all(is_pt(q) for q in o['path']):
        o['path'] = [[sc(v) for v in q] for q in o['path']]; hit = True
    return hit

FW = 18  # MapDb.FOOT_W; foot box x-9..x+9, y-6..y+2 (not scaled)

def blocked_fn(area, props):
    rs = [tuple(r) for r in area.get('walls', [])]
    for p in area.get('props', []):
        d = props.get(p['type'], {})
        if d.get('cw', 0) > 0 and d.get('ch', 0) > 0: rs.append((p['x'] - d['cw'] / 2, p['y'] - d['ch'], d['cw'], d['ch']))
    es = [tuple(e) for e in area.get('ellipses', [])]
    def blocked(x, y):
        x0, y0, x1, y1 = x - FW / 2, y - 6, x + FW / 2, y + 2
        if x0 < 0 or y0 < 0 or x1 > area['w'] or y1 > area['h']: return True
        for (rx, ry, rw, rh) in rs:
            if x0 < rx + rw and x1 > rx and y0 < ry + rh and y1 > ry: return True
        for (cx, cy, rx, ry) in es:
            for (px, py) in ((x0, y0), (x1, y0), (x0, y1), (x1, y1), (x, y)):
                if ((px - cx) / rx) ** 2 + ((py - cy) / ry) ** 2 < 1: return True
        return False
    return blocked

def nudge(pt, checks):
    """Halving walls while the foot box keeps its size can leave a standing point
    a few px inside furniture: move it to the nearest spot legal in every room."""
    x, y = pt
    if not any(b(x, y) for b in checks): return pt
    for r in range(1, 41):
        for dy in range(-r, r + 1):
            for dx in (-r, r) if abs(dy) != r else range(-r, r + 1):
                if not any(b(x + dx, y + dy) for b in checks): return [x + dx, y + dy]
    raise SystemExit(f'no legal spot near {pt}')

def main():
    mp = A / 'data/maps.json'; qp = A / 'data/quests.json'; pp = A / 'data/props.json'
    maps = json.loads(mp.read_text(encoding='utf-8')); areas = maps['areas']
    props = json.loads(pp.read_text(encoding='utf-8'))['props']
    todo = [k for k in ROOMS if not areas[k].get('v54Scale')]
    if not todo:
        print('room scale v5.4 already applied'); return
    for k in todo:
        a = areas[k]
        assert (a['w'], a['h']) == (1200, 896), k
        assert not a.get('elevationPlatforms'), k + ' has terraces'
        shrink_image(a['image'])
        a['w'] = sc(a['w']); a['h'] = sc(a['h'])
        a['spawn'] = [sc(v) for v in a['spawn']]
        a['walls'] = [rect(w) for w in a.get('walls', [])]
        a['ellipses'] = [rect(e) for e in a.get('ellipses', [])]
        a['water'] = [{kk: (sc(v) if kk in ('cx', 'cy', 'rx', 'ry') else v) for kk, v in w.items()} for w in a.get('water', [])]
        for g in a.get('gates', []): g['rect'] = rect(g['rect'])
        for d in a.get('doors', []): d['rect'] = rect(d['rect'])
        for p in a.get('props', []):
            p['x'] = sc(p['x']); p['y'] = sc(p['y'])
            if p['type'].startswith('maps_v4_' + k + '_'):
                shrink_image(props[p['type']]['image'])
        for e in a.get('examine', []): scale_xy(e)
        if k in BEDS: a['bed'] = [sc(v) for v in BEDS[k]]
        a['v54Scale'] = S
    for k, a in areas.items():
        for d in a.get('doors', []):
            if d.get('to') in todo: d['tx'] = sc(d['tx']); d['ty'] = sc(d['ty'])
    mp.write_text(json.dumps(maps, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    quests = json.loads(qp.read_text(encoding='utf-8')); n = [0]
    def walk(o, ctx):
        if isinstance(o, dict):
            a = o['area'] if isinstance(o.get('area'), str) else ctx
            # '$ROOM' is the route's own bedroom (arland_room / sofia_room).
            if (a in todo or (a == '$ROOM' and 'arland_room' in todo)) and scale_xy(o): n[0] += 1
            for v in o.values(): walk(v, a)
        elif isinstance(o, list):
            for v in o: walk(v, ctx)
    walk(quests, None)
    for s in quests['steps']:
        if s.get('id') in ROOM_CUTSCENE_STEPS:
            for blk in s.get('onStart', []):
                for c in blk.get('cmds', []):
                    if 'area' not in c and scale_xy(c, keep_r=True): n[0] += 1
    # Standing points (spawn, door landings, warps, cutscene place/move) must stay legal.
    B = {k: blocked_fn(areas[k], props) for k in todo}
    moved = []
    for k in todo:
        a = areas[k]; new = nudge(a['spawn'], [B[k]])
        if new != a['spawn']: moved.append((k, 'spawn', a['spawn'], new)); a['spawn'] = new
    for k, a in areas.items():
        for d in a.get('doors', []):
            if d.get('to') in B:
                new = nudge([d['tx'], d['ty']], [B[d['to']]])
                if new != [d['tx'], d['ty']]: moved.append((k, d['id'], [d['tx'], d['ty']], new)); d['tx'], d['ty'] = new
    def checks_for(a):
        if a == '$ROOM': return [B[r] for r in ('arland_room', 'sofia_room') if r in B]
        return [B[a]] if a in B else None
    def stand(o, ctx):
        if isinstance(o, dict):
            a = o['area'] if isinstance(o.get('area'), str) else ctx
            ch = checks_for(a)
            if ch:
                # Cutscene 'place' may sit an actor on furniture; only warps and move endpoints must be legal.
                if o.get('do') == 'warp' and isinstance(o.get('x'), (int, float)):
                    new = nudge([o['x'], o['y']], ch)
                    if new != [o['x'], o['y']]: moved.append((a, o.get('do') or o.get('c'), [o['x'], o['y']], new)); o['x'], o['y'] = new
                if o.get('c') == 'move':
                    if is_pt(o.get('to')):
                        new = nudge(o['to'], ch)
                        if new != o['to']: moved.append((a, 'move', o['to'], new)); o['to'] = new
                    if isinstance(o.get('path'), list) and o['path'] and is_pt(o['path'][-1]):
                        new = nudge(o['path'][-1], ch)
                        if new != o['path'][-1]: moved.append((a, 'path', o['path'][-1], new)); o['path'][-1] = new
            for v in o.values(): stand(v, a)
        elif isinstance(o, list):
            for v in o: stand(v, ctx)
    stand(quests, None)
    for st in quests['steps']:
        if st.get('id') in ROOM_CUTSCENE_STEPS:
            for blk in st.get('onStart', []):
                for c in blk.get('cmds', []):
                    room = {'arland': 'arland_room', 'sofia': 'sofia_room'}.get(c.get('route'))
                    if room in B: stand(c, room)
    for m in moved: print('nudged', *m)
    mp.write_text(json.dumps(maps, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    qp.write_text(json.dumps(quests, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'room scale v5.4 applied to {todo}; {n[0]} quest coordinates scaled')

if __name__ == '__main__':
    main()
