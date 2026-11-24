"""Membangun 15 peta pixel art + metadata (collision, props, pintu, examine, jangkar) dari satu sumber.
Output: android/assets/maps/*.png, android/assets/props/*.png, tools/build/maps_base.json, tools/build/props.json, tools/build/anchors.json
Pemakaian: python3 tools/build_maps.py
Kunci pintu per-cerita ditambahkan oleh tools/build_content.py.
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from mapkit.ground import Canvas
from mapkit import props as P

ROOT = os.path.join(os.path.dirname(__file__), '..')
ASSETS = os.path.join(ROOT, 'android', 'assets')
BUILD = os.path.join(os.path.dirname(__file__), 'build')
os.makedirs(BUILD, exist_ok=True)
os.makedirs(os.path.join(ASSETS, 'maps'), exist_ok=True)
os.makedirs(os.path.join(ASSETS, 'props'), exist_ok=True)

PROPDEFS = {}   # nama -> {image, cw, ch, layer}
SAVED = set()

def L(route_lines):
    """examine lines: {'arland': [(speaker, emo, text)], 'sofia': [...]} -> format json"""
    return {r: [{'s': s, 'e': e, 't': t} for (s, e, t) in v] for r, v in route_lines.items()}

def both(s_a, t_a, s_s, t_s, e_a='neutral', e_s='neutral'):
    return L({'arland': [(s_a, e_a, t_a)], 'sofia': [(s_s, e_s, t_s)]})

def narr(t):
    return L({'arland': [('narrator', 'neutral', t)], 'sofia': [('narrator', 'neutral', t)]})


class Map:
    def __init__(self, id, name, w, h, music='town', ambient=None, seed=1):
        self.id, self.name, self.w, self.h, self.music, self.ambient = id, name, w, h, music, ambient
        self.c = Canvas(w, h, seed)
        self.props, self.walls, self.ellipses, self.doors, self.examine, self.water = [], [], [], [], [], []
        self.anchors = {}
        self.gates = []
        self.spawn = (w // 2, h // 2)

    # ---------- props
    def _def(self, name, im, cw, ch, layer='sort'):
        if name not in SAVED:
            im.save(os.path.join(ASSETS, 'props', name + '.png')); SAVED.add(name)
        PROPDEFS[name] = {'image': 'props/' + name + '.png', 'cw': cw, 'ch': ch, 'layer': layer}

    def place(self, name, x, y, shadow=True, collide=True, variant=None, **kw):
        r = P.REG[name]
        pname = name if not (variant or kw) else name + '_' + (variant or '_'.join(str(v) for v in kw.values()))
        im = P.render(name, **kw)
        self._def(pname, im, r['cw'] if collide else 0, r['ch'] if collide else 0, r['layer'])
        if shadow and r['shadow']:
            rx, ry = r['shadow']; self.c.shadow(x, y - 2, rx, ry)
        self.props.append({'type': pname, 'x': x, 'y': y})
        return im

    def building(self, name, x, base, **kw):
        im, (drx, dry) = P.building(**kw)
        cw = im.width - 20; ch = int(im.height * 0.42)
        self._def(name, im, cw, ch)
        self.c.shadow(x + 6, base - 2, im.width / 2 + 4, 12, 0.8)
        self.props.append({'type': name, 'x': x, 'y': base})
        return (x - im.width // 2 + drx, base)   # titik pintu absolut (tengah, dasar)

    # ---------- collision & navigasi
    def wall(self, x, y, w, h): self.walls.append([int(x), int(y), int(w), int(h)])

    def block(self, mask, keep=None, cell=16):
        """Ubah mask (mis. air) menjadi kotak collision grid; 'keep' = area tetap bisa dilewati (jembatan)."""
        import numpy as np
        mk = mask & ~keep if keep is not None else mask
        H, W = mk.shape
        for gy in range(0, H, cell):
            run = None
            for gx in range(0, W + cell, cell):
                full = gx < W and mk[gy:gy + cell, gx:gx + cell].mean() > 0.5
                if full and run is None: run = gx
                if not full and run is not None:
                    self.wall(run, gy, gx - run, min(cell, H - gy)); run = None
    def ell(self, cx, cy, rx, ry): self.ellipses.append([int(cx), int(cy), int(rx), int(ry)])

    def border(self, t=20, gaps=None):
        """Tepi peta terhalang kecuali celah keluar. gaps: {'left': [(y0,y1)], 'right': [...], 'top': [(x0,x1)], 'bottom': [...]}"""
        gaps = gaps or {}
        def seg(lo, hi, gl):
            pts = [lo] + [v for g in sorted(gl) for v in g] + [hi]
            return [(pts[i], pts[i + 1]) for i in range(0, len(pts), 2)]
        for a, b in seg(0, self.h, gaps.get('left', [])): self.wall(0, a, t, b - a)
        for a, b in seg(0, self.h, gaps.get('right', [])): self.wall(self.w - t, a, t, b - a)
        for a, b in seg(0, self.w, gaps.get('top', [])): self.wall(a, 0, b - a, t)
        for a, b in seg(0, self.w, gaps.get('bottom', [])): self.wall(a, self.h - t, b - a, t)

    def door(self, id, rect, label, to, tx, ty, dir='down', route=None, routeText=None):
        d = {'id': id, 'rect': [int(v) for v in rect], 'label': label, 'to': to, 'tx': int(tx), 'ty': int(ty), 'dir': dir}
        if route: d['route'] = route; d['routeText'] = routeText or 'Pintu ini terkunci.'
        self.doors.append(d)

    def house_door(self, id, door_pt, label, to, tx, ty, route=None, routeText=None):
        x, b = door_pt
        self.door(id, (x - 22, b - 4, 44, 16), label, to, tx, ty, 'down', route, routeText)
        return (x, b + 30)

    def exam(self, id, x, y, label, lines, r=56, when=None):
        e = {'id': id, 'x': int(x), 'y': int(y), 'label': label, 'r': r, 'lines': lines}
        if when: e['when'] = when
        self.examine.append(e)

    def anchor(self, name, x, y): self.anchors[name] = [int(x), int(y)]

    def nogo_mask(self, *masks, pad=36):
        """Area terlarang untuk dekorasi: mask yang diberikan + pintu + jangkar + collision yang ada."""
        import numpy as np
        ng = np.zeros((self.h, self.w), bool)
        for mk in masks: ng |= mk
        for d in self.doors:
            x, y, w, h = d['rect']; self.c.rect(ng, x - 60, y - 40, w + 120, h + 120)
        for (x, y) in self.anchors.values(): self.c.ellipse(ng, x, y, 70, 60)
        for p in self.props:
            dfn = PROPDEFS[p['type']]
            self.c.rect(ng, p['x'] - max(30, dfn['cw'] / 2 + pad / 2), p['y'] - max(20, dfn['ch'] + 10), max(60, dfn['cw'] + pad), max(30, dfn['ch'] + 26))
        sx, sy = self.spawn; self.c.ellipse(ng, sx, sy, 80, 60)
        return ng

    def scatter(self, kinds, n, nogo, region=None, seed=0, tries=40):
        import random as R
        rng = R.Random(seed + len(self.props) * 7)
        x0, y0, x1, y1 = region or (40, 60, self.w - 40, self.h - 30)
        placed = 0
        for _ in range(n * tries):
            if placed >= n: break
            x, y = rng.randint(int(x0), int(x1)), rng.randint(int(y0), int(y1))
            k = rng.choice(kinds)
            r = P.REG[k]
            hw = max(16, r['cw'] / 2 + 8)
            if nogo[max(0, y - 30):min(self.h, y + 8), max(0, int(x - hw)):min(self.w, int(x + hw))].any(): continue
            self.place(k, x, y)
            self.c.rect(nogo, x - hw - 30, y - 50, hw * 2 + 60, 80)
            placed += 1
        return placed

    def ground_decor(self, nogo, patches=30, grass=40, seed=0, cols=None):
        import random as R
        rng = R.Random(seed)
        for _ in range(patches):
            x, y = rng.randint(30, self.w - 30), rng.randint(30, self.h - 30)
            if nogo[y, x]: continue
            self.c.flower_patch(x, y, rng.randint(14, 34), cols=cols or ('#ffffff', '#ffe28a', '#f7b6cf', '#c9b6ef'), nogo=nogo)
        for _ in range(grass):
            x, y = rng.randint(30, self.w - 30), rng.randint(30, self.h - 30)
            if nogo[y, x]: continue
            self.c.tall_grass(x, y, rng.randint(10, 22), nogo=nogo)

    def tree_line(self, kinds, sides='ltrb', step=70, inset=26, seed=0, skip=()):
        """Barisan pohon di tepi peta (di luar area jalan) agar peta terasa tertutup alami."""
        import random as R
        rng = R.Random(seed)
        def ok(x, y): return not any(abs(x - sx) < 110 and abs(y - sy) < 140 for (sx, sy) in skip)
        if 't' in sides:
            for x in range(40, self.w - 20, step):
                if ok(x, inset + 60): self.place(rng.choice(kinds), x + rng.randint(-12, 12), inset + 50 + rng.randint(-8, 8))
        if 'b' in sides:
            for x in range(40, self.w - 20, step):
                if ok(x, self.h - 4): self.place(rng.choice(kinds), x + rng.randint(-12, 12), self.h - 6)
        if 'l' in sides:
            for y in range(140, self.h - 40, step + 10):
                if ok(14, y): self.place(rng.choice(kinds), 14 + rng.randint(-6, 6), y + rng.randint(-10, 10))
        if 'r' in sides:
            for y in range(140, self.h - 40, step + 10):
                if ok(self.w - 14, y): self.place(rng.choice(kinds), self.w - 14 + rng.randint(-6, 6), y + rng.randint(-10, 10))

    def save(self):
        self.c.to_image().save(os.path.join(ASSETS, 'maps', self.id + '.png'), optimize=True)
        return {'name': self.name, 'image': 'maps/' + self.id + '.png', 'w': self.w, 'h': self.h, 'music': self.music,
                'ambient': self.ambient, 'spawn': list(self.spawn), 'walls': self.walls, 'ellipses': self.ellipses,
                'props': self.props, 'doors': self.doors, 'examine': self.examine, 'water': self.water, 'gates': self.gates}


# ======================================================================== INTERIOR
def interior(id, name, wall_cols, floor='wood', floor_col='#b98a5e', w=960, h=640, seed=1, music='town', windows=(240, 720), ambient=None):
    m = Map(id, name, w, h, music, ambient, seed)
    c = m.c
    fm = c.rect(c.mask(), 0, 224, w, h - 224)
    if floor == 'wood': c.wood_floor(fm, base=floor_col)
    elif floor == 'tiles': c.tiles(fm, *floor_col) if isinstance(floor_col, tuple) else c.tiles(fm)
    c.wallpaper(0, 0, w, 224, **wall_cols)
    for wx in windows:
        c.window(wx - 40, 52, 80, 92)
        c.sunbeam(wx - 50, 226, 90, 150, 0.08)
    c.fill(c.rect(c.mask(), 0, 0, 12, h), '#6b4e5a'); c.fill(c.rect(c.mask(), w - 12, 0, 12, h), '#6b4e5a')
    c.fill(c.rect(c.mask(), 0, h - 10, w, 10), '#6b4e5a')
    c.fill(c.rect(c.mask(), 0, 224, w, 4), '#5a3e48')
    m.wall(0, 0, w, 228); m.wall(0, 0, 14, h); m.wall(w - 14, 0, 14, h); m.wall(0, h - 12, w, 12)
    return m

def room_door(m, x, to, tx, ty, label, id=None):
    m.place('door', x, 226, shadow=False, collide=False)
    m.door(id or (m.id + '_out'), (x - 30, 222, 60, 14), label, to, tx, ty, 'down')
    return (x, 270)


maps = {}
anchors = {}

def done(m):
    maps[m.id] = m.save(); anchors[m.id] = m.anchors
    print('peta', m.id, m.w, 'x', m.h, 'props', len(m.props))

# ------------------------------------------------------------------------ Kamar Arland
m = interior('arland_room', 'Kamar Arland', dict(base='#c9d3e6', stripe='#bcc7dd', motif='#e2e8f3', panel='#8e9cbf', trim='#4f5878'), floor_col='#b98a5e', seed=11)
m.spawn = room_door(m, 480, 'plaza', 0, 0, 'Keluar ke Plaza')  # tujuan diisi ulang setelah plaza dibuat
m.place('bed_blue', 860, 352, shadow=False); m.place('desk', 300, 300, shadow=False); m.place('bookshelf', 130, 300, shadow=False)
m.place('wardrobe', 620, 300, shadow=False); m.place('plant', 40, 290); m.place('plant_big', 920, 610)
m.place('rug_rect', 480, 500, shadow=False, collide=False); m.place('poster', 380, 130, shadow=False, collide=False)
m.place('wall_clock', 560, 70, shadow=False, collide=False); m.place('frame_photo', 860, 150, shadow=False, collide=False)
m.place('floor_lamp', 760, 330); m.place('crate', 60, 610); m.place('sofa', 200, 610, shadow=False, variant='a')
m.place('plant', 720, 300); m.place('spice_shelf', 130, 160, shadow=False, collide=False, variant='books'); m.place('frame_photo', 700, 150, shadow=False, collide=False, variant='a2')
m.place('tv', 760, 600, shadow=False); m.place('barrel', 560, 616)
m.anchor('phone', 330, 322); m.anchor('desk_front', 300, 330); m.anchor('gift_table', 262, 330); m.anchor('shelf', 130, 324); m.anchor('bed', 830, 380)
m.anchor('center', 480, 460); m.anchor('door_in', 480, 270)
m.exam('a_window', 240, 250, 'Jendela', both('arland', 'Langitnya cerah. Hari yang pas buat keluar.', 'sofia', 'Dari sini kelihatan atap rumahku.'))
m.exam('a_clock', 560, 248, 'Jam dinding', both('arland', 'Jamnya selalu lima menit lebih cepat. Biar nggak telat.', 'sofia', 'Jamnya lebih cepat lima menit. Khas Arland.'))
m.exam('a_poster', 380, 250, 'Poster', both('arland', 'Poster galaksi. Dulu kubeli karena warnanya mirip langit sore.', 'sofia', 'Poster bintang... dia memang suka langit.'))
m.exam('a_frame', 860, 250, 'Foto pemandangan', both('arland', 'Foto bukit pertamaku. Miring sedikit, tapi aku suka.', 'sofia', 'Foto buatan Arland. Miringnya justru lucu.'))
done(m)

# ------------------------------------------------------------------------ Kamar Sofia
m = interior('sofia_room', 'Kamar Sofia', dict(base='#f2d7df', stripe='#ebc9d3', motif='#fbeef2', panel='#d6a9b7', trim='#8a5a6a'), floor_col='#c49a72', seed=12)
m.spawn = room_door(m, 480, 'plaza', 0, 0, 'Keluar ke Plaza')
m.place('bed_pink', 100, 352, shadow=False); m.place('vanity', 340, 300, shadow=False); m.place('bookshelf', 830, 300, shadow=False, variant='s', seed=7)
m.place('desk', 650, 300, shadow=False, variant='s', laptop=False); m.place('plant_big', 920, 300); m.place('plant', 40, 610)
m.place('rug_pink', 480, 500, shadow=False, collide=False); m.place('frame_photo', 640, 140, shadow=False, collide=False)
m.place('wall_clock', 380, 70, shadow=False, collide=False); m.place('sofa', 700, 600, shadow=False)
m.place('wardrobe', 520, 300, shadow=False, variant='s'); m.place('plant', 220, 300); m.place('floor_lamp', 880, 600); m.place('poster', 200, 120, shadow=False, collide=False, variant='s')
m.place('flowerbed', 520, 610, variant='in'); m.place('crate', 300, 616)
m.place('book_pile', 760, 340, shadow=False, collide=False, variant='sr', seed=9); m.place('candle', 300, 270, shadow=False, collide=False)
m.anchor('phone', 690, 322); m.anchor('desk_front', 650, 330); m.anchor('gift_table', 340, 330); m.anchor('shelf', 830, 324); m.anchor('bed', 130, 380)
m.anchor('wardrobe', 340, 330); m.anchor('center', 480, 460); m.anchor('door_in', 480, 270); m.anchor('corner', 760, 560)
m.exam('s_window', 720, 250, 'Jendela', both('arland', 'Cahaya sore masuk ke kamar Sofia.', 'sofia', 'Cahaya pagi masuk pelan-pelan. Rasanya tenang.', 'neutral', 'senyum'))
m.exam('s_vanity', 340, 330, 'Meja rias', both('arland', 'Rapi sekali. Beda dengan mejaku.', 'sofia', 'Jepit hijab favoritku ada di sini.'), when={'notSteps': ['C02_SOFIA_OUTFIT']})
m.exam('s_sofa', 700, 624, 'Sofa', both('arland', 'Sofa empuk. Pasti tempat Sofia membaca.', 'sofia', 'Tempat favorit untuk membaca sampai lupa waktu.'))
m.exam('s_frame', 640, 250, 'Foto', both('arland', 'Foto taman bunga. Siapa yang memotretnya?', 'sofia', 'Foto taman bunga dari jalan-jalan dulu.'))
done(m)

# ------------------------------------------------------------------------ Plaza Kota (hub)
m = Map('plaza', 'Plaza Kota', 1920, 1280, 'town', 'petals', seed=21)
c = m.c
c.grass(c.rect(c.mask(), 0, 0, m.w, m.h))
pl = c.rect(c.mask(), 300, 500, 1320, 420, r=60)
for x in (360, 960, 1560): c.rect(pl, x - 34, 420, 68, 90)
c.rect(pl, 0, 650, 320, 110); c.rect(pl, 1600, 650, 320, 110)
c.rect(pl, 900, 900, 120, 380)
c.cobble(pl)
c.dirt(c.poly_path(c.mask(), [(360, 300), (300, 200), (520, 120), (960, 150), (1400, 120), (1620, 200), (1560, 300)], 34))
fx, fy = 960, 800
m.place('fountain', fx, fy, shadow=False); m.ell(fx, fy - 46, 108, 46)
m.water.append({'cx': fx, 'cy': fy - 50, 'rx': 92, 'ry': 34})
dA = m.building('bld_arland_house', 360, 430, w=250, roof='#6f86c2', wall='#eef1f7', trim='#56607e', door=0.5, windows=(0.15, 0.85), seed=1)
dS = m.building('bld_sofia_house', 960, 430, w=260, roof='#d4799a', wall='#fbe9ee', trim='#8a5a6a', style='wood', door=0.5, windows=(0.15, 0.85), seed=2)
dC = m.building('bld_cafe', 1560, 430, w=280, roof='#9b80bd', wall='#fbe9dc', trim='#6b4e5a', door=0.5, windows=(0.14, 0.86), sign='KAFE SENJA', awning=('#f2a9c4', '#ffffff'), glow=True, seed=3)
for t, x, y in [('tree_cherry', 120, 420), ('tree_cherry', 1800, 420), ('tree_green', 660, 360), ('tree_green', 1260, 360), ('tree_pine', 60, 200), ('tree_pine', 1860, 200),
                ('tree_cherry', 180, 1180), ('tree_green', 380, 1240), ('tree_cherry', 1740, 1180), ('tree_green', 1540, 1240), ('tree_green', 120, 980), ('tree_green', 1800, 980),
                ('tree_pine', 760, 120), ('tree_pine', 1160, 120), ('tree_cherry', 660, 1150), ('tree_cherry', 1260, 1150)]:
    m.place(t, x, y)
for x in (420, 760, 1160, 1500):
    m.place('lamp', x, 506)
for x in (420, 680, 1240, 1500): m.place('lamp', x, 930)
for x, y in [(560, 580), (1360, 580)]: m.place('bench', x, y)
m.place('bench', 760, 870); m.place('bench', 1160, 870)
for x, y in [(520, 960), (1400, 960), (240, 560), (1680, 560), (640, 470), (1280, 470)]: m.place('flowerbed', x, y)
for x, y in [(80, 640), (80, 780), (1840, 640), (1840, 780), (840, 1220), (1080, 1220)]: m.place('bush', x, y)
m.place('mailbox', 470, 452); m.place('mailbox', 1080, 452); m.place('bicycle', 230, 470)
m.place('cafe_umbrella_table', 1760, 560); m.place('notice_board', 1300, 470)
m.place('mural', 420, 700)
m.place('signpost', 260, 640, variant='w', label='TAMAN'); m.place('signpost', 1660, 640, variant='e', label='JALAN')
m.place('signpost', 1060, 1180, variant='s', label='DANAU')
m.border(gaps={'left': [(660, 750)], 'right': [(660, 750)], 'bottom': [(905, 1015)]})
m.door('plaza_to_park', (0, 660, 18, 90), 'Ke Taman Kota', 'taman_kota', 1880, 700, 'left')
m.door('plaza_to_street', (1902, 660, 18, 90), 'Ke Jalan Kota', 'jalan_kota', 40, 600, 'right')
m.door('plaza_to_lake', (905, 1262, 110, 18), 'Ke Tepi Danau', 'riverside', 960, 60, 'down')
pA = m.house_door('door_arland_house', dA, 'Rumah Arland', 'arland_room', 480, 270, route='arland', routeText='Rumah Arland. Nanti saja mampir bareng dia.')
pS = m.house_door('door_sofia_house', dS, 'Rumah Sofia', 'sofia_room', 480, 270, route='sofia', routeText='Rumah Sofia. Mengetuk pintunya nanti saja.')
pC = m.house_door('door_cafe', dC, 'Kafe Senja', 'cafe', 480, 270)
m.spawn = (960, 640)
m.anchor('meet', 1040, 620); m.anchor('meet_partner', 1090, 600); m.anchor('bench_book', 1160, 890); m.anchor('mural', 420, 716)
m.anchor('front_arland', *pA); m.anchor('front_sofia', *pS); m.anchor('front_cafe', *pC); m.anchor('notice', 1300, 490)
m.anchor('fountain_front', 960, 830); m.anchor('center', 960, 640); m.anchor('behind_houses', 960, 200); m.anchor('bench_w', 560, 600)
m.anchor('west_exit', 60, 705); m.anchor('east_exit', 1860, 705); m.anchor('south_exit', 960, 1220)
m.exam('fountain', 960, 836, 'Air mancur', both('arland', 'Suara airnya bikin plaza terasa adem.', 'sofia', 'Aku suka duduk di sini sambil membaca.', 'neutral', 'senyum'))
m.exam('notice', 1300, 492, 'Papan pengumuman', narr('Papan pengumuman: "Festival Lentera di Taman Kota, segera!" dan "Dicari: kucing oranye bernama Mochi."'))
m.exam('bike', 230, 490, 'Sepeda', both('arland', 'Sepedaku. Bannya perlu dipompa.', 'sofia', 'Sepeda Arland. Keranjangnya muat buku, nih.'))
m.exam('behind', 960, 210, 'Jalan setapak', both('arland', 'Jalan kecil di belakang rumah-rumah. Dulu tempat main petak umpet.', 'sofia', 'Jalan setapak rahasia. Sepi dan sejuk.'))
behind = c.poly_path(c.mask(), [(360, 300), (300, 200), (520, 120), (960, 150), (1400, 120), (1620, 200), (1560, 300)], 60)
ng = m.nogo_mask(pl, behind, c.rect(c.mask(), 60, 300, 1800, 160))
m.tree_line(['tree_green', 'tree_cherry', 'tree_pine', 'tree_green'], sides='lrb', skip=[(0, 705), (1920, 705), (960, 1280)], seed=3)
m.scatter(['bush', 'bush_plain', 'rock', 'mushrooms', 'flowerbed', 'tree_green', 'tree_cherry'], 26, ng, seed=5)
m.ground_decor(ng, patches=46, grass=60, seed=7)
done(m)

# ------------------------------------------------------------------------ Jalan Kota
m = Map('jalan_kota', 'Jalan Kota', 2048, 1024, 'town', 'petals', seed=31)
c = m.c
c.grass(c.rect(c.mask(), 0, 0, m.w, m.h))
road = c.rect(c.mask(), 0, 560, m.w, 150)
c.cobble(road, base='#a89ca8', grout='#7d7287', hl='#c3b8c4', sw=(16, 26), sh=13)
walk = c.rect(c.mask(), 0, 470, m.w, 90); c.rect(walk, 0, 710, m.w, 70)
c.cobble(walk, base='#e1d4c4', grout='#b5a594', sw=(18, 18), sh=18)
for x in range(40, m.w, 120): c.fill(c.rect(c.mask(), x, 632, 60, 6), '#f1e8d8')
dF = m.building('bld_florist', 520, 480, w=270, roof='#7fb88f', wall='#fff4ea', trim='#5f7f6a', door=0.5, windows=(0.14, 0.86), sign='TOKO BUNGA MELATI', awning=('#8fd1a8', '#ffffff'), glow=True, seed=4)
dR = m.building('bld_arcade', 1110, 480, w=300, roof='#5a5aa8', wall='#e9e2f6', trim='#4a3f6e', style='brick', door=0.5, windows=(0.12, 0.88), sign='ARCADE BINTANG', sign_col='#2e2c5a', awning=('#ffd86b', '#5a5aa8'), glow=True, seed=5)
m.building('bld_bakery', 1640, 480, w=240, roof='#d79a5f', wall='#fbeedd', trim='#8a5a3c', door=0.5, windows=(0.15, 0.85), sign='ROTI HANGAT', sign_col='#8a5a3c', awning=('#f6c98d', '#ffffff'), seed=6)
for x in (230, 820, 1400, 1900): m.place('tree_green' if x % 3 else 'tree_cherry', x, 430)
for x in (340, 740, 900, 1330, 1480, 1800): m.place('lamp', x, 556)
m.place('bus_shelter', 1640, 780); m.place('vending', 1480, 770)
m.place('book_pile', 1560, 800, shadow=False, collide=False, variant='jk', seed=4); m.place('old_mailbox', 1900, 790); m.place('stall_flowers', 700, 780); m.place('bench', 1100, 776)
for x in (180, 380, 980, 1260, 1900): m.place('tree_cherry' if x % 2 else 'tree_green', x, 900)
for x, y in [(100, 830), (560, 960), (1360, 960), (1760, 900), (1990, 820)]: m.place('flowerbed' if x % 3 else 'bush', x, y)
m.place('crate', 1810, 500); m.place('barrel', 1840, 504); m.place('signpost', 1960, 520, variant='e', label='PERUMAHAN')
m.border(gaps={'left': [(560, 700)], 'right': [(560, 700)]})
m.door('street_to_res', (2030, 560, 18, 140), 'Ke Distrik Perumahan', 'perumahan', 60, 670, 'right')
m.door('street_to_plaza', (0, 560, 18, 140), 'Ke Plaza', 'plaza', 1870, 705, 'left')
pF = m.house_door('door_florist', dF, 'Toko Bunga', 'toko_bunga', 480, 270)
pR = m.house_door('door_arcade', dR, 'Arcade', 'arcade', 480, 270)
m.spawn = (120, 620)
m.anchor('front_florist', *pF); m.anchor('front_arcade', *pR); m.anchor('halte', 1640, 800); m.anchor('stall', 700, 800)
m.anchor('bakery', 1640, 512); m.anchor('vending', 1480, 790); m.anchor('bench', 1100, 796); m.anchor('center', 1000, 630); m.anchor('west', 80, 630)
m.exam('bakery', 1640, 512, 'Toko Roti Hangat', both('arland', 'Tutup hari ini. Wangi rotinya masih tercium, sih.', 'sofia', 'Roti kayu manisnya enak. Sayang hari ini tutup.', 'neutral', 'senang'))
m.exam('vending', 1480, 792, 'Mesin minuman', both('arland', 'Teh melati botol. Favorit Sofia.', 'sofia', 'Mesin minuman. Arland selalu pilih kopi susu.'))
ng = m.nogo_mask(road, walk, c.rect(c.mask(), 0, 160, m.w, 330))
m.tree_line(['tree_green', 'tree_cherry', 'tree_pine'], sides='tb', seed=4)
m.scatter(['bush', 'bush_plain', 'flowerbed', 'rock', 'tree_cherry'], 14, ng, region=(40, 790, m.w - 60, m.h - 40), seed=6)
m.ground_decor(ng, patches=30, grass=40, seed=8)
done(m)

# ------------------------------------------------------------------------ Taman Kota
m = Map('taman_kota', 'Taman Kota', 1920, 1408, 'town', 'petals', seed=41)
c = m.c
c.grass(c.rect(c.mask(), 0, 0, m.w, m.h), flowers=0.0028)
pond = c.ellipse(c.mask(), 640, 760, 300, 170); c.ellipse(pond, 860, 860, 160, 110)
stream = c.poly_path(c.mask(), [(1020, 900), (1180, 1040), (1240, 1250), (1260, 1408)], 46)
c.water(pond | stream)
bridge_keep = c.rect(c.mask(), 1140, 1136, 150, 46)
m.block(c.dilate(pond | stream, 2), keep=bridge_keep)
m.water.append({'cx': 640, 'cy': 760, 'rx': 280, 'ry': 150}); m.water.append({'cx': 860, 'cy': 860, 'rx': 140, 'ry': 90})
c.dirt(c.poly_path(c.mask(), [(1920, 705), (1600, 700), (1400, 600), (1200, 470), (900, 380), (560, 360), (300, 460), (220, 700), (320, 1020), (600, 1150), (900, 1180), (1130, 1150)], 52))
c.dirt(c.poly_path(c.mask(), [(1400, 600), (1500, 900), (1420, 1150), (1300, 1180)], 44))
m.place('bridge', 1215, 1192, shadow=False, collide=False, variant='park', w=150, h=64)
m.place('gazebo', 1500, 420); m.place('picnic_blanket', 1520, 1000, shadow=False, collide=False)
for x in (1300, 1700): m.place('hedge', x, 560, variant='tk')
m.place('garden_plot', 1180, 1320, shadow=False, variant='tk', seed=31); m.place('garden_plot', 1260 + 80, 1320, shadow=False, variant='tk2', seed=32)
for t, x, y in [('tree_cherry', 300, 300), ('tree_cherry', 860, 280), ('tree_green', 1180, 300), ('tree_cherry', 1760, 300), ('tree_green', 140, 560),
                ('tree_cherry', 120, 1000), ('tree_green', 420, 1300), ('tree_cherry', 760, 1340), ('tree_green', 1640, 1250), ('tree_cherry', 1820, 1000),
                ('tree_green', 1060, 600), ('tree_autumn', 1700, 700), ('tree_pine', 60, 200), ('tree_pine', 1860, 120), ('tree_autumn', 400, 1060), ('tree_green', 980, 1330)]:
    m.place(t, x, y)
for x, y in [(560, 420), (1000, 470), (360, 640), (1660, 860)]: m.place('bench', x, y)
for x, y in [(700, 520), (1300, 760), (240, 860), (560, 1080), (1700, 560)]: m.place('flowerbed', x, y)
for x, y in [(1260, 520), (1600, 600), (420, 940), (1840, 760), (900, 1060)]: m.place('lamp', x, y)
for x, y in [(860, 560), (380, 380), (1380, 1060), (1560, 1180), (200, 1200)]: m.place('bush', x, y)
for x, y in [(980, 700), (1000, 1000), (380, 720), (430, 880)]: m.place('rock', x, y)
m.place('mushrooms', 180, 1080, shadow=False, collide=False); m.place('mushrooms', 1720, 420, shadow=False, collide=False)
m.border(gaps={'right': [(650, 760)], 'top': [(900, 1020)]})
m.door('park_to_forest', (900, 0, 120, 18), 'Ke Hutan Bisik', 'hutan_bisik', 1280, 1850, 'up')
m.door('park_to_plaza', (1902, 650, 18, 110), 'Ke Plaza', 'plaza', 60, 705, 'right')
m.spawn = (1840, 705)
m.anchor('gazebo', 1500, 470); m.anchor('picnic', 1520, 1060); m.anchor('pond_n', 640, 570); m.anchor('pond_dock', 980, 900); m.anchor('bridge', 1215, 1170)
m.anchor('bench_pond', 360, 660); m.anchor('flowers_w', 240, 880); m.anchor('cat_spot', 380, 400); m.anchor('east', 1840, 705); m.anchor('bench_n', 1000, 490)
m.anchor('rain_bench', 1660, 880); m.anchor('tree_old', 1700, 720)
m.exam('pond', 640, 580, 'Kolam', both('arland', 'Ada ikan koi oranye. Gendut-gendut.', 'sofia', 'Ikan koinya mendekat. Mungkin mengira aku bawa roti.', 'neutral', 'tertawa'))
m.exam('gazebo_e', 1500, 476, 'Gazebo', both('arland', 'Gazebo putih. Tempat orang berteduh kalau hujan.', 'sofia', 'Kalau hujan, gazebo ini penuh orang membaca.'))
m.exam('old_tree', 1700, 724, 'Pohon tua', both('arland', 'Ada ukiran kecil di batangnya: dua bintang.', 'sofia', 'Daunnya mulai jingga. Cantik sekali.'))
paths = c.poly_path(c.mask(), [(1920, 705), (1600, 700), (1400, 600), (1200, 470), (900, 380), (560, 360), (300, 460), (220, 700), (320, 1020), (600, 1150), (900, 1180), (1130, 1150)], 80)
c.poly_path(paths, [(1400, 600), (1500, 900), (1420, 1150), (1300, 1180)], 70)
ng = m.nogo_mask(paths, c.dilate(pond | stream, 14))
m.tree_line(['tree_green', 'tree_cherry', 'tree_pine', 'tree_autumn'], sides='tlb', skip=[(1920, 705), (960, 0)], seed=9)
c.dirt(c.poly_path(c.mask(), [(960, 0), (960, 150)], 60))
m.place('signpost', 1060, 120, variant='n', label='HUTAN')
m.tree_line(['tree_green', 'tree_cherry'], sides='r', skip=[(1920, 705)], seed=10)
m.scatter(['bush', 'flowerbed', 'rock', 'mushrooms', 'tree_cherry', 'tree_green', 'bush_plain'], 30, ng, seed=11)
m.ground_decor(ng, patches=60, grass=70, seed=12)
done(m)

# ------------------------------------------------------------------------ Tepi Danau
m = Map('riverside', 'Tepi Danau', 1920, 1088, 'town', 'fireflies', seed=51)
c = m.c
c.grass(c.rect(c.mask(), 0, 0, m.w, m.h))
lake = c.rect(c.mask(), 0, 740, m.w, 348); c.ellipse(lake, 960, 740, 760, 50)
c.water(lake, shore=14)
c.dirt(c.poly_path(c.mask(), [(960, 0), (960, 200), (700, 420), (500, 620), (300, 660)], 50))
c.dirt(c.poly_path(c.mask(), [(700, 420), (1200, 560), (1500, 620), (1700, 600)], 44))
c.dirt(c.poly_path(c.mask(), [(1220, 560), (1220, 690)], 40))
c.dirt(c.poly_path(c.mask(), [(1700, 600), (1920, 610)], 44))
m.place('bridge', 1220, 872, shadow=False, collide=False, variant='pier', w=80, h=184)
m.block(c.dilate(lake, 3), keep=c.rect(c.mask(), 1186, 680, 68, 186))
m.water.append({'cx': 960, 'cy': 940, 'rx': 900, 'ry': 120})
for t, x, y in [('tree_green', 160, 300), ('tree_cherry', 420, 220), ('tree_green', 1500, 260), ('tree_cherry', 1760, 320), ('tree_pine', 80, 120), ('tree_pine', 1860, 140),
                ('tree_green', 1240, 140), ('tree_cherry', 660, 120), ('tree_autumn', 1700, 520), ('tree_green', 260, 520)]:
    m.place(t, x, y)
m.place('bench', 860, 664); m.place('bench', 1520, 650)
m.place('rowboat', 1110, 820, shadow=False, collide=False, variant='rv'); m.place('pier_post', 1186, 790, shadow=False, collide=False); m.place('pier_post', 1254, 790, shadow=False, collide=False)
m.place('telescope', 1640, 600)
for x, y in [(520, 636), (1100, 640), (1360, 600), (760, 360)]: m.place('lamp', x, y)
for x, y in [(380, 660), (1640, 660), (1060, 330), (560, 420)]: m.place('flowerbed' if x % 2 == 0 else 'bush', x, y)
for x, y in [(100, 650), (1820, 640), (1000, 660)]: m.place('rock', x, y)
m.border(gaps={'top': [(905, 1015)], 'right': [(560, 660)]})
m.door('lake_to_pier', (1902, 560, 18, 100), 'Ke Dermaga Danau', 'dermaga', 70, 425, 'right')
m.door('lake_to_plaza', (905, 0, 110, 18), 'Ke Plaza', 'plaza', 960, 1210, 'up')
m.spawn = (960, 70)
m.anchor('bench', 860, 640); m.anchor('pier_end', 1220, 840); m.anchor('bench_e', 1520, 640); m.anchor('north', 960, 70); m.anchor('reeds', 300, 660)
m.exam('lake', 600, 690, 'Danau', both('arland', 'Airnya tenang. Pantulan langitnya jelas sekali.', 'sofia', 'Danau ini selalu bikin pikiran lebih ringan.', 'neutral', 'senyum'))
paths = c.poly_path(c.mask(), [(960, 0), (960, 200), (700, 420), (500, 620), (300, 660)], 80)
c.poly_path(paths, [(700, 420), (1200, 560), (1500, 620), (1700, 600)], 74); c.poly_path(paths, [(1220, 560), (1220, 700)], 70); c.poly_path(paths, [(1700, 600), (1920, 610)], 80)
ng = m.nogo_mask(paths, c.rect(c.mask(), 0, 600, m.w, 500))
m.tree_line(['tree_green', 'tree_cherry', 'tree_pine'], sides='tlr', skip=[(960, 0)], seed=13)
m.scatter(['bush', 'flowerbed', 'rock', 'tree_green', 'tree_cherry', 'mushrooms'], 18, ng, region=(40, 80, m.w - 40, 600), seed=14)
m.ground_decor(ng, patches=40, grass=60, seed=15)
c.tall_grass(300, 690, 40); c.tall_grass(1700, 690, 40)
done(m)

# ------------------------------------------------------------------------ Kafe Senja
m = interior('cafe', 'Kafe Senja', dict(base='#f3e1cf', stripe='#ecd5c0', motif='#fbf0e4', panel='#b98a74', trim='#6b4e5a'), floor_col='#a8774f', seed=61, windows=(160, 640), music='cafe')
m.spawn = room_door(m, 400, 'plaza', 0, 0, 'Keluar ke Plaza')
m.place('door', 860, 226, shadow=False, collide=False, variant='k')
m.door('cafe_to_kitchen', (830, 222, 60, 14), 'Dapur', 'dapur', 480, 270, 'down')
m.place('counter', 210, 330, shadow=False); m.place('display_case', 380, 316, shadow=False)
m.place('symbol_table', 480, 470, shadow=False); m.place('rug_round', 480, 500, shadow=False, collide=False)
for x, y in [(160, 560), (800, 560), (780, 420), (620, 600)]: m.place('cafe_table', x, y)
m.place('bookshelf', 700, 300, shadow=False, variant='c', seed=9); m.place('plant_big', 40, 300); m.place('plant', 920, 610); m.place('plant', 560, 290)
m.place('frame_photo', 300, 120, shadow=False, collide=False); m.place('wall_clock', 520, 80, shadow=False, collide=False); m.place('poster', 760, 120, shadow=False, collide=False, variant='c')
m.place('plant_big', 920, 300, variant='c'); m.place('cafe_table', 300, 600, variant='c2'); m.place('plant', 40, 610, variant='c'); m.place('sofa', 920 - 60, 470, shadow=False, variant='c')
m.anchor('symbols', 480, 494); m.anchor('counter', 210, 352); m.anchor('barista', 210, 300); m.anchor('table_date', 800, 590); m.anchor('table_date_p', 840, 560)
m.anchor('shelf', 700, 324); m.anchor('door_in', 400, 270); m.anchor('center', 480, 400)
m.exam('cafe_case', 380, 340, 'Etalase kue', both('arland', 'Kue stroberi, cheesecake, dan roti cokelat. Susah memilih.', 'sofia', 'Kue stroberinya kelihatan enak.', 'neutral', 'senang'))
m.exam('cafe_shelf', 700, 324, 'Rak buku kafe', both('arland', 'Ada buku tamu. Banyak tulisan tangan di dalamnya.', 'sofia', 'Rak buku di kafe? Tempat ini makin kusuka.', 'neutral', 'senyum'))
done(m)

# ------------------------------------------------------------------------ Dapur
m = interior('dapur', 'Dapur Kafe', dict(base='#d6efe4', stripe='#c9e7da', motif='#ecf8f2', panel='#8fbfa9', trim='#4f7a68'), floor='tiles', floor_col=('#f3ece4', '#e2d6c8', '#c4b5a5'), seed=71, windows=(700,), music='cafe')
m.spawn = room_door(m, 480, 'cafe', 860, 280, 'Kembali ke Kafe')
m.place('stove', 160, 300, shadow=False); m.place('kitchen_counter', 300, 300, shadow=False); m.place('fridge', 880, 300, shadow=False)
m.place('kitchen_table', 480, 480); m.place('spice_shelf', 220, 150, shadow=False, collide=False); m.place('plant', 40, 300); m.place('plant_big', 920, 610)
m.place('crate', 80, 600); m.place('barrel', 120, 606); m.place('kitchen_counter', 650, 300, shadow=False, variant='b')
m.place('crate', 760, 610, variant='k'); m.place('plant', 40, 610, variant='k'); m.place('rug_rect', 480, 560, shadow=False, collide=False, variant='k')
m.anchor('stove', 160, 324); m.anchor('counter', 320, 324); m.anchor('fridge', 880, 324); m.anchor('table', 480, 510); m.anchor('center', 600, 420); m.anchor('crate', 80, 624)
m.exam('fridge_e', 880, 326, 'Kulkas', both('arland', 'Ada catatan barista: "Silakan pakai bahan seperlunya."', 'sofia', 'Kulkasnya penuh buah. Ada stroberi!', 'neutral', 'senang'))
done(m)

# ------------------------------------------------------------------------ Toko Bunga
m = interior('toko_bunga', 'Toko Bunga Melati', dict(base='#eef6e9', stripe='#e2efdc', motif='#f8fcf5', panel='#9fc29a', trim='#5f7f6a'), floor_col='#c9a27a', seed=81, windows=(200, 760))
m.spawn = room_door(m, 480, 'jalan_kota', 0, 0, 'Keluar ke Jalan')
m.place('flower_shelf', 120, 300, shadow=False); m.place('flower_shelf', 840, 300, shadow=False, variant='b')
m.place('shop_counter', 480, 420, shadow=False); m.place('flower_buckets', 240, 560); m.place('flower_buckets', 720, 560, variant='b')
m.place('plant_big', 620, 300); m.place('plant_big', 340, 300, variant='b'); m.place('rug_round', 480, 520, shadow=False, collide=False, variant='g', c1='#9fc29a', c2='#eef6e9')
m.place('flower_buckets', 480, 616, variant='c'); m.place('plant', 40, 610, variant='f'); m.place('plant', 920, 610, variant='f2'); m.place('stall_flowers', 160, 450, variant='in')
m.place('flowerbed', 800, 450, variant='f')
m.anchor('florist', 480, 380); m.anchor('counter_front', 480, 446); m.anchor('buckets_w', 240, 584); m.anchor('buckets_e', 720, 584); m.anchor('shelf_w', 120, 324); m.anchor('shelf_e', 840, 324)
m.exam('shelf_w_e', 120, 326, 'Rak bunga', both('arland', 'Mawar, melati, krisan. Wanginya campur jadi satu.', 'sofia', 'Melati putih. Wanginya menenangkan.'))
done(m)

# ------------------------------------------------------------------------ Arcade
m = interior('arcade', 'Arcade Bintang', dict(base='#3d3a6e', stripe='#36336a', motif='#ffe28a', panel='#2a2752', trim='#1d1a3e'), floor='tiles', floor_col=('#4a4580', '#3e3a70', '#2e2b5a'), seed=91, windows=(), music='game')
m.spawn = room_door(m, 480, 'jalan_kota', 0, 0, 'Keluar ke Jalan')
for i, (n, x) in enumerate([('arcade_pink', 120), ('arcade_blue', 180), ('arcade_green', 240), ('arcade_pink', 660), ('arcade_blue', 720)]):
    m.place(n, x, 300, shadow=False, variant=str(i) if i >= 3 else None)
m.place('claw_machine', 860, 310, shadow=False); m.place('photobooth', 360, 320, shadow=False)
m.place('prize_shelf', 820, 560, shadow=False); m.place('shop_counter', 640, 560, shadow=False, variant='a')
for i, x in enumerate((90, 150, 210, 270)): m.place(['arcade_green', 'arcade_pink', 'arcade_blue', 'arcade_green'][i], x, 600, shadow=False, variant='b%d' % i)
m.place('sofa', 420, 600, shadow=False, variant='ar'); m.place('vending', 920, 610, variant='ar'); m.place('plant', 560, 300, variant='ar')
for x in (60, 900): m.place('poster', x, 120, shadow=False, collide=False, variant='a' + str(x))
m.anchor('booth', 380, 346); m.anchor('claw', 860, 334); m.anchor('cabinets', 180, 324); m.anchor('prize', 640, 586); m.anchor('keeper', 640, 520); m.anchor('center', 480, 440)
m.exam('cabinet_e', 240, 326, 'Mesin game', both('arland', 'Game balap pesawat. Rekor tertinggi di sini... bukan punyaku.', 'sofia', 'Lampunya kelap-kelip. Ramai sekali.'))
done(m)

# ------------------------------------------------------------------------ Memory Garden
m = Map('memory_garden', 'Memory Garden', 1600, 1200, 'memory', 'sparkles', seed=101)
c = m.c
c.dream(c.rect(c.mask(), 0, 0, m.w, m.h))
p = c.poly_path(c.mask(), [(800, 1140), (800, 900), (790, 700), (810, 520), (800, 400)], 50)
c.poly_path(p, [(790, 760), (640, 700), (480, 730), (330, 760)], 44); c.poly_path(p, [(810, 760), (960, 700), (1120, 730), (1270, 760)], 44)
c.ellipse(p, 800, 720, 130, 74); c.ellipse(p, 270, 760, 96, 60); c.ellipse(p, 1330, 760, 96, 60); c.ellipse(p, 800, 1080, 90, 50)
c.glow_stones(p)
m.place('pedestal_book', 800, 360); m.place('arch_flowers', 800, 330, shadow=False, collide=False)
for x, y in [(240, 300), (1360, 300), (140, 1060), (1460, 1060), (520, 220), (1080, 220)]: m.place('tree_dream', x, y)
for x, y in [(700, 640), (900, 640), (700, 820), (900, 820), (420, 690), (1180, 690), (170, 760), (1430, 760)]: m.place('lantern_post', x, y)
for x, y in [(330, 460), (1270, 460), (700, 1060), (900, 1060), (120, 700), (1480, 700)]: m.place('crystal', x, y)
for x, y in [(400, 1120), (1200, 1120), (640, 260), (960, 260)]: m.place('bush', x, y, variant='d')
m.border()
m.spawn = (800, 1040)
m.anchor('shard1', 270, 770); m.anchor('shard2', 1330, 770); m.anchor('shard3', 800, 1090); m.anchor('portal', 800, 400); m.anchor('center', 800, 700); m.anchor('arrive', 800, 1040)
ng = m.nogo_mask(c.dilate(p, 30))
m.tree_line(['tree_dream', 'tree_dream', 'tree_lantern'], sides='tlrb', step=90, seed=16)
m.scatter(['crystal', 'bush', 'mushrooms', 'tree_dream', 'rock'], 22, ng, seed=17)
m.ground_decor(ng, patches=40, grass=0, seed=18, cols=('#fff3c4', '#ffd1ea', '#c8f0ff', '#e0d4ff'))
m.exam('mg_crystal', 330, 484, 'Kristal', both('arland', 'Kristalnya hangat disentuh. Seperti menyimpan suara tawa.', 'sofia', 'Kalau dilihat dekat, ada bayangan kecil di dalamnya.', 'penasaran', 'penasaran'))
done(m)

# ------------------------------------------------------------------------ Lantern Field
m = Map('lantern_field', 'Lantern Field', 1920, 1280, 'memory', 'fireflies', seed=111)
c = m.c
c.dream(c.rect(c.mask(), 0, 0, m.w, m.h), pal=('#2f4a5e', '#365670', '#3f6380', '#253c4d'), glow=('#ffe9a8', '#ffd27a', '#fff6d6'), dens=0.003)
c.glow_stones(c.poly_path(c.mask(), [(100, 1180), (420, 1000), (760, 900), (960, 700), (960, 420), (1300, 300), (1880, 300)], 44), col='#f3e2b6', rim='#c9a86a')
c.ellipse(c.mask(), 960, 640, 1, 1)
ring = c.ellipse(c.mask(), 960, 640, 210, 130); c.glow_stones(ring, col='#efe0bd', rim='#b89c66')
pos = [(840, 560), (960, 540), (1080, 560), (820, 680), (1100, 680), (960, 740)]
for i, (x, y) in enumerate(pos): m.place('lantern_off', x, y)
for x, y in [(200, 300), (480, 220), (1500, 1000), (1760, 820), (300, 760), (1400, 560), (640, 300), (1700, 140)]: m.place('tree_lantern', x, y)
for x, y in [(560, 1060), (1240, 900), (1600, 420), (380, 520)]: m.place('lantern_post', x, y)
lpath = c.poly_path(c.mask(), [(100, 1180), (420, 1000), (760, 900), (960, 700), (960, 420), (1300, 300), (1880, 300)], 80)
ng = m.nogo_mask(lpath, c.dilate(ring, 40))
m.tree_line(['tree_lantern', 'tree_dream', 'tree_lantern'], sides='tlb', step=86, seed=19, skip=[(1920, 300)])
m.scatter(['tree_lantern', 'crystal', 'bush_plain', 'lantern_post', 'rock'], 26, ng, seed=20)
m.ground_decor(ng, patches=36, grass=50, seed=21, cols=('#ffe9a8', '#ffd27a', '#fff6d6'))
m.border(gaps={'right': [(240, 360)]})
m.door('lantern_to_village', (1902, 240, 18, 120), 'Ke Starfall Village', 'starfall_village', 60, 640, 'right')
m.spawn = (140, 1150)
m.anchor('shrine', 960, 800); m.anchor('ring_center', 960, 640); m.anchor('arrive', 160, 1140); m.anchor('east', 1860, 300); m.anchor('stone_n', 960, 420)
for i, (x, y) in enumerate(pos): m.anchor('lantern%d' % (i + 1), x, y + 24)
done(m)

# ------------------------------------------------------------------------ Star Path
m = Map('star_path', 'Star Path', 2048, 1024, 'star', 'stars', seed=121)
c = m.c
c.starry(c.rect(c.mask(), 0, 0, m.w, m.h))
sp = c.poly_path(c.mask(), [(60, 520), (380, 380), (700, 620), (1020, 420), (1340, 640), (1660, 460), (2048, 520)], 70)
c.glow_stones(sp)
for x, y in [(380, 300), (700, 720), (1020, 330), (1340, 740), (1660, 370)]: m.place('star_stone', x, y)
for x, y in [(200, 760), (560, 200), (900, 860), (1200, 200), (1500, 860), (1850, 220), (260, 220), (1800, 820)]: m.place('crystal', x, y)
ng = m.nogo_mask(c.dilate(sp, 34))
m.scatter(['crystal', 'star_stone', 'crystal', 'rock'], 40, ng, seed=22)
m.ground_decor(ng, patches=0, grass=0, seed=23)
m.border(gaps={'left': [(470, 580)], 'right': [(470, 580)]})
m.door('star_to_village', (2030, 470, 18, 110), 'Ke Starfall Village', 'starfall_village', 60, 640, 'right')
m.spawn = (120, 520)
m.anchor('arrive', 120, 520); m.anchor('stone1', 380, 330); m.anchor('stone2', 700, 750); m.anchor('stone3', 1020, 360); m.anchor('stone4', 1340, 770); m.anchor('stone5', 1660, 400)
m.anchor('compass', 1020, 470); m.anchor('east', 1980, 520)
done(m)

# ------------------------------------------------------------------------ Starfall Village
m = Map('starfall_village', 'Starfall Village', 1920, 1280, 'star', 'stars', seed=131)
c = m.c
c.dream(c.rect(c.mask(), 0, 0, m.w, m.h), pal=('#46407a', '#4f4988', '#5a5496', '#3a3566'), glow=('#fff3c4', '#c8f0ff', '#ffd1ea'), dens=0.0022)
pl = c.rect(c.mask(), 520, 480, 880, 420, r=80); c.rect(pl, 0, 590, 540, 100); c.rect(pl, 1380, 590, 540, 100)
c.glow_stones(pl, col='#d8d2f6', rim='#9a90d6')
for i, (x, kw) in enumerate([(420, dict(roof='#7d6fc4', wall='#e7e0fb')), (960, dict(roof='#c46fa8', wall='#fbe6f4')), (1500, dict(roof='#6fa8c4', wall='#e0f2fb'))]):
    m.building('bld_star_house%d' % i, x, 440, w=220, trim='#4a3f6e', door=0.5, windows=(0.15, 0.85), glow=True, chimney=False, seed=20 + i, **kw)
m.place('pedestal_book', 960, 700, variant='map'); m.anchor('starmap', 960, 726)
for x, y in [(640, 560), (1280, 560), (640, 860), (1280, 860)]: m.place('star_stone', x, y)
for x, y in [(200, 300), (1720, 300), (200, 1080), (1720, 1080), (560, 1160), (1360, 1160)]: m.place('tree_dream', x, y)
for x, y in [(760, 520), (1160, 520), (760, 900), (1160, 900)]: m.place('lantern_post', x, y)
for x, y in [(860, 1000), (1060, 1000)]: m.place('stone_bench', x, y)
ng = m.nogo_mask(c.dilate(pl, 30), c.rect(c.mask(), 260, 200, 1400, 280))
m.tree_line(['tree_dream', 'tree_lantern'], sides='tbr', step=90, seed=24)
m.scatter(['tree_dream', 'crystal', 'bush', 'lantern_post', 'mushrooms'], 24, ng, seed=25)
m.ground_decor(ng, patches=40, grass=30, seed=26, cols=('#fff3c4', '#c8f0ff', '#ffd1ea'))
m.border(gaps={'left': [(590, 690)]})
m.door('village_to_lantern', (0, 590, 18, 100), 'Kembali', 'lantern_field', 1860, 300, 'left')
m.spawn = (80, 640)
m.anchor('arrive', 80, 640); m.anchor('lumi', 1040, 640); m.anchor('bench', 960, 1030); m.anchor('house_mid', 960, 470); m.anchor('center', 960, 760)
done(m)

# ------------------------------------------------------------------------ Eternal Garden
m = Map('eternal_garden', 'Eternal Garden', 1920, 1408, 'tender', 'petals', seed=141)
c = m.c
c.grass(c.rect(c.mask(), 0, 0, m.w, m.h), pal=('#7cc08a', '#8bcc94', '#9bd8a0', '#64a874'), flowers=0.006, flower_cols=('#ffffff', '#ffe28a', '#f7b6cf', '#c9b6ef', '#ffc8a8'))
ep = c.ellipse(c.mask(), 420, 1000, 220, 120); c.water(ep, shore=6); m.block(c.dilate(ep, 2)); m.water.append({'cx': 420, 'cy': 1000, 'rx': 200, 'ry': 100})
c.glow_stones(c.poly_path(c.mask(), [(960, 1408), (960, 1000), (960, 640), (700, 500), (960, 380), (1220, 500), (960, 640)], 60), col='#f6eee2', rim='#d8cbbb')
c.glow_stones(c.ellipse(c.mask(), 960, 470, 200, 110), col='#fbf3ee', rim='#d8cbbb')
m.place('wishing_tree', 960, 420)
m.place('arch_flowers', 960, 1180, shadow=False, collide=False, variant='e'); m.place('arch_flowers', 960, 820, shadow=False, collide=False, variant='e2')
for x, y in [(840, 640), (1080, 640)]: m.place('stone_bench', x, y)
for x, y in [(300, 300), (1620, 300), (200, 700), (1720, 700), (1500, 1100), (1700, 1300), (180, 1300), (640, 200), (1280, 200)]: m.place('tree_cherry', x, y)
for x, y in [(600, 760), (1320, 760), (700, 1100), (1220, 1100), (1500, 520), (420, 520)]: m.place('flowerbed', x, y)
for x, y in [(760, 300), (1160, 300), (1400, 900), (520, 860)]: m.place('lantern_post', x, y)
m.place('gazebo', 1500, 1000, variant='e')
egp = c.poly_path(c.mask(), [(960, 1408), (960, 1000), (960, 640), (700, 500), (960, 380), (1220, 500), (960, 640)], 90)
c.ellipse(egp, 960, 470, 230, 140)
ng = m.nogo_mask(egp, c.dilate(ep, 20))
m.tree_line(['tree_cherry', 'tree_green', 'tree_cherry'], sides='tlrb', step=80, seed=27)
m.scatter(['bush', 'flowerbed', 'tree_cherry', 'mushrooms', 'bush'], 30, ng, seed=28)
m.ground_decor(ng, patches=80, grass=40, seed=29, cols=('#ffffff', '#ffe28a', '#f7b6cf', '#c9b6ef', '#ffc8a8'))
m.border()
m.spawn = (960, 1340)
m.anchor('arrive', 960, 1340); m.anchor('tree', 960, 500); m.anchor('bench', 960, 660); m.anchor('pond', 420, 870); m.anchor('gazebo', 1500, 1040); m.anchor('final', 960, 520)
m.anchor('wish_a', 840, 660); m.anchor('wish_s', 1080, 660)
done(m)


# ======================================================================== v1.2 LOKASI BARU
# ------------------------------------------------------------------------ Distrik Perumahan
m = Map('perumahan', 'Distrik Perumahan', 2048, 1152, 'town', 'petals', seed=151)
c = m.c
c.grass(c.rect(c.mask(), 0, 0, m.w, m.h))
road = c.rect(c.mask(), 0, 600, m.w, 140)
c.cobble(road, base='#a89ca8', grout='#7d7287', hl='#c3b8c4', sw=(16, 26), sh=13)
for x in range(40, m.w, 120): c.fill(c.rect(c.mask(), x, 666, 60, 6), '#f1e8d8')
walk = c.rect(c.mask(), 0, 520, m.w, 80); c.rect(walk, 0, 740, m.w, 70)
for x in (300, 1700): c.rect(walk, x - 30, 800, 60, 140)
c.cobble(walk, base='#e1d4c4', grout='#b5a594', sw=(18, 18), sh=18)
dL = m.building('bld_library', 600, 520, w=400, roof='#5f6f9a', wall='#efe6d6', trim='#4a4f6e', style='brick', door=0.5, windows=(0.12, 0.3, 0.7, 0.88),
                sign='PERPUSTAKAAN KOTA', sign_col='#3f4a6e', awning=('#9ec5ff', '#ffffff'), glow=True, seed=11)
m.building('bld_house_a', 1170, 520, w=230, roof='#c97b5f', wall='#fbeedd', trim='#8a5a3c', door=0.5, windows=(0.18, 0.82), seed=12)
m.building('bld_house_b', 1580, 520, w=250, roof='#7fb88f', wall='#f4f8ee', trim='#5f7f6a', style='wood', door=0.5, windows=(0.16, 0.84), seed=13)
m.building('bld_house_c', 300, 1000, w=240, roof='#d4799a', wall='#fff1f4', trim='#8a5a6a', door=0.5, windows=(0.18, 0.82), seed=14)
m.building('bld_house_d', 1700, 1000, w=240, roof='#9b80bd', wall='#f6f0fb', trim='#5a4a7a', style='wood', door=0.5, windows=(0.18, 0.82), seed=15)
m.place('bus_shelter', 1100, 830); m.anchor('halte', 1100, 846)
for x in (180, 900, 1400, 1900): m.place('lamp', x, 596)
for x in (160, 760, 1300, 1980): m.place('lamp', x, 806)
for x in (140, 460): m.place('garden_plot', x, 1080, shadow=False, variant='g%d' % x, seed=x)
for x in (1540, 1860): m.place('garden_plot', x, 1080, shadow=False, variant='g%d' % x, seed=x)
for x in (520, 1340): m.place('hedge', x, 868)
m.place('old_mailbox', 1460, 860); m.place('bench', 860, 868); m.place('tree_autumn', 960, 1000); m.place('tree_cherry', 1240, 1010)
m.place('bicycle', 1310, 556); m.place('mailbox', 1290, 556); m.place('mailbox', 1720, 556); m.place('flowerbed', 1050, 560); m.place('flowerbed', 1450, 560)
for t, x, y in [('tree_green', 80, 420), ('tree_cherry', 900, 400), ('tree_pine', 1380, 380), ('tree_green', 1960, 420), ('tree_cherry', 2000, 980), ('tree_green', 60, 980)]:
    m.place(t, x, y)
m.place('signpost', 80, 560, variant='w2', label='JALAN')
m.border(gaps={'left': [(600, 740)]})
m.door('res_to_street', (0, 600, 18, 140), 'Ke Jalan Kota', 'jalan_kota', 1960, 630, 'left')
pL = m.house_door('door_library', dL, 'Perpustakaan Kota', 'perpustakaan', 640, 270)
m.spawn = (80, 670)
m.anchor('front_library', *pL); m.anchor('mailbox_old', 1460, 884); m.anchor('bench', 860, 890); m.anchor('center', 1000, 670); m.anchor('west', 80, 670)
m.anchor('garden', 460, 1100); m.anchor('house_c', 300, 1020)
m.exam('res_garden', 460, 1110, 'Kebun warga', both('arland', 'Kebun kecil warga. Tomatnya hampir merah.', 'sofia', 'Ada yang menanam melati di sela sayuran. Manis sekali.', 'neutral', 'senyum'))
m.exam('res_house_c', 300, 1024, 'Rumah merah muda', narr('Di jendela ada tulisan tangan anak kecil: "Rumah Dito!" Lengkap dengan gambar bintang.'))
m.exam('res_bench', 860, 892, 'Bangku halte', both('arland', 'Bangku ini menghadap jalan. Enak buat menunggu, atau melamun.', 'sofia', 'Dulu aku sering menunggu bus di sini sambil membaca.'))
ng = m.nogo_mask(road, walk, c.rect(c.mask(), 0, 200, m.w, 330), c.rect(c.mask(), 0, 860, m.w, 300))
m.tree_line(['tree_green', 'tree_cherry', 'tree_pine'], sides='tb', seed=16)
m.scatter(['bush', 'bush_plain', 'flowerbed', 'rock', 'mushrooms'], 16, ng, region=(40, 40, m.w - 40, m.h - 40), seed=17)
m.ground_decor(ng, patches=36, grass=50, seed=18)
done(m)

# ------------------------------------------------------------------------ Perpustakaan Kota
m = interior('perpustakaan', 'Perpustakaan Kota', dict(base='#e9e1d0', stripe='#dfd5c0', motif='#f5efe2', panel='#9b7a5a', trim='#5a4a3a'), floor_col='#9b7a5a', w=1280, h=768,
             seed=161, windows=(200, 460), music='cafe')
m.spawn = room_door(m, 640, 'perumahan', 0, 0, 'Keluar ke Perumahan')
m.place('library_counter', 330, 420, shadow=False)
for x in (820, 930, 1040): m.place('tall_bookshelf', x, 300, shadow=False, variant='w%d' % x, seed=x)
m.place('secret_shelf', 1160, 300, shadow=False)
m.place('tall_bookshelf', 110, 300, shadow=False, variant='w110', seed=110)
for x in (860, 1080): m.place('tall_bookshelf', x, 540, shadow=False, variant='m%d' % x, seed=x + 3)
for x in (860, 1080): m.place('tall_bookshelf', x, 720, shadow=False, variant='b%d' % x, seed=x + 7)
m.place('reading_table', 300, 600); m.place('reading_table', 300, 720, variant='b', lamp=False)
for y in (560, 740): m.place('tall_bookshelf', 110, y, shadow=False, variant='l%d' % y, seed=y)
m.place('reading_table', 1240 - 60, 640, variant='c'); m.place('candle', 1180, 612, shadow=False)
m.place('rug_round', 520, 620, shadow=False, collide=False, variant='lib', c1='#9b80bd', c2='#e9e1d0')
m.place('globe', 560, 460); m.place('sofa', 560, 690, shadow=False, variant='lib'); m.place('floor_lamp', 680, 720)
for x, y, sd in [(440, 470, 1), (720, 470, 2), (1220, 560, 3), (160, 560, 4)]: m.place('book_pile', x, y, variant='p%d' % sd, seed=sd)
m.place('plant_big', 40, 740); m.place('plant_big', 1240, 740, variant='lib'); m.place('plant', 720, 300); m.place('plant', 560, 300, variant='lib')
m.place('wall_clock', 640, 80, shadow=False, collide=False); m.place('frame_photo', 330, 130, shadow=False, collide=False, variant='lib')
m.place('poster', 980, 120, shadow=False, collide=False, variant='lib')
m.props[[p['type'] for p in m.props].index('secret_shelf')].update({'alt': 'secret_shelf_open', 'altFlag': 'LIB_SECRET_OPEN'})
m._def('secret_shelf_open', P.render('secret_shelf', open_=True), 92, 24, 'sort')
m.door('lib_to_archive', (1130, 286, 60, 18), 'Rak yang terbuka', 'ruang_arsip', 400, 270, 'up')
m.anchor('laras', 330, 384); m.anchor('counter_front', 330, 450); m.anchor('table', 300, 630); m.anchor('table2', 300, 750)
m.anchor('shelf_a', 860, 566); m.anchor('shelf_b', 1080, 566); m.anchor('shelf_c', 930, 326); m.anchor('secret', 1160, 326)
m.anchor('globe', 560, 484); m.anchor('sofa', 560, 714); m.anchor('center', 640, 520); m.anchor('door_in', 640, 270)
m.exam('lib_globe', 560, 486, 'Bola dunia', both('arland', 'Ada coretan pensil kecil di bola dunia: sebuah bintang di tengah laut.', 'sofia', 'Seseorang melingkari kota kita dengan pensil. Lucu.'))
m.exam('lib_sofa', 560, 716, 'Sofa baca', both('arland', 'Empuk. Bahaya, bisa ketiduran.', 'sofia', 'Sudut paling nyaman di perpustakaan ini.', 'neutral', 'senyum'))
m.exam('lib_clock', 640, 290, 'Jam dinding', narr('Jam dinding tua berdetak pelan. Jarumnya berhenti di 4:07, tapi tetap berdetak.'))
m.exam('lib_shelf_w', 110, 326, 'Rak sejarah kota', narr('Buku sejarah kota. Di halaman pertama: "Kota ini dibangun oleh orang-orang yang suka bercerita."'))
done(m)

# ------------------------------------------------------------------------ Ruang Arsip Rahasia
m = interior('ruang_arsip', 'Ruang Arsip Rahasia', dict(base='#3e3656', stripe='#383050', motif='#5a4f78', panel='#2e2840', trim='#1d1a2e'), floor='tiles',
             floor_col=('#4a4266', '#3e3858', '#2e2a44'), w=800, h=560, seed=171, windows=(), music='memory', ambient='sparkles')
m.spawn = room_door(m, 400, 'perpustakaan', 1160, 340, 'Kembali ke perpustakaan')
for x in (110, 210, 590, 690): m.place('jar_shelf', x, 300, shadow=False, variant='j%d' % x, seed=x)
m.place('archive_pedestal', 400, 440)
for x, y in [(300, 420), (500, 420), (300, 520), (500, 520), (60, 520), (740, 520)]: m.place('candle', x, y, shadow=False)
for x, y, sd in [(150, 470, 5), (650, 470, 6), (700, 380, 7)]: m.place('book_pile', x, y, variant='a%d' % sd, seed=sd)
m.place('rug_round', 400, 500, shadow=False, collide=False, variant='arc', c1='#6b5a80', c2='#3e3656')
m.anchor('pedestal', 400, 470); m.anchor('jars_w', 160, 330); m.anchor('jars_e', 640, 330); m.anchor('center', 400, 400)
m.exam('arc_jars', 160, 332, 'Stoples bercahaya', narr('Setiap stoples berisi cahaya kecil yang berdenyut pelan, seperti napas. Labelnya tulisan tangan: "Sore di dermaga", "Hujan pertama", "Tawa di pasar".'))
m.exam('arc_jars_e', 640, 332, 'Stoples tanpa label', narr('Stoples-stoples ini kosong, tapi tutupnya hangat. Seperti menunggu diisi.'))
done(m)

# ------------------------------------------------------------------------ Dermaga Danau
m = Map('dermaga', 'Dermaga Danau', 1920, 1088, 'town', 'fireflies', seed=181)
c = m.c
c.grass(c.rect(c.mask(), 0, 0, m.w, m.h))
lake = c.rect(c.mask(), 0, 560, m.w, m.h - 560); c.ellipse(lake, 960, 560, 900, 60)
c.water(lake, shore=16)
c.dirt(c.poly_path(c.mask(), [(0, 425), (400, 440), (800, 470), (960, 480), (1400, 500)], 46))
pier = c.rect(c.mask(), 924, 470, 72, 400); plat = c.rect(c.mask(), 790, 860, 340, 96)
m.place('bridge', 960, 880, shadow=False, collide=False, variant='dpier', w=72, h=420)
m.place('bridge', 960, 960, shadow=False, collide=False, variant='dplat', w=340, h=110)
m.block(c.dilate(lake, 3), keep=c.rect(c.mask(), 924, 470, 72, 400) | c.rect(c.mask(), 790, 856, 340, 100))
m.water.append({'cx': 960, 'cy': 860, 'rx': 920, 'ry': 220})
for (x, y) in [(918, 560), (1002, 560), (918, 700), (1002, 700), (790, 960), (1130, 960)]: m.place('pier_post', x, y, shadow=False)
m.place('lantern_post', 806, 880); m.place('lantern_post', 1114, 880)
m.place('rowboat', 860, 720, shadow=False, collide=False); m.place('rowboat', 1070, 660, shadow=False, collide=False, variant='b', col='#8fa8c8')
m.place('fishing_hut', 1460, 470); m.place('bench', 600, 470); m.place('bench', 1240, 470, variant='b')
for x in (420, 760, 1160, 1700): m.place('lamp', x, 452)
for t, x, y in [('tree_green', 120, 260), ('tree_cherry', 360, 200), ('tree_pine', 620, 140), ('tree_autumn', 900, 260), ('tree_green', 1180, 180), ('tree_cherry', 1700, 280), ('tree_pine', 1860, 140), ('tree_autumn', 1560, 200)]:
    m.place(t, x, y)
for x, y in [(240, 470), (1820, 480), (520, 330), (1320, 330)]: m.place('flowerbed' if x % 2 == 0 else 'bush', x, y)
for x, y in [(100, 520), (1880, 520), (700, 520)]: m.place('rock', x, y)
m.place('signpost', 140, 400, variant='w3', label='DANAU')
m.border(gaps={'left': [(380, 470)]})
m.door('pier_to_lake', (0, 380, 18, 90), 'Ke Tepi Danau', 'riverside', 1860, 610, 'left')
m.spawn = (70, 425)
m.anchor('arrive', 70, 425); m.anchor('pier_start', 960, 500); m.anchor('pier_end', 960, 930); m.anchor('plat_l', 880, 930); m.anchor('plat_r', 1040, 930)
m.anchor('hut', 1460, 492); m.anchor('bench', 600, 492); m.anchor('fish_spot', 1090, 935); m.anchor('center', 960, 470)
m.exam('pier_boat', 1000, 760, 'Perahu kecil', narr('Perahu kayu terikat di tiang dermaga. Namanya dicat di sisinya: "Senja".'))
m.exam('pier_hut', 1460, 494, 'Pondok sewa perahu', both('arland', 'Sewa perahu: tutup sore ini. Lain kali, mungkin.', 'sofia', 'Kapan-kapan kita naik perahu, ya?', 'neutral', 'senyum'))
m.exam('pier_water', 960, 945, 'Ujung dermaga', both('arland', 'Dari sini, langit dan danau seperti satu halaman.', 'sofia', 'Kalau sore, airnya jadi emas. Aku suka sekali.', 'neutral', 'senyum'))
ng = m.nogo_mask(c.poly_path(c.mask(), [(0, 425), (400, 440), (800, 470), (960, 480), (1400, 500)], 90), c.rect(c.mask(), 0, 420, m.w, 700))
m.tree_line(['tree_green', 'tree_cherry', 'tree_pine', 'tree_autumn'], sides='tlr', skip=[(0, 425)], seed=19)
m.scatter(['bush', 'flowerbed', 'rock', 'mushrooms', 'tree_green'], 16, ng, region=(40, 60, m.w - 40, 400), seed=20)
m.ground_decor(ng, patches=36, grass=50, seed=21)
c.tall_grass(320, 540, 36); c.tall_grass(1600, 545, 40); c.tall_grass(1220, 540, 26)
done(m)

# ======================================================================== v1.3 EKSPLORASI
# ------------------------------------------------------------------------ Hutan Bisik
m = Map('hutan_bisik', 'Hutan Bisik', 2560, 1920, 'memory', 'fireflies', seed=191)
c = m.c
c.forest_floor(c.rect(c.mask(), 0, 0, m.w, m.h))
# dataran tinggi barat laut (gua) dan timur (jalan ke bukit)
topW = c.rect(c.mask(), 100, 60, 820, 420, r=40)
topE = c.rect(c.mask(), 2080, 160, 480, 460, r=30)
faceW, sideW = c.cliff(topW); faceE, sideE = c.cliff(topE)
stW = c.stairs(470, 480, 70, 56); stE = c.stairs(2250, 620, 70, 56)
# sungai utara-selatan + air terjun
riv = c.stream([(1900, 0), (1880, 500), (1930, 1000), (1900, 1500), (1940, 1920)], 76)
m.place('waterfall', 1900, 120, shadow=False, collide=False, variant='hb', w=76, h=120)
paths = [
    [(1280, 1920), (1280, 1500), (1200, 1150)], [(1200, 1150), (1280, 800), (1280, 420)],
    [(1200, 1150), (820, 1060), (480, 900)], [(480, 900), (450, 640), (505, 540)],
    [(1280, 800), (1650, 800), (1980, 800), (2200, 720), (2285, 676)], [(2285, 600), (2400, 420), (2560, 400)],
    [(505, 470), (500, 300), (500, 250)], [(1200, 1150), (900, 1500), (600, 1700)]]
pm = c.mask()
for pt in paths: c.poly_path(pm, pt, 56)
secret = c.poly_path(c.mask(), [(1330, 400), (1470, 320), (1600, 230)], 34)
clear = c.mask()
for (cx, cy, rx, ry) in [(1200, 1150, 170, 110), (480, 900, 150, 110), (1280, 420, 150, 100), (1640, 200, 120, 80), (600, 1720, 160, 100), (2380, 400, 140, 110)]:
    c.ellipse(clear, cx, cy, rx, ry)
c.dirt(pm & ~riv & ~faceW & ~faceE, base='#c9a77a', dark='#a8875a', light='#dcc096', rim='#3f7a3d')
c.stepping_stones([(1330, 400), (1470, 320), (1600, 230)], every=30, r=7)
for (cx, cy, r) in [(1280, 420, 80), (1640, 200, 70), (600, 1720, 90), (480, 900, 60)]: c.flower_patch(cx, cy, r, dens=0.05)
# jembatan rusak (gerbang sampai diperbaiki)
m.place('bridge_broken', 1905, 830, shadow=False, collide=False, variant='hb', w=130, h=60)
m.props[-1].update({'alt': 'bridge_fixed_hb', 'altFlag': 'JEMBATAN_FIXED'})
m._def('bridge_fixed_hb', P.render('bridge', w=130, h=60), 0, 0, 'floor')
m.block(c.dilate(riv, 2), keep=c.rect(c.mask(), 1840, 772, 130, 56))
m.gates.append({'rect': [1846, 772, 118, 56], 'openFlag': 'JEMBATAN_FIXED'})
m.block(faceW | sideW, keep=stW | c.rect(c.mask(), 470, 470, 70, 20)); m.block(faceE | sideE, keep=stE | c.rect(c.mask(), 2250, 610, 70, 20))
# tempat-tempat
m.place('cave_entrance', 500, 250); m.door('forest_to_cave', (474, 238, 52, 16), 'Masuk Gua Kristal', 'gua_kristal', 640, 880, 'up')
m.place('stone_lantern', 420, 860); m.place('stone_lantern', 540, 860); m.place('carving', 480, 830, variant='moon', sym='moon')
m.place('tent', 1110, 1110); m.place('campfire', 1220, 1170); m.place('log_bench', 1300, 1150); m.place('log_bench', 1180, 1230, variant='b')
m.place('carving', 1340, 1090, variant='star', sym='star')
m.place('mushroom_ring', 1280, 450, shadow=False, collide=False)
m.place('chest', 1660, 190); m.props[-1].update({'alt': 'chest_open', 'altFlag': 'CHEST_GLADE'})
m.place('chest', 640, 1700, variant='hs'); m.props[-1].update({'alt': 'chest_open', 'altFlag': 'CHEST_FERN'})
m._def('chest_open', P.render('chest', open_=True), 26, 10, 'sort')
m.place('stone_lantern', 2330, 380, variant='e'); m.place('signpost', 2450, 360, variant='e2', label='BUKIT')
m.place('signpost', 1360, 1840, variant='s2', label='TAMAN'); m.place('signpost', 1340, 860, variant='hx', label='SUNGAI')
for x, y in [(700, 1640), (520, 1760), (1500, 260)]: m.place('bush_berry', x, y)
m.border(gaps={'bottom': [(1220, 1340)], 'right': [(360, 440)]})
m.door('forest_to_park', (1220, 1902, 120, 18), 'Ke Taman Kota', 'taman_kota', 960, 70, 'down')
m.door('forest_to_hill', (2542, 360, 18, 80), 'Ke Bukit Bintang', 'bukit_bintang', 70, 620, 'right')
m.spawn = (1280, 1850)
for k, v in dict(arrive=(1280, 1850), camp=(1200, 1190), shrine=(480, 930), carving_moon=(480, 856), carving_star=(1340, 1116), ring=(1280, 470),
                 glade=(1640, 230), chest_glade=(1660, 214), fern=(600, 1740), chest_fern=(640, 1724), bridge_w=(1830, 800), bridge_e=(1985, 800),
                 cave=(500, 300), east=(2380, 420), plank1=(1460, 330), plank2=(760, 1600), plank3=(330, 1010), stairs_w=(505, 560), river_bank=(1780, 1300)).items():
    m.anchor(k, *v)
m.exam('hb_ring', 1280, 470, 'Lingkaran jamur', narr('Lingkaran jamur sempurna. Kata orang, kalau berdiri di tengahnya, kamu bisa mendengar hutan berbisik.'))
m.exam('hb_tent', 1110, 1130, 'Tenda', narr('Tenda kosong dengan buku catatan pendaki: "Hari ke-3. Kunang-kunang di sini berkedip bergantian, seperti mengobrol."'))
m.exam('hb_falls', 1820, 160, 'Air terjun kecil', narr('Air terjun kecil. Suaranya menenggelamkan semua pikiran yang berisik.'))
m.exam('hb_stairs', 560, 600, 'Tangga batu', narr('Tangga batu tua ditumbuhi lumut. Seseorang menyapu daunnya baru-baru ini.'))
ng = m.nogo_mask(pm, secret, clear, riv, faceW, faceE, topW, topE, c.rect(c.mask(), 1180, 1700, 200, 220))
m.scatter(['tree_oak', 'tree_dark', 'tree_green', 'tree_pine', 'tree_oak', 'tree_autumn', 'bush', 'bush_plain', 'tree_dark'], 360, ng, region=(20, 20, m.w - 20, m.h - 20), seed=192, tries=60)
for tp, rg, sd in [(topW, (110, 70, 910, 470), 193), (topE, (2090, 170, 2550, 610), 194)]:
    ngp = m.nogo_mask(pm, clear, ~tp)
    m.scatter(['tree_pine', 'tree_dark', 'bush', 'rock'], 26, ngp, region=rg, seed=sd)
m.scatter(['mushrooms', 'rock', 'bush_berry', 'mushrooms'], 40, m.nogo_mask(pm, riv, faceW, faceE, secret), seed=195)
c.tall_grass(1700, 1300, 60, nogo=riv); c.tall_grass(900, 1400, 50); c.tall_grass(1500, 600, 40)
done(m)

# ------------------------------------------------------------------------ Bukit Bintang
m = Map('bukit_bintang', 'Bukit Bintang', 1920, 1280, 'star', 'petals', seed=201)
c = m.c
c.grass(c.rect(c.mask(), 0, 0, m.w, m.h), pal=('#7dbb67', '#88c470', '#93cd78', '#69a85a'), flowers=0.003)
low = c.rect(c.mask(), 0, 1040, m.w, 240)
c.grass(low, pal=('#5e9a50', '#669f58', '#4f8a46', '#5a9750'), flowers=0.001)
hill = c.rect(c.mask(), 0, 0, m.w, 990)
face, side = c.cliff(hill, face_h=50)
for x in range(0, m.w, 3):   # kabut lembah
    pass
c.tint('#e8e0ff', 0.04)
deck = c.rect(c.mask(), 1380, 640, 300, 170, r=20); c.cobble(deck, base='#d8d0c4', grout='#a89c8e', sw=(16, 22), sh=14)
pth = c.poly_path(c.mask(), [(0, 620), (500, 620), (900, 700), (1100, 720), (1400, 720)], 54); c.poly_path(pth, [(1100, 720), (1100, 560)], 54)
c.dirt(pth & ~deck, base='#d9b98a')
m.place('observatory', 1100, 560)
m.place('telescope', 1560, 700); m.place('bench', 1440, 790); m.place('picnic_blanket', 700, 860, shadow=False, collide=False)
for x in range(80, 1880, 64): m.place('fence', x, 985, shadow=False, variant='bb', n=1)
m.place('chest', 260, 300, variant='bb'); m.props[-1].update({'alt': 'chest_open', 'altFlag': 'CHEST_HILL'})
for t, x, y in [('tree_cherry', 300, 520), ('tree_green', 1700, 380), ('tree_oak', 1820, 760), ('tree_cherry', 640, 380), ('tree_pine', 1500, 220), ('tree_autumn', 180, 820)]: m.place(t, x, y)
for (cx, cy, r) in [(600, 760, 120), (1700, 560, 90), (300, 640, 80), (900, 420, 100), (1300, 900, 110)]: c.flower_patch(cx, cy, r, dens=0.03)
for x, y in [(820, 900), (1000, 880)]: m.place('flowerbed', x, y)
m.place('stone_lantern', 980, 700, variant='bb'); m.place('stone_lantern', 1220, 700, variant='bb2')
m.block(face | side | low)
m.border(gaps={'left': [(580, 660)]})
m.door('hill_to_forest', (0, 580, 18, 80), 'Ke Hutan Bisik', 'hutan_bisik', 2500, 400, 'left')
m.spawn = (70, 620)
for k, v in dict(arrive=(70, 620), obs_door=(1100, 590), telescope=(1560, 726), deck=(1530, 760), chest=(260, 324), nara=(1480, 700), picnic=(700, 880),
                 edge=(900, 960), meadow=(600, 760)).items():
    m.anchor(k, *v)
m.exam('bb_edge', 900, 962, 'Tepi bukit', both('arland', 'Dari sini seluruh kota kelihatan. Atap rumah Sofia yang merah muda itu, ya?', 'sofia', 'Kota kita kecil sekali dari atas. Tapi semuanya ada di situ.', 'neutral', 'senyum'))
m.exam('bb_obs', 1100, 592, 'Pintu observatorium', narr('Pintu terkunci. Ada catatan: "Sedang kalibrasi teleskop. Tanya Kak Nara di dek pandang."'))
ng = m.nogo_mask(pth, deck, face, low, c.rect(c.mask(), 900, 360, 400, 260))
m.tree_line(['tree_green', 'tree_cherry', 'tree_pine'], sides='tr', seed=202)
m.scatter(['bush', 'flowerbed', 'rock', 'tree_cherry', 'bush'], 20, ng, region=(40, 40, m.w - 40, 940), seed=203)
m.scatter(['tree_green', 'tree_pine', 'bush'], 24, m.nogo_mask(~low), region=(20, 1080, m.w - 20, m.h - 10), seed=204)
done(m)

# ------------------------------------------------------------------------ Gua Kristal
m = Map('gua_kristal', 'Gua Kristal', 1280, 960, 'memory', 'dark', seed=211)
c = m.c
c.fill(c.rect(c.mask(), 0, 0, m.w, m.h), '#1d1a2a')
floor = c.mask()
for (cx, cy, rx, ry) in [(640, 820, 200, 120), (640, 600, 260, 160), (380, 420, 200, 140), (900, 400, 230, 150), (1050, 200, 170, 110), (300, 200, 150, 100)]:
    c.ellipse(floor, cx, cy, rx, ry)
floor = c.wobble(floor, grow=8, amp=16)
c.poly_path(floor, [(640, 960), (640, 820)], 120)
c.cave_floor(floor)
pond = c.ellipse(c.mask(), 700, 560, 120, 60); c.water(pond, deep='#3a6aa0', mid='#4f86bf', shallow='#7fb8e0', shore=0)
wall = ~floor
rim = c.dilate(floor, 3) & wall; c.px[rim] = (60, 54, 82); c.px[c.dilate(floor, 1) & wall] = (88, 80, 112)
m.block(wall | pond)
for x, y in [(420, 300), (860, 300), (1180, 230), (210, 160), (1000, 520), (350, 520), (520, 760), (800, 760)]: m.place('crystal_big' if (x + y) % 3 else 'crystal', x, y)
for k, (x, y) in enumerate([(300, 380), (980, 330), (760, 680), (500, 650), (1150, 160), (240, 250)]): m.place('stalagmite', x, y, variant='s%d' % k, seed=k)
m.place('carving', 900, 470, variant='flower', sym='flower')
m.place('chest', 1080, 170, variant='gk'); m.props[-1].update({'alt': 'chest_open', 'altFlag': 'CHEST_CAVE'})
m.door('cave_to_forest', (580, 942, 120, 18), 'Keluar ke Hutan Bisik', 'hutan_bisik', 500, 320, 'down')
m.spawn = (640, 880)
for k, v in dict(arrive=(640, 880), carving=(900, 496), chest=(1080, 196), pond=(700, 640), hall=(640, 600), west=(300, 220), east=(1050, 240)).items():
    m.anchor(k, *v)
m.exam('gk_pond', 700, 640, 'Kolam bawah tanah', narr('Air kolamnya jernih sekali. Di dasarnya, kristal kecil berkedip seperti bintang yang tenggelam.'))
m.exam('gk_wall', 380, 470, 'Dinding gua', narr('Ada goresan tangan anak kecil di dinding: dua orang bergandengan, dan tulisan "W + S". Sudah sangat tua.'))
done(m)

# ------------------------------------------------------------------------ hubungkan pintu interior ke luar
def fix_door(map_id, door_id, tx, ty):
    for d in maps[map_id]['doors']:
        if d['id'] == door_id: d['tx'], d['ty'] = int(tx), int(ty)
pa, ps, pc = anchors['plaza']['front_arland'], anchors['plaza']['front_sofia'], anchors['plaza']['front_cafe']
fix_door('arland_room', 'arland_room_out', *pa); fix_door('sofia_room', 'sofia_room_out', *ps); fix_door('cafe', 'cafe_out', *pc)
fix_door('perpustakaan', 'perpustakaan_out', *anchors['perumahan']['front_library'])
fix_door('toko_bunga', 'toko_bunga_out', *anchors['jalan_kota']['front_florist']); fix_door('arcade', 'arcade_out', *anchors['jalan_kota']['front_arcade'])
for d in maps['cafe']['doors']:
    if d['id'] == 'cafe_out': pass
for d in maps['plaza']['doors']:
    if d['to'] == 'cafe': d['tx'], d['ty'] = 400, 270

json.dump(maps, open(os.path.join(BUILD, 'maps_base.json'), 'w'), ensure_ascii=False, indent=1)
json.dump({'_doc': 'Definisi properti (dibuat oleh tools/build_maps.py). Titik penempatan = tengah-bawah; cw/ch = kotak collision kaki.', 'props': PROPDEFS},
          open(os.path.join(ASSETS, 'data', 'props.json'), 'w'), ensure_ascii=False, indent=1)
json.dump(anchors, open(os.path.join(BUILD, 'anchors.json'), 'w'), indent=1)
print('selesai:', len(maps), 'peta,', len(PROPDEFS), 'props')
