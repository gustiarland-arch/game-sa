#!/usr/bin/env python3
"""HD remaster of the generated outdoor maps for the Godot build.

Keeps every map's size, collision walls, doors, quest points and examine spots, so the story and
saves are unaffected. What changes:
  * ground repainted at 2 texels per world unit (grass, paths, paving, sand, water with foam,
    cliffs) from the material layout of the current map, with smooth edges instead of 4-unit steps
  * vegetation and small street furniture swapped for the matching HD kit sprite (one art set)
  * soft contact shadows baked under every standing prop, so nothing floats on the ground
The source layout is read from tools/godot/pre_hd/<area>.png, a copy of the map image taken the
first time an area is remastered, so the tool can be re-run safely.

Usage: python3 tools/godot/hd_remaster.py <area|all> [--preview out.png] [--apply]
"""
import sys, json, hashlib, shutil
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/v6/worldgen'))
from paint import Canvas, rgb, wear, moss                              # noqa: E402
from ground import classify, dist_from, GRASS as C_GRASS, PATH as C_PATH, STONE as C_STONE, SAND as C_SAND, \
    WATER as C_WATER, DREAM as C_DREAM, DPATH as C_DPATH                   # noqa: E402
from hdmap import HDMap, K, TILE                                         # noqa: E402
import common                                                             # noqa: E402

A = ROOT / 'android' / 'assets'
PRE = Path(__file__).resolve().parent / 'pre_hd'
G, PV, ST, DK, WT, DIRT, SAND, CLIFF = 1, 2, 3, 5, 6, 7, 8, 4

AREAS = {
    'plaza': dict(keep_ground=True),   # designed paving and radial court: keep, props only
    'riverside': dict(),
    'dermaga': dict(),
    'hutan_bisik': dict(dark=True),
    'bukit_bintang': dict(),
    'memory_garden': dict(realm=True),
    'lantern_field': dict(realm=True),
    'star_path': dict(realm=True),
    'starfall_village': dict(realm=True),
    'eternal_garden': dict(realm=True),
}

# old prop type -> HD kit variants (picked by position so the choice is stable)
SWAP = {
    'tree_pine': ['hd_tree_pine_a', 'hd_tree_pine_b'],
    'tree_green': ['hd_tree_oak_a', 'hd_tree_oak_b'],
    'tree_oak': ['hd_tree_oak_c', 'hd_tree_oak_a'],
    'tree_dark': ['hd_tree_dark_a', 'hd_tree_dark_b'],
    'tree_autumn': ['hd_tree_autumn_a', 'hd_tree_autumn_b'],
    'tree_cherry': ['hd_tree_cherry_a', 'hd_tree_cherry_b'],
    'v43_v41_tree_cherry_cherry': ['hd_tree_cherry_a', 'hd_tree_cherry_b'],
    'v41_tree_cherry_cherry': ['hd_tree_cherry_b', 'hd_tree_cherry_a'],
    'tree_lantern': ['hd_tree_lantern', 'hd_tree_lantern_b'],
    'v44_tree_lantern': ['hd_tree_lantern_b', 'hd_tree_lantern'],
    'v41_tree_lantern_cherry': ['hd_tree_lantern', 'hd_tree_dream_c'],
    'tree_dream': ['hd_tree_dream_a', 'hd_tree_dream_b', 'hd_tree_dream_c'],
    'v44_tree_dream': ['hd_tree_dream_b', 'hd_tree_dream_a'],
    'v43_v41_tree_green_willow': ['hd_tree_willow'],
    'v41_tree_dark_willow': ['hd_tree_willow'],
    'bush': ['hd_bush_a', 'hd_bush_b'],
    'hedge': ['hd_bush_a', 'hd_bush_b'],
    'bush_berry': ['hd_bush_berry', 'hd_bush_rose'],
    'rock': ['hd_rock_a', 'hd_rock_b'],
    'v51_rock_moss': ['hd_rock_b'],
    'mushrooms': ['hd_mushrooms'],
    'v51_mushroom_glow': ['hd_mushrooms_glow'],
    'crystal': ['hd_crystal', 'hd_crystal_cyan'],
    'v44_crystal': ['hd_crystal_cyan', 'hd_crystal'],
    'v41_crystal_crystal_cluster': ['hd_crystal'],
    'v51_rock_crystal': ['hd_crystal_cyan'],
    'star_stone': ['hd_star_stone'],
    'v41_star_stone_starrocks': ['hd_star_stone'],
    'lantern_post': ['hd_lantern_post'],
    'v44_lantern_post': ['hd_lantern_post'],
    'v51_reeds': ['hd_reeds'],
    'flowerbed': ['hd_flowerbed'],
    'v44_flowerbed': ['hd_flowerbed'],
    'v43_v41_flowerbed_flower': ['hd_flowerbed'],
    'v51_bench_wood': ['hd_bench'],
    'v43_bench': ['hd_bench'],
    'bench': ['hd_bench'],
    'bench_b': ['hd_bench'],
    'v43_lamp': ['hd_lamp'],
    'lamp': ['hd_lamp'],
    'v51_street_lamp': ['hd_lamp'],
    'v51_planter_terracotta': ['hd_planter_pink'],
    'v51_planter_lavender': ['hd_planter_violet'],
    'crate': ['hd_crate'],
    'barrel': ['hd_barrel'],
    'cafe_umbrella_table': ['hd_umbrella_table'],
    'v44_fence_bb': ['hd_fence_h'],
    'v51_signpost': ['hd_signpost'],
    'stall_flowers': ['hd_stall_red', 'hd_stall_blue'],
}


