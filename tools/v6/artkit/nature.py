"""HD nature sprites: broadleaf trees, pines, bushes, rocks, flower clumps, reeds, stumps."""
import numpy as np
from kit import (Sprite, quant, bayer, sphere_shade, outline, noise, BARK, STONE, LEAF, PINE,
                 FLOWERS, hexrgb)


def _leafy_cluster_field(sp, clusters, R, seed, leaf_px=5):
    """Paint overlapping leaf clusters back-to-front; each cluster is a lit dome with leaf bumps."""
    rng = np.random.default_rng(seed)
    dith = bayer(sp.h, sp.w)
    bumps = noise(sp.h, sp.w, leaf_px, seed + 3)
    occl = np.zeros((sp.h, sp.w), np.float32)
    for (cx, cy, r, lift) in sorted(clusters, key=lambda c: c[1]):
        # irregular silhouette: radius modulated by leaf-sized noise
        d = np.sqrt(((sp.xx - cx) / r) ** 2 + ((sp.yy - cy) / (r * 0.9)) ** 2)
        m = d < 1.0 + (bumps - 0.5) * 0.28
        if not m.any():
            continue
        sh = sphere_shade(sp, cx - r * 0.1, cy - r * 0.15, r * 1.05, r * 0.95)
        sh = sh * 0.82 + lift * 0.18 + (bumps - 0.5) * 0.22
        # clusters lower in the crown and under others are darker (ambient occlusion)
        sh = sh - occl * 0.08
        col = quant(sh, R, dith)
        sp.put(m, col)
        occl = np.maximum(occl, m * 0.9)
        # sparse bright leaf glints on the lit side
        glint = m & (sh > 0.78) & (rng.random((sp.h, sp.w)) < 0.025)
        sp.rgb[glint] = R[-1]


def broadleaf(R=LEAF, seed=1, w=184, h=260, blossoms=None):
    sp = Sprite(w, h)
    rng = np.random.default_rng(seed)
    cx = w / 2
    # trunk + root flare
    base = h - 6
    tw = 22
    trunk = sp.poly([(cx - tw / 2 + 2, base - 95), (cx + tw / 2 - 2, base - 95), (cx + tw / 2 + 4, base - 8), (cx + tw / 2 + 12, base),
                     (cx - tw / 2 - 12, base), (cx - tw / 2 - 4, base - 8)])
    bx = (sp.xx - (cx - tw / 2 - 8)) / (tw + 16)
    bark_n = noise(h, w, 3, seed + 9)
    stripes = (np.sin(sp.xx * 1.3 + bark_n * 3) * 0.5 + 0.5)
    col = quant(np.clip(0.75 - bx * 0.6 + (stripes - 0.5) * 0.25, 0, 1), BARK, bayer(h, w))
    sp.put(trunk, col)
    # two branches into the crown
    for sx, ex in ((-1, -30), (1, 34)):
        br = sp.poly([(cx + sx * 2, base - 80), (cx + sx * 10, base - 88), (cx + ex + 5, base - 130), (cx + ex - 5, base - 132)])
        sp.put(br, BARK[2])
    # crown: dome of clusters
    clusters = []
    crown_cx, crown_cy, crx, cry = cx, base - 150, w * 0.46, 88
    for i in range(26):
        a = rng.uniform(0, 2 * np.pi)
        rr = np.sqrt(rng.uniform(0, 1))
        x = crown_cx + np.cos(a) * crx * rr * 0.78
        y = crown_cy + np.sin(a) * cry * rr * 0.72
        r = rng.uniform(26, 36) * (1.1 - rr * 0.25)
        lift = np.clip(0.5 - (y - crown_cy) / cry * 0.5 - (x - crown_cx) / crx * 0.25, 0, 1)
        clusters.append((x, y, r, lift))
    _leafy_cluster_field(sp, clusters, R, seed)
    if blossoms is not None:
        rng2 = np.random.default_rng(seed + 77)
        leaf = sp.a > 0.5
        ys, xs = np.nonzero(leaf & (sp.yy < base - 100))
        for i in rng2.integers(0, len(ys), 130):
            y, x = ys[i], xs[i]
            c = blossoms[rng2.integers(1, len(blossoms))]
            sp.rgb[y:y + 2, x:x + 2] = c
            sp.rgb[y, x] = blossoms[-1]
    outline(sp, R[0] * 0.75)
    return sp


def pine(seed=2, w=150, h=270, R=PINE):
    sp = Sprite(w, h)
    rng = np.random.default_rng(seed)
    cx, base = w / 2, h - 6
    trunk = sp.rect(cx - 7, base - 40, 14, 40)
    sp.put(trunk, quant(0.6 - (sp.xx - cx + 7) / 14 * 0.5, BARK, bayer(h, w)))
    dith = bayer(h, w)
    tiers = 6
    for t in range(tiers):
        ty = base - 34 - t * 36
        half = (tiers - t) * 12 + 14
        top = ty - 62
        pts = [(cx, top)]
        n = 9
        for i in range(n + 1):
            u = i / n
            x = cx - half + u * 2 * half
            droop = 8 * np.sin(u * np.pi * 4) ** 2
            pts.append((x, ty + droop))
        m = sp.poly(pts)
        u = (sp.xx - cx) / half
        v = (sp.yy - top) / (ty - top + 1e-3)
        shade = 0.55 - u * 0.35 - v * 0.25 + 0.25 * (t / tiers) + (noise(h, w, 4, seed + t) - 0.5) * 0.3
        sp.put(m, quant(shade, R, dith * 0.4 + 0.3))
        # needle tufts at the tier edge
        edge = m & (v > 0.82)
        sp.rgb[edge & (dith > 0.5)] = R[1]
    outline(sp, R[0] * 0.7)
    return sp


