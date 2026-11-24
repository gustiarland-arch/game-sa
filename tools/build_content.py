"""Membangun seluruh konten cerita dari naskah + definisi quest.
Input : docs/reference_data/story_scenes_reference.json (Prolog & Chapter 1 canon), tools/content/naskah_*.txt,
        tools/build/maps_base.json, tools/build/anchors.json
Output: android/assets/data/story.json, quests.json, maps.json, memory_book.json
Pemakaian: python3 tools/build_content.py
"""
import os, re, json, copy

ROOT = os.path.join(os.path.dirname(__file__), '..')
DATA = os.path.join(ROOT, 'android', 'assets', 'data')
BUILD = os.path.join(os.path.dirname(__file__), 'build')
ANCH = json.load(open(os.path.join(BUILD, 'anchors.json')))
MAPS = json.load(open(os.path.join(BUILD, 'maps_base.json')))

def A(area, name):
    return ANCH[area][name]

# ============================================================== NASKAH
SPK = {'Narator': 'narrator', 'Arland': 'arland', 'Sofia': 'sofia', 'Arland (pesan)': 'arland_msg', 'Sofia (pesan)': 'sofia_msg'}
LOC = {'Kamar Arland': 'arland_room', 'Kamar Sofia': 'sofia_room', 'Plaza Kota': 'plaza', 'Memory Garden': 'memory_garden', 'Kafe Senja': 'cafe', 'Tepi Danau': 'riverside'}

def parse_line(s):
    m = re.match(r'^([a-z_]+)(?:\(([^)]*)\))?:\s*(.+)$', s.strip())
    if not m: raise ValueError('Baris naskah tidak valid: ' + s)
    return {'s': m.group(1), 'e': m.group(2) or 'neutral', 't': m.group(3).strip()}

def parse_naskah(path):
    scenes = {}; cur = None; choice = None
    for raw in open(path, encoding='utf-8'):
        line = raw.rstrip('\n')
        if not line.strip() or line.lstrip().startswith('#'): continue
        if line.startswith('==='):
            parts = [p.strip() for p in line[3:].split('|')]
            cur = {'title': parts[1], 'route': parts[2], 'chapter': parts[3], 'location': '', 'trigger': '', 'lines': [], 'flags': [], 'note': '', 'choices': []}
            scenes[parts[0]] = cur; choice = None; continue
        if line.startswith('@flags'): cur['flags'] = line.split()[1:]; continue
        if line.startswith('? '):
            txt, _, flag = line[2:].partition('|')
            choice = {'text': txt.strip(), 'flags': [flag.strip()] if flag.strip() else [], 'byRoute': {'arland': [], 'sofia': []}}
            cur['choices'].append(choice); continue
        if line[:3] in ('A> ', 'S> ', 'B> '):
            ln = parse_line(line[3:])
            if line[0] in 'AB': choice['byRoute']['arland'].append(ln)
            if line[0] in 'SB': choice['byRoute']['sofia'].append(ln)
            continue
        cur['lines'].append(parse_line(line))
    return scenes

ref = json.load(open(os.path.join(ROOT, 'docs', 'reference_data', 'story_scenes_reference.json'), encoding='utf-8'))
scenes = {}
for s in ref['scenes']:
    if not (s['id'].startswith('P-') or s['id'].startswith('C01')): continue
    flags = s.get('set_flags') or []
    if isinstance(flags, str): flags = [f.strip() for f in flags.split(',') if f.strip()]
    scenes[s['id']] = {'title': s['title'], 'route': s['route'], 'chapter': 'PRO' if s['id'].startswith('P-') else 'C01',
                       'location': LOC.get(s['location'], s['location']), 'trigger': s['trigger'],
                       'lines': [{'s': SPK.get(l['speaker'], l['speaker'].lower()), 'e': l.get('emotion', 'neutral'), 't': l['text']} for l in s['lines']],
                       'flags': flags, 'note': s.get('director_note', ''), 'choices': [{'text': c} for c in s.get('choices', [])]}
scenes['P-X01']['choices'] = [
    {'text': 'Boleh aku lihat sekarang?', 'flags': ['PRO_CHOICE_OPEN_NOW'], 'byRoute': {
        'arland': [{'s': 'arland', 'e': 'senyum', 't': 'Boleh aku lihat sekarang?'}, {'s': 'sofia', 'e': 'malu', 't': 'Boleh. Tapi jangan dibaca keras-keras, ya.'}, {'s': 'arland', 'e': 'senang', 't': 'Siap. Aku simpan baik-baik.'}],
        'sofia': [{'s': 'sofia', 'e': 'senyum', 't': 'Boleh aku lihat sekarang?'}, {'s': 'arland', 'e': 'malu', 't': 'Boleh... tapi lipatannya agak miring.'}, {'s': 'sofia', 'e': 'tertawa', 't': 'Justru itu yang bikin lucu.'}]}},
    {'text': 'Kita duduk dulu, yuk.', 'flags': ['PRO_CHOICE_SIT_FIRST'], 'byRoute': {
        'arland': [{'s': 'arland', 'e': 'neutral', 't': 'Kita duduk dulu, yuk.'}, {'s': 'sofia', 'e': 'senang', 't': 'Iya, di bangku dekat air mancur saja.'}],
        'sofia': [{'s': 'sofia', 'e': 'neutral', 't': 'Kita duduk dulu, yuk.'}, {'s': 'arland', 'e': 'senang', 't': 'Boleh. Bangku dekat air mancur kosong, tuh.'}]}}]
for f in sorted(os.listdir(os.path.join(os.path.dirname(__file__), 'content'))):
    if f.startswith('naskah_') and f.endswith('.txt'):
        scenes.update(parse_naskah(os.path.join(os.path.dirname(__file__), 'content', f)))

# pembicara generik 'me' (tokoh yang dimainkan) / 'partner' -> dua versi adegan: ID@arland, ID@sofia
SPLIT = set()
for sid in list(scenes):
    sc_ = scenes[sid]
    allines = sc_['lines'] + [l for c in sc_.get('choices', []) for r in c.get('byRoute', {}).values() for l in r]
    if not any(l['s'] in ('me', 'partner') for l in allines): continue
    for r, o in (('arland', 'sofia'), ('sofia', 'arland')):
        c = copy.deepcopy(sc_); c['route'] = r
        def mp(ls):
            for l in ls: l['s'] = {'me': r, 'partner': o}.get(l['s'], l['s'])
        mp(c['lines'])
        for ch in c.get('choices', []):
            for lst in ch.get('byRoute', {}).values(): mp(lst)
        scenes[sid + '@' + r] = c
    del scenes[sid]; SPLIT.add(sid)

SPEAKERS = {
    'narrator': {'name': 'Narator', 'portrait': None},
    'arland': {'name': 'Arland', 'portrait': 'arland'}, 'sofia': {'name': 'Sofia', 'portrait': 'sofia'},
    'arland_msg': {'name': 'Arland (pesan)', 'portrait': 'arland', 'style': 'message'},
    'sofia_msg': {'name': 'Sofia (pesan)', 'portrait': 'sofia', 'style': 'message'},
    'raka': {'name': 'Kak Raka', 'portrait': None, 'style': 'npc', 'sprite': 'raka'},
    'melati': {'name': 'Bu Melati', 'portrait': None, 'style': 'npc', 'sprite': 'melati'},
    'juna': {'name': 'Bang Juna', 'portrait': None, 'style': 'npc', 'sprite': 'juna'},
    'sari': {'name': 'Nenek Sari', 'portrait': None, 'style': 'npc', 'sprite': 'sari'},
    'dito': {'name': 'Dito', 'portrait': None, 'style': 'npc', 'sprite': 'dito'},
    'lumi': {'name': 'Lumi', 'portrait': None, 'style': 'npc', 'sprite': 'lumi'},
    'udin': {'name': 'Pak Udin', 'portrait': None, 'style': 'npc', 'sprite': 'udin'},
    'pos': {'name': 'Pak Pos', 'portrait': None, 'style': 'npc', 'sprite': 'pos'},
    'laras': {'name': 'Bu Laras', 'portrait': None, 'style': 'npc', 'sprite': 'laras'},
    'bayu': {'name': 'Kak Bayu', 'portrait': None, 'style': 'npc', 'sprite': 'bayu'},
    'nara': {'name': 'Kak Nara', 'portrait': None, 'style': 'npc', 'sprite': 'nara'},
}
for sid, sc in scenes.items():
    for ln in sc['lines'] + [l for c in sc.get('choices', []) for r in c.get('byRoute', {}).values() for l in r]:
        if ln['s'] not in SPEAKERS: raise SystemExit('Pembicara tidak dikenal di %s: %s' % (sid, ln['s']))

EMOTIONS = {
    'neutral': {'portrait': ['normal'], 'emote': None},
    'senyum': {'portrait': ['tersenyum', 'senang', 'normal'], 'emote': None},
    'tersenyum': {'portrait': ['tersenyum', 'senang', 'normal'], 'emote': 'heart'},
    'senang': {'portrait': ['senang', 'normal'], 'emote': 'note'},
    'tertawa': {'portrait': ['tertawa', 'senang', 'normal'], 'emote': 'note'},
    'penasaran': {'portrait': ['pikir', 'serius', 'normal'], 'emote': 'question'},
    'bingung': {'portrait': ['pikir', 'serius', 'normal'], 'emote': 'question'},
    'malu': {'portrait': ['malu', 'normal'], 'emote': 'heart'},
    'kaget': {'portrait': ['kaget', 'normal'], 'emote': 'exclaim'},
    'sedih': {'portrait': ['sedih', 'normal'], 'emote': 'dots'},
    'serius': {'portrait': ['serius', 'pikir', 'normal'], 'emote': None},
    'lega': {'portrait': ['lega', 'senang', 'normal'], 'emote': 'note'},
    'khawatir': {'portrait': ['khawatir', 'sedih', 'normal'], 'emote': 'dots'},
    'jatuh_cinta': {'portrait': ['jatuh_cinta', 'malu', 'normal'], 'emote': 'heart'}}
for sid, sc_ in []: pass

CHAPTERS = [('PRO', 'Prologue — The Book of Us'), ('C01', 'Chapter 1 — The Beginning of Us'), ('C02', 'Chapter 2 — A Little Date'),
            ('C03', 'Chapter 3 — The Little Things'), ('C04', 'Chapter 4 — Even When It Rains'), ('C05', 'Chapter 5 — Across the Stars'),
            ('C06', 'Chapter 6 — Our Tomorrow'), ('EPI', 'Epilogue — To Be Continued')]

# ============================================================== helper aksi
def sc(i):
    if i in SPLIT: return {'do': 'scene', 'id': i + '@$ROUTE'}
    assert i in scenes, 'scene hilang ' + i; return {'do': 'scene', 'id': i}
def unfl(*ids): return [{'do': 'unflag', 'id': i} for i in ids]
def fl(*ids): return [{'do': 'flag', 'id': i} for i in ids]
def it(i, route=None): d = {'do': 'item', 'id': i}; d.update({'route': route} if route else {}); return d
def rm(i, route=None): d = {'do': 'removeItem', 'id': i}; d.update({'route': route} if route else {}); return d
def st(i): return {'do': 'step', 'id': i}
def warp(area, pt, dir='down'): return {'do': 'warp', 'area': area, 'x': pt[0], 'y': pt[1], 'dir': dir}
def comp(on): return {'do': 'companion', 'on': on}
def toast(t): return {'do': 'toast', 'text': t}
def sfx(i='sparkle'): return {'do': 'sfx', 'id': i}
def card(c): return {'do': 'chapterCard', 'chapter': c}
def cend(c): return {'do': 'chapterEnd', 'chapter': c}
def mg(i): return {'do': 'minigame', 'id': i}
def cnt(i, n=1): return {'do': 'count', 'id': i, 'add': n}
def emote(who, e): return {'do': 'emote', 'who': who, 'e': e}
def iff(when, then, els=()): return {'do': 'if', 'when': when, 'then': list(then), 'else': list(els)}
def say(lines, name=None, route=None):
    d = {'do': 'lines', 'lines': [{'s': s, 'e': e, 't': t} for (s, e, t) in lines]}
    if name: d['name'] = name
    if route: d['route'] = route
    return d

def I(id, area, pt, label, actions, route=None, r=64, sprite=None, when=None, hide=None, lbr=None, marker=True):
    d = {'id': id, 'area': area, 'x': pt[0], 'y': pt[1], 'r': r, 'label': label, 'actions': actions}
    if route: d['route'] = route
    if sprite: d['sprite'] = {'image': sprite[0], 'x': sprite[1], 'y': sprite[2], 'bob': len(sprite) > 3 and sprite[3]}
    if when: d['when'] = when
    if hide: d['hideIfFlag'] = hide
    if lbr: d['labelByRoute'] = lbr
    if not marker: d['marker'] = False
    return d

def NP(area, pt, dir='down', who='$PARTNER'): return {'who': who, 'area': area, 'x': pt[0], 'y': pt[1], 'dir': dir}

steps = []
def S(id, ch, quest, obj_a, obj_s=None, inter=(), npcs=(), enter=None, complete=None, counter=None, cmax=0, weather=None, tint=None, talpha=None, final=False, onstart=None, start_area=None, music=None, music_areas=None):
    d = {'id': id, 'chapter': ch, 'quest': quest, 'objective': {'arland': obj_a, 'sofia': obj_s or obj_a}}
    if inter: d['interactables'] = list(inter)
    if npcs: d['npcs'] = list(npcs)
    if enter: d['enterArea'] = {'area': enter[0], 'actions': enter[1]}
    if complete: d['complete'] = {'counter': complete[0], 'count': complete[1], 'actions': complete[2]}
    if counter: d['counter'] = counter; d['counterMax'] = cmax
    if weather: d['weather'] = weather
    if tint: d['tint'] = tint; d['tintAlpha'] = talpha or 0.3
    if final: d['final'] = True
    if onstart: d['onStart'] = list(onstart)
    if start_area: d['startArea'] = start_area
    if music: d['music'] = music; d['musicAreas'] = list(music_areas or [])
    steps.append(d)

ROOM = '$ROOM'
# ---- cutscene: cine(C('move', who='player', to=[x, y]), C('say', scene='P-X01', n=1), ...)
def C(c, **kw):
    if 'async_' in kw: kw['async'] = kw.pop('async_')
    if 'from_' in kw: kw['from'] = kw.pop('from_')
    if c == 'say' and kw.get('scene') in SPLIT: kw['scene'] += '@$ROUTE'
    kw['c'] = c; return kw
def cine(*cmds): return {'do': 'cine', 'cmds': [x for x in cmds if x]}
def RC(route, cmd): cmd['route'] = route; return cmd
RAIN, NIGHT = 'rain', '#1b2350'

# ============================================================== PROLOG
INTRO = cine(
    C('fade', to=1, t=0), C('bars', on=True, t=0.01),
    RC('arland', C('place', who='player', x=852, y=358, dir='down')), RC('sofia', C('place', who='player', x=108, y=358, dir='down')),
    C('pose', who='player', pose='sit'),
    RC('arland', C('cam', x=830, y=330, zoom=1.4, t=0)), RC('sofia', C('cam', x=130, y=330, zoom=1.4, t=0)),
    RC('arland', C('caption', text='Sabtu pagi', sub='Kamar Arland', t=2.6, async_=True)), RC('sofia', C('caption', text='Sabtu pagi', sub='Kamar Sofia', t=2.6, async_=True)),
    C('fade', to=0, t=1.8), C('wait', t=0.8),
    RC('sofia', C('fx', kind='glow', on='player', t=2.6)),
    C('emote', who='player', e='dots', t=1.6), C('wait', t=1.4),
    RC('arland', C('line', s='arland', e='neutral', t='Hm... sudah pagi, ya.')),
    RC('sofia', C('line', s='sofia', e='neutral', t='Hangat sekali rasanya... seperti habis memeluk sesuatu. Tapi apa, ya?')),
    RC('sofia', C('pose', who='player', pose='cheer', t=1.2, block=True)),
    C('pose', who='player', pose='none'),
    RC('arland', C('cam', x=700, y=380, zoom=1.0, t=1.8, async_=True)), RC('sofia', C('cam', x=280, y=380, zoom=1.0, t=1.8, async_=True)),
    RC('arland', C('move', who='player', path=[[820, 404], [640, 420]])), RC('sofia', C('move', who='player', path=[[140, 404], [320, 420]])),
    C('sfx', id='page'), C('emote', who='player', e='note', t=1.6),
    RC('arland', C('face', who='player', dir='left')), RC('sofia', C('face', who='player', dir='right')),
    RC('arland', C('line', s='narrator', e='neutral', t='Ponsel di meja kerja bergetar pelan.')),
    RC('sofia', C('line', s='narrator', e='neutral', t='Ponsel di meja rias berbunyi pelan.')),
    C('bars', on=False, t=0.6))
GIFT_CINE = cine(C('face', who='player', dir='down'), C('pose', who='player', pose='give', t=1.8, block=True), C('emote', who='player', e='heart', t=1.6), C('wait', t=0.5))
S('PRO_PHONE', 'PRO', 'Q_PRO_PHONE', 'Baca pesan di ponsel (meja kerja)', 'Baca pesan di ponsel (meja)', onstart=[INTRO], start_area=ROOM, inter=[
    I('phone', 'arland_room', A('arland_room', 'phone'), 'Lihat ponsel', [sfx('page'), sc('P-A01'), *fl('PRO_PHONE_READ'), st('PRO_GIFT')], route='arland'),
    I('phone', 'sofia_room', A('sofia_room', 'phone'), 'Lihat ponsel', [sfx('page'), sc('P-S01'), *fl('PRO_PHONE_READ'), st('PRO_GIFT')], route='sofia')])
S('PRO_GIFT', 'PRO', 'Q_PRO_GIFT', 'Ambil bunga kertas di dekat lemari', 'Ambil kartu pos di meja rias', inter=[
    I('gift', 'arland_room', A('arland_room', 'gift_table'), 'Bunga kertas', [sc('P-A02'), it('paper_flower'), sfx(), GIFT_CINE, *fl('PRO_GIFT_ARLAND'), st('PRO_GO_PLAZA')], route='arland',
      sprite=('props/pickup_paper_flower.png', 262, 262)),
    I('gift', 'sofia_room', A('sofia_room', 'gift_table'), 'Kartu pos', [sc('P-S02'), it('postcard'), sfx(), GIFT_CINE, *fl('PRO_GIFT_SOFIA'), st('PRO_GO_PLAZA')], route='sofia',
      sprite=('props/pickup_postcard.png', 340, 262))])
MP = A('plaza', 'meet_partner')
ARRIVE_PLAZA = cine(
    C('bars', on=True, t=0.5),
    C('place', who='partner', x=MP[0], y=MP[1], dir='left'),
    C('cam', x=960, y=640, zoom=0.75, t=2.0),
    C('caption', text='Plaza Kota', sub='Sabtu, pukul sepuluh pagi', t=2.6),
    C('cam', x=MP[0], y=MP[1] - 30, zoom=1.35, t=1.8),
    C('fx', kind='petals', x=MP[0], y=MP[1], t=5.6),
    RC('arland', C('pose', who='partner', pose='bow', t=1.4, block=True)),
    RC('sofia', C('pose', who='partner', pose='give', t=1.4, block=True)),
    C('emote', who='partner', e='sweat', t=1.4),
    RC('arland', C('line', s='narrator', e='neutral', t='Sofia sudah menunggu, sesekali merapikan ujung kerudungnya.')),
    RC('sofia', C('line', s='narrator', e='neutral', t='Arland sudah di sana, memandangi sesuatu di tangannya, lalu buru-buru menyembunyikannya.')),
    C('cam', on='player', zoom=1.0, t=1.4),
    C('bars', on=False, t=0.5))
S('PRO_GO_PLAZA', 'PRO', 'Q_PRO_MEET', 'Keluar rumah dan pergi ke Plaza Kota', enter=('plaza', [ARRIVE_PLAZA, st('PRO_MEET')]))
MID = (MP[0] - 19, MP[1] - 40)
MEET_CINE = cine(
    C('music', id='cinema_first_meet'),
    C('bars', on=True, t=0.4),
    C('face', who='partner', at='player'),
    C('pose', who='arland', pose='wave', t=1.6),
    C('cam', x=MID[0], y=MID[1] + 20, zoom=1.4, t=1.2, async_=True),
    C('say', scene='P-X01', n=1),
    C('move', who='player', to=[MP[0] - 38, MP[1] + 4], dir='right'), C('face', who='partner', dir='left'),
    C('say', scene='P-X01', from_=1, n=2),
    C('pose', who='arland', pose='give', t=2.0, block=True),
    C('pose', who='sofia', pose='reach', t=1.0), C('emote', who='sofia', e='heart', t=1.6), C('sfx', id='sparkle'), C('wait', t=0.7),
    C('say', scene='P-X01', from_=3, n=1),
    C('pose', who='sofia', pose='give', t=2.0, block=True),
    C('pose', who='arland', pose='reach', t=1.0), C('emote', who='arland', e='heart', t=1.6),
    C('fx', kind='hearts', x=MID[0], y=MID[1] + 30, t=2.6), C('sfx', id='sparkle'), C('wait', t=1.0),
    C('say', scene='P-X01', from_=4),
    C('wait', t=0.5),
    C('sfx', id='sparkle'), C('fx', kind='glow', x=1160, y=852, t=4.0),
    C('emote', who='player', e='exclaim', t=1.4), C('emote', who='partner', e='exclaim', t=1.4),
    C('pose', who='player', pose='surprised', t=0.5), C('pose', who='partner', pose='surprised', t=0.5),
    C('face', who='player', dir='down'), C('face', who='partner', dir='down'),
    C('cam', x=1160, y=820, zoom=1.25, t=1.8), C('wait', t=0.8),
    C('line', s='narrator', e='neutral', t='Di bangku selatan, sesuatu berpendar, seperti sedang menunggu disapa.'),
    C('cam', on='player', zoom=1.0, t=1.2),
    C('bars', on=False, t=0.5))
S('PRO_MEET', 'PRO', 'Q_PRO_MEET', 'Temui Sofia di dekat air mancur', 'Temui Arland di dekat air mancur', npcs=[NP('plaza', A('plaza', 'meet_partner'), 'left')], inter=[
    I('meet', 'plaza', A('plaza', 'meet_partner'), 'Sapa', [MEET_CINE, rm('paper_flower', 'arland'), it('postcard', 'arland'), rm('postcard', 'sofia'), it('paper_flower', 'sofia'),
      *fl('PRO_MET_PARTNER', 'CANON_PLAZA_MEET'), sfx(), comp(True), st('PRO_BOOK')], r=62, lbr={'arland': 'Sapa Sofia', 'sofia': 'Sapa Arland'})])
PORTAL_CINE = cine(
    C('music', id='cinema_memory_portal'),
    C('bars', on=True, t=0.4),
    C('move', who='partner', to=[1194, 900], dir='up', async_=True), C('move', who='player', to=[1128, 900], dir='up'),
    C('face', who='player', dir='up'), C('face', who='partner', dir='up'),
    C('cam', x=1160, y=850, zoom=1.5, t=1.4),
    C('say', scene='P-X02'),
    C('music', id='memory'), C('sfx', id='sparkle'),
    C('fx', kind='book', x=1160, y=860, t=6.5), C('wait', t=1.3),
    C('pose', who='player', pose='surprised', t=0.5), C('pose', who='partner', pose='surprised', t=0.5),
    C('shake', t=0.9, amp=2.5),
    C('fx', kind='portal', x=1160, y=850, t=10.0), C('fx', kind='sparkles', x=1160, y=840, t=3.0, n=40),
    C('cam', x=1160, y=840, zoom=1.85, t=2.4),
    C('line', s='narrator', e='neutral', t='Halaman-halaman buku terbuka sendiri. Cahaya di dalamnya berputar, membentuk sebuah pintu.'),
    C('move', who='partner', path=[[1194, 936], [1176, 936]], dir='down', async_=True), C('move', who='player', path=[[1128, 936], [1146, 936]], dir='down'),
    C('cam', x=1160, y=902, zoom=1.6, t=0.9), C('wait', t=0.2),
    C('pose', who='player', pose='hold_r'), C('pose', who='partner', pose='hold_l'),
    C('emote', who='partner', e='heart', t=1.4), C('wait', t=1.3),
    C('line', s='narrator', e='neutral', t='Tanpa perlu bicara, keduanya saling menggenggam tangan.'),
    C('sfx', id='sparkle'), C('flash', t=1.2), C('fade', to=1, t=0.7, color='fff6e8'))
GA = A('memory_garden', 'arrive')
GARDEN_CINE = cine(
    C('music', id='cinema_memory_portal'),
    C('fade', to=1, t=0, color='fff6e8'), C('bars', on=True, t=0.01),
    C('place', who='partner', x=GA[0] + 40, y=GA[1] + 4, dir='up'),
    C('cam', x=800, y=760, zoom=0.8, t=0),
    C('fade', to=0, t=1.8, color='fff6e8'),
    C('caption', text='Memory Garden', sub='Dunia di dalam Memory Book', t=2.8),
    C('fx', kind='petals', x=GA[0], y=GA[1] - 25, t=6.5),
    C('fx', kind='sparkles', x=GA[0], y=GA[1] - 45, t=5.5, n=22),
    C('cam', x=GA[0] + 20, y=GA[1] - 40, zoom=1.3, t=2.2),
    C('pose', who='partner', pose='surprised', t=0.5), C('emote', who='partner', e='question', t=1.6),
    C('face', who='player', dir='left'), C('wait', t=0.6), C('face', who='player', dir='right'), C('wait', t=0.6),
    C('face', who='player', at='partner'), C('face', who='partner', at='player'),
    C('say', scene='P-X03'),
    C('cam', on='player', zoom=1.0, t=1.2), C('bars', on=False, t=0.5))
