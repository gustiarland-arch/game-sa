"""Taman Kota v6: redesigned park (2400x1760, was 1920x1408; x1.25).

Usage: python3 tools/v6/worldgen/taman_kota_v6.py [--ground-only OUT.png] [--preview OUT.png] [--apply] [--repaint]

Keeps the park's topology (loop path round the koi lake, stream with bridge, gazebo
and Rain Garden gate, viewing terrace) so every quest point keeps its meaning, and
rebuilds everything else: organic lake with sand shore, reeds and an island, fishing
pier, flower court round the gazebo, picnic meadow, lantern walk, community garden,
groves instead of a single tree ring. Lake/stream shapes come from the old colliders
(smoothed), so collision follows the painted water.
"""
import sys, json, hashlib
from pathlib import Path
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paint import Canvas, rgb, hash2, bake_details, wear, moss   # noqa: E402
from ground import dist_from, noise, classify, PATH as G_PATH  # noqa: E402
import common                                                  # noqa: E402

AREA = 'taman_kota'
S = 1.25
W, H = 2400, 1760
SEED = int(hashlib.sha256(b'taman_kota_v6').hexdigest()[:8], 16)
A = common.A
_OLD = None


def old_area():
    """The pre-v6 area (from git HEAD~ data if already migrated)."""
    global _OLD
    if _OLD is None:
        M = json.loads((A / 'data/maps.json').read_text(encoding='utf-8'))
        a = M['areas'][AREA]
        if a.get('v6Layout'):
            a = json.loads((Path(__file__).resolve().parent / 'pre_v6' / (AREA + '.json')).read_text(encoding='utf-8'))
        _OLD = a
    return _OLD


def old_image():
    p = Path(__file__).resolve().parent / 'pre_v6' / (AREA + '.png')
    return np.array(Image.open(p if p.exists() else A / 'maps/taman_kota.png').convert('RGB'))


def up(mask_small):
    """Upscale an old-resolution mask x1.25 and smooth the 16px stair steps away."""
    im = Image.fromarray(mask_small.astype(np.uint8) * 255).resize((W, H), Image.BILINEAR)
    from PIL import ImageFilter
    im = im.filter(ImageFilter.GaussianBlur(9))
    return np.array(im) > 127


def water_masks():
    a = old_area()
    mk = np.zeros((1408, 1920), bool)
    for x, y, w, h in a['walls']:
        if w >= 1900 or h >= 640 or w == 20 or (h == 20 and (y == 0 or y >= 1388)):
            continue
        mk[y:y + h, x:x + w] = True
    coll = up(mk)
    # painted water: close the bridge gap so the stream runs under the bridge
    bx, by = 1215, 1192
    mk2 = mk.copy()
    mk2[by - 60:by + 20, bx - 30:bx + 30] |= True
    col = mk2[:, bx - 30:bx + 30].any(axis=1)
    paint = up(mk2)
    return coll, paint


def path_mask():
    t, _ = classify(old_image())
    small = np.repeat(np.repeat(t == G_PATH, 4, 0), 4, 1)[:1408, :1920]
    return up(small)


# --------------------------------------------------------------------------- features
ISLAND = (690, 930, 74, 40)
PIER = (1236, 1032, 104, 34)          # fishing pier east of the south lobe
GAZEBO_COURT = (1875, 590, 190, 120)  # ellipse round the gazebo
PICNIC = (1890, 1280, 260, 150)
GARDEN = (1040, 1560, 380, 140)


