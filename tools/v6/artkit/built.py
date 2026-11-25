"""HD man-made sprites in the same light/outline rules: cottages, shops, benches, lamps, fences,
bridges, gazebo, signposts, bins, stalls, fountain, well, pier planks, boats."""
import numpy as np
from kit import (Sprite, quant, bayer, outline, noise, hexrgb, WOOD, STONE, METAL, PLASTER, BRICK,
                 ROOF_BLUE, ROOF_RED, ROOF_GREEN, LEAF, FLOWERS, WATER, BARK)

WIN_DAY = (hexrgb('#9cc7dd'), hexrgb('#d8eef6'), hexrgb('#5d8aa3'))


def _planks(sp, m, R, horizontal=True, board=12, seed=0):
    """Boards with one tone each, soft grain streaks along the board and dark seams."""
    rng = np.random.default_rng(seed)
    coord = sp.yy if horizontal else sp.xx
    along = sp.xx if horizontal else sp.yy
    idx = np.floor(coord / board).astype(int)
    tone = rng.uniform(-0.08, 0.08, idx.max() + 2)[np.clip(idx, 0, None)]
    grain = (np.sin(along * 0.21 + idx * 1.7) * np.sin(along * 0.053 + idx) > 0.55) * -0.07
    pos = (coord % board) / board
    shade = 0.58 + tone + grain + (pos < 0.25) * 0.08
    col = quant(shade, R)
    col[(coord % board) < 1.5] = R[1]
    sp.put(m, col)


