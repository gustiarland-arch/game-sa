"""Membuat lembar pose dari sprite jalan asli (desain karakter tidak diganti, hanya lengan/kaki/kepala diubah).
Output: characters/<c>/poses.png, 8 kolom (4 arah x 2 frame) x len(POSES) baris, sel 48x72.
Pemakaian: python3 gen_poses.py <assets>"""
import os, sys
from PIL import Image, ImageDraw

POSES = ['sit', 'wave', 'give', 'reach', 'bow', 'hold_l', 'hold_r', 'cheer', 'hug', 'lean', 'photo', 'highfive', 'dance', 'read', 'water', 'sweep']
FW, FH = 48, 72
D, L, R, U = 0, 1, 2, 3
OL = (44, 34, 46, 255)
GIFT, RIB = (236, 136, 168, 255), (255, 226, 140, 255)

def frame(sheet, d, f=0): return sheet.crop((f * FW, d * FH, f * FW + FW, d * FH + FH))

def opaque(im, x, y):
    return 0 <= x < im.width and 0 <= y < im.height and im.getpixel((x, y))[3] > 40

def colors(sheet):
    f = frame(sheet, D)
    bb = f.getbbox(); cx = (bb[0] + bb[2]) // 2
    def pick(x, y):
        best = None
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                p = f.getpixel((x + dx, y + dy))
                if p[3] > 200 and sum(p[:3]) > 120: best = p; break
            if best: break
        return best or (200, 200, 200, 255)
    # baris kulit: cari baris wajah (lebih terang & kemerahan) di sepertiga atas-tengah
    skin = (238, 200, 176, 255)
    for y in range(int(FH * 0.32), int(FH * 0.55)):
        p = f.getpixel((cx, y))
        if p[3] > 200 and p[0] > 200 and p[0] > p[2] + 25: skin = p; break
    sleeve = pick(cx - 9, int(FH * 0.66))
    pants = pick(cx - 5, int(FH * 0.86))
    return skin, sleeve, pants

def extents(im, y):
    xs = [x for x in range(im.width) if opaque(im, x, y)]
    return (xs[0], xs[-1]) if xs else (None, None)

def erase_arm(im, side):
    """hapus lengan yang menggantung di sisi kiri/kanan (tampak depan/belakang)."""
    y0, y1 = int(FH * 0.58), int(FH * 0.84)
    # tepi torso = median tepi pada baris tengah lengan dikurangi lebar lengan
    for y in range(y0, y1):
        l, r = extents(im, y)
        if l is None: continue
        if side == 'r':
            for x in range(r - 5, r + 1): im.putpixel((x, y), (0, 0, 0, 0))
            if opaque(im, r - 6, y): im.putpixel((r - 6, y), OL)
        else:
            for x in range(l, l + 6): im.putpixel((x, y), (0, 0, 0, 0))
            if opaque(im, l + 6, y): im.putpixel((l + 6, y), OL)

def arm(dr, pts, sleeve, skin, hand=True, w=5):
    dr.line(pts, fill=OL, width=w + 2, joint='curve')
    dr.line(pts, fill=sleeve, width=w, joint='curve')
    if hand:
        x, y = pts[-1]
        dr.ellipse((x - 3, y - 3, x + 3, y + 3), fill=skin, outline=OL)

def gift(dr, x, y):
    dr.rectangle((x - 5, y - 5, x + 5, y + 4), fill=GIFT, outline=OL)
    dr.line((x, y - 5, x, y + 4), fill=RIB); dr.line((x - 5, y - 1, x + 5, y - 1), fill=RIB)
    dr.line((x - 3, y - 8, x, y - 5), fill=RIB); dr.line((x + 3, y - 8, x, y - 5), fill=RIB)

def mirror(im): return im.transpose(Image.FLIP_LEFT_RIGHT)

