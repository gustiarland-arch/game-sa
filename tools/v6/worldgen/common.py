"""Shared steps for v6 map redesigns: quest-coordinate migration, collider generation
from painted masks, walkability/reachability validation, and applying to the data files.

A map script defines: AREA, W, H, paint_ground() -> Canvas, area_entry(old) -> dict,
remap_point(x, y) -> (x, y), DOOR_TARGETS {door_id_in_other_map: (x, y)} and optionally
SITE (terrace dict for tools/v51_environment_sites.json). Then calls common.run(module).
"""
import sys, json
from pathlib import Path
from collections import deque
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
A = ROOT / 'android' / 'assets'


def migrate_quests(q, area, remap):
    """Remap every coordinate that belongs to `area`. Context = nearest 'area' key; inside
    action lists a warp switches the area for the following actions (cutscenes after warps)."""
    moved = []

    def walk(o, ctx):
        if isinstance(o, dict):
            if isinstance(o.get('area'), str):
                ctx = o['area']
            if ctx == area:
                if 'x' in o and 'y' in o and isinstance(o['x'], (int, float)) and not isinstance(o['x'], bool):
                    nx, ny = remap(o['x'], o['y'])
                    moved.append((o.get('id') or o.get('c') or o.get('do') or o.get('at') or '?', o['x'], o['y'], nx, ny, o.get('r')))
                    o['x'], o['y'] = nx, ny
                if o.get('c') == 'move':
                    v = o.get('to')
                    if isinstance(v, list) and len(v) == 2 and all(isinstance(n, (int, float)) for n in v):
                        o['to'] = list(remap(*v)); moved.append(('move', v[0], v[1], *o['to'], None))
                    if isinstance(o.get('path'), list):
                        old = o['path']; o['path'] = [list(remap(*pt)) for pt in old]
                        moved.extend(('path', a[0], a[1], b[0], b[1], None) for a, b in zip(old, o['path']))
            for v in o.values():
                if isinstance(v, (dict, list)):
                    walk(v, ctx)
        elif isinstance(o, list):
            cur = ctx
            for v in o:
                if isinstance(v, dict) and v.get('do') == 'warp' and isinstance(v.get('area'), str):
                    walk(v, cur); cur = v['area']; continue
                walk(v, cur)
    walk(q, None)
    return moved


def mask_to_walls(mask, step=8, min_run=1):
    """Blocked mask -> list of [x, y, w, h] row-strip rectangles (step px tall), merged runs."""
    H, W = mask.shape
    out = []
    for y in range(0, H, step):
        row = mask[y:y + step].any(axis=0)
        x = 0
        while x < W:
            if row[x]:
                s = x
                while x < W and row[x]:
                    x += 1
                if x - s >= min_run:
                    out.append([int(s), int(y), int(x - s), int(min(step, H - y))])
            else:
                x += 1
    # merge identical strips stacked vertically
    out.sort(key=lambda r: (r[0], r[2], r[1]))
    merged = []
    for r in out:
        if merged and merged[-1][0] == r[0] and merged[-1][2] == r[2] and merged[-1][1] + merged[-1][3] == r[1]:
            merged[-1][3] += r[3]
        else:
            merged.append(r)
    return merged


def blocked_fn(a, P):
    rects = list(a['walls'])
    for pr in a['props']:
        d = P[pr['type']]
        if d.get('cw', 0) > 0 and d.get('ch', 0) > 0:
            rects.append([pr['x'] - d['cw'] / 2, pr['y'] - d['ch'], d['cw'], d['ch']])
    R = np.array(rects, float) if rects else np.zeros((0, 4))

    def blocked(x, y):
        if x - 11 < 0 or x + 11 > a['w'] or y - 10 < 0 or y + 10 > a['h']:
            return True
        if len(R) and np.any((x - 11 < R[:, 0] + R[:, 2]) & (x + 11 > R[:, 0]) & (y - 10 < R[:, 1] + R[:, 3]) & (y + 10 > R[:, 1])):
            return True
        for cx, cy, rw, rh in a.get('ellipses', []):
            if ((x - cx) / (rw + 11)) ** 2 + ((y - cy) / (rh + 10)) ** 2 < 1:
                return True
        return False
    return blocked