def _window(sp, x, y, w, h, frame=WOOD, lit=False, box=True):
    sp.put(sp.rect(x - 3, y - 3, w + 6, h + 6), frame[2])
    glass = sp.rect(x, y, w, h)
    g = (sp.yy - y) / h
    col = np.where((g < 0.45)[..., None], WIN_DAY[1], WIN_DAY[0])
    if lit:
        col = np.where((g < 0.45)[..., None], hexrgb('#ffe7a6'), hexrgb('#f5c66b'))
    sp.put(glass, col)
    sp.put(sp.rect(x + w // 2 - 1, y, 3, h) | sp.rect(x, y + h // 2 - 1, w, 3), frame[3])
    sp.put(sp.rect(x - 5, y + h + 2, w + 10, 5), frame[4])          # sill
    if box:                                                        # flower box
        sp.put(sp.rect(x - 3, y + h + 7, w + 6, 8), frame[2])
        rng = np.random.default_rng(int(x * 7 + y))
        for i in range(int(w / 4)):
            fx = x - 2 + i * 4 + rng.integers(0, 2)
            sp.put(sp.ellipse(fx, y + h + 6, 2.5, 2.5), LEAF[3])
            if rng.random() < 0.6:
                sp.put(sp.ellipse(fx, y + h + 4, 1.8, 1.8), FLOWERS[i % 3][2])


def cottage(roof=ROOF_BLUE, wall=PLASTER, seed=1, w=360, h=330, door_col='#7a4a2c', chimney=True, sign=None):
    sp = Sprite(w, h)
    dith = bayer(h, w)
    wall_top, wall_bot = 175, h - 14
    x0, x1 = 28, w - 28
    # stone footing
    sp.put(sp.rect(x0 - 4, wall_bot - 16, x1 - x0 + 8, 18), quant(0.5 + (noise(h, w, 4, seed) - 0.5) * 0.5, STONE, dith))
    sp.put(sp.rect(x0 - 4, wall_bot - 16, x1 - x0 + 8, 2), STONE[5])
    # front wall: plaster with soft vertical gradient + timber frame
    wm = sp.rect(x0, wall_top, x1 - x0, wall_bot - 16 - wall_top)
    grad = 0.78 - (sp.yy - wall_top) / (wall_bot - wall_top) * 0.25 + (noise(h, w, 6, seed + 1) - 0.5) * 0.1
    sp.put(wm, quant(grad, wall, dith))
    for xx in (x0, x0 + (x1 - x0) // 2 - 4, x1 - 9):
        sp.put(sp.rect(xx, wall_top, 9, wall_bot - 16 - wall_top), WOOD[2])
        sp.put(sp.rect(xx, wall_top, 2, wall_bot - 16 - wall_top), WOOD[4])
    sp.put(sp.rect(x0, wall_top, x1 - x0, 9), WOOD[2])
    # under-eave shadow
    sp.put(sp.rect(x0, wall_top, x1 - x0, 16), sp.rgb * 0 + wall[1], 1)
    # door with small porch roof and step
    dx = w // 2 - 26
    sp.put(sp.rect(dx - 6, wall_bot - 92, 64, 78), WOOD[1])
    door = sp.rect(dx, wall_bot - 86, 52, 72)
    sp.put(door, quant(0.5 + ((sp.xx - dx) % 13 < 1.5) * -0.2 + (sp.yy - wall_bot) * 0, ramp_from(door_col), None))
    sp.put(sp.ellipse(dx + 42, wall_bot - 48, 3, 3), hexrgb('#e6c35a'))
    sp.put(sp.rect(dx - 14, wall_bot - 14, 80, 14), STONE[4])
    sp.put(sp.rect(dx - 14, wall_bot - 14, 80, 3), STONE[6])
    # windows
    for wx in (x0 + 30, x1 - 30 - 56):
        _window(sp, wx, wall_top + 52, 56, 50)
    # roof: gable front, tiles in rows, ridge, overhang
    r_top, r_bot = 18, wall_top + 20
    roof_m = sp.poly([(x0 - 22, r_bot), (x0 + 40, r_top), (x1 - 40, r_top), (x1 + 22, r_bot)])
    row = ((sp.yy - r_top) / 14).astype(int)
    tile = ((sp.xx + (row % 2) * 12) % 24) < 2
    v = (sp.yy - r_top) / (r_bot - r_top)
    shade = 0.82 - v * 0.38 + ((sp.yy - r_top) % 14 < 3) * 0.12 + (noise(h, w, 5, seed + 2) - 0.5) * 0.12
    col = quant(shade, roof, dith)
    col[tile] = roof[1]
    sp.put(roof_m, col)
    eave = sp.rect(x0 - 22, r_bot - 6, x1 - x0 + 44, 8) & roof_m
    sp.put(eave, roof[0])
    sp.put(sp.rect(x0 + 40, r_top, x1 - x0 - 80, 6), roof[-1])
    if chimney:
        cx = x1 - 90
        sp.put(sp.rect(cx, 0, 34, r_top + 34), quant(0.6 - (sp.xx - cx) / 34 * 0.4, BRICK, dith))
        sp.put(sp.rect(cx - 4, 0, 42, 8), BRICK[1])
    if sign:
        sp.put(sp.rect(w // 2 - 60, wall_top + 18, 120, 26), WOOD[1])
        sp.put(sp.rect(w // 2 - 56, wall_top + 21, 112, 20), hexrgb(sign))
    outline(sp, roof[0] * 0.7)
    return sp


def ramp_from(h):
    c = hexrgb(h)
    return np.array([c * 0.55, c * 0.72, c * 0.88, c, np.minimum(c * 1.15 + 10, 255)], np.float32)


def bench(seed=1, w=120, h=70):
    sp = Sprite(w, h)
    for lx in (14, w - 22):
        sp.put(sp.rect(lx, 34, 8, 30), METAL[2])
    sp.put(sp.rect(6, 8, w - 12, 22), WOOD[1])
    _planks(sp, sp.rect(8, 10, w - 16, 18), WOOD, True, 6, seed)
    sp.put(sp.rect(4, 34, w - 8, 16), WOOD[2])
    _planks(sp, sp.rect(4, 34, w - 8, 12), WOOD, True, 6, seed + 1)
    sp.put(sp.rect(4, 46, w - 8, 4), WOOD[0])
    outline(sp, WOOD[0] * 0.8)
    return sp


def lamp_post(w=44, h=176, lit=False):
    sp = Sprite(w, h)
    cx = w // 2
    sp.put(sp.rect(cx - 9, h - 14, 18, 12), METAL[2])
    sp.put(sp.rect(cx - 4, 46, 8, h - 58), quant(0.7 - (sp.xx - cx + 4) / 8 * 0.6, METAL))
    sp.put(sp.rect(cx - 14, 40, 28, 8), METAL[1])
    glass = sp.poly([(cx - 12, 40), (cx + 12, 40), (cx + 9, 14), (cx - 9, 14)])
    sp.put(glass, hexrgb('#ffe2a0') if lit else hexrgb('#f3e5c0'))
    sp.put(sp.rect(cx - 1, 14, 2, 26), METAL[2])
    sp.put(sp.poly([(cx - 16, 15), (cx + 16, 15), (cx, 2)]), METAL[3])
    outline(sp, METAL[0])
    return sp


def fence(length=192, vertical=False, seed=1):
    """Wooden rail fence; horizontal = runs left-right (front view), vertical = side view posts."""
    if not vertical:
        w, h = length, 60
        sp = Sprite(w, h)
        for x in range(6, w - 4, 32):
            sp.put(sp.rect(x, 8, 10, 46), quant(0.75 - (sp.xx - x) / 10 * 0.5, WOOD))
            sp.put(sp.rect(x, 6, 10, 4), WOOD[5])
        for y in (18, 34):
            sp.put(sp.rect(0, y, w, 8), WOOD[3])
            sp.put(sp.rect(0, y, w, 2), WOOD[5])
            sp.put(sp.rect(0, y + 6, w, 2), WOOD[1])
    else:
        w, h = 24, length
        sp = Sprite(w, h)
        sp.put(sp.rect(8, 0, 8, h), WOOD[3])
        sp.put(sp.rect(8, 0, 2, h), WOOD[5])
        for y in range(4, h - 10, 32):
            sp.put(sp.rect(4, y, 16, 22), quant(0.8 - (sp.xx - 4) / 16 * 0.6, WOOD))
            sp.put(sp.rect(4, y, 16, 3), WOOD[5])
    outline(sp, WOOD[0] * 0.8, width=1)
    return sp


def bridge(span=200, width=96, vertical=False, seed=1):
    """Plank bridge. vertical=False crosses a vertical stream (deck runs left-right)."""
    if vertical:
        w, h = width + 24, span
    else:
        w, h = span, width + 30
    sp = Sprite(w, h)
    if not vertical:
        deck = sp.rect(0, 22, w, width)
        _planks(sp, deck, WOOD, horizontal=False, board=14, seed=seed)
        sp.put(sp.rect(0, 22 + width, w, 8), WOOD[0])              # deck side
        for y in (10, 22 + width - 12):
            sp.put(sp.rect(0, y, w, 7), WOOD[4]); sp.put(sp.rect(0, y + 5, w, 2), WOOD[2])
            for x in range(4, w, 40):
                sp.put(sp.rect(x, y - 6, 8, 18), WOOD[2])
    else:
        deck = sp.rect(12, 0, width, h)
        _planks(sp, deck, WOOD, horizontal=True, board=14, seed=seed)
        for x in (4, 12 + width - 2):
            sp.put(sp.rect(x, 0, 8, h), WOOD[4]); sp.put(sp.rect(x + 5, 0, 2, h), WOOD[2])
            for y in range(4, h, 40):
                sp.put(sp.rect(x - 2, y, 12, 10), WOOD[2])
    outline(sp, WOOD[0] * 0.8, width=1)
    return sp


def signpost(text_col='#f3e2c0', w=70, h=100):
    sp = Sprite(w, h)
    sp.put(sp.rect(w // 2 - 4, 30, 8, h - 32), quant(0.7 - (sp.xx - w // 2 + 4) / 8 * 0.5, WOOD))
    board = sp.poly([(6, 12), (w - 16, 12), (w - 4, 24), (w - 16, 36), (6, 36)])
    sp.put(board, WOOD[4])
    sp.put(sp.rect(12, 20, w - 34, 3) | sp.rect(12, 27, w - 44, 3), WOOD[1])
    outline(sp, WOOD[0] * 0.8)
    return sp


def trash_bin(w=40, h=54):
    sp = Sprite(w, h)
    body = sp.rect(6, 12, w - 12, h - 14)
    sp.put(body, quant(0.75 - (sp.xx - 6) / (w - 12) * 0.55 + ((sp.xx % 7) < 1) * -0.1, ROOF_GREEN))
    sp.put(sp.rect(3, 6, w - 6, 8), ROOF_GREEN[1])
    outline(sp, ROOF_GREEN[0])
    return sp


def gazebo(w=340, h=320, roof=ROOF_RED):
    sp = Sprite(w, h)
    dith = bayer(h, w)
    floor = sp.ellipse(w / 2, h - 46, w * 0.46, 40)
    _planks(sp, floor, WOOD, True, 10)
    sp.put(sp.ellipse(w / 2, h - 40, w * 0.46, 40) & ~floor, WOOD[1])
    for px in (34, w / 2 - 8, w - 50):
        sp.put(sp.rect(px, 150, 16, h - 200), quant(0.8 - (sp.xx - px) / 16 * 0.6, PLASTER))
    rail = sp.rect(20, h - 110, w - 40, 8) | sp.rect(20, h - 86, w - 40, 6)
    sp.put(rail, PLASTER[4])
    roof_m = sp.poly([(w / 2, 10), (w - 6, 150), (6, 150)])
    v = (sp.yy - 10) / 140
    stripes = (np.abs(((sp.xx - w / 2) / np.maximum(1, sp.yy - 8)) * 6) % 1) < 0.08
    col = quant(0.85 - v * 0.35 - (sp.xx - w / 2) / w * 0.25, roof, dith)
    col[stripes] = roof[1]
    sp.put(roof_m, col)
    sp.put(sp.rect(6, 146, w - 12, 10), roof[0])
    sp.put(sp.ellipse(w / 2, 10, 8, 8), hexrgb('#e8c45c'))
    outline(sp, roof[0] * 0.7)
    return sp


def picnic_blanket(w=120, h=80):
    sp = Sprite(w, h)
    m = sp.poly([(8, 14), (w - 4, 6), (w - 10, h - 8), (2, h - 4)])
    check = ((sp.xx // 12 + sp.yy // 12) % 2 == 0)
    sp.put(m, np.where(check[..., None], hexrgb('#e7d9c8'), hexrgb('#d7605f')))
    sp.put(sp.rect(56, 24, 26, 18), WOOD[3])                      # basket
    sp.put(sp.rect(56, 22, 26, 4), WOOD[5])
    return sp


def lily_pad(seed=1, w=40, h=26):
    sp = Sprite(w, h)
    m = sp.ellipse(w / 2, h / 2, w / 2 - 2, h / 2 - 2)
    notch = (np.abs(np.arctan2(sp.yy - h / 2, sp.xx - w / 2) + 0.4) < 0.25)
    sp.put(m & ~notch, quant(0.6 + (sp.xx - w / 2) / w * -0.4, LEAF))
    if seed % 3 == 0:
        sp.put(sp.ellipse(w / 2 + 4, h / 2 - 2, 4, 3), FLOWERS[0][3])
    return sp


def rowboat(w=150, h=70):
    sp = Sprite(w, h)
    hull = sp.ellipse(w / 2, h / 2, w / 2 - 4, h / 2 - 6)
    sp.put(hull, WOOD[1])
    inner = sp.ellipse(w / 2, h / 2 - 3, w / 2 - 14, h / 2 - 14)
    _planks(sp, inner, WOOD, False, 12)
    sp.put(sp.rect(w // 2 - 4, 10, 8, h - 22), WOOD[2])
    outline(sp, WOOD[0])
    return sp


def fountain(w=240, h=200):
    sp = Sprite(w, h)
    dith = bayer(h, w)
    basin = sp.ellipse(w / 2, h - 50, w / 2 - 6, 46)
    sp.put(basin, quant(0.6 + (sp.xx - w / 2) / w * -0.4, STONE, dith))
    water = sp.ellipse(w / 2, h - 54, w / 2 - 22, 34)
    sp.put(water, quant(0.55 + (sp.yy - (h - 54)) / 80, WATER, dith))
    sp.put(sp.rect(w // 2 - 14, 60, 28, h - 110), quant(0.8 - (sp.xx - w / 2 + 14) / 28 * 0.6, STONE))
    sp.put(sp.ellipse(w / 2, 62, 46, 16), STONE[4])
    sp.put(sp.ellipse(w / 2, 60, 38, 11), WATER[4])
    sp.put(sp.ellipse(w / 2, 40, 10, 22), WATER[6])
    outline(sp, STONE[0])
    return sp


def market_stall(awning=('#d7605f', '#f1e6d3'), w=220, h=200):
    sp = Sprite(w, h)
    sp.put(sp.rect(14, 70, 8, h - 76) | sp.rect(w - 22, 70, 8, h - 76), WOOD[2])
    counter = sp.rect(10, h - 64, w - 20, 50)
    _planks(sp, counter, WOOD, False, 16)
    sp.put(sp.rect(10, h - 68, w - 20, 8), WOOD[4])
    rng = np.random.default_rng(5)
    for i in range(14):                                          # goods on the counter
        x = 24 + i * 13
        sp.put(sp.ellipse(x, h - 74, 6, 6), FLOWERS[i % 5][2])
    a0, a1 = hexrgb(awning[0]), hexrgb(awning[1])
    aw = sp.poly([(0, 70), (w, 70), (w - 16, 12), (16, 12)])
    stripe = ((sp.xx // 24) % 2 == 0)
    col = np.where(stripe[..., None], a0, a1) * (0.8 + 0.2 * (1 - (sp.yy - 12) / 58))[..., None]
    sp.put(aw, col)
    for x in range(0, w, 24):
        sp.put(sp.ellipse(x + 12, 72, 12, 7) & (sp.yy >= 70), a0 if (x // 24) % 2 == 0 else a1)
    outline(sp, WOOD[0] * 0.8)
    return sp


def well(w=130, h=170):
    sp = Sprite(w, h)
    ring = sp.ellipse(w / 2, h - 40, w / 2 - 8, 34)
    sp.put(ring, quant(0.6 + (sp.xx - w / 2) / w * -0.5, STONE, bayer(h, w)))
    sp.put(sp.ellipse(w / 2, h - 48, w / 2 - 24, 20), hexrgb('#16212b'))
    for px in (14, w - 24):
        sp.put(sp.rect(px, 30, 10, h - 80), WOOD[2])
    roof = sp.poly([(w / 2, 6), (w - 2, 44), (2, 44)])
    sp.put(roof, quant(0.8 - (sp.yy - 6) / 40 * 0.4, ROOF_RED, bayer(h, w)))
    outline(sp, STONE[0])
    return sp


def flower_arch(w=150, h=190):
    """Garden arch over a gateway (walk-through: no collider)."""
    sp = Sprite(w, h)
    for px in (10, w - 24):
        sp.put(sp.rect(px, 50, 14, h - 52), quant(0.8 - (sp.xx - px) / 14 * 0.6, WOOD))
    ring = sp.ellipse(w / 2, 62, w / 2 - 4, 56) & ~sp.ellipse(w / 2, 66, w / 2 - 22, 46) & (sp.yy < 70)
    sp.put(ring, WOOD[3])
    rng = np.random.default_rng(3)
    ys, xs = np.nonzero(ring | (sp.rect(6, 50, 22, h - 60) | sp.rect(w - 28, 50, 22, h - 60)) & (sp.a > 0))
    for i in rng.integers(0, len(ys), 260):
        y, x = ys[i], xs[i]
        sp.put(sp.ellipse(x, y, 4, 3.5), LEAF[rng.integers(2, 6)])
    for i in rng.integers(0, len(ys), 70):
        y, x = ys[i], xs[i]
        sp.put(sp.ellipse(x, y, 2.4, 2.4), FLOWERS[i % 2][2])
        sp.rgb[y - 1, x - 1] = FLOWERS[i % 2][3]
    outline(sp, LEAF[0] * 0.8)
    return sp
