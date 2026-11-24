"""Plaza Kota v6: redesigned layout (2400x1600, was 1920x1280).

Usage: python3 tools/v6/worldgen/plaza_v6.py [--ground-only OUT.png] [--apply]

Districts
  north   back gardens behind the three houses (dirt loop, groves, flower meadow)
  row     Arland's house, Sofia's house and Kafe Senja on a brick promenade
  centre  paved square with a radial cobble ring and star mosaic around the fountain
  west    Pasar Minggu market square (terracotta tiles), mural wall, stalls
  east    cafe garden deck (wood) with umbrella tables and Nenek Sari's flower stall
  south   stone-banked canal with flowing water, three bridges, a riverside garden strip
Gameplay coordinates of every plaza quest point are migrated by --apply (x1.25 base
scale plus named overrides), then validated for walkability and reachability.
"""
import sys, json, hashlib
from pathlib import Path
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paint import Canvas, rgb, hash2           # noqa: E402
from ground import dist_from, noise            # noqa: E402

W, H = 2400, 1600
SEED = int(hashlib.sha256(b'plaza_v6').hexdigest()[:8], 16)

# --------------------------------------------------------------------------- layout
HOUSES = {'arland': 420, 'sofia': 1320, 'cafe': 1980}   # x of building foot centre
HOUSE_FOOT = 500
PROM = (40, 512, 2320, 120)            # promenade x, y, w, h
SQUARE = (820, 632, 760, 660, 60)      # central paved square (rounded)
CIRCLE = (1200, 960, 300, 0.78)        # cx, cy, rx, ry scale
AVE_W = (0, 862, 840, 112)             # west avenue to park exit
AVE_E = (1560, 862, 840, 112)          # east avenue to street exit
MARKET = (250, 720, 520, 470, 28)
DECK = (1650, 700, 520, 400)
CANAL = (20, 1338, 2360, 76)           # water body (between bank caps)
BRIDGES = {'west': (430, 110, 'wood'), 'centre': (1130, 140, 'stone'), 'east': (1850, 110, 'wood')}
SOUTH_PATH = (1140, 1290, 120, 310)
TERRACE = dict(x=780, y=342, w=168, h=92, rise=26, stairLength=78, stairWidth=56)


def smooth(pts, n=10):
    """Catmull-Rom through the control points (organic garden paths)."""
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = (np.array(P[j], float) for j in (i - 1, i, i + 1, i + 2))
        for t in np.linspace(0, 1, n, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)))
    out.append(tuple(pts[-1]))
    return out


