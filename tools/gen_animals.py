"""Sprite hewan ambient (pixel art 1x, menghadap kanan). Tiap lembar: 4 frame menyamping
[jalan A, jalan B, diam, istirahat]. Bebek: [renang A, renang B, diam, menyelam]. Burung: [kepak A, kepak B, berdiri, mematuk].
Pemakaian: python3 tools/gen_animals.py <android/assets>
"""
import sys, os
from PIL import Image, ImageDraw

A = sys.argv[1]
OUT = os.path.join(A, 'animals'); os.makedirs(OUT, exist_ok=True)
OUTLINE = (42, 30, 40, 255)

def hexc(h, a=255): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (a,)
def mul(c, k): return tuple(max(0, min(255, int(v * k))) for v in c[:3]) + (c[3],)

def finish(img):
    """bayangan bawah, sorotan atas, lalu garis tepi 1 px di luar bentuk."""
    w, h = img.size; px = img.load(); src = img.copy(); sp = src.load()
    for y in range(h):
        for x in range(w):
            c = sp[x, y]
            if c[3] == 0 or c == OUTLINE or c[:3] == (255, 255, 255) and False: continue
            if c[3] < 250: continue
            up = sp[x, y - 1] if y > 0 else (0, 0, 0, 0)
            dn = sp[x, y + 1] if y < h - 1 else (0, 0, 0, 0)
            if up[3] == 0: px[x, y] = mul(c, 1.14)
            elif dn[3] == 0: px[x, y] = mul(c, 0.78)
    out = img.copy(); op = out.load(); ip = img.load()
    for y in range(h):
        for x in range(w):
            if ip[x, y][3] != 0: continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and ip[nx, ny][3] >= 250 and ip[nx, ny] != OUTLINE: op[x, y] = OUTLINE; break
    return out

def sheet(name, frames):
    fw, fh = frames[0].size
    s = Image.new('RGBA', (fw * len(frames), fh), (0, 0, 0, 0))
    for i, f in enumerate(frames): s.alpha_composite(finish(f), (i * fw, 0))
    s.save(os.path.join(OUT, name + '.png'))

def canvas(w, h): img = Image.new('RGBA', (w, h), (0, 0, 0, 0)); return img, ImageDraw.Draw(img)

# ---------------------------------------------------------------- kucing (24x22)
def cat(main, belly, accent=None, eye='#3a8a3a'):
    M, B = hexc(main), hexc(belly); Ac = hexc(accent) if accent else M; E = hexc(eye); ear = hexc('#e9a0a8')
    fr = []
    for f in range(4):
        img, d = canvas(24, 22)
        if f == 3:  # meringkuk seperti roti
            d.ellipse([3, 11, 19, 20], fill=M); d.ellipse([6, 15, 15, 20], fill=B)
            d.ellipse([14, 8, 22, 16], fill=M); d.polygon([(15, 9), (16, 5), (18, 9)], fill=M); d.polygon([(19, 9), (21, 5), (22, 10)], fill=M)
            d.point((16, 7), fill=ear); d.point((20, 7), fill=ear)
            d.line([(17, 12), (18, 12)], fill=OUTLINE); d.line([(20, 12), (21, 12)], fill=OUTLINE)  # mata terpejam
            d.ellipse([1, 16, 9, 20], fill=Ac)  # ekor melingkar
            if accent: d.ellipse([8, 11, 13, 15], fill=Ac)
        else:
            sit = f == 2
            lift = [0, 1, 0][f] if f < 3 else 0
            # ekor
            if sit: d.line([(4, 18), (2, 14), (3, 10)], fill=Ac, width=2)
            else: d.line([(5, 12), (2, 8), (3, 5)], fill=Ac, width=2)
            # badan
            if sit: d.ellipse([5, 9, 16, 20], fill=M); d.ellipse([9, 12, 15, 20], fill=B)
            else: d.ellipse([4, 9 - lift, 18, 17 - lift], fill=M); d.ellipse([8, 13 - lift, 16, 17 - lift], fill=B)
            if accent and not sit: d.ellipse([6, 9 - lift, 11, 13 - lift], fill=Ac)
            # kaki
            if sit: d.rectangle([11, 18, 12, 20], fill=B); d.rectangle([14, 18, 15, 20], fill=B)
            else:
                a, b_ = (0, 1) if f == 0 else (1, 0)
                for lx, o in ((6, a), (9, b_), (13, a), (16, b_)): d.rectangle([lx, 16 - lift, lx + 1, 19 - o * 2], fill=M if lx < 12 else B)
            # kepala
            hx, hy = (12, 2) if sit else (14, 3 - lift)
            d.ellipse([hx, hy + 2, hx + 9, hy + 10], fill=M)
            d.polygon([(hx + 1, hy + 4), (hx + 2, hy), (hx + 4, hy + 3)], fill=M); d.polygon([(hx + 6, hy + 3), (hx + 8, hy), (hx + 9, hy + 5)], fill=M)
            d.point((hx + 2, hy + 2), fill=ear); d.point((hx + 8, hy + 2), fill=ear)
            d.ellipse([hx + 3, hy + 6, hx + 8, hy + 10], fill=B)
            d.point((hx + 4, hy + 5), fill=E); d.point((hx + 7, hy + 5), fill=E)
            d.point((hx + 6, hy + 7), fill=hexc('#d0707a'))
        fr.append(img)
    return fr