SHARDS_DONE_CINE = cine(
    C('bars', on=True, t=0.4),
    C('sfx', id='sparkle'), C('fx', kind='sparkles', on='player', t=2.2, n=40), C('fx', kind='restore', on='player', t=2.6),
    C('cam', on='player', zoom=1.45, t=1.2), C('pose', who='player', pose='cheer', t=1.2, block=True),
    C('say', scene='P-X04'),
    C('fx', kind='beam', x=800, y=420, t=5.0), C('fx', kind='portal', x=800, y=410, t=5.0),
    C('cam', x=800, y=470, zoom=1.0, t=1.8), C('wait', t=0.8),
    C('line', s='narrator', e='neutral', t='Di utara, gerbang cahaya terbuka. Jalan pulang sudah menunggu.'),
    C('cam', on='player', zoom=1.0, t=1.4), C('bars', on=False, t=0.5))
S('PRO_BOOK', 'PRO', 'Q_PRO_GARDEN', 'Periksa buku bercahaya di bangku selatan plaza', inter=[
    I('book', 'plaza', A('plaza', 'bench_book'), 'Buku bercahaya', [PORTAL_CINE, it('memory_book'), *fl('PRO_BOOK_FOUND', 'CANON_BOOK_OPEN'),
      warp('memory_garden', A('memory_garden', 'arrive'), 'up'), GARDEN_CINE, *fl('PRO_GARDEN_ENTERED'), st('PRO_SHARDS')], sprite=('props/glowing_book.png', 1160, 852))])
S('PRO_SHARDS', 'PRO', 'Q_PRO_GARDEN', 'Kumpulkan 3 keping cahaya', counter='shards', cmax=3, inter=[
    I('shard_%d' % k, 'memory_garden', A('memory_garden', 'shard%d' % k), 'Keping cahaya', [*fl('SHARD_%d' % k), {'do': 'shard'}, sfx()], hide='SHARD_%d' % k,
      sprite=('props/light_shard.png', A('memory_garden', 'shard%d' % k)[0], A('memory_garden', 'shard%d' % k)[1] - 14, True)) for k in (1, 2, 3)],
  complete=('shards', 3, [SHARDS_DONE_CINE, *fl('PRO_COMPLETED', 'CANON_MEMORY_GARDEN'), st('PRO_PORTAL')]))
S('PRO_PORTAL', 'PRO', 'Q_PRO_GARDEN', 'Masuk gerbang cahaya di utara untuk pulang', inter=[
    I('portal', 'memory_garden', A('memory_garden', 'portal'), 'Gerbang pulang', [sfx(), warp('plaza', A('plaza', 'bench_book')), cend('PRO'), comp(False),
      warp(ROOM, (480, 440)), card('C01'), st('C01_NOTE')], r=80)])

# ============================================================== CHAPTER 1
S('C01_NOTE', 'C01', 'Q_C01_PERSONAL', 'Cari catatan kecil di rak buku', 'Cari pembatas buku di rak buku', inter=[
    I('note', 'arland_room', A('arland_room', 'shelf'), 'Rak buku', [sc('C01-A01'), it('small_note'), sfx('page'), *fl('C01_ARLAND_NOTE'), st('C01_GO_PLAZA')], route='arland',
      sprite=('props/pickup_note.png', 130, 214)),
    I('note', 'sofia_room', A('sofia_room', 'shelf'), 'Rak buku', [sc('C01-S01'), it('bookmark'), sfx('page'), *fl('C01_SOFIA_BOOKMARK'), st('C01_GO_PLAZA')], route='sofia',
      sprite=('props/pickup_bookmark.png', 830, 214))])
S('C01_GO_PLAZA', 'C01', 'Q_C01_MURAL', 'Pergi ke Plaza Kota', enter=('plaza', [toast('Plaza Kota'), st('C01_MURAL')]))
S('C01_MURAL', 'C01', 'Q_C01_MURAL', 'Amati mural di sisi barat plaza', inter=[
    I('mural', 'plaza', A('plaza', 'mural'), 'Amati mural', [sc('C01-A02'), *fl('C01_HINT_ARLAND'), toast('Petunjuk: BUNGA → BUKU → BINTANG'), st('C01_CAFE')], route='arland'),
    I('mural', 'plaza', A('plaza', 'mural'), 'Amati mural', [sc('C01-S02'), *fl('C01_HINT_SOFIA'), toast('Petunjuk: BINTANG → BUKU → BUNGA'), st('C01_CAFE')], route='sofia')])
S('C01_CAFE', 'C01', 'Q_C01_PUZZLE', 'Masuk ke Kafe Senja (bangunan ungu di timur laut)', enter=('cafe', [comp(True), sc('C01-X01'), *fl('C01_PUZZLE_ACTIVE'), st('C01_PUZZLE')]))
S('C01_PUZZLE', 'C01', 'Q_C01_PUZZLE', 'Susun tiga simbol di meja simbol', inter=[
    I('symbols', 'cafe', A('cafe', 'symbols'), 'Meja simbol', [{'do': 'puzzle', 'id': 'C01_SYMBOLS'}, *fl('C01_PUZZLE_SOLVED'), sfx(), sc('C01-X02'), it('letter_two_sides'),
      *fl('C01_LETTER_FOUND', 'CANON_CAFE_LETTER'), sc('C01-LIB-0'), st('C01_LIBRARY_GO')], r=66)])
LIB = lambda k: A('perpustakaan', k)
LIB_ENTER = cine(
    C('bars', on=True, t=0.4), C('cam', x=640, y=520, zoom=0.9, t=1.6),
    C('caption', text='Perpustakaan Kota', sub='Sunyi, hangat, dan wangi kertas tua', t=2.6),
    C('fx', kind='glow', x=LIB('laras')[0], y=LIB('laras')[1], t=4.0),
    C('cam', x=LIB('laras')[0], y=LIB('laras')[1] - 10, zoom=1.35, t=1.4),
    C('pose', who='laras', pose='bow', t=1.2, block=True), C('emote', who='laras', e='note', t=1.4),
    C('cam', on='player', zoom=1.0, t=1.2), C('bars', on=False, t=0.5))
S('C01_LIBRARY_GO', 'C01', 'Q_C01_LIBRARY', 'Ikuti cap arsip ke Perpustakaan Kota (Jalan Kota ke timur, lalu Distrik Perumahan)',
  enter=('perpustakaan', [LIB_ENTER, st('C01_LARAS')]))
S('C01_LARAS', 'C01', 'Q_C01_LIBRARY', 'Tanyakan cap "Arsip No. 7" pada Bu Laras di meja informasi', inter=[
    I('laras1', 'perpustakaan', LIB('counter_front'), 'Bicara dengan Bu Laras', [sc('C01-LIB-1'), toast('Cari 3 buku: bunga, buku, bintang'), st('C01_BOOKS')], r=66)])
BOOK_SPOTS = [('libbook1', LIB('shelf_a'), 'C01-LIB-B1', 'Ensiklopedia bunga'), ('libbook2', LIB('shelf_c'), 'C01-LIB-B2', 'Buku tentang buku'), ('libbook3', LIB('shelf_b'), 'C01-LIB-B3', 'Peta langit malam')]
S('C01_BOOKS', 'C01', 'Q_C01_LIBRARY', 'Temukan 3 buku catatan Pak Wira di rak-rak (bunga, buku, bintang)', counter='libbook', cmax=3, inter=[
    I(i, 'perpustakaan', pt, lab, [cine(C('pose', who='player', pose='reach', t=0.8, block=True)), sc(scn), *fl('LIB_' + i.upper()), cnt('libbook'), sfx('page')], hide='LIB_' + i.upper(), r=56)
    for i, pt, scn, lab in BOOK_SPOTS],
  complete=('libbook', 3, [toast('Letakkan ketiga buku di meja baca'), st('C01_TABLE')]))
SECRET = LIB('secret')
OPEN_A = cine(C('bars', on=True, t=0.4), C('face', who='player', dir='up'), C('pose', who='player', pose='give', t=1.2, block=True),
              C('say', scene='C01-LIB-OPEN', n=2), C('cam', x=SECRET[0], y=SECRET[1] - 40, zoom=1.4, t=1.4))
OPEN_B = cine(C('sfx', id='sparkle'), C('shake', t=0.7, amp=2), C('fx', kind='sparkles', x=SECRET[0], y=SECRET[1] - 40, t=2.2, n=36), C('fx', kind='glow', x=SECRET[0], y=SECRET[1] - 30, t=3.5),
              C('wait', t=1.0), C('emote', who='player', e='exclaim'), C('emote', who='partner', e='exclaim'),
              C('say', scene='C01-LIB-OPEN', from_=2), C('cam', on='player', zoom=1.0, t=1.0), C('bars', on=False, t=0.4))
S('C01_TABLE', 'C01', 'Q_C01_LIBRARY', 'Letakkan ketiga buku di meja baca', inter=[
    I('libtable', 'perpustakaan', LIB('table'), 'Meja baca', [OPEN_A, *fl('LIB_SECRET_OPEN'), OPEN_B, st('C01_ARCHIVE')], r=60)])
ARC = lambda k: A('ruang_arsip', k)
ARC_ENTER = cine(C('fade', to=1, t=0), C('bars', on=True, t=0.01), C('cam', x=400, y=380, zoom=1.1, t=0), C('fade', to=0, t=1.4),
                 C('caption', text='Arsip No. 7', sub='Ruangan yang tidak tercatat di peta mana pun', t=2.8),
                 C('fx', kind='glow', x=ARC('jars_w')[0], y=ARC('jars_w')[1] - 30, t=3), C('fx', kind='glow', x=ARC('jars_e')[0], y=ARC('jars_e')[1] - 30, t=3),
                 C('cam', x=400, y=440, zoom=1.35, t=1.8), C('emote', who='partner', e='question'), C('cam', on='player', zoom=1.0, t=1.0), C('bars', on=False, t=0.4))
S('C01_ARCHIVE', 'C01', 'Q_C01_LIBRARY', 'Masuk ke rak yang terbuka', enter=('ruang_arsip', [ARC_ENTER, st('C01_PEDESTAL')]))
PED = ARC('pedestal')
PED_CINE = cine(C('bars', on=True, t=0.4), C('move', who='partner', to=[PED[0] + 34, PED[1] + 6], dir='up', async_=True), C('move', who='player', to=[PED[0] - 22, PED[1] + 6], dir='up'),
                C('cam', x=PED[0], y=PED[1] - 50, zoom=1.5, t=1.4), C('fx', kind='glow', x=PED[0], y=PED[1] - 40, t=12),
                C('say', scene='C01-ARC-1', n=5), C('sfx', id='sparkle'), C('fx', kind='book', on='player', t=4.0), C('fx', kind='sparkles', on='player', t=2.5, n=30),
                C('say', scene='C01-ARC-1', from_=5, n=2), C('shake', t=0.4, amp=1), C('wait', t=0.6),
                C('say', scene='C01-ARC-1', from_=7), C('pose', who='partner', pose='bow', t=1.2), C('face', who='player', at='partner'), C('wait', t=0.8),
                C('cam', on='player', zoom=1.0, t=1.0), C('bars', on=False, t=0.4))
S('C01_PEDESTAL', 'C01', 'Q_C01_LIBRARY', 'Baca catatan di tiang batu', inter=[
    I('pedestal', 'ruang_arsip', PED, 'Catatan di tiang batu', [PED_CINE, it('catatan_wira'), *fl('C01_ARCHIVE_DONE', 'CANON_ARCHIVE_SEED'), iff({'route': 'arland'}, [st('C01_Q_A_MAP')], [st('C01_Q_S_MARGIN')])], r=60)])
# v1.8: dua cara membaca arsip Wira, dengan langkah dan kenangan yang benar-benar berbeda.
S('C01_Q_A_MAP', 'C01', 'Q_C01_LIBRARY', 'Periksa denah di stoples barat ruang arsip', inter=[
    I('q_a_map', 'ruang_arsip', A('ruang_arsip', 'jars_w'), 'Denah Pak Wira', [sc('Q-C01-A'), *fl('Q_C01_A_MAP'), sfx('page'), st('C01_LARAS2')], route='arland', r=66)])
S('C01_Q_S_MARGIN', 'C01', 'Q_C01_LIBRARY', 'Baca tulisan pinggir buku di stoples timur', inter=[
    I('q_s_margin', 'ruang_arsip', A('ruang_arsip', 'jars_e'), 'Catatan pinggir', [sc('Q-C01-S'), *fl('Q_C01_S_MARGIN'), sfx('page'), st('C01_LARAS2')], route='sofia', r=66)])
S('C01_LARAS2', 'C01', 'Q_C01_LIBRARY', 'Ceritakan pada Bu Laras', inter=[
    I('laras2', 'perpustakaan', LIB('counter_front'), 'Bicara dengan Bu Laras', [sc('C01-ARC-2'), st('C01_RIVERSIDE')], r=66)])
SUNSET = '#ff8a4a'
S('C01_RIVERSIDE', 'C01', 'Q_C01_LETTER', 'Pergi ke Tepi Danau (selatan plaza), lalu ke dermaga di timurnya', tint=SUNSET, talpha=0.16,
  enter=('riverside', [toast('Matahari mulai turun...'), st('C01_PIER')]))
PIER = lambda k: A('dermaga', k)
PIER_ARRIVE = cine(C('bars', on=True, t=0.4), C('cam', x=960, y=640, zoom=0.8, t=2.2), C('caption', text='Dermaga Danau', sub='Pukul lima sore', t=2.6),
                   C('cam', x=960, y=900, zoom=1.0, t=2.0), C('wait', t=0.6), C('cam', on='player', zoom=1.0, t=1.4), C('bars', on=False, t=0.4))
S('C01_PIER', 'C01', 'Q_C01_LETTER', 'Pergi ke Dermaga Danau (sisi timur Tepi Danau)', tint=SUNSET, talpha=0.2, music='tender', music_areas=['dermaga'], enter=('dermaga', [PIER_ARRIVE, st('C01_SUNSET')]))
SUNSET_CINE = cine(
    C('bars', on=True, t=0.5), C('music', id='tender'),
    C('move', who='partner', path=[[PIER('pier_end')[0] + 10, PIER('pier_end')[1] - 40], [PIER('plat_r')[0] - 40, PIER('pier_end')[1] + 18]], dir='down', async_=True),
    C('move', who='player', path=[[PIER('pier_end')[0] - 10, PIER('pier_end')[1] - 40], [PIER('plat_l')[0] + 40, PIER('pier_end')[1] + 18]], dir='down'),
    C('wait', t=0.7), C('face', who='player', dir='down'), C('face', who='partner', dir='down'),
    C('pose', who='player', pose='sit'), C('pose', who='partner', pose='sit'),
    C('cam', x=960, y=930, zoom=1.6, t=2.2), C('tint', color='ff7a3a', a=0.22, t=3.0), C('fx', kind='glow', x=960, y=1040, t=30),
    C('wait', t=1.2), C('say', scene='C01-PIER', n=4),
    C('face', who='partner', at='player'), C('face', who='player', at='partner'),
    C('say', scene='C01-PIER', from_=4, n=1), C('emote', who='partner', e='heart', t=1.6), C('say', scene='C01-PIER', from_=5),
    C('face', who='player', dir='down'), C('face', who='partner', dir='down'),
    C('tint', color='6a4a9a', a=0.26, t=4.0), C('cam', x=960, y=920, zoom=1.25, t=4.0, async_=True), C('wait', t=1.2),
    C('say', scene='C01-X03'),
    C('fx', kind='stars', x=960, y=900, t=8, n=30), C('wait', t=2.0), C('fade', to=1, t=1.4))
S('C01_SUNSET', 'C01', 'Q_C01_LETTER', 'Duduk bersama di ujung dermaga', tint=SUNSET, talpha=0.2, music='tender', music_areas=['dermaga'], inter=[
    I('pierend', 'dermaga', PIER('pier_end'), 'Duduk bersama', [SUNSET_CINE, *fl('C01_COMPLETED', 'CANON_RIVERSIDE', 'C01_PIER_SUNSET'), cend('C01'), comp(False),
      warp(ROOM, (480, 440)), card('C02'), st('C02_PHONE')], r=60)])

# ============================================================== CHAPTER 2
S('C02_PHONE', 'C02', 'Q_C02_DATE', 'Baca pesan dari Sofia di ponsel', 'Kirim ajakan lewat ponsel', inter=[
    I('phone2', 'arland_room', A('arland_room', 'phone'), 'Lihat ponsel', [sfx('page'), sc('C02-A00'), sc('C02-FREE'), st('C02_FREE')], route='arland'),
    I('phone2', 'sofia_room', A('sofia_room', 'phone'), 'Ambil ponsel', [sfx('page'), sc('C02-S00'), st('C02_S_OUTFIT')], route='sofia')])
HARI = 'Hari bebas: '
def after_free(a_step, s_step, txt): return [toast(txt), iff({'route': 'arland'}, [st(a_step)], [st(s_step)])]
SARI = (1420, 610)
BEDS = [(1060, 860), (480, 540), (260, 660)]
HIDE = [(420, 430), (1660, 880), (240, 880)]
S('C02_FREE', 'C02', 'Q_C02_FREE', HARI + 'lakukan 2 dari 3 kegiatan (Nenek Sari di plaza, Bang Juna di arcade, Dito di taman)', counter='hari_C02', cmax=2, inter=[
    I('f2_sari', 'plaza', SARI, 'Bicara dengan Nenek Sari', [sc('F2-SIRAM-1'), *fl('F2_SIRAM_START'), it('gembor'), toast('Siram 3 petak bunga di plaza')], when={'notFlags': ['F2_SIRAM_START']}, r=70),
    *[I('f2_bed%d' % (k + 1), 'plaza', p, 'Siram bunga', [*fl('F2_BED_%d' % (k + 1)), cnt('siram'), sfx(), toast('Petak bunga %d/3 disiram' % (k + 1))],
        when={'flags': ['F2_SIRAM_START']}, hide='F2_BED_%d' % (k + 1), sprite=('props/watering.png', p[0], p[1] - 10, True), r=56) for k, p in enumerate(BEDS)],
    I('f2_sari_done', 'plaza', SARI, 'Kembali ke Nenek Sari', [sc('F2-SIRAM-2'), rm('gembor'), it('permen_jahe'), *fl('F2_SIRAM_DONE'), cnt('hari_C02'), sfx()],
      when={'count': {'siram': 3}, 'notFlags': ['F2_SIRAM_DONE']}, r=70),
    I('f2_juna', 'arcade', A('arcade', 'keeper'), 'Bicara dengan Bang Juna', [sc('F2-ARCADE-1'), mg('starcatch'), sc('F2-ARCADE-2'), it('stiker_bintang'), *fl('F2_ARCADE_DONE'), cnt('hari_C02'), sfx()],
      hide='F2_ARCADE_DONE', r=70),
    I('f2_dito', 'taman_kota', (1100, 540), 'Bicara dengan Dito', [sc('F2-DITO-1'), *fl('F2_DITO_START', 'F2_DITO_HIDING'), toast('Cari Dito: 3 tempat persembunyian di taman')],
      when={'notFlags': ['F2_DITO_START']}, r=64),
    I('f2_hide1', 'taman_kota', HIDE[0], 'Periksa semak', [sc('F2-DITO-2'), *fl('F2_HIDE_1')], when={'flags': ['F2_DITO_HIDING'], 'notFlags': ['F2_HIDE_1']}, r=56),
    I('f2_hide2', 'taman_kota', HIDE[1], 'Periksa balik bangku', [sc('F2-DITO-2'), *fl('F2_HIDE_2')], when={'flags': ['F2_HIDE_1'], 'notFlags': ['F2_HIDE_2']}, r=56),
    I('f2_hide3', 'taman_kota', HIDE[2], 'Periksa petak bunga', [sc('F2-DITO-3'), *fl('F2_HIDE_3', 'F2_DITO_DONE'), *unfl('F2_DITO_HIDING'), cnt('hari_C02'), sfx()],
      when={'flags': ['F2_HIDE_2'], 'notFlags': ['F2_HIDE_3']}, r=56)],
  complete=('hari_C02', 2, [*unfl('F2_DITO_HIDING'), rm('gembor'), *fl('C02_FREE_DONE')] + after_free('C02_A_FLORIST', 'C02_S_PRINT', 'Sudah siang. Waktunya bersiap untuk sore!')))
S('C02_A_FLORIST', 'C02', 'Q_C02_DATE', 'Beli bunga di Toko Bunga Melati (Jalan Kota, timur plaza)', inter=[
    I('florist', 'toko_bunga', A('toko_bunga', 'florist'), 'Bicara dengan Bu Melati', [sc('C02-A01'), it('bunga_pita'), sfx(), st('C02_TO_CAFE')], route='arland', r=70)])
S('C02_S_OUTFIT', 'C02', 'Q_C02_DATE', 'Pilih outfit di lemari', inter=[
    I('wardrobe', 'sofia_room', (520, 326), 'Lemari pakaian', [sc('C02-S01'), sfx('page'), sc('C02-FREE'), st('C02_FREE')], route='sofia')])
S('C02_S_PRINT', 'C02', 'Q_C02_DATE', 'Cetak foto kecil di Arcade Bintang (Jalan Kota)', inter=[
    I('juna_print', 'arcade', A('arcade', 'keeper'), 'Bicara dengan Bang Juna', [sc('C02-S02'), it('foto_kecil'), sfx(), st('C02_TO_CAFE')], route='sofia', r=70)])
S('C02_TO_CAFE', 'C02', 'Q_C02_DATE', 'Temui Sofia di Kafe Senja', 'Temui Arland di Kafe Senja', npcs=[NP('cafe', A('cafe', 'table_date_p'), 'left')], inter=[
    I('date', 'cafe', A('cafe', 'table_date_p'), 'Duduk bersama', [sc('C02-X00'), sc('C02-X01'), comp(True), st('C02_DATE')], r=64,
      lbr={'arland': 'Sapa Sofia', 'sofia': 'Sapa Arland'})])
S('C02_DATE', 'C02', 'Q_C02_DATE', 'Kencan: duduk di gazebo Taman Kota & foto di photobooth Arcade', counter='date_spots', cmax=2, inter=[
    I('gazebo', 'taman_kota', A('taman_kota', 'gazebo'), 'Duduk di gazebo', [sc('C02-X03'), cnt('date_spots'), sfx()], hide='C02_PARK_DONE'),
    I('booth', 'arcade', A('arcade', 'booth'), 'Photobooth', [mg('photobooth'), sc('C02-X02'), it('foto_berdua'), cnt('date_spots'), sfx()], hide='C02_PHOTO_UNLOCKED')],
  complete=('date_spots', 2, [toast('Langit mulai jingga...'), st('C02_SUNSET')]))
S('C02_SUNSET', 'C02', 'Q_C02_DATE', 'Lihat senja di ujung dermaga Tepi Danau', inter=[
    I('pier', 'riverside', A('riverside', 'pier_end'), 'Lihat senja', [sc('C02-X04'), rm('bunga_pita', 'arland'), it('foto_kecil', 'arland'), rm('foto_kecil', 'sofia'), it('bunga_pita', 'sofia'),
      cend('C02'), comp(False), warp(ROOM, (480, 440)), card('C03'), iff({'route': 'arland'}, [st('C03_A_IDEA')], [st('C03_S_CORNER')])], r=60)],
  tint='#ff9a5a', talpha=0.16)

# ============================================================== CHAPTER 3
S('C03_A_IDEA', 'C03', 'Q_C03_PICNIC', 'Rencanakan sesuatu di meja kerja', inter=[
    I('idea', 'arland_room', A('arland_room', 'desk_front'), 'Meja kerja', [sc('C03-A00'), sc('C03-FREE'), st('C03_FREE')], route='arland')])
S('C03_FREE', 'C03', 'Q_C03_FREE', HARI + 'kunjungi 2 lapak di Pasar Minggu (plaza)', counter='hari_C03', cmax=2,
  npcs=[NP('plaza', (1250, 760), 'down', who='juna')], inter=[
    I('f3_buah', 'plaza', (760, 660), 'Lapak buah', [sc('F3-BUAH'), it('buah_pasar'), *fl('F3_BUAH_DONE'), cnt('hari_C03'), sfx()], hide='F3_BUAH_DONE', r=64),
    I('f3_buku', 'plaza', (820, 980), 'Lapak buku bekas', [sc('F3-BUKU'), it('buku_pasar'), *fl('F3_BUKU_DONE'), cnt('hari_C03'), sfx('page')], hide='F3_BUKU_DONE', r=64),
    I('f3_gelang', 'plaza', (1250, 760), 'Lempar gelang', [sc('F3-GELANG-1'), mg('ringtoss'), sc('F3-GELANG-2'), it('gantungan_bintang'), *fl('F3_GELANG_DONE'), cnt('hari_C03'), sfx()],
      hide='F3_GELANG_DONE', r=64)],
  complete=('hari_C03', 2, [*fl('C03_FREE_DONE')] + after_free('C03_A_INGREDIENTS', 'C03_S_DECOR', 'Pasar mulai sepi. Kembali ke rencana hari ini!')))
S('C03_A_INGREDIENTS', 'C03', 'Q_C03_PICNIC', 'Kumpulkan bahan: stroberi (kulkas dapur kafe), madu (Nenek Sari), daun mint (taman)', counter='bahan', cmax=3, inter=[
    I('fridge', 'dapur', A('dapur', 'fridge'), 'Ambil stroberi', [sc('C03-A02'), it('stroberi'), cnt('bahan'), sfx()], route='arland', hide='C03_GOT_BERRY'),
    I('honey', 'plaza', (1420, 610), 'Minta madu', [sc('C03-A03'), it('madu'), cnt('bahan'), sfx()], route='arland', hide='C03_GOT_HONEY'),
    I('mint', 'taman_kota', A('taman_kota', 'flowers_w'), 'Petik daun mint', [sc('C03-A04'), it('daun_mint'), cnt('bahan'), sfx()], route='arland', hide='C03_GOT_MINT')],
  complete=('bahan', 3, [toast('Semua bahan lengkap! Ke dapur Kafe Senja.'), st('C03_A_KITCHEN')]))
