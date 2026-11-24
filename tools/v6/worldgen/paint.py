"""v6 ground painter: reusable pixel-art materials for designed (not classified) maps.

Every function paints into a float32 RGB canvas through a boolean mask, so a map layout
is a sequence of shapes -> masks -> materials. Deterministic for a given seed.
"""
import numpy as np
from ground import noise, dist_from


def rgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32)


def hash2(a, b, seed=0):
    """Integer hash of two int arrays -> [0,1)."""
    h = (np.asarray(a, np.int64) * 73856093) ^ (np.asarray(b, np.int64) * 19349663) ^ (seed * 83492791)
    h = (h ^ (h >> 13)) * 1274126177
    return ((h ^ (h >> 16)) & 0xFFFF) / 65536.0


class Canvas:
    def __init__(self, w, h, seed):
        self.w, self.h, self.seed = w, h, seed
        self.img = np.zeros((h, w, 3), np.float32)
        self.mat = np.zeros((h, w), np.int8)      # material id per pixel (for edges)
        self.yy, self.xx = np.mgrid[0:h, 0:w]

    # ---------------------------------------------------------------- shapes
    def rect(self, x, y, w, h):
        return (self.xx >= x) & (self.xx < x + w) & (self.yy >= y) & (self.yy < y + h)

    def rrect(self, x, y, w, h, r):
        m = self.rect(x, y, w, h)
        for cx, cy in ((x + r, y + r), (x + w - r, y + r), (x + r, y + h - r), (x + w - r, y + h - r)):
            corner = ((self.xx < x + r) if cx == x + r else (self.xx >= x + w - r)) & \
                     ((self.yy < y + r) if cy == y + r else (self.yy >= y + h - r))
            m &= ~(corner & ((self.xx - cx) ** 2 + (self.yy - cy) ** 2 > r * r))
        return m

    def ellipse(self, cx, cy, rx, ry):
        return ((self.xx - cx) / rx) ** 2 + ((self.yy - cy) / ry) ** 2 < 1

    def poly_path(self, pts, width):
        """Thick polyline (round joins)."""
        m = np.zeros((self.h, self.w), bool)
        r = width / 2
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            dx, dy = x1 - x0, y1 - y0
            L2 = dx * dx + dy * dy or 1
            x_lo, x_hi = int(max(0, min(x0, x1) - r - 1)), int(min(self.w, max(x0, x1) + r + 2))
            y_lo, y_hi = int(max(0, min(y0, y1) - r - 1)), int(min(self.h, max(y0, y1) + r + 2))
            X = self.xx[y_lo:y_hi, x_lo:x_hi]; Y = self.yy[y_lo:y_hi, x_lo:x_hi]
            t = np.clip(((X - x0) * dx + (Y - y0) * dy) / L2, 0, 1)
            d2 = (X - x0 - t * dx) ** 2 + (Y - y0 - t * dy) ** 2
            m[y_lo:y_hi, x_lo:x_hi] |= d2 <= r * r
        return m

    def wobble(self, mask, amp=2, scale=7, salt=0):
        """Organic, pixel-stepped boundary."""
        nz = noise(self.h, self.w, scale, self.seed + 900 + salt)
        nz2 = noise(self.h, self.w, scale, self.seed + 901 + salt)
        sx = np.clip(self.xx + ((nz - .5) * 2 * amp).round().astype(int), 0, self.w - 1)
        sy = np.clip(self.yy + ((nz2 - .5) * 2 * amp).round().astype(int), 0, self.h - 1)
        return mask[sy, sx]

    def put(self, mask, color_img, mat):
        self.img[mask] = color_img[mask]
        self.mat[mask] = mat

    # ---------------------------------------------------------------- materials
    def grass(self, pal=('#579a60', '#5ea166', '#66a96b', '#6eb070', '#77b875', '#82c07d')):
        p = np.stack([rgb(c) for c in pal])
        H, W, s = self.h, self.w, self.seed
        v = 0.4 * noise(H, W, 120, s + 1) + 0.35 * noise(H, W, 40, s + 2) + 0.25 * noise(H, W, 11, s + 3)
        idx = np.clip(((v - 0.18) / 0.64 * (len(p) - 1)).round().astype(int), 0, len(p) - 1)
        img = p[idx]
        # dither the band borders with a 2x2 checker so bands read as pixel art, not posterised
        frac = (v - 0.18) / 0.64 * (len(p) - 1) - idx
        chk = ((self.xx + self.yy) % 2 == 0)
        up = (frac > 0.32) & chk & (idx < len(p) - 1)
        img[up] = p[np.clip(idx + 1, 0, len(p) - 1)][up]
        # micro texture: 2px clumps of +-5% so the lawn reads as blades, not a smooth wash
        micro = hash2(self.xx // 2, self.yy, s + 5)
        img = img * (0.95 + 0.1 * micro)[..., None]
        rng = np.random.default_rng(s + 4)
        n = H * W // 85
        ys = rng.integers(4, H - 2, n); xs = rng.integers(2, W - 2, n)
        for y, x in zip(ys, xs):          # tufts: dark roots, light tips
            base = img[y + 1, x]
            img[y, x - 1] = img[y, x] = img[y, x + 1] = base * 0.72
            img[y - 1, x - 1] = base * 0.88
            img[y - 1, x] = base * 1.02
            img[y - 2, x] = np.clip(base * 1.22 + 8, 0, 255)
            img[y - 1, x + 1] = np.clip(base * 1.14, 0, 255)
            if rng.random() < 0.35:
                img[y - 2, x - 1] = np.clip(base * 1.12, 0, 255)
        flowers = [rgb(c) for c in ('#fbf6ec', '#f7c9d9', '#f4d870', '#c4b2f2')]
        for _ in range(H * W // 2600):
            y, x = rng.integers(2, H - 2), rng.integers(2, W - 2)
            c = flowers[rng.integers(0, len(flowers))]
            img[y, x] = c; img[y + 1, x] = img[y + 1, x] * 0.7
        return img

    def bricks(self, pal, bw=18, bh=9, mortar='#8f7a62', tint_scale=80, salt=0):
        p = np.stack([rgb(c) for c in pal])
        X, Y = self.xx, self.yy
        row = Y // bh
        col = (X + (row % 2) * (bw // 2)) // bw
        r = hash2(row, col, self.seed + salt)
        tone = noise(self.h, self.w, tint_scale, self.seed + 40 + salt)
        k = np.clip((r * 0.6 + tone * 0.8 - 0.1) * (len(p) - 1), 0, len(p) - 1).round().astype(int)
        img = p[k].copy()
        lx = (X + (row % 2) * (bw // 2)) % bw
        ly = Y % bh
        img[ly == 0] = np.clip(img[ly == 0] * 1.08 + 6, 0, 255)          # top light
        m = rgb(mortar)
        img[(ly == bh - 1) | (lx == 0)] = m
        img[(ly == bh - 2) & (lx != 0)] *= 0.94                         # bottom shade
        chip = hash2(row * 7 + 3, col * 5 + 1, self.seed + 77 + salt) < 0.07
        cpx = (lx == 2 + (r * 10).astype(int) % max(1, bw - 4)) & (ly == 3) & chip
        img[cpx] *= 0.82
        return img

    def radial(self, cx, cy, ry_scale, pal, ring=12, blen=20, salt=0, mortar='#8a7258'):
        p = np.stack([rgb(c) for c in pal])
        dx = (self.xx - cx).astype(np.float32); dy = (self.yy - cy) / ry_scale
        r = np.sqrt(dx * dx + dy * dy)
        th = np.arctan2(dy, dx) + np.pi
        ri = (r // ring).astype(int)
        nper = np.maximum(1, np.round(2 * np.pi * (ri + 0.5) * ring / blen))
        along = th / (2 * np.pi) * nper + 0.5 * (ri % 2)
        bi = np.floor(along).astype(int)
        h = hash2(ri, bi, self.seed + salt)
        k = np.clip((h * (len(p) - 1)).round().astype(int), 0, len(p) - 1)
        img = p[k].copy()
        m = rgb(mortar)
        img[(r % ring) < 1.0] = m
        img[(along % 1) * blen < 1.0] = m
        return img, r, th, ri

    def tiles(self, a, b, size=24, grout='#9b7a5e', salt=0):
        X, Y = self.xx, self.yy
        tx, ty = X // size, Y // size
        A, B = rgb(a), rgb(b)
        img = np.where(((tx + ty) % 2 == 0)[..., None], A, B).astype(np.float32)
        var = hash2(tx, ty, self.seed + salt)[..., None]
        img *= 0.94 + 0.1 * var
        lx, ly = X % size, Y % size
        img[(lx == 1) | (ly == 1)] = np.clip(img[(lx == 1) | (ly == 1)] * 1.07, 0, 255)
        img[(lx == 0) | (ly == 0)] = rgb(grout)
        wear = noise(self.h, self.w, 40, self.seed + salt + 5) > 0.72
        img[wear] = img[wear] * 0.9 + rgb('#b09070') * 0.1
        return img

    def planks(self, pal=('#8a5a3a', '#9a6844', '#a8744c', '#b58156'), ph=10, salt=0, vertical=False):
        p = np.stack([rgb(c) for c in pal])
        X, Y = (self.yy, self.xx) if vertical else (self.xx, self.yy)
        row = Y // ph
        seg_len = 64 + (hash2(row, 0, self.seed + salt) * 60).astype(int)
        off = (hash2(row, 1, self.seed + salt) * 90).astype(int)
        seg = (X + off) // seg_len
        k = np.clip((hash2(row, seg, self.seed + salt + 2) * (len(p) - 1)).round().astype(int), 0, len(p) - 1)
        img = p[k].copy()
        grain = noise(self.h, self.w, 5, self.seed + salt + 3)
        img *= (0.94 + 0.1 * grain)[..., None]
        ly = Y % ph; lx = (X + off) % seg_len
        img[ly == 0] = rgb('#5a3826')
        img[ly == 1] = np.clip(img[ly == 1] * 1.1, 0, 255)
        img[lx == 0] = rgb('#5a3826')
        nail = ((lx == 3) | (lx == seg_len - 4)) & (ly == ph // 2)
        img[nail] = rgb('#4a3020')
        return img

    def dirt(self, pal=('#a88760', '#b6946a', '#c3a276', '#cfb085')):
        p = np.stack([rgb(c) for c in pal])
        v = 0.65 * noise(self.h, self.w, 26, self.seed + 60) + 0.35 * noise(self.h, self.w, 6, self.seed + 61)
        idx = np.clip(((v - 0.2) / 0.6 * (len(p) - 1)).round().astype(int), 0, len(p) - 1)
        img = p[idx]
        rng = np.random.default_rng(self.seed + 62)
        for _ in range(self.h * self.w // 500):
            y, x = rng.integers(1, self.h - 2), rng.integers(1, self.w - 2)
            img[y, x:x + 2] = p[0] * 0.92; img[y - 1, x] = p[-1] * 1.05
        return np.clip(img, 0, 255)

    def water(self, mask, pal=('#24577f', '#2b6990', '#357ca2', '#4290b4', '#5aa6c6')):
        p = np.stack([rgb(c) for c in pal])
        d = dist_from(~mask, 24) / 24.0
        v = 0.55 * (1 - d) + 0.45 * noise(self.h, self.w, 30, self.seed + 70)
        idx = np.clip((v * (len(p) - 1)).round().astype(int), 0, len(p) - 1)
        img = p[idx]
        rng = np.random.default_rng(self.seed + 71)
        hl = rgb('#a9d8ec')
        ys, xs = np.nonzero(mask)
        for i in rng.integers(0, len(ys), max(1, len(ys) // 600)):
            y, x = ys[i], xs[i]
            img[y, x:x + rng.integers(3, 8)] = hl
        return img

    # ---------------------------------------------------------------- finishing
    def rim(self, hard, soft, dark='#5c4632', width=1, ao=(0.8, 0.88, 0.95)):
        """Dark rim inside hard surfaces where they meet soft ground, occlusion on the soft side."""
        d_in = dist_from(~hard, 3)
        self.img[hard & (d_in == 1)] = self.img[hard & (d_in == 1)] * 0.55 + rgb(dark) * 0.45
        if width > 1:
            self.img[hard & (d_in == 2)] *= 0.9
        d_out = dist_from(hard, len(ao) + 1)
        for i, f in enumerate(ao, 1):
            self.img[soft & (d_out == i)] *= f

    def overhang(self, hard, grass_mask, p=0.3, salt=0):
        d_in = dist_from(~hard, 2)
        edge = hard & (d_in == 1)
        ys, xs = np.nonzero(edge)
        rng = np.random.default_rng(self.seed + 300 + salt)
        pick = rng.random(len(ys)) < p
        for y, x in zip(ys[pick], xs[pick]):
            for dy, dx in ((-3, 0), (3, 0), (0, -3), (0, 3)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < self.h and 0 <= xx < self.w and grass_mask[yy, xx]:
                    src = self.img[yy, xx]
                    self.img[y, x] = src * 0.82
                    y2, x2 = y - np.sign(dy), x - np.sign(dx)
                    if 0 <= y2 < self.h and 0 <= x2 < self.w and hard[y2, x2] and rng.random() < 0.5:
                        self.img[y2, x2] = src * 0.7
                    break

    def shadow(self, mask, f=0.72):
        self.img[mask] *= f

    def result(self):
        return np.clip(self.img, 0, 255).astype(np.uint8)


# ----------------------------------------------------------------------------- polish pass
def bake_details(c, props, P, assets, seed=0):
    """Ground details that depend on where props stand: contact shadows, petals and
    leaves under trees, worn ground in front of benches and doors."""
    from PIL import Image
    rng = np.random.default_rng(seed + 501)
    sizes = {}
    for pr in props:
        t = pr['type']
        if t not in sizes:
            with Image.open(assets / P[t]['image']) as im:
                a = np.array(im.convert('RGBA'))[:, :, 3]
            cols = np.nonzero(a[-max(6, a.shape[0] // 5):].max(axis=0) > 40)[0]   # footprint width
            sizes[t] = (im.width, im.height, (cols.max() - cols.min() + 1) if len(cols) else im.width)
    shade = np.ones((c.h, c.w), np.float32)
    for pr in props:
        t = pr['type']; layer = P[t].get('layer', 'sort')
        if layer == 'floor':
            continue
        w, h, foot = sizes[t]
        x, y = pr['x'], pr['y']
        tree = t.startswith(('tree', 'v41_tree', 'v43_v41_tree', 'v44_tree'))
        bld = 'bld_' in t
        if bld:
            x0, x1 = int(x - foot * 0.47), int(x + foot * 0.47)
            for i, f in enumerate((0.6, 0.72, 0.84, 0.92)):
                yy = y + i * 3
                if 0 <= yy < c.h:
                    shade[yy:yy + 3, max(0, x0 + i * 2):min(c.w, x1 + 10 - i * 2)] = np.minimum(
                        shade[yy:yy + 3, max(0, x0 + i * 2):min(c.w, x1 + 10 - i * 2)], f)
            continue
        rx = max(6, (w * 0.40) if tree else foot * 0.55)
        ry = max(3, rx * (0.32 if tree else 0.28))
        cx, cy = x + (4 if tree else 2), y - (2 if tree else 0)
        y0, y1 = int(max(0, cy - ry - 2)), int(min(c.h, cy + ry + 2))
        x0, x1 = int(max(0, cx - rx - 2)), int(min(c.w, cx + rx + 2))
        if y1 <= y0 or x1 <= x0:
            continue
        d = ((c.xx[y0:y1, x0:x1] - cx) / rx) ** 2 + ((c.yy[y0:y1, x0:x1] - cy) / ry) ** 2
        f = np.where(d < 0.45, 0.66, np.where(d < 0.75, 0.76, np.where(d < 1.0, 0.87, 1.0)))
        shade[y0:y1, x0:x1] = np.minimum(shade[y0:y1, x0:x1], f)
        # petals / leaves around trees
        if tree:
            pal = {'cherry': ('#f6c2d4', '#eaa3bd', '#fbe1ea'), 'autumn': ('#e59a3e', '#cf7b2c', '#f2bf62')}
            kind = 'cherry' if 'cherry' in t else 'autumn' if 'autumn' in t else None
            if kind:
                cols = [rgb(cc) for cc in pal[kind]]
                for _ in range(46):
                    ang = rng.uniform(0, 2 * np.pi); rr = abs(rng.normal(0, w * 0.45))
                    px, py = int(x + np.cos(ang) * rr * 1.3), int(y - 6 + np.sin(ang) * rr * 0.6)
                    if 1 <= px < c.w - 2 and 1 <= py < c.h - 1:
                        col = cols[rng.integers(0, 3)]
                        c.img[py, px] = col
                        if rng.random() < 0.4:
                            c.img[py, px + 1] = col * 0.9
    c.img *= shade[..., None]
    return c


def wear(c, mask, strength=0.07, salt=0):
    """Large-scale stains and sun-bleaching so wide paved areas are not flat."""
    v = 0.6 * noise(c.h, c.w, 90, c.seed + 700 + salt) + 0.4 * noise(c.h, c.w, 24, c.seed + 701 + salt)
    f = 1 + (v - 0.5) * 2 * strength
    c.img[mask] *= f[mask][:, None]
    rng = np.random.default_rng(c.seed + 702 + salt)
    ys, xs = np.nonzero(mask)
    if len(ys):
        for i in rng.integers(0, len(ys), max(1, len(ys) // 9000)):   # small stains
            y, x = ys[i], xs[i]
            r = rng.integers(3, 9)
            sl = c.ellipse(x, y, r * 1.6, r) & mask
            c.img[sl] *= 0.93
    return c


def moss(c, hard, grass, p=0.5, salt=0):
    """Moss creeping into the mortar of hard surfaces near grass."""
    d = dist_from(grass, 10)
    zone = hard & (d > 0) & (d < 10)
    lum = c.img.mean(axis=2)
    mortarish = lum < np.percentile(lum[hard], 25) if hard.any() else zone
    nz = noise(c.h, c.w, 14, c.seed + 720 + salt)
    sel = zone & mortarish & (nz * (1.2 - d / 10) > 1 - p)
    c.img[sel] = c.img[sel] * 0.45 + rgb('#5f8f4e') * 0.55
    return c
