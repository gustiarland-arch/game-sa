"""Membuat BitmapFont (format BMFont teks .fnt + .png) untuk LibGDX tanpa butuh FreeType di runtime.
Font: Inter (SIL OFL 1.1) + fallback DejaVu Sans untuk simbol yang tidak ada di Inter.
Pemakaian: python3 tools/gen_font.py <out_dir>
Font dirender 2x lebih besar lalu di-skala 0.5 di game agar tajam di layar HP resolusi tinggi.
"""
import sys, os
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
CHARS = ''.join(chr(c) for c in range(32, 127)) + '♡♥✦—–…“”‘’◇◆→←↑↓•éèáàíóúñçÉ×·°ëäöüÀÁ★☆♪‹›▼▲▶◀✓✕✿✉'
FALLBACK = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

def build(name, path, size, stroke=0):
    font = ImageFont.truetype(path, size)
    fb = ImageFont.truetype(FALLBACK, int(size * 0.9))
    cmap = TTFont(path).getBestCmap()
    ascent, descent = font.getmetrics()
    glyphs = []
    for ch in CHARS:
        f = font if ord(ch) in cmap else fb
        x0, y0, x1, y1 = f.getbbox(ch, stroke_width=stroke)
        w, h = max(1, x1 - x0), max(1, y1 - y0)
        adv = int(round(f.getlength(ch))) + stroke
        glyphs.append((ch, f, x0, y0, w, h, adv))
    # packing sederhana per baris
    W = 1024; pad = 2; x = pad; y = pad; rowh = 0; pos = []
    for g in glyphs:
        w, h = g[4], g[5]
        if x + w + pad > W:
            x = pad; y += rowh + pad; rowh = 0
        pos.append((x, y)); x += w + pad; rowh = max(rowh, h)
    H = 1
    while H < y + rowh + pad: H *= 2
    img = Image.new('RGBA', (W, H), (255, 255, 255, 0))
    d = ImageDraw.Draw(img)
    lines = []
    for (ch, f, x0, y0, w, h, adv), (px, py) in zip(glyphs, pos):
        if ch != ' ':
            if stroke:
                d.text((px - x0, py - y0), ch, font=f, fill=(255, 255, 255, 255),
                       stroke_width=stroke, stroke_fill=(38, 30, 52, 255))
            else:
                d.text((px - x0, py - y0), ch, font=f, fill=(255, 255, 255, 255))
        lines.append(f'char id={ord(ch)} x={px} y={py} width={w if ch != " " else 0} height={h if ch != " " else 0} '
                     f'xoffset={x0} yoffset={y0} xadvance={adv} page=0 chnl=15')
    img.save(os.path.join(OUT, name + '.png'))
    with open(os.path.join(OUT, name + '.fnt'), 'w', encoding='utf-8') as fh:
        fh.write(f'info face="{name}" size={size} bold=0 italic=0 charset="" unicode=1 stretchH=100 smooth=1 aa=1 padding=0,0,0,0 spacing=1,1\n')
        fh.write(f'common lineHeight={ascent + descent + stroke * 2} base={ascent + stroke} scaleW={W} scaleH={H} pages=1 packed=0\n')
        fh.write(f'page id=0 file="{name}.png"\n')
        fh.write(f'chars count={len(lines)}\n')
        fh.write('\n'.join(lines) + '\n')
    print(name, W, H, len(lines))

INTER = '/usr/share/fonts/opentype/inter/'
build('font_body', INTER + 'Inter-SemiBold.otf', 46)
build('font_title', INTER + 'Inter-ExtraBold.otf', 92)
build('font_label', INTER + 'Inter-Bold.otf', 40, stroke=4)