LAND_LEFTOVERS = {'v51_bridge_wood', 'v51_ramp_wood', 'v51_rail_wood', 'v51_rail_stone', 'v51_rail_metal'}


def shades(base, factors=(0.80, 0.87, 0.94, 1.0, 1.07, 1.15)):
    out = []
    for f in factors:
        c = np.clip(np.asarray(base, float) * f + (8 if f > 1 else 0), 0, 255).astype(int)
        out.append('#%02x%02x%02x' % tuple(c))
    return tuple(out)


def median_of(med, t, cls, fallback):
    sel = med[t == cls]
    return np.median(sel, axis=0) if len(sel) > 20 else np.array(fallback, float)


def smooth_up(mask_cells, W, H, blur=6, thr=127):
    """4-unit material cells -> smooth mask at K texels per unit."""
    im = Image.fromarray(mask_cells.astype(np.uint8) * 255)
    im = im.resize((W * K, H * K), Image.BILINEAR).filter(ImageFilter.GaussianBlur(blur))
    return np.array(im) > thr


class Remaster:
    def __init__(self, area):
        self.area = area
        self.cfg = AREAS[area]
        self.M = json.loads((A / 'data/maps.json').read_text(encoding='utf-8'))
        self.a = self.M['areas'][area]
        self.W, self.H = self.a['w'], self.a['h']
        PRE.mkdir(exist_ok=True)
        src = PRE / (area + '.png')
        if not src.exists():
            shutil.copy(A / self.a['image'], src)
        pre_json = PRE / (area + '.props.json')
        if not pre_json.exists():
            pre_json.write_text(json.dumps(self.a['props'], ensure_ascii=False), encoding='utf-8')
        self.old_props = json.loads(pre_json.read_text(encoding='utf-8'))
        self.src = np.array(Image.open(src).convert('RGB').resize((self.W, self.H), Image.NEAREST))
        self.seed = int(hashlib.sha256((area + '_godot_hd').encode()).hexdigest()[:8], 16)
        self.P = json.loads((A / 'data/props.json').read_text(encoding='utf-8'))['props']

    # ------------------------------------------------------------------ ground
    def paint(self):
        W, H, cfg = self.W, self.H, self.cfg
        if cfg.get('realm') or cfg.get('keep_ground'):
            # dream realms keep their painted ground (rune circles, glowing walkways); only the
            # props become HD and get contact shadows
            c = Canvas(W * K, H * K, self.seed)
            c.img = np.repeat(np.repeat(self.src.astype(np.float32), K, 0), K, 1)
            self.c = c
            return
        t, med = classify(self.src, 4)
        t = t[:H // 4, :W // 4]
        med = med[:H // 4, :W // 4]
        realm = cfg.get('realm', False)
        # baked prop shadows of the old art read as small dark blobs: blobs of water or rock smaller
        # than ~60x60 units become the surrounding ground again
        from scipy import ndimage
        for cls in (C_WATER, C_DREAM) if not realm else (C_WATER,):
            lab, n = ndimage.label(t == cls)
            if n:
                size = ndimage.sum(np.ones_like(lab), lab, index=np.arange(1, n + 1))
                small = np.isin(lab, np.nonzero(size < cfg.get('min_blob', 220))[0] + 1)
                t = t.copy()
                t[small] = C_GRASS if not realm else C_DREAM
        c = Canvas(W * K, H * K, self.seed)
        self.c = c
        water = smooth_up(t == C_WATER, W, H, 5)
        sand = smooth_up(t == C_SAND, W, H, 6) & ~water
        if realm:
            walk = smooth_up((t == C_DPATH) | (t == C_PATH) | (t == C_STONE) | (t == C_SAND), W, H, 6) & ~water
            stone, path, cliff = walk, np.zeros_like(walk), np.zeros_like(walk)
        else:
            stone = smooth_up(t == C_STONE, W, H, 6) & ~water
            path = smooth_up((t == C_PATH) | (t == C_DPATH), W, H, 6) & ~water & ~stone
            cliff = smooth_up(t == C_DREAM, W, H, 4) & ~water & ~stone & ~path
        # base ground
        if realm:
            base = median_of(med, t, C_DREAM, (92, 82, 150))
            gp = shades(base, (0.78, 0.85, 0.92, 1.0, 1.06, 1.12))
        else:
            base = median_of(med, t, C_GRASS, (96, 168, 100))
            if cfg.get('dark'):
                base = base * 0.92
            gp = shades(base)
        c.put(np.ones((H * K, W * K), bool), c.grass(gp), G)
        if realm:
            rng = np.random.default_rng(self.seed + 17)
            n = W * H * K * K // 900
            ys, xs = rng.integers(2, H * K - 2, n), rng.integers(2, W * K - 2, n)
            star = rgb('#f4f0ff')
            for y, x in zip(ys, xs):
                f = 0.55 + 0.45 * rng.random()
                c.img[y, x] = c.img[y, x] * (1 - f) + star * f
                if rng.random() < 0.1:
                    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                        c.img[y + dy, x + dx] = c.img[y + dy, x + dx] * 0.5 + star * 0.5
        # cliffs / rock outcrops (grey cells on real-world maps)
        if cliff.any():
            cb = median_of(med, t, C_DREAM, (128, 122, 116))
            face = c.bricks(shades(cb, (0.82, 0.9, 0.98, 1.05)), 30, 16, '#%02x%02x%02x' % tuple(np.clip(cb * 0.62, 0, 255).astype(int)), salt=31)
            c.put(cliff, face, CLIFF)
            top = cliff & ~np.roll(cliff, 12, 0)
            c.img[top] = np.clip(c.img[top] * 1.12 + 8, 0, 255)
            foot = (~cliff) & np.roll(cliff, 2, 0)
            for i, f in enumerate((0.6, 0.72, 0.84, 0.92)):
                m = np.roll(foot, i * 2, 0) & ~cliff & ~water
                c.img[m] *= f
        # paths
        if path.any():
            pb = median_of(med, t, C_PATH, (196, 170, 128))
            c.put(path, c.dirt(shades(pb, (0.88, 0.95, 1.0, 1.06))), DIRT)
        if stone.any():
            sb = median_of(med, t, C_DPATH if realm else C_STONE, (214, 200, 180))
            mortar = '#%02x%02x%02x' % tuple(np.clip(sb * 0.7, 0, 255).astype(int))
            if realm or cfg.get('paving'):
                pave = c.bricks(shades(sb, (0.9, 0.95, 1.0, 1.04, 1.08)), 40, 20, mortar, salt=21)
            else:
                pave = c.bricks(shades(sb, (0.9, 0.96, 1.0, 1.05)), 32, 18, mortar, salt=22)
            c.put(stone, pave, PV)
            if realm:
                halo = (~stone) & (dist_from(stone, 22) < 20) & ~water
                c.img[halo] = np.clip(c.img[halo] * 0.78 + sb * 0.3, 0, 255)
        if sand.any():
            c.put(sand, c.dirt(('#cdb58a', '#d6bf95', '#dfc9a1', '#e7d3ad')), SAND)
        if water.any():
            wb = median_of(med, t, C_WATER, (48, 117, 156))
            wp = shades(wb, (0.7, 0.82, 0.94, 1.06, 1.2))
            shore = (dist_from(water, 26) < 18) & ~water & ~stone & (c.mat == G)
            c.put(shore, c.dirt(('#cdb58a', '#d6bf95', '#dfc9a1', '#e7d3ad')), SAND)
            c.put(water, c.water(water, wp), WT)
            dl = dist_from(~water, 8)
            foam = rgb('#dcf0f6')
            for i, f in ((1, 0.7), (2, 0.55), (3, 0.3), (4, 0.15)):
                sel = water & (dl == i)
                c.img[sel] = c.img[sel] * (1 - f) + foam * f
        self.water = water
        # finishing
        grass = c.mat == G
        hard = np.isin(c.mat, [ST, PV, DK])
        c.rim(hard, grass)
        c.rim(c.mat == DIRT, grass, dark='#7d6446', ao=(0.88, 0.95))
        c.overhang(np.isin(c.mat, [DIRT, PV]), grass, 0.3)
        wear(c, c.mat == DIRT, 0.05, salt=3)
        moss(c, np.isin(c.mat, [PV]), grass, 0.4)
        rng = np.random.default_rng(self.seed + 9)
        flowers = [rgb(h) for h in (('#fbf6ec', '#c4b2f2', '#9fd6f2', '#f7c9d9') if realm else ('#fbf6ec', '#f7c9d9', '#f4d870', '#c4b2f2', '#f29f9f'))]
        for _ in range(int(W * H / 26000)):
            cx, cy = rng.integers(40, W * K - 40), rng.integers(40, H * K - 40)
            col = flowers[rng.integers(0, len(flowers))]
            for _ in range(rng.integers(8, 20)):
                x = int(cx + rng.normal(0, 22)); y = int(cy + rng.normal(0, 12))
                if 2 <= x < W * K - 3 and 2 <= y < H * K - 4 and grass[y, x] and grass[y + 2, x]:
                    c.img[y:y + 2, x:x + 2] = col
                    c.img[y + 2:y + 4, x] = rgb('#3f7a46') if not realm else c.img[y + 2:y + 4, x] * 0.7
        edge = np.minimum.reduce([c.xx, c.yy, W * K - 1 - c.xx, H * K - 1 - c.yy])
        c.img[edge < 10] *= 0.86

    # ------------------------------------------------------------------ props
    def props(self):
        out = []
        water = getattr(self, 'water', None)
        for p in self.old_props:
            # leftovers of the removed v5.1 terraces: deck, ramp and rail pieces standing on dry grass
            if p['type'] in LAND_LEFTOVERS and water is not None:
                y, x = int(p['y'] * K) - 8, int(p['x'] * K)
                if not water[max(0, y - 40):y + 40, max(0, x - 60):x + 60].any():
                    continue
            q = dict(p)
            v = SWAP.get(p['type'])
            if v and all(x in self.P for x in v):
                q['type'] = v[(p['x'] * 7 + p['y'] * 3) % len(v)]
            out.append(q)
        return out

    def run(self, apply=False, preview=None):
        self.paint()
        props = self.props()
        m = HDMap(self.area, self.W, self.H, self.seed)
        m.c = self.c
        m.props = props
        m.bake_shadows(self.P)
        img = np.clip(self.c.img, 0, 255).astype(np.uint8)
        a = dict(self.a)
        a['props'] = props
        a['visualStyle'] = 'godot_hd_remaster'
        a['visualUpdate'] = 'godot_hd_remaster'
        tiles = []
        for ty in range(0, self.c.h, TILE):
            for tx in range(0, self.c.w, TILE):
                tiles.append(dict(image='maps/hd/%s_%d_%d@2x.png' % (self.area, ty // TILE, tx // TILE),
                                  x=tx // K, y=ty // K, w=min(TILE, self.c.w - tx) // K, h=min(TILE, self.c.h - ty) // K))
        a['tiles'] = tiles
        # validate: every quest point, examine spot and door arrival still reachable
        Q = json.loads((A / 'data/quests.json').read_text(encoding='utf-8'))
        pts = [(mm[0], mm[3], mm[4], mm[5]) for mm in common.migrate_quests(Q, self.area, lambda x, y: (x, y))]
        pts += [('examine ' + e['id'], e['x'], e['y'], e.get('r')) for e in a.get('examine', [])]
        pts += [(d['id'], d['tx'], d['ty'], None) for b in self.M['areas'].values() for d in b.get('doors', []) if d.get('to') == self.area]
        bad = common.validate(a, self.P, pts)
        for b in bad:
            print('INVALID', *b)
        swapped = sum(1 for q in props if q['type'].startswith('hd_'))
        print('dropped', len(self.old_props) - len(props), 'leftover pieces on land')
        print(self.area, len(props), 'props (%d swapped to HD),' % swapped, len(pts), 'points,', len(bad), 'invalid')
        if preview:
            hd = Image.fromarray(img).convert('RGBA')
            for pr in sorted(props, key=lambda p: (self.P[p['type']].get('layer') != 'floor', p['y'])):
                d = self.P.get(pr['type'])
                if not d:
                    continue
                tex = Image.open(A / d['image']).convert('RGBA')
                k = 1 if '@2x' in d['image'] else 2
                if k == 2:
                    tex = tex.resize((tex.width * 2, tex.height * 2), Image.NEAREST)
                hd.alpha_composite(tex, (int(pr['x'] * K - tex.width / 2), int(pr['y'] * K - tex.height)))
            hd.convert('RGB').resize((self.W, self.H), Image.LANCZOS).save(preview)
        if apply:
            if bad:
                raise SystemExit('not applied: fix invalid points first')
            (A / 'maps/hd').mkdir(parents=True, exist_ok=True)
            for tl in tiles:
                X, Y = tl['x'] * K, tl['y'] * K
                Image.fromarray(img[Y:Y + tl['h'] * K, X:X + tl['w'] * K]).save(A / tl['image'], optimize=True)
            M = json.loads((A / 'data/maps.json').read_text(encoding='utf-8'))
            M['areas'][self.area] = a
            (A / 'data/maps.json').write_text(json.dumps(M, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            print('applied', len(tiles), 'tiles')
        return bad


def main():
    args = sys.argv[1:]
    which = args[0]
    prev = args[args.index('--preview') + 1] if '--preview' in args else None
    areas = list(AREAS) if which == 'all' else which.split(',')
    for ar in areas:
        p = prev.replace('.png', '_%s.png' % ar) if (prev and len(areas) > 1) else prev
        Remaster(ar).run(apply='--apply' in args, preview=p)


if __name__ == '__main__':
    main()
