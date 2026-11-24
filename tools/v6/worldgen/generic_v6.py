"""Generic v6 outdoor-map rebuild (x1.25), configured per area.

Usage: python3 tools/v6/worldgen/generic_v6.py <area> [--preview OUT.png] [--apply] [--repaint]

Topology comes from the pre-v6 map so quests keep their meaning:
  * paths      = 'path' cells of the old ground image (classified), scaled and smoothed
  * water      = 'water' cells of the old ground image, scaled and smoothed (painted)
  * collision  = old interior walls, scaled and smoothed (so blocking follows the art)
  * props      = old non-vegetation props at scaled positions; vegetation is re-planted
                 as groves (dense borders, sparse interior) away from paths and quest points
Each area adds its own features through CONFIG[area] hooks (paint + props).
"""
import sys, json, hashlib, importlib
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from paint import Canvas, rgb, hash2, bake_details, wear, moss   # noqa: E402
from ground import dist_from, noise, classify, PATH as C_PATH, WATER as C_WATER, STONE as C_STONE, SAND as C_SAND  # noqa: E402
import common                                                     # noqa: E402

A = common.A
S = 1.25
G, PV, ST, DK, WT, DIRT, SAND = 1, 2, 3, 5, 6, 7, 8
VEG = ('tree', 'v41_tree', 'v43_v41_tree', 'v44_tree', 'v44_v41_tree', 'bush', 'rock', 'mushrooms', 'v51_bush_lush', 'v51_wildflowers')


class Ctx:
    def __init__(self, area):
        self.area = area
        pre = HERE / 'pre_v6'
        pre.mkdir(exist_ok=True)
        M = json.loads((A / 'data/maps.json').read_text(encoding='utf-8'))
        cur = M['areas'][area]
        pj, pp = pre / (area + '.json'), pre / (area + '.png')
        if not cur.get('v6Layout') and not pj.exists():
            pj.write_text(json.dumps(cur, ensure_ascii=False), encoding='utf-8')
            Image.open(A / cur['image']).convert('RGB').save(pp)
        self.old = json.loads(pj.read_text(encoding='utf-8')) if pj.exists() else cur
        self.migrated = bool(cur.get('v6Layout'))
        self.cur = cur
        self.img = np.array(Image.open(pp if pp.exists() else A / cur['image']).convert('RGB'))
        self.OW, self.OH = self.old['w'], self.old['h']
        self.W, self.H = int(round(self.OW * S)), int(round(self.OH * S))
        self.seed = int(hashlib.sha256((area + '_v6').encode()).hexdigest()[:8], 16)
        self.cfg = CONFIG.get(area, {})

    def grass_palette(self):
        t, med = classify(self.img)
        sel = med[(t == 0) | (t == 5)]
        base = np.median(sel, axis=0) if len(sel) else np.array([104, 172, 106], float)
        cols = []
        for f in (0.80, 0.87, 0.94, 1.0, 1.07, 1.15):
            c = np.clip(base * f + (8 if f > 1 else 0), 0, 255).astype(int)
            cols.append('#%02x%02x%02x' % tuple(c))
        return tuple(cols)

    def sc(self, x, y):
        return int(round(x * S)), int(round(y * S))

    def up(self, small, blur=9, thr=127):
        im = Image.fromarray(small.astype(np.uint8) * 255).resize((self.W, self.H), Image.BILINEAR)
        return np.array(im.filter(ImageFilter.GaussianBlur(blur))) > thr

    def is_border(self, r):
        """Thin map-edge wall (kept as an edge wall, not painted)."""
        x, y, w, h = r
        return (w <= 24 and (x <= 0 or x + w >= self.OW)) or (h <= 24 and (y <= 0 or y + h >= self.OH))

    def wall_mask(self):
        mk = np.zeros((self.OH, self.OW), bool)
        for r in self.old['walls']:
            if self.is_border(r):
                continue
            x, y, w, h = r
            mk[y:y + h, x:x + w] = True
        return mk

    def terrain(self):
        t, med = classify(self.img)
        cell = lambda k: np.repeat(np.repeat(t == k, 4, 0), 4, 1)[:self.OH, :self.OW]
        return cell(C_PATH) | cell(C_STONE) | cell(C_SAND), cell(C_WATER)


