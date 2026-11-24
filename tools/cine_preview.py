"""Pratinjau cutscene: membaca aksi 'cine' dari quests.json dan merendernya ke MP4 dengan aset asli.
Meniru semantik CutscenePlayer.java (berurutan, async, kamera tween, pose, fx sederhana, letterbox, caption, fade).
Ini alat bantu penulis cutscene, bukan engine game.
Pemakaian: python3 cine_preview.py <assets> <out.mp4> <route> <step_id>[:<idx>] [...]
  idx = indeks aksi cine di daftar aksi interaksi pertama / enter / complete / onStart step itu."""
import sys, os, json, math, subprocess
from PIL import Image, ImageDraw, ImageFont

A, OUT, ROUTE = sys.argv[1], sys.argv[2], sys.argv[3]
SPECS = sys.argv[4:]
W, H, FPS, Z = 1280, 720, 30, 2
Q = json.load(open(os.path.join(A, 'data', 'quests.json')))
MAPS = json.load(open(os.path.join(A, 'data', 'maps.json')))['areas']
PROPS = json.load(open(os.path.join(A, 'data', 'props.json')))['props']
STORY = json.load(open(os.path.join(A, 'data', 'story.json')))
PARTNER = 'sofia' if ROUTE == 'arland' else 'arland'
FD = '/usr/share/fonts/opentype/inter/'
def F(sz, w='Regular'): return ImageFont.truetype(FD + 'Inter-%s.otf' % w, sz)
f_body, f_name, f_title, f_small = F(27), F(25, 'Bold'), F(50, 'Bold'), F(24, 'SemiBold')
INK, CREAM, GOLD = (59, 48, 73), (251, 243, 238), (255, 214, 120)
POSES = ['sit', 'wave', 'give', 'reach', 'bow', 'hold_l', 'hold_r', 'cheer']
_c = {}
def img(p):
    if p not in _c: _c[p] = Image.open(os.path.join(A, p)).convert('RGBA')
    return _c[p]
def res(s):
    if not isinstance(s, str): return s
    return s.replace('$ROOM', ROUTE + '_room').replace('$PARTNER', PARTNER).replace('$ROUTE', ROUTE)

class Actor:
    def __init__(s, ch, x, y, d=0): s.ch, s.x, s.y, s.dir, s.walk, s.anim, s.pose, s.pt, s.pdur, s.emote, s.et, s.vis = ch, x, y, d, False, 0, None, 0, 0, None, 0, True
    def frame(s):
        pi = POSES.index(s.pose) if s.pose in POSES else -1
        lift = 0
        if pi >= 0:
            f = int(s.pt * 5) & 1 if s.pose in ('wave', 'cheer') else 0
            im = img('characters/%s/poses.png' % s.ch).crop(((s.dir * 2 + f) * 48, pi * 72, (s.dir * 2 + f) * 48 + 48, pi * 72 + 72))
        else:
            f = [1, 0, 2, 0][int(s.anim) % 4] if s.walk else 0
            im = img('characters/%s/walk.png' % s.ch).crop((f * 48, s.dir * 72, f * 48 + 48, s.dir * 72 + 72))
            if s.pose == 'surprised' and s.pt < 0.35: lift = math.sin(s.pt / 0.35 * math.pi) * 7
            if s.pose == 'laugh': lift = abs(math.sin(s.pt * 12)) * 2.5
        return im.resize((41, 61), Image.NEAREST), lift

def dirof(s): return {'left': 1, 'right': 2, 'up': 3}.get(s, 0)
def face(a, dx, dy):
    if abs(dx) > abs(dy): a.dir = 1 if dx < 0 else 2
    elif dy: a.dir = 3 if dy < 0 else 0

