"""Extra HD kit sprites for the Godot map remaster, in the same light/outline rules as
tools/v6/artkit (top-left light, coloured outlines, shared ramps). Registers each sprite in
props.json as props/hd/<id>@2x.png.

Usage: python3 tools/godot/kit_extra.py [id ...] [--sheet out.png]
"""
import sys, json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/v6/artkit'))
import kit, nature, built                                         # noqa: E402
from kit import (Sprite, quant, bayer, sphere_shade, outline, noise, hexrgb, ramp, BARK, STONE, LEAF,   # noqa: E402
                 LEAF_DARK, WOOD, METAL, FLOWERS)

A = ROOT / 'android' / 'assets'
OUT = A / 'props' / 'hd'

DREAM = ramp('#2e2656', '#40357a', '#5a4b9c', '#7865bb', '#9a86d6', '#bdaaee', '#e0d4ff')
DREAM_BLUE = ramp('#1d2f5a', '#26437a', '#335d9a', '#467ab6', '#6198cc', '#86b6e0', '#b6d6f2')
LANTERN = ramp('#8a3c12', '#c2611e', '#ef8f3b', '#ffc27a', '#ffe3a8')
CRYSTAL = ramp('#2b2a6a', '#3f3f99', '#5a5cc4', '#7c84e0', '#a5b3f2', '#d3defc', '#ffffff')
CRYSTAL_CYAN = ramp('#164a5c', '#1f6a80', '#2b8ea3', '#45b3c4', '#76d2dc', '#b4ecef', '#ffffff')
TERRACOTTA = ramp('#5a2a1a', '#7a3a22', '#9c4e2c', '#bb6638', '#d2814c', '#e3a06c')
CLOTH_RED = ramp('#6a1f26', '#8f2c33', '#b33e44', '#d35a5c', '#ec8a86')


def glow(sp, cx, cy, r, col, strength=0.55):
    """Soft additive halo baked into the sprite (alpha fades out)."""
    d = np.sqrt((sp.xx - cx) ** 2 + (sp.yy - cy) ** 2) / r
    a = np.clip(1 - d, 0, 1) ** 2 * strength
    c = np.asarray(col, np.float32)
    keep = sp.a > 0.5
    sp.rgb = np.where(keep[..., None], np.clip(sp.rgb + c * a[..., None] * 0.6, 0, 255),
                      np.where((a > sp.a)[..., None], c, sp.rgb))
    sp.a = np.where(keep, sp.a, np.maximum(sp.a, a))


def dream_tree(R=DREAM, seed=31, sparkle='#fff6c8'):
    sp = nature.broadleaf(R, seed)
    rng = np.random.default_rng(seed + 5)
    leaf = (sp.a > 0.5) & (sp.yy < sp.h - 110)
    ys, xs = np.nonzero(leaf)
    s = hexrgb(sparkle)
    for i in rng.integers(0, len(ys), 70):
        y, x = ys[i], xs[i]
        sp.rgb[y, x] = s
        if rng.random() < 0.3:
            sp.rgb[max(0, y - 1):y + 2, x] = s * 0.9
            sp.rgb[y, max(0, x - 1):x + 2] = s * 0.9
    return sp


def lantern_tree(seed=41):
    sp = nature.broadleaf(LEAF_DARK, seed)
    rng = np.random.default_rng(seed)
    leaf = sp.a > 0.5
    for i in range(9):
        x = int(rng.uniform(40, sp.w - 40))
        ys = np.nonzero(leaf[:, x])[0]
        if not len(ys):
            continue
        y = int(ys.max() - rng.uniform(4, 40))
        if y > sp.h - 110:
            continue
        sp.put(sp.rect(x, y - 12, 1, 12), BARK[1])
        body = sp.ellipse(x, y + 5, 6, 7)
        sp.put(body, quant(sphere_shade(sp, x, y + 5, 6, 7) * 0.6 + 0.4, LANTERN))
        sp.put(sp.rect(x - 4, y - 2, 9, 2), BARK[1])
        glow(sp, x, y + 5, 16, LANTERN[3], 0.35)
    return sp