# ----------------------------------------------------------------------------- painting
def paint(ctx, placed=None, Pdef=None):
    cfg = ctx.cfg
    W, H = ctx.W, ctx.H
    c = Canvas(W, H, ctx.seed)
    c.put(np.ones((H, W), bool), c.grass(cfg.get('grass') or ctx.grass_palette()), G)
    old_path, old_water = ctx.terrain()
    wmask = ctx.wall_mask()
    coll = ctx.up(wmask)
    water = ctx.up(old_water | (wmask if cfg.get('walls_are_water', False) else np.zeros_like(wmask)))
    for hook in cfg.get('water_fill', []):          # e.g. close a gap under a bridge
        water |= hook(c)
    path = c.wobble(ctx.up(old_path, cfg.get('path_blur', 5), cfg.get('path_thr', 95)) & ~water & ~coll, 2, 6, 1)
    c.put(path, c.dirt(cfg.get('path_pal', ('#b39a74', '#bea67f', '#c8b18b', '#d3bd98'))), DIRT)
    if water.any():
        sw = cfg.get('shore', 12)
        shore = c.wobble(dist_from(water, sw + 4) < sw, 2, 5, 3) & ~water
        c.put(shore, c.dirt(('#cdb58a', '#d6bf95', '#dfc9a1', '#e7d3ad')), SAND)
        c.put(water, c.water(water, cfg.get('water_pal', ('#1f5378', '#27638a', '#30759c', '#3d89ae', '#57a0c2'))), WT)
        dl = dist_from(~water, 4)
        c.img[water & (dl == 1)] = c.img[water & (dl == 1)] * 0.35 + rgb('#d9eef5') * 0.65
        c.img[water & (dl == 2)] = c.img[water & (dl == 2)] * 0.7 + rgb('#d9eef5') * 0.3
    cliff_all = coll & ~water & ~ctx.up(old_water, 9, 60)
    e = 34                                                         # carry blocked areas out to the map edge
    cliff_all[H - e:, :] |= cliff_all[H - e - 1, :][None, :]
    cliff_all[:e, :] |= cliff_all[e, :][None, :]
    cliff_all[:, W - e:] |= cliff_all[:, W - e - 1][:, None]
    cliff_all[:, :e] |= cliff_all[:, e][:, None]
    deep = cliff_all & (dist_from(~cliff_all, 34) >= 34)          # interior of big blocked areas stays ground
    cliff = cliff_all & ~deep
    c.deep = deep
    if cliff.any():
        top = cliff & ~np.roll(cliff, 8, 0)                       # upper lip (grass edge seen from above)
        face = c.bricks(cfg.get('cliff_pal', ('#7f7a73', '#8b857d', '#979087', '#a39b91')), 14, 8, '#5b5650', salt=31)
        c.put(cliff, face, ST)
        c.img[cliff] *= 0.92
        lip = c.bricks(('#a8a196', '#b4ada1', '#bfb8ab'), 20, 6, '#7c766d', salt=32)
        c.img[top] = lip[top]
        foot = (~cliff) & np.roll(cliff, -1, 0) & ~water
        for i, f in enumerate((0.62, 0.74, 0.86)):
            m = np.roll(foot, i, 0) & ~cliff
            c.img[m] *= f
    c.water_mask = water
    c.coll = coll
    for hook in cfg.get('paint', []):
        hook(c, ctx)
    bd = np.minimum.reduce([c.xx, c.yy, W - 1 - c.xx, H - 1 - c.yy])
    c.img[bd < 6] *= 0.85
    grass = c.mat == G
    hard = np.isin(c.mat, [ST, DK, PV])
    c.rim(hard, grass)
    c.rim(c.mat == DIRT, grass, dark='#7d6446', ao=(0.88, 0.95))
    c.overhang(np.isin(c.mat, [DIRT, ST, PV]), grass, 0.33)
    wear(c, c.mat == DIRT, 0.06, salt=3)
    moss(c, np.isin(c.mat, [ST, PV]), grass, 0.5)
    rng = np.random.default_rng(ctx.seed + 9)
    if water.any() and cfg.get('lilies', 60):
        ys, xs = np.nonzero(water & (dist_from(~water, 60) > 12) & (dist_from(~water, 90) < 80))
        for i in rng.integers(0, len(ys), cfg.get('lilies', 60)):
            x, y = xs[i], ys[i]; rr = rng.integers(4, 9)
            pad = c.ellipse(x, y, rr * 1.3, rr * 0.8) & water
            c.img[pad] = rgb('#4c8c48'); c.img[pad & (c.yy < y - rr * 0.4)] = rgb('#68a75a')
            c.img[pad & (c.yy == y) & (c.xx > x)] = rgb('#27638a')
            if rng.random() < 0.3:
                c.img[y - 1:y + 1, x - 1:x + 1] = rgb('#f7c9d9')
    flowers = [rgb(h) for h in cfg.get('flowers', ('#fbf6ec', '#f7c9d9', '#f4d870', '#c4b2f2', '#f29f9f'))]
    for _ in range(int(W * H / 48000)):
        cx, cy = rng.integers(40, W - 40), rng.integers(40, H - 40)
        col = flowers[rng.integers(0, len(flowers))]
        for _ in range(rng.integers(10, 26)):
            x = int(cx + rng.normal(0, 16)); y = int(cy + rng.normal(0, 9))
            if 1 <= x < W - 1 and 1 <= y < H - 2 and grass[y, x] and grass[y + 1, x]:
                c.img[y, x] = col; c.img[y + 1, x] = rgb('#3f7a46')
    if placed is not None:
        bake_details(c, placed, Pdef, A, ctx.seed)
    return c