def paint_ground():
    c = Canvas(W, H, SEED)
    G, P, S, T, D, WT, DIRT = 1, 2, 3, 4, 5, 6, 7
    c.put(np.ones((H, W), bool), c.grass(), G)

    # back-garden dirt loop + spurs to the promenade between the houses
    loop = c.poly_path(smooth([(230, 512), (200, 400), (290, 290), (520, 240), (760, 270), (1060, 230), (1300, 200), (1560, 260), (1900, 230), (2170, 300), (2220, 420), (2140, 512)]), 46)
    loop |= c.poly_path(smooth([(1060, 240), (1040, 380), (1080, 512)]), 40) | c.poly_path(smooth([(1660, 250), (1680, 380), (1650, 512)]), 40)
    loop = c.wobble(loop, 2, 6, 1)
    c.put(loop, c.dirt(), DIRT)

    prom = c.rrect(*PROM, 18)
    prom_img = c.bricks(('#b9a184', '#c4ac8d', '#cdb697', '#d6c0a2', '#ddc9ac'), 18, 9, '#8d7860', salt=1)
    c.put(prom, prom_img, P)
    # door aprons in front of each building
    for x in HOUSES.values():
        ap = c.rect(x - 34, HOUSE_FOOT - 6, 68, 22)
        c.put(ap, c.bricks(('#a99580', '#b5a08a', '#bfab94'), 12, 6, '#7f6c58', salt=2), P)

    sq = c.rrect(*SQUARE)
    aves = c.rect(*AVE_W) | c.rect(*AVE_E) | c.rect(*SOUTH_PATH) | c.rect(1110, 600, 180, 60)
    sq_img = c.bricks(('#c7ab80', '#d0b58a', '#d9bf95', '#e1c99f', '#e8d3ab'), 16, 8, '#937a5a', salt=3)
    c.put(sq | aves, sq_img, S)

    # radial ring + mosaic
    cx, cy, rx, rys = CIRCLE
    ring = c.ellipse(cx, cy, rx, rx * rys)
    rad, r, th, ri = c.radial(cx, cy, rys, ('#bfa68a', '#c9b195', '#d3bca0', '#dcc6ab', '#e5d1b7'), 11, 19, salt=5)
    c.put(ring, rad, S)
    band = ring & (((r > rx - 14) & (r < rx - 4)) | ((r > 196) & (r < 206)))
    c.img[band] = np.where(((th * 30 / np.pi).astype(int) % 2 == 0)[band][:, None], rgb('#8f6f58'), rgb('#a8826a'))
    c.img[ring & (r >= rx - 4)] = rgb('#7e6450')
    # eight-point star inlay between radius 120 and 196
    k = 8
    star_r = 120 + 76 * np.abs(np.cos(th * k / 2)) ** 3
    inlay = ring & (r > 122) & (r < star_r) & (r < 196)
    inlay_col = np.where(((th * k / np.pi).astype(int) % 2 == 0)[..., None], rgb('#e9dcc2'), rgb('#c98f6a'))
    c.img[inlay] = inlay_col[inlay] * (0.96 + 0.06 * hash2(ri, (th * 40).astype(int), 9))[inlay][:, None]
    edge = inlay & ~(c.wobble(inlay, 0) & np.roll(inlay, 1, 0) & np.roll(inlay, -1, 0) & np.roll(inlay, 1, 1) & np.roll(inlay, -1, 1))
    c.img[edge] = rgb('#7a5c48')
    inner = ring & (r <= 122)
    c.img[inner] = rad[inner] * 0.96

    # market square: terracotta + cream tiles with a border course
    mk = c.rrect(*MARKET)
    c.put(mk, c.tiles('#c98d66', '#e4d2b2', 24, '#9a7458', salt=6), T)
    border = mk & ~c.rrect(MARKET[0] + 10, MARKET[1] + 10, MARKET[2] - 20, MARKET[3] - 20, MARKET[4] - 8)
    c.put(border, c.bricks(('#9b7c64', '#a88870', '#b3937a'), 10, 10, '#6f5643', salt=7), T)

    # cafe garden deck
    dk = c.rect(*DECK)
    c.put(dk, c.planks(salt=8), D)
    dk_edge = dk & ~c.rect(DECK[0] + 6, DECK[1] + 6, DECK[2] - 12, DECK[3] - 12)
    c.img[dk_edge] = rgb('#6b4430')

    # canal: north bank wall face (seen from above-front), caps, water
    x0, y0, w0, h0 = CANAL
    cap_n = c.rect(x0, y0 - 22, w0, 8)
    face_n = c.rect(x0, y0 - 14, w0, 14)
    cap_s = c.rect(x0, y0 + h0, w0, 8)
    wat = c.rect(x0, y0, w0, h0)
    c.put(wat, c.water(wat), WT)
    c.put(face_n, c.bricks(('#7f7a78', '#8a8481', '#958e89'), 16, 7, '#5d5856', salt=9), S)
    c.img[face_n] *= 0.86
    c.put(cap_n | cap_s, c.bricks(('#b4ada4', '#bfb8ae', '#c9c2b7'), 24, 8, '#878079', salt=10), S)
    shade = c.rect(x0, y0, w0, 10)
    c.img[shade & wat] *= 0.72                              # wall shadow on the water
    foam = c.rect(x0, y0 + h0 - 2, w0, 2)
    c.img[foam] = c.img[foam] * 0.4 + rgb('#d9eef5') * 0.6

    # bridges
    for name, (bx, bw, kind) in BRIDGES.items():
        deck_m = c.rect(bx, y0 - 26, bw, h0 + 38)
        if kind == 'stone':
            img = c.bricks(('#c8b9a4', '#d2c4ae', '#dccfba'), 16, 8, '#8c7d6a', salt=11)
        else:
            img = c.planks(('#8b5d3c', '#996a46', '#a5754f'), 9, salt=12, vertical=True)
        c.put(deck_m, img, S if kind == 'stone' else D)
        par_l = c.rect(bx, y0 - 26, 8, h0 + 38); par_r = c.rect(bx + bw - 8, y0 - 26, 8, h0 + 38)
        c.img[par_l | par_r] = rgb('#8a7a6a') if kind == 'stone' else rgb('#5e3b27')
        c.img[c.rect(bx + bw, y0, 6, h0)] *= 0.6               # bridge shadow on water (east side)

    # paths through the south garden strip to the west/east bridges
    sp = c.poly_path(smooth([(485, 1420), (490, 1490), (640, 1540), (1140, 1545)]), 40) | \
        c.poly_path(smooth([(1905, 1420), (1900, 1490), (1750, 1540), (1260, 1545)]), 40)
    sp = c.wobble(sp, 2, 6, 3) & ~c.rect(0, 1330, W, 100)
    c.put(sp, c.dirt(), DIRT)
    # connectors from the square to the north-bank bridge heads
    nb = c.poly_path([(485, 1300), (485, 1190)], 40) | c.poly_path([(1905, 1300), (1905, 1100)], 40)
    nb = c.wobble(nb, 2, 6, 4) & ~c.rect(0, 1316, W, 120)
    c.put(nb & (c.mat == G), c.dirt(), DIRT)

    # map border: darker grass vignette band
    border_d = np.minimum.reduce([c.xx, c.yy, W - 1 - c.xx, H - 1 - c.yy])
    c.img[border_d < 6] *= 0.85

    grass = c.mat == G
    hard = np.isin(c.mat, [P, S, T, D])
    c.rim(hard, grass)
    c.rim(c.mat == DIRT, grass, dark='#7d6446', ao=(0.88, 0.95))
    c.overhang(hard | (c.mat == DIRT), grass, 0.33)
    return c


