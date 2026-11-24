"""Generator aset pixel art orisinal (props, ikon, emote, UI, ikon aplikasi).
Semua digambar prosedural agar bebas lisensi dan mudah diganti.
Pemakaian: python3 tools/gen_art.py <android/assets> <android/res>
Ganti file PNG hasil dengan gambar buatanmu sendiri kapan saja: nama file & ukuran dicatat di docs/ASSET_LIST.md.
"""
import math
import sys, os, math
from PIL import Image, ImageDraw, ImageFont

ASSETS, RES = sys.argv[1], sys.argv[2]
OL = (59, 48, 73, 255)          # outline ungu tua (dari palet lembar karakter)
CREAM = (251, 243, 238, 255)
PINK = (232, 156, 180, 255); PINK_D = (196, 112, 146, 255)
LAV = (155, 138, 184, 255); LAV_D = (114, 98, 146, 255); LAV_L = (196, 184, 220, 255)
WOOD = (168, 119, 90, 255); WOOD_D = (126, 84, 64, 255); WOOD_L = (198, 152, 116, 255)
LEAF = (104, 150, 98, 255); LEAF_D = (70, 112, 74, 255); LEAF_L = (142, 186, 120, 255)
GOLD = (255, 214, 120, 255); GOLD_D = (222, 168, 72, 255)
SKY = (150, 196, 222, 255); GREY = (150, 146, 164, 255); GREY_D = (104, 100, 120, 255)
WHITE = (255, 255, 255, 255); T = (0, 0, 0, 0)

def new(w, h): return Image.new('RGBA', (w, h), T)
def save(img, *parts):
    p = os.path.join(ASSETS, *parts); os.makedirs(os.path.dirname(p), exist_ok=True); img.save(p)

def box(d, x, y, w, h, fill, outline=OL, hl=None, sh=None):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=outline)
    d.rectangle([x + 1, y + 1, x + w - 2, y + h - 2], fill=fill)
    if hl: d.line([x + 1, y + 1, x + w - 2, y + 1], fill=hl)
    if sh: d.line([x + 1, y + h - 2, x + w - 2, y + h - 2], fill=sh)

def ellipse(d, x, y, w, h, fill, outline=OL):
    d.ellipse([x, y, x + w - 1, y + h - 1], fill=outline)
    d.ellipse([x + 1, y + 1, x + w - 2, y + h - 2], fill=fill)

# ---------------- ikon & simbol ----------------
def flower(d, cx, cy, r, petal=PINK, center=GOLD):
    for a in range(5):
        ang = a * 2 * math.pi / 5 - math.pi / 2
        px, py = cx + math.cos(ang) * r * 0.62, cy + math.sin(ang) * r * 0.62
        ellipse(d, int(px - r * 0.45), int(py - r * 0.45), int(r * 0.9) + 1, int(r * 0.9) + 1, petal)
    ellipse(d, int(cx - r * 0.33), int(cy - r * 0.33), int(r * 0.66) + 1, int(r * 0.66) + 1, center)

def star(d, cx, cy, r, fill=GOLD):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.45
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    d.polygon(pts, fill=fill, outline=OL)

