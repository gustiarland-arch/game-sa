"""Validasi jangkauan fisik di peta (BFS kaki karakter, grid 6 px).
Cek: spawn & target pintu bebas, pintu terjangkau, semua titik interaksi quest/side/NPC/examine bisa didekati,
warp tidak masuk tembok, semua gambar ada. Opsional: render overlay collision.
Pemakaian: python3 tools/check_layout.py <android/assets> [out_preview_dir]
"""
import sys, os, json, math
from collections import deque
from PIL import Image, ImageDraw

A = sys.argv[1]; OUT = sys.argv[2] if len(sys.argv) > 2 else None
J = lambda p: json.load(open(os.path.join(A, 'data', p), encoding='utf-8'))
maps, props, quests, book = J('maps.json')['areas'], J('props.json')['props'], J('quests.json'), J('memory_book.json')
errors = []
FW = 18

def rects(area):
    m = maps[area]; rs = [tuple(r) for r in m['walls']]
    for p in m['props']:
        d = props[p['type']]
        if d.get('cw', 0) > 0 and d.get('ch', 0) > 0: rs.append((p['x'] - d['cw'] / 2, p['y'] - d['ch'], d['cw'], d['ch']))
    return rs

CACHE = {}
def blocked(area, x, y):
    if area not in CACHE: CACHE[area] = (rects(area), [tuple(e) for e in maps[area]['ellipses']])
    rs, es = CACHE[area]; m = maps[area]
    x0, y0, x1, y1 = x - FW / 2, y - 6, x + FW / 2, y + 2
    if x0 < 0 or y0 < 0 or x1 > m['w'] or y1 > m['h']: return True
    for (rx, ry, rw, rh) in rs:
        if x0 < rx + rw and x1 > rx and y0 < ry + rh and y1 > ry: return True
    for (cx, cy, rx, ry) in es:
        for (px, py) in ((x0, y0), (x1, y0), (x0, y1), (x1, y1), (x, y)):
            if ((px - cx) / rx) ** 2 + ((py - cy) / ry) ** 2 < 1: return True
    return False

