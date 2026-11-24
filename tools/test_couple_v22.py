"""Verifikasi aset dan katalog couple v2.2 (bukan tes rendering OpenGL/HP)."""
from pathlib import Path
from PIL import Image, ImageChops
import json
root = Path(__file__).resolve().parent.parent
assets = root / 'android' / 'assets'
q = json.loads((assets/'data'/'quests.json').read_text(encoding='utf8'))
st = json.loads((assets/'data'/'story.json').read_text(encoding='utf8'))
book = json.loads((assets/'data'/'memory_book.json').read_text(encoding='utf8'))
actions = q['romance']['coupleActions']
assert len(actions) == 8 and len({a['id'] for a in actions}) == 8
scenes = st['scenes']
entries = {x['id']: x for x in book['entries']}
assert len(entries) == len(book['entries']), 'Duplicate Memory Book ID; satu memori menimpa memori lain'
assert len(scenes) >= 319, 'Jumlah adegan seharusnya tidak turun'
checks = 0
for action in actions:
    assert action['affection'] >= 0
    assert action['gesture'] in {'handwalk','hug','lean','photo','highfive','dance'}
    for route in ('arland','sofia'):
        sc = scenes[action['scene'][route]]
        assert sc['route'] == route and len(sc['lines']) >= 4
        checks += 1
    flag = 'ROM_ACT_' + action['id'].upper() + '_ONCE'
    assert any(e['unlock'] == flag for e in entries.values())
    checks += 1
pose_names = ['sit', 'wave', 'give', 'reach', 'bow', 'hold_l', 'hold_r', 'cheer', 'hug', 'lean', 'photo', 'highfive', 'dance', 'read', 'water', 'sweep']
actors = []
for p in sorted((assets/'characters').glob('*/walk.png')):
    base = Image.open(p).convert('RGBA')
    if base.size != (144,288): continue
    pose = Image.open(p.parent/'poses.png').convert('RGBA')
    assert pose.size == (384,72*len(pose_names)), p
    for posidx in range(8,13):
        for direction in range(4):
            c1 = pose.crop((direction*96,posidx*72,direction*96+48,(posidx+1)*72))
            c2 = pose.crop((direction*96+48,posidx*72,direction*96+96,(posidx+1)*72))
            assert c1.getbbox() and c2.getbbox(), (p,posidx,direction)
            assert ImageChops.difference(c1,c2).getbbox(), (p,posidx,direction,'animation phases identical')
            checks += 1
    actors.append(p.parent.name)
assert len(actors)>=25 and {'arland','sofia'}.issubset(actors)
# Sync behavior must be implemented in the actual screen/cutscene, not only in JSON and UI.
cu = (root/'core/src/main/java/com/arlandsofia/olu/game/CutscenePlayer.java').read_text()
sc = (root/'core/src/main/java/com/arlandsofia/olu/screens/GameScreen.java').read_text()
assert 'case "pair":' in cu and 'pl.setPose(pp, dur); other.setPose(op, dur);' in cu
assert 'p.holdingHands' in sc and 'area.blocked(tx, ty)' in sc
checks += 4
print(f'COUPLE v2.2 visual/data OK: {len(actors)} pose atlases, 5 pose baru × 2 frame × 4 arah, 8 aksi route, {checks} checks')
