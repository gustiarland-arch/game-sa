"""Pratinjau time-lapse dunia hidup: membaca quests.json + maps.json dan memutar satu hari (06:00-02:00) di satu area.
Meniru WorldClock.light, jadwal npcPlace (dengan cuaca), wander NPC, dan hewan ambient. Alat bantu desain, BUKAN rekaman game:
oklusi prop disederhanakan dan gerak dipercepat ~60x.
Pemakaian: python3 tools/world_preview.py <assets> <out.mp4> <area>:<hari>[:<x>,<y>] [...]   (x,y = fokus kamera dekat)"""
import sys, os, json, math, random, subprocess, tempfile, shutil
from PIL import Image, ImageDraw, ImageFont

A, OUT = sys.argv[1], sys.argv[2]
W, H, FPS, MIN_PER_FRAME = 1280, 720, 30, 2
Q = json.load(open(os.path.join(A, 'data', 'quests.json')))
MAPS = json.load(open(os.path.join(A, 'data', 'maps.json')))['areas']
PROPS = json.load(open(os.path.join(A, 'data', 'props.json')))['props']
FD = '/usr/share/fonts/opentype/inter/'
f_hud, f_big, f_small = ImageFont.truetype(FD + 'Inter-SemiBold.otf', 24), ImageFont.truetype(FD + 'Inter-Bold.otf', 30), ImageFont.truetype(FD + 'Inter-Regular.otf', 18)
_c = {}
def img(p):
    if p not in _c: _c[p] = Image.open(os.path.join(A, p)).convert('RGBA')
    return _c[p]