# ---------------------------------------------------------------- anjing (30x22)
def dog():
    M, B, Ear = hexc('#c8904c'), hexc('#f2e2c4'), hexc('#7a4e2a'); fr = []
    for f in range(4):
        img, d = canvas(30, 22)
        if f == 3:
            d.ellipse([3, 12, 23, 20], fill=M); d.ellipse([18, 10, 28, 19], fill=M); d.ellipse([23, 14, 29, 19], fill=B)
            d.ellipse([18, 10, 22, 17], fill=Ear); d.line([(24, 13), (25, 13)], fill=OUTLINE); d.point((28, 15), fill=OUTLINE)
            d.line([(3, 16), (0, 18)], fill=M, width=2)
        else:
            lift = 1 if f == 1 else 0
            tail = [(5, 10), (2, 5)] if f != 2 else [(5, 10), (1, 7)]
            d.line(tail, fill=M, width=2)
            d.ellipse([4, 8 - lift, 22, 16 - lift], fill=M); d.ellipse([9, 12 - lift, 20, 16 - lift], fill=B)
            a, b_ = (0, 1) if f == 0 else (1, 0) if f == 1 else (0, 0)
            for lx, o in ((6, a), (9, b_), (17, a), (20, b_)): d.rectangle([lx, 15 - lift, lx + 1, 20 - o * 2], fill=M)
            hx, hy = 18, 1 - lift
            d.ellipse([hx, hy + 2, hx + 10, hy + 11], fill=M); d.ellipse([hx + 5, hy + 6, hx + 11, hy + 11], fill=B)
            d.ellipse([hx, hy + 3, hx + 4, hy + 11], fill=Ear)
            d.point((hx + 7, hy + 5), fill=OUTLINE); d.point((hx + 10, hy + 7), fill=OUTLINE)
            if f == 2: d.rectangle([hx + 7, hy + 10, hx + 8, hy + 12], fill=hexc('#e2707a'))  # lidah
        fr.append(img)
    return fr

# ---------------------------------------------------------------- bebek (24x22)
def duck():
    W, Hd, Bk = hexc('#f6f0e0'), hexc('#2f7a4a'), hexc('#f0a030'); wave = hexc('#bfe6ff', 200); fr = []
    for f in range(4):
        img, d = canvas(24, 22)
        if f == 3:  # menyelam: ekor saja
            d.polygon([(8, 16), (13, 10), (16, 16)], fill=W)
        else:
            by = 11 + (1 if f == 1 else 0)
            d.ellipse([3, by, 18, by + 7], fill=W); d.polygon([(3, by + 2), (0, by - 1), (5, by + 1)], fill=W)
            d.ellipse([6, by + 1, 13, by + 5], fill=hexc('#ddd4c0'))
            d.rectangle([13, by - 5, 15, by + 1], fill=Hd)
            d.ellipse([12, by - 9, 19, by - 3], fill=Hd)
            d.rectangle([19, by - 6, 22, by - 5], fill=Bk); d.point((17, by - 7), fill=OUTLINE)
        img2 = img.copy(); dd = ImageDraw.Draw(img2)
        dd.line([(1, 19), (22, 19)], fill=wave); dd.point((4 + f * 3, 18), fill=wave)
        fr.append(img2)
    return fr

# ---------------------------------------------------------------- burung (16x14)
def bird():
    M, B, Bk = hexc('#8a6a4a'), hexc('#e8d0b0'), hexc('#e0a040'); fr = []
    for f in range(4):
        img, d = canvas(16, 14)
        if f < 2:  # terbang
            d.ellipse([4, 6, 12, 10], fill=M); d.ellipse([10, 4, 15, 8], fill=M); d.point((14, 6), fill=Bk)
            if f == 0: d.polygon([(6, 7), (9, 1), (10, 7)], fill=M)
            else: d.polygon([(6, 8), (9, 13), (10, 8)], fill=M)
        else:
            peck = f == 3
            d.ellipse([3, 6, 11, 12], fill=M); d.ellipse([5, 9, 10, 12], fill=B); d.line([(3, 8), (0, 6)], fill=M, width=2)
            hy = 6 if peck else 3
            d.ellipse([8, hy, 13, hy + 5], fill=M); d.point((14, hy + 3 if peck else hy + 2), fill=Bk); d.point((11, hy + 1), fill=OUTLINE)
            d.line([(6, 12), (6, 13)], fill=Bk); d.line([(8, 12), (8, 13)], fill=Bk)
        fr.append(img)
    return fr

