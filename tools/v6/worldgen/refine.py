"""v6 refine pass for hand-composed painted maps (keeps size, layout, colours and every coordinate).

Usage: python3 tools/v6/worldgen/refine.py <area> [--out PNG]

Only flat-colour areas are touched (pixels whose 7x7 neighbourhood is one colour), so line art,
puzzle marks and accents keep their exact original pixels. Flat areas get
  - quantised value noise with checker dither (painted-material feel instead of flat fill),
  - a soft 2px ambient-occlusion band along every colour edge,
  - star dust on dark night areas and shimmer streaks on blue water areas.
"""
import sys, json, hashlib
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from ground import noise   # noqa: E402

A = HERE.parents[2] / 'android' / 'assets'


def refine(img, seed):
    H, W = img.shape[:2]
    a = img.astype(np.float32)
    key = (img[..., 0].astype(np.int32) << 16) | (img[..., 1].astype(np.int32) << 8) | img[..., 2]
    kimg = Image.fromarray((key % 65521).astype(np.int32))
    same = np.array(kimg.filter(ImageFilter.MaxFilter(7))) == np.array(kimg.filter(ImageFilter.MinFilter(7)))
    edge = ~(np.array(kimg.filter(ImageFilter.MaxFilter(3))) == np.array(kimg.filter(ImageFilter.MinFilter(3))))
    near_edge = np.array(Image.fromarray(edge.astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(5))) > 0
    v = 0.55 * noise(H, W, 46, seed + 1) + 0.3 * noise(H, W, 14, seed + 2) + 0.15 * noise(H, W, 4, seed + 3)
    chk = (np.indices((H, W)).sum(0) % 2 == 0)
    f = 1 + (np.floor(v * 3) / 2.0 - 0.5) * 0.06
    f = np.where(((v * 3) % 1 > 0.85) & chk, f + 0.03, f)
    out = a.copy()
    out[same] = a[same] * f[same][:, None]
    ao = near_edge & ~edge & ~same
    out[ao] = out[ao] * 0.94
    rng = np.random.default_rng(seed)
    lum = a.mean(-1); r, g, b = a[..., 0], a[..., 1], a[..., 2]
    dark = same & (lum < 60)
    ys, xs = np.nonzero(dark)
    for i in rng.integers(0, max(1, len(ys)), len(ys) // 260 if len(ys) else 0):
        y, x = ys[i], xs[i]
        out[y, x] = (232, 230, 255) if rng.random() < 0.8 else (255, 236, 170)
    water = same & (b > r + 25) & (b > 90) & (lum >= 60)
    ys, xs = np.nonzero(water)
    for i in rng.integers(0, max(1, len(ys)), len(ys) // 900 if len(ys) else 0):
        y, x = ys[i], xs[i]; n = rng.integers(3, 8)
        seg = water[y, x:x + n]
        out[y, x:x + n][seg] = np.clip(a[y, x] * 1.25 + 22, 0, 255)
    return np.clip(out, 0, 255).astype(np.uint8)


if __name__ == '__main__':
    area = sys.argv[1]
    M = json.loads((A / 'data/maps.json').read_text(encoding='utf-8'))
    a = M['areas'][area]
    pre = HERE / 'pre_v6'
    src = pre / (area + '.png')
    if not src.exists():
        Image.open(A / a['image']).convert('RGB').save(src)
    seed = int(hashlib.sha256((area + '_refine').encode()).hexdigest()[:8], 16)
    out = refine(np.array(Image.open(src).convert('RGB')), seed)
    dst = Path(sys.argv[sys.argv.index('--out') + 1]) if '--out' in sys.argv else A / a['image']
    Image.fromarray(out, 'RGB').save(dst, optimize=True)
    print(area, 'refined ->', dst)
