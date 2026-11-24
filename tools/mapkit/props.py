"""Pelukis properti pixel art (PIL). Setiap prop didaftarkan dengan collision kaki (cw, ch) dan bayangan (rx, ry).
Jangkar = tengah-bawah gambar. Semua orisinal, prosedural.
"""
import math, random
from PIL import Image, ImageDraw, ImageFont

OL = (58, 44, 64, 255)
REG = {}

def C(h, a=255):
    h = h.lstrip('#'); return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)

def mul(c, k): return tuple(max(0, min(255, int(v * k))) for v in c[:3]) + (c[3] if len(c) > 3 else 255,)
def mix(c, d, t): return tuple(int(c[i] * (1 - t) + d[i] * t) for i in range(3)) + (255,)
WHITE = (255, 255, 255, 255)

def prop(name, cw, ch, shadow=None, layer='sort'):
    def deco(fn):
        REG[name] = dict(fn=fn, cw=cw, ch=ch, shadow=shadow, layer=layer)
        return fn
    return deco

def new(w, h): return Image.new('RGBA', (w, h), (0, 0, 0, 0))

def box(d, x0, y0, x1, y1, fill, ol=OL, hl=1.18, sh=0.82):
    d.rectangle([x0, y0, x1, y1], fill=ol)
    d.rectangle([x0 + 1, y0 + 1, x1 - 1, y1 - 1], fill=fill)
    if hl and x1 - x0 > 3: d.line([x0 + 1, y0 + 1, x1 - 1, y0 + 1], fill=mul(fill, hl))
    if sh and y1 - y0 > 3: d.line([x0 + 1, y1 - 1, x1 - 1, y1 - 1], fill=mul(fill, sh))

def blob(d, cx, cy, r, fill, ol=OL):
    d.ellipse([cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1], fill=ol)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)

def font(sz):
    try: return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', sz)
    except Exception: return ImageFont.load_default()

def text(d, xy, s, col, sz=9, anchor='mm'):
    d.fontmode = '1'
    d.text(xy, s, fill=col, font=font(sz), anchor=anchor)

def flower_dot(d, x, y, col):
    d.point([(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)], fill=col); d.point([(x, y)], fill=C('#ffd86b'))