def find_cines(step, idx):
    out = []
    s = next(x for x in Q['steps'] if x['id'] == step)
    npc = next(((n['x'], n['y'], dirof(n['dir'])) for n in s.get('npcs', [])), None)
    def walk(acts, area, start):
        for ac in acts:
            if ac.get('route') not in (None, ROUTE): continue
            if ac.get('do') == 'warp': area = res(ac['area']); start = (ac['x'], ac['y'])
            if ac.get('do') == 'cine': out.append((ac, area, start, npc))
            if ac.get('do') == 'if': walk(ac['then'], area, start)
    walk(s.get('onStart', []), s.get('startArea') and res(s['startArea']), None)
    if 'enterArea' in s: walk(s['enterArea']['actions'], res(s['enterArea']['area']), None)
    for it in s.get('interactables', []):
        if it.get('route') in (None, ROUTE): walk(it['actions'], res(it['area']), (it['x'] - 46, it['y'] + 12))
    return out if idx is None else [out[idx]]

def wrap(t, font, mw):
    out, cur = [], ''
    for w in t.split():
        x = (cur + ' ' + w).strip()
        if font.getlength(x) > mw and cur: out.append(cur); cur = w
        else: cur = x
    return out + ([cur] if cur else [])

class Player:
    def __init__(s, area, start):
        s.area = area; m = MAPS[area]; s.m = m
        s.bg = img(m['image']).copy(); s.sort = []
        for p in m['props']:
            d = PROPS[p['type']]; im = img(d['image'])
            if d.get('layer') == 'floor': s.bg.alpha_composite(im, (int(p['x'] - im.width / 2), int(p['y'] - im.height)))
            else: s.sort.append((p['y'], im, int(p['x'] - im.width / 2), int(p['y'] - im.height)))
        s.actors = {'player': Actor(ROUTE, *start), 'partner': Actor(PARTNER, start[0] + 34, start[1] + 4)}
        s.actors['partner'].vis = False
        for n in Q.get('townNpcs', []):
            if n['area'] == area: s.actors[n['id']] = Actor(n['sprite'], n['x'], n['y'], dirof(n.get('dir')))
        s.cam = [start[0], start[1] - 24, 1.0]; s.bars = 0; s.btarget = 0; s.fade = 0; s.fadec = (0, 0, 0); s.flash = 0; s.fx = []; s.cap = None; s.t = 0
    def actor(s, w):
        if w in ('player', ROUTE): return s.actors['player']
        if w in ('partner', PARTNER): s.actors['partner'].vis = True; return s.actors['partner']
        return s.actors.get(w)
    def render(s, dlg=None):
        cx, cy, z = s.cam; vw, vh = W / (Z * z), H / (Z * z)
        x0 = max(0, min(s.m['w'] - vw, cx - vw / 2)) if s.m['w'] > vw else (s.m['w'] - vw) / 2
        y0 = max(0, min(s.m['h'] - vh, cy - vh / 2)) if s.m['h'] > vh else (s.m['h'] - vh) / 2
        fr = Image.new('RGBA', (int(vw) + 2, int(vh) + 2), (20, 16, 30, 255))
        fr.alpha_composite(s.bg.crop((int(x0), int(y0), int(x0 + vw) + 2, int(y0 + vh) + 2)) if x0 >= 0 and y0 >= 0 else s.bg, (0, 0) if x0 >= 0 and y0 >= 0 else (int(-x0), int(-y0)))
        items = list(s.sort)
        sh = img('ui/shadow.png').resize((26, 9))
        for a in s.actors.values():
            if not a.vis: continue
            im, lift = a.frame()
            fr.alpha_composite(sh, (int(a.x - 13 - x0), int(a.y - 4 - y0)))
            items.append((a.y, im, int(a.x - 20), int(a.y - 61 + 4 - lift)))
        for y, im, x, top in sorted(items, key=lambda i: i[0]):
            px, py = x - int(x0), top - int(y0)
            if px > fr.width or py > fr.height or px + im.width < 0 or py + im.height < 0: continue
            fr.alpha_composite(im, (px, py))
        dr = ImageDraw.Draw(fr)
        for f in s.fx:
            k = f['t'] / f['dur']; al = max(0, min(1, (f['dur'] - f['t']) * 2, f['t'] * 3))
            gx, gy = f['x'] - x0, f['y'] - y0
            col = (255, 235, 180, int(200 * al))
            if f['kind'] in ('glow', 'book'):
                r = 40 + math.sin(s.t * 3) * 5; g = Image.new('RGBA', fr.size); ImageDraw.Draw(g).ellipse((gx - r, gy - r - 10, gx + r, gy + r - 10), fill=(255, 225, 160, int(90 * al))); fr.alpha_composite(g)
                if f['kind'] == 'book':
                    bk = img('props/glowing_book.png'); fr.alpha_composite(bk, (int(gx - bk.width / 2), int(gy - bk.height - min(1, k * 2) * 30)))
            elif f['kind'] == 'portal':
                rad = 6 + min(1, k * 1.6) * 46
                for i in range(36):
                    an = i / 36 * 6.283 + s.t * 2.2
                    dr.ellipse((gx + math.cos(an) * rad - 3, gy - 30 + math.sin(an) * rad * 1.2 - 3, gx + math.cos(an) * rad + 3, gy - 30 + math.sin(an) * rad * 1.2 + 3), fill=(220, 210, 255, int(255 * al)))
            elif f['kind'] in ('sparkles', 'restore'):
                for i in range(f.get('n', 24)):
                    an = i * 2.4; r = (8 + k * (40 + (i % 5) * 12)) if f['kind'] == 'sparkles' else k * 400
                    dr.ellipse((gx + math.cos(an) * r - 2, gy + math.sin(an) * r * 0.8 - 2, gx + math.cos(an) * r + 2, gy + math.sin(an) * r * 0.8 + 2), fill=col)
            elif f['kind'] == 'hearts':
                h = img('ui/emote_heart.png')
                for i in range(6):
                    tt = (f['t'] * 0.6 + i * 0.37) % 1
                    fr.alpha_composite(h.resize((14, 14)), (int(gx + math.sin(i * 1.7 + f['t'] * 2) * 18 - 7), int(gy - 50 - tt * 50)))
            elif f['kind'] == 'beam':
                if gy > 0: dr.rectangle((gx - 12, 0, gx + 12, gy), fill=(255, 245, 210, int(80 * al)))
        for a in s.actors.values():
            if a.vis and a.emote:
                e = img('ui/emote_%s.png' % a.emote); fr.alpha_composite(e, (int(a.x - 11 - x0), int(a.y - 61 - 26 - y0)))
        fr = fr.crop((0, 0, int(vw), int(vh))).resize((W, H), Image.NEAREST)
        dr = ImageDraw.Draw(fr)
        if s.bars > 0: bh = int(H * 0.11 * s.bars); dr.rectangle((0, 0, W, bh), fill=INK); dr.rectangle((0, H - bh, W, H), fill=INK)
        if s.cap:
            t_, sub, ct, cd = s.cap[:4]; al = int(255 * max(0, min(1, ct * 2, (cd - ct) * 2)))
            dr.text(((W - f_title.getlength(t_)) / 2, H / 2 - 70), t_, font=f_title, fill=CREAM + (al,))
            if sub: dr.text(((W - f_small.getlength(sub)) / 2, H / 2 + 0), sub, font=f_small, fill=GOLD + (al,))
        if dlg:
            sp, e, txt, shown = dlg
            por = None
            if sp in ('arland', 'sofia'):
                p = os.path.join(A, 'characters/%s/portraits/%s.png' % (sp, {'senyum': 'senang'}.get(e, e)))
                por = img(p[len(A) + 1:]) if os.path.exists(p) else img('characters/%s/portraits/normal.png' % sp)
            if por: ph = 210; fr.alpha_composite(por.resize((int(por.width * ph / por.height), ph)), (50, H - 200 - ph + 30))
            dr.rounded_rectangle((40, H - 190, W - 40, H - 30), 20, fill=CREAM + (245,), outline=INK, width=4)
            tx = 290 if por else 80
            if sp != 'narrator':
                nm = STORY['speakers'].get(sp, {}).get('name', sp); nw = f_name.getlength(nm) + 36
                dr.rounded_rectangle((tx - 10, H - 212, tx - 10 + nw, H - 170), 12, fill=(155, 138, 184), outline=INK, width=3); dr.text((tx + 8, H - 206), nm, font=f_name, fill=CREAM)
            for i, ln in enumerate(wrap(txt[:shown], f_body, W - tx - 90)[:3]): dr.text((tx, H - 150 + i * 36), ln, font=f_body, fill=INK if sp != 'narrator' else (100, 84, 120))
        if s.fade > 0: fr = Image.blend(fr, Image.new('RGBA', fr.size, s.fadec + (255,)), s.fade)
        if s.flash > 0: fr = Image.blend(fr, Image.new('RGBA', fr.size, (255, 255, 255, 255)), min(1, s.flash))
        return fr