# ---------------------------------------------------------------- ayam (24x22)
def chicken():
    W, R, Bk = hexc('#fbf6ec'), hexc('#e04040'), hexc('#f0b030'); fr = []
    for f in range(4):
        img, d = canvas(24, 22)
        peck = f == 3; lift = 1 if f == 1 else 0
        d.polygon([(4, 8 - lift), (2, 3 - lift), (7, 7 - lift)], fill=W)  # ekor
        d.ellipse([3, 7 - lift, 17, 17 - lift], fill=W); d.ellipse([6, 10 - lift, 13, 14 - lift], fill=hexc('#e8e0d0'))
        hx, hy = (14, 8) if peck else (13, 1 - lift)
        d.ellipse([hx, hy + 2, hx + 7, hy + 9], fill=W)
        d.rectangle([hx + 2, hy, hx + 5, hy + 2], fill=R)
        d.polygon([(hx + 7, hy + 5), (hx + 9, hy + 6), (hx + 7, hy + 7)], fill=Bk); d.point((hx + 5, hy + 4), fill=OUTLINE)
        d.rectangle([hx + 6, hy + 8, hx + 7, hy + 9], fill=R)
        a, b_ = (0, 1) if f == 0 else (1, 0) if f == 1 else (0, 0)
        d.line([(8, 17 - lift), (8, 20 - a)], fill=Bk); d.line([(12, 17 - lift), (12, 20 - b_)], fill=Bk)
        fr.append(img)
    return fr

# ---------------------------------------------------------------- kelinci (24x22)
def rabbit():
    M, B, Ear = hexc('#b89878'), hexc('#f4ece0'), hexc('#e9a0a8'); fr = []
    for f in range(4):
        img, d = canvas(24, 22)
        hop = 2 if f == 1 else 0; flat = f == 3
        by = 12 - hop
        d.ellipse([4, by, 17, by + 9], fill=M); d.ellipse([2, by + 3, 6, by + 7], fill=B)  # ekor
        d.ellipse([9, by + 4, 16, by + 9], fill=B)
        hx, hy = 13, by - 4
        d.ellipse([hx, hy + 2, hx + 8, hy + 9], fill=M)
        if flat: d.ellipse([hx - 6, hy + 2, hx + 2, hy + 5], fill=M)
        else: d.ellipse([hx + 1, hy - 6, hx + 4, hy + 3], fill=M); d.ellipse([hx + 4, hy - 5, hx + 7, hy + 3], fill=M); d.line([(hx + 2, hy - 4), (hx + 2, hy + 1)], fill=Ear)
        d.point((hx + 5, hy + 4), fill=OUTLINE); d.point((hx + 8, hy + 6), fill=Ear)
        if f != 1: d.rectangle([6, by + 8, 9, by + 10], fill=M); d.rectangle([13, by + 8, 14, by + 10], fill=B)
        fr.append(img)
    return fr

# ---------------------------------------------------------------- tupai (18x22)
def squirrel():
    M, B, T = hexc('#b8642e'), hexc('#f0d0a0'), hexc('#d07a3a'); fr = []
    for f in range(4):
        img, d = canvas(18, 22)
        lift = 2 if f == 1 else 0
        d.ellipse([0, 3 - lift, 8, 16 - lift], fill=T); d.ellipse([2, 6 - lift, 7, 14 - lift], fill=hexc('#e0965a'))  # ekor besar
        d.ellipse([5, 11 - lift, 13, 19 - lift], fill=M); d.ellipse([8, 13 - lift, 12, 19 - lift], fill=B)
        hy = 6 - lift if f != 3 else 9
        d.ellipse([9, hy, 16, hy + 7], fill=M); d.polygon([(10, hy + 1), (11, hy - 2), (13, hy + 1)], fill=M)
        d.point((13, hy + 3), fill=OUTLINE); d.point((16, hy + 4), fill=OUTLINE)
        if f == 3: d.ellipse([12, hy + 6, 15, hy + 9], fill=hexc('#7a5030'))  # memegang biji
        d.rectangle([7, 19 - lift, 8, 20], fill=M); d.rectangle([11, 19 - lift, 12, 20], fill=M)
        fr.append(img)
    return fr

sheet('cat_orange', cat('#e8964a', '#fbe8cc'))
sheet('cat_grey', cat('#8f939e', '#e6e6ea', eye='#d0a020'))
sheet('cat_black', cat('#3e3a44', '#5a5462', eye='#e0c040'))
sheet('cat_calico', cat('#f6efe4', '#ffffff', accent='#e0904a', eye='#4a9a6a'))
sheet('dog', dog()); sheet('duck', duck()); sheet('bird', bird()); sheet('chicken', chicken()); sheet('rabbit', rabbit()); sheet('squirrel', squirrel())

if len(sys.argv) > 2:  # pratinjau diperbesar
    names = ['cat_orange', 'cat_grey', 'cat_black', 'cat_calico', 'dog', 'duck', 'bird', 'chicken', 'rabbit', 'squirrel']
    ims = [Image.open(os.path.join(OUT, n + '.png')) for n in names]
    W = max(i.width for i in ims) * 6 + 20; H = sum(i.height * 6 + 10 for i in ims) + 10
    pv = Image.new('RGBA', (W, H), (120, 170, 110, 255)); y = 10
    for i in ims: pv.alpha_composite(i.resize((i.width * 6, i.height * 6), Image.NEAREST), (10, y)); y += i.height * 6 + 10
    pv.save(sys.argv[2])
print('hewan: 10 lembar sprite')