# ----------------------------------------------------------------------------- props
def base_props(ctx, ground):
    out = []
    for p in ctx.old['props']:
        if p['type'].startswith(VEG) and p['type'] not in ctx.cfg.get('keep_veg', ()):
            continue
        q = dict(p); q['x'], q['y'] = ctx.sc(p['x'], p['y'])
        out.append(q)
    for hook in ctx.cfg.get('props', []):
        out.extend(hook(ctx, ground))
    plant(ctx, ground, out)
    return out


def points(ctx):
    Q = json.loads((A / 'data/quests.json').read_text(encoding='utf-8'))
    f = (lambda x, y: (x, y)) if ctx.migrated else remap(ctx)
    pts = [(m[3], m[4]) for m in common.migrate_quests(Q, ctx.area, f)]
    pts += [ctx.sc(e['x'], e['y']) for e in ctx.old.get('examine', [])]
    pts += [door_target(ctx, d) for d in incoming(ctx)]
    return pts


def plant(ctx, c, out):
    W, H = ctx.W, ctx.H
    rng = np.random.default_rng(ctx.seed + 3)
    blocked = (c.coll & ~getattr(c, 'deep', np.zeros_like(c.coll))) | (c.mat != G)
    pts = points(ctx)
    kinds = ctx.cfg.get('trees', ['tree_green', 'tree_cherry', 'tree_pine', 'tree_autumn', 'v43_v41_tree_cherry_cherry', 'tree_oak', 'v43_v41_tree_green_willow'])
    wts = np.array(ctx.cfg.get('tree_weights', [30, 22, 14, 12, 6, 6, 4][:len(kinds)]), float); wts /= wts.sum()
    border, inner = ctx.cfg.get('density', (0.9, 0.022))
    keep_out = []
    for t in ctx.old.get('elevationPlatforms', []):             # terrace + stair corridor stay clear
        x0, y0 = ctx.sc(t['x'], t['y'])
        keep_out.append((x0 - 60, y0 - 40, t['w'] + 120, t['h'] + t['stairLength'] + 120))
    for d in ctx.old.get('doors', []):
        x0, y0, w0, h0 = scale_rect(ctx, d['rect'])
        keep_out.append((x0 - 70, y0 - 70, w0 + 140, h0 + 140))
    placed = []
    for _ in range(int(9000 * W * H / (2400 * 1760))):
        x, y = rng.integers(40, W - 40), rng.integers(90, H - 6)
        edge = min(x, W - x, y, H - y)
        if rng.random() > (border if edge < 150 else inner):
            continue
        if blocked[max(0, y - 60):y + 10, max(0, x - 40):x + 40].any():
            continue
        if any((x - px) ** 2 + ((y - py) * 1.4) ** 2 < (70 if min(x, W - x, y, H - y) < 150 else ctx.cfg.get('inner_gap', 150)) ** 2 for px, py in placed):
            continue
        if any((x - qx) ** 2 + (y - qy) ** 2 < 85 ** 2 for qx, qy in pts):
            continue
        if any(kx <= x <= kx + kw and ky <= y <= ky + kh + 60 for kx, ky, kw, kh in keep_out):
            continue
        if any(abs(x - q['x']) < 70 and -30 < y - q['y'] < 120 for q in out):
            continue
        placed.append((x, y))
        out.append(dict(type=str(rng.choice(kinds, p=wts)), x=int(x), y=int(y)))
    for x, y in placed[::5]:
        if x + 44 < W and not blocked[y - 2, x + 44]:
            out.append(dict(type=('bush', 'bush_berry', 'mushrooms', 'rock')[rng.integers(0, 4)], x=int(x + 44), y=int(y + 4)))


