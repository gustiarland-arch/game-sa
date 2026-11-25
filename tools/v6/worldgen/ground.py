"""v6 ground repaint: keeps every map's layout, replaces its flat ground art with
pixel-art materials, autotiled edges, ambient occlusion and scattered detail.

Usage: python3 tools/v6/worldgen/ground.py <area_id> [<area_id> ...] [--out DIR] [--src DIR]

How it works
1. Terrain map: the current ground image (or its archived original) is classified per
   4x4-pixel cell into materials (grass, path, stone, sand, water, dream ground,
   dream path) from colour. A majority filter removes speckle from the old decals.
2. Materials: each material is painted from a small fixed palette with layered value
   noise quantised to the palette (clustered pixels, no dithering mush), plus its own
   structure (grass blades, brick courses, pebbles, wave glints, star dust).
3. Edges: higher materials get a dark rim and a light lip, grass grows tufts over path
   edges, shores get foam and wet sand, lower ground gets soft stepped occlusion.
4. Detail: flowers, pebbles, leaves and sparkles scattered by a seeded generator,
   never on paths or water.
Deterministic: same input, same bytes. Pure numpy + Pillow.
"""
import json, sys, hashlib
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / 'android' / 'assets'
GRASS, PATH, STONE, SAND, WATER, DREAM, DPATH = range(7)
NAMES = ['grass', 'path', 'stone', 'sand', 'water', 'dream', 'dpath']
# Elevation order used for edge rims: what sits "on top" of what.
HEIGHT = {WATER: 0, SAND: 1, GRASS: 2, DREAM: 2, PATH: 3, DPATH: 3, STONE: 4}


def hexrgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], dtype=np.float32)


PALETTES = {
    GRASS: ['#2f6b3a', '#3a7d40', '#468f45', '#55a04c', '#68b356', '#82c564'],
    PATH: ['#8a6a46', '#a07c52', '#b58f60', '#c6a26f', '#d6b583', '#e3c697'],
    STONE: ['#7d6e68', '#958478', '#ab9887', '#c0ab96', '#d2bea6', '#e2d0b8'],
    SAND: ['#c9ad7c', '#d8bd8b', '#e4cb9b', '#eed8ab', '#f5e4bd'],
    WATER: ['#1d4e7a', '#22608f', '#2a72a3', '#3486b5', '#4a9cc6', '#7cc0de'],
}


def noise(h, w, scale, seed):
    """Smooth value noise in [0,1] (bilinear over a random lattice)."""
    rng = np.random.default_rng(seed)
    gh, gw = h // scale + 2, w // scale + 2
    g = rng.random((gh, gw)).astype(np.float32)
    y = np.arange(h, dtype=np.float32) / scale
    x = np.arange(w, dtype=np.float32) / scale
    y0, x0 = y.astype(int), x.astype(int)
    fy, fx = (y - y0)[:, None], (x - x0)[None, :]
    fy, fx = fy * fy * (3 - 2 * fy), fx * fx * (3 - 2 * fx)
    a = g[y0][:, x0]; b = g[y0][:, x0 + 1]; c = g[y0 + 1][:, x0]; d = g[y0 + 1][:, x0 + 1]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def quantise(v, pal):
    """Map v in [0,1] onto palette entries (clustered bands -> pixel-art look)."""
    p = np.stack([hexrgb(c) for c in pal]) if isinstance(pal[0], str) else np.asarray(pal, np.float32)
    idx = np.clip((v * len(p)).astype(int), 0, len(p) - 1)
    return p[idx]


def shades(base, n=6, spread=0.38):
    """Palette ramp around an arbitrary base colour (used for dream maps)."""
    base = np.asarray(base, np.float32)
    out = []
    for i in range(n):
        t = (i / (n - 1) - 0.5) * 2 * spread
        c = base * (1 + t) + (np.array([30, 20, 60], np.float32) * max(0, t))
        out.append(np.clip(c, 0, 255))
    return out


# ----------------------------------------------------------------------------- classify

