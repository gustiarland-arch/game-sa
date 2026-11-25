"""v6 story pass (idempotent, keeps every scene id, flag, choice and the canon ending).

1. Optional panorama scenes (V50-VIEW-<AREA>-<ROUTE>): the four shared template lines are
   replaced by per-location narration and dialogue (v6_story_text.VIEW).
2. Optional World Trace scenes (V49-DISC-*): the shared meta closing line is replaced by a
   per-location closing (v6_story_text.DISC_CLOSE).
3. Expression pass: spoken lines still marked "neutral" get an emotion from their wording
   (portrait + emote come from story.json "emotions"). Narrator lines stay neutral.

Usage: python3 tools/v6/story/apply_story_v6.py [--dry]
"""
import sys, json, re, collections
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from v6_story_text import VIEW, DISC_CLOSE   # noqa: E402

ROOT = HERE.parents[2]
DATA = ROOT / 'android' / 'assets' / 'data'
VIEW_TEMPLATE = {
    0: "Kalian menaiki tangga satu per satu. Tempat yang baru terlihat terbentang di sisi lain railing.",
    3: "Angin lewat pelan. Kalian memilih menikmati pemandangan sebelum turun lagi.",
    6: "Satu panorama baru tersimpan. Jalan cerita utama tidak berubah.",
}
DISC_TEMPLATE = "Sebuah jejak kecil tersimpan di Memory Book. Kisah utama tetap berjalan seperti semula."

RULES = [   # first match wins; patterns are matched on the lower-cased line
    ('jatuh_cinta', r'\b(sayang|cinta|jatuh hati|cantik banget|kamu ada di semuanya)\b'),
    ('tertawa', r'(haha|hehe|wkwk|\blucu\b|ngakak|\bcurang\b)'),
    ('kaget', r'^(eh|hah|lho|loh|astaga|ya ampun|wah|waduh|aduh|serius\?)\b'),
    ('penasaran', r'\bpenasaran\b'),
    ('sedih', r'\b(sedih|maaf|menyesal|nyesel|kecewa|kangen|rindu|kehilangan|menangis|nangis|terlambat|telat|sendirian|sepi)\b'),
    ('khawatir', r'\b(khawatir|takut|cemas|gugup|hati-hati|jangan-jangan|kalau aku salah|ragu)\b'),
    ('malu', r'\b(malu|deg-degan|salting|pipiku|pipimu)\b'),
    ('lega', r'\b(syukurlah|lega|akhirnya|untung(lah)?|berhasil)\b'),
    ('penasaran', r'(\?\s*["”]?$|\bpenasaran\b|\bgimana kalau\b|\bapa ya\b|\bkenapa\b)'),
    ('senang', r'(\b(senang|seru|asyik|asik|makasih|terima kasih|bangga|keren|hore|yay|lumayan banget)\b|!\s*["”]?$)'),
    ('serius', r'\b(janji|harus|nggak boleh|tidak boleh|berani|jujur|belajar|memilih|keputusan|bertanggung jawab|ingin tetap|aku ingin|aku mau)\b'),
    ('senyum', r'\b(kita|bareng|bersama|kamu|pelan-pelan|nanti|yuk|semoga|ayo)\b'),
]
RULES = [(e, re.compile(p)) for e, p in RULES]


def classify(text):
    t = text.strip().lower()
    for e, rx in RULES:
        if rx.search(t):
            return e
    return 'neutral'


def spoken_lines(o):
    if isinstance(o, dict):
        if 's' in o and 't' in o and isinstance(o.get('t'), str):
            yield o
        for v in o.values():
            yield from spoken_lines(v)
    elif isinstance(o, list):
        for v in o:
            yield from spoken_lines(v)


def main():
    dry = '--dry' in sys.argv
    sp = DATA / 'story.json'; qp = DATA / 'quests.json'
    S = json.loads(sp.read_text(encoding='utf-8'))
    Q = json.loads(qp.read_text(encoding='utf-8'))
    sc = S['scenes']
    stats = collections.Counter()
    # 1. panorama scenes
    for sid, s in sc.items():
        m = re.match(r'V50-VIEW-(.+)-(ARLAND|SOFIA)$', sid)
        if not m:
            continue
        area, route = m.group(1), m.group(2).lower()
        arrive, pause, (pov, e1), (partner, e2), close = VIEW[area]
        L = s['lines']
        if L[0]['t'] == VIEW_TEMPLATE[0]:
            L[0]['t'] = arrive; stats['view_arrive'] += 1
        if L[3]['t'] == VIEW_TEMPLATE[3]:
            L[3]['t'] = pause; stats['view_pause'] += 1
        if L[6]['t'] == VIEW_TEMPLATE[6]:
            other = 'sofia' if route == 'arland' else 'arland'
            L[4] = {'s': route, 'e': e1, 't': pov}
            L[5] = {'s': other, 'e': e2, 't': partner}
            L[6]['t'] = close; stats['view_dialogue'] += 1
    # 2. world-trace closings
    for sid, s in sc.items():
        m = re.match(r'V49-DISC-(.+)-[AS]$', sid)
        if not m:
            continue
        for l in s['lines']:
            if l['t'] == DISC_TEMPLATE:
                l['t'] = DISC_CLOSE[m.group(1)]; stats['disc_close'] += 1
    # 3. expression pass
    before = collections.Counter()
    for root in (sc, Q):
        for l in spoken_lines(root):
            if l['s'] == 'narrator' or l.get('e', 'neutral') != 'neutral':
                continue
            before['neutral_spoken'] += 1
            e = classify(l['t'])
            if e != 'neutral':
                l['e'] = e; stats['emotion_' + e] += 1
    S['meta']['storyV6'] = 'v6.0 story pass: per-location panorama + world-trace text, expression pass'
    for k, v in sorted(stats.items()):
        print(f'{k:22s} {v}')
    print('spoken neutral before', before['neutral_spoken'], 'still neutral',
          before['neutral_spoken'] - sum(v for k, v in stats.items() if k.startswith('emotion_')))
    if not dry:
        sp.write_text(json.dumps(S, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        qp.write_text(json.dumps(Q, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print('written')


if __name__ == '__main__':
    main()