def willow(seed=51, w=200, h=250):
    sp = Sprite(w, h)
    rng = np.random.default_rng(seed)
    cx, base = w / 2, h - 6
    trunk = sp.poly([(cx - 9, base - 120), (cx + 9, base - 120), (cx + 14, base), (cx - 14, base)])
    sp.put(trunk, quant(0.7 - (sp.xx - cx + 14) / 28 * 0.6, BARK, bayer(h, w)))
    clusters = []
    for i in range(18):
        a = rng.uniform(np.pi, 2 * np.pi)
        clusters.append((cx + np.cos(a) * rng.uniform(0, 62), base - 160 + np.sin(a) * rng.uniform(0, 40),
                         rng.uniform(26, 34), 0.5))
    nature._leafy_cluster_field(sp, clusters, LEAF, seed)
    # hanging strands
    for i in range(46):
        x0 = cx + rng.uniform(-88, 88)
        top = base - 175 + abs(x0 - cx) * 0.45 + rng.uniform(-6, 6)
        length = rng.uniform(60, 120)
        for y in range(int(top), int(min(base - 8, top + length))):
            t = (y - top) / length
            x = int(x0 + np.sin(t * 2.2 + i) * 2)
            if 0 <= x < w - 2:
                sp.put(sp.rect(x, y, 3, 1), LEAF[2 + (i % 4)] * (1 - t * 0.15))
    outline(sp, LEAF[0] * 0.75)
    return sp


def mushrooms(glowing=False, seed=61, w=96, h=66):
    sp = Sprite(w, h)
    rng = np.random.default_rng(seed)
    capR = CRYSTAL_CYAN if glowing else CLOTH_RED
    for i in range(5):
        x = rng.uniform(20, w - 20)
        s = rng.uniform(0.95, 1.45)
        top = h - 8 - 22 * s
        sp.put(sp.rect(int(x - 3 * s), int(top + 6 * s), int(6 * s) + 1, int(h - 6 - top - 6 * s)), hexrgb('#efe4cf'))
        cap = sp.ellipse(x, top + 6 * s, 12 * s, 8 * s) & (sp.yy < top + 8 * s)
        sp.put(cap, quant(sphere_shade(sp, x, top + 6 * s, 12 * s, 8 * s), capR))
        for k in range(3):
            sp.put(sp.ellipse(x + rng.uniform(-6, 6) * s, top + rng.uniform(1, 5) * s, 1.6, 1.3), hexrgb('#fff6ea'))
        if glowing:
            glow(sp, x, top + 6 * s, 22 * s, capR[4], 0.45)
    outline(sp, capR[0] * 0.8, width=2)
    return sp


def crystal(R=CRYSTAL, seed=71, w=90, h=120):
    sp = Sprite(w, h)
    rng = np.random.default_rng(seed)
    base = h - 8
    shards = [(w / 2, 1.0, 0), (w / 2 - 22, 0.62, -0.35), (w / 2 + 22, 0.7, 0.3), (w / 2 - 34, 0.38, -0.6), (w / 2 + 34, 0.42, 0.55)]
    for x, s, lean in sorted(shards, key=lambda q: q[1]):
        hh = (h - 26) * s
        bw = 12 + 10 * s
        tipx = x + lean * hh * 0.35
        pts = [(x - bw / 2, base), (x - bw / 2 + lean * hh * 0.25, base - hh * 0.78), (tipx, base - hh), (x + bw / 2 + lean * hh * 0.25, base - hh * 0.78), (x + bw / 2, base)]
        m = sp.poly(pts)
        left = sp.xx < (x + lean * (base - sp.yy) * 0.3)
        sh = np.where(left, 0.82, 0.48) + (base - sp.yy) / hh * 0.15
        sp.put(m, quant(sh, R))
        sp.put(m & (np.abs(sp.xx - (x + lean * (base - sp.yy) * 0.3)) < 1.2), R[-1])
    sp.put(sp.ellipse(w / 2, base, w * 0.42, 6) & (sp.a < 0.5), STONE[2])
    glow(sp, w / 2, base - 40, 60, R[4], 0.35)
    outline(sp, R[0] * 0.8)
    return sp


def star_stone(seed=81, w=70, h=80):
    sp = nature.rock(seed, w, h, STONE)
    cx, cy = w / 2, h * 0.55
    star = []
    for i in range(10):
        a = -np.pi / 2 + i * np.pi / 5
        r = 11 if i % 2 == 0 else 4.5
        star.append((cx + np.cos(a) * r, cy + np.sin(a) * r))
    m = sp.poly(star) & (sp.a > 0.5)
    sp.rgb[m] = hexrgb('#fff1a8')
    glow(sp, cx, cy, 26, hexrgb('#ffe680'), 0.45)
    return sp


