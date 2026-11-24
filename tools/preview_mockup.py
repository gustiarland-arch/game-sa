"""Mockup pratinjau layar bermain (BUKAN screenshot APK): merender peta, props, karakter, HUD, kontrol,
dan kotak dialog memakai koordinat & skala yang sama dengan GameScreen (dunia 640x360, UI 1280x720).
Pemakaian: python3 tools/preview_mockup.py <android/assets> <out.png>
"""
import sys, os, json
from PIL import Image, ImageDraw, ImageFont

A, OUT = sys.argv[1], sys.argv[2]
J = lambda p: json.load(open(os.path.join(A, 'data', p), encoding='utf-8'))
maps, props, story = J('maps.json')['areas'], J('props.json')['props'], J('story.json')
F = lambda sz, w='SemiBold': ImageFont.truetype(f'/usr/share/fonts/opentype/inter/Inter-{w}.otf', sz)
SYM = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 18)
img = lambda p: Image.open(os.path.join(A, p)).convert('RGBA')

area = maps['plaza']; px, py = 1010, 640
player = ('arland', 2, px, py); partner = ('sofia', 1, 1090, 600)
WW, WH = 640, 360
cx = min(max(px, WW / 2), area['w'] - WW / 2); cyMap = min(max(py - 24, WH / 2), area['h'] - WH / 2)
left, top = int(cx - WW / 2), int(cyMap - WH / 2)
world = img(area['image']).copy()
draw_list = []
for p in area['props']:
    d = props[p['type']]; draw_list.append((p['y'], 'prop', p))
for ch in (player, partner): draw_list.append((ch[3], 'actor', ch))
shadow = img('ui/shadow.png').resize((26, 10))
for _, kind, o in sorted(draw_list, key=lambda t: t[0]):
    if kind == 'prop':
        t = img(props[o['type']]['image']); world.alpha_composite(t, (int(o['x'] - t.width / 2), int(o['y'] - t.height)))
    else:
        c, dr, x, y = o
        sheet = img(f'characters/{c}/walk.png'); fr = sheet.crop((0, dr * 72, 48, dr * 72 + 72))
        fr = fr.resize((41, 61), Image.NEAREST)
        world.alpha_composite(shadow, (int(x - 13), int(y - 5)))
        world.alpha_composite(fr, (int(x - 20), int(y - 61 + 1)))
mk = img('ui/marker.png'); tinted = Image.new('RGBA', mk.size, (247, 179, 212, 255)); tinted.putalpha(mk.getchannel('A'))
world.alpha_composite(tinted, (1090 - 7, int(600 - 61 - 22)))
em = img('ui/emote_note.png'); world.alpha_composite(em, (px - 11, int(py - 61 - 26)))
view = world.crop((left, top, left + WW, top + WH)).resize((1280, 720), Image.NEAREST)
d = ImageDraw.Draw(view, 'RGBA')

def panel(x, y, w, h, dark=True):
    d.rounded_rectangle([x, y, x + w, y + h], 14, fill=(44, 34, 60, 230) if dark else (251, 243, 238, 248), outline=(196, 184, 220, 200) if dark else (88, 70, 108, 255), width=3)
# HUD (koordinat gambar: y ke bawah)
panel(16, 16, 330, 88); d.text((38, 26), 'Plaza Kota', font=F(24), fill=(251, 243, 238))
d.text((38, 64), 'ARLAND ROUTE • PROLOG', font=F(16), fill=(155, 138, 184))
panel(375, 16, 530, 88); d.text((640, 30), '✦ MISI AKTIF', font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 15), fill=(232, 156, 180), anchor='mt')
d.text((640, 58), 'Temui Sofia di plaza', font=F(21), fill=(251, 243, 238), anchor='mt')
panel(1026, 16, 150, 66, False); d.text((1101, 49), '♥ Buku', font=SYM, fill=(59, 48, 73), anchor='mm')
panel(1188, 16, 76, 66, False); d.text((1226, 49), 'II', font=F(22), fill=(59, 48, 73), anchor='mm')
hud_only = view.copy()
# kontrol
d.ellipse([70, 720 - 46 - 216, 70 + 216, 720 - 46], fill=(44, 34, 60, 100), outline=(255, 255, 255, 120), width=4)
d.ellipse([178 - 46, 720 - 154 - 46, 178 + 46, 720 - 154 + 46], fill=(251, 243, 238, 230), outline=(88, 70, 108), width=4)
ax, ay = 1280 - 60 - 78, 720 - 60 - 78
d.ellipse([ax - 78, ay - 78, ax + 78, ay + 78], fill=(232, 156, 180, 235), outline=(88, 70, 108), width=5)
d.text((ax, ay - 8), '♥', font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 44), fill='white', anchor='mm')
d.text((ax, ay + 40), 'AKSI', font=F(15), fill='white', anchor='mm')
sx, sy = ax - 78 - 54 - 34, 720 - 40 - 54
d.ellipse([sx - 54, sy - 54, sx + 54, sy + 54], fill=(251, 243, 238, 220), outline=(88, 70, 108), width=4)
d.text((sx, sy), 'LARI', font=F(17), fill=(59, 48, 73), anchor='mm')
panel(ax - 110, ay - 78 - 64, 220, 52); d.text((ax, ay - 78 - 38), '✦ Sapa Sofia', font=SYM, fill=(251, 243, 238), anchor='mm')
view.save(OUT.replace('.png', '_explore.png'))

# varian dengan dialog
dv = hud_only; d = ImageDraw.Draw(dv, 'RGBA')
x, y, w, h = 24, 720 - 18 - 212, 1232, 212
d.rounded_rectangle([x, y, x + w, y + h], 14, fill=(251, 243, 238, 248), outline=(88, 70, 108, 255), width=3)
por = img('characters/arland/portraits/senang.png'); ph = h - 32; pw = int(ph * por.width / por.height)
d.rounded_rectangle([x + 14, y + 10, x + 26 + pw, y + h - 10], 12, fill=(251, 243, 238), outline=(88, 70, 108), width=3)
dv.alpha_composite(por.resize((pw, ph), Image.LANCZOS), (x + 20, y + 16))
tx = x + 20 + pw + 28
d.rectangle([tx - 6, y - 26, tx - 6 + 150, y + 14], fill=(155, 138, 184))
d.text((tx + 69, y - 6), 'Arland', font=F(21), fill='white', anchor='mm')
line = story['scenes']['P-X01']['lines'][0]['t']
d.text((tx, y + 40), line, font=F(24), fill=(59, 48, 73))
d.text((x + w - 52, y + h - 60), '▼', font=SYM, fill=(196, 86, 126))
d.rounded_rectangle([x + w - 150, y - 52, x + w - 10, y - 6], 14, fill=(255, 250, 247), outline=(88, 70, 108), width=3)
d.text((x + w - 80, y - 29), 'Lewati ▶', font=SYM, fill=(59, 48, 73), anchor='mm')
dv.save(OUT.replace('.png', '_dialog.png'))
print('ok')