def run(cmds, P, sink):
    dt = 1 / FPS
    q = [c for c in cmds if c.get('route') in (None, ROUTE)]
    movers = {}; wait = 0; wmover = None; camtw = None; fadetw = None; dlg = None
    def hex2(h): return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    while True:
        # pump
        while not dlg and wait <= 0 and wmover is None and not (camtw and not camtw[-1]) and not (fadetw and not fadetw[-1]) and not (P.cap and not P.cap[4]):
            if not q: return
            c = q.pop(0); k = c['c']; asy = c.get('async', False)
            a = P.actor(c.get('who', 'player')) if 'who' in c or k in ('move', 'place', 'face', 'pose', 'emote') else None
            if k == 'wait': wait = c.get('t', 0.5)
            elif k == 'move':
                pts = ([c['to']] if c.get('to') else []) + c.get('path', [])
                movers[id(a)] = [a, pts, c.get('speed', 150 if c.get('run') else 78), dirof(c['dir']) if 'dir' in c else None]; a.pose = None
                if not asy: wmover = id(a)
            elif k == 'place': a.x, a.y = c['x'], c['y']; a.vis = True; a.dir = dirof(c.get('dir')) if 'dir' in c else a.dir
            elif k == 'face':
                if 'at' in c: o = P.actor(c['at']); face(a, o.x - a.x, o.y - a.y)
                else: a.dir = dirof(c.get('dir'))
            elif k == 'pose':
                a.pose = None if c.get('pose') in (None, 'none') else c['pose']; a.pt = 0; a.pdur = c.get('t', 0)
                if c.get('block'): wait = c.get('t', 0.6)
            elif k == 'emote': a.emote = c.get('e', 'heart'); a.et = c.get('t', 1.8)
            elif k == 'cam':
                on = P.actor(c['on']) if 'on' in c else None
                tgt = [on.x, on.y - 24] if on else [c.get('x', P.cam[0]), c.get('y', P.cam[1])]
                z1 = c.get('zoom', P.cam[2]); t = c.get('t', 1)
                if t <= 0: P.cam = [tgt[0], tgt[1], z1]
                else: camtw = [list(P.cam), [tgt[0], tgt[1], z1], 0, t, asy]
            elif k == 'bars': P.btarget = 1 if c.get('on', True) else 0
            elif k == 'fade':
                P.fadec = hex2(c.get('color', '000000')); t = c.get('t', 0.6)
                if t <= 0: P.fade = c.get('to', 1)
                else: fadetw = [P.fade, c.get('to', 1), 0, t, asy]
            elif k == 'flash': P.flash = 1
            elif k == 'fx':
                on = P.actor(c['on']) if 'on' in c else None
                P.fx.append({'kind': c.get('kind'), 'x': on.x if on else c.get('x'), 'y': on.y - 30 if on else c.get('y'), 't': 0, 'dur': c.get('t', 2), 'n': c.get('n', 24)})
                if c.get('block'): wait = c.get('t', 2)
            elif k == 'caption': P.cap = [c.get('text'), c.get('sub'), 0, c.get('t', 2.6), asy]
            elif k == 'say':
                sc = STORY['scenes'][res(c['scene'])]; ls = sc['lines']; fr_ = c.get('from', 0); n = c.get('n', 0)
                ls = ls[fr_:fr_ + n] if n else ls[fr_:]
                dlg = [[(l['s'], l['e'], l['t']) for l in ls], 0, 0.0]
            elif k == 'line': dlg = [[(c.get('s', 'narrator'), c.get('e', 'neutral'), c.get('t', ''))], 0, 0.0]
        # step
        P.t += dt
        P.bars += max(-dt * 2, min(dt * 2, P.btarget - P.bars)); P.flash = max(0, P.flash - dt * 1.2)
        if wait > 0: wait -= dt
        if camtw:
            camtw[2] += dt; k = min(1, camtw[2] / camtw[3]); e = k * k * (3 - 2 * k)
            P.cam = [camtw[0][i] + (camtw[1][i] - camtw[0][i]) * e for i in range(3)]
            if k >= 1: camtw = None
        if fadetw:
            fadetw[2] += dt; k = min(1, fadetw[2] / fadetw[3]); P.fade = fadetw[0] + (fadetw[1] - fadetw[0]) * k
            if k >= 1: fadetw = None
        if P.cap:
            P.cap[2] += dt
            if P.cap[2] >= P.cap[3]: P.cap = None
        for key, (a, pts, sp, ed) in list(movers.items()):
            tx, ty = pts[0]; dx, dy = tx - a.x, ty - a.y; d = math.hypot(dx, dy)
            if d <= sp * dt:
                a.x, a.y = tx, ty; pts.pop(0)
                if not pts:
                    a.walk = False; del movers[key]
                    if ed is not None: a.dir = ed
                    if wmover == key: wmover = None
                    continue
            else: a.x += dx / d * sp * dt; a.y += dy / d * sp * dt; face(a, dx, dy)
            a.walk = True; a.anim += dt * 7
        for a in P.actors.values():
            if a.pose: a.pt += dt; a.pose = None if (a.pdur and a.pt >= a.pdur) else a.pose
            if a.emote: a.et -= dt; a.emote = None if a.et <= 0 else a.emote
        for f in P.fx: f['t'] += dt
        P.fx = [f for f in P.fx if f['t'] < f['dur']]
        cur = None
        if dlg:
            lines, i, tt = dlg; sp, e, txt = lines[i]; dlg[2] += dt
            cur = (sp, e, txt, int(dlg[2] * 42))
            if dlg[2] > len(txt) / 42 + 1.3:
                dlg[1] += 1; dlg[2] = 0
                if dlg[1] >= len(lines): dlg = None
        sink(P.render(cur))

