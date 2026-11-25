"""Per-area configuration for generic_v6.py (features, palettes, overrides)."""
import numpy as np
from paint import rgb
from ground import dist_from


# ----------------------------------------------------------------------------- riverside
def rv_fill(c):
    return c.rect(1478, 840, 84, 260)          # water continues under the pier


def rv_paint(c, ctx):
    w = c.water_mask
    # far islet with a pebble beach (not reachable; decoration on the open lake)
    isl = c.wobble(c.ellipse(640, 1215, 120, 46), 3, 8, 7) & w
    beach = c.wobble(c.ellipse(640, 1215, 136, 56), 3, 8, 8) & w & ~isl
    c.put(beach, c.dirt(('#cdb58a', '#d6bf95', '#dfc9a1', '#e7d3ad')), 8)
    c.put(isl, c.grass(), 1)
    c.img[beach & (dist_from(~beach, 3) == 1)] = rgb('#e6f2f6')
    c.water_mask = w & ~(isl | beach)
    # rocky east shore: scattered boulders on the sand
    rng = np.random.default_rng(ctx.seed + 41)
    sand = c.mat == 8
    ys, xs = np.nonzero(sand & (c.xx > 1700))
    for i in rng.integers(0, len(ys), 40):
        y, x = ys[i], xs[i]; r = rng.integers(3, 7)
        m = c.ellipse(x, y, r * 1.3, r) & sand
        c.img[m] = rgb('#8f8a86'); c.img[m & (c.yy < y - r * 0.3)] = rgb('#b3aea8')
        c.img[c.ellipse(x + 1, y + r, r * 1.2, 2) & sand] *= 0.75


def rv_props(ctx, c):
    return [dict(type='v43_v41_tree_green_willow', x=610, y=1215), dict(type='tree_pine', x=690, y=1200),
            dict(type='rock', x=560, y=1232), dict(type='v44_fishing_hut', x=2130, y=850),
            dict(type='v44_v41_rowboat_b_rowboat', x=2010, y=930), dict(type='v51_reeds', x=300, y=905),
            dict(type='v51_reeds', x=880, y=880), dict(type='v51_reeds', x=1900, y=880),
            dict(type='v44_picnic_blanket', x=520, y=640), dict(type='v51_bench_wood', x=360, y=820)]