# --------------------------------------------------------------------------- props
def props():
    P = []
    add = lambda t, x, y, **kw: P.append(dict(type=t, x=int(x), y=int(y), **kw))
    add('v43_v41_bld_arland_house_house_blue', HOUSES['arland'], HOUSE_FOOT)
    add('v43_v41_bld_sofia_house_house_brick', HOUSES['sofia'], HOUSE_FOOT)
    add('v43_bld_cafe', HOUSES['cafe'], HOUSE_FOOT)
    add('v43_v41_fountain_fountain', 1200, 1000)
    # back gardens: tree line along the top edge, groves, meadow
    rng = np.random.default_rng(SEED)
    for i, x in enumerate(range(70, 2400, 150)):
        add(('tree_pine', 'tree_green', 'tree_pine', 'v43_v41_tree_green_willow')[i % 4], x + rng.integers(-20, 20), 118 + rng.integers(0, 24))
    for t, x, y in [('tree_oak', 560, 360), ('v41_tree_cherry_cherry', 680, 330), ('tree_green', 120, 330),
                    ('v43_v41_tree_green_willow', 1420, 380), ('v41_tree_cherry_cherry', 1800, 390),
                    ('tree_oak', 2280, 250), ('tree_autumn', 2300, 470), ('tree_green', 120, 470),
                    ('tree_cherry', 1560, 400), ('tree_autumn', 1150, 400)]:
        add(t, x, y)
    for i, (x, y) in enumerate([(440, 330), (900, 200), (1400, 230), (1760, 300), (2020, 380), (330, 420), (1880, 180),
                                (620, 180), (1160, 160), (2060, 200)]):
        add(('bush_berry', 'mushrooms', 'bush', 'rock')[i % 4], x, y)
    add('v51_bench_wood', 1330, 245)
    add('garden_plot_tk', 1990, 400); add('garden_plot_tk2', 2080, 400) if False else None
    add('v51_birdbath', 360, 220)
    add('v51_approach_plaza', 1000, 506)
    # promenade
    add('bicycle', 290, 525); add('mailbox', 530, 520); add('mailbox', 1430, 520)
    add('old_mailbox', 1010, 628)
    add('notice_board', 1625, 592)
    for x in (180, 640, 1110, 1290, 1760, 2230):
        add('v51_street_lamp', x, 630)
    add('v51_banner_cafe', 1840, 520); add('v51_banner_cafe', 2120, 520)
    for x in (560, 1250, 1560, 2120):
        add('v51_planter_terracotta', x, 514)
    # central square
    add('v43_bench', 950, 1092); add('v43_bench', 1450, 1092); add('v43_bench', 700, 728)
    for x, y in [(880, 700), (1520, 700), (880, 1250), (1520, 1250), (905, 960), (1495, 960)]:
        add('v43_lamp', x, y)
    add('v43_v41_flowerbed_flower', 1325, 1048); add('v43_v41_flowerbed_flower', 1075, 1048)
    for x, y in [(1110, 1300), (1290, 1300)]:
        add('v51_column_stone', x, y)
    # west: Pasar Minggu
    add('mural', 525, 862, alt='mural_new', altFlag='SQ_MURAL_PAINTED')
    add('v43_v41_flowerbed_flower', 600, 646); add('flowerbed', 325, 802)
    add('stall_flowers', 360, 1120); add('stall_flowers', 600, 1120)
    add('crate', 720, 1160); add('crate', 742, 1140); add('barrel', 280, 760); add('barrel', 300, 770)
    add('crate', 290, 1000); add('barrel', 300, 1030); add('flower_buckets_c', 470, 1160)
    add('stall_flowers', 700, 960)
    add('v51_fountain_tiered', 510, 1030)
    add('hedge', 400, 700)
    for x, y in [(260, 1185), (760, 735)]:
        add('v51_planter_lavender', x, y)
    # east: cafe garden deck
    add('stall_flowers', 1775, 735)
    for x, y in [(1760, 905), (1960, 830), (2080, 970), (1880, 1040), (2090, 790)]:
        add('cafe_umbrella_table', x, y)
    add('flower_buckets', 1700, 1000); add('flower_buckets_b', 1960, 1085)
    add('v51_lantern_gold', 1655, 860); add('v51_lantern_gold', 2165, 860)
    add('vending', 2150, 1060)
    for x, y in [(1662, 1096), (2160, 1096), (2160, 712)]:
        add('v51_planter_lavender', x, y)
    add('hedge', 2080, 690)
    # canal and south garden
    add('v51_wall_stone', 2300, 1300); add('v51_rail_stone', 1200, 1310) if False else None
    for x in (60, 330, 700, 900, 1500, 1700, 2100, 2330):
        add('v51_reeds', x, 1430)
    for t, x, y in [('v41_tree_cherry_cherry', 300, 1490), ('tree_cherry', 820, 1475), ('tree_cherry', 1600, 1475),
                    ('v41_tree_cherry_cherry', 2150, 1495), ('v43_v41_tree_green_willow', 1000, 1470)]:
        add(t, x, y)
    for i, x in enumerate(range(60, 2400, 120)):
        if 1060 < x < 1340:
            continue
        add(('tree_green', 'tree_cherry', 'tree_green', 'tree_pine')[i % 4], x + rng.integers(-15, 15), 1598)
    # edges of the square and avenues
    for t, x, y in [('tree_pine', 200, 760), ('tree_green', 190, 1060), ('tree_oak', 2280, 770), ('tree_green', 2300, 1100),
                    ('v41_tree_cherry_cherry', 800, 1250), ('v41_tree_cherry_cherry', 1640, 1250), ('tree_green', 2050, 1220),
                    ('tree_autumn', 60, 600), ('tree_autumn', 2350, 600)]:
        add(t, x, y)
    for x, y in [(790, 650), (1610, 650), (790, 1290), (1610, 1290), (60, 1040), (2340, 1040)]:
        add('bush', x, y)
    # square corners: planters and benches so the paving is not empty
    for x, y in [(860, 820), (1540, 820), (860, 1150), (1540, 1150)]:
        add('v51_planter_terracotta', x, y)
    add('v51_bench_wood', 1000, 700); add('v51_bench_wood', 1420, 1250)
    add('signpost_w', 120, 850); add('signpost_e', 2290, 850); add('signpost_s', 1300, 1580)
    return [p for p in P if p]