def bush(seed=3, w=96, h=70, R=LEAF, flowers=None):
    sp = Sprite(w, h)
    rng = np.random.default_rng(seed)
    clusters = []
    for i in range(9):
        x = w / 2 + rng.uniform(-w * 0.3, w * 0.3)
        y = h - 26 + rng.uniform(-14, 6)
        r = rng.uniform(16, 22)
        clusters.append((x, y, r, np.clip(0.6 - (y - (h - 30)) / 30 - (x - w / 2) / w * 0.4, 0, 1)))
    _leafy_cluster_field(sp, clusters, R, seed, leaf_px=4)
    if flowers is not None:
        ys, xs = np.nonzero(sp.a > 0.5)
        for i in rng.integers(0, len(ys), 26):
            y, x = ys[i], xs[i]
            sp.rgb[y:y + 3, x:x + 3] = flowers[2]
            sp.rgb[y, x] = flowers[3]
            sp.rgb[y + 2:y + 3, x + 2:x + 3] = flowers[1]
    outline(sp, R[0] * 0.75)
    return sp


def rock(seed=4, w=64, h=44, R=STONE):
    sp = Sprite(w, h)
    rng = np.random.default_rng(seed)
    pts = []
    for i in range(9):
        a = np.pi + i / 8 * np.pi
        rx, ry = w * 0.46 * rng.uniform(0.85, 1.0), h * 0.82 * rng.uniform(0.8, 1.0)
        pts.append((w / 2 + np.cos(a) * rx, h - 4 + np.sin(a) * ry))
    pts += [(w * 0.94, h - 4), (w * 0.06, h - 4)]
    m = sp.poly(pts)
    sh = sphere_shade(sp, w / 2, h - 4, w * 0.48, h * 0.9)
    facet = (np.floor((sp.xx * 0.7 + sp.yy) / 9) % 2) * 0.08
    sp.put(m, quant(sh * 0.9 + facet + (noise(h, w, 3, seed) - 0.5) * 0.15, R, bayer(h, w)))
    # moss cap
    moss = m & (sp.yy < h * 0.45) & (noise(h, w, 5, seed + 1) > 0.55)
    sp.rgb[moss] = LEAF[3]
    outline(sp, R[0] * 0.8)
    return sp


def flower_clump(kind=0, seed=5, w=56, h=34):
    """Floor-layer clump: leaves + small blossoms, no outline (reads as part of the ground)."""
    sp = Sprite(w, h)
    rng = np.random.default_rng(seed)
    F = FLOWERS[kind % len(FLOWERS)]
    for i in range(18):
        x, y = rng.uniform(6, w - 6), rng.uniform(8, h - 4)
        m = sp.ellipse(x, y, rng.uniform(3, 6), rng.uniform(2, 4))
        sp.put(m, LEAF[rng.integers(2, 5)])
    for i in range(14):
        x, y = rng.uniform(6, w - 6), rng.uniform(4, h - 8)
        m = sp.ellipse(x, y, 2.6, 2.2)
        sp.put(m, F[2])
        sp.rgb[int(y) - 1, int(x) - 1] = F[3]
        sp.rgb[int(y), int(x)] = hexrgb('#ffe9a0')
    return sp


def reeds(seed=6, w=60, h=90):
    sp = Sprite(w, h)
    rng = np.random.default_rng(seed)
    for i in range(16):
        x0 = rng.uniform(10, w - 10)
        top = rng.uniform(8, 40)
        bend = rng.uniform(-8, 8)
        for y in range(int(top), h - 2):
            t = (y - top) / (h - top)
            x = x0 + bend * (1 - t) ** 2
            sp.put(sp.rect(int(x), y, 2, 1), LEAF[2 + (i % 3)])
        if rng.random() < 0.6:   # cattail head
            m = sp.ellipse(x0 + bend, top + 6, 2.5, 7)
            sp.put(m, BARK[3])
    outline(sp, LEAF[0] * 0.8, inner=False, width=1)
    return sp


def stump(seed=7, w=64, h=48):
    sp = Sprite(w, h)
    side = sp.rect(10, 16, 44, 26) | sp.ellipse(32, 42, 22, 5)
    sp.put(side, quant(0.7 - (sp.xx - 10) / 44 * 0.6, BARK, bayer(h, w)))
    top = sp.ellipse(32, 16, 22, 8)
    rings = (np.sqrt(((sp.xx - 32) / 22) ** 2 + ((sp.yy - 16) / 8) ** 2) * 5) % 1
    sp.put(top, np.where((rings < 0.25)[..., None], hexrgb('#b48a5f'), hexrgb('#d6b07e')))
    outline(sp, BARK[0])
    return sp
