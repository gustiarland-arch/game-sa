"""v6 art kit core: palette ramps, shaded volumes and outline rules shared by every HD sprite.

All sprites are authored at 2 texels per world unit (files end in @2x.png) and share one light
direction (top-left), one outline rule (darker, hue-shifted rim on the shadow side, no black lines)
and limited colour ramps, so trees, houses and props read as one art set.
"""
import numpy as np
from PIL import Image

LIGHT = np.array([-0.55, -0.75, 0.65])
LIGHT = LIGHT / np.linalg.norm(LIGHT)


def hexrgb(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32)


def ramp(*hexes):
    return np.array([hexrgb(h) for h in hexes], np.float32)


# shared ramps (dark -> light)
LEAF = ramp('#1f3b2d', '#2b5537', '#3b7040', '#4f8a47', '#6aa54f', '#8cc062', '#b4d97c')
LEAF_DARK = ramp('#17302a', '#204233', '#2d5a3c', '#3c7142', '#52884a', '#6c9f55', '#8db86a')
PINE = ramp('#14302c', '#1d4135', '#275640', '#356b48', '#468052', '#5d9660', '#7cae70')
CHERRY = ramp('#6b3050', '#8c3f62', '#b05677', '#cc7190', '#e294aa', '#f1b6c4', '#fbd9df')
AUTUMN = ramp('#5c2a1c', '#7c3a1f', '#a04f22', '#c26a28', '#dc8a33', '#eeac4a', '#f7cd70')
BARK = ramp('#2e1f1a', '#43302a', '#5a4236', '#735643', '#8c6c52', '#a68566')
STONE = ramp('#3a3d4a', '#4f5361', '#666b78', '#7f8590', '#9aa0a8', '#b8bdc2', '#d6d9da')
WOOD = ramp('#3b2418', '#55341f', '#704628', '#8d5c33', '#a87443', '#c18f58', '#d8ac76')
ROOF_BLUE = ramp('#1f2a4a', '#2b3a63', '#3a4e7e', '#4c6597', '#6382b0', '#84a2c8')
ROOF_RED = ramp('#4a1f1f', '#6a2a26', '#8c3a2f', '#ad4f38', '#c96a46', '#de8c5e')
ROOF_GREEN = ramp('#1e3a30', '#28503d', '#346748', '#457f55', '#5d9866', '#7ab07c')
PLASTER = ramp('#6d5f55', '#8b7c6e', '#a99a88', '#c6b8a3', '#ded2bd', '#efe6d4', '#faf5ea')
BRICK = ramp('#4a2a25', '#663a30', '#83503d', '#9e6649', '#b98159', '#cf9d74')
METAL = ramp('#1c2128', '#2a313a', '#3b444f', '#515c68', '#6b7783', '#8995a0', '#aab4bc')
WATER = ramp('#1b3f5e', '#245273', '#2f6788', '#3c7d9c', '#4f93ae', '#69aabf', '#8fc4d2')
FLOWERS = [ramp('#7a2840', '#b33a55', '#e0627a', '#f7a3b0'), ramp('#6b5a12', '#b09318', '#e7c636', '#fbe98a'),
           ramp('#3f2d6e', '#5c44a0', '#8a72cf', '#bfaef0'), ramp('#7a7f8a', '#c9ccd2', '#eef0f2', '#ffffff'),
           ramp('#7a3a12', '#c2611e', '#ef8f3b', '#ffc27a')]


class Sprite:
    """RGBA canvas with helpers; y grows downward like the map."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.rgb = np.zeros((h, w, 3), np.float32)
        self.a = np.zeros((h, w), np.float32)
        self.yy, self.xx = np.mgrid[0:h, 0:w].astype(np.float32)

    def put(self, mask, col, alpha=1.0):
        col = np.asarray(col, np.float32)
        if col.ndim == 1:
            self.rgb[mask] = col
        else:
            self.rgb[mask] = col[mask]
        self.a[mask] = np.maximum(self.a[mask], alpha)

    def ellipse(self, cx, cy, rx, ry):
        return ((self.xx - cx) / rx) ** 2 + ((self.yy - cy) / ry) ** 2 <= 1

    def rect(self, x, y, w, h):
        return (self.xx >= x) & (self.xx < x + w) & (self.yy >= y) & (self.yy < y + h)

    def poly(self, pts):
        from matplotlib.path import Path as MP
        P = MP(pts)
        inside = P.contains_points(np.stack([self.xx.ravel() + 0.5, self.yy.ravel() + 0.5], 1))
        return inside.reshape(self.h, self.w)

    def image(self):
        out = np.dstack([np.clip(self.rgb, 0, 255), np.clip(self.a * 255, 0, 255)]).astype(np.uint8)
        return Image.fromarray(out, 'RGBA')

    def save(self, path):
        self.image().save(path, optimize=True)


def quant(val, R, dither=None):
    """Map 0..1 shading values to a ramp with optional ordered dither between steps."""
    n = len(R)
    v = np.clip(val, 0, 0.999) * n
    if dither is not None:
        v = v + (dither - 0.5) * 0.55
    idx = np.clip(v.astype(int), 0, n - 1)
    return R[idx]


BAYER = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], np.float32) + 0.5) / 16


def bayer(h, w):
    return np.tile(BAYER, (h // 4 + 1, w // 4 + 1))[:h, :w]


def sphere_shade(sp, cx, cy, rx, ry, mask=None):
    """Lambert shading of an ellipsoid; returns 0..1."""
    nx = (sp.xx + 0.5 - cx) / rx
    ny = (sp.yy + 0.5 - cy) / ry
    d = np.clip(1 - nx * nx - ny * ny, 0, 1)
    nz = np.sqrt(d)
    l = nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2]
    return np.clip(0.18 + 0.82 * l, 0, 1)


def outline(sp, R_dark, inner=True, width=2):
    """Coloured outline: outer rim on the alpha edge, darker on the bottom/right shadow side."""
    from scipy import ndimage
    m = sp.a > 0.5
    grown = ndimage.binary_dilation(m, iterations=width) & ~m
    edge_in = m & ~ndimage.binary_erosion(m, iterations=width)
    shadow_side = (np.roll(m, -width, 0) == 0) | (np.roll(m, -width, 1) == 0)
    sp.rgb[grown] = R_dark
    sp.a[grown] = 1
    if inner:
        sp.rgb[edge_in & shadow_side] = sp.rgb[edge_in & shadow_side] * 0.78


def noise(h, w, scale, seed):
    rng = np.random.default_rng(seed)
    gh, gw = h // scale + 3, w // scale + 3
    g = rng.random((gh, gw)).astype(np.float32)
    im = Image.fromarray((g * 255).astype(np.uint8)).resize((gw * scale, gh * scale), Image.BICUBIC)
    return np.asarray(im, np.float32)[:h, :w] / 255.0


def sheet(sprites, path, bg=(92, 140, 84)):
    """Contact sheet of (name, Image) on a grass-coloured background for review."""
    pad = 12
    W = sum(im.width + pad for _, im in sprites) + pad
    H = max(im.height for _, im in sprites) + pad * 2
    out = Image.new('RGBA', (W, H), bg + (255,))
    x = pad
    for _, im in sprites:
        out.alpha_composite(im, (x, H - pad - im.height))
        x += im.width + pad
    out.save(path)