def walls():
    w = [[0, 0, 20, 862], [0, 974, 20, 626], [2380, 0, 20, 862], [2380, 974, 20, 626], [0, 0, 2400, 20],
         [0, 1582, 1140, 18], [1260, 1582, 1140, 18]]
    x0, y0, w0, h0 = CANAL
    spans = sorted((bx, bx + bw) for bx, bw, _ in BRIDGES.values())
    cur = x0
    for a, b in spans:
        w.append([cur, y0 - 14, a - cur, h0 + 22]); cur = b
    w.append([cur, y0 - 14, x0 + w0 - cur, h0 + 22])
    for bx, bw, _ in BRIDGES.values():
        w.append([bx, y0 - 26, 8, h0 + 38]); w.append([bx + bw - 8, y0 - 26, 8, h0 + 38])
    return w


def area_entry(old):
    a = dict(old)
    a.update(w=W, h=H, spawn=[1200, 700], walls=walls(), ellipses=[[1200, 954, 108, 46]], props=props(),
             water=[{'cx': 1200, 'cy': 950, 'rx': 92, 'ry': 34}])
    x0, y0, w0, h0 = CANAL
    a['waterFlow'] = [{'x': x0, 'y': y0, 'w': w0, 'h': h0, 'dx': 1, 'speed': 18}]
    doors = {d['id']: dict(d) for d in old['doors']}
    doors['plaza_to_park']['rect'] = [0, 862, 18, 112]
    doors['plaza_to_street']['rect'] = [2382, 862, 18, 112]
    doors['plaza_to_lake']['rect'] = [1140, 1582, 120, 18]
    for key, did in (('arland', 'door_arland_house'), ('sofia', 'door_sofia_house'), ('cafe', 'door_cafe')):
        doors[did]['rect'] = [HOUSES[key] - 22, HOUSE_FOOT - 4, 44, 16]
    a['doors'] = [doors[d['id']] for d in old['doors']]
    ex = {e['id']: dict(e) for e in old['examine']}
    for k, (x, y) in {'fountain': (1200, 1045), 'notice': (1625, 614), 'bike': (290, 548), 'behind': (1200, 262)}.items():
        ex[k]['x'], ex[k]['y'] = x, y
    a['examine'] = [ex[e['id']] for e in old['examine']]
    a['animals'] = [{'type': 'cat_orange', 'n': 1, 'region': [300, 1440, 1700, 110]},
                    {'type': 'bird', 'n': 5, 'region': [900, 700, 600, 500]},
                    {'type': 'bird', 'n': 3, 'region': [300, 220, 1800, 160]},
                    {'type': 'cat_calico', 'n': 1, 'region': [1660, 720, 480, 360], 'day': False}]
    a['elevationPlatforms'] = [dict(old['elevationPlatforms'][0], **{k: TERRACE[k] for k in ('x', 'y', 'w', 'h', 'rise', 'stairLength', 'stairWidth')})]
    a.pop('v41PropReplacementIndex', None)
    a['visualStyle'] = 'v6_designed_layout'
    a['visualUpdate'] = 'v6_plaza_redesign'
    a['v6Layout'] = {'version': 1, 'generator': 'tools/v6/worldgen/plaza_v6.py', 'scaleFromV5': 1.25,
                     'districts': ['back gardens', 'promenade', 'central square', 'Pasar Minggu', 'cafe deck', 'canal + south garden']}
    a['environmentV51'] = dict(old['environmentV51'], landmark='Balkon taman belakang menghadap promenade dan alun-alun')
    return a


