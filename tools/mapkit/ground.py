"""Pelukis lapisan tanah (numpy) untuk peta pixel art: rumput, jalan tanah, batu, air, lantai kayu, dinding, dunia kenangan.
Semua deterministik (seed) sehingga build ulang menghasilkan gambar identik.
"""
import numpy as np

def rgb(h):
    h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.int16)

class Canvas:
    def __init__(self, w, h, seed):
        self.w, self.h = w, h
        self.px = np.zeros((h, w, 3), np.int16)
        self.rng = np.random.default_rng(seed)
        self.yy, self.xx = np.mgrid[0:h, 0:w]

    # ---------- utilitas mask
    def mask(self): return np.zeros((self.h, self.w), bool)

    def rect(self, m, x, y, w, h, r=0):
        x0, y0, x1, y1 = int(x), int(y), int(x + w), int(y + h)
        c = lambda v, hi: max(0, min(hi, v))
        if r <= 0:
            m[c(y0, self.h):c(y1, self.h), c(x0, self.w):c(x1, self.w)] = True
            return m
        m[c(y0 + r, self.h):c(y1 - r, self.h), c(x0, self.w):c(x1, self.w)] = True
        m[c(y0, self.h):c(y1, self.h), c(x0 + r, self.w):c(x1 - r, self.w)] = True
        for cx, cy in ((x0 + r, y0 + r), (x1 - r - 1, y0 + r), (x0 + r, y1 - r - 1), (x1 - r - 1, y1 - r - 1)):
            self.ellipse(m, cx, cy, r + 0.5, r + 0.5)
        return m

    def ellipse(self, m, cx, cy, rx, ry):
        m[((self.xx - cx) / rx) ** 2 + ((self.yy - cy) / ry) ** 2 <= 1] = True
        return m

    def poly_path(self, m, pts, width):
        """Jalan berkelok: polyline tebal dengan ujung bulat."""
        r = width / 2
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            dx, dy = x1 - x0, y1 - y0
            L2 = max(1e-6, dx * dx + dy * dy)
            bx0, bx1 = int(min(x0, x1) - r - 1), int(max(x0, x1) + r + 2)
            by0, by1 = int(min(y0, y1) - r - 1), int(max(y0, y1) + r + 2)
            bx0, by0 = max(0, bx0), max(0, by0)
            X, Y = self.xx[by0:by1, bx0:bx1], self.yy[by0:by1, bx0:bx1]
            t = np.clip(((X - x0) * dx + (Y - y0) * dy) / L2, 0, 1)
            d2 = (X - (x0 + t * dx)) ** 2 + (Y - (y0 + t * dy)) ** 2
            m[by0:by1, bx0:bx1] |= d2 <= r * r
        return m

    def noise(self, cell, seed_off=0):
        """Value noise halus 0..1."""
        rng = np.random.default_rng(int(self.rng.integers(1 << 30)) + seed_off)
        gw, gh = self.w // cell + 3, self.h // cell + 3
        g = rng.random((gh, gw))
        fx = self.xx / cell; fy = self.yy / cell
        x0 = fx.astype(int); y0 = fy.astype(int)
        tx = fx - x0; ty = fy - y0
        tx = tx * tx * (3 - 2 * tx); ty = ty * ty * (3 - 2 * ty)
        a = g[y0, x0]; b = g[y0, x0 + 1]; c = g[y0 + 1, x0]; d = g[y0 + 1, x0 + 1]
        return a * (1 - tx) * (1 - ty) + b * tx * (1 - ty) + c * (1 - tx) * ty + d * tx * ty

    @staticmethod
    def edge(m):
        """Piksel di dalam mask yang bersebelahan dengan luar mask."""
        e = np.zeros_like(m)
        e[1:, :] |= m[1:, :] & ~m[:-1, :]; e[:-1, :] |= m[:-1, :] & ~m[1:, :]
        e[:, 1:] |= m[:, 1:] & ~m[:, :-1]; e[:, :-1] |= m[:, :-1] & ~m[:, 1:]
        return e

    @staticmethod
    def dilate(m, n=1):
        o = m.copy()
        for _ in range(n):
            t = o.copy()
            t[1:, :] |= o[:-1, :]; t[:-1, :] |= o[1:, :]; t[:, 1:] |= o[:, :-1]; t[:, :-1] |= o[:, 1:]
            o = t
        return o

    def dist_in(self, m, maxd):
        """Jarak (langkah) ke tepi untuk piksel di dalam mask, dibatasi maxd."""
        d = np.full(m.shape, maxd, np.int16)
        cur = m.copy()
        for k in range(maxd):
            er = cur.copy()
            er[1:, :] &= cur[:-1, :]; er[:-1, :] &= cur[1:, :]; er[:, 1:] &= cur[:, :-1]; er[:, :-1] &= cur[:, 1:]
            d[cur & ~er] = np.minimum(d[cur & ~er], k)
            cur = er
        d[~m] = -1
        return d

    # ---------- pelukis
    def fill(self, m, col): self.px[m] = rgb(col)

    BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0

    def _shift(self, mk, dy, dx):
        o = np.zeros_like(mk)
        ys0, ys1 = max(0, dy), self.h + min(0, dy); xs0, xs1 = max(0, dx), self.w + min(0, dx)
        o[ys0:ys1, xs0:xs1] = mk[ys0 - dy:ys1 - dy, xs0 - dx:xs1 - dx]
        return o

    def grass(self, m, pal=('#74b262', '#7ebb69', '#89c571', '#5e9a50'), flowers=0.0012, tufts=0.006,
              flower_cols=('#ffffff', '#ffe28a', '#f7b6cf', '#c9b6ef')):
        """Rumput berlapis: 3 nada dengan dither Bayer (bukan bercak acak), rumpun ber-highlight, helai, semanggi, kerikil."""
        n = self.noise(56); n2 = self.noise(14, 7); n3 = self.noise(5, 3)
        v = n * 0.62 + n2 * 0.28 + n3 * 0.10
        dith = self.BAYER[self.yy % 4, self.xx % 4] - 0.5
        q = np.clip(((v - 0.30) / 0.42) * 3 + dith * 0.55, 0, 2.99).astype(int)
        cols = np.array([rgb(c) for c in pal[:3]])
        out = cols[q]
        self.px[m] = out[m]
        dark, light = rgb(pal[3]), rgb(pal[2]) + 16
        # rumpun rumput: tepi atas terang, tepi bawah gelap (kesan volume)
        cm = (self.noise(9, 11) > 0.64) & m
        top = cm & ~self._shift(cm, 1, 0); bot = cm & ~self._shift(cm, -1, 0)
        self.px[top] = light; self.px[bot & ~top] = dark
        # helai rumput halus
        bm = m & (self.rng.random((self.h, self.w)) < 0.03)
        self.px[bm] = (self.px[bm] * 0.86).astype(np.int16)
        up = self._shift(bm, -1, 0) & m; self.px[up] = (self.px[up] * 0.9).astype(np.int16)
        tip = self._shift(bm, -2, 0) & m & (self.rng.random((self.h, self.w)) < 0.5); self.px[tip] = light
        # semanggi kecil & kerikil
        cl = m & (self.rng.random((self.h, self.w)) < 0.0012)
        for dy, dx in ((0, 0), (0, 1), (-1, 0), (-1, 1)):
            mm = self._shift(cl, dy, dx) & m; self.px[mm] = rgb(pal[2]) + 26
        pb = m & (self.rng.random((self.h, self.w)) < 0.0009)
        self.px[pb] = rgb('#a9a39a'); pb2 = self._shift(pb, 0, 1) & m; self.px[pb2] = rgb('#cfc9c0')
        ys, xs = np.nonzero(m & (self.rng.random((self.h, self.w)) < tufts))
        dark, light = rgb(pal[3]), rgb(pal[2]) + 18
        for y, x in zip(ys, xs):
            if 2 <= x < self.w - 2 and 2 <= y < self.h - 1:
                self.px[y, x - 1] = dark; self.px[y - 1, x] = dark; self.px[y, x + 1] = dark; self.px[y - 2, x] = light
        ys, xs = np.nonzero(m & (self.rng.random((self.h, self.w)) < flowers))
        for y, x in zip(ys, xs):
            if 1 <= x < self.w - 1 and 1 <= y < self.h - 1:
                c = rgb(flower_cols[int(self.rng.integers(len(flower_cols)))])
                self.px[y, x - 1] = c; self.px[y, x + 1] = c; self.px[y - 1, x] = c; self.px[y + 1, x] = c
                self.px[y, x] = rgb('#ffd86b')

    def dirt(self, m, base='#d9b98a', dark='#b8955f', light='#ead0a4', rim='#4f8a46'):
        """Jalan tanah: 3 nada dither, jejak roda, kerikil bersorot, tepi bertingkat, rumput menjuntai."""
        n = self.noise(22) * 0.55 + self.noise(7, 4) * 0.45
        dith = self.BAYER[self.yy % 4, self.xx % 4] - 0.5
        q = np.clip(((n - 0.3) / 0.4) * 3 + dith * 0.6, 0, 2.99).astype(int)
        cols = np.array([rgb(dark) + 10, rgb(base), rgb(light)])
        self.px[m] = cols[q][m]
        acc = getattr(self, '_dirt_acc', None)
        u = m if acc is None else (m | acc)
        self._dirt_acc = u
        d = self.dist_in(u, 6)
        if acc is not None:   # tepi jalan lama yang kini berada di tengah persimpangan: lukis ulang
            fix = acc & ~m & self.dilate(m, 3) & (d >= 2); self.px[fix] = cols[q][fix]
        self.px[m & (d == 1)] = rgb(dark); self.px[m & (d == 0)] = rgb(dark) - 18
        peb = m & (d > 2) & (self.rng.random((self.h, self.w)) < 0.0035)
        self.px[peb] = rgb(dark) - 28
        hl = self._shift(peb, 0, 1) & m; self.px[hl] = rgb(light) + 12
        sh = self._shift(peb, 1, 0) & m; self.px[sh] = rgb(dark) - 10
        ring = self.dilate(u, 1) & ~u & self.dilate(m, 1)
        self.px[ring] = rgb(rim)
        hang = self._shift(ring, 1, 0) & m & (self.rng.random((self.h, self.w)) < 0.35)
        self.px[hang] = rgb(rim) + 14

    def cobble(self, m, base='#cdbba6', var=18, grout='#9e8a78', hl='#e3d5c4', sw=(12, 20), sh=11):
        y = 0; row = 0
        canvas = np.zeros((self.h, self.w), np.int16)
        lab = np.full((self.h, self.w), -1, np.int32)
        sid = 0
        while y < self.h:
            x = -int(self.rng.integers(0, sw[1] + 1))
            while x < self.w:
                wst = int(self.rng.integers(sw[0], sw[1] + 1))
                lab[y:y + sh, max(0, x):max(0, x + wst)] = sid
                sid += 1; x += wst
            y += sh; row += 1
        tone = self.rng.integers(-var, var, sid + 1)
        b = rgb(base)
        img = b[None, None, :] + tone[np.clip(lab, 0, sid)][..., None]
        # grout: tepi label
        g = np.zeros((self.h, self.w), bool)
        g[:, 1:] |= lab[:, 1:] != lab[:, :-1]
        g[1:, :] |= lab[1:, :] != lab[:-1, :]
        h1 = np.zeros((self.h, self.w), bool)
        h1[1:, 1:] = g[:-1, 1:] & ~g[1:, 1:]
        img[h1] = rgb(hl)
        img[g] = rgb(grout)
        speck = self.rng.random((self.h, self.w)) < 0.03
        img[speck & ~g] -= 10
        self.px[m] = img[m]
        self.px[self.edge(m)] = rgb(grout) - 25

    def water(self, m, deep='#3f7fb0', mid='#5a9fcb', shallow='#86c4dd', foam='#e9f6fb', sand='#ead7a6', shore=5):
        d = self.dist_in(m, 14)
        img = np.where((d < 3)[..., None], rgb(shallow), np.where((d < 8)[..., None], rgb(mid), rgb(deep)))
        n = self.noise(20)
        img = img + ((n - 0.5) * 16)[..., None].astype(np.int16)
        self.px[m] = img[m]
        # kilau horizontal
        ys, xs = np.nonzero(m & (d > 3) & (self.rng.random((self.h, self.w)) < 0.0035))
        for y, x in zip(ys, xs):
            L = int(self.rng.integers(3, 9))
            self.px[y, x:min(self.w, x + L)] = rgb('#cfe9f5')
        self.px[m & (d == 0)] = rgb(foam)
        if shore > 0:
            ring = self.dilate(m, shore) & ~m
            sn = (self.rng.random((self.h, self.w)) < 0.08)
            self.px[ring] = rgb(sand)
            self.px[ring & sn] = rgb(sand) - 22
            self.px[self.dilate(m, shore + 1) & ~self.dilate(m, shore)] = rgb(sand) - 35

    def wood_floor(self, m, base='#b98a5e', var=14, seam='#7d5638', ph=16):
        lab = np.full((self.h, self.w), 0, np.int32)
        sid = 1; y = 0
        while y < self.h:
            x = -int(self.rng.integers(0, 90))
            while x < self.w:
                L = int(self.rng.integers(56, 150))
                lab[y:y + ph, max(0, x):max(0, x + L)] = sid
                sid += 1; x += L
            y += ph
        tone = self.rng.integers(-var, var, sid + 1)
        img = rgb(base)[None, None, :] + tone[lab][..., None]
        grain = (np.sin(self.xx * 0.21 + lab * 1.7) > 0.93) & (self.rng.random((self.h, self.w)) < 0.6)
        img[grain] -= 12
        s = np.zeros((self.h, self.w), bool)
        s[:, 1:] |= lab[:, 1:] != lab[:, :-1]
        s[1:, :] |= lab[1:, :] != lab[:-1, :]
        img[s] = rgb(seam)
        hl = np.zeros_like(s); hl[1:, :] = s[:-1, :] & ~s[1:, :]
        img[hl] += 14
        self.px[m] = img[m]

    def tiles(self, m, a='#f3ece4', b='#d9cfc4', grout='#b5a89a', t=24):
        chk = ((self.xx // t + self.yy // t) % 2 == 0)
        img = np.where(chk[..., None], rgb(a), rgb(b))
        g = (self.xx % t == 0) | (self.yy % t == 0)
        img[g] = rgb(grout)
        self.px[m] = img[m]

    def wallpaper(self, x, y, w, h, base='#e7cfd6', stripe='#dcbcc7', motif='#f6e6ea', panel='#c9a3b0', trim='#7d5a66', wainscot=46):
        m = self.rect(self.mask(), x, y, w, h)
        img = np.where(((self.xx // 12) % 2 == 0)[..., None], rgb(base), rgb(stripe))
        mot = ((self.xx % 24 == 6) & (self.yy % 28 == 10)) | ((self.xx % 24 == 18) & (self.yy % 28 == 24))
        img[mot] = rgb(motif)
        self.px[m] = img[m]
        # list atas
        self.fill(self.rect(self.mask(), x, y, w, 8), trim)
        self.fill(self.rect(self.mask(), x, y + 8, w, 3), panel)
        # wainscot bawah
        wy = y + h - wainscot
        self.fill(self.rect(self.mask(), x, wy, w, wainscot), panel)
        for px in range(int(x) + 8, int(x + w) - 30, 64):
            self.fill(self.rect(self.mask(), px, wy + 8, 52, wainscot - 18), self.hexmix(panel, '#ffffff', 0.18))
            self.fill(self.rect(self.mask(), px, wy + 8, 52, 1), self.hexmix(panel, '#000000', 0.25))
        self.fill(self.rect(self.mask(), x, wy - 3, w, 3), trim)
        self.fill(self.rect(self.mask(), x, y + h - 6, w, 6), trim)

    @staticmethod
    def hexmix(a, b, t):
        ca, cb = rgb(a), rgb(b)
        c = (ca * (1 - t) + cb * t).astype(int)
        return '#%02x%02x%02x' % tuple(int(v) for v in c)

    def window(self, x, y, w=72, h=84, frame='#6b4e3d', glass='#bfe3f2', sky='#fde9c8', curtain='#f0b8c8'):
        self.fill(self.rect(self.mask(), x - 4, y - 4, w + 8, h + 8), frame)
        gm = self.rect(self.mask(), x, y, w, h)
        grad = (self.yy - y) / max(1, h)
        img = (rgb(sky)[None, None, :] * (1 - grad[..., None]) + rgb(glass)[None, None, :] * grad[..., None]).astype(np.int16)
        self.px[gm] = img[gm]
        for k in range(3):  # kilau diagonal
            sh = gm & (np.abs((self.xx - x) - (self.yy - y) * 0.8 - 14 - k * 4) < 1.2)
            self.px[sh] = rgb('#ffffff')
        self.fill(self.rect(self.mask(), x + w // 2 - 2, y, 4, h), frame)
        self.fill(self.rect(self.mask(), x, y + h // 2 - 2, w, 4), frame)
        self.fill(self.rect(self.mask(), x - 6, y + h + 4, w + 12, 6), self.hexmix(frame, '#ffffff', 0.25))
        self.fill(self.rect(self.mask(), x - 10, y - 8, 14, h + 14), curtain)
        self.fill(self.rect(self.mask(), x + w - 4, y - 8, 14, h + 14), curtain)
        self.fill(self.rect(self.mask(), x - 12, y - 12, w + 24, 5), frame)

    def sunbeam(self, x, y, w, h, strength=0.10):
        """Cahaya jendela miring di lantai (mencerahkan)."""
        m = (self.yy >= y) & (self.yy < y + h) & (self.xx >= x + (self.yy - y) * 0.45) & (self.xx < x + w + (self.yy - y) * 0.45)
        self.px[m] = (self.px[m] * (1 - strength) + 255 * strength).astype(np.int16)

    def shadow(self, cx, cy, rx, ry, k=0.78):
        m = ((self.xx - cx) / max(1, rx)) ** 2 + ((self.yy - cy) / max(1, ry)) ** 2 <= 1
        self.px[m] = (self.px[m] * k).astype(np.int16)

    def dream(self, m, pal=('#6d6aa8', '#7b78b8', '#8d89c6', '#5b5893'), glow=('#fff3c4', '#ffd1ea', '#c8f0ff'), dens=0.0016):
        self.grass(m, pal=pal, flowers=0, tufts=0.004)
        ys, xs = np.nonzero(m & (self.rng.random((self.h, self.w)) < dens))
        for y, x in zip(ys, xs):
            c = rgb(glow[int(self.rng.integers(len(glow)))])
            if 1 <= x < self.w - 1 and 1 <= y < self.h - 1:
                self.px[y, x] = c
                if self.rng.random() < 0.4:
                    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                        self.px[y + dy, x + dx] = (c * 0.6 + self.px[y + dy, x + dx] * 0.4).astype(np.int16)

    def starry(self, m, base='#1d2347', base2='#262d5c', dens=0.004):
        n = self.noise(64)
        img = np.where((n > 0.55)[..., None], rgb(base2), rgb(base))
        self.px[m] = img[m]
        ys, xs = np.nonzero(m & (self.rng.random((self.h, self.w)) < dens))
        for y, x in zip(ys, xs):
            b = int(self.rng.integers(150, 256))
            self.px[y, x] = (b, b, min(255, b + 20))
            if b > 235 and 1 <= x < self.w - 1 and 1 <= y < self.h - 1:
                for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                    self.px[y + dy, x + dx] = (120, 130, 190)

    def glow_stones(self, m, col='#cfd8ff', rim='#8f9be0'):
        self.cobble(m, base=col, var=16, grout=rim, hl='#ffffff', sw=(14, 24), sh=12)

    def flower_patch(self, cx, cy, r, cols=('#ffffff', '#ffe28a', '#f7b6cf', '#c9b6ef'), dens=0.09, nogo=None):
        x0, y0, x1, y1 = max(1, int(cx - r)), max(1, int(cy - r)), min(self.w - 2, int(cx + r)), min(self.h - 2, int(cy + r))
        for y in range(y0, y1):
            for x in range(x0, x1):
                if (x - cx) ** 2 + ((y - cy) * 1.6) ** 2 > r * r: continue
                if nogo is not None and nogo[y, x]: continue
                if self.rng.random() < dens:
                    col = rgb(cols[int(self.rng.integers(len(cols)))])
                    self.px[y, x - 1] = col; self.px[y, x + 1] = col; self.px[y - 1, x] = col; self.px[y + 1, x] = col
                    self.px[y, x] = rgb('#ffd86b')
                    self.px[y + 2, x] = rgb('#4f8a46')

    def tall_grass(self, cx, cy, r, dark='#4f8a46', light='#9bd27c', nogo=None):
        for _ in range(int(r * r * 0.12)):
            x = int(cx + self.rng.uniform(-r, r)); y = int(cy + self.rng.uniform(-r, r) * 0.6)
            if not (3 <= x < self.w - 3 and 4 <= y < self.h - 1): continue
            if nogo is not None and nogo[y, x]: continue
            self.px[y, x] = rgb(dark); self.px[y - 1, x] = rgb(dark); self.px[y - 2, x - 1] = rgb(dark); self.px[y - 3, x - 1] = rgb(light)
            self.px[y - 1, x + 1] = rgb(dark); self.px[y - 2, x + 2] = rgb(light)

    # ---------- v1.3: medan berlapis
    def cliff(self, top, face_h=56, rock='#9a8f86', dark='#6e6460', light='#b8aea4', grass_top=('#86c06c', '#90c975', '#9bd27e', '#6fa95c')):
        """Dataran tinggi: rumput lebih terang di atas, dinding batu berlapis di bawah tepi selatan.
        Mengembalikan mask dinding (untuk collision) dan menggambar bayangan di kaki tebing."""
        self.grass(top, pal=grass_top, flowers=0.001, tufts=0.005)
        below = np.zeros_like(top); below[1:, :] = top[:-1, :]
        lip = below & ~top          # baris pertama di bawah tepi selatan
        face = np.zeros_like(top)
        for k in range(face_h):
            sh = np.zeros_like(top); sh[k:, :] = lip[:self.h - k, :] if k else lip
            face |= sh
        face &= ~top
        n = self.noise(10)
        strata = ((self.yy // 9) % 2 == 0)
        img = np.where((n > 0.6)[..., None], rgb(light), np.where((n < 0.35)[..., None], rgb(dark), rgb(rock)))
        img = img - np.where(strata[..., None], 10, 0).astype(np.int16)
        cracks = self.rng.random((self.h, self.w)) < 0.01
        img[cracks] = rgb(dark) - 15
        self.px[face] = img[face]
        # rumput menjuntai di bibir tebing + garis gelap
        self.px[lip] = rgb('#5e9a50')
        lip2 = np.zeros_like(top); lip2[1:, :] = lip[:-1, :]; lip2 &= face
        self.px[lip2 & (self.rng.random((self.h, self.w)) < 0.5)] = rgb('#4f8a46')
        bottom = np.zeros_like(top); bottom[:-1, :] = face[1:, :]; base = face & ~bottom
        for k in range(1, 9):   # bayangan lembut di kaki tebing
            sh = np.zeros_like(top); sh[k:, :] = base[:self.h - k, :]
            sh &= ~face & ~top
            self.px[sh] = (self.px[sh] * (0.72 + 0.03 * k)).astype(np.int16)
        self.px[self.edge(face)] = rgb(dark) - 25
        # tepi samping dataran: garis batu tipis
        side = self.dilate(top, 2) & ~top & ~face & ~self.dilate(face, 1)
        self.px[side] = rgb(dark)
        return face, side

    def stairs(self, x, y, w, h, stone='#c9bfb4', edge='#8a7f78'):
        """Tangga batu (x,y = kiri-atas), digambar di atas dinding tebing."""
        for k, yy in enumerate(range(int(y), int(y + h), 8)):
            self.px[yy:yy + 8, int(x):int(x + w)] = rgb(stone) - (k % 2) * 8
            self.px[yy + 6:yy + 8, int(x):int(x + w)] = rgb(edge)
        self.px[int(y):int(y + h), int(x):int(x) + 2] = rgb(edge) - 20
        self.px[int(y):int(y + h), int(x + w) - 2:int(x + w)] = rgb(edge) - 20
        m = self.mask(); self.rect(m, x, y, w, h); return m

    def stream(self, pts, width=60):
        m = self.poly_path(self.mask(), pts, width)
        self.water(m, deep='#4a8cbf', mid='#62a6d0', shallow='#8ccbe2', shore=4)
        return m

    def stepping_stones(self, pts, every=26, r=8):
        """Batu pijakan di atas rumput sepanjang polyline."""
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            L = max(1, int(np.hypot(x1 - x0, y1 - y0) // every))
            for i in range(L):
                t = i / L; cx = x0 + (x1 - x0) * t + self.rng.uniform(-5, 5); cy = y0 + (y1 - y0) * t + self.rng.uniform(-4, 4)
                m = self.ellipse(self.mask(), cx, cy, r * self.rng.uniform(0.85, 1.2), r * 0.7)
                self.px[m] = rgb('#b8b0a8'); self.px[self.edge(m)] = rgb('#7d746e')
                hl = self.ellipse(self.mask(), cx - 2, cy - 2, r * 0.4, r * 0.25); self.px[hl & m] = rgb('#d6cfc8')

    def forest_floor(self, m):
        self.grass(m, pal=('#4f8a46', '#5a9750', '#669f58', '#447a3d'), flowers=0.0005, tufts=0.01)
        leaves = m & (self.rng.random((self.h, self.w)) < 0.006)
        ys, xs = np.nonzero(leaves)
        cols = [rgb('#c9873a'), rgb('#d9a441'), rgb('#9a6a3a')]
        for y, x in zip(ys, xs):
            c = cols[int(self.rng.integers(3))]
            if x + 1 < self.w: self.px[y, x] = c; self.px[y, x + 1] = c

    def cave_floor(self, m):
        n = self.noise(22) * 0.6 + self.noise(7, 5) * 0.4
        dith = self.BAYER[self.yy % 4, self.xx % 4] - 0.5
        q = np.clip(((n - 0.3) / 0.4) * 3 + dith * 0.6, 0, 2.99).astype(int)
        cols = np.array([rgb('#2f2b42'), rgb('#3a3550'), rgb('#46415e')])
        img = cols[q]
        self.px[m] = img[m]
        cr = (self.noise(6, 9) > 0.7) & m
        self.px[cr & ~self._shift(cr, 1, 0)] = rgb('#57527a'); self.px[cr & ~self._shift(cr, -1, 0)] = rgb('#25222f')
        peb = m & (self.rng.random((self.h, self.w)) < 0.004); self.px[peb] = rgb('#5d5878')
        glint = m & (self.rng.random((self.h, self.w)) < 0.0012); self.px[glint] = rgb('#9fd8ff')

    def wobble(self, m, grow=10, amp=14, cell=16):
        """Tepi mask jadi tidak beraturan (gua, danau alami)."""
        big = self.dilate(m, grow)
        d = self.dist_in(big, grow + amp + 4)
        return big & (d > 3 + self.noise(cell, 21) * amp)

    def vignette(self, strength=0.18):
        cx, cy = self.w / 2, self.h / 2
        d = np.sqrt(((self.xx - cx) / cx) ** 2 + ((self.yy - cy) / cy) ** 2)
        k = 1 - strength * np.clip(d - 0.55, 0, 1)
        self.px = (self.px * k[..., None]).astype(np.int16)

    def tint(self, col, t):
        self.px = (self.px * (1 - t) + rgb(col) * t).astype(np.int16)

    def to_image(self):
        from PIL import Image
        return Image.fromarray(np.clip(self.px, 0, 255).astype(np.uint8), 'RGB')