# ----------------------------------------------------------------------------- forest / hill
def leaf_litter(c, ctx):
    rng = np.random.default_rng(ctx.seed + 51)
    g = c.mat == 1
    cols = [rgb(h) for h in ('#7a5a32', '#946b38', '#5f7a3a', '#a87a3a')]
    for _ in range(c.w * c.h // 160):
        x, y = rng.integers(1, c.w - 2), rng.integers(1, c.h - 1)
        if g[y, x]:
            col = cols[rng.integers(0, 4)]
            c.img[y, x] = col
            if rng.random() < 0.5:
                c.img[y, x + 1] = col * 0.85
    # dappled canopy light
    from ground import noise
    v = noise(c.h, c.w, 50, ctx.seed + 52)
    lit = g & (v > 0.62)
    c.img[lit] = np.clip(c.img[lit] * 1.08 + 4, 0, 255)


def star_flowers(c, ctx):
    rng = np.random.default_rng(ctx.seed + 61)
    g = c.mat == 1
    for _ in range(c.w * c.h // 700):
        x, y = rng.integers(2, c.w - 2), rng.integers(2, c.h - 2)
        if g[y, x]:
            col = rgb(('#e8f4ff', '#bcd8ff', '#fff3b0')[rng.integers(0, 3)])
            c.img[y, x] = col
            if rng.random() < 0.25:
                c.img[y - 1, x] = c.img[y + 1, x] = c.img[y, x - 1] = c.img[y, x + 1] = col * 0.75


def dm_props(ctx, c):
    out = []
    for x, y in [(1380, 470), (1410, 488), (1640, 470)]:
        out.append(dict(type='barrel', x=x, y=y))
    for x, y in [(1350, 500), (1700, 492)]:
        out.append(dict(type='crate', x=x, y=y))
    for x in (260, 700, 980, 1900, 2200):
        out.append(dict(type='v51_reeds', x=x, y=618))
    out.append(dict(type='v44_v41_rowboat_rowboat', x=900, y=720))
    out.append(dict(type='v51_dock_pile', x=1420, y=690))
    return out


def rune_circle(cx, cy, r, col='#efe4ff', ry=0.62):
    def hook(c, ctx):
        dx = (c.xx - cx).astype(np.float32); dy = (c.yy - cy) / ry
        d = np.sqrt(dx * dx + dy * dy); th = np.arctan2(dy, dx)
        lines = (np.abs(d - r) < 1.6) | (np.abs(d - r * 0.82) < 1.0) | (np.abs(d - r * 0.45) < 1.2)
        ticks = (d > r * 0.84) & (d < r * 0.98) & (np.abs(((th / (2 * np.pi) * 24) % 1) - 0.5) > 0.46)
        star = (d < r * 0.80) & (d > r * 0.47) & (np.abs(np.abs(np.cos(th * 3)) ** 8 * (r * 0.33) - (d - r * 0.47)) < 1.4)
        m = lines | ticks | star
        c.img[m] = np.clip(c.img[m] * 0.45 + rgb(col) * 0.6, 0, 255)
        glow = (~m) & (dist_from(m, 4) < 3)
        c.img[glow] = np.clip(c.img[glow] * 0.85 + rgb(col) * 0.2, 0, 255)
    return hook


FOREST = ['tree_dark', 'tree_pine', 'tree_oak', 'tree_green', 'v41_tree_dark_willow', 'tree_autumn']

CONFIG = {
    'riverside': dict(
        water_fill=[rv_fill], paint=[rv_paint], props=[rv_props], shore=22, lilies=50, walls_are_water=True,
        grass=('#5a9c5e', '#62a464', '#6aac69', '#72b36e', '#7cba74', '#87c27b'),
        door_targets={'plaza_to_lake': (1200, 80)},
        districts=['sandy west beach', 'wooden viewing deck + pier', 'rocky east shore + fishing hut',
                   'far islet', 'meadow paths to plaza and dermaga']),
    'dermaga': dict(walls_are_water=True, shore=20, lilies=40, props=[dm_props],
                    grass=('#5a9c5e', '#62a464', '#6aac69', '#72b36e', '#7cba74', '#87c27b'),
                    districts=['long pier and platform', 'sandy shore', 'boat shed meadow']),
    'hutan_bisik': dict(trees=FOREST, tree_weights=[24, 22, 14, 18, 6, 8], density=(0.95, 0.07), inner_gap=92,
                        paint=[leaf_litter], flowers=('#f6f1e7', '#c4b2f2', '#9fd3c7'),
                        water_pal=('#2f6f9c', '#3a80ad', '#4690bb', '#58a2c8', '#74b8d6'),
                        districts=['dense whispering woods', 'stone terraces with stairs', 'clear stream + bridge', 'camp clearing']),
    'bukit_bintang': dict(trees=['tree_pine', 'tree_dark', 'tree_oak', 'tree_green'], tree_weights=[40, 22, 14, 10],
                          density=(0.85, 0.02), paint=[star_flowers], path_thr=55, path_blur=7,
                          flowers=('#e8f4ff', '#bcd8ff', '#fff3b0'),
                          districts=['observatory hilltop', 'star meadow', 'fenced ridge path']),
    'memory_garden': dict(realm=True, paint=[rune_circle(1000, 905, 330)], trees=['v44_tree_dream', 'v44_tree_lantern', 'tree_dream', 'v44_v41_tree_dream_memory_tree'],
                          tree_weights=[50, 20, 20, 3], density=(0.9, 0.018), flowers=('#f6e8ff', '#d8b8ff', '#ffd6f0'), lilies=0,
                          keep_veg=('v44_crystal',), districts=['crossroads of light paths', 'memory arches', 'crystal glade']),
    'lantern_field': dict(realm=True, paint=[rune_circle(1130, 792, 190, '#ffe7b0')], trees=['tree_lantern', 'tree_dream', 'v41_tree_lantern_cherry'], tree_weights=[50, 30, 6],
                          density=(0.9, 0.02), flowers=('#ffe9a8', '#ffd27a', '#fff6d8'), star='#ffe9b0', lilies=0,
                          districts=['lantern meadow', 'glowing causeway', 'release plaza']),
    'starfall_village': dict(realm=True, paint=[rune_circle(1200, 868, 290)], trees=['tree_dream', 'tree_lantern', 'v41_tree_dream_memory_tree'], tree_weights=[50, 40, 3],
                             density=(0.9, 0.02), flowers=('#e8f4ff', '#d8c8ff', '#fff3b0'), lilies=0,
                             districts=['star cottages', 'village square', 'lantern lane']),
    'star_path': dict(realm=True, trees=['crystal', 'star_stone', 'v41_crystal_crystal_cluster'], tree_weights=[40, 30, 10],
                      density=(0.5, 0.01), keep_veg=(), flowers=('#e8f4ff', '#bcd8ff', '#ffffff'), lilies=0,
                      districts=['zigzag starlight road', 'constellation field', 'viewpoints']),
    'eternal_garden': dict(trees=['tree_cherry', 'tree_green', 'v43_v41_tree_cherry_cherry', 'tree_oak'], tree_weights=[40, 25, 15, 6],
                           walls_are_water=False, shore=14, lum_paths=True, path_lum=200, path_sat=60,
                           districts=['wishing tree terrace', 'cherry avenue with arches', 'reflecting pond', 'gazebo lawn']),
}