# --------------------------------------------------------------------------- coordinate migration
OVERRIDES = {(849, 492): (864, 380), (1060, 1120): (1325, 1290), (1059, 1119): (1325, 1290),
             (1250, 1050): (1562, 1290), (1820, 1100): (2275, 1480), (1820, 1096): (2275, 1476), (1329, 789): (1600, 930)}
DOOR_TARGETS = {'park_to_plaza': (70, 918), 'street_to_plaza': (2330, 918), 'lake_to_plaza': (1200, 1530),
                'arland_room_out': (HOUSES['arland'], 530), 'sofia_room_out': (HOUSES['sofia'], 530),
                'cafe_out': (HOUSES['cafe'], 530)}


def remap_point(x, y):
    if (x, y) in OVERRIDES:
        return OVERRIDES[(x, y)]
    return int(round(x * 1.25)), int(round(y * 1.25))


def migrate_quests(q):
    """Remap every plaza coordinate. Context = nearest 'area' key, and inside action lists a
    warp changes the area for the actions that follow it (cutscenes after a warp)."""
    moved = []

    def point(o, key, ctx):
        v = o[key]
        if key in ('to',) and isinstance(v, list) and len(v) == 2 and all(isinstance(n, (int, float)) for n in v):
            o[key] = list(remap_point(*v)); moved.append((o.get('c'), v[0], v[1], *o[key], None))
        elif key == 'path' and isinstance(v, list):
            o[key] = [list(remap_point(*pt)) for pt in v]
            moved.extend((o.get('c'), a[0], a[1], b[0], b[1], None) for a, b in zip(v, o[key]))

    def walk(o, ctx):
        if isinstance(o, dict):
            if isinstance(o.get('area'), str):
                ctx = o['area']
            if ctx == 'plaza':
                if 'x' in o and 'y' in o and isinstance(o['x'], (int, float)) and not isinstance(o['x'], bool):
                    nx, ny = remap_point(o['x'], o['y'])
                    moved.append((o.get('id') or o.get('c') or o.get('do') or o.get('at') or '?', o['x'], o['y'], nx, ny, o.get('r')))
                    o['x'], o['y'] = nx, ny
                if o.get('c') == 'move':
                    for k in ('to', 'path'):
                        if k in o:
                            point(o, k, ctx)
            for k, v in o.items():
                if isinstance(v, (dict, list)):
                    walk(v, ctx)
        elif isinstance(o, list):
            cur = ctx
            for v in o:
                if isinstance(v, dict) and v.get('do') == 'warp' and isinstance(v.get('area'), str):
                    walk(v, cur)
                    cur = v['area']
                    continue
                walk(v, cur)
    walk(q, None)
    return moved