S('C03_A_KITCHEN', 'C03', 'Q_C03_PICNIC', 'Pergi ke dapur Kafe Senja (pintu kanan di dalam kafe)', enter=('dapur', [comp(True), sc('C03-A01'), st('C03_COOK')]))
S('C03_S_CORNER', 'C03', 'Q_C03_CORNER', 'Lihat kotak kenangan di sudut kamar', inter=[
    I('corner', 'sofia_room', A('sofia_room', 'corner'), 'Kotak kenangan', [sc('C03-S00'), sc('C03-S01'), sc('C03-FREE'), st('C03_FREE')], route='sofia')])
S('C03_S_DECOR', 'C03', 'Q_C03_CORNER', 'Kumpulkan dekorasi: bunga kering (Bu Melati), lampu tumbler (Kak Raka), bingkai (Bang Juna)', counter='dekor', cmax=3, inter=[
    I('dried', 'toko_bunga', A('toko_bunga', 'florist'), 'Minta bunga kering', [sc('C03-S03'), it('bunga_kering'), cnt('dekor'), sfx()], route='sofia', hide='C03_GOT_DRIED', r=70),
    I('lights', 'cafe', A('cafe', 'barista'), 'Minta lampu tumbler', [sc('C03-S04'), it('lampu_tumbler'), cnt('dekor'), sfx()], route='sofia', hide='C03_GOT_LIGHTS', r=70),
    I('frame', 'arcade', A('arcade', 'keeper'), 'Minta bingkai', [sc('C03-S05'), it('bingkai_bintang'), cnt('dekor'), sfx()], route='sofia', hide='C03_GOT_FRAME', r=70)],
  complete=('dekor', 3, [toast('Dekorasi lengkap! Pulang dan tata sudut kenangan.'), st('C03_S_ARRANGE')]))
S('C03_S_ARRANGE', 'C03', 'Q_C03_CORNER', 'Tata sudut kenangan di kamar', inter=[
    I('arrange', 'sofia_room', A('sofia_room', 'corner'), 'Tata sudut kenangan', [sc('C03-S02'), sfx(), st('C03_S_KITCHEN')], route='sofia')])
S('C03_S_KITCHEN', 'C03', 'Q_C03_PICNIC', 'Susul Arland ke dapur Kafe Senja', enter=('dapur', [comp(True), sc('C03-S06'), st('C03_COOK')]))
S('C03_COOK', 'C03', 'Q_C03_PICNIC', 'Masak bersama di kompor', inter=[
    I('stove', 'dapur', A('dapur', 'stove'), 'Masak bersama', [mg('cooking'), sc('C03-X01'), it('roti_lapis'), *fl('C03_COOKED'), st('C03_V26_DETAILS')])])
# v2.6 — ruang untuk dua perspektif dalam kegiatan sehari-hari.
S('C03_V26_DETAILS', 'C03', 'Q_C03_PICNIC',
  'Periksa catatan resep dan kemas bekal bersama', 'Tuliskan kenangan resep dan kemas bekal bersama',
  counter='v26_c03_details', cmax=2, inter=[
    I('v26_c03_recipe', 'dapur', A('dapur', 'stove'), 'Catatan di balik resep',
      [iff({'route': 'arland'}, [sc('V26-C03-A1')], [sc('V26-C03-S1')]),
       *fl('V26_C03_RECIPE'), cnt('v26_c03_details'), sfx('page')], hide='V26_C03_RECIPE', r=66),
    I('v26_c03_packing', 'dapur', A('dapur', 'counter'), 'Bungkus bekal berdua',
      [iff({'route': 'arland'}, [sc('V26-C03-A2')], [sc('V26-C03-S2')]),
       *fl('V26_C03_PACKED'), cnt('v26_c03_details'), sfx('paper_fold')], hide='V26_C03_PACKED', r=66)],
  complete=('v26_c03_details', 2, [*fl('V26_C03_FINISHED'), st('C03_PICNIC')]))
S('C03_PICNIC', 'C03', 'Q_C03_PICNIC', 'Piknik di selimut Taman Kota', inter=[
    I('picnic', 'taman_kota', A('taman_kota', 'picnic'), 'Mulai piknik', [sc('C03-X02'), rm('roti_lapis'), cend('C03'), comp(False), warp(ROOM, (480, 440)), card('C04'),
      iff({'route': 'arland'}, [st('C04_A_WAKE')], [st('C04_S_WAKE')])])])

# ============================================================== CHAPTER 4 (hujan)
S('C04_A_WAKE', 'C04', 'Q_C04_RAIN', 'Isi daya ponsel di meja', inter=[
    I('phone4', 'arland_room', A('arland_room', 'phone'), 'Ponsel', [sfx('page'), sc('C04-A00'), st('C04_A_CAFE')], route='arland')], weather=RAIN)
S('C04_A_CAFE', 'C04', 'Q_C04_RAIN', 'Cari Sofia di Kafe Senja', weather=RAIN, inter=[
    I('raka4', 'cafe', A('cafe', 'barista'), 'Bicara dengan Kak Raka', [sc('C04-A02'), st('C04_A_HALTE')], route='arland', r=70)])
HALTE = A('perumahan', 'halte'); MBOX = A('perumahan', 'mailbox_old')
HALTE_CINE = cine(
    C('music', id='cinema_rain_conflict'),C('bars', on=True, t=0.5), C('move', who='player', to=[HALTE[0] + 6, HALTE[1] - 4], dir='down'),
    C('cam', x=HALTE[0], y=HALTE[1] - 30, zoom=1.5, t=2.0), C('caption', text='Halte, Distrik Perumahan', sub='Hujan belum juga reda', t=2.6),
    C('say', scene='C04-A-HALTE', n=2), C('pose', who='player', pose='bow', t=1.6, block=True), C('say', scene='C04-A01', from_=1),
    C('cam', x=MBOX[0], y=MBOX[1] - 30, zoom=1.4, t=1.6), C('fx', kind='glow', x=MBOX[0], y=MBOX[1] - 20, t=4), C('say', scene='C04-A-HALTE', from_=2),
    C('pose', who='player', pose='none'), C('cam', on='player', zoom=1.0, t=1.0), C('bars', on=False, t=0.4))
S('C04_A_HALTE', 'C04', 'Q_C04_RAIN', 'Berteduh dan berpikir di halte Jalan Kota', weather=RAIN, inter=[
    I('halte', 'perumahan', HALTE, 'Berteduh di halte', [HALTE_CINE, st('C04_A_MAILBOX')], route='arland', r=70)])
S('C04_A_MAILBOX', 'C04', 'Q_C04_RAIN', 'Periksa kotak surat tua di samping halte', weather=RAIN, inter=[
    I('mbox', 'perumahan', MBOX, 'Kotak surat tua', [cine(C('face', who='player', dir='up'), C('pose', who='player', pose='reach', t=1.0, block=True)), sc('C04-A-LETTER'),
      it('surat_wira'), *fl('C04_LETTER_WIRA'), sc('C04-A03'), st('C04_Q_A_REPLY')], route='arland', r=56)])
S('C04_Q_A_REPLY', 'C04', 'Q_C04_RAIN', 'Baca ulang surat Pak Wira di bangku halte', weather=RAIN, inter=[
    I('q_a_reply', 'perumahan', A('perumahan', 'halte'), 'Dengarkan hujan', [sc('Q-C04-A'), *fl('Q_C04_A_REPLY'), st('C04_A_PARK')], route='arland', r=72)])
S('C04_A_PARK', 'C04', 'Q_C04_RAIN', 'Temui Sofia di gazebo Taman Kota', weather=RAIN, npcs=[NP('taman_kota', A('taman_kota', 'gazebo'), 'down')], inter=[
    I('meet4', 'taman_kota', A('taman_kota', 'gazebo'), 'Sapa Sofia', [{'do':'music','id':'cinema_reconciliation'}, sc('C04-X00'), warp('lantern_field', A('lantern_field', 'arrive'), 'right'), comp(True), sc('C04-X02'), st('C04_LIGHTS')], route='arland')])
S('C04_S_WAKE', 'C04', 'Q_C04_RAIN', 'Lihat ponsel di meja', weather=RAIN, inter=[
    I('phone4', 'sofia_room', A('sofia_room', 'phone'), 'Ponsel', [sfx('page'), sc('C04-S00'), st('C04_S_CAFE')], route='sofia')])
S('C04_S_CAFE', 'C04', 'Q_C04_RAIN', 'Mampir ke Kafe Senja', weather=RAIN, inter=[
    I('raka4', 'cafe', A('cafe', 'barista'), 'Bicara dengan Kak Raka', [sc('C04-S02'), st('C04_S_LIBRARY')], route='sofia', r=70)])
S('C04_S_LIBRARY', 'C04', 'Q_C04_RAIN', 'Berteduh di Perpustakaan Kota (Distrik Perumahan)', weather=RAIN, inter=[
    I('laras4', 'perpustakaan', LIB('counter_front'), 'Bicara dengan Bu Laras', [sc('C04-S-LIBRARY'), it('surat_sari'), st('C04_S_READ')], route='sofia', r=66)])
SOFA = LIB('sofa')
READ_CINE = cine(
    C('music', id='cinema_rain_conflict'),C('bars', on=True, t=0.5), C('move', who='player', to=[SOFA[0] - 14, SOFA[1] - 22], dir='down'), C('pose', who='player', pose='sit'),
    C('cam', x=SOFA[0], y=SOFA[1] - 50, zoom=1.55, t=1.8), C('tint', color='2a3550', a=0.18, t=2.0),
    C('fx', kind='glow', x=SOFA[0], y=SOFA[1] - 18, t=6.0), C('say', scene='C04-S-LETTER', n=4),
    C('pose', who='player', pose='bow', t=1.6, block=True), C('say', scene='C04-S-LETTER', from_=4, n=2),
    C('pose', who='player', pose='none'), C('say', scene='C04-S-LETTER', from_=6), C('move', who='player', to=[SOFA[0], SOFA[1] + 6], dir='down'),
    C('cam', on='player', zoom=1.0, t=1.0), C('bars', on=False, t=0.4))
S('C04_S_READ', 'C04', 'Q_C04_RAIN', 'Baca surat itu di sofa baca', weather=RAIN, inter=[
    I('read4', 'perpustakaan', SOFA, 'Baca surat di sofa', [READ_CINE, *fl('C04_LETTER_SARI'), st('C04_Q_S_REPLY')], route='sofia', r=60)])
S('C04_Q_S_REPLY', 'C04', 'Q_C04_RAIN', 'Tuliskan hal yang tidak sempat Nenek Sari ucapkan', weather=RAIN, inter=[
    I('q_s_reply', 'perpustakaan', LIB('table2'), 'Tulis di kertas', [sc('Q-C04-S'), *fl('Q_C04_S_REPLY'), st('C04_S_PARK')], route='sofia', r=70)])
S('C04_S_PARK', 'C04', 'Q_C04_RAIN', 'Berteduh di gazebo Taman Kota', weather=RAIN, inter=[
    I('gazebo4', 'taman_kota', A('taman_kota', 'gazebo'), 'Berteduh di gazebo', [sc('C04-S01'), st('C04_S_MEET')], route='sofia')])
S('C04_S_MEET', 'C04', 'Q_C04_RAIN', 'Bicara dengan Arland', weather=RAIN, npcs=[NP('taman_kota', A('taman_kota', 'bench_n'), 'right')], inter=[
    I('meet4', 'taman_kota', A('taman_kota', 'bench_n'), 'Sapa Arland', [{'do':'music','id':'cinema_reconciliation'}, sc('C04-X00'), warp('lantern_field', A('lantern_field', 'arrive'), 'right'), comp(True), sc('C04-X02'), st('C04_LIGHTS')], route='sofia')])
S('C04_LIGHTS', 'C04', 'Q_C04_LANTERN', 'Temukan Cahaya Mendengar & Cahaya Jujur di Lantern Field', counter='cahaya', cmax=2, inter=[
    I('light_listen', 'lantern_field', (560, 1010), 'Cahaya kecil', [sc('C04-L01'), cnt('cahaya'), sfx()], hide='C04_LIGHT_LISTEN', sprite=('props/light_orb.png', 560, 990, True)),
    I('light_honest', 'lantern_field', (1420, 360), 'Cahaya kecil', [sc('C04-L02'), cnt('cahaya'), sfx()], hide='C04_LIGHT_HONEST', sprite=('props/light_orb.png', 1420, 340, True))],
  complete=('cahaya', 2, [toast('Bawa kedua cahaya ke altar lentera di tengah padang.'), st('C04_PUZZLE')]))
S('C04_PUZZLE', 'C04', 'Q_C04_LANTERN', 'Nyalakan lentera di altar tengah padang', inter=[
    I('shrine', 'lantern_field', A('lantern_field', 'shrine'), 'Altar lentera', [mg('lanterns'), sfx(), sc('C04-X01'), *fl('C04_LANTERNS_LIT'),
      warp('taman_kota', A('taman_kota', 'gazebo')), sc('C04-X03'), st('C04_V26_RECONCILE')], r=80)])
# v2.6 — rekonsiliasi bukan hanya akhir satu puzzle; ada percakapan yang bisa dimainkan.
S('C04_V26_RECONCILE', 'C04', 'Q_C04_LANTERN', 'Bicarakan perasaan di gazebo dan lihat pantulan kolam',
  counter='v26_rain', cmax=2, inter=[
    I('v26_c04_gazebo', 'taman_kota', A('taman_kota', 'gazebo'), 'Duduk dan bicara',
      [sc('V26-C04-ME'), *fl('V26_C04_GAZEBO'), cnt('v26_rain'), sfx('page')], hide='V26_C04_GAZEBO', r=65),
    I('v26_c04_pond', 'taman_kota', A('taman_kota', 'pond_n'), 'Lihat pantulan kolam',
      [sc('V26-C04-POND'), *fl('V26_C04_POND'), cnt('v26_rain'), sfx('sparkle')], hide='V26_C04_POND', r=65)],
  complete=('v26_rain', 2, [st('C04_V26_VOW')]))
S('C04_V26_VOW', 'C04', 'Q_C04_LANTERN', 'Tulis janji yang bisa dilakukan berdua di bangku taman', inter=[
    I('v26_c04_vow', 'taman_kota', A('taman_kota', 'bench_n'), 'Janji untuk besok',
      [cine(C('music', id='cinema_reconciliation'), C('bars', on=True, t=0.4),
            C('cam', x=A('taman_kota', 'bench_n')[0], y=A('taman_kota', 'bench_n')[1] - 30, zoom=1.28, t=1.3),
            C('fx', kind='petals', on='player', t=4.0),
            C('caption', text='Setelah Hujan', sub='Belajar saling mendengar', t=2.6),
            C('cam', on='player', zoom=1.0, t=1.0), C('bars', on=False, t=0.35)),
       sc('V26-C04-VOW'), cend('C04'), comp(False), warp(ROOM, (480, 440)), card('C05'), sc('C05-FREE'), st('C05_FREE')], r=70)])
SUNSET = '#ff9a5a'
F5_LANTERNS = [(1440, 560), (720, 620), (1300, 1110), (1640, 780)]
S('C05_FREE', 'C05', 'Q_C05_FREE', HARI + 'bantu 2 persiapan festival (Kak Raka, Bu Melati, papan pengumuman plaza)', counter='hari_C05', cmax=2, tint=SUNSET, talpha=0.14, inter=[
    I('f5_raka', 'cafe', A('cafe', 'barista'), 'Bicara dengan Kak Raka', [sc('F5-TEH-1'), mg('pour'), sc('F5-TEH-2'), it('teh_rempah'), *fl('F5_TEH_DONE'), cnt('hari_C05'), sfx()], hide='F5_TEH_DONE', r=70),
    I('f5_melati', 'toko_bunga', A('toko_bunga', 'florist'), 'Bicara dengan Bu Melati', [sc('F5-LENTERA-1'), *fl('F5_LANTERN_START'), it('lentera_kertas'), toast('Gantung 4 lentera di Taman Kota')],
      when={'notFlags': ['F5_LANTERN_START']}, r=70),
    *[I('f5_lantern%d' % (k + 1), 'taman_kota', p, 'Gantung lentera', [*fl('F5_LANTERN_%d' % (k + 1)), cnt('lentera_f5'), sfx(), toast('Lentera %d/4' % (k + 1)),
        iff({'count': {'lentera_f5': 4}}, [rm('lentera_kertas'), toast('Semua lentera tergantung! Kembali ke Bu Melati.')])],
        when={'flags': ['F5_LANTERN_START']}, hide='F5_LANTERN_%d' % (k + 1), r=56) for k, p in enumerate(F5_LANTERNS)],
    I('f5_melati_done', 'toko_bunga', A('toko_bunga', 'florist'), 'Lapor ke Bu Melati', [sc('F5-LENTERA-2'), *fl('F5_LANTERN_DONE'), cnt('hari_C05'), sfx()],
      when={'count': {'lentera_f5': 4}, 'notFlags': ['F5_LANTERN_DONE']}, r=70),
    I('f5_card', 'plaza', (1220, 500), 'Tulis kartu harapan', [sc('F5-KARTU'), *fl('F5_KARTU_DONE'), cnt('hari_C05'), sfx('page')], hide='F5_KARTU_DONE', r=60)],
  complete=('hari_C05', 2, [rm('lentera_kertas'), *fl('C05_FREE_DONE'), toast('Matahari terbenam... malam ini terasa istimewa.'), warp(ROOM, (480, 440)),
                            iff({'route': 'arland'}, [st('C05_A_START')], [st('C05_S_START')])]))

# ============================================================== CHAPTER 5 (malam)
S('C05_A_START', 'C05', 'Q_C05_STARS', 'Lihat ponsel yang bergetar', tint=NIGHT, talpha=0.32, inter=[
    I('phone5', 'arland_room', A('arland_room', 'phone'), 'Ponsel', [sfx('page'), sc('C05-A00'), st('C05_A_PIER')], route='arland')])
S('C05_A_PIER', 'C05', 'Q_C05_STARS', 'Pergi ke ujung dermaga Tepi Danau', tint=NIGHT, talpha=0.32, inter=[
    I('portal_pier', 'riverside', A('riverside', 'pier_end'), 'Sentuh pantulan bintang', [sfx(), warp('star_path', A('star_path', 'arrive'), 'right'), sc('C05-A02'), st('C05_A_STARS')], route='arland', r=60)])
S('C05_A_STARS', 'C05', 'Q_C05_STARS', 'Nyalakan 5 batu bintang di Star Path', counter='bintang', cmax=5, inter=[
    I('stone%d' % k, 'star_path', A('star_path', 'stone%d' % k), 'Batu bintang', [*fl('C05_STONE_%d' % k), cnt('bintang'), sfx(),
      say([('narrator', 'neutral', t)])], route='arland', hide='C05_STONE_%d' % k)
    for k, t in [(1, 'Batu pertama berdenting. Sebuah garis cahaya mengarah ke timur.'), (2, 'Batu kedua menyala. Ada ukiran kecil: "Dengarkan sampai selesai."'),
                 (3, 'Batu ketiga hangat, seperti teh melati yang baru diseduh.'), (4, 'Batu keempat memantulkan bayangan gazebo di hari hujan.'),
                 (5, 'Batu kelima menyala paling terang. Di tengah jalur, sesuatu berputar pelan.')]],
  complete=('bintang', 5, [toast('Kompas muncul di tengah jalur!'), st('C05_A_COMPASS')]))
S('C05_A_COMPASS', 'C05', 'Q_C05_STARS', 'Ambil kompas bercahaya di tengah jalur', inter=[
    I('compass', 'star_path', A('star_path', 'compass'), 'Kompas bercahaya', [sc('C05-A01'), it('kompas'), sfx(), st('C05_TO_VILLAGE')], route='arland',
      sprite=('props/compass.png', A('star_path', 'compass')[0], A('star_path', 'compass')[1] - 20, True))])
S('C05_S_START', 'C05', 'Q_C05_STARS', 'Lihat Memory Book di sudut kenangan', tint=NIGHT, talpha=0.32, inter=[
    I('book5', 'sofia_room', A('sofia_room', 'corner'), 'Memory Book', [sfx(), sc('C05-S00'), st('C05_S_POND')], route='sofia')])
S('C05_S_POND', 'C05', 'Q_C05_STARS', 'Pergi ke tepi utara kolam Taman Kota', tint=NIGHT, talpha=0.32, inter=[
    I('portal_pond', 'taman_kota', A('taman_kota', 'pond_n'), 'Sentuh permukaan kolam', [sfx(), warp('lantern_field', A('lantern_field', 'arrive'), 'right'), sc('C05-S02'), st('C05_S_SPARKS')], route='sofia', r=70)])
SPARKS = [(420, 1020), (900, 860), (1300, 900), (1180, 300)]
S('C05_S_SPARKS', 'C05', 'Q_C05_STARS', 'Tangkap 4 percik cahaya di Lantern Field', counter='percik', cmax=4, inter=[
    I('spark%d' % (k + 1), 'lantern_field', p, 'Percik cahaya', [*fl('C05_SPARK_%d' % (k + 1)), cnt('percik'), sfx(), sc('C05-S03')], route='sofia', hide='C05_SPARK_%d' % (k + 1),
      sprite=('props/spark.png', p[0], p[1] - 16, True)) for k, p in enumerate(SPARKS)],
  complete=('percik', 4, [toast('Percik cahaya terbang ke altar!'), st('C05_S_SHRINE')]))
S('C05_S_SHRINE', 'C05', 'Q_C05_STARS', 'Lihat warna lentera di altar tengah', inter=[
    I('shrine5', 'lantern_field', A('lantern_field', 'shrine'), 'Altar lentera', [sc('C05-S01'), it('lentera_kecil'), sfx(), st('C05_TO_VILLAGE')], route='sofia', r=80)])
S('C05_TO_VILLAGE', 'C05', 'Q_C05_STARS', 'Lanjutkan jalur ke timur menuju Starfall Village', enter=('starfall_village', [toast('Starfall Village'), st('C05_MEET')]))
S('C05_MEET', 'C05', 'Q_C05_STARS', 'Temui Sofia di desa', 'Temui Arland di desa', npcs=[NP('starfall_village', (880, 640), 'left')], inter=[
    I('meet5', 'starfall_village', (880, 640), 'Sapa', [sc('C05-X02'), comp(True), sc('C05-X03'), st('C05_STARMAP')], lbr={'arland': 'Sapa Sofia', 'sofia': 'Sapa Arland'})])
S('C05_STARMAP', 'C05', 'Q_C05_STARS', 'Lengkapi peta bintang di altar desa', inter=[
    I('starmap', 'starfall_village', A('starfall_village', 'starmap'), 'Peta bintang', [mg('starmap'), sfx(), sc('C05-X01'), sc('C05-X04'), iff({'route': 'arland'}, [st('C05_V26_A_SURVEY')], [st('C05_V26_S_NOTES')])], r=72)])

# v2.6 — jalur malam. Arland mengukur arah; Sofia menyusun kalimat.
_A_V26_SPOTS = [('bench', 'Periksa panah di bangku', 'V26-C05-A2'),
                ('house_mid', 'Periksa pantulan rumah tengah', 'V26-C05-A3'),
                ('center', 'Ukur arah di tengah desa', 'V26-C05-A4')]
S('C05_V26_A_SURVEY', 'C05', 'Q_C05_STARS',
  'Temukan tiga petunjuk peta: bangku, rumah tengah, dan lapangan', counter='v26_survey', cmax=3,
  onstart=[sc('V26-C05-A1')], inter=[
    I('v26_a_clue_%d' % i, 'starfall_village', A('starfall_village', a), label,
      [sc(scene), *fl('V26_A_CLUE_%d' % i), cnt('v26_survey'), sfx('page')],
      route='arland', hide='V26_A_CLUE_%d' % i, r=70)
    for i, (a, label, scene) in enumerate(_A_V26_SPOTS, 1)],
  complete=('v26_survey', 3, [st('C05_V26_A_KEY')]))
S('C05_V26_A_KEY', 'C05', 'Q_C05_STARS', 'Susun simbol dari tiga petunjuk arah di bangku desa', inter=[
    I('v26_a_key', 'starfall_village', A('starfall_village', 'bench'), 'Kunci jarak Arland',
      [sc('V26-C05-A5'), mg('v26_night_compass'), *fl('V26_C05_A_SOLVED'), st('C05_V26_NIGHT_TALK')],
      route='arland', r=72)])
_S_V26_SPOTS = [('house_mid', 'Baca tulisan di rumah tengah', 'V26-C05-S2'),
                ('bench', 'Baca ukiran di bangku', 'V26-C05-S3'),
                ('center', 'Temukan potongan di tengah desa', 'V26-C05-S4')]
S('C05_V26_S_NOTES', 'C05', 'Q_C05_STARS',
  'Kumpulkan tiga potongan kalimat di Starfall Village', counter='v26_notes', cmax=3,
  onstart=[sc('V26-C05-S1')], inter=[
    I('v26_s_note_%d' % i, 'starfall_village', A('starfall_village', a), label,
      [sc(scene), *fl('V26_S_NOTE_%d' % i), cnt('v26_notes'), sfx('page')],
      route='sofia', hide='V26_S_NOTE_%d' % i, r=70)
    for i, (a, label, scene) in enumerate(_S_V26_SPOTS, 1)],
  complete=('v26_notes', 3, [st('C05_V26_S_COMPOSE')]))
S('C05_V26_S_COMPOSE', 'C05', 'Q_C05_STARS', 'Urutkan empat potongan kalimat dalam Memory Book', inter=[
    I('v26_s_compose', 'starfall_village', A('starfall_village', 'bench'), 'Empat halaman Sofia',
      [sc('V26-C05-S5'), mg('v26_night_pages'), *fl('V26_C05_S_SOLVED'), st('C05_V26_NIGHT_TALK')],
      route='sofia', r=72)])
