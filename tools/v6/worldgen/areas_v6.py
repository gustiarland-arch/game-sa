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


CONFIG = {
    'riverside': dict(
        water_fill=[rv_fill], paint=[rv_paint], props=[rv_props], shore=22, lilies=50,
        door_targets={'plaza_to_lake': (1200, 80)},
        districts=['sandy west beach', 'wooden viewing deck + pier', 'rocky east shore + fishing hut',
                   'far islet', 'meadow paths to plaza and dermaga']),
}