def migrate_doors(areas):
    for name, a in areas.items():
        for d in a.get('doors', []):
            if d.get('to') == 'plaza':
                d['tx'], d['ty'] = DOOR_TARGETS[d['id']]


# --------------------------------------------------------------------------- validation
def blocked_fn(a, P):
    rects = list(a['walls'])
    for pr in a['props']:
        d = P[pr['type']]
        if d.get('cw', 0) > 0 and d.get('ch', 0) > 0:
            rects.append([pr['x'] - d['cw'] / 2, pr['y'] - d['ch'], d['cw'], d['ch']])

    def blocked(x, y):
        if x - 11 < 0 or x + 11 > a['w'] or y - 10 < 0 or y + 10 > a['h']:
            return True
        for rx, ry, rw, rh in rects:
            if x - 11 < rx + rw and x + 11 > rx and y - 10 < ry + rh and y + 10 > ry:
                return True
        for cx, cy, rw, rh in a['ellipses']:
            if ((x - cx) / (rw + 11)) ** 2 + ((y - cy) / (rh + 10)) ** 2 < 1:
                return True
        return False
    return blocked


def reachable_grid(a, blocked, st=8):
    from collections import deque
    gw, gh = a['w'] // st, a['h'] // st
    ok = np.zeros((gh, gw), bool)
    for j in range(gh):
        for i in range(gw):
            ok[j, i] = not blocked(i * st + st / 2, j * st + st / 2)
    seen = np.zeros_like(ok)
    sx, sy = a['spawn'][0] // st, a['spawn'][1] // st
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
    seen, st = reachable_grid(a, blocked)
    bad = []
    for label, x, y, r in points:
        if blocked(x, y):
            # interaction radius: fine if a reachable cell lies within r of the point
            rr = r or 40
            near = seen[max(0, int((y - rr) // st)):int((y + rr) // st) + 1, max(0, int((x - rr) // st)):int((x + rr) // st) + 1]
            if not near.any():
                bad.append(('blocked', label, x, y))
            continue
        if not seen[int(y // st), int(x // st)]:
            bad.append(('unreachable', label, x, y))
    return bad, seen


def main():
    root = Path(__file__).resolve().parents[3]
    A = root / 'android' / 'assets'
    M = json.loads((A / 'data/maps.json').read_text(encoding='utf-8'))
    Q = json.loads((A / 'data/quests.json').read_text(encoding='utf-8'))
    P = json.loads((A / 'data/props.json').read_text(encoding='utf-8'))['props']
    old = M['areas']['plaza']
    if old.get('v6Layout'):
        raise SystemExit('plaza already migrated to v6 (re-run from the pre-v6 data)')
    new = area_entry(old)
    moved = migrate_quests(Q)
    M['areas']['plaza'] = new
    migrate_doors(M['areas'])
    pts = [(m[0], m[3], m[4], m[5]) for m in moved]
    pts += [(d['id'], d['tx'], d['ty'], None) for a in M['areas'].values() for d in a.get('doors', []) if d.get('to') == 'plaza']
    pts += [('examine ' + e['id'], e['x'], e['y'], e['r']) for e in new['examine']]
    bad, seen = validate(new, P, pts)
    for b in bad:
        print('INVALID', *b)
    print('migrated', len(moved), 'quest coordinates;', len(pts), 'points checked;', len(bad), 'invalid')
    if '--apply' in sys.argv:
        if bad and '--force' not in sys.argv:
            raise SystemExit('not applied: fix invalid points first')
        c = paint_ground()
        Image.fromarray(c.result(), 'RGB').save(A / 'maps/plaza.png', optimize=True)
        (A / 'data/maps.json').write_text(json.dumps(M, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        (A / 'data/quests.json').write_text(json.dumps(Q, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        sites = json.loads((root / 'tools/v51_environment_sites.json').read_text(encoding='utf-8'))
        t = TERRACE
        sites['plaza'].update(x=t['x'], y=t['y'], w=t['w'], h=t['h'], stair=t['stairLength'], rise=t['rise'], stairWidth=t['stairWidth'],
                              reason='Plaza v6: balkon taman belakang, tangga turun ke promenade di antara rumah Arland dan Sofia')
        (root / 'tools/v51_environment_sites.json').write_text(json.dumps(sites, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print('applied')
    return new, P, seen


if __name__ == '__main__':
    if '--ground-only' in sys.argv:
        c = paint_ground()
        Image.fromarray(c.result(), 'RGB').save(sys.argv[sys.argv.index('--ground-only') + 1], optimize=True)
    else:
        main()