S('C05_V26_NIGHT_TALK', 'C05', 'Q_C05_STARS', 'Duduk berdua dan ceritakan yang ditemukan', inter=[
    I('v26_night_talk', 'starfall_village', A('starfall_village', 'bench'), 'Duduk di bangku bintang',
      [cine(C('music', id='star_road'), C('bars', on=True, t=0.4),
            C('cam', x=A('starfall_village', 'bench')[0], y=A('starfall_village', 'bench')[1] - 25, zoom=1.35, t=1.6),
            C('fx', kind='stars', on='partner', t=5.0),
            C('caption', text='Satu Langit', sub='Dua cara menemukan jalan', t=2.4),
            C('cam', on='player', zoom=1.0, t=1.1), C('bars', on=False, t=0.4)),
       sc('V26-C05-TALK'), sc('V26-C05-CHOICE'), *fl('V26_C05_TOGETHER'), st('C05_V26_STARGAZE')], r=75)])
S('C05_V26_STARGAZE', 'C05', 'Q_C05_STARS', 'Lihat bintang jatuh dari lapangan desa sebelum berangkat', inter=[
    I('v26_stargaze', 'starfall_village', A('starfall_village', 'center'), 'Lihat langit bersama',
      [sc('V26-C05-STAR'), *fl('V26_C05_STARGAZE'), st('C05_Q_ECHO')], r=72)])

# Petunjuk akhir dari peta bintang; narasi C05 berbeda menurut route, namun canon tidak bercabang.

S('C05_Q_ECHO', 'C05', 'Q_C05_STARS', 'Baca pesan kecil di bawah peta bintang', inter=[
    I('q_echo', 'starfall_village', A('starfall_village', 'bench'), 'Pesan di bangku', [
        iff({'route': 'arland'}, [sc('Q-C05-A')], [sc('Q-C05-S')]), *fl('Q_C05_ECHO'),
        cend('C05'), card('C06'), warp('eternal_garden', A('eternal_garden', 'arrive'), 'up'), sc('C06-X00'), st('C06_PETALS')], r=72)])

# ============================================================== CHAPTER 6
PETALS = [A('eternal_garden', 'pond'), A('eternal_garden', 'gazebo'), (960, 1210)]
S('C06_PETALS', 'C06', 'Q_C06_TOMORROW', 'Kumpulkan 3 Kelopak Esok di Eternal Garden', counter='kelopak', cmax=3, inter=[
    I('petal%d' % (k + 1), 'eternal_garden', p, 'Kelopak Esok', [*fl('C06_PETAL_%d' % (k + 1)), cnt('kelopak'), sfx(), sc('C06-P0%d' % (k + 1))], hide='C06_PETAL_%d' % (k + 1),
      sprite=('props/petal.png', p[0], p[1] - 14, True)) for k, p in enumerate(PETALS)],
  complete=('kelopak', 3, [toast('Tiga kelopak membuka jejak kenangan. Cari petunjuk The Quiet.'), iff({'route': 'arland'}, [st('C06_Q_A_TRACES')], [st('C06_Q_S_TRACES')])]))
# v1.8 — klimaks investigasi utama. Arland menyusun bukti kronologis; Sofia menyusun rasa dan pesan.
QA_SPOTS = [('pond', 'Pantulan pertama'), ('gazebo', 'Jejak kedua'), ('bench', 'Titik ketiga')]
QS_SPOTS = [('bench', 'Kata pertama'), ('gazebo', 'Kenangan kedua'), ('pond', 'Suara ketiga')]
S('C06_Q_A_TRACES', 'C06', 'Q_C06_TOMORROW', 'Lacak 3 jejak di kebun: kolam, gazebo, bangku', counter='quiet_a', cmax=3, inter=[
    I('q_a_%d' % i, 'eternal_garden', A('eternal_garden', area), label,
      [sc('Q-C06-A%d' % i), *fl('Q_C06_A_TRACE_%d' % i), cnt('quiet_a'), sfx()],
      route='arland', hide='Q_C06_A_TRACE_%d' % i, r=68)
    for i, (area, label) in enumerate(QA_SPOTS, 1)],
  complete=('quiet_a', 3, [toast('Tiga jejak menyatu. Buka kunci simbol di bawah pohon.'), st('C06_Q_A_CIPHER')]))
S('C06_Q_S_TRACES', 'C06', 'Q_C06_TOMORROW', 'Dengarkan 3 pesan: bangku, gazebo, kolam', counter='quiet_s', cmax=3, inter=[
    I('q_s_%d' % i, 'eternal_garden', A('eternal_garden', area), label,
      [sc('Q-C06-S%d' % i), *fl('Q_C06_S_TRACE_%d' % i), cnt('quiet_s'), sfx()],
      route='sofia', hide='Q_C06_S_TRACE_%d' % i, r=68)
    for i, (area, label) in enumerate(QS_SPOTS, 1)],
  complete=('quiet_s', 3, [toast('Tiga pesan tersusun. Satukan halaman di bangku batu.'), st('C06_Q_S_PAGES')]))
S('C06_Q_A_CIPHER', 'C06', 'Q_C06_TOMORROW', 'Pecahkan kunci simbol dari denah Pak Wira', inter=[
    I('q_a_cipher', 'eternal_garden', A('eternal_garden', 'tree'), 'Kunci tiga simbol',
      [sc('Q-C06-A4'), mg('quiet_cipher'), *fl('Q_C06_A_SOLVED'), st('C06_Q_REVEAL')], route='arland', r=78)])
S('C06_Q_S_PAGES', 'C06', 'Q_C06_TOMORROW', 'Susun empat halaman pesan dari Nenek Sari', inter=[
    I('q_s_pages', 'eternal_garden', A('eternal_garden', 'bench'), 'Empat halaman',
      [sc('Q-C06-S4'), mg('quiet_pages'), *fl('Q_C06_S_SOLVED'), st('C06_Q_REVEAL')], route='sofia', r=78)])
S('C06_Q_REVEAL', 'C06', 'Q_C06_TOMORROW', 'Ungkap The Quiet bersama pasangan di Pohon Harapan', inter=[
    I('q_reveal', 'eternal_garden', A('eternal_garden', 'tree'), 'Halaman yang memudar', [
      cine(C('music', id='cinema_quiet'), C('bars', on=True, t=0.4),
           C('cam', x=A('eternal_garden', 'tree')[0], y=A('eternal_garden', 'tree')[1] - 40, zoom=1.45, t=1.6),
           C('fx', kind='restore', x=A('eternal_garden', 'tree')[0], y=A('eternal_garden', 'tree')[1] - 30, t=5.0),
           C('caption', text='The Quiet', sub='Suara yang kembali didengar', t=2.7),
           C('cam', on='player', zoom=1.0, t=1.1), C('bars', on=False, t=0.3)),
      sc('Q-C06-REVEAL'), iff({'route': 'arland'}, [sc('Q-C06-A5')], [sc('Q-C06-S5')]),
      *fl('THE_QUIET_REVEALED'), it('halaman_suara'), sfx(), st('C06_LETTER')], r=80)])

S('C06_LETTER', 'C06', 'Q_C06_TOMORROW', 'Tulis surat harapan di bangku batu dekat pohon', inter=[
    I('letter_a', 'eternal_garden', A('eternal_garden', 'wish_a'), 'Tulis surat', [sc('C06-A01'), it('surat_esok'), sfx('page'), st('C06_TREE')], route='arland'),
    I('letter_s', 'eternal_garden', A('eternal_garden', 'wish_s'), 'Tulis surat', [sc('C06-S01'), it('surat_esok'), sfx('page'), st('C06_TREE')], route='sofia')])
S('C06_TREE', 'C06', 'Q_C06_TOMORROW', 'Gantungkan surat di Pohon Harapan', inter=[
    I('tree', 'eternal_garden', A('eternal_garden', 'tree'), 'Pohon Harapan', [sc('C06-X02'), rm('surat_esok'), st('C06_FINAL')], r=80)])
S('C06_FINAL', 'C06', 'Q_C06_TOMORROW', 'Susun halaman-halaman kenangan di bawah pohon', inter=[
    I('pages', 'eternal_garden', A('eternal_garden', 'final'), 'Halaman kenangan', [mg('pages'), sfx(), sc('C06-X01'), sc('C06-X03'), cend('C06'), {'do': 'credits'},
      warp('plaza', A('plaza', 'fountain_front')), comp(True), card('EPI'), sc('EPI-X01'), sc('EPI-FEST-0'), st('EPI_FEST_GO')], r=80)])
FEST = {'raka': (1360, 560), 'melati': (1180, 700), 'juna': (880, 500), 'udin': (360, 660)}
S('EPI_FEST_GO', 'EPI', 'Q_EPI_FEST', 'Datang ke Festival Lentera di Taman Kota', tint=SUNSET, talpha=0.18,
  enter=('taman_kota', [sc('EPI-FEST-1'), *fl('F5_LANTERN_1', 'F5_LANTERN_2', 'F5_LANTERN_3', 'F5_LANTERN_4', 'EPI_FESTIVAL_START'), st('EPI_SARI_CLOSURE')]))
S('EPI_SARI_CLOSURE', 'EPI', 'Q_EPI_FEST', 'Temui Nenek Sari dan serahkan halaman Pak Wira di taman',
  npcs=[NP('taman_kota', A('taman_kota', 'bench_n'), 'down', who='sari')], inter=[
    I('q_sari_closure', 'taman_kota', A('taman_kota', 'bench_n'), 'Nenek Sari: halaman Wira', [
      sc('Q-EPI-SARI'), iff({'route': 'arland'}, [sc('Q-EPI-A')], [sc('Q-EPI-S')]),
      rm('halaman_suara'), it('pembatas_wira'), *fl('Q_SARI_CLOSURE'), sfx('page'), st('EPI_FEST')], r=80)])
S('EPI_FEST', 'EPI', 'Q_EPI_FEST', 'Festival: nikmati 3 kegiatan (teh, mahkota bunga, Hujan Bintang, cerita Pak Udin)', counter='festival', cmax=3, tint=NIGHT, talpha=0.24,
  npcs=[NP('taman_kota', p, 'down', who=w) for w, p in FEST.items()], inter=[
    I('fest_raka', 'taman_kota', FEST['raka'], 'Teh rempah', [sc('EPI-FEST-TEH'), *fl('FEST_TEH'), cnt('festival'), sfx()], hide='FEST_TEH', r=64),
    I('fest_melati', 'taman_kota', FEST['melati'], 'Mahkota bunga', [sc('EPI-FEST-MAHKOTA'), it('mahkota_bunga'), *fl('FEST_MAHKOTA'), cnt('festival'), sfx()], hide='FEST_MAHKOTA', r=64),
    I('fest_juna', 'taman_kota', FEST['juna'], 'Hujan Bintang', [sc('EPI-FEST-BINTANG'), mg('starcatch'), *fl('FEST_BINTANG'), cnt('festival'), sfx()], hide='FEST_BINTANG', r=64),
    I('fest_udin', 'taman_kota', FEST['udin'], 'Dengar cerita Pak Udin', [sc('EPI-FEST-UDIN'), *fl('FEST_UDIN'), cnt('festival')], hide='FEST_UDIN', r=64)],
  complete=('festival', 3, [toast('Lentera siap dilepas. Pergi ke tepi utara kolam.'), st('EPI_FEST_LEPAS')]))
S('EPI_FEST_LEPAS', 'EPI', 'Q_EPI_FEST', 'Lepaskan lentera bersama di tepi utara kolam', tint=NIGHT, talpha=0.24, inter=[
    I('fest_release', 'taman_kota', A('taman_kota', 'pond_n'), 'Lepaskan lentera', [
      cine(C('music', id='cinema_lantern_finale'), C('bars', on=True, t=0.5), C('cam', x=A('taman_kota', 'pond_n')[0], y=A('taman_kota', 'pond_n')[1] - 60, zoom=1.25, t=1.8),
           C('fx', kind='lanterns', x=A('taman_kota', 'pond_n')[0], y=A('taman_kota', 'pond_n')[1] - 70, t=7, n=24),
           C('caption', text='Festival Lentera', sub='Satu kisah, dua sudut pandang', t=2.6),
           C('cam', on='player', zoom=1.0, t=1.0), C('bars', on=False, t=0.4)),
      sc('EPI-FEST-LEPAS'), it('lentera_harapan'), sfx(), cend('EPI'), st('EPI_FREE')], r=70)])
S('EPI_FREE', 'EPI', 'Q_EPI', 'Tamat! Jelajahi kota bersama & selesaikan misi sampingan', final=True)

# ============================================================== SIDE QUEST & NPC
SIDE_QUESTS = [
    {'id': 'SQ_BUNGA', 'title': 'Antar Bunga', 'desc': 'Antar tiga buket dari Bu Melati: Nenek Sari (Plaza), Kak Raka (kafe), Dito (taman).', 'startFlag': 'SQ_BUNGA_START', 'doneFlag': 'SQ_BUNGA_DONE', 'chapter': 'C02'},
    {'id': 'SQ_MOCHI', 'title': 'Mochi Hilang', 'desc': 'Cari kucing oranye Nenek Sari. Ia suka tempat sepi: belakang rumah plaza, tepi danau, pohon tua taman.', 'startFlag': 'SQ_MOCHI_START', 'doneFlag': 'SQ_MOCHI_DONE', 'chapter': 'C02'},
    {'id': 'SQ_CAPIT', 'title': 'Tantangan Mesin Capit', 'desc': 'Dapatkan 3 boneka dari mesin capit di Arcade Bintang.', 'startFlag': 'SQ_CAPIT_START', 'doneFlag': 'SQ_CAPIT_DONE', 'chapter': 'C02'},
    {'id': 'SQ_FOTO', 'title': 'Lomba Foto Kota', 'desc': 'Potret air mancur, gazebo, dermaga, halte, dan pohon tua. Lalu tempel di papan pengumuman.', 'startFlag': 'SQ_FOTO_START', 'doneFlag': 'SQ_FOTO_DONE', 'chapter': 'C02'},
    {'id': 'SQ_BATU', 'title': 'Batu Berkilau', 'desc': 'Temukan 5 batu berkilau untuk Dito: Plaza, Jalan Kota, Tepi Danau, dan dua di Taman Kota.', 'startFlag': 'SQ_BATU_START', 'doneFlag': 'SQ_BATU_DONE', 'chapter': 'C03'},
    {'id': 'SQ_RESEP', 'title': 'Resep yang Hilang', 'desc': 'Cari kartu resep teh rempah di rak buku Kafe Senja.', 'startFlag': 'SQ_RESEP_START', 'doneFlag': 'SQ_RESEP_DONE', 'chapter': 'C03'},
    {'id': 'SQ_ROUTE_A', 'title': 'Rute Lentera Arland', 'desc': 'Bantu Kak Bayu mengecek tiga penanda arah Festival Lentera: halte, dermaga, dan kolam taman.', 'startFlag': 'SQ_ROUTE_A_START', 'doneFlag': 'SQ_ROUTE_A_DONE', 'chapter': 'C03', 'route': 'arland'},
    {'id': 'SQ_ROUTE_S', 'title': 'Catatan Tamu Sofia', 'desc': 'Bantu Bu Laras mengumpulkan tiga potongan pesan tamu festival dari kafe, toko bunga, dan taman.', 'startFlag': 'SQ_ROUTE_S_START', 'doneFlag': 'SQ_ROUTE_S_DONE', 'chapter': 'C03', 'route': 'sofia'},
    {'id': 'SQ_RAIN_A', 'title': 'Sketsa Setelah Gerimis', 'desc': 'Arland menggambar tiga tempat yang tetap terasa hangat setelah hujan: halte, dermaga, dan perpustakaan.', 'startFlag': 'SQ_RAIN_A_START', 'doneFlag': 'SQ_RAIN_A_DONE', 'chapter': 'C04', 'route': 'arland'},
    {'id': 'SQ_COLOR_S', 'title': 'Palet Langit Sofia', 'desc': 'Sofia mencari tiga nuansa senja: gazebo taman, toko bunga, dan Bukit Bintang.', 'startFlag': 'SQ_COLOR_S_START', 'doneFlag': 'SQ_COLOR_S_DONE', 'chapter': 'C05', 'route': 'sofia'},
]
SIDE_QUESTS += [
    {'id': 'SQ_V26_MAP_A', 'title': 'Peta untuk Dito',
     'desc': 'Bantu Kak Nara membuat peta tiga simbol di plaza, kafe, dan danau. Bawa kembali ke bukit.',
     'startFlag': 'SQ_V26_MAP_A_START', 'doneFlag': 'SQ_V26_MAP_A_DONE', 'chapter': 'C02', 'route': 'arland'},
    {'id': 'SQ_V26_CARDS_S', 'title': 'Tiga Kartu Cerita',
     'desc': 'Bantu Bu Laras menulis kartu dari plaza, Toko Bunga, dan halte. Kembalikan ke perpustakaan.',
     'startFlag': 'SQ_V26_CARDS_S_START', 'doneFlag': 'SQ_V26_CARDS_S_DONE', 'chapter': 'C02', 'route': 'sofia'},
    {'id': 'SQ_V26_LISTEN', 'title': 'Tiga Cerita Setelah Hujan',
     'desc': 'Dengarkan pesan titipan Nenek Sari di kafe, perpustakaan, dan halte, lalu kembali ke plaza.',
     'startFlag': 'SQ_V26_LISTEN_START', 'doneFlag': 'SQ_V26_LISTEN_DONE', 'chapter': 'C04'},
    {'id': 'SQ_V26_LAMPS', 'title': 'Peta Lampu Kota',
     'desc': 'Periksa tiga lentera festival: halte, dermaga, Bukit Bintang. Kembali ke Kak Bayu.',
     'startFlag': 'SQ_V26_LAMPS_START', 'doneFlag': 'SQ_V26_LAMPS_DONE', 'chapter': 'C05'},
]
TOWN = {'minChapter': 'C01'}
SIDE = []
# Mochi
SIDE += [I('mochi1', 'plaza', A('plaza', 'behind_houses'), 'Kucing oranye', [sc('SQ-MOCHI-2'), *fl('SQ_MOCHI_1'), emote('$ROUTE', 'exclaim')], when={'flags': ['SQ_MOCHI_START'], 'notFlags': ['SQ_MOCHI_1']},
           sprite=('props/mochi.png',) + tuple(A('plaza', 'behind_houses')), marker=False),
         I('mochi2', 'riverside', A('riverside', 'reeds'), 'Kucing oranye', [sc('SQ-MOCHI-3'), *fl('SQ_MOCHI_2')], when={'flags': ['SQ_MOCHI_1'], 'notFlags': ['SQ_MOCHI_2']},
           sprite=('props/mochi.png',) + tuple(A('riverside', 'reeds')), marker=False),
         I('mochi3', 'taman_kota', A('taman_kota', 'tree_old'), 'Kucing oranye', [sc('SQ-MOCHI-4'), *fl('SQ_MOCHI_3'), it('mochi_digendong')], when={'flags': ['SQ_MOCHI_2'], 'notFlags': ['SQ_MOCHI_3']},
           sprite=('props/mochi.png',) + tuple(A('taman_kota', 'tree_old')), marker=False)]
# Batu berkilau
STONES = [('plaza', A('plaza', 'behind_houses')[0] + 260, A('plaza', 'behind_houses')[1] - 40), ('jalan_kota', 1860, 860), ('riverside', 1700, 640), ('taman_kota', 1215, 1060), ('taman_kota', 380, 400)]
for k, (ar, x, y) in enumerate(STONES):
    SIDE.append(I('stone%d' % (k + 1), ar, (x, y), 'Batu berkilau', [*fl('SQ_BATU_%d' % (k + 1)), cnt('batu'), sfx(), toast('Batu berkilau ditemukan!')],
                  when={'flags': ['SQ_BATU_START']}, hide='SQ_BATU_%d' % (k + 1), sprite=('props/shiny_stone.png', x, y - 2, True), r=50, marker=False))
# Foto
SPOTS = [('plaza', A('plaza', 'fountain_front'), 'Potret air mancur'), ('taman_kota', A('taman_kota', 'gazebo'), 'Potret gazebo'),
         ('riverside', A('riverside', 'pier_end'), 'Potret dermaga'), ('jalan_kota', A('jalan_kota', 'halte'), 'Potret halte'), ('taman_kota', A('taman_kota', 'tree_old'), 'Potret pohon tua')]
for k, (ar, p, lab) in enumerate(SPOTS):
    SIDE.append(I('photo%d' % (k + 1), ar, p, lab, [*fl('SQ_FOTO_%d' % (k + 1)), cnt('foto'), sfx('page'), toast('Cekrek! Foto %d/5' % (k + 1))],
                  when={'flags': ['SQ_FOTO_START'], 'notFlags': ['SQ_FOTO_DONE']}, hide='SQ_FOTO_%d' % (k + 1), r=56))
SIDE += [I('notice_start', 'plaza', A('plaza', 'notice'), 'Papan pengumuman', [sc('SQ-FOTO-1'),
            say([('arland', 'senang', 'Lomba foto? Aku ikut! Kameraku sudah lama nganggur.')], route='arland'),
            say([('sofia', 'senang', 'Lomba foto? Aku ikut! Arland pasti iri.')], route='sofia'), *fl('SQ_FOTO_START')],
           when={'minChapter': 'C02', 'notFlags': ['SQ_FOTO_START']}, r=60),
         I('notice_done', 'plaza', A('plaza', 'notice'), 'Tempel foto', [sc('SQ-FOTO-2'), *fl('SQ_FOTO_DONE'), it('album_kota'), sfx()],
           when={'count': {'foto': 5}, 'notFlags': ['SQ_FOTO_DONE']}, r=60),
         I('claw', 'arcade', A('arcade', 'claw'), 'Mesin capit', [mg('claw'), iff({'count': {'last_claw': 1}}, [cnt('boneka'), toast('Dapat boneka!'), sfx()], [toast('Hampir! Coba lagi.')])],
           when={'flags': ['SQ_CAPIT_START'], 'notFlags': ['SQ_CAPIT_DONE'], 'countBelow': {'boneka': 3}}, r=60),
         I('recipe', 'cafe', A('cafe', 'shelf'), 'Cari kartu resep', [say([('narrator', 'neutral', 'Di antara buku tamu, terselip kartu kuning bertuliskan "Teh Rempah — Pak Harto".')]), *fl('SQ_RESEP_FOUND'), it('kartu_resep'), sfx('page')],
           when={'flags': ['SQ_RESEP_START'], 'notFlags': ['SQ_RESEP_FOUND']}, r=60)]
AR_ROUTE = [('jalan_kota', A('jalan_kota', 'halte'), 'Penanda arah halte', 'Papan kecilnya masih kokoh. Arland meluruskan panahnya sedikit.'),
            ('riverside', A('riverside', 'pier_end'), 'Penanda arah dermaga', 'Panah ke arah dermaga miring kena angin. Sekarang kembali lurus.'),
            ('taman_kota', A('taman_kota', 'pond_n'), 'Penanda arah kolam', 'Cat emasnya mulai pudar, tapi tulisan Festival Lentera masih terbaca.')]
for k, (ar, p0, lab, txt) in enumerate(AR_ROUTE, 1):
    SIDE.append(I('route_a_%d' % k, ar, p0, lab, [*fl('SQ_ROUTE_A_%d' % k), cnt('route_a'), sfx(), say([('arland', 'neutral', txt)], route='arland')],
                  route='arland', when={'flags': ['SQ_ROUTE_A_START'], 'notFlags': ['SQ_ROUTE_A_DONE']}, hide='SQ_ROUTE_A_%d' % k, r=60))
SO_ROUTE = [('cafe', A('cafe', 'shelf'), 'Potongan pesan kafe', 'Tulisan pertama berbunyi: "Terima kasih sudah mengingat malam ini."'),
            ('toko_bunga', A('toko_bunga', 'florist'), 'Potongan pesan bunga', 'Potongan kedua bertuliskan: "Lenteranya cantik sekali waktu dilihat berdua."'),
            ('taman_kota', A('taman_kota', 'gazebo'), 'Potongan pesan gazebo', 'Potongan terakhir: "Kalau nanti lupa, ceritakan lagi dari awal."')]
for k, (ar, p0, lab, txt) in enumerate(SO_ROUTE, 1):
    SIDE.append(I('route_s_%d' % k, ar, p0, lab, [*fl('SQ_ROUTE_S_%d' % k), cnt('route_s'), sfx('page'), say([('sofia', 'senyum', txt)], route='sofia')],
                  route='sofia', when={'flags': ['SQ_ROUTE_S_START'], 'notFlags': ['SQ_ROUTE_S_DONE']}, hide='SQ_ROUTE_S_%d' % k, r=60))

# v2.0: cerita opsional sinematik di dua route. Komplet setelah tiga lokasi.
SIDE += [
    I('rain_a_1', 'jalan_kota', A('jalan_kota', 'halte'), 'Jejak di halte',
      [sc('SQ-RAIN-A-1'), *fl('SQ_RAIN_A_START'), sfx('page'), emote('player', 'note')],
      route='arland', when={'minChapter': 'C04', 'notFlags': ['SQ_RAIN_A_START']}, r=66),
    I('rain_a_2', 'riverside', A('riverside', 'pier_end'), 'Sketsa dermaga',
      [sc('SQ-RAIN-A-2'), *fl('SQ_RAIN_A_PIER'), sfx('sparkle')],
      route='arland', when={'flags': ['SQ_RAIN_A_START'], 'notFlags': ['SQ_RAIN_A_PIER']}, r=66),
    I('rain_a_3', 'perpustakaan', A('perpustakaan', 'table'), 'Sketsa di meja baca',
      [sc('SQ-RAIN-A-3'), *fl('SQ_RAIN_A_DONE'), it('sketsa_gerimis'), sfx('page')],
      route='arland', when={'flags': ['SQ_RAIN_A_PIER'], 'notFlags': ['SQ_RAIN_A_DONE']}, r=66),
    I('color_s_1', 'taman_kota', A('taman_kota', 'gazebo'), 'Warna gazebo',
      [sc('SQ-COLOR-S-1'), *fl('SQ_COLOR_S_START'), sfx('page'), emote('player', 'heart')],
      route='sofia', when={'minChapter': 'C05', 'notFlags': ['SQ_COLOR_S_START']}, r=66),
    I('color_s_2', 'toko_bunga', A('toko_bunga', 'buckets_e'), 'Warna bunga',
      [sc('SQ-COLOR-S-2'), *fl('SQ_COLOR_S_FLOWER'), sfx('sparkle')],
      route='sofia', when={'flags': ['SQ_COLOR_S_START'], 'notFlags': ['SQ_COLOR_S_FLOWER']}, r=66),
    I('color_s_3', 'bukit_bintang', A('bukit_bintang', 'deck'), 'Palet langit',
      [sc('SQ-COLOR-S-3'), *fl('SQ_COLOR_S_DONE'), it('palet_langit'), sfx('sparkle')],
      route='sofia', when={'flags': ['SQ_COLOR_S_FLOWER'], 'notFlags': ['SQ_COLOR_S_DONE']}, r=66),
]