def reachable(a, blocked, st=8):
    gw, gh = a['w'] // st, a['h'] // st
    ok = np.zeros((gh, gw), bool)
    for j in range(gh):
        for i in range(gw):
            ok[j, i] = not blocked(i * st + st / 2, j * st + st / 2)
    seen = np.zeros_like(ok)
    sx, sy = int(a['spawn'][0] // st), int(a['spawn'][1] // st)
    if not ok[sy, sx]:
        return seen, st
    dq = deque([(sx, sy)]); seen[sy, sx] = True
    while dq:
        i, j = dq.popleft()
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ii, jj = i + di, j + dj
            if 0 <= ii < gw and 0 <= jj < gh and ok[jj, ii] and not seen[jj, ii]:
                seen[jj, ii] = True; dq.append((ii, jj))
    return seen, st


def validate(a, P, points):
    blocked = blocked_fn(a, P)
    seen, st = reachable(a, blocked)
    bad = []
    if not seen.any():
        bad.append(('spawn blocked', 'spawn', *a['spawn']))
    for label, x, y, r in points:
        if blocked(x, y):
            rr = r or 40
            near = seen[max(0, int((y - rr) // st)):int((y + rr) // st) + 1, max(0, int((x - rr) // st)):int((x + rr) // st) + 1]
            if not near.any():
                bad.append(('blocked', label, x, y))
            continue
        if not seen[int(y // st), int(x // st)]:
            bad.append(('unreachable', label, x, y))
    return bad


def run(mod):
    area = mod.AREA
    M = json.loads((A / 'data/maps.json').read_text(encoding='utf-8'))
    Q = json.loads((A / 'data/quests.json').read_text(encoding='utf-8'))
    P = json.loads((A / 'data/props.json').read_text(encoding='utf-8'))['props']
    if '--ground-only' in sys.argv:
        c = mod.paint_ground()
        Image.fromarray(c.result(), 'RGB').save(sys.argv[sys.argv.index('--ground-only') + 1], optimize=True)
        return
    old = M['areas'][area]
    if old.get('v6Layout'):
        raise SystemExit(area + ' already migrated to v6 (re-run from the pre-v6 data)')
    c = mod.paint_ground()
    new = mod.area_entry(old, c)
    moved = migrate_quests(Q, area, mod.remap_point)
    M['areas'][area] = new
    for a in M['areas'].values():
        for d in a.get('doors', []):
            if d.get('to') == area:
                d['tx'], d['ty'] = mod.DOOR_TARGETS[d['id']]
    pts = [(m[0], m[3], m[4], m[5]) for m in moved]
    pts += [(d['id'], d['tx'], d['ty'], None) for a in M['areas'].values() for d in a.get('doors', []) if d.get('to') == area]
    pts += [('examine ' + e['id'], e['x'], e['y'], e.get('r')) for e in new.get('examine', [])]
    bad = validate(new, P, pts)
    for b in bad:
        print('INVALID', *b)
    print(area, ': migrated', len(moved), 'coordinates;', len(pts), 'points checked;', len(bad), 'invalid')
    if '--preview' in sys.argv:
        out = sys.argv[sys.argv.index('--preview') + 1]
        preview(new, P, c.result(), out, debug='--debug' in sys.argv)
    if '--apply' in sys.argv:
        if bad and '--force' not in sys.argv:
            raise SystemExit('not applied: fix invalid points first')
        Image.fromarray(c.result(), 'RGB').save(A / new['image'], optimize=True)
        (A / 'data/maps.json').write_text(json.dumps(M, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        (A / 'data/quests.json').write_text(json.dumps(Q, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        site = getattr(mod, 'SITE', None)
        if site:
            p = ROOT / 'tools/v51_environment_sites.json'
            sites = json.loads(p.read_text(encoding='utf-8'))
            sites[area].update(site)
            p.write_text(json.dumps(sites, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print('applied')


def preview(a, P, ground, out, debug=False):
    from PIL import ImageDraw
    im = Image.fromarray(ground).convert('RGBA')
    for pr in sorted(a['props'], key=lambda p: (P[p['type']].get('layer') != 'floor', p['y'])):
        t = Image.open(A / P[pr['type']]['image']).convert('RGBA')
        im.alpha_composite(t, (int(pr['x'] - t.width / 2), int(pr['y'] - t.height)))
    for t in a.get('elevationPlatforms', []):
        b = Image.open(A / t['image']).convert('RGBA'); im.alpha_composite(b, (int(t['x'] - 20), int(t['y'] - 40)))
    if debug:
        d = ImageDraw.Draw(im)
        for r in a['walls']:
            d.rectangle([r[0], r[1], r[0] + r[2], r[1] + r[3]], outline=(255, 0, 0, 255))
        for pr in a['props']:
            q = P[pr['type']]
            if q.get('cw', 0) > 0:
                d.rectangle([pr['x'] - q['cw'] / 2, pr['y'] - q['ch'], pr['x'] + q['cw'] / 2, pr['y']], outline=(255, 0, 255, 255))
    im.convert('RGB').save(out)