# ----------------------------------------------------------------------------- data
def remap(ctx):
    ov = ctx.cfg.get('overrides', {})
    return lambda x, y: ov.get((x, y), ctx.sc(x, y))


def incoming(ctx):
    M = json.loads((A / 'data/maps.json').read_text(encoding='utf-8'))
    return [d for a in M['areas'].values() for d in a.get('doors', []) if d.get('to') == ctx.area]


def door_target(ctx, d):
    if d['id'] in ctx.cfg.get('door_targets', {}):
        return ctx.cfg['door_targets'][d['id']]
    return (d['tx'], d['ty']) if ctx.migrated else ctx.sc(d['tx'], d['ty'])


def scale_rect(ctx, r):
    x, y, w, h = r
    nx, ny, nw, nh = int(round(x * S)), int(round(y * S)), int(round(w * S)), int(round(h * S))
    if x <= 0: nx, nw = 0, w
    if y <= 0: ny, nh = 0, h
    if x + w >= ctx.OW: nx, nw = ctx.W - w, w
    if y + h >= ctx.OH: ny, nh = ctx.H - h, h
    return [nx, ny, nw, nh]


def entry(ctx, old, c, props):
    a = dict(old)
    walls = [scale_rect(ctx, r) for r in old['walls'] if ctx.is_border(r)]
    coll = c.coll.copy()
    for hook in ctx.cfg.get('walk_on_water', []):
        coll &= ~hook(c)
    walls += common.mask_to_walls(coll, 8)
    a.update(w=ctx.W, h=ctx.H, walls=walls, props=props, spawn=list(ctx.sc(*old['spawn'])))
    a['ellipses'] = [[int(cx * S), int(cy * S), rw, rh] for cx, cy, rw, rh in old.get('ellipses', [])]
    a['water'] = [dict(w, cx=int(w['cx'] * S), cy=int(w['cy'] * S), rx=int(w['rx'] * S), ry=int(w['ry'] * S)) for w in old.get('water', [])]
    if 'waterFlow' in old:
        wf = []
        for f in old['waterFlow']:
            f = dict(f)
            for k in ('x', 'y', 'w', 'h'):
                if k in f:
                    f[k] = int(round(f[k] * S))
            if 'path' in f:
                f['path'] = [[int(round(p[0] * S)), int(round(p[1] * S))] for p in f['path']]
            if 'width' in f:
                f['width'] = int(round(f['width'] * S))
            wf.append(f)
        a['waterFlow'] = wf
    a['doors'] = [dict(d, rect=scale_rect(ctx, d['rect'])) for d in old['doors']]
    a['examine'] = [dict(e, x=ctx.sc(e['x'], e['y'])[0], y=ctx.sc(e['x'], e['y'])[1]) for e in old.get('examine', [])]
    an2 = []
    for an in old.get('animals', []):
        an = dict(an)
        if 'region' in an:
            an['region'] = [int(v * S) for v in an['region']]
        if 'water' in an:
            an['water'] = [int(an['water'][0] * S), int(an['water'][1] * S), int(an['water'][2] * S), int(an['water'][3] * S)]
        an2.append(an)
    a['animals'] = an2
    if old.get('elevationPlatforms'):
        t = dict(old['elevationPlatforms'][0])
        t['x'], t['y'] = ctx.sc(t['x'], t['y'])
        a['elevationPlatforms'] = [t]
    a.pop('v41PropReplacementIndex', None)
    a['visualStyle'] = 'v6_designed_layout'
    a['visualUpdate'] = 'v6_' + ctx.area + '_redesign'
    a['v6Layout'] = {'version': 1, 'generator': 'tools/v6/worldgen/generic_v6.py', 'scaleFromV5': S,
                     'districts': ctx.cfg.get('districts', [])}
    return a