# v2.6 — rantai empat quest: dialog berurutan, reward, halaman album; tidak bergantung pada quest utama.
SIDE += [
    I('v26_sqa_start', 'bukit_bintang', A('bukit_bintang', 'nara'), 'Kak Nara: peta untuk Dito',
      [sc('V26-SQA-START'), *fl('SQ_V26_MAP_A_START')], route='arland',
      when={'minChapter':'C02', 'notFlags':['SQ_V26_MAP_A_START']}, r=78),
    I('v26_sqa_1', 'plaza', A('plaza', 'fountain_front'), 'Gambar simbol plaza',
      [sc('V26-SQA-1'), *fl('SQ_V26_MAP_A_1'), sfx('page')], route='arland',
      when={'flags':['SQ_V26_MAP_A_START']}, hide='SQ_V26_MAP_A_1', r=66),
    I('v26_sqa_2', 'cafe', A('cafe', 'counter'), 'Gambar simbol kafe',
      [sc('V26-SQA-2'), *fl('SQ_V26_MAP_A_2'), sfx('page')], route='arland',
      when={'flags':['SQ_V26_MAP_A_1']}, hide='SQ_V26_MAP_A_2', r=66),
    I('v26_sqa_3', 'riverside', A('riverside', 'bench'), 'Gambar simbol danau',
      [sc('V26-SQA-3'), *fl('SQ_V26_MAP_A_3'), sfx('page')], route='arland',
      when={'flags':['SQ_V26_MAP_A_2']}, hide='SQ_V26_MAP_A_3', r=66),
    I('v26_sqa_done', 'bukit_bintang', A('bukit_bintang', 'nara'), 'Serahkan denah kepada Kak Nara',
      [sc('V26-SQA-END'), *fl('SQ_V26_MAP_A_DONE'), it('denah_dito'), sfx('quest_complete')], route='arland',
      when={'flags':['SQ_V26_MAP_A_3']}, hide='SQ_V26_MAP_A_DONE', r=78),
    I('v26_sqs_start', 'perpustakaan', A('perpustakaan', 'laras'), 'Bu Laras: klub baca',
      [sc('V26-SQS-START'), *fl('SQ_V26_CARDS_S_START')], route='sofia',
      when={'minChapter':'C02', 'notFlags':['SQ_V26_CARDS_S_START']}, r=78),
    I('v26_sqs_1', 'plaza', A('plaza', 'fountain_front'), 'Tulis kartu plaza',
      [sc('V26-SQS-1'), *fl('SQ_V26_CARDS_S_1'), sfx('page')], route='sofia',
      when={'flags':['SQ_V26_CARDS_S_START']}, hide='SQ_V26_CARDS_S_1', r=66),
    I('v26_sqs_2', 'toko_bunga', A('toko_bunga', 'buckets_w'), 'Tulis kartu bunga',
      [sc('V26-SQS-2'), *fl('SQ_V26_CARDS_S_2'), sfx('page')], route='sofia',
      when={'flags':['SQ_V26_CARDS_S_1']}, hide='SQ_V26_CARDS_S_2', r=66),
    I('v26_sqs_3', 'jalan_kota', A('jalan_kota', 'halte'), 'Tulis kartu halte',
      [sc('V26-SQS-3'), *fl('SQ_V26_CARDS_S_3'), sfx('page')], route='sofia',
      when={'flags':['SQ_V26_CARDS_S_2']}, hide='SQ_V26_CARDS_S_3', r=66),
    I('v26_sqs_done', 'perpustakaan', A('perpustakaan', 'laras'), 'Serahkan kartu kepada Bu Laras',
      [sc('V26-SQS-END'), *fl('SQ_V26_CARDS_S_DONE'), it('kartu_klub_baca'), sfx('quest_complete')], route='sofia',
      when={'flags':['SQ_V26_CARDS_S_3']}, hide='SQ_V26_CARDS_S_DONE', r=78),
    I('v26_sql_start', 'plaza', A('plaza', 'bench_w'), 'Nenek Sari: cerita hujan',
      [sc('V26-SQL-START'), *fl('SQ_V26_LISTEN_START')],
      when={'minChapter':'C04', 'notFlags':['SQ_V26_LISTEN_START']}, r=75),
    I('v26_sql_1', 'cafe', A('cafe', 'barista'), 'Dengarkan cerita kafe',
      [sc('V26-SQL-1'), *fl('SQ_V26_LISTEN_1'), sfx('page')],
      when={'flags':['SQ_V26_LISTEN_START']}, hide='SQ_V26_LISTEN_1', r=66),
    I('v26_sql_2', 'perpustakaan', A('perpustakaan', 'table2'), 'Baca cerita perpustakaan',
      [sc('V26-SQL-2'), *fl('SQ_V26_LISTEN_2'), sfx('page')],
      when={'flags':['SQ_V26_LISTEN_1']}, hide='SQ_V26_LISTEN_2', r=66),
    I('v26_sql_3', 'perumahan', A('perumahan', 'halte'), 'Baca cerita halte',
      [sc('V26-SQL-3'), *fl('SQ_V26_LISTEN_3'), sfx('page')],
      when={'flags':['SQ_V26_LISTEN_2']}, hide='SQ_V26_LISTEN_3', r=66),
    I('v26_sql_done', 'plaza', A('plaza', 'bench_w'), 'Kembalikan cerita ke Nenek Sari',
      [sc('V26-SQL-END'), *fl('SQ_V26_LISTEN_DONE'), it('kumpulan_cerita_hujan'), sfx('quest_complete')],
      when={'flags':['SQ_V26_LISTEN_3']}, hide='SQ_V26_LISTEN_DONE', r=75),
    I('v26_sqf_start', 'dermaga', A('dermaga', 'arrive'), 'Kak Bayu: peta lampu festival',
      [sc('V26-SQF-START'), *fl('SQ_V26_LAMPS_START')],
      when={'minChapter':'C05','notFlags':['SQ_V26_LAMPS_START']}, r=75),
    I('v26_sqf_1', 'jalan_kota', A('jalan_kota', 'halte'), 'Periksa lentera Jalan Kota',
      [sc('V26-SQF-1'), *fl('SQ_V26_LAMPS_1'), sfx('sparkle')],
      when={'flags':['SQ_V26_LAMPS_START']}, hide='SQ_V26_LAMPS_1', r=66),
    I('v26_sqf_2', 'riverside', A('riverside', 'pier_end'), 'Periksa lentera dermaga',
      [sc('V26-SQF-2'), *fl('SQ_V26_LAMPS_2'), sfx('sparkle')],
      when={'flags':['SQ_V26_LAMPS_1']}, hide='SQ_V26_LAMPS_2', r=66),
    I('v26_sqf_3', 'bukit_bintang', A('bukit_bintang', 'deck'), 'Periksa lentera bukit',
      [sc('V26-SQF-3'), *fl('SQ_V26_LAMPS_3'), sfx('sparkle')],
      when={'flags':['SQ_V26_LAMPS_2']}, hide='SQ_V26_LAMPS_3', r=66),
    I('v26_sqf_done', 'dermaga', A('dermaga', 'arrive'), 'Serahkan laporan lampu festival',
      [sc('V26-SQF-END'), *fl('SQ_V26_LAMPS_DONE'), it('peta_lampu_kota'), sfx('quest_complete')],
      when={'flags':['SQ_V26_LAMPS_3']}, hide='SQ_V26_LAMPS_DONE', r=75),
]

def D(when, actions): return {'when': when, 'actions': actions}
def chat(npc, text, e='neutral'): return say([(npc, e, text)])
NPCS = [
    {'id': 'raka', 'name': 'Kak Raka', 'sprite': 'raka', 'area': 'cafe', 'x': A('cafe', 'barista')[0], 'y': A('cafe', 'barista')[1], 'dir': 'down', 'when': {},
     'dialogs': [
        D({'flags': ['SQ_BUNGA_START'], 'notFlags': ['SQ_BUNGA_RAKA']}, [sc('SQ-BUNGA-RAKA'), *fl('SQ_BUNGA_RAKA'), cnt('antar'), sfx()]),
        D({'flags': ['SQ_RESEP_FOUND'], 'notFlags': ['SQ_RESEP_DONE']}, [sc('SQ-RESEP-2'), *fl('SQ_RESEP_DONE'), sfx()]),
        D({'flags': ['C03_COMPLETED'], 'notFlags': ['SQ_RESEP_START']}, [sc('SQ-RESEP-1'), *fl('SQ_RESEP_START')]),
        D({'chapters': ['PRO', 'C01']}, [chat('raka', 'Selamat datang di Kafe Senja! Menu hari ini: teh melati dan roti kayu manis.', 'senyum')]),
        D({'chapters': ['C02']}, [chat('raka', 'Meja dekat jendela itu paling bagus waktu senja. Rekomendasi barista.', 'senyum')]),
        D({'chapters': ['C03']}, [chat('raka', 'Dapur boleh dipakai, asal dibersihkan lagi. Tepungnya juga, ya.', 'tertawa')]),
        D({'chapters': ['C04']}, [chat('raka', 'Hujan begini, kafe jadi tempat orang menunda pulang. Saya suka.', 'neutral')]),
        D({'chapters': ['C05']}, [chat('raka', 'Malam cerah. Bintangnya kelihatan jelas dari jendela belakang.', 'senyum')]),
        D({}, [chat('raka', 'Kalian kelihatan lebih tenang akhir-akhir ini. Teh rempah gratis untuk pasangan favorit kafe.', 'senyum')])]},
    {'id': 'melati', 'name': 'Bu Melati', 'sprite': 'melati', 'area': 'toko_bunga', 'x': A('toko_bunga', 'florist')[0], 'y': A('toko_bunga', 'florist')[1], 'dir': 'down', 'when': {},
     'dialogs': [
        D({'count': {'antar': 3}, 'notFlags': ['SQ_BUNGA_DONE']}, [sc('SQ-BUNGA-2'), *fl('SQ_BUNGA_DONE'), it('bros_bunga'), sfx()]),
        D({'minChapter': 'C02', 'notFlags': ['SQ_BUNGA_START'], 'notSteps': ['C02_A_FLORIST']}, [sc('SQ-BUNGA-1'), *fl('SQ_BUNGA_START'), toast('Misi sampingan: Antar Bunga')]),
        D({'flags': ['SQ_BUNGA_START'], 'notFlags': ['SQ_BUNGA_DONE']}, [chat('melati', 'Buketnya masih segar? Nenek Sari di Plaza, Kak Raka di kafe, Dito di taman.', 'neutral')]),
        D({'chapters': ['PRO', 'C01']}, [chat('melati', 'Bunga melati wanginya paling kuat di pagi hari. Seperti niat yang baik.', 'senyum')]),
        D({'chapters': ['C04']}, [chat('melati', 'Hujan bagus untuk bunga. Kadang juga untuk hati yang perlu disiram.', 'senyum')]),
        D({}, [chat('melati', 'Bunga yang dirawat setiap hari akan mekar pada waktunya. Hubungan juga begitu, Nak.', 'senyum')])]},
    {'id': 'juna', 'name': 'Bang Juna', 'sprite': 'juna', 'area': 'arcade', 'x': A('arcade', 'keeper')[0], 'y': A('arcade', 'keeper')[1], 'dir': 'down', 'when': {},
     'dialogs': [
        D({'count': {'boneka': 3}, 'notFlags': ['SQ_CAPIT_DONE']}, [sc('SQ-CAPIT-2'), *fl('SQ_CAPIT_DONE'), it('boneka_kucing'), sfx()]),
        D({'minChapter': 'C02', 'notFlags': ['SQ_CAPIT_START'], 'notSteps': ['C02_S_PRINT']}, [sc('SQ-CAPIT-1'), *fl('SQ_CAPIT_START'), toast('Misi sampingan: Tantangan Mesin Capit')]),
        D({'flags': ['SQ_CAPIT_START'], 'notFlags': ['SQ_CAPIT_DONE']}, [chat('juna', 'Mesin capitnya di pojok kanan. Tenang, fokus, lepas!', 'senang')]),
        D({'chapters': ['C04']}, [chat('juna', 'Hujan bikin arcade ramai. Tapi kok kamu kelihatan galau?', 'serius')]),
        D({}, [chat('juna', 'Arcade Bintang: tempat rekor dipecahkan dan kenangan dicetak!', 'senang')])]},
    {'id': 'sari', 'name': 'Nenek Sari', 'sprite': 'sari', 'area': 'plaza', 'x': 1420, 'y': 610, 'dir': 'left', 'when': {'notSteps': ['PRO_MEET', 'PRO_BOOK']},
     'dialogs': [
        D({'flags': ['SQ_BUNGA_START'], 'notFlags': ['SQ_BUNGA_SARI']}, [sc('SQ-BUNGA-SARI'), *fl('SQ_BUNGA_SARI'), cnt('antar'), sfx()]),
        D({'flags': ['SQ_MOCHI_3'], 'notFlags': ['SQ_MOCHI_DONE']}, [sc('SQ-MOCHI-5'), *fl('SQ_MOCHI_DONE'), rm('mochi_digendong'), it('foto_mochi'), sfx()]),
        D({'minChapter': 'C02', 'notFlags': ['SQ_MOCHI_START']}, [sc('SQ-MOCHI-1'), *fl('SQ_MOCHI_START'), toast('Misi sampingan: Mochi Hilang')]),
        D({'steps': ['C03_A_INGREDIENTS'], 'route': 'arland', 'notFlags': ['C03_GOT_HONEY']}, [chat('sari', 'Cari madu? Ayo, dekati Nenek.', 'senyum')]),
        D({'chapters': ['PRO', 'C01']}, [chat('sari', 'Dulu ada cerita tentang buku yang mencatat kenangan orang yang saling peduli. Nenek kira itu dongeng.', 'neutral')]),
        D({'chapters': ['C04']}, [chat('sari', 'Bertengkar itu wajar, Nak. Yang penting siapa yang mau mendengar duluan.', 'neutral')]),
        D({'chapters': ['C05', 'C06']}, [chat('sari', 'Malam secerah ini, kakek dulu suka menghitung bintang sampai tertidur.', 'senyum')]),
        D({}, [chat('sari', 'Nenek senang melihat anak muda saling menjaga. Kota ini jadi terasa muda lagi.', 'senyum')])]},
    {'id': 'dito', 'name': 'Dito', 'sprite': 'dito', 'area': 'taman_kota', 'x': 1100, 'y': 540, 'dir': 'down', 'when': {},
     'dialogs': [
        D({'flags': ['SQ_BUNGA_START'], 'notFlags': ['SQ_BUNGA_DITO']}, [sc('SQ-BUNGA-DITO'), *fl('SQ_BUNGA_DITO'), cnt('antar'), sfx()]),
        D({'count': {'batu': 5}, 'notFlags': ['SQ_BATU_DONE']}, [sc('SQ-BATU-2'), *fl('SQ_BATU_DONE'), it('batu_bintang'), sfx()]),
        D({'minChapter': 'C03', 'notFlags': ['SQ_BATU_START']}, [sc('SQ-BATU-1'), *fl('SQ_BATU_START'), toast('Misi sampingan: Batu Berkilau')]),
        D({'flags': ['SQ_BATU_START'], 'notFlags': ['SQ_BATU_DONE']}, [chat('dito', 'Batunya berkilau kalau kena cahaya. Cari di tempat yang jarang dilewati!', 'senang')]),
        D({'chapters': ['C04']}, [chat('dito', 'Hujan! Dito suka lompat di genangan. Jangan bilang Ibu, ya.', 'tertawa')]),
        D({}, [chat('dito', 'Kak, Kakak berdua pacaran, ya? Hehe. Dito nggak bilang siapa-siapa kok!', 'tertawa')])]},
    {'id': 'lumi_lf', 'name': 'Lumi', 'sprite': 'lumi', 'area': 'lantern_field', 'x': 1000, 'y': 600, 'dir': 'down', 'when': {'steps': ['C04_LIGHTS', 'C04_PUZZLE']},
     'dialogs': [D({'steps': ['C04_LIGHTS']}, [chat('lumi', 'Dua cahaya tersisa: satu di barat daya padang, satu di timur laut. Aku tunggu di sini.', 'senyum')]),
                 D({}, [chat('lumi', 'Altarnya di tengah lingkaran lentera. Nyalakan semuanya bersama-sama.', 'neutral')])]},
    {'id': 'lumi_v', 'name': 'Lumi', 'sprite': 'lumi', 'area': 'starfall_village', 'x': A('starfall_village', 'lumi')[0], 'y': A('starfall_village', 'lumi')[1], 'dir': 'down',
     'when': {'steps': ['C05_STARMAP']}, 'dialogs': [D({}, [chat('lumi', 'Arah dari kompas, warna dari lentera. Pilih bintang yang cocok, berurutan.', 'senyum')])]},
    {'id': 'lumi_e', 'name': 'Lumi', 'sprite': 'lumi', 'area': 'eternal_garden', 'x': 1080, 'y': 560, 'dir': 'down', 'when': {'chapters': ['C06']},
     'dialogs': [D({'steps': ['C06_PETALS']}, [chat('lumi', 'Kelopak Esok ada di kolam, di gazebo, dan di gerbang bunga selatan.', 'senyum')]),
                 D({}, [chat('lumi', 'Pelan-pelan saja. Taman ini tidak akan ke mana-mana.', 'senyum')])]},
]

# ============================================================== NGOBROL BERSAMA PASANGAN
def T(id, scene, area, **when): return {'id': id, 'scene': scene, 'area': area, 'when': when}
TALKS = [
    T('c01_cafe', 'T-C01-CAFE', 'cafe', steps=['C01_PUZZLE']), T('c01_lake', 'T-C01-LAKE', 'riverside', steps=['C01_PIER']),
    T('c02_park', 'T-C02-PARK', 'taman_kota', steps=['C02_DATE', 'C02_SUNSET']), T('c02_arcade', 'T-C02-ARCADE', 'arcade', steps=['C02_DATE', 'C02_SUNSET']),
    T('c02_street', 'T-C02-STREET', 'jalan_kota', steps=['C02_DATE', 'C02_SUNSET']), T('c02_lake', 'T-C02-LAKE', 'riverside', steps=['C02_SUNSET']),
    T('c03_kitchen', 'T-C03-KITCHEN', 'dapur', steps=['C03_COOK']), T('c03_park', 'T-C03-PARK', 'taman_kota', steps=['C03_PICNIC']),
    T('c03_plaza', 'T-C03-PLAZA', 'plaza', steps=['C03_PICNIC']),
    T('c04_field', 'T-C04-FIELD', 'lantern_field', steps=['C04_LIGHTS', 'C04_PUZZLE']), T('c04_field2', 'T-C04-FIELD2', 'lantern_field', steps=['C04_PUZZLE']),
    T('c05_v1', 'T-C05-VILLAGE', 'starfall_village', steps=['C05_STARMAP']), T('c05_v2', 'T-C05-VILLAGE2', 'starfall_village', steps=['C05_STARMAP']),
    T('c05_v3', 'T-C05-VILLAGE3', 'starfall_village', steps=['C05_STARMAP']),
    T('c06_g1', 'T-C06-GARDEN', 'eternal_garden', chapters=['C06']), T('c06_g2', 'T-C06-GARDEN2', 'eternal_garden', chapters=['C06']),
    T('c06_g3', 'T-C06-GARDEN3', 'eternal_garden', steps=['C06_TREE', 'C06_FINAL']),
    T('epi_plaza', 'T-EPI-PLAZA', 'plaza', steps=['EPI_FREE']), T('epi_cafe', 'T-EPI-CAFE', 'cafe', steps=['EPI_FREE']),
    T('epi_park', 'T-EPI-PARK', 'taman_kota', steps=['EPI_FREE']), T('epi_lake', 'T-EPI-LAKE', 'riverside', steps=['EPI_FREE']),
    T('epi_street', 'T-EPI-STREET', 'jalan_kota', steps=['EPI_FREE']), T('epi_home', 'T-EPI-HOME', None, steps=['EPI_FREE'], flags=['TALK_epi_plaza'])]
for t_ in TALKS: assert t_['scene'] in scenes, t_['scene']

# ============================================================== HALAMAN HILANG (lore)
LORE = [
    ('plaza', 300, 236, 'Air mancur plaza dibangun empat puluh tahun lalu. Katanya, siapa pun yang berbaikan di dekatnya akan mendengar airnya bernyanyi.'),
    ('plaza', 1700, 1010, 'Catatan tangan: "Hari ini dia tertawa melihat bungaku yang miring. Aku akan terus melipat bunga miring."'),
    ('plaza', 150, 900, 'Daftar belanja lama: madu, roti, dua tiket bioskop. Di pojok tertulis kecil: "untuk Sari".'),
    ('plaza', 1250, 1050, '"Buku ini menyala lagi. Kami bertengkar soal hal kecil, lalu duduk di bangku sampai senja."'),
    ('jalan_kota', 300, 830, 'Toko Roti Hangat berdiri sejak zaman kakek pemiliknya. Resep roti kayu manisnya tidak pernah berubah.'),
    ('jalan_kota', 1700, 330, 'Potongan karcis bus tahun lama, jurusan "Kota Tepi Danau". Di baliknya: "Aku tunggu di halte."'),
    ('jalan_kota', 1950, 770, '"Jalan ini pernah banjir. Kami berdua menggulung celana dan tertawa sepanjang jalan pulang."'),
    ('taman_kota', 1500, 300, 'Gazebo putih dibangun warga bersama-sama setelah badai besar. Tiap tiang dicat oleh keluarga berbeda.'),
    ('taman_kota', 200, 1100, '"Ikan koi pertama di kolam ini kami lepas bersama. Namanya Gembul. Sekarang cucunya ada di mana-mana."'),
    ('taman_kota', 700, 1250, 'Sketsa pensil: dua orang duduk di selimut piknik kotak-kotak. Satu roti di tangan, satu sedikit gosong.'),
    ('taman_kota', 1800, 1200, '"Ukiran dua bintang di pohon tua itu buatan kami. Jangan bilang penjaga taman."'),
    ('riverside', 300, 300, 'Danau ini dulu tempat lomba perahu kertas. Pemenangnya selalu anak-anak yang paling sabar.'),
    ('riverside', 1600, 420, '"Malam itu bintang-bintang turun ke danau. Atau kami yang naik ke langit? Aku tidak yakin."'),
    ('riverside', 900, 520, 'Coretan di kertas basah: "Kompas tidak menunjuk utara. Kompas menunjuk pulang."'),
    ('cafe', 900, 600, 'Pak Harto, pendiri Kafe Senja, menulis: "Kafe ini untuk orang yang ingin bicara pelan-pelan."'),
    ('dapur', 800, 560, 'Resep lama yang tercoret-coret: "Madu sedikit saja. Biar semua rasa dapat giliran."'),
    ('toko_bunga', 850, 580, 'Kartu bunga lama: "Krisan kuning, setiap ulang tahun pernikahan. Jangan sampai lupa."'),
    ('arcade', 110, 450, 'Lembar skor arcade kuno. Nama di urutan pertama: "S&K". Skornya dibagi dua, sama rata.'),
    ('$ROOM', 900, 452, '"Lentera kecil yang menuntun kami punya nama. Kami memanggilnya Lumi. Semoga dia menemukan teman baru."'),
    ('$ROOM', 180, 470, '"Kalau kau menemukan halaman-halaman ini, rawat bukumu baik-baik. Isi halaman kosongnya pelan-pelan."'),
]
for k, (ar, x, y, txt) in enumerate(LORE):
    SIDE.append(I('page%d' % (k + 1), ar, (x, y), 'Halaman lama', [*fl('LORE_%d' % (k + 1)), cnt('halaman'), sfx('page'),
        say([('narrator', 'neutral', 'Halaman Hilang %d/20' % (k + 1)), ('narrator', 'neutral', txt)])],
        when={'minChapter': 'C01'}, hide='LORE_%d' % (k + 1), sprite=('props/old_page.png', x, y - 2, True), r=48, marker=False))

# ============================================================== MEMANCING (Pak Udin)
FISH_NAMES = ['Ikan Mas', 'Nila', 'Mujair', 'Lele', 'Gurami', 'Koi Danau', 'Ikan Pelangi', 'Ikan Bintang']
def fish_result():
    branches = []
    for k in range(1, 9):   # luar = jenis paling langka, diperiksa lebih dulu
        branches = [iff({'count': {'last_fishing': k}}, [iff({'notFlags': ['FISH_%d' % k]}, [*fl('FISH_%d' % k), cnt('spesies'), toast('Jenis baru: %s! Catatan ikan diperbarui.' % FISH_NAMES[k - 1])]),
                                                       cnt('ikan')], branches)]
    return branches
for ar, pt in [('riverside', A('riverside', 'pier_end')), ('taman_kota', A('taman_kota', 'pond_dock')), ('dermaga', A('dermaga', 'fish_spot'))]:
    SIDE.append(I('fish_' + ar, ar, pt, 'Memancing', [mg('fishing'), *fish_result()], when={'items': ['joran']}, r=58))