def book(d, x, y, w, h, cover=LAV, page=CREAM):
    box(d, x, y, w, h, cover, hl=LAV_L, sh=LAV_D)
    d.rectangle([x + 3, y + 2, x + 4, y + h - 3], fill=LAV_D)
    d.rectangle([x + w - 4, y + 3, x + w - 2, y + h - 3], fill=page)
    star(d, x + w // 2 + 1, y + h // 2, max(3, w // 5), GOLD)

def icon(name, painter, size=32):
    im = new(size, size); painter(ImageDraw.Draw(im), size); save(im, 'items', name + '.png'); return im

icon('paper_flower', lambda d, s: (d.line([16, 18, 16, 30], fill=LEAF_D, width=2), d.polygon([(16, 24), (10, 20), (12, 26)], fill=LEAF, outline=OL), flower(d, 16, 13, 10, PINK, GOLD)))
icon('postcard', lambda d, s: (box(d, 3, 7, 26, 19, CREAM, hl=WHITE, sh=(226, 214, 206, 255)), d.rectangle([20, 10, 26, 16], fill=PINK, outline=OL), d.line([6, 13, 16, 13], fill=GREY), d.line([6, 17, 16, 17], fill=GREY), d.line([6, 21, 13, 21], fill=GREY)))
icon('memory_book', lambda d, s: book(d, 5, 4, 22, 25))
icon('letter_two_sides', lambda d, s: (box(d, 3, 8, 26, 18, CREAM, hl=WHITE), d.line([4, 9, 16, 18, 28, 9], fill=OL), ellipse(d, 13, 15, 7, 7, PINK)))
icon('light_shard', lambda d, s: (d.polygon([(16, 2), (24, 14), (16, 30), (8, 14)], fill=GOLD, outline=OL), d.polygon([(16, 5), (20, 14), (16, 26)], fill=(255, 240, 190, 255))))
for nm, p in [('symbol_flower', lambda d, s: flower(d, s // 2, s // 2, s // 2 - 3)),
              ('symbol_book', lambda d, s: book(d, 5, 5, s - 10, s - 9)),
              ('symbol_star', lambda d, s: star(d, s // 2, s // 2 + 1, s // 2 - 2))]:
    icon(nm, p, 48)

# ---------------- penanda & efek ----------------
m = new(14, 14); d = ImageDraw.Draw(m); d.polygon([(7, 0), (13, 7), (7, 13), (0, 7)], fill=WHITE, outline=OL); save(m, 'ui', 'marker.png')
sh = new(32, 12); d = ImageDraw.Draw(sh); d.ellipse([0, 0, 31, 11], fill=(30, 24, 40, 90)); save(sh, 'ui', 'shadow.png')
px = new(4, 4); ImageDraw.Draw(px).rectangle([0, 0, 3, 3], fill=WHITE); save(px, 'ui', 'pixel.png')
sp = new(9, 9); d = ImageDraw.Draw(sp); d.line([4, 0, 4, 8], fill=WHITE); d.line([0, 4, 8, 4], fill=WHITE); d.point([(3, 3), (5, 5), (3, 5), (5, 3)], fill=WHITE); save(sp, 'ui', 'sparkle.png')
shard = new(20, 26); d = ImageDraw.Draw(shard); d.polygon([(10, 0), (19, 10), (10, 25), (1, 10)], fill=GOLD, outline=OL); d.polygon([(10, 3), (14, 10), (10, 21)], fill=(255, 244, 200, 255)); save(shard, 'props', 'light_shard.png')

def emote(name, painter):
    im = new(22, 22); d = ImageDraw.Draw(im); ellipse(d, 0, 0, 22, 19, CREAM); d.polygon([(7, 17), (11, 21), (13, 17)], fill=CREAM, outline=OL); d.line([8, 17, 12, 17], fill=CREAM); painter(d); save(im, 'ui', 'emote_' + name + '.png')
emote('exclaim', lambda d: (d.rectangle([10, 4, 11, 10], fill=(214, 72, 92, 255)), d.rectangle([10, 13, 11, 14], fill=(214, 72, 92, 255))))
emote('heart', lambda d: (d.ellipse([5, 5, 11, 11], fill=PINK_D), d.ellipse([10, 5, 16, 11], fill=PINK_D), d.polygon([(5, 9), (16, 9), (10.5, 15)], fill=PINK_D)))
emote('dots', lambda d: [d.rectangle([x, 9, x + 1, 10], fill=OL) for x in (6, 10, 14)])
emote('question', lambda d: (d.arc([7, 3, 14, 10], 180, 90, fill=LAV_D, width=2), d.line([11, 10, 11, 12], fill=LAV_D, width=2), d.rectangle([10, 14, 11, 15], fill=LAV_D)))
emote('note', lambda d: (d.line([12, 4, 12, 12], fill=LAV_D, width=2), d.line([12, 4, 16, 6], fill=LAV_D, width=2), d.ellipse([7, 10, 12, 14], fill=LAV_D)))
emote('sweat', lambda d: d.polygon([(12, 4), (15, 10), (12, 13), (9, 10)], fill=SKY, outline=OL))

# (props furnitur kini dibuat oleh tools/mapkit/props.py lewat tools/build_maps.py)
def prop(name, w, h, painter):
    im = new(w, h); painter(ImageDraw.Draw(im), w, h); save(im, 'props', name + '.png')

def glowing_book(d, w, h):
    ellipse(d, 0, h - 8, w, 8, (255, 236, 170, 120), (255, 236, 170, 0))
    book(d, 4, 0, w - 8, h - 4)
prop('glowing_book', 26, 24, glowing_book)

def pickup(name, src):
    im = Image.open(os.path.join(ASSETS, 'items', src)).convert('RGBA').resize((18, 18), Image.NEAREST)
    save(im, 'props', name + '.png')
pickup('pickup_paper_flower', 'paper_flower.png'); pickup('pickup_postcard', 'postcard.png')
pickup('pickup_note', 'small_note.png'); pickup('pickup_bookmark', 'bookmark.png')

# ---------------- ikon item tambahan (Chapter 2-6, side quest) ----------------
def ic(name, painter, size=32): icon(name, painter, size)
ic('bouquet', lambda d, s: (d.polygon([(10, 16), (22, 16), (18, 30), (14, 30)], fill=(150, 196, 222, 255), outline=OL),
    d.polygon([(13, 22), (19, 22), (17, 25), (15, 25)], fill=LAV),
    [flower(d, x, y, 5, c, GOLD) for (x, y, c) in [(10, 10, PINK), (16, 7, (255, 240, 246, 255)), (22, 10, LAV_L), (16, 13, PINK_D)]]))
ic('photo_small', lambda d, s: (box(d, 5, 5, 22, 24, WHITE), d.rectangle([8, 8, 23, 21], fill=(253, 205, 170, 255)), d.rectangle([8, 16, 23, 21], fill=(196, 160, 210, 255)), ellipse(d, 16, 9, 5, 5, GOLD)))
ic('photo_strip', lambda d, s: (box(d, 9, 1, 14, 30, WHITE), [d.rectangle([11, 3 + k * 9, 21, 9 + k * 9], fill=[PINK, LAV_L, SKY][k]) for k in range(3)]))
ic('strawberry', lambda d, s: (d.polygon([(8, 12), (24, 12), (16, 29)], fill=(226, 80, 96, 255), outline=OL), d.polygon([(10, 12), (16, 6), (22, 12)], fill=LEAF, outline=OL),
    [d.point([(x, y)], fill=GOLD) for (x, y) in [(13, 16), (19, 16), (16, 21), (14, 24), (18, 24)]]))
ic('honey', lambda d, s: (box(d, 8, 10, 16, 20, (240, 176, 64, 255)), box(d, 7, 6, 18, 6, WOOD_L), d.line([10, 14, 12, 26], fill=(255, 220, 140, 255))))
ic('mint', lambda d, s: [d.ellipse([x, y, x + 10, y + 14], fill=LEAF_L, outline=OL) for (x, y) in [(6, 12), (16, 10), (11, 4)]])
ic('sandwich', lambda d, s: (d.polygon([(4, 24), (28, 24), (16, 8)], fill=(240, 214, 160, 255), outline=OL), d.line([7, 20, 25, 20], fill=(226, 80, 96, 255), width=2), d.line([9, 17, 23, 17], fill=LEAF, width=1)))
ic('dried_flowers', lambda d, s: (d.line([16, 14, 12, 30], fill=WOOD_D), d.line([16, 14, 20, 30], fill=WOOD_D), d.line([16, 14, 16, 30], fill=WOOD_D),
    [ellipse(d, x, y, 5, 5, c) for (x, y, c) in [(10, 6, (226, 180, 190, 255)), (17, 3, CREAM), (20, 9, (210, 170, 200, 255)), (12, 12, CREAM)]], d.rectangle([12, 22, 20, 25], fill=LAV)))
ic('fairy_lights', lambda d, s: (d.arc([2, 0, 30, 24], 20, 160, fill=OL), [ellipse(d, x, y, 6, 6, c) for (x, y, c) in [(4, 10, GOLD), (10, 17, PINK), (16, 19, (200, 240, 255, 255)), (22, 17, GOLD), (27, 10, PINK)]]))
ic('star_frame', lambda d, s: (star(d, 16, 17, 14, GOLD_D), star(d, 16, 17, 8, (253, 205, 170, 255))))
ic('compass', lambda d, s: (ellipse(d, 4, 4, 24, 24, GOLD), ellipse(d, 7, 7, 18, 18, CREAM), d.polygon([(16, 8), (19, 16), (16, 24), (13, 16)], fill=(214, 72, 92, 255), outline=OL), d.point([(16, 16)], fill=OL)))
ic('lantern_small', lambda d, s: (d.line([16, 2, 16, 6], fill=OL), box(d, 9, 6, 14, 20, (255, 222, 160, 255)), d.rectangle([12, 9, 13, 23], fill=(170, 140, 230, 255)), d.rectangle([18, 9, 19, 23], fill=(120, 170, 240, 255))))
ic('brooch', lambda d, s: (flower(d, 16, 15, 12, PINK, GOLD), d.line([8, 27, 24, 27], fill=GREY_D, width=2)))
ic('cat_photo', lambda d, s: (box(d, 3, 4, 26, 24, WHITE), d.rectangle([6, 7, 25, 24], fill=(255, 236, 214, 255)), ellipse(d, 10, 12, 12, 10, (240, 160, 80, 255)),
    d.polygon([(11, 13), (12, 8), (15, 12)], fill=(240, 160, 80, 255)), d.polygon([(18, 12), (20, 8), (21, 13)], fill=(240, 160, 80, 255))))
ic('star_stone', lambda d, s: (d.polygon([(6, 28), (8, 10), (16, 3), (24, 10), (26, 28)], fill=(90, 96, 160, 255), outline=OL), star(d, 16, 16, 6, GOLD)))
ic('cat_plush', lambda d, s: (ellipse(d, 6, 10, 20, 18, (250, 220, 230, 255)), d.polygon([(8, 14), (9, 5), (14, 11)], fill=(250, 220, 230, 255), outline=OL),
    d.polygon([(18, 11), (23, 5), (24, 14)], fill=(250, 220, 230, 255), outline=OL), d.point([(12, 18), (20, 18)], fill=OL), d.line([14, 22, 18, 22], fill=PINK_D)))
ic('recipe', lambda d, s: (box(d, 5, 4, 22, 25, (255, 236, 170, 255)), [d.line([8, y, 23, y], fill=WOOD) for y in (9, 13, 17, 21)], ellipse(d, 20, 20, 6, 6, (226, 80, 96, 255))))
ic('album', lambda d, s: (box(d, 5, 4, 22, 25, (140, 110, 170, 255)), d.rectangle([9, 8, 23, 18], fill=CREAM), star(d, 16, 23, 3, GOLD)))

ic('fishing_rod', lambda d, s: (d.line([6, 28, 26, 4], fill=WOOD_D, width=3), d.line([26, 4, 26, 20], fill=GREY), ellipse(d, 23, 19, 6, 6, (214, 72, 92, 255)), ellipse(d, 6, 22, 7, 7, GREY_D)))
ic('fish_hat', lambda d, s: (d.ellipse([3, 16, 29, 26], fill=(150, 160, 100, 255), outline=OL), d.rectangle([9, 8, 23, 20], fill=(170, 180, 116, 255), outline=OL), d.line([9, 16, 23, 16], fill=(214, 72, 92, 255), width=2)))
op = new(18, 16); d = ImageDraw.Draw(op); d.polygon([(2, 3), (15, 1), (16, 14), (3, 15)], fill=(246, 234, 206, 255), outline=OL); d.line([5, 6, 13, 5], fill=WOOD); d.line([5, 9, 12, 8], fill=WOOD); d.point([(14, 3)], fill=GOLD); save(op, 'props', 'old_page.png')

def orb(name, col, r=7):
    im = new(r * 4, r * 4); d = ImageDraw.Draw(im); c = r * 2
    for k, a in [(r * 2 - 1, 50), (r + 3, 110)]: d.ellipse([c - k, c - k, c + k, c + k], fill=col[:3] + (a,))
    d.ellipse([c - r + 2, c - r + 2, c + r - 2, c + r - 2], fill=col); d.ellipse([c - 2, c - 3, c + 1, c], fill=WHITE)
    save(im, 'props', name + '.png')
orb('light_orb', (255, 236, 170, 255), 8); orb('spark', (190, 220, 255, 255), 5)
pt = new(20, 16); d = ImageDraw.Draw(pt); d.ellipse([2, 3, 17, 13], fill=(247, 182, 207, 255), outline=OL); d.line([5, 8, 15, 8], fill=(255, 230, 240, 255)); save(pt, 'props', 'petal.png')
cp = new(24, 24); d = ImageDraw.Draw(cp); ellipse(d, 2, 2, 20, 20, GOLD); ellipse(d, 5, 5, 14, 14, CREAM); d.polygon([(12, 5), (14, 12), (12, 19), (10, 12)], fill=(214, 72, 92, 255)); save(cp, 'props', 'compass.png')
st_ = new(16, 12); d = ImageDraw.Draw(st_); d.polygon([(1, 11), (3, 4), (8, 1), (13, 4), (15, 11)], fill=(170, 220, 255, 255), outline=OL); d.point([(6, 4), (7, 4), (6, 5)], fill=WHITE); save(st_, 'props', 'shiny_stone.png')
# ---- v1.0: hari bebas, festival, side quest baru
ic('ginger_candy', lambda d, s: (ellipse(d, 8, 10, 16, 12, (230, 170, 80, 255)), d.polygon([(8, 16), (2, 11), (2, 21)], fill=(240, 120, 120, 255), outline=OL), d.polygon([(24, 16), (30, 11), (30, 21)], fill=(240, 120, 120, 255), outline=OL)))
ic('star_sticker', lambda d, s: (ellipse(d, 3, 3, 26, 26, CREAM), star(d, 16, 16, 10, GOLD)))
ic('keychain_star', lambda d, s: (ellipse(d, 4, 2, 10, 10, GREY), d.line([9, 11, 14, 16], fill=GREY_D, width=2), star(d, 19, 21, 9, (190, 160, 240, 255))))
ic('market_book', lambda d, s: (box(d, 6, 4, 20, 25, (120, 160, 130, 255)), d.rectangle([9, 4, 11, 28], fill=(90, 120, 100, 255)), d.line([14, 10, 23, 10], fill=CREAM), d.line([14, 14, 21, 14], fill=CREAM)))
ic('fruit', lambda d, s: (ellipse(d, 5, 7, 22, 20, (255, 160, 60, 255)), d.line([16, 7, 17, 3], fill=WOOD_D, width=2), ellipse(d, 17, 2, 8, 5, (110, 180, 100, 255))))
ic('flower_crown', lambda d, s: (d.ellipse([4, 10, 28, 26], outline=(110, 170, 100, 255), width=3), *[ellipse(d, x, y, 7, 7, c) for x, y, c in [(3, 13, PINK), (12, 8, CREAM), (21, 13, GOLD), (8, 20, LAV_L), (17, 20, PINK)]]))
ic('stamp', lambda d, s: (box(d, 5, 5, 22, 22, CREAM), d.rectangle([9, 9, 23, 23], fill=(110, 140, 200, 255)), star(d, 16, 16, 5, GOLD)))
ic('apron', lambda d, s: (d.polygon([(10, 4), (22, 4), (22, 10), (27, 12), (25, 29), (7, 29), (5, 12), (10, 10)], fill=(214, 120, 120, 255), outline=OL), d.rectangle([12, 16, 20, 22], fill=CREAM, outline=OL)))
ic('lantern_bookmark', lambda d, s: (box(d, 11, 2, 10, 28, (180, 150, 220, 255)), ellipse(d, 12, 10, 8, 10, GOLD), d.line([16, 30, 16, 31], fill=PINK_D)))
ic('tea_glass', lambda d, s: (d.polygon([(8, 8), (24, 8), (22, 28), (10, 28)], fill=(200, 130, 70, 220), outline=OL), d.line([10, 12, 22, 12], fill=CREAM)))
ic('wish_card', lambda d, s: (box(d, 6, 6, 20, 22, (255, 230, 200, 255)), d.line([16, 2, 16, 6], fill=WOOD), ellipse(d, 11, 13, 10, 8, PINK)))
ic('lantern_paper', lambda d, s: (ellipse(d, 6, 6, 20, 22, (255, 190, 110, 255)), d.line([6, 17, 26, 17], fill=(230, 140, 70, 255)), d.rectangle([12, 27, 20, 29], fill=WOOD_D), ellipse(d, 13, 13, 6, 6, (255, 240, 180, 255))))
bk = new(18, 14); d = ImageDraw.Draw(bk); d.rectangle([1, 2, 16, 12], fill=(160, 90, 110, 255), outline=OL); d.rectangle([3, 3, 15, 10], fill=CREAM); d.line([3, 11, 16, 11], fill=OL); save(bk, 'props', 'lost_book.png')
pc = new(14, 16); d = ImageDraw.Draw(pc); d.rectangle([1, 3, 12, 15], fill=GREY, outline=OL); d.rectangle([1, 6, 12, 11], fill=(232, 156, 180, 255)); d.arc([3, 0, 10, 6], 180, 360, fill=OL); save(pc, 'props', 'paint_can.png')
for nm, col in [('paint_pink', (232, 156, 180, 255)), ('paint_yellow', (255, 214, 100, 255)), ('paint_purple', (170, 130, 220, 255)), ('paint_blue', (120, 170, 230, 255))]:
    pc = new(14, 16); d = ImageDraw.Draw(pc); d.rectangle([1, 3, 12, 15], fill=GREY, outline=OL); d.rectangle([1, 6, 12, 11], fill=col); d.arc([3, 0, 10, 6], 180, 360, fill=OL); save(pc, 'props', nm + '.png')
lt = new(16, 12); d = ImageDraw.Draw(lt); d.rectangle([1, 1, 14, 10], fill=CREAM, outline=OL); d.line([1, 1, 8, 6], fill=OL); d.line([14, 1, 8, 6], fill=OL); d.point([(12, 8)], fill=(214, 72, 92, 255)); save(lt, 'props', 'letter.png')
wc = new(18, 14); d = ImageDraw.Draw(wc); d.rectangle([4, 4, 13, 13], fill=SKY, outline=OL); d.line([13, 6, 17, 2], fill=OL, width=2); d.arc([0, 2, 7, 11], 90, 270, fill=OL); save(wc, 'props', 'watering.png')
ic('watering', lambda d, s: (box(d, 7, 10, 15, 16, SKY), d.line([22, 13, 29, 6], fill=OL, width=3), d.arc([2, 10, 12, 22], 90, 270, fill=OL, width=2)))
# ---- v1.3: eksplorasi
ic('symbol_moon', lambda d, s: (ellipse(d, 5, 4, 22, 22, GOLD), ellipse(d, 12, 2, 20, 20, (0, 0, 0, 0)) if False else d.ellipse([12, 1, 31, 22], fill=(0, 0, 0, 0))))
ic('shell', lambda d, s: (d.pieslice([4, 6, 28, 30], 180, 360, fill=(250, 214, 196, 255), outline=OL), *[d.line([16, 18, 16 + 11 * math.cos(math.radians(a)), 18 - 11 * math.sin(math.radians(a))], fill=(214, 150, 140, 255)) for a in (20, 55, 90, 125, 160)], box(d, 13, 17, 19, 24, (240, 190, 170, 255))))
ic('music_box', lambda d, s: (box(d, 4, 12, 27, 28, (190, 140, 200, 255)), box(d, 3, 8, 28, 13, (220, 180, 230, 255)), d.line([24, 6, 28, 2], fill=GOLD, width=2), star(d, 15, 20, 4, GOLD)))
ic('scarf', lambda d, s: (d.polygon([(4, 8), (28, 8), (28, 14), (12, 14), (12, 28), (6, 28)], fill=(214, 100, 120, 255), outline=OL), *[d.line([x, 9, x, 13], fill=(240, 160, 170, 255)) for x in range(8, 27, 4)]))
ic('mini_painting', lambda d, s: (box(d, 4, 4, 27, 27, WOOD), box(d, 7, 7, 24, 24, (170, 210, 240, 255)), d.polygon([(8, 23), (14, 14), (19, 20), (22, 16), (24, 23)], fill=(110, 170, 100, 255)), ellipse(d, 18, 9, 4, 4, GOLD)))
ic('crystal_necklace', lambda d, s: (d.arc([4, 2, 28, 22], 20, 160, fill=GOLD, width=2), d.polygon([(16, 16), (21, 22), (16, 30), (11, 22)], fill=(150, 210, 255, 255), outline=OL), d.line([16, 18, 16, 27], fill=WHITE)))
ic('plank', lambda d, s: (d.polygon([(3, 20), (24, 4), (29, 10), (8, 26)], fill=(200, 150, 100, 255), outline=OL), d.line([8, 21, 25, 8], fill=(160, 110, 70, 255))))
ic('mini_telescope', lambda d, s: (d.polygon([(4, 20), (24, 6), (28, 12), (8, 26)], fill=(180, 160, 230, 255), outline=OL), box(d, 23, 3, 29, 11, GOLD), d.line([14, 20, 10, 30], fill=GREY_D, width=2), d.line([14, 20, 20, 30], fill=GREY_D, width=2)))
ic('star_piece', lambda d, s: (star(d, 16, 16, 12, GOLD), star(d, 16, 16, 6, (255, 246, 200, 255))))
sp = new(20, 20); d = ImageDraw.Draw(sp); star(d, 10, 10, 9, GOLD); star(d, 10, 10, 4, (255, 248, 210, 255)); save(sp, 'props', 'star_piece.png')
pk = new(26, 14); d = ImageDraw.Draw(pk); d.polygon([(1, 9), (20, 1), (25, 5), (6, 13)], fill=(200, 150, 100, 255), outline=OL); d.line([6, 9, 20, 3], fill=(160, 110, 70, 255)); save(pk, 'props', 'plank.png')
# lingkar cahaya gua: tengah bening, tepi gelap (warna sama dengan isi luar)
import numpy as _np
_N = 256; _yy, _xx = _np.mgrid[0:_N, 0:_N]; _r = _np.sqrt(((_xx - _N / 2) / (_N / 2)) ** 2 + ((_yy - _N / 2) / (_N / 2)) ** 2)
_a = _np.clip((_r - 0.35) / 0.65, 0, 1) ** 1.4 * 0.9 * 255
_img = _np.zeros((_N, _N, 4), _np.uint8); _img[..., 0] = 8; _img[..., 1] = 5; _img[..., 2] = 18; _img[..., 3] = _a.astype(_np.uint8)
save(Image.fromarray(_img, 'RGBA'), 'ui', 'darkness.png')
def cat_img():
    im = new(30, 24); d = ImageDraw.Draw(im); O = (240, 160, 80, 255); OD = (200, 120, 60, 255)
    d.ellipse([4, 9, 25, 23], fill=OL); d.ellipse([5, 10, 24, 22], fill=O)
    d.ellipse([16, 2, 29, 14], fill=OL); d.ellipse([17, 3, 28, 13], fill=O)
    d.polygon([(17, 5), (18, 0), (21, 4)], fill=O, outline=OL); d.polygon([(24, 4), (27, 0), (28, 6)], fill=O, outline=OL)
    d.point([(20, 8), (25, 8)], fill=OL); d.line([1, 14, 5, 18], fill=OD, width=2)
    for x in (9, 13): d.line([x, 12, x + 1, 20], fill=OD)
    return im
save(cat_img(), 'props', 'mochi.png')

# ---------------- UI (dibuat 2x lalu diperkecil agar halus) ----------------
def aa(w, h, painter, ss=4):
    big = Image.new('RGBA', (w * ss, h * ss), T); painter(ImageDraw.Draw(big), w * ss, h * ss, ss)
    return big.resize((w, h), Image.LANCZOS)

def rounded(fill, border, r=14, bw=3, w=48, h=48):
    def p(d, W, H, s):
        d.rounded_rectangle([0, 0, W - 1, H - 1], radius=r * s, fill=border)
        d.rounded_rectangle([bw * s, bw * s, W - 1 - bw * s, H - 1 - bw * s], radius=(r - bw) * s, fill=fill)
    return aa(w, h, p)
save(rounded((251, 243, 238, 245), (88, 70, 108, 255)), 'ui', 'panel.png')
save(rounded((44, 34, 60, 225), (196, 184, 220, 200)), 'ui', 'panel_dark.png')
save(rounded((255, 250, 247, 255), (88, 70, 108, 255), r=16), 'ui', 'button.png')
save(rounded((236, 188, 208, 255), (88, 70, 108, 255), r=16), 'ui', 'button_down.png')
save(rounded((232, 156, 180, 255), (88, 70, 108, 255), r=16), 'ui', 'button_accent.png')
save(rounded((210, 204, 216, 255), (150, 140, 160, 255), r=16), 'ui', 'button_disabled.png')

def circle(fill, border, size, bw=4):
    def p(d, W, H, s):
        d.ellipse([0, 0, W - 1, H - 1], fill=border)
        d.ellipse([bw * s, bw * s, W - 1 - bw * s, H - 1 - bw * s], fill=fill)
    return aa(size, size, p)
save(circle((44, 34, 60, 110), (255, 255, 255, 120), 256, 5), 'ui', 'joy_base.png')
save(circle((251, 243, 238, 230), (88, 70, 108, 255), 112, 5), 'ui', 'joy_knob.png')
save(circle((232, 156, 180, 235), (88, 70, 108, 255), 160, 6), 'ui', 'btn_action.png')
save(circle((251, 243, 238, 220), (88, 70, 108, 255), 120, 5), 'ui', 'btn_round.png')
save(circle((255, 214, 120, 235), (88, 70, 108, 255), 120, 5), 'ui', 'btn_round_on.png')

def heart_icon(size, col):
    def p(d, W, H, s):
        r = W * 0.27
        d.ellipse([W * 0.08, H * 0.12, W * 0.08 + 2 * r, H * 0.12 + 2 * r], fill=col)
        d.ellipse([W * 0.92 - 2 * r, H * 0.12, W * 0.92, H * 0.12 + 2 * r], fill=col)
        d.polygon([(W * 0.1, H * 0.42), (W * 0.9, H * 0.42), (W * 0.5, H * 0.9)], fill=col)
    return aa(size, size, p)
save(heart_icon(64, (255, 255, 255, 255)), 'ui', 'icon_heart.png')

def coin_icon(size):
    def p(d, W, H, s):
        d.ellipse([W * 0.1, H * 0.1, W * 0.9, H * 0.9], fill=(120, 88, 34, 255))
        d.ellipse([W * 0.16, H * 0.16, W * 0.84, H * 0.84], fill=GOLD)
        d.ellipse([W * 0.24, H * 0.24, W * 0.76, H * 0.76], fill=(255, 236, 168, 255))
        star(d, W * 0.5, H * 0.5, W * 0.16, (255, 210, 92, 255))
    return aa(size, size, p)

def soft_glow(size):
    import numpy as _np
    n = size
    yy, xx = _np.mgrid[0:n, 0:n]
    r = _np.sqrt((xx - n / 2) ** 2 + (yy - n / 2) ** 2) / (n / 2)
    a = _np.clip(1 - r, 0, 1) ** 2.6
    img = _np.zeros((n, n, 4), _np.uint8)
    img[..., 0] = 255; img[..., 1] = 244; img[..., 2] = 212; img[..., 3] = (a * 215).astype(_np.uint8)
    return Image.fromarray(img, 'RGBA')

save(coin_icon(64), 'ui', 'icon_coin.png')
save(soft_glow(128), 'ui', 'soft_glow.png')

# ---------------- ikon aplikasi Android ----------------
def app_icon(size):
    bg = aa(size, size, lambda d, W, H, s: (d.ellipse([0, 0, W - 1, H - 1], fill=(155, 138, 184, 255)),
                                            d.ellipse([W * 0.06, H * 0.06, W * 0.94, H * 0.94], fill=(246, 196, 214, 255))))
    a = Image.open(os.path.join(ASSETS, 'characters', 'arland', 'walk.png')).crop((0, 0, 48, 72))
    b = Image.open(os.path.join(ASSETS, 'characters', 'sofia', 'walk.png')).crop((0, 0, 48, 72))
    pair = Image.new('RGBA', (84, 72), T); pair.alpha_composite(a, (0, 0)); pair.alpha_composite(b, (36, 0))
    k = (size * 0.62) / pair.height
    pair = pair.resize((max(1, int(pair.width * k)), max(1, int(pair.height * k))), Image.NEAREST)
    bg.alpha_composite(pair, ((size - pair.width) // 2, int(size * 0.24)))
    h = heart_icon(max(8, size // 5), (214, 72, 120, 255)); bg.alpha_composite(h, ((size - h.width) // 2, int(size * 0.07)))
    return bg
for dens, s in [('mdpi', 48), ('hdpi', 72), ('xhdpi', 96), ('xxhdpi', 144), ('xxxhdpi', 192)]:
    p = os.path.join(RES, 'mipmap-' + dens); os.makedirs(p, exist_ok=True)
    app_icon(s).save(os.path.join(p, 'ic_launcher.png'))
app_icon(512).save(os.path.join(ASSETS, 'ui', 'app_icon_512.png'))
print('art ok')