def module_for(area):
    ctx = Ctx(area)
    mod = type(sys)('v6_' + area)
    mod.AREA = area
    cache = {}

    def ground():
        if 'g' not in cache:
            cache['g'] = paint(ctx)
        return cache['g']

    def props():
        if 'p' not in cache:
            cache['p'] = base_props(ctx, ground())
        return [dict(p) for p in cache['p']]

    def paint_ground():
        Pd = json.loads((A / 'data/props.json').read_text(encoding='utf-8'))['props']
        c = paint(ctx, props(), Pd)
        return c
    mod.paint_ground = paint_ground
    mod.props = props
    mod.area_entry = lambda old, c: entry(ctx, ctx.old, c, props())
    mod.remap_point = remap(ctx)
    mod.DOOR_TARGETS = {d['id']: door_target(ctx, d) for d in incoming(ctx)}
    t = ctx.old.get('elevationPlatforms')
    if t:
        x, y = ctx.sc(t[0]['x'], t[0]['y'])
        mod.SITE = dict(x=x, y=y)
    mod.ctx = ctx
    return mod


CONFIG = {}


def load_configs():
    import importlib.util
    p = HERE / 'areas_v6.py'
    spec = importlib.util.spec_from_file_location('areas_v6', p)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    CONFIG.update(m.CONFIG)


if __name__ == '__main__':
    load_configs()
    area = sys.argv[1]
    mod = module_for(area)
    if '--refresh' in sys.argv:
        # re-place props of an already migrated map, validate, then repaint
        import subprocess
        sys.modules['v6_' + area] = mod
        M = json.loads((A / 'data/maps.json').read_text(encoding='utf-8'))
        Q = json.loads((A / 'data/quests.json').read_text(encoding='utf-8'))
        Pd = json.loads((A / 'data/props.json').read_text(encoding='utf-8'))['props']
        a = M['areas'][area]
        a['props'] = mod.props()
        pts = [(m[0], m[3], m[4], m[5]) for m in common.migrate_quests(Q, area, lambda x, y: (x, y))]
        pts += [(d['id'], d['tx'], d['ty'], None) for b in M['areas'].values() for d in b.get('doors', []) if d.get('to') == area]
        bad = common.validate(a, Pd, pts)
        for b in bad:
            print('INVALID', *b)
        if bad:
            raise SystemExit('not refreshed')
        (A / 'data/maps.json').write_text(json.dumps(M, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        c = paint(mod.ctx, a['props'], Pd)
        Image.fromarray(c.result(), 'RGB').save(A / a['image'], optimize=True)
        print(area, 'refreshed')
    elif '--repaint' in sys.argv:
        M = json.loads((A / 'data/maps.json').read_text(encoding='utf-8'))
        Pd = json.loads((A / 'data/props.json').read_text(encoding='utf-8'))['props']
        c = paint(mod.ctx, M['areas'][area]['props'], Pd)
        Image.fromarray(c.result(), 'RGB').save(A / M['areas'][area]['image'], optimize=True)
    else:
        common.run(mod)
