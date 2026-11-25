"""v6 HD map builder: paints a designed ground at 2 texels per world unit, places HD kit props,
derives collision from the painted water, validates every quest point and writes the result.

A map script provides:
  AREA, W, H, SEED
  design(m)      -> paints the ground through the helpers below and appends props with m.prop()
  DECOR (opt)    dict of extra fields written into the area (e.g. 'water' zones, 'animals')
Run:  python3 <script> --preview out.png   |   --apply
"""
import sys, json
from pathlib import Path
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from paint import Canvas, rgb            # noqa: E402
from ground import noise, dist_from      # noqa: E402
import common                            # noqa: E402

K = 2                       # texels per world unit
TILE = 2048                 # texture tile size in texels (<= 4096 for old GPUs)
A = common.A
GRASS, PATH, STONE, WATER, DECK, SAND, SOIL, BED = 1, 2, 3, 6, 5, 8, 9, 10


class HDMap:
    def __init__(self, area, W, H, seed):
        self.area, self.W, self.H, self.seed = area, W, H, seed
        self.c = Canvas(W * K, H * K, seed)
        self.props = []
        self.walk_over = np.zeros((H * K, W * K), bool)   # decks/bridges over water stay walkable
        self.rng = np.random.default_rng(seed + 7)
        self.keep_out = []   # (x, y, r) world circles where nothing may be planted

    # --------------------------------------------------------------- geometry (world coords)
    def ellipse(self, cx, cy, rx, ry, wob=0, salt=0):
        m = self.c.ellipse(cx * K, cy * K, rx * K, ry * K)
        return self.c.wobble(m, wob * K, 9 * K, salt) if wob else m

    def path(self, pts, width, wob=0, salt=0):
        m = self.c.poly_path([(x * K, y * K) for x, y in pts], width * K)
        return self.c.wobble(m, wob * K, 6 * K, salt) if wob else m

    def rect(self, x, y, w, h):
        return self.c.rect(x * K, y * K, w * K, h * K)

    def prop(self, pid, x, y, keep=True):
        self.props.append(dict(type=pid, x=int(x), y=int(y)))

    # --------------------------------------------------------------- planting
    def free(self, x, y, blocked, r, P):
        if x < 30 or y < 60 or x > self.W - 30 or y > self.H - 10:
            return False
        X, Y = int(x * K), int(y * K)
        rr = int(r * K)
        if blocked[max(0, Y - rr):Y + rr, max(0, X - rr):X + rr].any():
            return False
        for kx, ky, kr in self.keep_out:
            if (x - kx) ** 2 + (y - ky) ** 2 < kr * kr:
                return False
        for p in self.props:
            d = P[p['type']]
            if d.get('cw', 0) > 0 and abs(p['x'] - x) < max(28, d['cw'] / 2 + 18) and -30 < p['y'] - y < 40:
                return False
        return True

    def scatter(self, ids, weights, n, region, blocked, r, P, tries=40):
        x0, y0, w, h = region
        wts = np.array(weights, float) / sum(weights)
        placed = 0
        for _ in range(n * tries):
            if placed >= n:
                break
            x, y = x0 + self.rng.uniform(0, w), y0 + self.rng.uniform(0, h)
            if self.free(x, y, blocked, r, P):
                self.prop(ids[self.rng.choice(len(ids), p=wts)], x, y)
                placed += 1
        return placed

    # --------------------------------------------------------------- finishing
    def bake_shadows(self, P):
        """Soft shadows cast toward the bottom-right (light from the top-left), under every
        standing prop at its exact placement, so sprites sit on the ground instead of floating."""
        c = self.c
        sh = np.zeros((c.h, c.w), np.float32)
        for p in self.props:
            d = P[p['type']]
            if d.get('layer') == 'floor':
                continue
            im = Image.open(A / d['image'])
            sw = im.width * (0.5 if '@2x' in d['image'] else 1.0)
            tall = im.height * (0.5 if '@2x' in d['image'] else 1.0)
            tree = 'tree' in p['type']
            rx = sw * (0.46 if tree else 0.52)
            ry = rx * (0.36 if tree else 0.30)
            cx = p['x'] + (sw * 0.10 if tree else 6)
            cy = p['y'] - (2 if not tree else 4) + (ry * 0.2)
            X0, X1 = int(max(0, (cx - rx - 4) * K)), int(min(c.w, (cx + rx + 4) * K))
            Y0, Y1 = int(max(0, (cy - ry - 4) * K)), int(min(c.h, (cy + ry + 4) * K))
            if X1 <= X0 or Y1 <= Y0:
                continue
            xx, yy = c.xx[Y0:Y1, X0:X1] / K, c.yy[Y0:Y1, X0:X1] / K
            dd = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
            a = np.clip(1.15 - dd, 0, 1) * (0.42 if tree else 0.34)
            if tall > 120 and not tree:
                a *= 1.1
            sh[Y0:Y1, X0:X1] = np.maximum(sh[Y0:Y1, X0:X1], a)
        chk = ((c.xx // 2 + c.yy // 2) % 2 == 0)
        sh = np.where(chk, sh, sh * 0.85)
        water = c.mat == WATER
        sh[water] *= 0.5
        tint = rgb('#1d3324')
        c.img = c.img * (1 - sh[..., None]) + tint * sh[..., None]

    def collision(self, P):
        water = (self.c.mat == WATER) & ~self.walk_over
        small = water.reshape(self.H, K, self.W, K).any(axis=(1, 3))
        return common.mask_to_walls(small, step=8)

    def write(self, base_entry, extra, P, Q, apply=False, preview=None, checks=True):
        c = self.c
        img = np.clip(c.img, 0, 255).astype(np.uint8)
        walls = self.collision(P)
        a = dict(base_entry)
        a.update(dict(w=self.W, h=self.H, walls=walls, ellipses=[], props=self.props,
                      elevationPlatforms=[], visualStyle='v6_hd_kit', visualUpdate='v6_hd_rebuild'))
        a.pop('environmentV51', None)
        a.update(extra)
        tiles = []
        for ty in range(0, c.h, TILE):
            for tx in range(0, c.w, TILE):
                tiles.append(dict(image='maps/hd/%s_%d_%d@2x.png' % (self.area, ty // TILE, tx // TILE),
                                  x=tx // K, y=ty // K, w=min(TILE, c.w - tx) // K, h=min(TILE, c.h - ty) // K))
        a['tiles'] = tiles
        pts = [(m[0], m[3], m[4], m[5]) for m in common.migrate_quests(json.loads(json.dumps(Q)), self.area, lambda x, y: (x, y))]
        pts += [('examine ' + e['id'], e['x'], e['y'], e.get('r')) for e in a.get('examine', [])]
        M = json.loads((A / 'data/maps.json').read_text(encoding='utf-8'))
        pts += [(d['id'], d['tx'], d['ty'], None) for b in M['areas'].values() for d in b.get('doors', []) if d.get('to') == self.area]
        bad = common.validate(a, P, pts) if checks else []
        for b in bad:
            print('INVALID', *b)
        print(self.area, len(self.props), 'props,', len(walls), 'walls,', len(pts), 'points,', len(bad), 'invalid')
        if preview:
            hd = Image.fromarray(img).convert('RGBA')
            for pr in sorted(self.props, key=lambda p: (P[p['type']].get('layer') != 'floor', p['y'])):
                t = Image.open(A / P[pr['type']]['image']).convert('RGBA')
                k = 1 if '@2x' in P[pr['type']]['image'] else 2
                if k == 2:
                    t = t.resize((t.width * 2, t.height * 2), Image.NEAREST)
                hd.alpha_composite(t, (int(pr['x'] * K - t.width / 2), int(pr['y'] * K - t.height)))
            hd.convert('RGB').save(preview.replace('.png', '_hd.png'))
        if apply:
            if bad and '--force' not in sys.argv:
                raise SystemExit('not applied: fix invalid points first')
            (A / 'maps/hd').mkdir(parents=True, exist_ok=True)
            for t in tiles:
                X, Y = t['x'] * K, t['y'] * K
                Image.fromarray(img[Y:Y + t['h'] * K, X:X + t['w'] * K]).save(A / t['image'], optimize=True)
            Image.fromarray(img).resize((self.W, self.H), Image.LANCZOS).save(A / a['image'], optimize=True)
            M['areas'][self.area] = a
            (A / 'data/maps.json').write_text(json.dumps(M, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            print('applied', len(tiles), 'tiles')
        return bad