def classify(img, cell=4):
    a = img[:, :, :3].astype(np.float32)
    H, W = a.shape[:2]
    h, w = H // cell, W // cell
    c = a[:h * cell, :w * cell].reshape(h, cell, w, cell, 3).transpose(0, 2, 1, 3, 4).reshape(h, w, cell * cell, 3)
    m = np.median(c, axis=2)
    r, g, b = m[..., 0], m[..., 1], m[..., 2]
    lum = 0.3 * r + 0.59 * g + 0.11 * b
    t = np.full((h, w), DREAM, np.int8)
    green = (g > r + 12) & (g > b + 4)
    blue = (b > r + 40) & (b > g + 8) & (b > 110)
    warm = (r > b + 28) & (r >= g - 6)
    t[green] = GRASS
    t[blue] = WATER
    t[warm & (lum > 150) & (r - b < 70)] = STONE
    t[warm & (lum > 120) & (r - b >= 70)] = PATH
    t[warm & (lum > 205)] = SAND
    dream = ~(green | blue | warm)
    # Dream maps: the lighter band becomes the walkway.
    if dream.mean() > 0.5:
        thr = np.percentile(lum[dream], 88)
        t[dream & (lum >= thr) & (lum > np.median(lum[dream]) + 30)] = DPATH
    # Majority filter (3 passes, 5x5) clears decal speckle.
    for _ in range(3):
        t = majority(t, 2)
    return t, m


def majority(t, rad):
    h, w = t.shape
    pad = np.pad(t, rad, mode='edge')
    counts = np.zeros((7, h, w), np.int16)
    for dy in range(-rad, rad + 1):
        for dx in range(-rad, rad + 1):
            win = pad[rad + dy:rad + dy + h, rad + dx:rad + dx + w]
            for k in range(7):
                counts[k] += (win == k)
    return counts.argmax(0).astype(np.int8)


# ----------------------------------------------------------------------------- materials

def paint_grass(H, W, seed, pal=None):
    pal = pal or PALETTES[GRASS]
    v = 0.55 * noise(H, W, 48, seed) + 0.30 * noise(H, W, 14, seed + 1) + 0.15 * noise(H, W, 5, seed + 2)
    img = quantise(np.clip((v - 0.2) * 1.5, 0, 0.999) * 0.8 + 0.1, pal)
    rng = np.random.default_rng(seed + 3)
    p = np.stack([hexrgb(c) for c in pal]) if isinstance(pal[0], str) else np.asarray(pal)
    # Blades: short vertical strokes, light tip over dark root.
    n = H * W // 22
    ys = rng.integers(2, H - 1, n); xs = rng.integers(0, W, n)
    for y, x in zip(ys, xs):
        k = rng.integers(2, 4)
        img[y, x] = p[min(len(p) - 1, 4 + rng.integers(0, 2))]
        img[y - 1, x] = p[min(len(p) - 1, 4)]
        if k == 3:
            img[y + 1, x] = p[1]
    return img