def make(sheet):
    skin, sleeve, pants = colors(sheet)
    base = {d: frame(sheet, d) for d in (D, L, R, U)}
    bb = base[D].getbbox(); top = bb[1]
    sh_y = int(FH * 0.62)  # tinggi bahu
    out = {}

    # --- sit
    fr = {}
    for d in (D, L, R, U):
        src = base[d]; im = Image.new('RGBA', (FW, FH)); cut = int(FH * 0.80)
        im.alpha_composite(src.crop((0, 0, FW, cut)), (0, 8))
        dr = ImageDraw.Draw(im)
        b = src.getbbox(); cx = (b[0] + b[2]) // 2
        if d == D:
            for lx in (cx - 7, cx + 2):
                dr.rectangle((lx, cut + 6, lx + 5, FH - 3), fill=pants, outline=OL)
                dr.rectangle((lx, FH - 4, lx + 5, FH - 1), fill=OL)
        elif d in (L, R):
            sgn = 1 if d == R else -1
            x0, x1 = (cx, cx + 14) if d == R else (cx - 14, cx)
            dr.rectangle((x0, cut + 2, x1, cut + 8), fill=pants, outline=OL)
            fx = x1 if d == R else x0
            dr.rectangle((fx - 2, cut + 3, fx + 2, cut + 12), fill=OL)
        fr[d] = [im, im]
    out['sit'] = fr

    # --- wave (lengan kanan layar terangkat, dua frame melambai)
    fr = {}
    for d in (D, U, R):
        im = base[d].copy()
        l, r = extents(im, sh_y)
        frames = []
        if d in (D, U):
            erase_arm(im, 'r'); sx = r - 6
            for k, (hx, hy) in enumerate([(sx + 9, top + 18), (sx + 11, top + 21)]):
                f2 = im.copy(); dr = ImageDraw.Draw(f2)
                arm(dr, [(sx, sh_y), (sx + 6, sh_y - 9), (hx, hy)], sleeve, skin); frames.append(f2)
        else:
            sx = (l + r) // 2
            for k in range(2):
                f2 = im.copy(); dr = ImageDraw.Draw(f2)
                arm(dr, [(sx, sh_y), (r + 3, sh_y - 5), (r + 6 + k, top + 30 - k * 3)], sleeve, skin); frames.append(f2)
        fr[d] = frames
    fr[L] = [mirror(x) for x in fr[R]]
    out['wave'] = fr

    # --- give / reach (lengan ke depan)
    for name, with_gift in (('give', True), ('reach', False)):
        fr = {}
        im = base[R].copy(); l, r = extents(im, sh_y); sx = (l + r) // 2
        frames = []
        for k in range(2):
            f2 = im.copy(); dr = ImageDraw.Draw(f2)
            ex = r + 5 + k
            arm(dr, [(sx, sh_y - 1), (ex, sh_y + 1)], sleeve, skin)
            if with_gift: gift(dr, ex + 4, sh_y)
            frames.append(f2)
        fr[R] = frames; fr[L] = [mirror(x) for x in frames]
        im = base[D].copy(); erase_arm(im, 'l'); erase_arm(im, 'r')
        l, r = extents(im, sh_y); cx = (l + r) // 2
        f2 = im.copy(); dr = ImageDraw.Draw(f2)
        arm(dr, [(l + 1, sh_y), (cx - 4, sh_y + 6)], sleeve, skin, w=4); arm(dr, [(r - 1, sh_y), (cx + 4, sh_y + 6)], sleeve, skin, w=4)
        if with_gift: gift(dr, cx, sh_y + 3)
        fr[D] = [f2, f2]
        fr[U] = [base[U], base[U]]
        out[name] = fr

    # --- bow / sedih (kepala menunduk)
    fr = {}
    for d in (D, L, R, U):
        src = base[d]; im = Image.new('RGBA', (FW, FH))
        neck = int(FH * 0.56)
        im.alpha_composite(src.crop((0, neck, FW, FH)), (0, neck))
        im.alpha_composite(src.crop((0, 0, FW, neck)), (1 if d == R else -1 if d == L else 0, 3))
        fr[d] = [im, im]
    out['bow'] = fr

    # --- gandengan: tampak depan, lengan ke sisi kiri / kanan layar
    for name, side in (('hold_l', 'l'), ('hold_r', 'r')):
        fr = {}
        im = base[D].copy(); erase_arm(im, side); l, r = extents(im, sh_y)
        f2 = im.copy(); dr = ImageDraw.Draw(f2)
        if side == 'l': arm(dr, [(l + 6, sh_y), (l - 2, sh_y + 12)], sleeve, skin, w=4)
        else: arm(dr, [(r - 6, sh_y), (r + 2, sh_y + 12)], sleeve, skin, w=4)
        fr[D] = [f2, f2]
        for d in (L, R, U): fr[d] = [base[d], base[d]]
        out[name] = fr

    # --- cheer: kedua lengan naik (gembira / kaget)
    fr = {}
    im = base[D].copy(); erase_arm(im, 'l'); erase_arm(im, 'r'); l, r = extents(im, sh_y)
    frames = []
    for k in range(2):
        f2 = im.copy(); dr = ImageDraw.Draw(f2)
        arm(dr, [(l + 6, sh_y), (l - 1, sh_y - 10), (l - 3 - k * 2, top + 16 + k * 2)], sleeve, skin)
        arm(dr, [(r - 6, sh_y), (r + 1, sh_y - 10), (r + 3 + k * 2, top + 16 + k * 2)], sleeve, skin)
        frames.append(f2)
    fr[D] = frames
    for d in (L, R, U): fr[d] = [base[d], base[d]]
    out['cheer'] = fr

    # v2.2: pose berpasangan. Sprite asli tetap sebagai sumber, siluet dan lengan digambar ulang
    # secara prosedural menjadi frame terpisah, bukan sekadar meregangkan gambar saat runtime.
    for name in ('hug', 'lean', 'photo', 'highfive', 'dance'):
        frames = {}
        for d in (D, L, R, U):
            variants = []
            for k in range(2):
                im = base[d].copy()
                dr = ImageDraw.Draw(im)
                l, r = extents(im, sh_y)
                cx = (l + r) // 2
                if name == 'hug':
                    if d in (D, U):
                        erase_arm(im, 'l'); erase_arm(im, 'r')
                        dr = ImageDraw.Draw(im)
                        arm(dr, [(l + 5, sh_y), (cx - 8, sh_y + 5 + k), (cx - 2, sh_y + 6)], sleeve, skin, w=3)
                        arm(dr, [(r - 5, sh_y), (cx + 8, sh_y + 5 + k), (cx + 2, sh_y + 6)], sleeve, skin, w=3)
                    else:
                        sg = -1 if d == L else 1
                        arm(dr, [(cx, sh_y), (cx + sg * (11 + k), sh_y + 5)], sleeve, skin, w=4)
                elif name == 'lean':
                    # Bahu dan kepala sedikit miring. Tangan rileks di depan badan.
                    im = Image.new('RGBA', (FW, FH))
                    neck = int(FH * 0.54)
                    im.alpha_composite(base[d].crop((0, neck, FW, FH)), (0, neck))
                    im.alpha_composite(base[d].crop((0, 0, FW, neck)), ((-2 if d != L else 2) - k, 2 + k))
                elif name == 'photo':
                    sg = -1 if d == L else 1
                    ex, ey = cx + sg * (15 + 2 * k), sh_y - 15 - k
                    arm(dr, [(cx + sg * 6, sh_y), (ex, ey)], sleeve, skin, w=3)
                    # Ponsel kecil di tangan untuk selfie.
                    dr.rectangle((ex-2, ey-8, ex+4, ey+1), fill=(63,60,91,255), outline=OL)
                    dr.rectangle((ex-1, ey-7, ex+3, ey-2), fill=(135,196,217,255))
                elif name == 'highfive':
                    sg = -1 if d == L else 1
                    ex = cx + sg * (14 + k * 2)
                    arm(dr, [(cx + sg*7, sh_y), (ex, sh_y-15-k)], sleeve, skin, w=4)
                elif name == 'dance':
                    arm(dr, [(l + 5, sh_y), (l-2-k, sh_y-14+k)], sleeve, skin, w=4)
                    arm(dr, [(r - 5, sh_y), (r+2+k, sh_y-10-k)], sleeve, skin, w=4)
                    dr.line([(cx - 7, FH - 7), (cx - 9-k*2, FH - 3)], fill=pants, width=4)
                if k == 1:
                    # Frame kedua memiliki gerak vertikal 1px pada SEMUA karakter,
                    # termasuk NPC dengan warna/bentuk lengan sangat pendek.
                    lifted = Image.new('RGBA', (FW, FH))
                    lifted.alpha_composite(im, (0, -1))
                    im = lifted
                variants.append(im)
            frames[d] = variants
        out[name] = frames

    # v2.3: NPC activity poses. These are authored pixels on the existing character style,
    # rather than runtime stretching.  All four directions have two nonidentical frames.
    for name in ('read', 'water', 'sweep'):
        frames = {}
        for d in (D, L, R, U):
            pair = []
            for k in (0, 1):
                im = base[d].copy()
                dr = ImageDraw.Draw(im)
                l, r = extents(im, sh_y)
                cx = (l + r) // 2
                if name == 'read':
                    # A small open book with cream pages and a coloured binding.
                    dr.polygon([(cx-12,sh_y+4+k), (cx-1,sh_y+6+k),
                                (cx,sh_y+19+k), (cx-12,sh_y+17+k)], fill=(242,226,197,255), outline=OL)
                    dr.polygon([(cx,sh_y+6+k),(cx+11,sh_y+3+k),
                                (cx+11,sh_y+17+k),(cx,sh_y+19+k)],fill=(251,241,214,255), outline=OL)
                    dr.line((cx,sh_y+6+k,cx,sh_y+19+k), fill=(168,115,141,255),width=2)
                    dr.line((cx-9,sh_y+9+k,cx-4,sh_y+10+k),fill=(174,156,155,255))
                elif name == 'water':
                    sg = -1 if d == L else 1
                    hx = cx + sg*(13 + k*2)
                    arm(dr,[(cx+sg*5,sh_y),(hx,sh_y+9-k)],sleeve,skin,w=3)
                    dr.polygon([(hx-4,sh_y+9),(hx+5,sh_y+9),(hx+4,sh_y+18),(hx-3,sh_y+18)],
                               fill=(114,180,208,255),outline=OL)
                    dr.line((hx+5,sh_y+12,hx+9,sh_y+10),fill=(183,218,228,255),width=2)
                    dr.point((hx+11,sh_y+18+k),fill=(126,203,232,255))
                else:  # sweep
                    sg = -1 if d == L else 1
                    hx = cx + sg*(10+k*2)
                    dr.line((hx,sh_y-2,hx+sg*5,FH-8), fill=OL,width=5)
                    dr.line((hx,sh_y-2,hx+sg*5,FH-8), fill=(173,130,94,255),width=3)
                    dr.polygon([(hx+sg*1,FH-9),(hx+sg*11,FH-9),(hx+sg*14,FH-3),(hx+sg*1,FH-3)],
                               fill=(211,174,107,255),outline=OL)
                if k == 1:
                    moved = Image.new('RGBA',(FW,FH))
                    moved.alpha_composite(im,(0,-1))
                    im=moved
                pair.append(im)
            frames[d]=pair
        out[name]=frames

    sheet_out = Image.new('RGBA', (FW * 8, FH * len(POSES)))
    for pi, name in enumerate(POSES):
        for d in (D, L, R, U):
            for f in range(2): sheet_out.alpha_composite(out[name][d][f], ((d * 2 + f) * FW, pi * FH))
    return sheet_out

if __name__ == '__main__':
    root = os.path.join(sys.argv[1], 'characters')
    for c in sorted(os.listdir(root)):
        p = os.path.join(root, c, 'walk.png')
        if not os.path.exists(p): continue
        make(Image.open(p).convert('RGBA')).save(os.path.join(root, c, 'poses.png'))
        print('pose', c)