if __name__ == '__main__':
    tmp = OUT + '.part.mp4'
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H), '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-crf', '20', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    frames = [0]
    def sink(fr):
        p.stdin.write(fr.convert('RGB').tobytes()); frames[0] += 1
        if os.environ.get('STILLS') and frames[0] % int(os.environ['STILLS']) == 0: fr.convert('RGB').save('%s_%05d.jpg' % (OUT, frames[0]), quality=88)
    P = None
    for spec in SPECS:
        step, _, idx = spec.partition(':')
        st_ = next(x for x in Q['steps'] if x['id'] == step)
        found = find_cines(step, int(idx) if idx else None)
        if not idx and 'complete' in st_:
            found += [(ac, P.area if P else None, None, None) for ac in st_['complete']['actions'] if ac.get('do') == 'cine']
        for ac, area, start, npc in found:
            if area is None: area = P.area if P else ROUTE + '_room'
            if start is None: start = (P.actors['player'].x, P.actors['player'].y) if P and P.area == area else tuple(MAPS[area]['spawn'])
            np_ = Player(area, start)
            if P and P.area == area and P.actors['partner'].vis: np_.actors['partner'] = P.actors['partner']
            elif P and P.actors['partner'].vis: np_.actors['partner'].vis = True
            if npc: pa = np_.actors['partner']; pa.x, pa.y, pa.dir = npc; pa.vis = True
            P = np_
            run(ac['cmds'], P, sink)
            for _ in range(int(FPS * 0.6)): sink(P.render())
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, OUT); print('frames', frames[0], '%.1fs' % (frames[0] / FPS))