def _paint(placed=None, Pdef=None):
    c = Canvas(W, H, SEED)
    G, P_, ST, D, WT, DIRT, SAND = 1, 2, 3, 5, 6, 7, 8
    c.put(np.ones((H, W), bool), c.grass(('#5a9c5e', '#62a464', '#6aac69', '#72b36e', '#7cba74', '#87c27b')), G)
    # picnic meadow: lighter, flowery lawn
    pm = c.wobble(c.ellipse(PICNIC[0], PICNIC[1], PICNIC[2], PICNIC[3]), 6, 18, 2)
    c.img[pm] = c.img[pm] * 1.05 + 4
    # paths (topology from the old park), gravel look
    pth = path_mask()
    pth = c.wobble(pth, 2, 6, 1)
    c.put(pth, c.dirt(('#b39a74', '#bea67f', '#c8b18b', '#d3bd98')), DIRT)
    # gazebo flower court: radial stone + rose border
    gx, gy, grx, gry = GAZEBO_COURT
    court = c.ellipse(gx, gy, grx, gry)
    rad, r, th, ri = c.radial(gx, gy, gry / grx, ('#d4c7b4', '#dcd0be', '#e4d9c8', '#ebe2d3'), 10, 18, salt=4, mortar='#a99a85')
    c.put(court, rad, ST)
    ring = court & (r > grx - 10)
    c.img[ring] = rgb('#9d8b74')
    # water: shore sand ring, depth, island, lilies
    coll, wpaint = water_masks()
    shore = c.wobble(dist_from(wpaint, 14) < 12, 2, 5, 3) & ~wpaint
    c.put(shore & (c.mat != ST), c.dirt(('#cdb58a', '#d6bf95', '#dfc9a1', '#e7d3ad')), SAND)
    isl = c.wobble(c.ellipse(*ISLAND), 3, 7, 4)
    lake = wpaint & ~isl
    c.put(lake, c.water(lake, ('#1f5378', '#27638a', '#30759c', '#3d89ae', '#57a0c2')), WT)
    c.put(isl, c.grass(), G)
    isl_sh = isl & (dist_from(~isl, 6) < 5)
    c.img[isl_sh] = c.img[isl_sh] * 0.5 + rgb('#cdb58a') * 0.5
    dl = dist_from(~lake, 4)
    c.img[lake & (dl == 1)] = c.img[lake & (dl == 1)] * 0.35 + rgb('#d9eef5') * 0.65
    c.img[lake & (dl == 2)] = c.img[lake & (dl == 2)] * 0.7 + rgb('#d9eef5') * 0.3
    rng = np.random.default_rng(SEED + 9)
    ys, xs = np.nonzero(lake & (dist_from(~lake, 40) > 10))
    for i in rng.integers(0, len(ys), 90):
        x, y = xs[i], ys[i]
        rr = rng.integers(4, 9)
        pad = c.ellipse(x, y, rr * 1.3, rr * 0.8) & lake
        c.img[pad] = rgb('#4c8c48'); c.img[pad & (c.yy < y - rr * 0.4)] = rgb('#68a75a')
        c.img[pad & (c.yy == y) & (c.xx > x)] = rgb('#27638a')
        if rng.random() < 0.3:
            c.img[y - 1:y + 1, x - 1:x + 1] = rgb('#f7c9d9') if rng.random() < 0.7 else rgb('#fbf6ec')
    # fishing pier (planks over the water)
    pr = c.rect(*PIER)
    c.put(pr, c.planks(('#8b5d3c', '#996a46', '#a5754f'), 8, salt=5, vertical=True), D)
    c.img[pr & ~c.rect(PIER[0], PIER[1] + 3, PIER[2], PIER[3] - 6)] = rgb('#5e3b27')
    c.img[c.rect(PIER[0], PIER[1] + PIER[3], PIER[2], 5) & lake] *= 0.65
    # community garden beds (tilled soil rows)
    gx0, gy0, gw0, gh0 = GARDEN
    for k in range(4):
        bed = c.rrect(gx0 + k * 96, gy0, 80, gh0, 8) & ~wpaint
        soil = c.dirt(('#6e5038', '#7a5a3f', '#866447', '#916f50'))
        rows = ((c.yy - gy0) % 14) < 3
        soil[rows] *= 0.78
        c.put(bed, soil, DIRT)
    # map border vignette
    bd = np.minimum.reduce([c.xx, c.yy, W - 1 - c.xx, H - 1 - c.yy])
    c.img[bd < 6] *= 0.85
    grass = c.mat == G
    hard = np.isin(c.mat, [ST, D])
    c.rim(hard, grass)
    c.rim(c.mat == DIRT, grass, dark='#7d6446', ao=(0.88, 0.95))
    c.overhang(np.isin(c.mat, [DIRT, ST]), grass, 0.33)
    wear(c, c.mat == DIRT, 0.06, salt=3)
    moss(c, c.mat == ST, grass, 0.5)
    flowers = [rgb(h) for h in ('#fbf6ec', '#f7c9d9', '#f4d870', '#c4b2f2', '#f29f9f')]
    for k in range(120):
        if k < 40:
            cx, cy = int(PICNIC[0] + rng.normal(0, PICNIC[2] * 0.5)), int(PICNIC[1] + rng.normal(0, PICNIC[3] * 0.5))
        else:
            cx, cy = rng.integers(40, W - 40), rng.integers(40, H - 40)
        col = flowers[rng.integers(0, len(flowers))]
        for _ in range(rng.integers(10, 26)):
            x = int(cx + rng.normal(0, 16)); y = int(cy + rng.normal(0, 9))
            if 1 <= x < W - 1 and 1 <= y < H - 2 and grass[y, x] and grass[y + 1, x]:
                c.img[y, x] = col; c.img[y + 1, x] = rgb('#3f7a46')
    # roses round the gazebo court
    ys, xs = np.nonzero(court & (r > grx - 10) & (r < grx - 4))
    for i in range(0, len(ys), 7):
        c.img[ys[i], xs[i]] = rgb('#e0607a') if (i // 7) % 3 else rgb('#f6c2d4')
    if placed is not None:
        bake_details(c, placed, Pdef, A, SEED)
    c.coll = coll
    return c


# --------------------------------------------------------------------------- props
def sc(x, y):
    return int(round(x * S)), int(round(y * S))


KEEP = ('v43_bridge_park', 'v43_v41_gazebo_gazebo', 'picnic_blanket', 'hedge_tk', 'garden_plot_tk', 'garden_plot_tk2',
        'v43_bench', 'v43_v41_flowerbed_flower', 'flowerbed', 'v43_lamp', 'signpost_n', 'lantern_off',
        'v51_approach_taman_kota', 'v51_planter_woodland', 'v51_garden_lamp', 'v51_bench_wood', 'v51_bush_lush',
        'v51_wildflowers', 'v51_birdbath', 'v51_step_stone', 'v51_trim_terrain')


_PROPS = None


def props():
    global _PROPS
    if _PROPS is None:
        _PROPS = _props()
    return [dict(p) for p in _PROPS]


def _props():
    out = []
    for p in old_area()['props']:
        if p['type'] in KEEP:
            q = dict(p); q['x'], q['y'] = sc(p['x'], p['y'])
            if p['type'] in ('garden_plot_tk', 'garden_plot_tk2'):
                continue
            out.append(q)
    add = lambda t, x, y, **kw: out.append(dict(type=t, x=int(x), y=int(y), **kw))
    # community garden: plots on the painted beds + tools
    for k in range(4):
        add(('garden_plot_tk', 'garden_plot_tk2', 'garden_plot_g140', 'garden_plot_g460')[k], GARDEN[0] + k * 96 + 40, GARDEN[1] + 60)
    add('crate', GARDEN[0] - 30, GARDEN[1] + 40); add('barrel', GARDEN[0] - 26, GARDEN[1] + 80)
    # fishing pier
    add('v44_pier_post', PIER[0] + PIER[2] - 4, PIER[1] + 4); add('v44_pier_post', PIER[0] + PIER[2] - 4, PIER[1] + PIER[3] + 2)
    add('v43_v41_rowboat_rv_rowboat', 1150, 1140)
    # island
    add('v43_v41_tree_green_willow', ISLAND[0], ISLAND[1] + 6); add('rock', ISLAND[0] + 40, ISLAND[1] + 20)
    # lake edge reeds and rocks
    for x, y in [(420, 900), (470, 1060), (1010, 820), (1180, 960), (900, 1190), (620, 1110), (1290, 1180)]:
        add('v51_reeds', x, y)
    # picnic meadow extras
    add('v44_picnic_blanket', PICNIC[0] - 120, PICNIC[1] + 40) if False else None
    add('v51_wildflowers', PICNIC[0] + 140, PICNIC[1] - 60)
    # trees: border groves + inner groves, kept off paths, water and quest points
    rng = np.random.default_rng(SEED + 3)
    c = _ground_cache()
    blocked = c.coll | (c.mat != 1)
    pts = _points()
    kinds = ['tree_green', 'tree_cherry', 'tree_pine', 'tree_autumn', 'v43_v41_tree_cherry_cherry', 'tree_oak', 'v43_v41_tree_green_willow']
    wts = np.array([30, 22, 14, 12, 6, 6, 4], float); wts /= wts.sum()
    cand = []
    for _ in range(9000):
        x, y = rng.integers(40, W - 40), rng.integers(90, H - 6)
        edge = min(x, W - x, y, H - y)
        p = 0.9 if edge < 150 else 0.022
        if rng.random() > p:
            continue
        cand.append((x, y))
    placed = []
    for x, y in cand:
        if blocked[max(0, y - 60):y + 10, max(0, x - 40):x + 40].any():
            continue
        if any((x - px) ** 2 + ((y - py) * 1.4) ** 2 < (70 if min(x, W - x, y, H - y) < 150 else 150) ** 2 for px, py in placed):
            continue
        if any((x - qx) ** 2 + (y - qy) ** 2 < 85 ** 2 for qx, qy in pts):
            continue
        if any(abs(x - q['x']) < 70 and -30 < y - q['y'] < 120 for q in out):
            continue
        placed.append((x, y))
        add(rng.choice(kinds, p=wts), x, y)
    for x, y in placed[::5]:
        if not blocked[y - 2, min(W - 1, x + 44)]:
            add(('bush', 'bush_berry', 'mushrooms', 'rock')[rng.integers(0, 4)], x + 44, y + 4)
    return out


_C = None


def _ground_cache():
    global _C
    if _C is None:
        _C = _paint()
    return _C


def _points():
    Q = json.loads((A / 'data/quests.json').read_text(encoding='utf-8'))
    already = bool(json.loads((A / 'data/maps.json').read_text(encoding='utf-8'))['areas'][AREA].get('v6Layout'))
    f = (lambda x, y: (x, y)) if already else remap_point
    pts = [(m[3], m[4]) for m in common.migrate_quests(Q, AREA, f)]
    pts += [(e['x'] * (1 if already else S), e['y'] * (1 if already else S)) for e in old_area()['examine']]
    pts += list(DOOR_TARGETS.values())
    return pts


# --------------------------------------------------------------------------- data
OVERRIDES = {}
DOOR_TARGETS = {'plaza_to_park': (2330, 875), 'forest_to_park': (1200, 80), 'rain_garden_to_park': (1988, 640)}
TERR = dict(x=1356, y=444, w=168, h=92, rise=26, stairLength=78, stairWidth=56)
SITE = dict(x=TERR['x'], y=TERR['y'], w=168, h=92, stair=78, rise=26, stairWidth=56,
            reason='Taman Kota v6: teras pemandang di utara danau, menghadap kolam koi dan jalan lingkar')


def remap_point(x, y):
    return OVERRIDES.get((x, y), sc(x, y))


def area_entry(old, c):
    a = dict(old)
    walls = [[0, 0, 20, 875 - 70], [0, 875 + 70, 20, H], [2380, 0, 20, 812], [2380, 950, 20, H - 950],
             [0, 0, 1125, 20], [1275, 0, W - 1275, 20], [0, H - 20, W, 20]]
    coll = c.coll.copy()
    coll[c.rect(*PIER)] = False
    walls += common.mask_to_walls(coll, 8)
    a.update(w=W, h=H, spawn=[2300, 880], walls=walls, ellipses=[], props=props())
    a['water'] = [{'cx': 800, 'cy': 950, 'rx': 350, 'ry': 188}, {'cx': 1075, 'cy': 1075, 'rx': 175, 'ry': 112}]
    doors = {d['id']: dict(d) for d in old['doors']}
    doors['park_to_forest']['rect'] = [1125, 0, 150, 18]
    doors['park_to_plaza']['rect'] = [2382, 812, 18, 138]
    r = doors['park_to_rain_garden']['rect']
    doors['park_to_rain_garden']['rect'] = [int(r[0] * S), int(r[1] * S), int(r[2] * S), int(r[3] * S)]
    a['doors'] = [doors[d['id']] for d in old['doors']]
    a['examine'] = [dict(e, x=sc(e['x'], e['y'])[0], y=sc(e['x'], e['y'])[1]) for e in old['examine']]
    a['animals'] = []
    for an in old['animals']:
        an = dict(an)
        if 'region' in an:
            an['region'] = [int(v * S) for v in an['region']]
        if 'water' in an:
            an['water'] = [800, 950, 300, 150]
        a['animals'].append(an)
    a['elevationPlatforms'] = [dict(old['elevationPlatforms'][0], **{k: TERR[k] for k in ('x', 'y', 'w', 'h', 'rise', 'stairLength', 'stairWidth')})]
    a.pop('v41PropReplacementIndex', None)
    a['visualStyle'] = 'v6_designed_layout'
    a['visualUpdate'] = 'v6_taman_kota_redesign'
    a['v6Layout'] = {'version': 1, 'generator': 'tools/v6/worldgen/taman_kota_v6.py', 'scaleFromV5': S,
                     'districts': ['koi lake + island + fishing pier', 'stream + bridge', 'gazebo flower court + Rain Garden gate',
                                   'picnic meadow', 'community garden', 'viewing terrace', 'woodland groves']}
    return a


def paint_ground():
    Pd = json.loads((A / 'data/props.json').read_text(encoding='utf-8'))['props']
    c = _paint(props(), Pd)
    c.coll = _ground_cache().coll
    return c


if __name__ == '__main__':
    pre = Path(__file__).resolve().parent / 'pre_v6'
    pre.mkdir(exist_ok=True)
    M = json.loads((A / 'data/maps.json').read_text(encoding='utf-8'))
    if not M['areas'][AREA].get('v6Layout') and not (pre / (AREA + '.json')).exists():
        (pre / (AREA + '.json')).write_text(json.dumps(M['areas'][AREA], ensure_ascii=False), encoding='utf-8')
        Image.open(A / 'maps/taman_kota.png').convert('RGB').save(pre / (AREA + '.png'))
    if '--repaint' in sys.argv:
        Pd = json.loads((A / 'data/props.json').read_text(encoding='utf-8'))['props']
        c = _paint(M['areas'][AREA]['props'], Pd)
        Image.fromarray(c.result(), 'RGB').save(A / M['areas'][AREA]['image'], optimize=True)
    else:
        common.run(sys.modules[__name__])