DAYS = ['Sabtu', 'Minggu', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat']
def weather(day):  # salinan WorldClock.weather
    if day <= 2: return 'cerah'
    M = (1 << 64) - 1
    h = ((day * 2654435761) ^ 0x5bd1e995) & M; h ^= h >> 13; h = (h * 0x5bd1e995) & M; h ^= h >> 15
    if h >= 1 << 63: h -= 1 << 64
    r = h % 100
    return 'hujan' if r < 14 else 'berawan' if r < 34 else 'berangin' if r < 44 else 'cerah'
def mix(a, b, t): t = max(0, min(1, t)); return [a[i] + (b[i] - a[i]) * t for i in range(4)]
def light(m):
    if m < 420: return mix([1, .72, .55, .14], [1, .85, .7, 0], (m - 300) / 120)
    if m < 960: return [1, 1, 1, 0]
    if m < 1080: return mix([1, .78, .5, 0], [1, .6, .32, .18], (m - 960) / 120)
    if m < 1170: return mix([1, .6, .32, .18], [.18, .2, .42, .3], (m - 1080) / 90)
    if m < 1380: return [.11, .14, .32, .32]
    return mix([.11, .14, .32, .32], [.06, .07, .2, .42], (m - 1380) / 120)
def parse(t): h, m = t.split(':'); return int(h) * 60 + int(m)

def place(n, minute, w):  # salinan QuestEngine.npcPlace (tanpa neededByStep)
    pick = None
    for e in n.get('schedule', []):
        if e.get('weather') and w not in e['weather']: continue
        if parse(e['at']) <= minute: pick = e
    if not n.get('schedule') or pick is None: return (n['area'], n['x'], n['y'], n.get('wander', 0))
    if pick.get('hidden'): return None
    return (pick['area'], pick['x'], pick['y'], pick.get('wander', 0))

def blocked_fn(aid):
    m = MAPS[aid]
    rs = [tuple(r) for r in m['walls']] + [(p['x'] - PROPS[p['type']]['cw'] / 2, p['y'] - PROPS[p['type']]['ch'], PROPS[p['type']]['cw'], PROPS[p['type']]['ch'])
          for p in m['props'] if PROPS[p['type']].get('cw', 0) > 0 and PROPS[p['type']].get('ch', 0) > 0]
    def b(x, y):
        x0, y0, x1, y1 = x - 9, y - 6, x + 9, y + 2
        if x0 < 0 or y0 < 0 or x1 > m['w'] or y1 > m['h']: return True
        if any(x0 < rx + rw and x1 > rx and y0 < ry + rh and y1 > ry for (rx, ry, rw, rh) in rs): return True
        return any(((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 < 1 for (cx, cy, rx, ry) in m['ellipses'])
    return b

def render(aid, day, tmpdir, start_idx, focus=None):
    m = MAPS[aid]; w = weather(day); rnd = random.Random(day * 31 + len(aid)); blocked = blocked_fn(aid)
    base = img(m['image']).copy()
    for p in sorted(m['props'], key=lambda p: (PROPS[p['type']].get('layer') != 'floor', p['y'])):
        im = img(PROPS[p['type']]['image']); base.alpha_composite(im, (int(p['x'] - im.width / 2), int(p['y'] - im.height)))
    lamps = [(p['x'], p['y'] - 70) for p in m['props'] if 'lamp' in p['type']]
    if focus:  # kamera mendekat (skala 1,33x seperti di HP)
        camw, camh = 960, 540; cx0 = max(0, min(m['w'] - camw, focus[0] - camw // 2)); cy0 = max(0, min(m['h'] - camh, focus[1] - camh // 2))
    else:
        camw = min(m['w'], int(m['h'] * W / H)); camh = int(camw * H / W)
        cx0 = (m['w'] - camw) // 2; cy0 = max(0, min(m['h'] - camh, m['h'] // 2 - camh // 2 + 60))
    actors = {}; animals = []
    for sp in m.get('animals', []):
        for _ in range(sp.get('n', 1)):
            if 'water' in sp:
                cx, cy, rx, ry = sp['water']; a = rnd.uniform(0, 6.28); r = rnd.uniform(0, .6)
                animals.append({'t': sp['type'], 'x': cx + math.cos(a) * rx * r, 'y': cy + math.sin(a) * ry * r, 'sp': sp, 'tx': None, 'swim': True, 'f': 0})
            else:
                rx, ry, rw, rh = sp['region']
                for _k in range(20):
                    x, y = rx + rnd.uniform(0, rw), ry + rnd.uniform(0, rh)
                    if not blocked(x, y): animals.append({'t': sp['type'], 'x': x, 'y': y, 'sp': sp, 'tx': None, 'swim': False, 'f': 0}); break
    idx = start_idx
    for minute in range(360, 1560, MIN_PER_FRAME):
        night = (minute // 60) % 24 >= 19 or (minute // 60) % 24 < 5
        # NPC
        here = {}
        for n in Q['townNpcs']:
            if n['sprite'] == 'lumi': continue
            pl = place(n, minute, w)
            if pl and pl[0] == aid: here[n['id']] = (n, pl)
        for k in list(actors):
            if k not in here: del actors[k]
        for k, (n, pl) in here.items():
            a = actors.get(k)
            if a is None: a = actors[k] = {'sprite': n['sprite'], 'x': pl[1], 'y': pl[2], 'tx': pl[1], 'ty': pl[2], 'home': pl, 'dir': 0, 'walk': 0, 'name': n['name']}
            if a['home'] != pl: a['home'] = pl; a['tx'], a['ty'] = pl[1], pl[2]
            dx, dy = a['tx'] - a['x'], a['ty'] - a['y']; d = math.hypot(dx, dy)
            if d > 2:
                s = min(d, 14); nx, ny = a['x'] + dx / d * s, a['y'] + dy / d * s
                if not blocked(nx, ny): a['x'], a['y'] = nx, ny; a['walk'] += 1
                else: a['tx'], a['ty'] = a['x'], a['y']
                a['dir'] = (1 if dx < 0 else 2) if abs(dx) > abs(dy) else (3 if dy < 0 else 0)
            elif pl[3] > 0 and rnd.random() < 0.08:
                for _k in range(5):
                    nx, ny = pl[1] + rnd.uniform(-pl[3], pl[3]), pl[2] + rnd.uniform(-pl[3] * .6, pl[3] * .6)
                    if not blocked(nx, ny): a['tx'], a['ty'] = nx, ny; break
            else: a['walk'] = 0
        # hewan (siang saja kecuali kucing / hujan: hanya kucing)
        vis = []
        for an in animals:
            day_only = an['sp'].get('day', not an['t'].startswith('cat'))
            if day_only and (night or (w == 'hujan' and an['t'] != 'duck')): continue
            if an['tx'] is None or math.hypot(an['tx'] - an['x'], an['ty'] - an['y']) < 2:
                if rnd.random() < 0.12:
                    nx, ny = an['x'] + rnd.uniform(-60, 60), an['y'] + rnd.uniform(-40, 40)
                    if an['swim']:
                        cx, cy, rx, ry = an['sp']['water']
                        if ((nx - cx) / rx) ** 2 + ((ny - cy) / ry) ** 2 < .7: an['tx'], an['ty'] = nx, ny
                    else:
                        rx, ry, rw, rh = an['sp']['region']
                        if rx < nx < rx + rw and ry < ny < ry + rh and not blocked(nx, ny): an['tx'], an['ty'] = nx, ny
                an['f'] = 2
            else:
                dx, dy = an['tx'] - an['x'], an['ty'] - an['y']; d = math.hypot(dx, dy); s = min(d, 6 if an['swim'] else 9)
                an['x'] += dx / d * s; an['y'] += dy / d * s; an['left'] = dx < 0; an['f'] = (an['f'] + 1) % 2
            vis.append(an)
        # gambar
        fr = base.copy()
        sh = img('ui/shadow.png')
        draw_list = [(a['y'], 'npc', a) for a in actors.values()] + [(an['y'], 'an', an) for an in vis]
        for _, kind, o in sorted(draw_list, key=lambda t: t[0]):
            if kind == 'npc':
                f = [1, 0, 2, 0][o['walk'] % 4] if o['walk'] else 0
                im = img('characters/%s/walk.png' % o['sprite']).crop((f * 48, o['dir'] * 72, f * 48 + 48, o['dir'] * 72 + 72))
                fr.alpha_composite(sh.resize((30, 8)), (int(o['x'] - 15), int(o['y'] - 4)))
                fr.alpha_composite(im, (int(o['x'] - 24), int(o['y'] - 70)))
            else:
                t = o['t']; fw = 30 if t == 'dog' else 16 if t == 'bird' else 18 if t == 'squirrel' else 24; fh = 14 if t == 'bird' else 22
                fi = (minute // 2) % 2 if o['swim'] else o['f']
                im = img('animals/%s.png' % t).crop((fi * fw, 0, fi * fw + fw, fh))
                if o.get('left'): im = im.transpose(Image.FLIP_LEFT_RIGHT)
                fr.alpha_composite(im, (int(o['x'] - fw / 2), int(o['y'] - fh + 1)))
        L = light(minute)
        if L[3] > 0:
            ov = Image.new('RGBA', fr.size, (int(L[0] * 255), int(L[1] * 255), int(L[2] * 255), int(L[3] * 255)))
            fr.alpha_composite(ov)
        if w == 'berawan': fr.alpha_composite(Image.new('RGBA', fr.size, (140, 148, 168, 34)))
        if night:
            gl = Image.new('RGBA', fr.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(gl)
            for (lx, ly) in lamps:
                for r_, a_ in ((70, 28), (44, 40), (22, 70)): gd.ellipse([lx - r_, ly - r_, lx + r_, ly + r_], fill=(255, 214, 140, a_))
            fr.alpha_composite(gl)
        view = fr.crop((cx0, cy0, cx0 + camw, cy0 + camh)).resize((W, H), Image.NEAREST if camw < W else Image.BILINEAR)
        d = ImageDraw.Draw(view)
        if w == 'hujan':
            for i in range(160):
                x = (i * 97 + minute * 23) % W; y = (i * 53 + minute * 41) % H
                d.line([(x, y), (x - 6, y + 18)], fill=(190, 210, 240, 150), width=1)
        hh = minute % 1440
        hud = '%s • Hari %d • %02d:%02d • %s' % (DAYS[(day - 1) % 7], day, hh // 60, hh % 60, w.capitalize())
        d.rounded_rectangle([20, 18, 30 + f_hud.getlength(hud) + 20, 66], 12, fill=(40, 30, 52, 215))
        d.text((40, 30), hud, font=f_hud, fill=(255, 214, 120))
        d.text((24, 76), MAPS[aid]['name'] + '  •  warga di area ini: %d  •  hewan terlihat: %d' % (len(actors), len(vis)), font=f_small, fill=(251, 243, 238), stroke_width=2, stroke_fill=(40, 30, 52))
        d.text((W - 24, H - 30), 'Pratinjau dari data game (bukan rekaman APK) • 1 detik = 1 jam', font=f_small, fill=(251, 243, 238), anchor='ra', stroke_width=2, stroke_fill=(40, 30, 52))
        view.convert('RGB').save(os.path.join(tmpdir, 'f%05d.jpg' % idx), quality=92); idx += 1
    return idx

tmp = tempfile.mkdtemp(prefix='wp_')
i = 0
for spec in sys.argv[3:]:
    parts = spec.split(':'); foc = tuple(int(v) for v in parts[2].split(',')) if len(parts) > 2 else None
    i = render(parts[0], int(parts[1]), tmp, i, foc)
tmpout = OUT[:-4] + '.part.mp4'
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(tmp, 'f%05d.jpg'), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', tmpout], check=True)
os.replace(tmpout, OUT)
shutil.rmtree(tmp)
print('frame', i, '->', OUT)