SIDE_QUESTS.append({'id': 'SQ_IKAN', 'title': 'Pemancing Pemula', 'desc': 'Pancing 5 jenis ikan berbeda di ujung dermaga atau kolam taman, lalu temui Pak Udin.', 'startFlag': 'SQ_IKAN_START', 'doneFlag': 'SQ_IKAN_DONE', 'chapter': 'C02'})
SIDE_QUESTS.append({'id': 'SQ_HALAMAN', 'title': 'Halaman yang Hilang', 'desc': 'Temukan 20 halaman lama yang tersebar di kota dan di dalam rumah-rumah, lalu tunjukkan pada Nenek Sari.', 'startFlag': 'LORE_1', 'doneFlag': 'SQ_HALAMAN_DONE', 'chapter': 'C01'})
NPCS.append({'id': 'udin', 'name': 'Pak Udin', 'sprite': 'udin', 'area': 'riverside', 'x': 1120, 'y': 640, 'dir': 'right', 'when': {},
    'dialogs': [
        D({'count': {'spesies': 5}, 'notFlags': ['SQ_IKAN_DONE']}, [sc('SQ-IKAN-2'), *fl('SQ_IKAN_DONE'), it('topi_pancing'), sfx()]),
        D({'minChapter': 'C02', 'notFlags': ['SQ_IKAN_START'], 'notSteps': ['C02_SUNSET', 'C05_A_PIER']}, [sc('SQ-IKAN-1'), *fl('SQ_IKAN_START'), it('joran'), toast('Misi sampingan: Pemancing Pemula')]),
        D({'flags': ['FISH_8']}, [chat('udin', 'Ikan Bintang! Seumur hidup Bapak baru lihat sekali. Kopi gratis, sesuai janji!', 'kaget')]),
        D({'flags': ['SQ_IKAN_START'], 'notFlags': ['SQ_IKAN_DONE']}, [chat('udin', 'Tunggu pelampung bergerak, ketuk, lalu sabar. Ikan langka bergerak lebih lincah.', 'neutral')]),
        D({'chapters': ['PRO', 'C01']}, [chat('udin', 'Pagi, Nak. Danau tenang hari ini. Bagus untuk memancing dan merenung.', 'senyum')]),
        D({'chapters': ['C04']}, [chat('udin', 'Hujan begini ikan malah lapar. Tapi Bapak lebih lapar lagi, ha ha.', 'tertawa')]),
        D({}, [chat('udin', 'Danau ini menyimpan banyak cerita. Sebagian berenang, sebagian bercahaya.', 'senyum')])]})
NPCS[[n['id'] for n in NPCS].index('sari')]['dialogs'].insert(0, D({'count': {'halaman': 20}, 'notFlags': ['SQ_HALAMAN_DONE']}, [sc('SQ-HALAMAN'), *fl('SQ_HALAMAN_DONE'), it('halaman_lama'), sfx()]))

# ============================================================== KOMENTAR COMPANION (sekali per area; pembicara = pasangan)
COMMENTS = {
    'plaza': {'arland': ['Air mancurnya selalu bikin aku pengin duduk lama di sini.', 'Lihat, Nenek Sari lagi menyiram bunga lagi.'],
              'sofia': ['Plaza ini kelihatan lebih kecil kalau kita jalan berdua.', 'Kafe Senja wangi kopinya sampai sini.']},
    'jalan_kota': {'arland': ['Toko-toko di sini lucu-lucu, ya. Nanti mampir, yuk.'], 'sofia': ['Dulu aku sering lewat jalan ini sendirian. Sekarang beda rasanya.']},
    'taman_kota': {'arland': ['Bangku dekat kolam itu tempat favoritku buat baca.'], 'sofia': ['Kalau sore, kolamnya jadi oranye. Kamu harus lihat.']},
    'riverside': {'arland': ['Anginnya enak. Pak Udin pasti sudah dari subuh di sini.'], 'sofia': ['Suara air bikin pikiran jadi tenang, ya.']},
    'cafe': {'arland': ['Kursi dekat jendela masih kosong. Pas.'], 'sofia': ['Kak Raka hafal pesananku. Agak malu, sih.']},
    'dapur': {'arland': ['Wah, dapurnya rapi sekali. Aku jadi takut berantakin.'], 'sofia': ['Jangan lihat-lihat kalau aku salah potong, ya.']},
    'toko_bunga': {'arland': ['Bunga melati di sini wanginya sampai ke pintu.'], 'sofia': ['Kamu tahu bunga kesukaanku, kan? ...Kan?']},
    'arcade': {'arland': ['Mesin capit itu curang. Aku yakin.'], 'sofia': ['Skor tertinggi di mesin itu masih punyaku, lho.']},
    'memory_garden': {'arland': ['Semua di sini terasa seperti mimpi yang kita ingat bersama.'], 'sofia': ['Aku nggak takut. Selama kamu di sini.']},
    'lantern_field': {'arland': ['Lentera-lentera ini... seperti menunggu kita.'], 'sofia': ['Kalau satu lentera padam, kita nyalakan lagi bareng, ya.']},
    'star_path': {'arland': ['Jangan lihat ke bawah. Lihat ke depan saja, ke aku.'], 'sofia': ['Jalannya sempit. Pegang tanganku.']},
    'starfall_village': {'arland': ['Desa ini sepi, tapi rasanya hangat.'], 'sofia': ['Penduduknya bintang-bintang kecil? Lucu sekali.']},
    'eternal_garden': {'arland': ['Di sini, waktu seperti berhenti sebentar untuk kita.'], 'sofia': ['Aku ingin mengingat tempat ini selamanya.']},
}

# ============================================================== NPC v1.2
NPCS.append({'id': 'laras', 'name': 'Bu Laras', 'sprite': 'laras', 'area': 'perpustakaan', 'x': A('perpustakaan', 'laras')[0], 'y': A('perpustakaan', 'laras')[1], 'dir': 'down', 'when': {},
    'dialogs': [
        D({'route': 'sofia', 'minChapter': 'C03', 'notFlags': ['SQ_ROUTE_S_START']}, [sc('SQ-ROUTE-S-1'), *fl('SQ_ROUTE_S_START'), toast('Misi sampingan: Catatan Tamu Sofia')]),
        D({'route': 'sofia', 'count': {'route_s': 3}, 'notFlags': ['SQ_ROUTE_S_DONE']}, [sc('SQ-ROUTE-S-2'), *fl('SQ_ROUTE_S_DONE'), it('catatan_lentera'), sfx('page')]),
        D({'route': 'sofia', 'flags': ['SQ_ROUTE_S_START'], 'notFlags': ['SQ_ROUTE_S_DONE']}, [chat('laras', 'Cek tiga potongan catatan itu, lalu kita satukan lagi di meja baca.', 'senyum')]),
        D({'chapters': ['PRO', 'C01'], 'notFlags': ['C01_ARCHIVE_DONE']}, [chat('laras', 'Selamat datang. Perpustakaan ini sudah berdiri sebelum kota punya lampu jalan.', 'senyum')]),
        D({'chapters': ['C02']}, [sc('NPC-LARAS-C02')]),
        D({'chapters': ['C03']}, [sc('NPC-LARAS-C03')]),
        D({'chapters': ['C04']}, [chat('laras', 'Hujan bikin perpustakaan ramai. Semua orang tiba-tiba ingat mereka suka membaca.', 'tertawa')]),
        D({}, [sc('NPC-LARAS-LATE')])]})
NPCS.append({'id': 'bayu', 'name': 'Kak Bayu', 'sprite': 'bayu', 'area': 'dermaga', 'x': 1400, 'y': 510, 'dir': 'down', 'when': {},
    'dialogs': [
        D({'route': 'arland', 'minChapter': 'C03', 'notFlags': ['SQ_ROUTE_A_START']}, [sc('SQ-ROUTE-A-1'), *fl('SQ_ROUTE_A_START'), toast('Misi sampingan: Rute Lentera Arland')]),
        D({'route': 'arland', 'count': {'route_a': 3}, 'notFlags': ['SQ_ROUTE_A_DONE']}, [sc('SQ-ROUTE-A-2'), *fl('SQ_ROUTE_A_DONE'), it('peta_lentera'), sfx()]),
        D({'route': 'arland', 'flags': ['SQ_ROUTE_A_START'], 'notFlags': ['SQ_ROUTE_A_DONE']}, [chat('bayu', 'Tiga titik itu penting buat alur pengunjung malam festival. Tinggal sedikit lagi.', 'senyum')]),
        D({'notFlags': ['BAYU_MET']}, [sc('NPC-BAYU-1'), *fl('BAYU_MET')]),
        D({'chapters': ['C04']}, [sc('NPC-BAYU-RAIN')]),
        D({}, [sc('NPC-BAYU-2')])]})
sd = NPCS[[n['id'] for n in NPCS].index('sari')]['dialogs']
sd.insert(2, D({'flags': ['C01_ARCHIVE_DONE'], 'notFlags': ['SARI_ARC_TALK']}, [sc('NPC-SARI-ARC'), *fl('SARI_ARC_TALK')]))
sd.insert(3, D({'anyFlags': ['C04_LETTER_WIRA', 'C04_LETTER_SARI'], 'minChapter': 'C05', 'notFlags': ['SARI_LETTER_TALK']}, [sc('NPC-SARI-LETTERS'), *fl('SARI_LETTER_TALK')]))
COMMENTS.update({
    'perumahan': {'arland': ['Rumah-rumah di sini kecil, tapi semuanya punya kebun. Aku suka.'], 'sofia': ['Halte itu... entah kenapa aku selalu ingat hujan kalau lewat sini.']},
    'perpustakaan': {'arland': ['Ssst. Di sini kita harus bisik-bisik, ya.'], 'sofia': ['Wangi kertas tua. Aku bisa betah seharian di sini.']},
    'ruang_arsip': {'arland': ['Cahaya di stoples itu... seperti sedang bernapas.'], 'sofia': ['Rasanya kita tidak boleh bicara terlalu keras di sini.']},
    'dermaga': {'arland': ['Dari ujung dermaga, langitnya kelihatan lebih luas.'], 'sofia': ['Kapan-kapan kita sewa perahu, ya. Janji?']},
})

# ============================================================== EKSPLORASI v1.3
HB = lambda k: A('hutan_bisik', k); BB = lambda k: A('bukit_bintang', k); GK = lambda k: A('gua_kristal', k)
EXPLORE = {'minChapter': 'C02'}
# --- jembatan hutan
SIDE_QUESTS.append({'id': 'SQ_JEMBATAN', 'title': 'Jembatan Hutan', 'desc': 'Temukan 3 papan kayu di Hutan Bisik untuk memperbaiki jembatan di atas sungai.', 'startFlag': 'SQ_JEMBATAN_START', 'doneFlag': 'JEMBATAN_FIXED', 'chapter': 'C02'})
SIDE.append(I('bridge_start', 'hutan_bisik', HB('bridge_w'), 'Jembatan patah', [sc('SQ-JEMBATAN-1'), *fl('SQ_JEMBATAN_START'), toast('Misi sampingan: Jembatan Hutan')],
              when={'notFlags': ['SQ_JEMBATAN_START']}, r=60))
for k in (1, 2, 3):
    SIDE.append(I('plank%d' % k, 'hutan_bisik', HB('plank%d' % k), 'Papan kayu', [*fl('PLANK_%d' % k), cnt('papan'), sfx(), toast('Papan kayu %d/3' % k)],
                  when={'flags': ['SQ_JEMBATAN_START']}, hide='PLANK_%d' % k, sprite=('props/plank.png', HB('plank%d' % k)[0], HB('plank%d' % k)[1] - 2, True), r=50, marker=False))
BR = HB('bridge_w')
SIDE.append(I('bridge_fix', 'hutan_bisik', BR, 'Perbaiki jembatan', [
    cine(C('bars', on=True, t=0.4), C('face', who='player', dir='right'), C('cam', x=BR[0] + 70, y=BR[1] - 10, zoom=1.5, t=1.2),
         C('pose', who='player', pose='reach', t=1.6, block=True), C('sfx', id='page'), C('shake', t=0.4, amp=1.5)),
    *fl('JEMBATAN_FIXED'),
    cine(C('fx', kind='sparkles', x=BR[0] + 75, y=BR[1], t=2.2, n=36), C('sfx', id='sparkle'), C('pose', who='player', pose='cheer', t=1.2, block=True),
         C('say', scene='SQ-JEMBATAN-2'), C('cam', on='player', zoom=1.0, t=1.0), C('bars', on=False, t=0.4))],
    when={'count': {'papan': 3}, 'notFlags': ['JEMBATAN_FIXED']}, r=60))
# --- kepingan bintang (30) di seluruh kota
STAR_SPOTS = [('hutan_bisik', HB('glade')[0] - 50, HB('glade')[1] + 20), ('hutan_bisik', 1050, 1060), ('hutan_bisik', 540, 1660), ('hutan_bisik', 180, 140),
    ('hutan_bisik', 2480, 260), ('hutan_bisik', 1760, 1280), ('hutan_bisik', 400, 960), ('hutan_bisik', 1200, 470),
    ('bukit_bintang', 220, 660), ('bukit_bintang', 1760, 300), ('bukit_bintang', 760, 880), ('bukit_bintang', 1640, 790),
    ('gua_kristal', 300, 220), ('gua_kristal', 1150, 250), ('gua_kristal', 420, 620), ('gua_kristal', 860, 640), ('gua_kristal', 540, 860),
    ('plaza', 560, 170), ('plaza', 1820, 1100), ('jalan_kota', 1990, 880), ('jalan_kota', 60, 900),
    ('taman_kota', 1840, 1300), ('taman_kota', 120, 200), ('taman_kota', 980, 1340),
    ('riverside', 1860, 200), ('riverside', 120, 560), ('perumahan', 1990, 1100), ('perumahan', 60, 450), ('dermaga', 1860, 300), ('dermaga', 240, 500)]
SIDE_QUESTS.append({'id': 'SQ_BINTANG', 'title': 'Kepingan Bintang', 'desc': 'Kumpulkan 30 kepingan bintang yang tersembunyi di seluruh kota, hutan, bukit, dan gua. Bawa ke Kak Nara di Bukit Bintang.', 'startFlag': 'STAR_ANY', 'doneFlag': 'SQ_BINTANG_DONE', 'chapter': 'C02'})
for k, (ar, x, y) in enumerate(STAR_SPOTS):
    SIDE.append(I('star%d' % (k + 1), ar, (x, y), 'Kepingan bintang', [*fl('STAR_%d' % (k + 1), 'STAR_ANY'), cnt('bintang'), sfx(), toast('✦ Kepingan bintang ditemukan')],
                  when=EXPLORE, hide='STAR_%d' % (k + 1), sprite=('props/star_piece.png', x, y - 4, True), r=46, marker=False))
# --- peti
for fid, ar, pt, sid, item in [('CHEST_GLADE', 'hutan_bisik', HB('chest_glade'), 'CHEST-GLADE', 'kotak_musik'), ('CHEST_FERN', 'hutan_bisik', HB('chest_fern'), 'CHEST-FERN', 'syal'),
                               ('CHEST_HILL', 'bukit_bintang', BB('chest'), 'CHEST-HILL', 'lukisan_mini')]:
    SIDE.append(I(fid.lower(), ar, pt, 'Peti kayu', [cine(C('face', who='player', dir='up'), C('pose', who='player', pose='reach', t=0.8, block=True)), *fl(fid), sfx(), sc(sid), it(item)],
                  when=EXPLORE, hide=fid, r=50))
SIDE.append(I('chest_cave', 'gua_kristal', GK('chest'), 'Peti terkunci', [sc('CHEST-CAVE-LOCK'), mg('code_gua'), *fl('CHEST_CAVE'), sfx(), sc('CHEST-CAVE'), it('kalung_kristal')],
              when=EXPLORE, hide='CHEST_CAVE', r=50))
SIDE_QUESTS.append({'id': 'SQ_PETI', 'title': 'Peti Kristal', 'desc': 'Buka peti bersimbol di Gua Kristal. Petunjuknya terukir di batu-batu Hutan Bisik dan gua.', 'startFlag': 'CHEST_CAVE_SEEN', 'doneFlag': 'CHEST_CAVE', 'chapter': 'C02'})
# --- teropong Kak Nara
SIDE.append(I('telescope', 'bukit_bintang', BB('telescope'), 'Teropong', [sc('NARA-SCOPE'), mg('starmap_bukit'), *fl('TELESCOPE_DONE'), sc('NARA-SCOPE-DONE'), cnt('bintang'), *fl('STAR_ANY'), sfx(), toast('✦ Kepingan bintang ditemukan')],
              when={'flags': ['NARA_MET'], 'notFlags': ['TELESCOPE_DONE']}, r=56))
NPCS.append({'id': 'nara', 'name': 'Kak Nara', 'sprite': 'nara', 'area': 'bukit_bintang', 'x': BB('nara')[0], 'y': BB('nara')[1], 'dir': 'down', 'when': {},
    'dialogs': [
        D({'notFlags': ['NARA_MET']}, [sc('NARA-1'), *fl('NARA_MET'), toast('Kepingan bintang: cari 30 di seluruh kota')]),
        D({'count': {'bintang': 30}, 'notFlags': ['SQ_BINTANG_DONE']}, [sc('NARA-R3'), *fl('SQ_BINTANG_DONE', 'NARA_R3'), it('peta_langit'), sfx()]),
        D({'count': {'bintang': 20}, 'notFlags': ['NARA_R2']}, [sc('NARA-R2'), *fl('NARA_R2'), it('teropong_saku'), sfx()]),
        D({'count': {'bintang': 10}, 'notFlags': ['NARA_R1']}, [sc('NARA-R1'), *fl('NARA_R1'), it('bros_bintang'), sfx()]),
        D({'chapters': ['C04']}, [chat('nara', 'Langit mendung terus. Teleskop cuma bisa melihat awan. Tapi awan juga cantik, sih.', 'tertawa')]),
        D({'minChapter': 'C05'}, [chat('nara', 'Akhir-akhir ini bintang-bintang terasa lebih dekat. Seperti ada jalan di antara mereka.', 'serius')]),
        D({}, [chat('nara', 'Bintang suka bersembunyi di tempat yang jarang didatangi orang. Coba cek balik semak dan sudut-sudut peta.', 'senyum')])]})
COMMENTS.update({
    'hutan_bisik': {'arland': ['Dengar? Daun-daunnya seperti berbisik.', 'Hutan ini lebih luas dari yang kukira. Jangan sampai tersesat, ya.'], 'sofia': ['Wangi tanah basah dan daun. Aku suka sekali.', 'Pegang tanganku kalau jalannya gelap.']},
    'bukit_bintang': {'arland': ['Kotanya kelihatan kecil sekali dari sini.'], 'sofia': ['Kalau malam, pasti bintangnya kelihatan jelas dari sini.']},
    'gua_kristal': {'arland': ['Gelap... tapi kristalnya bercahaya. Cantik.'], 'sofia': ['Jangan jauh-jauh, ya. Aku nggak mau kehilangan kamu di sini.']},
})
lock_later = [('taman_kota', 'park_to_forest', {'when': {'maxChapter': 'C01'}, 'text': 'Jalan setapak ke hutan masih tertutup ranting tumbang. Mungkin nanti sudah dibersihkan.'})]

# ============================================================== SIDE QUEST v1.0
NPC_IDX = lambda i: [n['id'] for n in NPCS].index(i)
SIDE_QUESTS += [
    {'id': 'SQ_POS', 'title': 'Surat Pak Pos', 'desc': 'Antar lima surat untuk Bu Melati, Bang Juna, Pak Udin, Kak Raka, dan Nenek Sari.', 'startFlag': 'SQ_POS_START', 'doneFlag': 'SQ_POS_DONE', 'chapter': 'C03'},
    {'id': 'SQ_RESEP3', 'title': 'Koleksi Resep Kafe', 'desc': 'Masak tiga resep andalan Kafe Senja di dapur: kue jahe, puding kelapa, roti kayu manis.', 'startFlag': 'SQ_RESEP3_START', 'doneFlag': 'SQ_RESEP3_DONE', 'chapter': 'C04'},
    {'id': 'SQ_BUKU', 'title': 'Buku yang Tersesat', 'desc': 'Kembalikan lima buku pinjaman kafe yang tertinggal di plaza, jalan kota, tepi danau, taman, dan toko bunga.', 'startFlag': 'SQ_BUKU_START', 'doneFlag': 'SQ_BUKU_DONE', 'chapter': 'C04'},
    {'id': 'SQ_MURAL', 'title': 'Mural Baru', 'desc': 'Cari empat kaleng cat untuk Dito: belakang rumah plaza, Jalan Kota, Tepi Danau, dan dapur kafe.', 'startFlag': 'SQ_MURAL_START', 'doneFlag': 'SQ_MURAL_DONE', 'chapter': 'C04'},
]
POS_PT = (760, 520)
NPCS.append({'id': 'pos', 'name': 'Pak Pos', 'sprite': 'pos', 'area': 'plaza', 'x': POS_PT[0], 'y': POS_PT[1], 'dir': 'down', 'when': {'minChapter': 'C01'},
    'dialogs': [
        D({'count': {'surat': 5}, 'notFlags': ['SQ_POS_DONE']}, [sc('SQ-POS-2'), *fl('SQ_POS_DONE'), it('perangko'), sfx()]),
        D({'minChapter': 'C03', 'notFlags': ['SQ_POS_START']}, [sc('SQ-POS-1'), *fl('SQ_POS_START'), it('tas_surat'), toast('Misi sampingan: Surat Pak Pos')]),
        D({'flags': ['SQ_POS_START'], 'notFlags': ['SQ_POS_DONE']}, [chat('pos', 'Bu Melati di toko bunga, Bang Juna di arcade, Pak Udin di danau, Kak Raka di kafe, Nenek Sari di plaza.', 'neutral')]),
        D({'chapters': ['C04']}, [chat('pos', 'Hujan begini, surat harus dibungkus plastik dua lapis. Kenangan tidak boleh basah.', 'serius')]),
        D({'flags': ['SQ_POS_DONE']}, [chat('pos', 'Kurir terbaik kota! Kalau butuh pekerjaan sampingan, Bapak tahu orangnya.', 'senang')]),
        D({}, [chat('pos', 'Pagi! Surat zaman sekarang jarang, tapi setiap surat yang datang pasti penting.', 'senyum')])]})
for who, sid in [('melati', 'SQ-POS-MELATI'), ('juna', 'SQ-POS-JUNA'), ('udin', 'SQ-POS-UDIN'), ('raka', 'SQ-POS-RAKA'), ('sari', 'SQ-POS-SARI')]:
    f = 'SQ_POS_' + who.upper()
    NPCS[NPC_IDX(who)]['dialogs'].insert(0, D({'flags': ['SQ_POS_START'], 'notFlags': [f]}, [sc(sid), *fl(f), cnt('surat'), sfx('page'),
        iff({'count': {'surat': 5}}, [rm('tas_surat'), toast('Semua surat terantar! Kembali ke Pak Pos.')])]))
# Resep kafe
rk = NPCS[NPC_IDX('raka')]['dialogs']
rk.insert(0, D({'count': {'resep3': 3}, 'notFlags': ['SQ_RESEP3_DONE']}, [sc('SQ-RESEP3-2'), *fl('SQ_RESEP3_DONE'), it('celemek'), sfx()]))
rk.insert(4, D({'flags': ['SQ_RESEP_DONE'], 'minChapter': 'C04', 'notFlags': ['SQ_RESEP3_START']}, [sc('SQ-RESEP3-1'), *fl('SQ_RESEP3_START'), toast('Misi sampingan: Koleksi Resep Kafe')]))
for k, (mgid, nm) in enumerate([('cook_jahe', 'Kue jahe'), ('cook_puding', 'Puding kelapa'), ('cook_roti', 'Roti kayu manis')]):
    w = {'flags': ['SQ_RESEP3_START'], 'countBelow': {'resep3': k + 1}}
    if k: w['count'] = {'resep3': k}
    SIDE.append(I('cook%d' % (k + 1), 'dapur', A('dapur', 'stove'), 'Masak: ' + nm, [mg(mgid), cnt('resep3'), sfx(), toast('%s jadi! Resep %d/3' % (nm, k + 1))], when=w, r=60))
# Buku tersesat
BOOKS = [('plaza', (600, 640)), ('jalan_kota', (1150, 820)), ('riverside', (1560, 660)), ('taman_kota', (1700, 900)), ('toko_bunga', (300, 560))]
SIDE.append(I('books_start', 'cafe', A('cafe', 'shelf'), 'Rak buku pinjaman', [sc('SQ-BUKU-1'), *fl('SQ_BUKU_START'), toast('Misi sampingan: Buku yang Tersesat')],
              when={'flags': ['SQ_RESEP_DONE'], 'notFlags': ['SQ_BUKU_START']}, r=60))
for k, (ar, p_) in enumerate(BOOKS):
    SIDE.append(I('lostbook%d' % (k + 1), ar, p_, 'Buku tertinggal', [*fl('SQ_BUKU_%d' % (k + 1)), cnt('buku'), sfx('page'), toast('Buku pinjaman %d/5 ditemukan' % (k + 1))],
                  when={'flags': ['SQ_BUKU_START']}, hide='SQ_BUKU_%d' % (k + 1), sprite=('props/lost_book.png', p_[0], p_[1] - 4, True), r=50, marker=False))
SIDE.append(I('books_done', 'cafe', A('cafe', 'shelf'), 'Kembalikan buku', [sc('SQ-BUKU-2'), *fl('SQ_BUKU_DONE'), it('pembatas_lentera'), sfx()],
              when={'count': {'buku': 5}, 'notFlags': ['SQ_BUKU_DONE']}, r=60))
# Mural baru
CANS = [('plaza', (760, 220), 'paint_pink', 'merah muda'), ('jalan_kota', (760, 850), 'paint_yellow', 'kuning'), ('riverside', (1400, 700), 'paint_purple', 'ungu'), ('dapur', (140, 600), 'paint_blue', 'biru')]
for k, (ar, p_, img, nm) in enumerate(CANS):
    SIDE.append(I('paint%d' % (k + 1), ar, p_, 'Kaleng cat', [*fl('SQ_CAT_%d' % (k + 1)), cnt('cat'), sfx(), toast('Cat %s ditemukan (%d/4)' % (nm, k + 1))],
                  when={'flags': ['SQ_MURAL_START']}, hide='SQ_CAT_%d' % (k + 1), sprite=('props/%s.png' % img, p_[0], p_[1] - 4, True), r=50, marker=False))