REACH = {}
def reach(area):
    if area in REACH: return REACH[area]
    m = maps[area]; step = 6; seen = set(); q = deque()
    starts = [tuple(m['spawn'])] + [(d['tx'], d['ty']) for a in maps.values() for d in a['doors'] if d['to'] == area]
    for (sx, sy) in starts:
        c = (int(sx // step), int(sy // step))
        if c not in seen and not blocked(area, c[0] * step + 3, c[1] * step + 3): seen.add(c); q.append(c)
    while q:
        cx, cy = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (cx + dx, cy + dy)
            if n in seen or blocked(area, n[0] * step + 3, n[1] * step + 3): continue
            seen.add(n); q.append(n)
    REACH[area] = (seen, step)
    return REACH[area]

def near(area, x, y, r):
    seen, step = reach(area)
    return any(math.hypot(cx * step + 3 - x, cy * step + 3 - y) <= r * 0.85 for (cx, cy) in seen)

def img(p):
    if not os.path.exists(os.path.join(A, p)): errors.append('gambar hilang: ' + p)

for d in props.values(): img(d['image'])
for aid, m in maps.items():
    img(m['image'])
    if blocked(aid, *m['spawn']): errors.append('%s: spawn terhalang' % aid)
    for d in m['doors']:
        if d['to'] not in maps: errors.append('%s: pintu %s ke area tak dikenal' % (aid, d['id'])); continue
        if blocked(d['to'], d['tx'], d['ty']): errors.append('%s: target pintu %s terhalang' % (aid, d['id']))
        x, y, w, h = d['rect']
        seen, step = reach(aid)
        if not any(cx * step + 3 - 9 < x + w and cx * step + 3 + 9 > x and cy * step + 3 - 6 < y + h and cy * step + 3 + 2 > y for (cx, cy) in seen):
            errors.append('%s: pintu %s tidak terjangkau' % (aid, d['id']))
    for e in m['examine']:
        if not near(aid, e['x'], e['y'], e.get('r', 56)): errors.append('%s: examine %s tidak terjangkau' % (aid, e['id']))

def areas_for(a):
    return ['arland_room', 'sofia_room'] if a == '$ROOM' else [a]

def check_cine(cmds, cur, where):
    """posisi akhir pemain/pasangan setelah cutscene harus bebas & terjangkau (posisi di tengah cutscene boleh di atas kasur dll.)."""
    if not cur: return
    for who in ('player', 'partner'):
        for route in ('arland', 'sofia'):
            last = None
            for c in cmds:
                if c.get('route') not in (None, route) or c.get('who', 'player') != who: continue
                if c['c'] == 'move': last = (c.get('path') or [c.get('to')])[-1] if c.get('path') else c.get('to')
                elif c['c'] == 'place': last = (c['x'], c['y'])
            if last is None: continue
            ars = [a for a in cur if a in (route + '_room',) or not a.endswith('_room')] or cur
            for ar in ars:
                if blocked(ar, last[0], last[1]) or not near(ar, last[0], last[1], 30):
                    errors.append('cutscene %s: posisi akhir %s (%s) terhalang di %s: %s' % (where, who, route, ar, last))

def check_actions(acts, where, cur=None):
    for ac in acts:
        if ac.get('do') == 'warp':
            for ar in areas_for(ac['area']):
                if blocked(ar, ac['x'], ac['y']): errors.append('warp terhalang %s di %s' % (ar, where))
            cur = areas_for(ac['area'])
        if ac.get('do') == 'cine': check_cine(ac['cmds'], cur, where)
        if ac.get('do') == 'if':
            check_actions(ac.get('then', []), where, cur); check_actions(ac.get('else', []), where, cur)

for s in quests['steps']:
    for it in s.get('interactables', []):
        if 'sprite' in it: img(it['sprite']['image'])
        for ar in areas_for(it['area']):
            if not near(ar, it['x'], it['y'], it.get('r', 64)): errors.append('step %s: %s (%s) tidak terjangkau' % (s['id'], it['id'], ar))
        check_actions(it['actions'], s['id'], areas_for(it['area']))
    for n in s.get('npcs', []):
        if blocked(n['area'], n['x'], n['y']): errors.append('npc pasangan terhalang di step %s' % s['id'])
        if not near(n['area'], n['x'], n['y'], 60): errors.append('npc pasangan tak terjangkau di step %s' % s['id'])
    if 'enterArea' in s: check_actions(s['enterArea']['actions'], s['id'], areas_for(s['enterArea']['area']))
    if 'onStart' in s: check_actions(s['onStart'], s['id'] + ':onStart', areas_for(s['startArea']) if s.get('startArea') else None)
    if 'complete' in s: check_actions(s['complete']['actions'], s['id'])
for it in quests.get('side', []):
    if 'sprite' in it: img(it['sprite']['image'])
    for ar in areas_for(it['area']):
        if not near(ar, it['x'], it['y'], it.get('r', 64)): errors.append('side %s (%s) tidak terjangkau' % (it['id'], ar))
for n in quests.get('townNpcs', []):
    img('characters/%s/walk.png' % n['sprite'])
    if not near(n['area'], n['x'], n['y'], 70): errors.append('NPC %s tidak terjangkau' % n['id'])
    for e in n.get('schedule', []):
        if e.get('hidden'): continue
        if blocked(e['area'], e['x'], e['y']) or not near(e['area'], e['x'], e['y'], 30): errors.append('jadwal %s %s di %s tidak terjangkau' % (n['id'], e['at'], e['area']))
for aid, m in maps.items():
    for sp in m.get('animals', []):
        img('animals/%s.png' % sp['type'])
        if 'region' in sp:
            x, y, w, h = sp['region']; free = sum(1 for i in range(10) for j in range(6) if not blocked(aid, x + w * (i + .5) / 10, y + h * (j + .5) / 6))
            if free < 3: errors.append('region hewan %s di %s hampir seluruhnya terhalang (%d/60 bebas)' % (sp['type'], aid, free))
for e in book['entries']: img(e['icon'])
for i in book['items'].values(): img(i['icon'])

if OUT:
    os.makedirs(OUT, exist_ok=True)
    for aid, m in maps.items():
        bg = Image.open(os.path.join(A, m['image'])).convert('RGBA')
        for p in sorted(m['props'], key=lambda p: (props[p['type']].get('layer') != 'floor', p['y'])):
            im = Image.open(os.path.join(A, props[p['type']]['image'])).convert('RGBA')
            bg.alpha_composite(im, (int(p['x'] - im.width / 2), int(p['y'] - im.height)))
        ov = Image.new('RGBA', bg.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        for (x, y, w, h) in rects(aid): d.rectangle([x, y, x + w, y + h], fill=(255, 0, 0, 50))
        for dr in m['doors']:
            x, y, w, h = dr['rect']; d.rectangle([x, y, x + w, y + h], fill=(0, 80, 255, 140))
        for s in quests['steps']:
            for it in s.get('interactables', []):
                if it['area'] == aid: d.ellipse([it['x'] - 8, it['y'] - 8, it['x'] + 8, it['y'] + 8], fill=(255, 200, 0, 220))
        for n in quests.get('townNpcs', []):
            if n['area'] == aid: d.rectangle([n['x'] - 8, n['y'] - 40, n['x'] + 8, n['y']], outline=(0, 160, 120, 255), width=2)
        bg.alpha_composite(ov); bg.convert('RGB').save(os.path.join(OUT, aid + '.png'))

print('ERRORS (%d):' % len(errors) if errors else 'Layout OK, tanpa error.')
for e in errors: print(' -', e)
sys.exit(1 if errors else 0)