def lantern_post(seed=91, w=60, h=170):
    sp = Sprite(w, h)
    cx = w / 2
    sp.put(sp.rect(cx - 4, 40, 8, h - 50), quant(0.75 - (sp.xx - cx + 4) / 8 * 0.6, WOOD))
    sp.put(sp.rect(cx - 12, h - 14, 24, 10), WOOD[1])
    sp.put(sp.rect(cx - 4, 34, 22, 5), WOOD[2])                    # arm
    lx, ly = cx + 15, 62
    sp.put(sp.rect(lx, 38, 1, 12), METAL[1])
    body = sp.ellipse(lx, ly, 10, 13)
    sp.put(body, quant(sphere_shade(sp, lx, ly, 10, 13) * 0.55 + 0.45, LANTERN))
    for yy in (ly - 6, ly, ly + 6):
        sp.put(body & (np.abs(sp.yy - yy) < 0.8), LANTERN[1])
    sp.put(sp.rect(lx - 7, ly - 14, 14, 3) | sp.rect(lx - 7, ly + 12, 14, 3), WOOD[0])
    outline(sp, WOOD[0] * 0.8)
    glow(sp, lx, ly, 34, LANTERN[3], 0.5)
    return sp


def planter(flowers=0, seed=101, w=80, h=72):
    sp = Sprite(w, h)
    pot = sp.poly([(12, 34), (w - 12, 34), (w - 20, h - 6), (20, h - 6)])
    sp.put(pot, quant(0.8 - (sp.xx - 12) / (w - 24) * 0.55, TERRACOTTA))
    sp.put(sp.rect(8, 30, w - 16, 8), TERRACOTTA[4])
    sp.put(sp.rect(8, 36, w - 16, 2), TERRACOTTA[1])
    b = nature.bush(seed, w=w, h=46, flowers=FLOWERS[flowers % len(FLOWERS)])
    m = b.a > 0.5
    sub = np.zeros((h, w), bool)
    sub[0:46, :] = m
    sp.rgb[0:46][m] = b.rgb[m]
    sp.a[0:46][m] = 1
    outline(sp, TERRACOTTA[0] * 0.8)
    return sp


def crate(seed=111, w=64, h=64):
    sp = Sprite(w, h)
    front = sp.rect(6, 18, 46, 40)
    top = sp.poly([(6, 18), (18, 6), (w - 2, 6), (52, 18)])
    side = sp.poly([(52, 18), (w - 2, 6), (w - 2, 46), (52, 58)])
    built._planks(sp, front, WOOD, True, 10, seed)
    sp.put(top, WOOD[5])
    sp.put(side, WOOD[2])
    for m in (sp.rect(6, 18, 46, 4), sp.rect(6, 54, 46, 4), sp.rect(6, 18, 4, 40), sp.rect(48, 18, 4, 40)):
        sp.put(m, WOOD[1])
    outline(sp, WOOD[0] * 0.8)
    return sp


def barrel(seed=121, w=56, h=72):
    sp = Sprite(w, h)
    body = sp.ellipse(w / 2, h / 2 + 4, 22, 32) & sp.rect(4, 12, w - 8, h - 18)
    stave = ((sp.xx - 6) % 9 < 1.2)
    sh = 0.85 - np.abs(sp.xx - w / 2 + 6) / 26 * 0.6
    col = quant(sh, WOOD)
    col[stave] = WOOD[1]
    sp.put(body, col)
    for y in (20, h - 18):
        sp.put(body & (np.abs(sp.yy - y) < 2.5), METAL[2])
    sp.put(sp.ellipse(w / 2, 13, 20, 5), WOOD[4])
    outline(sp, WOOD[0] * 0.8)
    return sp


def umbrella_table(awning=('#e88aa8', '#fbf3ee'), w=150, h=170):
    sp = Sprite(w, h)
    cx = w / 2
    sp.put(sp.rect(cx - 3, 50, 6, h - 64), METAL[3])
    top = sp.ellipse(cx, h - 40, 44, 12)
    sp.put(sp.rect(cx - 4, h - 40, 8, 30), METAL[2])
    sp.put(top, hexrgb('#f6efe6'))
    sp.put(sp.ellipse(cx, h - 42, 44, 10), hexrgb('#ffffff'))
    for sx in (-1, 1):
        chair = sp.rect(cx + sx * 56 - 10, h - 46, 20, 34)
        sp.put(chair, hexrgb('#c79bd6'))
        sp.put(sp.rect(cx + sx * 56 - 10, h - 46, 20, 6), hexrgb('#e2c3ec'))
    can = sp.poly([(cx, 8), (w - 6, 54), (6, 54)])
    seg = (np.floor((np.arctan2(sp.yy - 8, sp.xx - cx) * 7)) % 2) == 0
    c0, c1 = hexrgb(awning[0]), hexrgb(awning[1])
    col = np.where(seg[..., None], c0, c1) * (1 - (sp.xx - 6) / (w - 12) * 0.2)[..., None]
    sp.put(can, col)
    sp.put(sp.rect(6, 52, w - 12, 5) & sp.poly([(0, 50), (w, 50), (w, 60), (0, 60)]), c0 * 0.8)
    outline(sp, c0 * 0.45)
    return sp


