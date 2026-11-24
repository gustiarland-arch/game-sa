"""Sprite sheet NPC (48x72 per frame, 3 kolom x 4 baris) dari sprite Arland/Sofia dengan ganti palet,
agar gaya pixel art NPC konsisten dengan tokoh utama. Lumi dibuat prosedural.
Pemakaian: python3 tools/gen_npcs.py <android/assets>
"""
import sys, os, colorsys, math
from PIL import Image, ImageDraw

A = sys.argv[1]
src = {c: Image.open(os.path.join(A, 'characters', c, 'walk.png')).convert('RGBA') for c in ('arland', 'sofia')}

def hexc(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def recolor(img, rule, target, light_bias=1.0, min_row=0):
    out = img.copy(); px = out.load(); tr, tg, tb = hexc(target)
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = px[x, y]
            if a < 10 or (y % 72) < min_row: continue
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if rule(h, s, v):
                k = min(1.25, (v / 0.9) * light_bias)
                px[x, y] = (min(255, int(tr * k)), min(255, int(tg * k)), min(255, int(tb * k)), a)
    return out

white = lambda h, s, v: s < 0.16 and v > 0.72
grey = lambda h, s, v: s < 0.2 and 0.42 < v <= 0.86

def shrink(img, k):
    out = Image.new('RGBA', img.size, (0, 0, 0, 0))
    for r in range(4):
        for c in range(3):
            cell = img.crop((c * 48, r * 72, c * 48 + 48, r * 72 + 72))
            bb = cell.getbbox()
            if not bb: continue
            spr = cell.crop(bb); spr = spr.resize((max(1, int(spr.width * k)), max(1, int(spr.height * k))), Image.NEAREST)
            out.alpha_composite(spr, (c * 48 + (48 - spr.width) // 2, r * 72 + 72 - spr.height - 1))
    return out

def save(name, img):
    d = os.path.join(A, 'characters', name); os.makedirs(d, exist_ok=True); img.save(os.path.join(d, 'walk.png'))

save('raka', recolor(src['arland'], white, '#c9935f', 1.0, 36))
save('juna', recolor(src['arland'], white, '#5f8fd8', 1.05, 36))
save('dito', shrink(recolor(src['arland'], white, '#ffd24a', 1.0, 36), 0.78))
save('pos', recolor(src['arland'], white, '#e8833a', 1.0, 36))
save('udin', shrink(recolor(src['arland'], white, '#8a9a5a', 0.95, 36), 0.96))
save('melati', recolor(src['sofia'], grey, '#7fb88f', 1.05))
save('laras', recolor(src['sofia'], grey, '#5fa8a8', 1.0))
save('bayu', recolor(src['arland'], white, '#4f7fa0', 0.95, 36))
save('nara', recolor(src['sofia'], grey, '#3f4f8a', 1.0))
save('sari', shrink(recolor(src['sofia'], grey, '#efe6da', 1.12), 0.92))

def hair(img, target, rows=(2, 22)):
    """ganti warna rambut gelap Arland (baris kepala saja) agar warga tidak terlihat kembar."""
    out = img.copy(); px = out.load(); tr, tg, tb = hexc(target)
    for y in range(out.height):
        if not (rows[0] <= y % 72 < rows[1]): continue
        for x in range(out.width):
            r, g, b, a = px[x, y]
            if a < 10: continue
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if v < 0.36 and s < 0.6:
                k = 0.55 + v * 1.6
                px[x, y] = (min(255, int(tr * k)), min(255, int(tg * k)), min(255, int(tb * k)), a)
    return out

# warga tambahan v1.4
save('rini', recolor(src['sofia'], grey, '#8a5a3c', 1.05))
save('harun', shrink(hair(recolor(src['arland'], white, '#6b8f3a', 0.95, 36), '#9a9a9a'), 0.98))
save('tika', shrink(recolor(src['sofia'], grey, '#f08aa8', 1.05), 0.78))
save('eko', hair(recolor(src['arland'], white, '#d84a4a', 1.0, 36), '#6a4428'))
save('wulan', recolor(src['sofia'], grey, '#c8a060', 1.0))
save('darmo', shrink(hair(recolor(src['arland'], white, '#7a8aa0', 0.95, 36), '#d8d8d8'), 0.93))

save('darto', hair(recolor(src['arland'], white, '#3a4a6a', 0.9, 36), '#2a2a2a'))
save('rara', shrink(recolor(src['sofia'], grey, '#6a8ad8', 1.05), 0.86))
save('bimo', shrink(hair(recolor(src['arland'], white, '#f0f0f0', 1.0, 36), '#3a2a20'), 0.86))
save('ujang', hair(recolor(src['arland'], white, '#e0b040', 1.0, 36), '#5a3a20'))
save('ina', shrink(recolor(src['sofia'], grey, '#b07ab0', 1.08), 0.9))
save('tigor', hair(recolor(src['arland'], white, '#2f8a5a', 0.95, 36), '#1a1a1a'))

# Lumi: roh lentera kecil melayang
lumi = Image.new('RGBA', (144, 288), (0, 0, 0, 0))
for r in range(4):
    for c in range(3):
        cell = Image.new('RGBA', (48, 72), (0, 0, 0, 0)); d = ImageDraw.Draw(cell)
        cy = 40 - c  # sedikit naik-turun antar frame
        for k, a in [(20, 40), (15, 80)]: d.ellipse([24 - k, cy - k, 24 + k, cy + k], fill=(255, 230, 160, a))
        d.ellipse([13, cy - 11, 35, cy + 11], fill=(58, 44, 64, 255)); d.ellipse([14, cy - 10, 34, cy + 10], fill=(255, 236, 170, 255))
        d.polygon([(18, cy - 8), (24, cy - 24 - c), (30, cy - 8)], fill=(255, 200, 120, 255), outline=(58, 44, 64, 255))
        d.ellipse([20, cy - 7, 28, cy + 1], fill=(255, 250, 230, 255))
        if r != 3:
            ox = {0: 0, 1: -3, 2: 3}[r]
            d.point([(20 + ox, cy + 1), (21 + ox, cy + 1), (27 + ox, cy + 1), (28 + ox, cy + 1)], fill=(58, 44, 64, 255))
            d.arc([21 + ox, cy + 2, 27 + ox, cy + 7], 20, 160, fill=(196, 86, 126, 255))
        for i in range(4):
            a_ = i / 4 * math.pi * 2 + c; d.point([(24 + int(math.cos(a_) * 18), cy + int(math.sin(a_) * 14))], fill=(255, 255, 255, 220))
        lumi.alpha_composite(cell, (c * 48, r * 72))
save('lumi', lumi)
print('npc ok')