# ============================================================ BANGUNAN
def building(w=240, wall_h=118, roof_h=78, wall='#f3dccb', roof='#c8697c', trim='#8d5a4c', style='siding',
             door=0.5, windows=(0.2, 0.8), sign=None, sign_col='#6b4e8a', awning=None, chimney=True, door_col='#7a5240',
             window_col='#bfe3f2', curtain='#f4c2cf', flowerbox=True, seed=1, glow=False):
    rng = random.Random(seed)
    ov = 10
    W, H = w + ov * 2, roof_h + wall_h
    im = new(W, H); d = ImageDraw.Draw(im)
    rf = C(roof); wl = C(wall); tr = C(trim)
    # cerobong
    if chimney:
        cx = int(W * 0.72); box(d, cx, 4, cx + 18, roof_h - 20, C('#b07a6a'))
        box(d, cx - 2, 2, cx + 20, 9, C('#8f6252'))
    # atap trapesium
    top_in = 18
    d.polygon([(top_in, 8), (W - top_in, 8), (W - 1, roof_h), (0, roof_h)], fill=OL)
    d.polygon([(top_in + 1, 9), (W - top_in - 1, 9), (W - 3, roof_h - 1), (2, roof_h - 1)], fill=rf)
    for i, y in enumerate(range(15, roof_h - 4, 7)):
        t = (y - 8) / (roof_h - 8)
        x0 = int(top_in - top_in * t) + 3; x1 = int(W - top_in + top_in * t) - 3
        d.line([x0, y, x1, y], fill=mul(rf, 0.8))
        off = 0 if i % 2 == 0 else 6
        for x in range(x0 + off, x1, 12): d.line([x, y - 6, x, y], fill=mul(rf, 0.86))
        d.line([x0, y + 1, x1, y + 1], fill=mul(rf, 1.1))
    d.line([top_in + 1, 9, W - top_in - 1, 9], fill=mul(rf, 1.3)); d.line([top_in + 1, 10, W - top_in - 1, 10], fill=mul(rf, 1.15))
    d.rectangle([0, roof_h - 6, W - 1, roof_h], fill=OL); d.rectangle([1, roof_h - 5, W - 2, roof_h - 1], fill=mul(rf, 0.62))
    # dinding
    y0 = roof_h; y1 = H - 1
    d.rectangle([ov, y0, W - ov - 1, y1], fill=OL)
    d.rectangle([ov + 1, y0, W - ov - 2, y1 - 1], fill=wl)
    if style == 'siding':
        for y in range(y0 + 6, y1 - 10, 7): d.line([ov + 1, y, W - ov - 2, y], fill=mul(wl, 0.9))
    elif style == 'brick':
        for r, y in enumerate(range(y0 + 2, y1 - 10, 7)):
            d.line([ov + 1, y, W - ov - 2, y], fill=mul(wl, 0.82))
            for x in range(ov + (0 if r % 2 else 8), W - ov, 16): d.line([x, y, x, y + 6], fill=mul(wl, 0.82))
    elif style == 'wood':
        for x in range(ov + 8, W - ov, 10): d.line([x, y0 + 1, x, y1 - 10], fill=mul(wl, 0.86))
    box(d, ov, y0, ov + 6, y1, tr, hl=None); box(d, W - ov - 7, y0, W - ov - 1, y1, tr, hl=None)
    d.rectangle([ov + 1, y1 - 9, W - ov - 2, y1 - 1], fill=C('#a69a9a')); d.line([ov + 1, y1 - 9, W - ov - 2, y1 - 9], fill=OL)
    for x in range(ov + 6, W - ov - 6, 14): d.line([x, y1 - 8, x, y1 - 2], fill=C('#8c8080'))
    # pintu
    dw, dh = 36, 56
    dx = int(ov + (w - dw) * door); dy = y1 - 9 - dh
    box(d, dx - 4, dy - 4, dx + dw + 4, y1 - 9, tr, hl=None)
    box(d, dx, dy, dx + dw, y1 - 9, C(door_col))
    box(d, dx + 5, dy + 6, dx + dw - 5, dy + 22, C(window_col) if glow else mul(C(door_col), 1.15))
    box(d, dx + 5, dy + 28, dx + dw - 5, dy + dh - 6, mul(C(door_col), 1.12))
    blob(d, dx + dw - 8, dy + dh // 2 + 4, 2, C('#ffd86b'))
    door_anchor = (dx + dw // 2, H)
    # jendela
    for fx in windows:
        ww, wh = 38, 40
        wx = int(ov + (w - ww) * fx); wy = y0 + 18
        if abs((wx + ww / 2) - (dx + dw / 2)) < 44: continue
        box(d, wx - 3, wy - 3, wx + ww + 3, wy + wh + 3, tr, hl=None)
        for yy in range(wh - 1):
            t = yy / wh
            d.line([wx, wy + yy, wx + ww, wy + yy], fill=mix(C('#fff1d6') if glow else C('#fde9c8'), C(window_col), t))
        d.line([wx + ww // 2, wy, wx + ww // 2, wy + wh], fill=tr); d.line([wx, wy + wh // 2, wx + ww, wy + wh // 2], fill=tr)
        for k in range(3): d.line([wx + 4 + k * 3, wy + wh - 3, wx + 14 + k * 3, wy + 3], fill=(255, 255, 255, 150))
        d.rectangle([wx, wy, wx + 5, wy + wh], fill=C(curtain)); d.rectangle([wx + ww - 5, wy, wx + ww, wy + wh], fill=C(curtain))
        if flowerbox:
            box(d, wx - 5, wy + wh + 3, wx + ww + 5, wy + wh + 10, C('#9b6a4c'))
            for k in range(5): flower_dot(d, wx - 1 + k * 10, wy + wh + 2, C(rng.choice(['#f7b6cf', '#ffffff', '#ffe28a', '#c9b6ef'])))
    # kanopi toko
    if awning:
        a1, a2 = C(awning[0]), C(awning[1])
        ax0, ax1, ay = dx - 26, dx + dw + 26, dy - 14
        for i, x in enumerate(range(ax0, ax1, 8)):
            d.polygon([(x, ay), (min(ax1, x + 8), ay), (min(ax1, x + 8) + 2, ay + 14), (x + 2, ay + 14)], fill=a1 if i % 2 == 0 else a2)
        d.line([ax0, ay, ax1, ay], fill=OL); d.line([ax0 + 2, ay + 14, ax1 + 2, ay + 14], fill=OL)
        for x in range(ax0 + 2, ax1, 8): d.arc([x, ay + 11, x + 8, ay + 18], 0, 180, fill=OL)
    if sign:
        sw = max(70, len(sign) * 7 + 18); sx = W // 2 - sw // 2; sy = y0 + 2 if not awning else dy - 34
        if awning: sx = dx + dw // 2 - sw // 2
        box(d, sx, sy, sx + sw, sy + 15, C(sign_col)); text(d, (sx + sw // 2, sy + 8), sign, C('#ffe9a8'), 9)
    return im, door_anchor

# ============================================================ POHON & TANAMAN
def _canopy(d, pts, base, ol=OL):
    for (x, y, r) in pts: d.ellipse([x - r - 1, y - r - 1, x + r + 1, y + r + 1], fill=ol)
    for (x, y, r) in pts: d.ellipse([x - r, y - r, x + r, y + r], fill=base)
    for (x, y, r) in pts: d.ellipse([x - r + 2, y - r + 6, x + r - 2, y + r], fill=mul(base, 0.86))
    for (x, y, r) in pts: d.ellipse([x - r + 2, y - r + 1, x + r - 6, y + r - 8], fill=base)
    for (x, y, r) in pts: d.ellipse([x - r * 0.55 - 2, y - r * 0.7, x + r * 0.1, y - r * 0.15], fill=mul(base, 1.14))

def _trunk(d, cx, top, bottom, col='#7b5238'):
    c = C(col)
    d.polygon([(cx - 7, bottom), (cx - 5, top), (cx + 5, top), (cx + 7, bottom)], fill=OL)
    d.polygon([(cx - 6, bottom - 1), (cx - 4, top), (cx + 4, top), (cx + 6, bottom - 1)], fill=c)
    d.line([cx + 2, top, cx + 3, bottom - 2], fill=mul(c, 0.75)); d.line([cx - 3, top + 6, cx - 3, bottom - 6], fill=mul(c, 1.2))
    d.line([cx - 9, bottom - 1, cx - 5, bottom - 4], fill=OL); d.line([cx + 9, bottom - 1, cx + 5, bottom - 4], fill=OL)

def tree(kind='green', seed=0):
    rng = random.Random(seed)
    W, H = 92, 130
    im = new(W, H); d = ImageDraw.Draw(im)
    cx = W // 2
    if kind == 'pine':
        _trunk(d, cx, H - 26, H - 1)
        base = C('#4f8f5f')
        for i, (y, hw) in enumerate([(H - 28, 40), (H - 52, 33), (H - 74, 25), (H - 94, 17)]):
            d.polygon([(cx - hw - 1, y + 1), (cx, y - 34), (cx + hw + 1, y + 1)], fill=OL)
            d.polygon([(cx - hw, y), (cx, y - 32), (cx + hw, y)], fill=base)
            d.polygon([(cx - hw + 4, y - 2), (cx, y - 28), (cx - 2, y - 2)], fill=mul(base, 1.15))
            d.line([cx - hw, y, cx + hw, y], fill=mul(base, 0.75))
        return im
    _trunk(d, cx, H - 44, H - 1, '#6f4a35' if kind != 'dream' else '#5a4a7a')
    base = {'green': C('#5fa463'), 'cherry': C('#f2a9c4'), 'autumn': C('#e3954f'), 'dream': C('#a59ae0'), 'lantern': C('#4f7f7a')}[kind]
    pts = [(cx, H - 78, 30), (cx - 22, H - 64, 22), (cx + 22, H - 64, 22), (cx - 10, H - 98, 20), (cx + 13, H - 94, 20), (cx, H - 58, 22)]
    _canopy(d, pts, base)
    for _ in range(14):
        x = rng.randint(cx - 30, cx + 30); y = rng.randint(H - 112, H - 50)
        if kind == 'cherry': d.point([(x, y), (x + 1, y)], fill=C('#fff0f6'))
        elif kind == 'green': d.point([(x, y)], fill=mul(base, 1.25))
        elif kind == 'autumn': d.point([(x, y)], fill=C('#f6c25a'))
        elif kind in ('dream', 'lantern'): blob(d, x, y, 1, C('#fff1b8'), C('#ffd27a'))
    if kind == 'green':
        for _ in range(4):
            x = rng.randint(cx - 26, cx + 26); y = rng.randint(H - 100, H - 56); flower_dot(d, x, y, C('#f7b6cf'))
    return im

for i, k in enumerate(['green', 'cherry', 'autumn', 'pine', 'dream', 'lantern']):
    prop('tree_' + k, 14, 8, shadow=(30, 9))(lambda k=k, i=i: tree(k, i))

@prop('bush', 34, 10, shadow=(20, 6))
def bush(flowers=True):
    im = new(46, 30); d = ImageDraw.Draw(im)
    _canopy(d, [(12, 18, 10), (24, 14, 12), (34, 18, 10)], C('#5c9e5c'))
    if flowers:
        for (x, y, c) in [(10, 14, '#f7b6cf'), (24, 9, '#ffffff'), (33, 15, '#c9b6ef'), (18, 20, '#ffe28a'), (28, 21, '#f7b6cf')]: flower_dot(d, x, y, C(c))
    return im

@prop('bush_plain', 34, 10, shadow=(20, 6))
def bush_plain(): return bush(False)

@prop('flowerbed', 60, 14, shadow=None)
def flowerbed():
    im = new(66, 30); d = ImageDraw.Draw(im)
    box(d, 0, 14, 65, 29, C('#a0714f'))
    for x in range(6, 64, 12): d.line([x, 16, x, 28], fill=mul(C('#a0714f'), 0.8))
    rng = random.Random(3)
    _canopy(d, [(10, 12, 8), (24, 10, 9), (40, 11, 9), (55, 12, 8)], C('#5c9e5c'))
    for k in range(12): flower_dot(d, rng.randint(5, 61), rng.randint(5, 15), C(rng.choice(['#f7b6cf', '#ffffff', '#ffe28a', '#c9b6ef', '#ff9fb1'])))
    return im

@prop('rock', 22, 8, shadow=(14, 5))
def rock():
    im = new(30, 20); d = ImageDraw.Draw(im)
    d.polygon([(2, 19), (5, 8), (13, 3), (24, 5), (29, 13), (27, 19)], fill=OL)
    d.polygon([(4, 18), (6, 9), (13, 5), (23, 7), (27, 13), (25, 18)], fill=C('#a7a3b4'))
    d.polygon([(7, 10), (13, 6), (19, 7), (12, 11)], fill=C('#cdc9d8'))
    return im

@prop('mushrooms', 0, 0, shadow=None)
def mushrooms():
    im = new(24, 16); d = ImageDraw.Draw(im)
    for (x, y, r, c) in [(6, 9, 5, '#e46b6b'), (16, 11, 4, '#f2a35b')]:
        d.rectangle([x - 1, y, x + 1, y + 5], fill=C('#f3ece4'), outline=OL)
        d.pieslice([x - r, y - r, x + r, y + r], 180, 360, fill=C(c), outline=OL); d.point([(x - 1, y - 2), (x + 2, y - 3)], fill=WHITE)
    return im

# ============================================================ PERABOT LUAR
@prop('lamp', 8, 6, shadow=(10, 4))
def lamp():
    im = new(22, 84); d = ImageDraw.Draw(im)
    box(d, 9, 20, 13, 80, C('#4e4a63'), hl=None); box(d, 5, 78, 17, 83, C('#4e4a63'))
    d.polygon([(3, 6), (19, 6), (16, 22), (6, 22)], fill=OL); d.polygon([(4, 7), (18, 7), (15, 21), (7, 21)], fill=C('#ffe7a6'))
    d.rectangle([7, 9, 9, 19], fill=WHITE); box(d, 2, 2, 20, 7, C('#4e4a63'))
    return im

@prop('bench', 66, 12, shadow=(36, 6))
def bench():
    im = new(72, 40); d = ImageDraw.Draw(im)
    box(d, 2, 2, 69, 9, C('#b9814f')); box(d, 2, 11, 69, 17, C('#a8723f'))
    box(d, 0, 20, 71, 27, C('#c58c57'))
    for x in (5, 61): box(d, x, 26, x + 6, 39, C('#4e4a63'), hl=None)
    for x in (8, 63): d.line([x, 8, x, 21], fill=C('#4e4a63'), width=2)
    return im

@prop('signpost', 6, 4, shadow=(10, 4))
def signpost(label='', arrow='→'):
    im = new(64, 56); d = ImageDraw.Draw(im)
    box(d, 29, 14, 34, 55, C('#8a5d3b'), hl=None)
    box(d, 2, 4, 61, 22, C('#c99a66'))
    d.polygon([(54, 6), (62, 13), (54, 20)], fill=C('#c99a66'), outline=OL)
    if label: text(d, (30, 13), label, C('#4a3426'), 8)
    return im

@prop('mailbox', 6, 4, shadow=(8, 3))
def mailbox():
    im = new(20, 40); d = ImageDraw.Draw(im)
    box(d, 8, 16, 11, 39, C('#7b5238'), hl=None)
    d.rounded_rectangle([1, 2, 18, 18], 6, fill=C('#d4646f'), outline=OL); d.line([3, 9, 16, 9], fill=mul(C('#d4646f'), 0.8))
    d.rectangle([15, 3, 17, 8], fill=C('#ffd86b'))
    return im

@prop('crate', 26, 10, shadow=(15, 5))
def crate():
    im = new(30, 30); d = ImageDraw.Draw(im)
    box(d, 1, 3, 28, 29, C('#c6935c')); d.line([2, 4, 27, 28], fill=mul(C('#c6935c'), 0.75)); d.line([27, 4, 2, 28], fill=mul(C('#c6935c'), 0.75))
    d.rectangle([1, 3, 28, 6], fill=mul(C('#c6935c'), 0.85), outline=OL)
    return im

@prop('barrel', 20, 8, shadow=(12, 4))
def barrel():
    im = new(24, 32); d = ImageDraw.Draw(im)
    d.rounded_rectangle([1, 2, 22, 31], 6, fill=C('#a8723f'), outline=OL)
    for y in (8, 24): d.line([2, y, 21, y], fill=C('#4e4a63'), width=2)
    d.ellipse([3, 1, 20, 7], fill=C('#c58c57'), outline=OL)
    return im

@prop('fence', 0, 0, shadow=None)
def fence(n=6):
    W = n * 16 + 4; im = new(W, 30); d = ImageDraw.Draw(im)
    for y in (9, 19): box(d, 0, y, W - 1, y + 4, C('#e9dccb'), hl=None)
    for i in range(n + 1):
        x = i * 16
        d.polygon([(x, 29), (x, 5), (x + 2, 2), (x + 4, 5), (x + 4, 29)], fill=OL)
        d.rectangle([x + 1, 5, x + 3, 28], fill=C('#f6eee2'))
    return im

@prop('fountain', 190, 70, shadow=None)
def fountain():
    W, H = 230, 170
    im = new(W, H); d = ImageDraw.Draw(im)
    cx = W // 2
    d.ellipse([2, 70, W - 3, H - 2], fill=OL); d.ellipse([4, 72, W - 5, H - 4], fill=C('#c9c1cf'))
    d.ellipse([14, 80, W - 15, H - 16], fill=C('#a79fb1'))
    d.ellipse([18, 84, W - 19, H - 18], fill=C('#5a9fcb'))
    d.ellipse([30, 92, W - 31, H - 26], fill=C('#6fb2d6'))
    for i in range(10):
        a = i / 10 * math.pi * 2; x = cx + math.cos(a) * 70; y = 120 + math.sin(a) * 22
        d.line([x - 4, y, x + 4, y], fill=C('#cfe9f5'))
    for k in range(16):
        a = k / 16 * math.pi * 2; x = cx + math.cos(a) * 106; y = 120 + math.sin(a) * 44
        d.ellipse([x - 7, y - 4, x + 7, y + 4], fill=C('#d9d2de'), outline=mul(C('#a79fb1'), 0.9))
    box(d, cx - 10, 50, cx + 10, 124, C('#d9d2de'))
    d.ellipse([cx - 44, 48, cx + 44, 70], fill=OL); d.ellipse([cx - 42, 49, cx + 42, 68], fill=C('#d9d2de')); d.ellipse([cx - 36, 52, cx + 36, 64], fill=C('#6fb2d6'))
    box(d, cx - 5, 18, cx + 5, 56, C('#e6e0ea'))
    d.ellipse([cx - 16, 12, cx + 16, 24], fill=C('#e6e0ea'), outline=OL)
    for k in range(-3, 4):
        d.arc([cx - 2 + k * 9 - 18, 2, cx - 2 + k * 9 + 18, 64], 200 if k < 0 else 270, 340 if k < 0 else 360 if k > 0 else 300, fill=C('#cfeefb'), width=1)
    for (x, y) in [(cx - 30, 58), (cx + 26, 60), (cx, 8), (cx - 60, 110), (cx + 66, 114)]: d.point([(x, y)], fill=WHITE)
    return im

@prop('stall_flowers', 84, 18, shadow=(46, 8))
def stall_flowers():
    im = new(96, 70); d = ImageDraw.Draw(im)
    for i, x in enumerate(range(4, 92, 11)):
        d.polygon([(x, 2), (x + 11, 2), (x + 12, 16), (x + 1, 16)], fill=C('#f4b4c8') if i % 2 == 0 else C('#ffffff'))
    d.line([4, 2, 92, 2], fill=OL); d.line([4, 16, 94, 16], fill=OL)
    for x in (8, 86): box(d, x, 16, x + 3, 50, C('#8a5d3b'), hl=None)
    box(d, 2, 44, 93, 62, C('#b9814f'))
    rng = random.Random(9)
    for i in range(6):
        bx = 6 + i * 15
        box(d, bx, 34, bx + 11, 46, C('#8fb3c9'))
        for k in range(4): flower_dot(d, bx + 2 + k * 3, 30 + (k % 2) * 3, C(rng.choice(['#f7b6cf', '#ffe28a', '#ffffff', '#ff8fa3', '#c9b6ef'])))
    for x in (6, 84): blob(d, x + 4, 64, 4, C('#4e4a63'))
    return im

@prop('vending', 26, 12, shadow=(16, 5))
def vending():
    im = new(30, 58); d = ImageDraw.Draw(im)
    box(d, 1, 1, 28, 57, C('#e86a7e')); box(d, 4, 5, 25, 34, C('#cfeefb'))
    for r in range(3):
        for c in range(3): box(d, 6 + c * 7, 7 + r * 9, 10 + c * 7, 13 + r * 9, C(['#ffd86b', '#8fd18c', '#9ec5ff'][c]), hl=None)
    box(d, 5, 40, 24, 48, C('#4e4a63'))
    return im

@prop('bus_shelter', 120, 16, shadow=(64, 8))
def bus_shelter():
    im = new(132, 96); d = ImageDraw.Draw(im)
    box(d, 2, 4, 129, 16, C('#5f7fa8'))
    for x in (6, 124): box(d, x, 16, x + 4, 92, C('#4e4a63'), hl=None)
    d.rectangle([12, 18, 120, 70], fill=(200, 230, 245, 110), outline=OL)
    d.line([66, 18, 66, 70], fill=OL)
    box(d, 20, 70, 112, 76, C('#c58c57')); box(d, 20, 76, 26, 92, C('#4e4a63'), hl=None); box(d, 106, 76, 112, 92, C('#4e4a63'), hl=None)
    box(d, 96, 0, 128, 14, C('#ffd86b')); text(d, (112, 7), 'HALTE', C('#3a2c40'), 8)
    return im

@prop('notice_board', 50, 8, shadow=(28, 5))
def notice_board():
    im = new(60, 58); d = ImageDraw.Draw(im)
    for x in (6, 50): box(d, x, 30, x + 4, 57, C('#7b5238'), hl=None)
    box(d, 1, 2, 58, 36, C('#a8723f')); box(d, 5, 6, 54, 32, C('#d8b98f'))
    for (x, y, c) in [(8, 9, '#ffffff'), (24, 11, '#f7b6cf'), (39, 8, '#ffe28a'), (14, 21, '#cfe9f5')]:
        box(d, x, y, x + 12, y + 10, C(c), hl=None); d.point([(x + 6, y + 1)], fill=C('#d4646f'))
    return im

@prop('cafe_umbrella_table', 40, 12, shadow=(30, 8))
def cafe_umbrella_table():
    im = new(80, 90); d = ImageDraw.Draw(im)
    for i in range(8):
        a0 = math.pi + i * math.pi / 8; a1 = a0 + math.pi / 8
        d.polygon([(40, 4), (40 + math.cos(a0) * 38, 30 + math.sin(a0) * 4), (40 + math.cos(a1) * 38, 30 + math.sin(a1) * 4)],
                  fill=C('#f2a9c4') if i % 2 == 0 else C('#fff4ea'), outline=OL)
    box(d, 39, 26, 41, 70, C('#4e4a63'), hl=None)
    d.ellipse([18, 62, 62, 74], fill=OL); d.ellipse([19, 63, 61, 72], fill=C('#f6eee2'))
    for x in (6, 64): box(d, x, 66, x + 10, 86, C('#c9b6ef'))
    return im

@prop('bicycle', 30, 6, shadow=(20, 4))
def bicycle():
    im = new(46, 30); d = ImageDraw.Draw(im)
    for x in (9, 36): d.ellipse([x - 8, 13, x + 8, 29], outline=OL, width=2)
    d.line([9, 21, 20, 12, 33, 12, 36, 21], fill=C('#5fa1c9'), width=2); d.line([20, 12, 24, 21, 9, 21], fill=C('#5fa1c9'), width=2)
    d.line([33, 12, 32, 6], fill=OL, width=2); d.line([28, 6, 36, 6], fill=OL, width=2); box(d, 17, 8, 24, 11, C('#4e4a63'), hl=None)
    box(d, 30, 14, 44, 20, C('#c58c57'))
    return im

@prop('gazebo', 150, 40, shadow=(84, 14))
def gazebo():
    W, H = 170, 150
    im = new(W, H); d = ImageDraw.Draw(im)
    d.polygon([(85, 2), (166, 48), (4, 48)], fill=OL); d.polygon([(85, 5), (162, 46), (8, 46)], fill=C('#f2f0f6'))
    for i in range(1, 6): d.line([85, 5, 8 + i * 25.6, 46], fill=C('#d8d2e2'))
    d.rectangle([4, 46, 166, 54], fill=OL); d.rectangle([5, 47, 165, 53], fill=C('#c9b6ef'))
    for x in (14, 54, 112, 152): box(d, x, 54, x + 6, 132, C('#f6eee2'), hl=None)
    box(d, 4, 130, 166, 146, C('#d8cbbb'))
    for x in range(8, 164, 12): d.line([x, 131, x, 145], fill=mul(C('#d8cbbb'), 0.85))
    for x in range(24, 150, 10): d.line([x, 100, x, 130], fill=C('#f6eee2'))
    d.line([20, 100, 150, 100], fill=OL)
    for (x, y) in [(30, 60), (62, 58), (106, 60), (140, 58)]: flower_dot(d, x, y, C('#f7b6cf'))
    return im

@prop('mural', 112, 12, shadow=(58, 7))
def mural():
    W, H = 120, 92
    im = new(W, H); d = ImageDraw.Draw(im)
    for x in (10, W - 16): box(d, x, H - 30, x + 6, H - 1, C('#8a5d3b'), hl=None)
    box(d, 0, 0, W - 1, H - 24, C('#f6eee2'))
    for yy in range(4, H - 28):
        t = (yy - 4) / (H - 32); d.line([4, yy, W - 5, yy], fill=mix(C('#ffd9c2'), C('#bcd9f0'), t))
    for (x, y) in [(14, 10), (W - 30, 14), (60, 50), (30, 46), (90, 44)]: d.point([(x, y), (x + 1, y), (x, y + 1)], fill=WHITE)
    cy = (H - 24) // 2
    for a in range(5):
        ang = a * 2 * math.pi / 5 - math.pi / 2
        blob(d, int(24 + math.cos(ang) * 7), int(cy + math.sin(ang) * 7), 5, C('#f2a9c4'))
    blob(d, 24, cy, 4, C('#ffd86b'))
    box(d, W // 2 - 12, cy - 13, W // 2 + 12, cy + 13, C('#a48ad0')); d.rectangle([W // 2 + 7, cy - 11, W // 2 + 10, cy + 11], fill=C('#f6eee2'))
    pts = [(W - 24 + math.cos(-math.pi / 2 + i * math.pi / 5) * (13 if i % 2 == 0 else 5.5), cy + math.sin(-math.pi / 2 + i * math.pi / 5) * (13 if i % 2 == 0 else 5.5)) for i in range(10)]
    d.polygon(pts, fill=C('#ffd86b'), outline=OL)
    return im

# ============================================================ DUNIA KENANGAN
@prop('lantern_post', 8, 6, shadow=(10, 4))
def lantern_post():
    im = new(26, 70); d = ImageDraw.Draw(im)
    box(d, 11, 18, 14, 69, C('#5a4a7a'), hl=None)
    d.ellipse([1, 0, 24, 26], fill=(255, 220, 140, 70))
    d.rounded_rectangle([6, 6, 19, 22], 4, fill=C('#ffd98a'), outline=OL); d.rectangle([9, 9, 11, 19], fill=WHITE)
    return im

@prop('lantern_off', 8, 6, shadow=(10, 4))
def lantern_off():
    im = new(26, 70); d = ImageDraw.Draw(im)
    box(d, 11, 18, 14, 69, C('#5a4a7a'), hl=None)
    d.rounded_rectangle([6, 6, 19, 22], 4, fill=C('#6a6488'), outline=OL)
    return im

@prop('crystal', 18, 8, shadow=(12, 4))
def crystal():
    im = new(30, 44); d = ImageDraw.Draw(im)
    for (x0, h, c) in [(4, 26, '#9fd8ff'), (12, 40, '#c8b6ff'), (20, 22, '#ffc8ea')]:
        d.polygon([(x0, 43), (x0 + 3, 43 - h), (x0 + 6, 43 - h - 4), (x0 + 9, 43 - h), (x0 + 10, 43)], fill=OL)
        d.polygon([(x0 + 1, 42), (x0 + 3, 44 - h), (x0 + 6, 42 - h - 2), (x0 + 8, 44 - h), (x0 + 9, 42)], fill=C(c))
        d.line([x0 + 4, 41, x0 + 5, 44 - h], fill=WHITE)
    return im

@prop('star_stone', 20, 10, shadow=(14, 5))
def star_stone():
    im = new(34, 60); d = ImageDraw.Draw(im)
    d.polygon([(4, 59), (7, 14), (17, 4), (27, 14), (30, 59)], fill=OL)
    d.polygon([(5, 58), (8, 15), (17, 6), (26, 15), (29, 58)], fill=C('#4b4f86'))
    d.polygon([(9, 50), (10, 18), (17, 10), (14, 50)], fill=C('#6267a6'))
    pts = [(17 + math.cos(-math.pi / 2 + i * math.pi / 5) * (7 if i % 2 == 0 else 3), 28 + math.sin(-math.pi / 2 + i * math.pi / 5) * (7 if i % 2 == 0 else 3)) for i in range(10)]
    d.polygon(pts, fill=C('#ffe28a'))
    return im

@prop('arch_flowers', 0, 0, shadow=None)
def arch_flowers():
    W, H = 120, 130
    im = new(W, H); d = ImageDraw.Draw(im)
    for x in (6, W - 16): box(d, x, 40, x + 10, H - 1, C('#f6eee2'))
    d.arc([6, 4, W - 6, 96], 180, 360, fill=OL, width=12); d.arc([8, 6, W - 8, 94], 180, 360, fill=C('#f6eee2'), width=8)
    rng = random.Random(4)
    for _ in range(40):
        a = rng.uniform(math.pi, 2 * math.pi); r = 52 + rng.uniform(-6, 6)
        x = W / 2 + math.cos(a) * r; y = 50 + math.sin(a) * 44
        blob(d, int(x), int(y), 3, C(rng.choice(['#f7b6cf', '#ffffff', '#c9b6ef', '#ffe28a'])), mul(C('#5c9e5c'), 1.0))
    for _ in range(20):
        x = rng.choice([rng.randint(2, 18), rng.randint(W - 20, W - 4)]); y = rng.randint(50, H - 10)
        blob(d, x, y, 3, C(rng.choice(['#f7b6cf', '#ffffff', '#5c9e5c'])), C('#4a8a50'))
    return im

@prop('wishing_tree', 30, 14, shadow=(60, 16))
def wishing_tree():
    W, H = 200, 220
    im = new(W, H); d = ImageDraw.Draw(im)
    _trunk(d, W // 2, H - 80, H - 1, '#6a4f80')
    d.polygon([(W // 2 - 16, H - 1), (W // 2 - 8, H - 70), (W // 2 + 8, H - 70), (W // 2 + 16, H - 1)], fill=C('#6a4f80'), outline=OL)
    pts = [(100, 80, 54), (56, 104, 38), (144, 104, 38), (74, 50, 36), (128, 52, 36), (100, 120, 40), (100, 34, 30)]
    _canopy(d, pts, C('#b6a6f0'))
    rng = random.Random(7)
    for _ in range(26):
        x = rng.randint(40, 160); y = rng.randint(20, 140)
        d.line([x, y - 6, x, y], fill=C('#fff1b8'))
        d.rectangle([x - 2, y, x + 2, y + 6], fill=C(rng.choice(['#ffd1ea', '#fff1b8', '#c8f0ff'])), outline=OL)
    for _ in range(18):
        x = rng.randint(30, 170); y = rng.randint(10, 150); d.point([(x, y), (x + 1, y)], fill=WHITE)
    return im

@prop('stone_bench', 60, 12, shadow=(34, 6))
def stone_bench():
    im = new(66, 28); d = ImageDraw.Draw(im)
    box(d, 1, 6, 64, 16, C('#d8d2e2')); box(d, 6, 16, 14, 27, C('#b9b2c6')); box(d, 51, 16, 59, 27, C('#b9b2c6'))
    return im

@prop('pedestal_book', 30, 12, shadow=(18, 5))
def pedestal_book():
    im = new(36, 54); d = ImageDraw.Draw(im)
    box(d, 10, 22, 25, 50, C('#d8d2e2')); box(d, 4, 46, 31, 53, C('#b9b2c6')); box(d, 3, 16, 32, 24, C('#b9b2c6'))
    d.polygon([(6, 16), (17, 6), (29, 16)], fill=C('#f6eee2'), outline=OL); d.line([17, 6, 17, 16], fill=OL)
    d.ellipse([10, 0, 24, 10], fill=(255, 230, 160, 120))
    return im

# ============================================================ INTERIOR
@prop('bed_blue', 76, 96, shadow=None)
def bed_blue(col='#7c91c4'):
    im = new(80, 112); d = ImageDraw.Draw(im)
    box(d, 0, 0, 79, 24, C('#9b6a4c')); d.rectangle([6, 5, 73, 10], fill=mul(C('#9b6a4c'), 1.15))
    box(d, 2, 20, 77, 106, C('#f6eee2'))
    box(d, 8, 24, 71, 42, WHITE); d.line([10, 38, 69, 38], fill=C('#e6ddd4'))
    box(d, 2, 48, 77, 104, C(col))
    d.rectangle([3, 49, 76, 56], fill=mul(C(col), 1.2))
    for y in range(62, 100, 10): d.line([6, y, 73, y], fill=mul(C(col), 0.85))
    for x in range(12, 72, 16):
        for y in range(66, 100, 20): flower_dot(d, x, y, mul(C(col), 1.35))
    box(d, 0, 104, 79, 111, C('#7b5238'))
    return im

@prop('bed_pink', 76, 96, shadow=None)
def bed_pink(): return bed_blue('#e9a3ba')

@prop('desk', 88, 26, shadow=None)
def desk(phone=True, laptop=True):
    im = new(92, 66); d = ImageDraw.Draw(im)
    box(d, 0, 18, 91, 30, C('#c99a66'))
    box(d, 2, 30, 89, 64, C('#b9814f'))
    box(d, 6, 34, 40, 60, mul(C('#b9814f'), 0.82))
    for i in range(2): box(d, 48, 34 + i * 13, 85, 45 + i * 13, C('#c58c57')); blob(d, 66, 39 + i * 13, 1, C('#ffd86b'))
    if laptop:
        d.polygon([(14, 18), (18, 2), (46, 2), (50, 18)], fill=OL); d.polygon([(16, 17), (19, 4), (45, 4), (48, 17)], fill=C('#9ec5ff'))
        box(d, 10, 16, 54, 20, C('#cfd6e4'))
    box(d, 60, 8, 74, 18, C('#f6eee2')); d.rectangle([62, 4, 72, 9], fill=C('#5c9e5c'), outline=OL)
    if phone: box(d, 78, 12, 88, 18, C('#3c3850')); d.rectangle([80, 13, 86, 16], fill=C('#bfe3f2'))
    return im

@prop('vanity', 72, 26, shadow=None)
def vanity():
    im = new(76, 80); d = ImageDraw.Draw(im)
    d.ellipse([18, 0, 58, 40], fill=OL); d.ellipse([20, 2, 56, 38], fill=C('#cfeefb'))
    d.line([28, 10, 40, 30], fill=WHITE, width=2)
    box(d, 0, 34, 75, 44, C('#f2d9e2')); box(d, 3, 44, 72, 78, C('#e9c3d0'))
    for i in range(2): box(d, 8 + i * 32, 50, 36 + i * 32, 70, mul(C('#e9c3d0'), 1.08)); blob(d, 22 + i * 32, 60, 1, C('#ffd86b'))
    for (x, c) in [(10, '#f7b6cf'), (18, '#c9b6ef'), (60, '#ffe28a')]: box(d, x, 26, x + 5, 34, C(c), hl=None)
    return im

@prop('bookshelf', 58, 24, shadow=None)
def bookshelf(seed=2):
    rng = random.Random(seed)
    im = new(62, 96); d = ImageDraw.Draw(im)
    box(d, 0, 0, 61, 95, C('#9b6a4c'))
    cols = ['#c9b6ef', '#f7b6cf', '#8fc9a8', '#ffd86b', '#9ec5ff', '#f6eee2', '#e98f8f']
    for r in range(4):
        y = 5 + r * 22
        d.rectangle([4, y, 57, y + 19], fill=mul(C('#9b6a4c'), 0.7))
        x = 6
        while x < 54:
            bw = rng.randint(3, 6); bh = rng.randint(13, 18)
            if rng.random() < 0.12: x += 4; continue
            box(d, x, y + 19 - bh, x + bw, y + 18, C(rng.choice(cols)), hl=None); x += bw + 1
        d.line([4, y + 19, 57, y + 19], fill=mul(C('#9b6a4c'), 1.2))
    return im

@prop('wardrobe', 60, 24, shadow=None)
def wardrobe():
    im = new(64, 104); d = ImageDraw.Draw(im)
    box(d, 0, 0, 63, 103, C('#b9814f')); box(d, 4, 6, 30, 96, C('#c99a66')); box(d, 33, 6, 59, 96, C('#c99a66'))
    blob(d, 27, 52, 2, C('#ffd86b')); blob(d, 36, 52, 2, C('#ffd86b'))
    return im

@prop('plant', 20, 10, shadow=(10, 3))
def plant(big=False):
    W, H = (40, 60) if big else (30, 46)
    im = new(W, H); d = ImageDraw.Draw(im)
    box(d, W // 2 - 9, H - 16, W // 2 + 9, H - 1, C('#d48464'))
    d.rectangle([W // 2 - 10, H - 17, W // 2 + 10, H - 13], fill=mul(C('#d48464'), 0.85), outline=OL)
    _canopy(d, [(W // 2, H - 26, 10), (W // 2 - 8, H - 32, 8), (W // 2 + 8, H - 33, 8), (W // 2, H - 40, 8)] + ([(W // 2, H - 50, 8)] if big else []), C('#5fa463'))
    return im

@prop('plant_big', 24, 10, shadow=(12, 4))
def plant_big(): return plant(True)

@prop('rug_round', 0, 0, shadow=None, layer='floor')
def rug_round(c1='#c9b6ef', c2='#f2e8fb'):
    im = new(170, 80); d = ImageDraw.Draw(im)
    d.ellipse([0, 0, 169, 79], fill=OL); d.ellipse([2, 2, 167, 77], fill=C(c1)); d.ellipse([14, 8, 155, 71], fill=C(c2))
    d.ellipse([34, 18, 135, 61], fill=C(c1)); d.ellipse([44, 24, 125, 55], fill=C(c2))
    for i in range(12):
        a = i / 12 * math.pi * 2; flower_dot(d, int(85 + math.cos(a) * 62), int(40 + math.sin(a) * 28), mul(C(c1), 0.8))
    return im

@prop('rug_pink', 0, 0, shadow=None, layer='floor')
def rug_pink(): return rug_round('#f2a9c4', '#fde7ef')

@prop('rug_rect', 0, 0, shadow=None, layer='floor')
def rug_rect():
    im = new(180, 90); d = ImageDraw.Draw(im)
    box(d, 0, 0, 179, 89, C('#9fb7d8'), hl=None); box(d, 8, 8, 171, 81, C('#e8eef8'), hl=None); box(d, 16, 16, 163, 73, C('#9fb7d8'), hl=None)
    for x in range(24, 160, 16): d.line([x, 24, x + 8, 66], fill=C('#e8eef8'))
    return im

@prop('sofa', 96, 22, shadow=None)
def sofa():
    im = new(100, 52); d = ImageDraw.Draw(im)
    box(d, 4, 2, 95, 30, C('#a48ad0')); box(d, 0, 18, 14, 50, C('#8f75bd')); box(d, 85, 18, 99, 50, C('#8f75bd'))
    box(d, 12, 26, 87, 46, C('#b8a0e0')); d.line([49, 27, 49, 45], fill=mul(C('#b8a0e0'), 0.8))
    box(d, 20, 10, 40, 26, C('#ffd1ea')); box(d, 62, 10, 82, 26, C('#fff1b8'))
    return im

@prop('floor_lamp', 10, 6, shadow=(10, 3))
def floor_lamp():
    im = new(30, 86); d = ImageDraw.Draw(im)
    box(d, 13, 22, 16, 80, C('#4e4a63'), hl=None); box(d, 7, 79, 23, 85, C('#4e4a63'))
    d.polygon([(4, 24), (26, 24), (21, 4), (9, 4)], fill=OL); d.polygon([(6, 23), (24, 23), (20, 5), (10, 5)], fill=C('#fff1d0'))
    return im

@prop('counter', 200, 40, shadow=None)
def counter():
    im = new(204, 72); d = ImageDraw.Draw(im)
    box(d, 0, 16, 203, 28, C('#e8d6c0'))
    box(d, 2, 28, 201, 70, C('#9b6a4c'))
    for x in range(8, 196, 32): box(d, x, 34, x + 26, 64, mul(C('#9b6a4c'), 1.12))
    box(d, 10, 0, 40, 20, C('#cfd6e4')); box(d, 14, 4, 36, 10, C('#4e4a63')); box(d, 22, 12, 28, 18, WHITE)
    for i, c in enumerate(['#f7b6cf', '#ffe28a', '#c9b6ef']): blob(d, 130 + i * 18, 10, 6, C(c)); d.line([124 + i * 18, 16, 136 + i * 18, 16], fill=C('#f6eee2'), width=2)
    box(d, 178, 4, 196, 20, C('#f6eee2')); text(d, (187, 12), '♥', C('#d4646f'), 9)
    return im

@prop('display_case', 70, 22, shadow=None)
def display_case():
    im = new(74, 56); d = ImageDraw.Draw(im)
    box(d, 0, 30, 73, 55, C('#9b6a4c'))
    d.rectangle([2, 4, 71, 31], fill=(210, 236, 248, 160), outline=OL)
    for i, (c, t) in enumerate([('#fde7ef', '#f2a9c4'), ('#fff1d6', '#c58c57'), ('#f2e8fb', '#a48ad0')]):
        x = 8 + i * 22; box(d, x, 18, x + 16, 29, C(c), hl=None); d.rectangle([x, 16, x + 16, 19], fill=C(t))
        d.point([(x + 8, 14)], fill=C('#d4646f'))
    return im

@prop('cafe_table', 56, 14, shadow=(30, 6))
def cafe_table():
    im = new(64, 50); d = ImageDraw.Draw(im)
    for x in (0, 50): box(d, x, 24, x + 13, 40, C('#c9b6ef')); box(d, x + 2, 40, x + 4, 49, C('#4e4a63'), hl=None); box(d, x + 9, 40, x + 11, 49, C('#4e4a63'), hl=None)
    d.ellipse([10, 4, 54, 24], fill=OL); d.ellipse([11, 5, 53, 22], fill=C('#f6eee2'))
    box(d, 30, 20, 34, 44, C('#4e4a63'), hl=None); box(d, 24, 44, 40, 48, C('#4e4a63'))
    d.ellipse([26, 8, 34, 14], fill=WHITE, outline=OL); blob(d, 40, 12, 2, C('#f7b6cf'))
    return im

@prop('symbol_table', 72, 20, shadow=None)
def symbol_table():
    im = new(76, 56); d = ImageDraw.Draw(im)
    box(d, 0, 0, 75, 24, C('#7a5f9a')); d.rectangle([3, 3, 72, 6], fill=C('#9b80bd'))
    for i, c in enumerate(['#f7b6cf', '#c9b6ef', '#ffe28a']):
        blob(d, 14 + i * 24, 13, 7, C('#f6eee2'))
    flower_dot(d, 14, 13, C('#f2a9c4')); box(d, 34, 8, 42, 18, C('#a48ad0'));
    pts = [(62 + math.cos(-math.pi / 2 + i * math.pi / 5) * (6 if i % 2 == 0 else 2.5), 13 + math.sin(-math.pi / 2 + i * math.pi / 5) * (6 if i % 2 == 0 else 2.5)) for i in range(10)]
    d.polygon(pts, fill=C('#ffd86b'))
    box(d, 6, 24, 69, 55, C('#9b6a4c')); box(d, 14, 30, 61, 50, mul(C('#9b6a4c'), 1.1))
    return im

@prop('flower_shelf', 110, 22, shadow=None)
def flower_shelf():
    rng = random.Random(5)
    im = new(114, 96); d = ImageDraw.Draw(im)
    box(d, 0, 0, 113, 95, C('#c99a66'))
    for r in range(3):
        y = 8 + r * 29
        d.rectangle([4, y, 109, y + 25], fill=mul(C('#c99a66'), 0.75))
        for k in range(5):
            x = 8 + k * 21
            box(d, x, y + 14, x + 14, y + 25, C(rng.choice(['#d48464', '#8fb3c9', '#f6eee2'])), hl=None)
            for j in range(3): flower_dot(d, x + 3 + j * 4, y + 8 + (j % 2) * 3, C(rng.choice(['#f7b6cf', '#ffe28a', '#ffffff', '#ff8fa3', '#c9b6ef'])))
            d.line([x + 7, y + 11, x + 7, y + 14], fill=C('#5c9e5c'))
    return im

@prop('flower_buckets', 70, 14, shadow=(36, 6))
def flower_buckets():
    rng = random.Random(8)
    im = new(76, 46); d = ImageDraw.Draw(im)
    for k in range(4):
        x = 2 + k * 18
        box(d, x, 26, x + 15, 45, C('#8fb3c9'))
        _canopy(d, [(x + 7, 18, 7)], C('#5c9e5c'))
        for j in range(5): flower_dot(d, x + 2 + rng.randint(0, 11), 12 + rng.randint(0, 10), C(rng.choice(['#f7b6cf', '#ffe28a', '#ffffff', '#ff8fa3', '#c9b6ef'])))
    return im

@prop('shop_counter', 120, 30, shadow=None)
def shop_counter():
    im = new(124, 58); d = ImageDraw.Draw(im)
    box(d, 0, 12, 123, 24, C('#f6eee2')); box(d, 2, 24, 121, 57, C('#b9814f'))
    for x in range(8, 116, 22): box(d, x, 30, x + 16, 52, mul(C('#b9814f'), 1.1))
    box(d, 8, 0, 28, 14, C('#cfd6e4')); box(d, 90, 2, 116, 14, C('#f2a9c4')); d.line([103, 2, 103, 14], fill=C('#ffffff'))
    return im

@prop('arcade_cabinet', 34, 14, shadow=None)
def arcade_cabinet(col='#e86a7e', seed=1):
    im = new(38, 80); d = ImageDraw.Draw(im)
    d.polygon([(2, 79), (2, 6), (8, 0), (35, 0), (35, 79)], fill=OL)
    d.polygon([(3, 78), (3, 7), (9, 1), (34, 1), (34, 78)], fill=C(col))
    box(d, 6, 4, 32, 12, C('#3c3850')); text(d, (19, 8), '★', C('#ffe28a'), 8)
    box(d, 6, 14, 32, 38, C('#1d2347'))
    rng = random.Random(seed)
    for _ in range(6): d.point([(rng.randint(8, 30), rng.randint(16, 36))], fill=C(rng.choice(['#ffe28a', '#9fd8ff', '#ffc8ea', '#8fd18c'])))
    d.polygon([(4, 42), (34, 42), (36, 50), (2, 50)], fill=mul(C(col), 0.8), outline=OL)
    blob(d, 12, 46, 2, C('#ffe28a')); blob(d, 22, 46, 2, C('#9fd8ff')); blob(d, 28, 45, 2, C('#ff8fa3'))
    box(d, 10, 56, 28, 70, mul(C(col), 0.85))
    return im

prop('arcade_blue', 34, 14)(lambda: arcade_cabinet('#5f8fd8', 2))
prop('arcade_green', 34, 14)(lambda: arcade_cabinet('#5fb88a', 3))
REG['arcade_pink'] = dict(fn=lambda: arcade_cabinet('#e86a7e', 1), cw=34, ch=14, shadow=None, layer='sort')

@prop('claw_machine', 44, 16, shadow=None)
def claw_machine():
    im = new(48, 92); d = ImageDraw.Draw(im)
    box(d, 0, 0, 47, 14, C('#f2a9c4')); text(d, (24, 7), 'CAPIT', C('#ffffff'), 8)
    d.rectangle([2, 14, 45, 58], fill=(210, 236, 248, 150), outline=OL)
    d.line([24, 16, 24, 28], fill=OL); d.line([19, 32, 24, 28, 29, 32], fill=OL)
    for (x, c) in [(10, '#ffd1ea'), (20, '#fff1b8'), (31, '#c8f0ff'), (39, '#c9b6ef')]: blob(d, x, 52, 4, C(c))
    box(d, 0, 58, 47, 91, C('#e86a7e')); box(d, 6, 64, 22, 74, C('#3c3850')); blob(d, 34, 68, 4, C('#ffe28a')); box(d, 10, 80, 38, 86, C('#3c3850'))
    return im

@prop('photobooth', 70, 20, shadow=None)
def photobooth():
    im = new(74, 112); d = ImageDraw.Draw(im)
    box(d, 0, 0, 73, 111, C('#a48ad0')); box(d, 2, 2, 71, 18, C('#ffd1ea')); text(d, (37, 10), 'FOTO ♥', C('#7a3b5a'), 9)
    d.rectangle([8, 24, 66, 106], fill=C('#e86a7e'), outline=OL)
    for x in range(12, 64, 6): d.line([x, 25, x + 1, 105], fill=mul(C('#e86a7e'), 0.85))
    d.rectangle([8, 24, 30, 106], fill=C('#d4646f'), outline=OL)
    for (x, y) in [(52, 40), (58, 70), (46, 92)]: text(d, (x, y), '♥', C('#ffffff'), 8)
    return im

@prop('prize_shelf', 90, 20, shadow=None)
def prize_shelf():
    im = new(94, 80); d = ImageDraw.Draw(im)
    box(d, 0, 0, 93, 79, C('#9b6a4c'))
    rng = random.Random(11)
    for r in range(3):
        y = 6 + r * 24; d.rectangle([4, y, 89, y + 20], fill=mul(C('#9b6a4c'), 0.72))
        for k in range(5): blob(d, 13 + k * 17, y + 12, 6, C(rng.choice(['#ffd1ea', '#fff1b8', '#c8f0ff', '#c9b6ef', '#8fd18c'])))
    return im

@prop('stove', 56, 22, shadow=None)
def stove():
    im = new(60, 62); d = ImageDraw.Draw(im)
    box(d, 0, 10, 59, 61, C('#e6e0ea')); box(d, 0, 0, 59, 12, C('#cfc8d6'))
    for (x, y) in [(14, 6), (44, 6)]: d.ellipse([x - 9, y - 4, x + 9, y + 4], fill=C('#4e4a63'), outline=OL)
    box(d, 6, 22, 53, 52, C('#3c3850')); d.rectangle([10, 26, 49, 48], fill=C('#5a5470'))
    for x in (12, 24, 36, 48): blob(d, x, 16, 2, C('#ff8fa3'))
    box(d, 34, -2, 52, 6, C('#d4646f'))
    return im

@prop('fridge', 40, 20, shadow=None)
def fridge():
    im = new(44, 100); d = ImageDraw.Draw(im)
    box(d, 0, 0, 43, 99, C('#cfe9f5')); d.line([1, 38, 42, 38], fill=OL)
    box(d, 34, 12, 37, 30, C('#9fb7d8'), hl=None); box(d, 34, 46, 37, 70, C('#9fb7d8'), hl=None)
    for (x, y, c) in [(8, 8, '#f7b6cf'), (16, 14, '#ffe28a'), (10, 50, '#c9b6ef')]: box(d, x, y, x + 7, y + 7, C(c), hl=None)
    return im

@prop('kitchen_counter', 130, 22, shadow=None)
def kitchen_counter():
    im = new(134, 62); d = ImageDraw.Draw(im)
    box(d, 0, 10, 133, 22, C('#f3ece4')); box(d, 2, 22, 131, 61, C('#9fc9b6'))
    for x in range(6, 126, 32): box(d, x, 28, x + 26, 56, mul(C('#9fc9b6'), 1.08)); blob(d, x + 13, 32, 1, C('#4e4a63'))
    box(d, 70, 12, 110, 20, C('#cfd6e4')); d.line([90, 0, 90, 12], fill=C('#9fb7d8'), width=3)
    box(d, 8, 2, 26, 12, C('#c58c57')); box(d, 32, 4, 44, 12, C('#f2a9c4'))
    return im

@prop('kitchen_table', 90, 24, shadow=(48, 8))
def kitchen_table():
    im = new(96, 60); d = ImageDraw.Draw(im)
    for x in (0, 80): box(d, x, 26, x + 15, 48, C('#c9b6ef'))
    box(d, 8, 10, 87, 26, C('#c99a66')); d.rectangle([10, 12, 85, 14], fill=C('#ead0a4'))
    for x in (12, 80): box(d, x, 26, x + 4, 56, C('#9b6a4c'), hl=None)
    box(d, 30, 4, 64, 12, C('#f6eee2')); d.ellipse([36, 0, 58, 8], fill=C('#f2a9c4'), outline=OL)
    return im

@prop('spice_shelf', 0, 0, shadow=None)
def spice_shelf():
    im = new(80, 34); d = ImageDraw.Draw(im)
    box(d, 0, 26, 79, 31, C('#9b6a4c'))
    for k in range(8): box(d, 4 + k * 9, 12 + (k % 2) * 4, 10 + k * 9, 26, C(['#e98f8f', '#ffd86b', '#8fc9a8', '#c9b6ef'][k % 4]), hl=None)
    return im

@prop('door', 0, 0, shadow=None)
def door_int():
    im = new(56, 90); d = ImageDraw.Draw(im)
    box(d, 0, 0, 55, 89, C('#7b5238')); box(d, 5, 5, 50, 89, C('#a8723f'))
    box(d, 10, 12, 45, 38, C('#bf8752')); box(d, 10, 46, 45, 80, C('#bf8752'))
    blob(d, 42, 48, 3, C('#ffd86b'))
    d.rectangle([-1, 86, 56, 89], fill=OL)
    return im

@prop('wall_clock', 0, 0, shadow=None)
def wall_clock():
    im = new(30, 30); d = ImageDraw.Draw(im)
    d.ellipse([1, 1, 28, 28], fill=C('#f6eee2'), outline=OL, width=2); d.line([15, 15, 15, 7], fill=OL, width=2); d.line([15, 15, 21, 17], fill=OL, width=2)
    return im

@prop('frame_photo', 0, 0, shadow=None)
def frame_photo():
    im = new(40, 32); d = ImageDraw.Draw(im)
    box(d, 0, 0, 39, 31, C('#c58c57')); d.rectangle([4, 4, 35, 27], fill=C('#cfe9f5'))
    d.polygon([(4, 27), (14, 14), (22, 22), (28, 16), (35, 27)], fill=C('#8fc9a8')); blob(d, 28, 9, 3, C('#ffe28a'))
    return im

@prop('poster', 0, 0, shadow=None)
def poster():
    im = new(36, 48); d = ImageDraw.Draw(im)
    box(d, 0, 0, 35, 47, C('#fff1d6')); d.rectangle([4, 4, 31, 30], fill=C('#c9b6ef'))
    pts = [(18 + math.cos(-math.pi / 2 + i * math.pi / 5) * (9 if i % 2 == 0 else 4), 17 + math.sin(-math.pi / 2 + i * math.pi / 5) * (9 if i % 2 == 0 else 4)) for i in range(10)]
    d.polygon(pts, fill=C('#ffe28a')); d.line([6, 36, 29, 36], fill=C('#a48ad0')); d.line([6, 41, 22, 41], fill=C('#a48ad0'))
    return im

@prop('tv', 70, 18, shadow=None)
def tv():
    im = new(74, 62); d = ImageDraw.Draw(im)
    box(d, 0, 30, 73, 61, C('#b9814f')); box(d, 6, 36, 34, 56, mul(C('#b9814f'), 1.1)); box(d, 40, 36, 68, 56, mul(C('#b9814f'), 1.1))
    box(d, 10, 0, 63, 30, C('#3c3850')); d.rectangle([13, 3, 60, 26], fill=C('#5a78b0')); d.line([16, 22, 30, 8], fill=C('#9ec5ff'))
    return im

@prop('picnic_blanket', 0, 0, shadow=None, layer='floor')
def picnic_blanket():
    im = new(110, 64); d = ImageDraw.Draw(im)
    d.polygon([(10, 0), (109, 6), (100, 63), (0, 56)], fill=OL)
    d.polygon([(11, 2), (107, 8), (98, 61), (2, 54)], fill=C('#f6eee2'))
    for i in range(1, 6): d.line([11 + i * 16, 2 + i, 2 + i * 16, 54 + i], fill=C('#e98f8f'), width=4)
    for j in range(1, 4): d.line([2 + j * 2, 2 + j * 13, 107 - j * 2, 8 + j * 13], fill=C('#e98f8f'), width=4)
    box(d, 40, 20, 66, 38, C('#c58c57')); d.arc([44, 12, 62, 30], 180, 360, fill=OL, width=2)
    return im

@prop('bridge', 0, 0, shadow=None, layer='floor')
def bridge(w=120, h=60):
    im = new(w, h); d = ImageDraw.Draw(im)
    box(d, 0, 6, w - 1, h - 7, C('#c99a66'), hl=None)
    for x in range(4, w - 4, 10): d.line([x, 7, x, h - 8], fill=mul(C('#c99a66'), 0.8))
    for y in (0, h - 7): box(d, 0, y, w - 1, y + 6, C('#9b6a4c'))
    for x in range(0, w, 30): box(d, x, 0, x + 5, 8, C('#7b5238'), hl=None); box(d, x, h - 9, x + 5, h - 1, C('#7b5238'), hl=None)
    return im

# ============================================================ v1.2: perpustakaan, arsip, dermaga, perumahan
def glow(im, bbox, col):
    layer = new(im.width, im.height); ImageDraw.Draw(layer).ellipse(bbox, fill=col); im.alpha_composite(layer)
@prop('tall_bookshelf', 92, 24, shadow=None)
def tall_bookshelf(seed=3, wood='#7b5238'):
    rng = random.Random(seed)
    im = new(96, 132); d = ImageDraw.Draw(im)
    box(d, 0, 0, 95, 131, C(wood)); box(d, 0, 0, 95, 8, mul(C(wood), 1.15))
    cols = ['#c9b6ef', '#f7b6cf', '#8fc9a8', '#ffd86b', '#9ec5ff', '#f6eee2', '#e98f8f', '#b07a6a', '#6f86c2']
    for r in range(5):
        y = 11 + r * 24
        d.rectangle([4, y, 91, y + 20], fill=mul(C(wood), 0.62))
        x = 6
        while x < 88:
            if rng.random() < 0.08: x += 5; continue
            if rng.random() < 0.06:  # buku miring
                d.polygon([(x, y + 20), (x + 4, y + 20), (x + 11, y + 6), (x + 7, y + 5)], fill=C(rng.choice(cols)), outline=OL); x += 12; continue
            bw = rng.randint(3, 6); bh = rng.randint(14, 19)
            box(d, x, y + 20 - bh, x + bw, y + 19, C(rng.choice(cols)), hl=None)
            if bw > 4: d.line([x + 1, y + 23 - bh, x + bw - 1, y + 23 - bh], fill=C('#ffe7a6'))
            x += bw + 1
        d.line([4, y + 20, 91, y + 20], fill=mul(C(wood), 1.25)); d.line([4, y + 21, 91, y + 21], fill=OL)
    return im

@prop('secret_shelf', 92, 24, shadow=None)
def secret_shelf(open_=False):
    im = tall_bookshelf(seed=17)
    if open_:
        d = ImageDraw.Draw(im)
        d.rectangle([20, 22, 75, 131], fill=OL); d.rectangle([22, 24, 73, 131], fill=C('#1d1a2e'))
        for k in range(10):
            d.point([(30 + (k * 13) % 40, 40 + (k * 17) % 80)], fill=C('#ffe7a6'))
        glow(im, [34, 60, 62, 88], (255, 220, 150, 60))
    return im

@prop('reading_table', 84, 16, shadow=(44, 7))
def reading_table(lamp=True, books=True):
    im = new(90, 52); d = ImageDraw.Draw(im)
    box(d, 2, 14, 87, 30, C('#a8723f')); d.line([3, 15, 86, 15], fill=C('#c99a66'))
    for x in (6, 78): box(d, x, 30, x + 6, 51, C('#7b5238'), hl=None)
    if books:
        box(d, 12, 6, 30, 15, C('#9ec5ff')); box(d, 14, 2, 30, 7, C('#f7b6cf')); box(d, 52, 9, 70, 15, C('#f6eee2'), hl=None); d.line([61, 9, 61, 15], fill=OL)
    if lamp:
        box(d, 75, 0, 85, 4, C('#8fc9a8')); d.line([80, 4, 80, 14], fill=OL, width=2); glow(im, [70, 3, 90, 13], (255, 230, 160, 70))
    return im

@prop('globe', 22, 10, shadow=(12, 4))
def globe():
    im = new(30, 50); d = ImageDraw.Draw(im)
    box(d, 12, 34, 17, 46, C('#7b5238'), hl=None); box(d, 6, 44, 23, 49, C('#7b5238'))
    blob(d, 15, 18, 12, C('#7fb3d9')); d.arc([2, 5, 28, 31], 200, 340, fill=C('#c99a66'), width=2)
    for (x, y, w, h) in [(8, 10, 8, 6), (17, 16, 6, 8), (10, 20, 5, 4)]: d.ellipse([x, y, x + w, y + h], fill=C('#8fc98a'))
    d.point([(10, 12), (11, 11)], fill=WHITE)
    return im

@prop('library_counter', 150, 22, shadow=None)
def library_counter():
    im = new(156, 60); d = ImageDraw.Draw(im)
    box(d, 0, 18, 155, 59, C('#9b6a4c')); box(d, 0, 12, 155, 20, C('#c99a66'))
    for x in range(10, 150, 36): box(d, x, 26, x + 28, 52, mul(C('#9b6a4c'), 1.1))
    box(d, 16, 2, 36, 12, C('#f6eee2')); box(d, 40, 4, 58, 12, C('#c9b6ef'))
    box(d, 120, 0, 130, 12, C('#8fc9a8')); glow(im, [110, -2, 140, 12], (255, 230, 160, 60))
    box(d, 70, 6, 92, 12, C('#ffd86b')); text(d, (81, 9), 'INFO', C('#3a2c40'), 6)
    return im

@prop('book_pile', 22, 8, shadow=(12, 4))
def book_pile(seed=1):
    rng = random.Random(seed); im = new(28, 30); d = ImageDraw.Draw(im)
    cols = ['#c9b6ef', '#f7b6cf', '#8fc9a8', '#ffd86b', '#9ec5ff', '#e98f8f']
    y = 26
    for k in range(rng.randint(3, 5)):
        w = rng.randint(16, 24); x = 2 + rng.randint(0, 26 - w - 2)
        box(d, x, y - 5, x + w, y, C(rng.choice(cols)), hl=None); y -= 5
    return im

@prop('candle', 8, 4, shadow=(6, 2))
def candle():
    im = new(14, 30); d = ImageDraw.Draw(im)
    box(d, 3, 24, 10, 29, C('#b9b2c6')); box(d, 5, 12, 8, 24, C('#f6eee2'), hl=None)
    d.ellipse([4, 4, 9, 12], fill=C('#ffd86b')); d.ellipse([5, 6, 8, 11], fill=WHITE); d.ellipse([0, 0, 13, 16], fill=(255, 220, 140, 50))
    return im

@prop('jar_shelf', 88, 20, shadow=None)
def jar_shelf(seed=5):
    rng = random.Random(seed); im = new(92, 110); d = ImageDraw.Draw(im)
    box(d, 0, 0, 91, 109, C('#4a3f5e'))
    glows = ['#ffe28a', '#f7b6cf', '#9ec5ff', '#c9b6ef', '#8fe0c0']
    for r in range(4):
        y = 8 + r * 25
        d.rectangle([4, y, 87, y + 21], fill=C('#2e2840'))
        for x in range(7, 84, 14):
            if rng.random() < 0.15: continue
            g = C(rng.choice(glows)); h = rng.randint(12, 17)
            glow(im, [x - 3, y + 21 - h - 3, x + 13, y + 21 + 3], g[:3] + (70,)); d = ImageDraw.Draw(im)
            box(d, x, y + 21 - h, x + 10, y + 20, (220, 235, 245, 255), hl=None)
            d.rectangle([x + 2, y + 23 - h, x + 8, y + 18], fill=g)
            box(d, x + 1, y + 19 - h, x + 9, y + 22 - h, C('#b07a6a'), hl=None)
        d.line([4, y + 21, 87, y + 21], fill=C('#6b5a80'))
    return im

@prop('archive_pedestal', 40, 14, shadow=(22, 6))
def archive_pedestal():
    im = new(48, 72); d = ImageDraw.Draw(im)
    glow(im, [0, 0, 47, 40], (255, 225, 160, 70))
    box(d, 14, 34, 33, 66, C('#8a7fa8')); box(d, 6, 62, 41, 71, C('#6b5a80')); box(d, 4, 26, 43, 35, C('#6b5a80'))
    d.polygon([(8, 26), (24, 14), (40, 26)], fill=C('#f6eee2'), outline=OL); d.line([24, 14, 24, 26], fill=OL)
    for k in range(5): d.point([(14 + k * 5, 8 + (k % 2) * 3)], fill=C('#ffe7a6'))
    return im

@prop('rowboat', 0, 0, shadow=None, layer='floor')
def rowboat(col='#c58c57'):
    im = new(84, 34); d = ImageDraw.Draw(im)
    d.polygon([(2, 12), (12, 3), (72, 3), (82, 12), (72, 31), (12, 31)], fill=OL)
    d.polygon([(4, 12), (13, 5), (71, 5), (79, 12), (71, 29), (13, 29)], fill=C(col))
    d.polygon([(10, 12), (16, 8), (68, 8), (74, 12), (68, 26), (16, 26)], fill=mul(C(col), 0.7))
    for x in (30, 52): box(d, x, 8, x + 6, 26, C('#a8723f'), hl=None)
    d.line([40, 16, 62, 30], fill=C('#7b5238'), width=2)
    return im

@prop('pier_post', 8, 6, shadow=None)
def pier_post():
    im = new(12, 30); d = ImageDraw.Draw(im)
    box(d, 2, 4, 9, 29, C('#7b5238'), hl=None); box(d, 1, 0, 10, 6, C('#9b6a4c'))
    d.line([2, 20, 9, 20], fill=C('#c9b6a0'))
    return im

@prop('fishing_hut', 120, 22, shadow=(66, 8))
def fishing_hut():
    im = new(130, 110); d = ImageDraw.Draw(im)
    d.polygon([(4, 40), (65, 4), (126, 40)], fill=OL); d.polygon([(8, 39), (65, 7), (122, 39)], fill=C('#5f7fa8'))
    for y in range(14, 40, 6): d.line([65 - (y - 4) * 1.6, y, 65 + (y - 4) * 1.6, y], fill=mul(C('#5f7fa8'), 0.85))
    box(d, 12, 40, 117, 106, C('#c99a66'))
    for y in range(46, 104, 7): d.line([13, y, 116, y], fill=mul(C('#c99a66'), 0.86))
    box(d, 54, 64, 76, 106, C('#7a5240')); blob(d, 72, 86, 1, C('#ffd86b'))
    box(d, 20, 54, 42, 74, C('#bfe3f2')); box(d, 88, 54, 110, 74, C('#bfe3f2'))
    d.line([24, 80, 40, 104], fill=C('#4e4a63'), width=2); d.arc([14, 76, 34, 96], 300, 60, fill=C('#e9f6fb'))
    box(d, 86, 30, 118, 40, C('#ffd86b')); text(d, (102, 35), 'SEWA', C('#3a2c40'), 7)
    return im

@prop('old_mailbox', 12, 6, shadow=(10, 4))
def old_mailbox():
    im = new(28, 50); d = ImageDraw.Draw(im)
    box(d, 11, 20, 16, 49, C('#7b5238'), hl=None)
    d.rounded_rectangle([1, 4, 26, 24], 6, fill=OL); d.rounded_rectangle([2, 5, 25, 23], 5, fill=C('#8fa88a'))
    d.line([5, 14, 22, 14], fill=mul(C('#8fa88a'), 0.75)); box(d, 22, 2, 25, 12, C('#d4646f'), hl=None)
    for k in range(4): d.point([(6 + k * 4, 19)], fill=C('#b07a6a'))
    return im

@prop('garden_plot', 70, 20, shadow=None)
def garden_plot(seed=2):
    rng = random.Random(seed); im = new(76, 40); d = ImageDraw.Draw(im)
    box(d, 0, 4, 75, 39, C('#9b6a4c')); d.rectangle([4, 8, 71, 35], fill=C('#6b4a33'))
    for y in (14, 22, 30): d.line([6, y, 69, y], fill=C('#5a3d2a'))
    for x in range(10, 68, 10):
        for y in (12, 20, 28):
            if rng.random() < 0.7:
                d.line([x, y, x, y - 4], fill=C('#5e9a50')); d.point([(x - 1, y - 3), (x + 1, y - 4)], fill=C('#89c571'))
                if rng.random() < 0.4: flower_dot(d, x, y - 5, C(rng.choice(['#f7b6cf', '#ffd86b', '#ffffff', '#c9b6ef'])))
    return im

@prop('hedge', 90, 14, shadow=(46, 6))
def hedge(w=96):
    im = new(w, 40); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 6, w - 1, 39], 10, fill=OL); d.rounded_rectangle([1, 7, w - 2, 38], 9, fill=C('#5e9a50'))
    for x in range(6, w - 6, 9): d.ellipse([x - 4, 8, x + 6, 18], fill=C('#74b262')); d.point([(x, 11)], fill=C('#9bd27c'))
    return im

@prop('puddle', 0, 0, shadow=None, layer='floor')
def puddle(w=60, h=20):
    im = new(w, h); d = ImageDraw.Draw(im)
    d.ellipse([0, 0, w - 1, h - 1], fill=(120, 150, 190, 150)); d.ellipse([4, 3, w - 12, h - 6], fill=(170, 200, 230, 120))
    d.line([w * 0.3, h * 0.35, w * 0.55, h * 0.35], fill=(240, 250, 255, 200))
    return im

@prop('telescope', 24, 10, shadow=(14, 4))
def telescope():
    im = new(40, 52); d = ImageDraw.Draw(im)
    for (x0, y0, x1, y1) in [(20, 30, 8, 51), (20, 30, 32, 51), (20, 30, 20, 51)]: d.line([x0, y0, x1, y1], fill=C('#4e4a63'), width=2)
    d.polygon([(4, 18), (30, 4), (35, 12), (9, 27)], fill=OL); d.polygon([(6, 18), (30, 6), (33, 12), (9, 25)], fill=C('#c9b6ef'))
    box(d, 29, 2, 37, 14, C('#ffd86b'))
    return im

# ============================================================ v1.3: eksplorasi hutan, gua, bukit
@prop('tree_oak', 22, 10, shadow=(44, 12))
def tree_oak(seed=4, base='#4f8f55'):
    rng = random.Random(seed); W, H = 136, 170
    im = new(W, H); d = ImageDraw.Draw(im); cx = W // 2
    d.polygon([(cx - 12, H - 1), (cx - 8, H - 60), (cx + 8, H - 60), (cx + 12, H - 1)], fill=OL)
    d.polygon([(cx - 11, H - 2), (cx - 7, H - 58), (cx + 7, H - 58), (cx + 11, H - 2)], fill=C('#6a4532'))
    for k in (-1, 1): d.line([cx + 9 * k, H - 3, cx + 20 * k, H - 1], fill=OL, width=3)
    d.line([cx + 3, H - 56, cx + 4, H - 6], fill=C('#57382a'))
    b = C(base)
    _canopy(d, [(cx, H - 100, 42), (cx - 36, H - 84, 30), (cx + 36, H - 84, 30), (cx - 18, H - 130, 30), (cx + 20, H - 128, 30), (cx, H - 74, 28), (cx - 48, H - 106, 22), (cx + 48, H - 104, 22)], b)
    for _ in range(26):
        x = rng.randint(cx - 50, cx + 50); y = rng.randint(H - 150, H - 70); d.point([(x, y), (x + 1, y)], fill=mul(b, 1.3))
    for _ in range(8):
        x = rng.randint(cx - 46, cx + 46); y = rng.randint(H - 140, H - 74); d.point([(x, y)], fill=mul(b, 0.7))
    return im

@prop('tree_dark', 14, 8, shadow=(30, 9))
def tree_dark(): return tree_oak(seed=9, base='#3f7a4a').resize((92, 115), Image.NEAREST)

@prop('bush_berry', 34, 10, shadow=(20, 6))
def bush_berry():
    im = bush(False); d = ImageDraw.Draw(im)
    for (x, y) in [(10, 14), (17, 19), (24, 11), (30, 17), (35, 20), (21, 23)]: blob(d, x, y, 1, C('#d4467a'), C('#8a2048'))
    return im

@prop('chest', 26, 10, shadow=(16, 5))
def chest(open_=False):
    im = new(34, 32); d = ImageDraw.Draw(im)
    box(d, 2, 14, 31, 31, C('#b07a44')); d.rectangle([2, 20, 31, 22], fill=C('#d9a441')); d.rectangle([3, 21, 30, 21], fill=C('#ffe28a'))
    for x in (6, 27): d.rectangle([x, 14, x + 1, 31], fill=C('#8a5a30'))
    if open_:
        d.polygon([(2, 14), (6, 2), (30, 2), (31, 14)], fill=OL); d.polygon([(4, 13), (7, 4), (29, 4), (29, 13)], fill=C('#6a4532'))
        d.rectangle([5, 12, 28, 15], fill=C('#2e2030'))
        for k in range(5): d.point([(10 + k * 4, 10 - (k % 2) * 3)], fill=C('#ffe28a'))
    else:
        d.rounded_rectangle([2, 4, 31, 16], 5, fill=OL); d.rounded_rectangle([3, 5, 30, 15], 4, fill=C('#c58c57'))
        d.line([4, 7, 29, 7], fill=C('#d9a466')); box(d, 14, 11, 19, 19, C('#ffd86b'))
    return im

@prop('cave_entrance', 0, 0, shadow=None)
def cave_entrance():
    im = new(110, 90); d = ImageDraw.Draw(im)
    d.polygon([(0, 89), (8, 30), (30, 6), (80, 4), (102, 26), (109, 89)], fill=OL)
    d.polygon([(2, 88), (10, 31), (31, 8), (79, 6), (100, 27), (107, 88)], fill=C('#8a7f78'))
    for (x0, y0, x1, y1) in [(14, 40, 40, 30), (70, 20, 96, 36), (20, 70, 44, 64)]: d.line([x0, y0, x1, y1], fill=C('#6e6460'))
    d.polygon([(26, 89), (30, 46), (44, 28), (66, 28), (80, 46), (84, 89)], fill=OL)
    d.polygon([(28, 89), (32, 47), (45, 30), (65, 30), (78, 47), (82, 89)], fill=C('#16121f'))
    for k in range(4): d.point([(40 + k * 9, 60 + (k % 2) * 8)], fill=C('#9fd8ff'))
    _canopy(d, [(20, 14, 10), (34, 8, 9), (88, 12, 10)], C('#5e9a50'))
    return im

@prop('observatory', 200, 40, shadow=(110, 12))
def observatory():
    W, H = 220, 210; im = new(W, H); d = ImageDraw.Draw(im)
    box(d, 20, 96, 199, 209, C('#e9e2f6')); 
    for y in range(102, 206, 8): d.line([21, y, 198, y], fill=C('#d8cfe8'))
    d.pieslice([30, 10, 190, 170], 180, 360, fill=OL); d.pieslice([32, 12, 188, 168], 180, 360, fill=C('#6f86c2'))
    for x in range(48, 180, 18): d.line([x, 90, 110 + (x - 110) * 0.3, 16], fill=C('#5a6fa8'))
    d.polygon([(100, 12), (122, 12), (124, 90), (98, 90)], fill=C('#2e2c5a'))
    d.line([111, 30, 150, 4], fill=C('#c9b6ef'), width=6); d.line([111, 30, 150, 4], fill=OL, width=1)
    box(d, 16, 88, 203, 98, C('#8a7fa8'))
    box(d, 92, 150, 128, 209, C('#7a5240')); blob(d, 122, 182, 2, C('#ffd86b'))
    for x in (44, 160): box(d, x, 122, x + 24, 150, C('#2e2c5a')); d.point([(x + 6, 128), (x + 16, 136), (x + 10, 142)], fill=C('#ffe7a6'))
    box(d, 70, 104, 150, 118, C('#ffd86b')); text(d, (110, 111), 'OBSERVATORIUM', C('#3a2c40'), 8)
    return im

@prop('stone_lantern', 18, 8, shadow=(12, 4))
def stone_lantern(lit=True):
    im = new(28, 56); d = ImageDraw.Draw(im)
    box(d, 6, 46, 21, 55, C('#9a948e')); box(d, 10, 30, 17, 46, C('#aaa39c'))
    box(d, 4, 16, 23, 30, C('#aaa39c')); d.rectangle([9, 19, 18, 27], fill=C('#ffe28a') if lit else C('#3a3440'))
    d.polygon([(1, 16), (14, 4), (26, 16)], fill=OL); d.polygon([(3, 15), (14, 6), (24, 15)], fill=C('#8a837c'))
    if lit: d.point([(13, 22), (14, 21)], fill=WHITE)
    return im

@prop('bridge_broken', 0, 0, shadow=None, layer='floor')
def bridge_broken(w=120, h=60):
    im = bridge(w, h); d = ImageDraw.Draw(im)
    d.rectangle([w // 2 - 20, 6, w // 2 + 22, h - 7], fill=(0, 0, 0, 0))
    for x in (w // 2 - 22, w // 2 + 20): d.line([x, 8, x + 3, h - 9], fill=C('#7b5238'), width=2)
    return im

@prop('carving', 22, 8, shadow=(14, 4))
def carving(sym='moon'):
    im = new(34, 44); d = ImageDraw.Draw(im)
    d.polygon([(3, 43), (2, 12), (10, 2), (24, 2), (32, 12), (31, 43)], fill=OL)
    d.polygon([(4, 42), (4, 13), (11, 4), (23, 4), (30, 13), (30, 42)], fill=C('#a7a3b4'))
    c = C('#6a6680')
    if sym == 'moon': d.ellipse([10, 12, 24, 26], fill=c); d.ellipse([14, 10, 27, 24], fill=C('#a7a3b4'))
    elif sym == 'star': d.polygon([(17, 10), (20, 18), (28, 18), (22, 23), (24, 31), (17, 26), (10, 31), (12, 23), (6, 18), (14, 18)], fill=c)
    elif sym == 'flower': [d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=c) for x, y in ((17, 13), (12, 19), (22, 19), (14, 26), (20, 26))]
    else: box(d, 10, 12, 24, 30, c, hl=None); d.line([17, 12, 17, 30], fill=C('#a7a3b4'))
    for k, y in enumerate((34, 38)): d.line([8 + k * 3, y, 26 - k * 2, y], fill=c)
    return im

@prop('mushroom_ring', 0, 0, shadow=None, layer='floor')
def mushroom_ring(r=46):
    W = r * 2 + 16; im = new(W, int(r * 1.3) + 16); d = ImageDraw.Draw(im)
    cx, cy = W // 2, im.height // 2
    for k in range(14):
        a = k / 14 * 2 * math.pi; x = cx + math.cos(a) * r; y = cy + math.sin(a) * r * 0.6
        d.rectangle([x - 1, y - 2, x + 1, y + 2], fill=C('#f6eee2'))
        d.pieslice([x - 5, y - 7, x + 5, y + 1], 180, 360, fill=C('#e05a6a') if k % 2 else C('#f0a040'), outline=OL)
        d.point([(x - 2, y - 5), (x + 2, y - 4)], fill=WHITE)
    return im

@prop('campfire', 22, 8, shadow=None)
def campfire():
    im = new(36, 34); d = ImageDraw.Draw(im)
    for k in range(7):
        a = k / 7 * 2 * math.pi; blob(d, 18 + math.cos(a) * 13, 26 + math.sin(a) * 6, 3, C('#8a837c'))
    d.line([8, 28, 28, 22], fill=C('#6a4532'), width=4); d.line([8, 22, 28, 28], fill=C('#7b5238'), width=4)
    d.polygon([(10, 25), (14, 10), (18, 16), (22, 4), (26, 25)], fill=C('#f08a3a')); d.polygon([(14, 25), (18, 14), (22, 25)], fill=C('#ffe28a'))
    glow(im, [0, 0, 36, 34], (255, 180, 90, 50))
    return im

@prop('tent', 76, 16, shadow=(44, 8))
def tent():
    im = new(84, 62); d = ImageDraw.Draw(im)
    d.polygon([(2, 61), (42, 4), (82, 61)], fill=OL); d.polygon([(5, 60), (42, 7), (79, 60)], fill=C('#e3954f'))
    d.polygon([(42, 7), (79, 60), (60, 60)], fill=C('#c97a3a')); d.polygon([(34, 60), (42, 26), (50, 60)], fill=C('#5a3a2a'))
    d.line([42, 0, 42, 7], fill=OL, width=2); d.polygon([(42, 0), (52, 3), (42, 6)], fill=C('#f7b6cf'))
    return im

@prop('log_bench', 56, 10, shadow=(30, 5))
def log_bench():
    im = new(62, 22); d = ImageDraw.Draw(im)
    d.rounded_rectangle([1, 4, 60, 18], 6, fill=OL); d.rounded_rectangle([2, 5, 59, 17], 5, fill=C('#9b6a4c'))
    d.ellipse([52, 5, 60, 17], fill=C('#d9b98a'), outline=OL); d.ellipse([54, 8, 58, 14], outline=C('#a0714f'))
    d.line([6, 8, 48, 8], fill=C('#b9814f'))
    return im

@prop('stalagmite', 18, 8, shadow=(12, 4))
def stalagmite(seed=1):
    rng = random.Random(seed); im = new(30, 52); d = ImageDraw.Draw(im)
    for (x0, h) in [(2, rng.randint(24, 34)), (10, rng.randint(36, 50)), (19, rng.randint(20, 30))]:
        d.polygon([(x0, 51), (x0 + 5, 51 - h), (x0 + 10, 51)], fill=OL); d.polygon([(x0 + 1, 50), (x0 + 5, 53 - h), (x0 + 9, 50)], fill=C('#5d5878'))
        d.line([x0 + 4, 48, x0 + 5, 54 - h], fill=C('#7d7898'))
    return im

@prop('crystal_big', 34, 12, shadow=(22, 6))
def crystal_big():
    im = new(50, 76); d = ImageDraw.Draw(im)
    glow(im, [0, 4, 50, 76], (150, 210, 255, 60)); d = ImageDraw.Draw(im)
    for (x0, h, c) in [(4, 40, '#9fd8ff'), (14, 70, '#c8b6ff'), (28, 52, '#9fd8ff'), (36, 30, '#ffc8ea')]:
        d.polygon([(x0, 75), (x0 + 4, 75 - h), (x0 + 8, 75 - h - 6), (x0 + 12, 75 - h), (x0 + 13, 75)], fill=OL)
        d.polygon([(x0 + 1, 74), (x0 + 4, 76 - h), (x0 + 8, 74 - h - 4), (x0 + 11, 76 - h), (x0 + 12, 74)], fill=C(c))
        d.line([x0 + 5, 72, x0 + 7, 76 - h], fill=WHITE)
    return im

@prop('waterfall', 0, 0, shadow=None, layer='floor')
def waterfall(w=60, h=110):
    im = new(w, h); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w - 1, h - 1], fill=C('#7fc0e0'))
    rng = random.Random(5)
    for k in range(40):
        x = rng.randint(2, w - 3); y = rng.randint(0, h - 12); d.line([x, y, x, y + rng.randint(6, 16)], fill=C('#d8f0fa'))
    d.ellipse([-8, h - 18, w + 8, h + 8], fill=C('#e9f6fb'))
    return im

def render(name, **kw):
    r = REG[name]; im = r['fn'](**kw) if kw else r['fn']()
    if isinstance(im, tuple): im = im[0]
    return im