dd = NPCS[NPC_IDX('dito')]['dialogs']
dd.insert(3, D({'count': {'cat': 4}, 'notFlags': ['SQ_MURAL_DONE']}, [sc('SQ-MURAL-2'), *fl('SQ_MURAL_DONE'), sfx()]))
dd.insert(4, D({'minChapter': 'C04', 'notFlags': ['SQ_MURAL_START']}, [sc('SQ-MURAL-1'), *fl('SQ_MURAL_START'), toast('Misi sampingan: Mural Baru')]))
dd.insert(6, D({'flags': ['SQ_MURAL_START'], 'notFlags': ['SQ_MURAL_DONE']}, [chat('dito', 'Kalengnya: belakang rumah plaza, Jalan Kota, tepi danau, sama dapur kafe!', 'senang')]))
NPCS[NPC_IDX('dito')]['when'] = {'notFlags': ['F2_DITO_HIDING']}
NPCS[NPC_IDX('juna')]['when'] = {'notSteps': ['C03_FREE']}

# ============================================================== MINIGAME, PUZZLE, KREDIT
import random as _r
def lights_board(n, presses, seed):
    rng = _r.Random(seed); b = [1] * (n * n)
    def tog(x, y):
        if 0 <= x < n and 0 <= y < n: b[y * n + x] ^= 1
    for _ in range(presses):
        x, y = rng.randrange(n), rng.randrange(n)
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)): tog(x + dx, y + dy)
    if all(b): return lights_board(n, presses, seed + 1)
    return b
MINIGAMES = {
    'v26_night_compass': {'type':'code', 'title':'Kunci Jarak Starfall',
                           'desc':'Uji tiga simbol dari denah Pak Wira di bawah langit desa.',
                           'answer':[0,1,2], 'hint':'Bunga, buku, lalu bintang. Perhatikan jedanya.'},
    'v26_night_pages': {'type':'pages', 'title':'Surat di Langit Starfall',
                         'desc':'Urutkan empat potongan kalimat yang dikumpulkan Sofia.',
                         'pages':['Ketika langit', 'mulai gelap', 'ingatlah suara yang menunggumu', 'meski tidak terlihat']},
    'quiet_cipher': {'type': 'code', 'title': 'Kunci Sunyi Pak Wira',
                     'desc': 'Ikuti urutan simbol dari denah arsip: bunga, buku, bintang.',
                     'answer': [0, 1, 2], 'hint': 'Bunga dahulu, kemudian buku, lalu bintang.'},
    'quiet_pages': {'type': 'pages', 'title': 'Empat Halaman Sari',
                    'desc': 'Susun kembali kata-kata dari sesuatu yang takut terlupakan.',
                    'pages': ['Aku mendengar', 'Aku mengingat', 'Aku berani bercerita', 'Kita tidak sendirian']},
    'photobooth': {'title': 'Photobooth', 'shots': 4, 'desc': 'Ketuk saat hati berada di zona tengah untuk pose terbaik!'},
    'cooking': {'title': 'Masak Bersama', 'desc': 'Ikuti urutan bahan, lalu ketuk saat jarum masuk zona hijau.',
                'steps': ['Cuci stroberi', 'Iris stroberi', 'Potong roti', 'Oles madu tipis', 'Tata stroberi', 'Tabur mint', 'Panggang sebentar', 'Bungkus untuk piknik']},
    'lanterns': {'title': 'Altar Lentera', 'desc': 'Menyentuh satu lentera membalik nyala lentera itu dan tetangganya. Nyalakan semua di tiap altar!',
                 'boards': [lights_board(3, 3, 11), lights_board(3, 5, 12), lights_board(4, 5, 13)]},
    'fishing': {'title': 'Memancing', 'desc': 'Tunggu pelampung bergerak, ketuk, lalu ketuk lagi saat ikan di zona hijau.'},
    'starmap': {'title': 'Peta Bintang', 'desc': 'Pilih tiga bintang sesuai arah (kompas) dan warna (lentera), berurutan.',
                'order': [['timur', 'ungu'], ['utara', 'emas'], ['barat', 'biru']]},
    'pages': {'title': 'Halaman Kenangan', 'desc': 'Susun halaman sesuai urutan perjalanan kalian.',
              'pages': ['Pertemuan di Plaza', 'Tiga Keping Cahaya', 'Surat Dua Sisi', 'Foto Photobooth', 'Senja di Dermaga', 'Piknik di Taman', 'Lentera di Hari Hujan', 'Peta Bintang', 'Kelopak Esok']},
    'claw': {'title': 'Mesin Capit', 'desc': 'Gerakkan capit, lalu ketuk untuk menurunkannya tepat di atas boneka.'},
    'starcatch': {'title': 'Hujan Bintang', 'seconds': 25, 'desc': 'Geser keranjang untuk menangkap bintang jatuh. Bintang emas bernilai 3!'},
    'ringtoss': {'title': 'Lempar Gelang', 'throws': 5, 'desc': 'Ketuk saat garis emas masuk zona hijau di bawah botol yang menyala.'},
    'starmap_bukit': {'type': 'starmap', 'title': 'Teropong Observatorium', 'desc': 'Pilih bintang selatan merah muda, timur laut biru, lalu barat laut emas.',
                      'order': [['selatan', 'merah muda'], ['timur laut', 'biru'], ['barat laut', 'emas']]},
    'code_gua': {'type': 'code', 'title': 'Peti Kristal', 'desc': 'Putar tiga simbol sesuai petunjuk ukiran batu, lalu tekan Buka.', 'answer': [3, 2, 0],
                 'hint': 'Ukiran di kuil hutan, perkemahan, dan gua ini menyimpan urutannya.'},
    'pour': {'title': 'Tuang Teh Rempah', 'cups': 3, 'desc': 'Teh mengalir ke gelas. Ketuk untuk berhenti tepat di garis merah.'},
    'cook_jahe': {'type': 'cooking', 'title': 'Kue Jahe', 'desc': 'Resep andalan Kafe Senja #1. Ikuti urutan, lalu ketuk di zona hijau.',
                  'steps': ['Ayak tepung', 'Parut jahe', 'Kocok gula aren', 'Campur adonan', 'Cetak bintang', 'Panggang', 'Oles madu', 'Dinginkan']},
    'cook_puding': {'type': 'cooking', 'title': 'Puding Kelapa', 'desc': 'Resep andalan Kafe Senja #2.',
                    'steps': ['Peras santan', 'Rebus santan', 'Masukkan gula', 'Aduk agar-agar', 'Tuang ke cetakan', 'Tabur kelapa', 'Dinginkan', 'Potong rapi']},
    'bouquet': {'type': 'bouquet', 'title':'Merangkai Buket', 'desc':'Ketuk rangkaian bunga untuk memilih bunga, lalu periksa pesanannya.'},
    'scrapbook': {'type': 'scrapbook', 'title':'Scrapbook Kenangan', 'desc':'Ketuk dua kartu untuk menukar urutan, lalu periksa alur cerita.'},
    'cook_roti': {'type': 'cooking', 'title': 'Roti Kayu Manis', 'desc': 'Resep andalan Kafe Senja #3.',
                  'steps': ['Uleni adonan', 'Diamkan', 'Gilas tipis', 'Tabur kayu manis', 'Gulung', 'Potong', 'Panggang', 'Siram gula']},
}
CREDITS = ['Arland & Sofia: Our Little Universe', '', 'Cerita: Story Bible v1.0 (draft fiksi)', 'Karakter: lembar desain Arland & Sofia',
           'Peta, properti, musik: dibuat prosedural untuk game ini', 'Engine: LibGDX', '', 'Terima kasih sudah bermain.', 'To Be Continued ♡']

PUZZLES = {'C01_SYMBOLS': {'title': 'Puzzle Tiga Simbol', 'symbols': ['BUNGA', 'BUKU', 'BINTANG'],
                           'order': {'arland': ['BUNGA', 'BUKU', 'BINTANG'], 'sofia': ['BINTANG', 'BUKU', 'BUNGA']},
                           'hintFlag': {'arland': 'C01_HINT_ARLAND', 'sofia': 'C01_HINT_SOFIA'}, 'hintAfterFails': 2}}

quests = {'_doc': 'Dibuat oleh tools/build_content.py — edit di sana lalu jalankan ulang. Token: $ROOM, $PARTNER, $RU, $ROUTE.',
          'chapters': [{'id': c, 'firstStep': f} for c, f in [('PRO', 'PRO_PHONE'), ('C01', 'C01_NOTE'), ('C02', 'C02_PHONE'), ('C03', ''), ('C04', ''), ('C05', 'C05_FREE'), ('C06', 'C06_PETALS'), ('EPI', '')]],
          'steps': steps, 'side': SIDE, 'townNpcs': NPCS, 'comments': COMMENTS, 'sideQuests': SIDE_QUESTS, 'talks': TALKS, 'puzzles': PUZZLES, 'minigames': MINIGAMES, 'credits': CREDITS}
# chapter dengan step pertama berbeda per route: snapshot dibuat saat step pertama mana pun tercapai
ROUTE_FIRST = {'C03': ['C03_A_IDEA', 'C03_S_CORNER'], 'C04': ['C04_A_WAKE', 'C04_S_WAKE']}
quests['chapterRouteFirst'] = ROUTE_FIRST

# ============================================================== PETA: kunci pintu & alt props
maps = copy.deepcopy(MAPS)
INTERIOR = {'arland_room', 'sofia_room', 'cafe', 'dapur', 'toko_bunga', 'arcade'}
for k, m in maps.items(): m['indoor'] = k in INTERIOR
def lock(map_id, door_id, *locks):
    for d in maps[map_id]['doors']:
        if d['id'] == door_id: d.setdefault('locked', []).extend(locks); return
    raise SystemExit('pintu tidak ada: %s/%s' % (map_id, door_id))
def L_steps(steps_, text): return {'steps': steps_, 'text': text}
def L_when(when, text): return {'when': when, 'text': text}
for _m, _d, _l in lock_later: lock(_m, _d, _l)
lock('perpustakaan', 'lib_to_archive', L_when({'notFlags': ['LIB_SECRET_OPEN']}, 'Rak buku tua yang sangat rapi. Tidak ada celah sedikit pun.'))
ROOM_LOCKS = [
    L_steps(['PRO_PHONE', 'PRO_GIFT'], {'arland': 'Sebelum pergi, aku mau menyiapkan sesuatu dulu.', 'sofia': 'Tunggu, kartu posnya belum kusiapkan.'}),
    L_steps(['C01_NOTE'], {'arland': 'Catatan kecilku belum ketemu. Cari dulu, ah.', 'sofia': 'Pembatas bukuku... aku mau membawanya dulu.'}),
    L_steps(['C02_PHONE', 'C03_A_IDEA', 'C03_S_CORNER', 'C04_A_WAKE', 'C04_S_WAKE', 'C05_A_START', 'C05_S_START'], 'Ponselnya berbunyi. Lihat dulu sebentar.'),
    L_steps(['C02_S_OUTFIT'], 'Belum ganti baju. Pilih outfit dulu di lemari.'),
    L_steps(['C03_S_ARRANGE'], 'Dekorasinya sudah lengkap. Tata dulu sudut kenangan.')]
for room in ('arland_room', 'sofia_room'):
    d = [x for x in maps[room]['doors'] if x['id'] == room + '_out'][0]
    d['locked'] = [dict(l, text=(l['text'] if isinstance(l['text'], dict) else l['text'])) for l in ROOM_LOCKS]
WAITING = L_steps(['PRO_MEET', 'PRO_BOOK'], 'Ada yang sedang menunggu di plaza.')
for did in ('plaza_to_park', 'plaza_to_street', 'plaza_to_lake'): lock('plaza', did, WAITING)
lock('plaza', 'door_cafe', L_steps(['PRO_PHONE', 'PRO_GIFT', 'PRO_GO_PLAZA', 'PRO_MEET', 'PRO_BOOK', 'PRO_SHARDS', 'PRO_PORTAL', 'C01_NOTE', 'C01_GO_PLAZA', 'C01_MURAL'], 'Kafe Senja belum buka. Mungkin nanti.'))
lock('cafe', 'cafe_out', L_steps(['C01_PUZZLE'], 'Teka-teki di meja simbol belum selesai.'))
lock('cafe', 'cafe_to_kitchen', L_when({'maxChapter': 'C02'}, 'Dapur khusus staf. Kak Raka sedang sibuk.'))
lock('lantern_field', 'lantern_to_village', L_when({'chapters': ['C04']}, 'Kabut terlalu tebal ke arah sana.'),
     L_steps(['C05_S_SPARKS', 'C05_S_SHRINE'], 'Jalannya masih gelap. Ikuti percik cahaya dulu.'))
lock('star_path', 'star_to_village', L_steps(['C05_A_STARS', 'C05_A_COMPASS'], 'Jalur bintang belum lengkap.'))
for k, (x, y) in enumerate(F5_LANTERNS):
    maps['taman_kota']['props'].append({'type': 'lantern_off', 'x': x + 34, 'y': y - 6, 'alt': 'lantern_post', 'altFlag': 'F5_LANTERN_%d' % (k + 1)})
for t_, x, y in [('cafe_umbrella_table', 700, 610), ('crate', 690, 690), ('crate', 900, 950), ('cafe_umbrella_table', 1330, 740)]:
    maps['plaza']['props'].append({'type': t_, 'x': x, 'y': y})
PROPS_JSON = os.path.join(DATA, 'props.json')
_pj = json.load(open(PROPS_JSON, encoding='utf-8'))
from PIL import Image, ImageDraw
_mu = Image.open(os.path.join(ROOT, 'android', 'assets', 'props', 'mural.png')).convert('RGBA')
_mn = _mu.copy(); W_, H_ = _mn.size
_strip = _mn.crop((int(W_ * 0.335), 0, int(W_ * 0.335) + 1, H_))
for xx in range(int(W_ * 0.37), int(W_ * 0.63)): _mn.paste(_strip, (xx, 0))
_d = ImageDraw.Draw(_mn); OL_ = (59, 48, 73, 255)
for k in range(7):
    cx, cy = int(W_ * (0.12 + 0.125 * k)), int(H_ * (0.14 + 0.07 * (k % 2)))
    _d.polygon([(cx, cy - 3), (cx + 1, cy - 1), (cx + 3, cy), (cx + 1, cy + 1), (cx, cy + 3), (cx - 1, cy + 1), (cx - 3, cy), (cx - 1, cy - 1)], fill=(255, 220, 120, 255))
for fx, col, hair in [(0.455, (90, 110, 170, 255), (70, 50, 60, 255)), (0.545, (210, 120, 160, 255), (110, 70, 60, 255))]:
    x0, y0 = int(W_ * fx), int(H_ * 0.42)
    _d.rectangle([x0 - 4, y0 + 4, x0 + 4, y0 + 18], fill=col, outline=OL_)
    _d.ellipse([x0 - 4, y0 - 5, x0 + 4, y0 + 4], fill=(250, 222, 200, 255), outline=OL_); _d.rectangle([x0 - 4, y0 - 5, x0 + 4, y0 - 2], fill=hair)