def paint_path(H, W, seed, pal=None):
    pal = pal or PALETTES[PATH]
    v = 0.6 * noise(H, W, 20, seed) + 0.4 * noise(H, W, 6, seed + 1)
    img = quantise(np.clip(v * 0.7 + 0.25, 0, 0.999), pal)
    p = np.stack([hexrgb(c) for c in pal]) if isinstance(pal[0], str) else np.asarray(pal)
    rng = np.random.default_rng(seed + 5)
    for _ in range(H * W // 260):  # pebbles: dark body, light top-left highlight
        y, x = rng.integers(1, H - 2), rng.integers(1, W - 2)
        img[y:y + 2, x:x + 2] = p[1]
        img[y, x] = p[-1]
    return img


def paint_stone(H, W, seed, pal=None):
    """Running-bond brick courses with per-brick tint, top light and bottom shadow."""
    pal = pal or PALETTES[STONE]
    p = np.stack([hexrgb(c) for c in pal]) if isinstance(pal[0], str) else np.asarray(pal)
    img = np.zeros((H, W, 3), np.float32)
    rng = np.random.default_rng(seed)
    bh, bw = 8, 16
    tone = noise(H, W, 64, seed + 9)
    for row in range(0, H, bh):
        off = (row // bh % 2) * (bw // 2)
        for col in range(-bw, W, bw):
            x0, x1 = max(0, col + off), min(W, col + off + bw)
            y0, y1 = row, min(H, row + bh)
            if x1 <= x0:
                continue
            k = int(np.clip(2 + rng.integers(-1, 2) + (tone[y0, x0] - 0.5) * 3, 1, len(p) - 2))
            img[y0:y1, x0:x1] = p[k]
            img[y0, x0:x1] = p[k + 1]            # top light
            img[y1 - 1, x0:x1] = p[0]            # mortar line / shadow
            img[y0:y1, x0] = p[0]
            if rng.random() < 0.18:              # chipped / mossy brick
                cy, cx = rng.integers(y0 + 1, max(y0 + 2, y1 - 1)), rng.integers(x0 + 1, max(x0 + 2, x1 - 1))
                img[cy, cx] = p[k - 1]
    return img


def paint_sand(H, W, seed):
    v = 0.7 * noise(H, W, 24, seed) + 0.3 * noise(H, W, 4, seed + 1)
    img = quantise(np.clip(v * 0.8 + 0.15, 0, 0.999), PALETTES[SAND])
    rng = np.random.default_rng(seed + 2)
    for _ in range(H * W // 400):
        img[rng.integers(0, H), rng.integers(0, W)] = hexrgb('#fff4d6')
    return img


def paint_water(H, W, seed, depth):
    p = PALETTES[WATER]
    v = 0.5 * noise(H, W, 40, seed) + 0.5 * depth
    img = quantise(np.clip(1 - v, 0, 0.999) * 0.75, p)
    rng = np.random.default_rng(seed + 4)
    hl = hexrgb(p[-1])
    for _ in range(H * W // 700):  # static wave glints (runtime adds moving ones)
        y, x = rng.integers(0, H), rng.integers(0, W - 6)
        img[y, x:x + rng.integers(3, 7)] = hl
    return img


def paint_dream(H, W, seed, base, path=False):
    pal = shades(base, 6, 0.30 if not path else 0.18)
    v = 0.5 * noise(H, W, 56, seed) + 0.35 * noise(H, W, 12, seed + 1) + 0.15 * noise(H, W, 4, seed + 2)
    img = quantise(np.clip(v * 0.9 + 0.05, 0, 0.999), pal)
    rng = np.random.default_rng(seed + 3)
    for _ in range(H * W // (160 if not path else 300)):  # star dust
        y, x = rng.integers(1, H - 1), rng.integers(1, W - 1)
        c = np.clip(np.asarray(base) * 1.6 + 60, 0, 255)
        img[y, x] = c
        if rng.random() < 0.12:
            img[y - 1, x] = img[y + 1, x] = img[y, x - 1] = img[y, x + 1] = c * 0.8
    return img


# ----------------------------------------------------------------------------- compose

def upsample(t, cell, H, W):
    return np.repeat(np.repeat(t, cell, 0), cell, 1)[:H, :W]


def soften_edges(mask, seed, amp=2):
    """Pixel-level jitter of a boolean mask boundary for organic edges."""
    H, W = mask.shape
    nz = noise(H, W, 6, seed)
    shift = ((nz - 0.5) * 2 * amp).round().astype(int)
    ys, xs = np.mgrid[0:H, 0:W]
    xs2 = np.clip(xs + shift, 0, W - 1)
    ys2 = np.clip(ys + np.roll(shift, 7, 1), 0, H - 1)
    return mask[ys2, xs2]


def dist_from(mask, maxd):
    """Chebyshev distance (in px) from True cells, capped at maxd."""
    d = np.full(mask.shape, maxd, np.int16)
    d[mask] = 0
    cur = mask.copy()
    for i in range(1, maxd):
        grown = cur.copy()
        grown[1:] |= cur[:-1]; grown[:-1] |= cur[1:]
        grown[:, 1:] |= cur[:, :-1]; grown[:, :-1] |= cur[:, 1:]
        d[grown & ~cur] = i
        cur = grown
    return d


def render(area_id, src_img, seed):
    H, W = src_img.shape[:2]
    terr, med = classify(src_img)
    cell = 4
    t = upsample(terr, cell, H, W)
    masks = {k: soften_edges(t == k, seed + 11 * k, 2 if k in (PATH, DPATH, STONE) else 1) for k in range(7)}
    # Resolve overlaps from jitter: higher material wins.
    final = np.full((H, W), -1, np.int8)
    for k in sorted(range(7), key=lambda k: HEIGHT[k]):
        final[masks[k]] = k
    final[final < 0] = t[final < 0]

    out = np.zeros((H, W, 3), np.float32)
    dream_base = np.median(med[terr == DREAM], axis=0) if (terr == DREAM).any() else np.array([90, 80, 150])
    dpath_base = np.median(med[terr == DPATH], axis=0) if (terr == DPATH).any() else dream_base * 1.4
    water = final == WATER
    depth = np.clip(dist_from(~water, 40) / 40.0, 0, 1)
    layers = {
        GRASS: lambda: paint_grass(H, W, seed + 1),
        PATH: lambda: paint_path(H, W, seed + 2),
        STONE: lambda: paint_stone(H, W, seed + 3),
        SAND: lambda: paint_sand(H, W, seed + 4),
        WATER: lambda: paint_water(H, W, seed + 5, depth),
        DREAM: lambda: paint_dream(H, W, seed + 6, dream_base),
        DPATH: lambda: paint_dream(H, W, seed + 7, dpath_base, True),
    }
    for k, fn in layers.items():
        m = final == k
        if m.any():
            out[m] = fn()[m]

    # Edges: rims on higher materials, tufts and occlusion on lower ones.
    for k in (PATH, STONE, DPATH, SAND):
        m = final == k
        if not m.any():
            continue
        outside = ~m
        d_in = dist_from(outside, 4)   # distance inside k from its border
        d_out = dist_from(m, 5)        # distance outside k from k
        lower = outside & np.isin(final, [GRASS, DREAM, SAND, WATER])
        dark = np.array([60, 44, 34], np.float32) if k != DPATH else dream_base * 0.55
        out[m & (d_in == 1)] = out[m & (d_in == 1)] * 0.55 + dark * 0.45
        out[m & (d_in == 2)] *= 0.93
        lip = np.array([255, 240, 210], np.float32) if k != DPATH else np.clip(dpath_base * 1.3, 0, 255)
        sel = m & (d_in == 3)
        out[sel] = out[sel] * 0.85 + lip * 0.15
        # stepped occlusion on the lower side
        for dd, f in ((1, 0.78), (2, 0.86), (3, 0.93)):
            s = lower & (d_out == dd)
            out[s] *= f
    # Grass tufts creeping over path rims.
    rng = np.random.default_rng(seed + 21)
    g_pal = [hexrgb(c) for c in PALETTES[GRASS]]
    grass = final == GRASS
    near = (~grass) & (dist_from(grass, 3) == 1) & np.isin(final, [PATH, STONE])
    ys, xs = np.nonzero(near)
    pick = rng.random(len(ys)) < 0.35
    for y, x in zip(ys[pick], xs[pick]):
        out[y, x] = g_pal[3]
        if y > 0:
            out[y - 1, x] = g_pal[4]
    # Shore: foam ring and wet sand.
    if water.any():
        dw = dist_from(water, 6)
        dl = dist_from(~water, 6)
        foam = np.array([226, 244, 250], np.float32)
        out[water & (dl == 1)] = foam
        out[water & (dl == 2)] = out[water & (dl == 2)] * 0.5 + foam * 0.5
        wet = (~water) & (dw <= 3) & (dw >= 1)
        out[wet] *= 0.82

    # Scattered detail on grass / dream ground (never paths or water).
    det = np.random.default_rng(seed + 31)
    flowers = [hexrgb(c) for c in ('#f6f1e7', '#f5c6d6', '#f2d36b', '#b9a6f0', '#ef8f8f')]
    leaf = hexrgb('#2a5a30')
    for _ in range(H * W // 900):
        y, x = det.integers(2, H - 3), det.integers(2, W - 3)
        if final[y, x] == GRASS and dist_from_point_ok(final, y, x, GRASS):
            c = flowers[det.integers(0, len(flowers))]
            out[y, x] = c; out[y - 1, x] = c * 0.9; out[y, x - 1] = c * 0.9; out[y, x + 1] = c * 0.9
            out[y + 1, x] = leaf
        elif final[y, x] == DREAM:
            c = np.clip(dream_base * 1.8 + 50, 0, 255)
            out[y, x] = c
    for _ in range(H * W // 2500):  # darker grass clumps for depth
        y, x = det.integers(3, H - 4), det.integers(3, W - 6)
        if final[y, x] == GRASS:
            out[y:y + 2, x:x + 5] *= 0.86
    return np.clip(out, 0, 255).astype(np.uint8), final


def dist_from_point_ok(final, y, x, k):
    return (final[y - 2:y + 3, x - 2:x + 3] == k).all()


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    out_dir = Path(sys.argv[sys.argv.index('--out') + 1]) if '--out' in sys.argv else ASSETS / 'maps'
    src_dir = Path(sys.argv[sys.argv.index('--src') + 1]) if '--src' in sys.argv else None
    maps = json.loads((ASSETS / 'data' / 'maps.json').read_text(encoding='utf-8'))['areas']
    args = [a for a in args if a not in (str(out_dir), str(src_dir))]
    for area_id in args:
        rel = maps[area_id]['image']
        src = (src_dir / Path(rel).name) if src_dir else ASSETS / rel
        img = np.array(Image.open(src).convert('RGB'))
        seed = int(hashlib.sha256(area_id.encode()).hexdigest()[:8], 16)
        out, terr = render(area_id, img, seed)
        out_dir.mkdir(parents=True, exist_ok=True)
        Image.fromarray(out, 'RGB').save(out_dir / Path(rel).name, optimize=True)
        counts = {NAMES[k]: round(float((terr == k).mean()) * 100, 1) for k in range(7) if (terr == k).any()}
        print(area_id, counts)


if __name__ == '__main__':
    main()


# ----------------------------------------------------------------------------- enhance mode
# Full repaint loses each map's hand-placed decals (mosaics, rugs, markings). Enhance mode
# keeps the original ground and adds what flat maps lack: depth (tonal patches), texture
# (grass tufts), and readable edges (rims, overhang, occlusion, shore foam).

def enhance(area_id, src_img, seed):
    H, W = src_img.shape[:2]
    terr, med = classify(src_img)
    t = upsample(terr, 4, H, W)
    final = t.copy()
    for k in (PATH, STONE, DPATH, SAND):
        m = soften_edges(t == k, seed + 11 * k, 1)
        final[m & np.isin(t, [GRASS, DREAM, k])] = k
    out = src_img[:, :, :3].astype(np.float32)
    grass = final == GRASS
    soft = np.isin(final, [GRASS, DREAM])
    # 1. depth: big soft patches, quantised to 4 steps so it reads as pixel art
    v = 0.65 * noise(H, W, 90, seed + 1) + 0.35 * noise(H, W, 28, seed + 2)
    step = np.floor(np.clip(v, 0, 0.999) * 4) / 3.0          # 0..1 in 4 bands
    out[soft] *= (0.90 + 0.14 * step[soft])[:, None]
    # 2. grass tufts: 3-blade clumps tinted from the local colour
    rng = np.random.default_rng(seed + 3)
    n = int(grass.sum() // 160)
    ys = rng.integers(3, H - 2, n); xs = rng.integers(2, W - 2, n)
    for y, x in zip(ys, xs):
        if not grass[y, x] or not grass[y - 3, x]:
            continue
        base = out[y + 1, x].copy()
        dark, lite = base * 0.72, np.clip(base * 1.18 + 8, 0, 255)
        out[y, x - 1] = dark; out[y - 1, x - 1] = base * 0.86
        out[y, x] = dark; out[y - 1, x] = base; out[y - 2, x] = lite
        out[y, x + 1] = dark; out[y - 1, x + 1] = lite
    # 3. edges between soft ground and hard surfaces
    hard = np.isin(final, [PATH, STONE, DPATH])
    if hard.any() and soft.any():
        d_in = dist_from(~hard, 4)
        d_out = dist_from(hard, 4)
        rim = hard & (d_in == 1)
        out[rim] = out[rim] * 0.62 + np.array([70, 50, 36], np.float32) * 0.38
        out[hard & (d_in == 2)] *= 0.92
        lip = hard & (d_in == 3)
        out[lip] = np.clip(out[lip] * 1.06, 0, 255)
        g_side = soft & (d_out <= 2)
        out[g_side & (d_out == 1)] *= 0.80
        out[g_side & (d_out == 2)] *= 0.90
        # grass overhang: blades leaning onto the path rim
        ys, xs = np.nonzero(rim)
        pick = rng.random(len(ys)) < 0.28
        for y, x in zip(ys[pick], xs[pick]):
            g = med[min(y // 4, med.shape[0] - 1), min(x // 4, med.shape[1] - 1)]
            src = out[max(0, y - 3), x] if grass[max(0, y - 3), x] else None
            if src is None:
                continue
            out[y, x] = src * 0.85
            if y + 1 < H:
                out[y + 1, x] = src * 0.7
    # 4. shores
    water = final == WATER
    if water.any():
        dl = dist_from(~water, 4); dw = dist_from(water, 4)
        foam = np.array([226, 244, 250], np.float32)
        out[water & (dl == 1)] = out[water & (dl == 1)] * 0.3 + foam * 0.7
        out[water & (dl == 2)] = out[water & (dl == 2)] * 0.7 + foam * 0.3
        out[(~water) & (dw == 1)] *= 0.78
        out[(~water) & (dw == 2)] *= 0.88
    return np.clip(out, 0, 255).astype(np.uint8), final
