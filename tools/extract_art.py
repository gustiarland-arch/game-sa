"""Ekstraksi aset dari CHARACTER_DESIGN_REFERENCE.png (lembar desain milik user).
Hasil: sprite sheet 4 arah, potret ekspresi, kartu profil, banner judul.
Pemakaian: python3 tools/extract_art.py <sheet.png> <out_assets_dir>
"""
import sys, os
from collections import deque
from PIL import Image
import numpy as np

SRC, OUT = sys.argv[1], sys.argv[2]
img = Image.open(SRC).convert('RGB')
A = np.asarray(img).astype(int)

COLS = {'arland': [(79,121),(134,177),(191,233)], 'sofia': [(266,303),(321,356),(375,410)]}
ROWS = [(386,452),(462,526),(537,599),(608,673)]   # depan, kiri, kanan, belakang
CELL_W, CELL_H = 48, 72                            # frame ukuran seragam (asli, tanpa resample)
PAD = 3

def cut_sprite(x0, y0, x1, y1, tol=46):
    """Flood-fill latar dari tepi kotak; sisa = sprite (interior putih hoodie tetap aman)."""
    x0-=PAD; y0-=PAD; x1+=PAD; y1+=PAD
    r = A[y0:y1+1, x0:x1+1]
    h, w, _ = r.shape
    bg = np.median(np.concatenate([r[0], r[-1], r[:,0], r[:,-1]]), axis=0)
    near = np.abs(r - bg).sum(axis=2) <= tol
    seen = np.zeros((h,w), bool)
    q = deque()
    for x in range(w):
        for y in (0, h-1):
            if near[y,x] and not seen[y,x]: seen[y,x]=True; q.append((y,x))
    for y in range(h):
        for x in (0, w-1):
            if near[y,x] and not seen[y,x]: seen[y,x]=True; q.append((y,x))
    while q:
        y,x = q.popleft()
        for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
            ny,nx = y+dy, x+dx
            if 0<=ny<h and 0<=nx<w and not seen[ny,nx] and near[ny,nx]:
                seen[ny,nx]=True; q.append((ny,nx))
    alpha = np.where(seen, 0, 255).astype(np.uint8)
    rgba = np.dstack([r.astype(np.uint8), alpha])
    im = Image.fromarray(rgba, 'RGBA')
    bb = im.getbbox()
    return im.crop(bb)

def build_sheet(name):
    sheet = Image.new('RGBA', (CELL_W*3, CELL_H*4), (0,0,0,0))
    for ri,(y0,y1) in enumerate(ROWS):
        for ci,(x0,x1) in enumerate(COLS[name]):
            spr = cut_sprite(x0,y0,x1,y1)
            if spr.width > CELL_W or spr.height > CELL_H:
                spr.thumbnail((CELL_W, CELL_H), Image.NEAREST)
            # rata tengah horizontal, kaki menempel dasar sel
            ox = ci*CELL_W + (CELL_W - spr.width)//2
            oy = ri*CELL_H + (CELL_H - spr.height) - 1
            sheet.alpha_composite(spr, (ox, oy))
    d = os.path.join(OUT, 'characters', name); os.makedirs(d, exist_ok=True)
    sheet.save(os.path.join(d, 'walk.png'))

EXPR = ['normal','senang','tertawa','kaget','serius','malu','sedih','tersenyum']
EXPR_SOFIA = ['normal','senang','tertawa','kaget','pikir','malu','sedih','tersenyum']
CUTS = {'arland': [864,945,1025,1107,1192,1273,1355,1435,1519],
        'sofia':  [864,945,1026,1107,1193,1274,1353,1435,1520]}
PW, PH = 88, 110   # kanvas potret seragam (sebelum diperbesar 2x nearest)
def build_portraits(name, y0, y1, names, skip=()):
    d = os.path.join(OUT, 'characters', name, 'portraits'); os.makedirs(d, exist_ok=True)
    c = CUTS[name]
    for i, e in enumerate(names):
        if i in skip: continue
        crop = img.crop((c[i]+1, y0, c[i+1], y1))
        canvas = Image.new('RGB', (PW, PH), (251, 243, 240))
        canvas.paste(crop, ((PW-crop.width)//2, PH-crop.height))
        canvas.resize((PW*2, PH*2), Image.NEAREST).save(os.path.join(d, e + '.png'))

def build_ui():
    d = os.path.join(OUT, 'ui'); os.makedirs(d, exist_ok=True)
    img.crop((0, 0, 880, 292)).save(os.path.join(d, 'title_banner.png'))
    img.crop((903, 53, 1029, 253)).save(os.path.join(d, 'card_arland.png'))
    img.crop((1214, 55, 1340, 254)).save(os.path.join(d, 'card_sofia.png'))

build_sheet('arland'); build_sheet('sofia')
# Ekspresi ke-8 Arland ("Tersenyum") di lembar asli ternyata wajah Sofia -> dilewati.
build_portraits("arland", 378, 476, EXPR, skip=(7,))
build_portraits("sofia", 554, 657, EXPR_SOFIA)
build_ui()
print('ok')