def flowerbed(seed=131, w=140, h=60):
    sp = Sprite(w, h)
    sp.put(sp.rect(4, 24, w - 8, h - 30), WOOD[2])
    sp.put(sp.rect(4, 24, w - 8, 4), WOOD[4])
    sp.put(sp.rect(10, 28, w - 20, 10), hexrgb('#6e5038'))
    rng = np.random.default_rng(seed)
    for i in range(22):
        x, y = rng.uniform(12, w - 12), rng.uniform(10, 30)
        sp.put(sp.ellipse(x, y, rng.uniform(5, 8), rng.uniform(4, 6)), LEAF[rng.integers(2, 6)])
    for i in range(24):
        x, y = rng.uniform(12, w - 12), rng.uniform(6, 28)
        F = FLOWERS[i % 4]
        sp.put(sp.ellipse(x, y, 3.2, 2.8), F[2])
        sp.put(sp.ellipse(x - 1, y - 1, 1.2, 1.2), F[3])
    outline(sp, WOOD[0] * 0.8)
    return sp


KIT = {
    'hd_tree_dream_a': (lambda: dream_tree(DREAM, 31), 16, 9, 'sort'),
    'hd_tree_dream_b': (lambda: dream_tree(DREAM_BLUE, 33, '#e8f6ff'), 16, 9, 'sort'),
    'hd_tree_dream_c': (lambda: dream_tree(kit.CHERRY, 35), 16, 9, 'sort'),
    'hd_tree_lantern': (lambda: lantern_tree(41), 16, 9, 'sort'),
    'hd_tree_lantern_b': (lambda: lantern_tree(43), 16, 9, 'sort'),
    'hd_tree_willow': (lambda: willow(51), 18, 9, 'sort'),
    'hd_tree_dark_a': (lambda: nature.broadleaf(LEAF_DARK, 23), 16, 9, 'sort'),
    'hd_tree_dark_b': (lambda: nature.broadleaf(LEAF_DARK, 27), 16, 9, 'sort'),
    'hd_mushrooms': (lambda: mushrooms(False, 61), 0, 0, 'sort'),
    'hd_mushrooms_glow': (lambda: mushrooms(True, 63), 0, 0, 'sort'),
    'hd_crystal': (lambda: crystal(CRYSTAL, 71), 30, 10, 'sort'),
    'hd_crystal_cyan': (lambda: crystal(CRYSTAL_CYAN, 73), 30, 10, 'sort'),
    'hd_star_stone': (lambda: star_stone(81), 26, 10, 'sort'),
    'hd_lantern_post': (lambda: lantern_post(91), 8, 6, 'sort'),
    'hd_planter_pink': (lambda: planter(0, 101), 30, 10, 'sort'),
    'hd_planter_violet': (lambda: planter(2, 103), 30, 10, 'sort'),
    'hd_crate': (lambda: crate(111), 26, 10, 'sort'),
    'hd_barrel': (lambda: barrel(121), 22, 9, 'sort'),
    'hd_umbrella_table': (lambda: umbrella_table(), 60, 14, 'sort'),
    'hd_flowerbed': (lambda: flowerbed(131), 60, 10, 'sort'),
    'hd_bush_berry': (lambda: nature.bush(19, flowers=FLOWERS[0]), 36, 10, 'sort'),
}


def build(only=None, sheet=None):
    OUT.mkdir(parents=True, exist_ok=True)
    pj = A / 'data/props.json'
    data = json.loads(pj.read_text(encoding='utf-8'))
    shots = []
    for pid, (fn, cw, ch, layer) in KIT.items():
        if only and pid not in only:
            continue
        img = fn().image()
        rel = 'props/hd/%s@2x.png' % pid
        img.save(A / rel, optimize=True)
        data['props'][pid] = {'image': rel, 'cw': cw, 'ch': ch, 'layer': layer}
        shots.append((pid, img))
        print(pid, img.size)
    pj.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if sheet:
        kit.sheet(shots, sheet)


if __name__ == '__main__':
    args = sys.argv[1:]
    sheet = None
    if '--sheet' in args:
        i = args.index('--sheet'); sheet = args[i + 1]; del args[i:i + 2]
    build(set(args) or None, sheet)