_d.line([int(W_ * 0.47), int(H_ * 0.47), int(W_ * 0.5), int(H_ * 0.3)], fill=OL_); _d.line([int(W_ * 0.53), int(H_ * 0.47), int(W_ * 0.5), int(H_ * 0.3)], fill=OL_)
lx, ly = int(W_ * 0.5), int(H_ * 0.24)
_d.ellipse([lx - 5, ly - 6, lx + 5, ly + 6], fill=(255, 190, 110, 255), outline=OL_); _d.ellipse([lx - 2, ly - 2, lx + 2, ly + 2], fill=(255, 245, 190, 255))
_mn.save(os.path.join(ROOT, 'android', 'assets', 'props', 'mural_new.png'))
_pj['props']['mural_new'] = dict(_pj['props']['mural'], image='props/mural_new.png')
json.dump(_pj, open(PROPS_JSON, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for p in maps['plaza']['props']:
    if p['type'] == 'mural': p['alt'] = 'mural_new'; p['altFlag'] = 'SQ_MURAL_PAINTED'
for p in maps['lantern_field']['props']:
    if p['type'] == 'lantern_off': p['alt'] = 'lantern_post'; p['altFlag'] = 'C04_LANTERNS_LIT'

# ============================================================== MEMORY BOOK
ITEMS = {
    'denah_dito': ('Denah untuk Dito', 'items/compass.png', 'Peta sederhana dari tiga tempat yang dikenali seorang anak.'),
    'kartu_klub_baca': ('Kartu Klub Baca', 'items/postcard.png', 'Tiga kartu kecil tentang hal baik di tempat biasa.'),
    'kumpulan_cerita_hujan': ('Cerita Setelah Hujan', 'items/memory_page.png', 'Salinan tiga cerita Nenek Sari yang mengajarkan cara mendengar.'),
    'peta_lampu_kota': ('Peta Lampu Festival', 'items/lantern_paper.png', 'Rute tiga lentera yang diperiksa sebelum festival.'),
    'halaman_suara': ('Halaman Suara', 'items/memory_page.png', 'Halaman terakhir Pak Wira yang memudar ketika tidak pernah diceritakan.'),
    'pembatas_wira': ('Pembatas Kenangan Wira', 'items/lantern_bookmark.png', 'Titipan Nenek Sari: cerita baik patut disampaikan lagi.'),
    'paper_flower': ('Bunga Kertas', 'items/paper_flower.png', 'Bunga kecil dari kertas, dilipat sendiri.'),
    'postcard': ('Kartu Pos', 'items/postcard.png', 'Kartu pos dengan pesan singkat yang ditulis hati-hati.'),
    'memory_book': ('Memory Book', 'items/memory_book.png', 'Buku kecil bercahaya yang menyimpan kenangan.'),
    'small_note': ('Catatan Kecil', 'items/small_note.png', 'Catatan kecil milik Arland.'),
    'bookmark': ('Pembatas Buku', 'items/bookmark.png', 'Pembatas buku Sofia dengan gambar bintang kecil.'),
    'letter_two_sides': ('Surat Dua Sisi', 'items/letter_two_sides.png', '"Setiap kenangan punya dua sisi, tetapi satu tempat pulang."'),
    'bunga_pita': ('Buket Berpita', 'items/bouquet.png', 'Buket kecil dari Toko Bunga Melati dengan pita pilihan sendiri.'),
    'foto_kecil': ('Foto Langit Plaza', 'items/photo_small.png', 'Foto kecil langit sore di atas plaza.'),
    'foto_berdua': ('Foto Photobooth', 'items/photo_strip.png', 'Tiga jepretan: kaget, tertawa, lalu tersenyum.'),
    'stroberi': ('Stroberi', 'items/strawberry.png', 'Stroberi segar dari kulkas dapur kafe.'),
    'madu': ('Madu', 'items/honey.png', 'Madu dari kebun lebah cucu Nenek Sari.'),
    'daun_mint': ('Daun Mint', 'items/mint.png', 'Tiga lembar daun mint dari taman.'),
    'roti_lapis': ('Roti Lapis Madu', 'items/sandwich.png', 'Roti lapis stroberi madu. Satu sedikit gosong.'),
    'bunga_kering': ('Bunga Kering', 'items/dried_flowers.png', "Baby's breath dan mawar kecil yang dikeringkan."),
    'lampu_tumbler': ('Lampu Tumbler', 'items/fairy_lights.png', 'Lampu kecil yang membuat sudut kenangan hangat.'),
    'bingkai_bintang': ('Bingkai Bintang', 'items/star_frame.png', 'Bingkai foto berbentuk bintang dari arcade.'),
    'kompas': ('Kompas Bintang', 'items/compass.png', 'Jarumnya menunjuk timur, utara, lalu barat.'),
    'lentera_kecil': ('Lentera Kecil', 'items/lantern_small.png', 'Lentera yang berganti warna: ungu, emas, biru.'),
    'surat_esok': ('Surat untuk Besok', 'items/letter_two_sides.png', 'Surat harapan yang akan digantung di Pohon Harapan.'),
    'bros_bunga': ('Bros Bunga', 'items/brooch.png', 'Bunga yang tidak layu, untuk kenangan yang tidak layu.'),
    'mochi_digendong': ('Mochi', 'items/cat_photo.png', 'Kucing oranye yang berat. Antar pulang ke Nenek Sari.'),
    'foto_mochi': ('Foto Mochi Kecil', 'items/cat_photo.png', 'Dulu Mochi muat di dalam cangkir teh.'),
    'batu_bintang': ('Batu Bintang', 'items/star_stone.png', 'Agak bercahaya kalau dilihat malam hari.'),
    'boneka_kucing': ('Boneka Kucing', 'items/cat_plush.png', 'Hadiah juara mesin capit edisi terbatas.'),
    'kartu_resep': ('Kartu Resep', 'items/recipe.png', 'Teh Rempah — Pak Harto. Untuk orang yang baru berbaikan.'),
    'album_kota': ('Album Kota', 'items/album.png', 'Lima foto tempat favorit di kota.'),
    'joran': ('Joran Pancing', 'items/fishing_rod.png', 'Joran cadangan Pak Udin. Pancing di dermaga atau kolam taman.'),
    'topi_pancing': ('Topi Pancing', 'items/fish_hat.png', 'Topi Pak Udin waktu muda. Tanda pemancing sejati.'),
    'halaman_lama': ('Halaman Lama', 'items/memory_page.png', 'Dua puluh halaman dari buku kenangan Nenek Sari dan kakek.'),
    'gembor': ('Gembor', 'items/watering.png', 'Gembor pinjaman Nenek Sari untuk menyiram bunga plaza.'),
    'permen_jahe': ('Permen Jahe', 'items/ginger_candy.png', 'Buatan Nenek Sari. "Bagus sebelum bicara penting."'),
    'stiker_bintang': ('Stiker Bintang', 'items/star_sticker.png', 'Hadiah papan skor Hujan Bintang.'),
    'buah_pasar': ('Buah Pasar Minggu', 'items/fruit.png', 'Hadiah tebak berat semangka.'),
    'buku_pasar': ('Buku Bekas', 'items/market_book.png', '"Semoga harimu menyenangkan," tulis pemilik sebelumnya.'),
    'gantungan_bintang': ('Gantungan Bintang', 'items/keychain_star.png', 'Hadiah lempar gelang. Diskon perasaan tidak termasuk.'),
    'teh_rempah': ('Teh Rempah Festival', 'items/tea_glass.png', 'Jahe, kayu manis, gula aren. Untuk tangan yang hangat.'),
    'lentera_kertas': ('Lentera Kertas', 'items/lantern_paper.png', 'Empat lentera untuk digantung di Taman Kota.'),
    'mahkota_bunga': ('Mahkota Bunga', 'items/flower_crown.png', 'Buatan Bu Melati di malam festival.'),
    'lentera_harapan': ('Kenangan Lentera', 'items/lantern_paper.png', '"Semoga kita terus punya alasan untuk jalan-jalan sore."'),
    'tas_surat': ('Tas Surat', 'items/postcard.png', 'Lima surat titipan Pak Pos.'),
    'perangko': ('Perangko Festival', 'items/stamp.png', 'Perangko langka edisi festival, hadiah Pak Pos.'),
    'celemek': ('Celemek Kafe Senja', 'items/apron.png', 'Tanda koki resmi Kafe Senja.'),
    'pembatas_lentera': ('Pembatas Lentera', 'items/lantern_bookmark.png', 'Terselip di balik buku pinjaman terakhir.'),
    'catatan_wira': ('Catatan Pak Wira', 'items/memory_page.png', '"Kenangan hanya menjadi sunyi ketika tidak ada lagi yang menceritakannya."'),
    'surat_wira': ('Surat Pak Wira', 'items/letter_two_sides.png', '"Aku bawa payung. Dan telinga."'),
    'surat_sari': ('Surat Nenek Sari', 'items/postcard.png', '"Aku diam bukan karena marah."'),
    'kotak_musik': ('Kotak Musik Dua Bintang', 'items/music_box.png', 'Ditemukan di lembah rahasia Hutan Bisik. Melodinya terasa akrab.'),
    'syal': ('Syal Rajut', 'items/scarf.png', '"Untuk siapa pun yang kedinginan di hutan ini."'),
    'lukisan_mini': ('Lukisan Kota dari Bukit', 'items/mini_painting.png', 'Dilukis W., untuk S.'),
    'kalung_kristal': ('Kalung Kristal', 'items/crystal_necklace.png', 'Bulan, bintang, lalu bunga.'),
    'bros_bintang': ('Bros Bintang', 'items/brooch.png', 'Hadiah Kak Nara untuk 10 kepingan bintang.'),
    'teropong_saku': ('Teropong Saku', 'items/mini_telescope.png', 'Arahkan ke timur laut di malam cerah.'),
    'peta_langit': ('Peta Langit Kota', 'items/star_frame.png', 'Tiga puluh kepingan menjadi satu peta "jalan bintang".'),
    'peta_lentera': ('Peta Rute Lentera', 'items/compass.png', 'Catatan rute festival yang diberi tanda ulang bersama Kak Bayu.'),
    'catatan_lentera': ('Catatan Tamu Lentera', 'items/wish_card.png', 'Tiga potongan pesan pengunjung yang dirapikan ulang bersama Bu Laras.'),
    'sketsa_gerimis': ('Sketsa Setelah Gerimis', 'items/compass.png', 'Peta tiga tempat untuk berjalan pelan, dilipat dengan perhatian.'),
    'palet_langit': ('Palet Langit Kita', 'items/photo_small.png', 'Tiga warna yang tidak bisa menangkap seluruh keindahan satu sore.'),
}
def E(id, ch, route, typ, unlock, icon, title, text): return {'id': id, 'chapter': ch, 'route': route, 'type': typ, 'unlock': unlock, 'icon': icon, 'title': title, 'text': text}
ENTRIES = [
    E('m_v26_cooking', 'C03', 'shared', 'fictional_memory', 'V26_C03_FINISHED', 'items/recipe.png', 'Di Pinggir Resep', 'Makanan biasa bisa mengingatkan kita bahwa belajar bersama lebih menyenangkan.'),
    E('m_v26_afterrain', 'C04', 'shared', 'fictional_memory', 'V26_AFTER_RAIN', 'items/memory_page.png', 'Setelah Hujan', 'Bukan janji tidak pernah salah, melainkan keberanian untuk membicarakannya.'),
    E('m_v26_night_a', 'C05', 'arland', 'clue', 'V26_C05_A_SOLVED', 'items/compass.png', 'Peta yang Bisa Mendengar', 'Tiga titik di Starfall Village mengubah cara Arland melihat arah.'),
    E('m_v26_night_s', 'C05', 'sofia', 'letter', 'V26_C05_S_SOLVED', 'items/postcard.png', 'Kalimat di Balik Bintang', 'Empat potongan kalimat tentang suara yang tetap menunggu.'),
    E('m_v26_night', 'C05', 'shared', 'fictional_memory', 'V26_C05_TOGETHER', 'items/star_frame.png', 'Dua Jalan di Satu Langit', 'Arland mencari arah; Sofia mencari cerita. Mereka duduk di bangku yang sama.'),
    E('m_v26_map_a', 'SIDE', 'arland', 'souvenir', 'SQ_V26_MAP_A_DONE', 'items/compass.png', 'Peta untuk Dito', 'Tiga simbol yang membuat jalan pulang tidak lagi terasa asing.'),
    E('m_v26_cards_s', 'SIDE', 'sofia', 'letter', 'SQ_V26_CARDS_S_DONE', 'items/postcard.png', 'Tiga Kartu Cerita', 'Sofia menemukan tiga alasan kecil untuk kembali ke kota.'),
    E('m_v26_listen', 'SIDE', 'shared', 'fictional_memory', 'SQ_V26_LISTEN_DONE', 'items/memory_page.png', 'Suara Setelah Hujan', 'Tiga pesan yang tidak memberi jawaban instan, tetapi membuat orang merasa didengar.'),
    E('m_v26_lamps', 'SIDE', 'shared', 'fictional_memory', 'SQ_V26_LAMPS_DONE', 'items/lantern_paper.png', 'Peta Lampu Kota', 'Tiga lentera kecil memandu pengunjung melalui cerita orang lain.'),
    E('q_map_a', 'C01', 'arland', 'clue', 'Q_C01_A_MAP', 'items/compass.png', 'Denah di Stoples', 'Arland membaca kota lewat jalur, bukan lewat kalimat.'),
    E('q_margin_s', 'C01', 'sofia', 'clue', 'Q_C01_S_MARGIN', 'items/bookmark.png', 'Kata di Pinggir Halaman', 'Sofia memperhatikan kalimat yang tidak pernah selesai.'),
    E('q_rain_a', 'C04', 'arland', 'letter', 'Q_C04_A_REPLY', 'items/letter_two_sides.png', 'Jawaban di Halte', 'Belajar mendengar sebelum buru-buru memperbaiki.'),
    E('q_rain_s', 'C04', 'sofia', 'letter', 'Q_C04_S_REPLY', 'items/postcard.png', 'Kata yang Tertahan', 'Memberi ruang pada kalimat yang tertinggal.'),
    E('q_echo', 'C05', 'shared', 'clue', 'Q_C05_ECHO', 'items/star_frame.png', 'Petunjuk di Bangku Bintang', 'Dua cara mencari, satu tempat untuk bercerita.'),
    E('q_answer_a', 'C06', 'arland', 'fictional_memory', 'Q_C06_A_SOLVED', 'items/compass.png', 'Kunci Simbol', 'Bunga, buku, bintang. Susunan seorang pemeta.'),
    E('q_answer_s', 'C06', 'sofia', 'fictional_memory', 'Q_C06_S_SOLVED', 'items/memory_page.png', 'Empat Halaman', 'Kata-kata yang akhirnya berani dibaca.'),
    E('q_reveal', 'C06', 'shared', 'fictional_memory', 'THE_QUIET_REVEALED', 'items/memory_book.png', 'Arti The Quiet', 'Bukan makhluk: kesunyian yang muncul saat kenangan tak lagi dibagikan.'),
    E('q_sari_closure', 'EPI', 'shared', 'letter', 'Q_SARI_CLOSURE', 'items/lantern_bookmark.png', 'Halaman untuk Sari', 'Cerita Pak Wira kembali ke tangan yang mengenalnya.'),
    E('m_phone_a', 'PRO', 'arland', 'fictional_memory', 'PRO_PHONE_READ', 'items/memory_page.png', 'Pesan Pagi', 'Pesan singkat dari Sofia: ketemu di plaza.'),
    E('m_phone_s', 'PRO', 'sofia', 'fictional_memory', 'PRO_PHONE_READ', 'items/memory_page.png', 'Sisa Mimpi', 'Mimpi tentang buku yang menyala, lalu pesan dari Arland.'),
    E('m_gift_a', 'PRO', 'arland', 'gift', 'PRO_GIFT_ARLAND', 'items/paper_flower.png', 'Bunga Kertas', 'Sederhana, tapi dibuat sendiri.'),
    E('m_gift_s', 'PRO', 'sofia', 'gift', 'PRO_GIFT_SOFIA', 'items/postcard.png', 'Kartu Pos', 'Ditulis singkat. Yang penting saja.'),
    E('m_meet', 'PRO', 'shared', 'fictional_memory', 'CANON_PLAZA_MEET', 'items/memory_page.png', 'Di Plaza', 'Dua hadiah kecil berpindah tangan.'),
    E('m_book', 'PRO', 'shared', 'fictional_memory', 'CANON_BOOK_OPEN', 'items/memory_book.png', 'Buku yang Bercahaya', 'Halaman pertama membuka pintu cahaya.'),
    E('m_garden', 'PRO', 'shared', 'fictional_memory', 'CANON_MEMORY_GARDEN', 'items/light_shard.png', 'Tiga Keping Cahaya', 'Tiga keping menyatu menjadi satu halaman.'),
    E('m_note_a', 'C01', 'arland', 'clue', 'C01_ARLAND_NOTE', 'items/small_note.png', 'Catatan Kecil', 'Terselip di antara buku-buku.'),
    E('m_note_s', 'C01', 'sofia', 'clue', 'C01_SOFIA_BOOKMARK', 'items/bookmark.png', 'Pembatas Buku', 'Bintang kecil yang mirip dengan mimpi itu.'),
    E('m_mural_a', 'C01', 'arland', 'clue', 'C01_HINT_ARLAND', 'items/symbol_flower.png', 'Mural Bunga', 'Bunga, buku, bintang.'),
    E('m_mural_s', 'C01', 'sofia', 'clue', 'C01_HINT_SOFIA', 'items/symbol_star.png', 'Mural Bintang', 'Bintang, buku, bunga.'),
    E('m_letter', 'C01', 'shared', 'letter', 'CANON_CAFE_LETTER', 'items/letter_two_sides.png', 'Two Sides, One Home', 'Setiap kenangan punya dua sisi, tetapi satu tempat pulang.'),
    E('m_river', 'C01', 'shared', 'fictional_memory', 'CANON_RIVERSIDE', 'items/memory_page.png', 'Di Tepi Danau', 'Kalau salah ingat, berarti ada dua versi untuk diceritakan.'),
    E('m_bouquet', 'C02', 'arland', 'gift', 'C02_ARLAND_GIFT_READY', 'items/bouquet.png', 'Buket Berpita', 'Telinga merah adalah tanda paling jujur, kata Bu Melati.'),
    E('m_outfit', 'C02', 'sofia', 'fictional_memory', 'C02_SOFIA_READY', 'items/photo_small.png', 'Persiapan Kecil', 'Yang nyaman saja. Yang penting bisa jalan lama.'),
    E('m_park', 'C02', 'shared', 'fictional_memory', 'C02_PARK_DONE', 'items/memory_page.png', 'Gazebo dan Ikan Koi', '"Mungkin mereka cuma suka ditemani."'),
    E('m_photo', 'C02', 'shared', 'photo', 'CANON_DATE_PHOTO', 'items/photo_strip.png', 'Foto Photobooth', 'Kaget, tertawa, lalu tersenyum.'),
    E('m_sunset', 'C02', 'shared', 'gift', 'C02_COMPLETED', 'items/photo_small.png', 'Senja di Dermaga', 'Bunga ditukar dengan foto langit yang sama.'),
    E('m_cook_a', 'C03', 'arland', 'fictional_memory', 'C03_ARLAND_PREP', 'items/sandwich.png', 'Koki Pemula', 'Tepung ikut ke mana-mana.'),
    E('m_corner', 'C03', 'sofia', 'souvenir', 'C03_SOFIA_PREP', 'items/fairy_lights.png', 'Sudut Kenangan', 'Lampu tumbler, bunga kering, dan satu bingkai bintang.'),
    E('m_route_a', 'C03', 'arland', 'fictional_memory', 'SQ_ROUTE_A_DONE', 'items/compass.png', 'Rute Lentera', 'Arland membantu Bayu menata tiga penanda arah supaya malam festival tetap terasa ramah.'),
    E('m_route_s', 'C03', 'sofia', 'fictional_memory', 'SQ_ROUTE_S_DONE', 'items/wish_card.png', 'Catatan Tamu', 'Sofia merapikan tiga pesan kecil yang membuat festival terasa lebih pribadi.'),
    E('m_rain_sketch_a', 'C04', 'arland', 'fictional_memory', 'SQ_RAIN_A_DONE', 'items/compass.png', 'Sketsa Gerimis', 'Tiga tempat, bukan tiga rute tercepat, yang membuat Arland belajar berhenti dan mendengarkan.'),
    E('m_color_s', 'C05', 'sofia', 'fictional_memory', 'SQ_COLOR_S_DONE', 'items/photo_small.png', 'Palet Langit', 'Tiga warna yang Sofia pilih untuk satu sore yang tidak ingin dibekukan.'),
    E('m_cook', 'C03', 'shared', 'fictional_memory', 'C03_COOKED', 'items/sandwich.png', 'Masak Bersama', 'Lumayan banget karena dibuat bareng.'),
    E('m_picnic', 'C03', 'shared', 'fictional_memory', 'C03_COMPLETED', 'items/memory_page.png', 'Piknik', 'Yang gosong itu yang paling ada usahanya.'),
    E('m_rain_a', 'C04', 'arland', 'fictional_memory', 'C04_ARLAND_REFLECT', 'items/memory_page.png', 'Pesan yang Belum Selesai', 'Maaf saja tidak cukup tanpa mendengar.'),
    E('m_rain_s', 'C04', 'sofia', 'fictional_memory', 'C04_SOFIA_REFLECT', 'items/memory_page.png', 'Di Balik Hujan', 'Jujur tanpa membuat semuanya rumit.'),
    E('m_lantern', 'C04', 'shared', 'fictional_memory', 'CANON_RAIN_TALK', 'items/lantern_small.png', 'Lentera yang Menyala', 'Makasih udah mau ngomong. Makasih udah dengerin.'),
    E('m_compass', 'C05', 'arland', 'clue', 'C05_COMPASS_CLUE', 'items/compass.png', 'Jalur Kompas', 'Timur, utara, lalu barat.'),
    E('m_colors', 'C05', 'sofia', 'clue', 'C05_LANTERN_CLUE', 'items/lantern_small.png', 'Jalur Lentera', 'Ungu, emas, biru.'),
    E('m_starmap', 'C05', 'shared', 'fictional_memory', 'C05_COMPLETED', 'items/star_stone.png', 'Peta Bintang', 'Dua petunjuk, satu rasi.'),
    E('m_wish_a', 'C06', 'arland', 'letter', 'C06_ARLAND_LETTER', 'items/letter_two_sides.png', 'Surat untuk Besok', 'Tetap punya waktu untuk cerita dan tertawa bareng.'),
    E('m_wish_s', 'C06', 'sofia', 'letter', 'C06_SOFIA_LETTER', 'items/letter_two_sides.png', 'Halaman yang Sama', 'Saling mendukung, bahkan saat sulit.'),
    E('m_end', 'C06', 'shared', 'fictional_memory', 'CANON_ETERNAL_GARDEN', 'items/memory_book.png', 'Halaman Kosong', 'To Be Continued.'),
    E('m_epi', 'EPI', 'shared', 'fictional_memory', 'EPI_UNLOCKED', 'items/memory_page.png', 'Sampai Nanti', 'Masih banyak halaman kosong.'),
    E('m_sq_bunga', 'SIDE', 'shared', 'souvenir', 'SQ_BUNGA_DONE', 'items/brooch.png', 'Kurir Bunga', 'Krisan untuk Nenek Sari, matahari untuk kafe, dan buket keren untuk Dito.'),
    E('m_sq_mochi', 'SIDE', 'shared', 'photo', 'SQ_MOCHI_DONE', 'items/cat_photo.png', 'Mochi Pulang', 'Kucing yang dulu muat di cangkir teh.'),
    E('m_sq_capit', 'SIDE', 'shared', 'souvenir', 'SQ_CAPIT_DONE', 'items/cat_plush.png', 'Juara Capit', 'Rekor baru Arcade Bintang.'),
    E('m_sq_foto', 'SIDE', 'shared', 'photo', 'SQ_FOTO_DONE', 'items/album.png', 'Album Kota', 'Lima tempat favorit, satu stiker bintang emas.'),
    E('m_sq_batu', 'SIDE', 'shared', 'souvenir', 'SQ_BATU_DONE', 'items/star_stone.png', 'Batu Bintang', 'Hadiah super rahasia dari Dito.'),
    E('m_sq_resep', 'SIDE', 'shared', 'souvenir', 'SQ_RESEP_DONE', 'items/recipe.png', 'Teh Rempah', 'Diminum orang yang baru berbaikan.'),
    E('m_sq_ikan', 'SIDE', 'shared', 'souvenir', 'SQ_IKAN_DONE', 'items/fish_hat.png', 'Pemancing Sejati', 'Memancing itu soal sabar.'),
    E('m_library', 'C01', 'shared', 'fictional_memory', 'LIB_SECRET_OPEN', 'items/symbol_book.png', 'Rak yang Sunyi', 'Tiga buku, satu klik, dan sebuah ruangan rahasia.'),
    E('m_archive', 'C01', 'shared', 'fictional_memory', 'C01_ARCHIVE_DONE', 'items/memory_page.png', 'Arsip No. 7', 'Stoples-stoples cahaya dan satu kata yang terasa dingin: sunyi.'),
    E('m_pier', 'C01', 'shared', 'fictional_memory', 'C01_PIER_SUNSET', 'items/photo_small.png', 'Senja di Dermaga', 'Langit dan danau seperti satu halaman.'),
    E('m_letter_wira', 'C04', 'arland', 'gift', 'C04_LETTER_WIRA', 'items/letter_two_sides.png', 'Surat untuk Sari', 'Sebuah permintaan maaf yang menunggu puluhan tahun di kotak surat.'),
    E('m_letter_sari', 'C04', 'sofia', 'gift', 'C04_LETTER_SARI', 'items/postcard.png', 'Surat untuk Wira', 'Diam karena takut, bukan karena marah.'),
    E('m_bridge', 'SIDE', 'shared', 'fictional_memory', 'JEMBATAN_FIXED', 'items/plank.png', 'Jembatan Hutan', 'Tiga papan, dan jalan ke bukit terbuka.'),
    E('m_glade', 'SIDE', 'shared', 'souvenir', 'CHEST_GLADE', 'items/music_box.png', 'Lembah Rahasia', 'Celah di antara pohon, dan sebuah kotak musik.'),
    E('m_cave', 'SIDE', 'shared', 'souvenir', 'CHEST_CAVE', 'items/crystal_necklace.png', 'Peti Kristal', 'Bulan, bintang, bunga.'),
    E('m_hill', 'SIDE', 'shared', 'souvenir', 'CHEST_HILL', 'items/mini_painting.png', 'Lukisan dari Bukit', 'Kota kita, dari tempat yang paling tinggi.'),
    E('m_stars10', 'SIDE', 'shared', 'souvenir', 'NARA_R1', 'items/brooch.png', 'Sepuluh Bintang', 'Bros dari pecahan bintang.'),
    E('m_stars30', 'SIDE', 'shared', 'fictional_memory', 'SQ_BINTANG_DONE', 'items/star_frame.png', 'Peta Langit', 'Tiga puluh kepingan, satu jalan bintang.'),
    E('m_free_c02', 'C02', 'shared', 'fictional_memory', 'C02_FREE_DONE', 'items/ginger_candy.png', 'Pagi yang Panjang', 'Bunga plaza, bintang arcade, dan petak umpet.'),
    E('m_free_c03', 'C03', 'shared', 'souvenir', 'C03_FREE_DONE', 'items/market_book.png', 'Pasar Minggu', 'Tenda warna-warni dan tawar-menawar pagi.'),
    E('m_free_c05', 'C05', 'shared', 'fictional_memory', 'C05_FREE_DONE', 'items/lantern_paper.png', 'Sebelum Festival', 'Teh, lentera, dan kartu harapan.'),
    E('m_festival', 'EPI', 'shared', 'fictional_memory', 'EPI_FESTIVAL_DONE', 'items/lantern_paper.png', 'Festival Lentera', 'Satu lentera, ratusan cahaya, dan seekor ikan kecil yang berpendar.'),
    E('m_sq_pos', 'SIDE', 'shared', 'souvenir', 'SQ_POS_DONE', 'items/stamp.png', 'Kurir Kota', 'Lima surat, lima kabar baik.'),
    E('m_sq_resep3', 'SIDE', 'shared', 'souvenir', 'SQ_RESEP3_DONE', 'items/apron.png', 'Koki Kafe Senja', 'Kue jahe, puding kelapa, roti kayu manis.'),
    E('m_sq_buku', 'SIDE', 'shared', 'souvenir', 'SQ_BUKU_DONE', 'items/lantern_bookmark.png', 'Rak Lengkap', 'Buku yang tersesat akhirnya pulang.'),
    E('m_sq_mural', 'SIDE', 'shared', 'photo', 'SQ_MURAL_DONE', 'items/album.png', 'Mural Baru', 'Lentera, bintang, dan dua orang di tengah.'),
    E('m_sq_halaman', 'SIDE', 'shared', 'real_memory', 'SQ_HALAMAN_DONE', 'items/memory_page.png', 'Buku Nenek Sari', 'Kenangan lama dan baru tinggal bersama.'),
]
# ============================================================== DUNIA HIDUP v1.4 (jadwal, warga, hewan)
exec(open(os.path.join(os.path.dirname(__file__), 'content', 'life_sim.py'), encoding='utf-8').read())
exec(open(os.path.join(os.path.dirname(__file__), 'content', 'economy.py'), encoding='utf-8').read())
exec(open(os.path.join(os.path.dirname(__file__), 'content', 'romance.py'), encoding='utf-8').read())
exec(open(os.path.join(os.path.dirname(__file__), 'content', 'romance_games_v25.py'), encoding='utf-8').read())
ROMANCE['games'] = ROMANCE_GAMES
quests['shops'] = SHOPS
quests['jobs'] = JOBS
quests['romance'] = ROMANCE

for _rg in ROMANCE_GAMES:
    ENTRIES.append(E('m_romgame_' + _rg['id'], 'SIDE', 'shared', 'fictional_memory', 'ROM_GAME_' + _rg['id'].upper() + '_ONCE', 'items/album.png', _rg['title'], 'Aktivitas kecil yang membuat satu hari menjadi kenangan berdua.'))

book = {'_doc': 'Dibuat oleh tools/build_content.py. Semua teks = draft fiksi.',
        'items': {k: {'name': v[0], 'icon': v[1], 'desc': v[2]} for k, v in ITEMS.items()},
        'entries': ENTRIES,
        'bonus': {'id': 'm_two_sided', 'title': 'Kenangan Dua Sisi (Bonus)', 'icon': 'items/letter_two_sides.png', 'requires': 'both_routes_C06',
                  'text': 'Arland melihat bunga dan arah bintang; Sofia melihat bintang dan warna lentera. Urutannya berbeda, tetapi setiap halaman berakhir di tempat yang sama: satu buku, dua nama, satu halaman kosong untuk besok.'}}

# ============================================================== TULIS
story = {'meta': {'title': 'Arland & Sofia: Our Little Universe', 'status': 'draft_fiction', 'game_format': 'olu-story-2',
                  'note_id': 'Semua dialog adalah draft fiksi, bukan fakta hubungan nyata.'},
         'speakers': SPEAKERS,
         'emotions': EMOTIONS,
         'chapters': [{'id': c, 'title': t} for c, t in CHAPTERS],
         'canon_event_ids': ref['canon_event_ids'], 'puzzle_orders': ref['puzzle_orders'], 'scenes': scenes}
def _acts(lst):
    for a in lst:
        yield a
        if a.get('do') == 'if': yield from _acts(a['then']); yield from _acts(a['else'])
_all = [a for s_ in steps for i_ in s_.get('interactables', []) for a in _acts(i_['actions'])] + [a for s_ in steps if s_.get('complete') for a in _acts(s_['complete']['actions'])]
_all += [a for i_ in SIDE for a in _acts(i_['actions'])] + [a for n in NPCS for d_ in n['dialogs'] for a in _acts(d_['actions'])]
used_items = {a['id'] for a in _all if a.get('do') in ('item', 'removeItem')}
for a in _all:
    if a.get('do') == 'scene': assert a['id'].replace('@$ROUTE', '@arland') in scenes, a['id']
    if a.get('do') == 'minigame': assert a['id'] in MINIGAMES, a['id']
used_items.update(g['item'] for shop in SHOPS.values() for g in shop['goods'])
missing_items = used_items - set(ITEMS)
if missing_items: raise SystemExit('Item tanpa definisi: %s' % missing_items)
# ---- hewan ke peta & snap titik jadwal NPC ke sel terjangkau (kaki 18x8 px, grid 6 px, jarak bebas >= 10 px)
for aid, lst in ANIMALS.items(): maps[aid]['animals'] = lst
_PROPS = json.load(open(os.path.join(DATA, 'props.json'), encoding='utf-8'))['props']
def _blocked(aid, x, y, pad=0):
    m = maps[aid]; x0, y0, x1, y1 = x - 9 - pad, y - 6 - pad, x + 9 + pad, y + 2 + pad
    if x0 < 0 or y0 < 0 or x1 > m['w'] or y1 > m['h']: return True
    rs = [tuple(r) for r in m['walls']] + [(p['x'] - _PROPS[p['type']]['cw'] / 2, p['y'] - _PROPS[p['type']]['ch'], _PROPS[p['type']]['cw'], _PROPS[p['type']]['ch'])
          for p in m['props'] if _PROPS[p['type']].get('cw', 0) > 0 and _PROPS[p['type']].get('ch', 0) > 0]
    if any(x0 < rx + rw and x1 > rx and y0 < ry + rh and y1 > ry for (rx, ry, rw, rh) in rs): return True
    return any(((px - cx) / rx) ** 2 + ((py - cy) / ry) ** 2 < 1 for (cx, cy, rx, ry) in m['ellipses'] for (px, py) in ((x0, y0), (x1, y0), (x0, y1), (x1, y1), (x, y)))
_REACH = {}
def _reach(aid):
    if aid in _REACH: return _REACH[aid]
    from collections import deque
    m = maps[aid]; st = 6; seen = set(); q = deque()
    for (sx, sy) in [tuple(m['spawn'])] + [(d['tx'], d['ty']) for a_ in maps.values() for d in a_['doors'] if d['to'] == aid]:
        c = (int(sx // st), int(sy // st))
        if c not in seen and not _blocked(aid, c[0] * st + 3, c[1] * st + 3): seen.add(c); q.append(c)
    while q:
        cx, cy = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n_ = (cx + dx, cy + dy)
            if n_ not in seen and not _blocked(aid, n_[0] * 6 + 3, n_[1] * 6 + 3): seen.add(n_); q.append(n_)
    _REACH[aid] = seen; return seen
def _snap(aid, x, y):
    seen = _reach(aid); best = None
    for (cx, cy) in seen:
        px, py = cx * 6 + 3, cy * 6 + 3; d = (px - x) ** 2 + (py - y) ** 2
        if best is None or d < best[0]:
            if _blocked(aid, px, py, 10): continue
            best = (d, px, py)
    if best is None: raise SystemExit('Tidak ada titik terjangkau di %s dekat %s,%s' % (aid, x, y))
    return best[1], best[2], best[0] ** 0.5
# Tambahan event data-driven (v2.7), setelah kalkulasi jangkauan peta.
exec(open(os.path.join(os.path.dirname(__file__), 'content', 'world_events_v27.py'), encoding='utf-8').read())
_moved = []
for n in NPCS:
    for e in n.get('schedule', []):
        if e.get('hidden'): continue
        x, y, dd = _snap(e['area'], e['x'], e['y'])
        if dd > 1: _moved.append((n['id'], e['at'], e['area'], round(dd)))
        e['x'], e['y'] = x, y
    if n['id'] in ('rini', 'harun', 'tika', 'eko', 'wulan', 'darmo'):
        n['x'], n['y'], _ = _snap(n['area'], n['x'], n['y'])
_far = [m_ for m_ in _moved if m_[3] > 60]
if _far: print('peringatan: titik jadwal digeser jauh:', _far)
print('jadwal NPC:', sum(len(n.get('schedule', [])) for n in NPCS), 'titik |', sum(1 for n in NPCS if n.get('schedule')), 'NPC berjadwal | hewan:', sum(s_['n'] for l_ in ANIMALS.values() for s_ in l_), 'di', len(ANIMALS), 'area')
json.dump(story, open(os.path.join(DATA, 'story.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(quests, open(os.path.join(DATA, 'quests.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump({'_doc': 'Dibuat oleh tools/build_maps.py + build_content.py (kunci pintu).', 'areas': maps}, open(os.path.join(DATA, 'maps.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(book, open(os.path.join(DATA, 'memory_book.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
nlines = sum(len(s_['lines']) + sum(len(l) for c in s_.get('choices', []) for l in c.get('byRoute', {}).values()) for s_ in scenes.values())
print('scene', len(scenes), '| baris dialog', nlines, '| step', len(steps), '| side', len(SIDE), '| npc', len(NPCS), '| item', len(ITEMS), '| entri', len(ENTRIES))
