"""Re-place the props of an already migrated v6 map from its script, then validate every
quest/NPC/door point of that area again. Usage: refresh_props.py <area> <module>"""
import sys, json, importlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import common

area, modname = sys.argv[1], sys.argv[2]
mod = importlib.import_module(modname)
M = json.loads((common.A / 'data/maps.json').read_text(encoding='utf-8'))
Q = json.loads((common.A / 'data/quests.json').read_text(encoding='utf-8'))
P = json.loads((common.A / 'data/props.json').read_text(encoding='utf-8'))['props']
a = M['areas'][area]
assert a.get('v6Layout'), 'not a v6 map'
a['props'] = mod.props()
pts = [(m[0], m[3], m[4], m[5]) for m in common.migrate_quests(Q, area, lambda x, y: (x, y))]
pts += [(d['id'], d['tx'], d['ty'], None) for b in M['areas'].values() for d in b.get('doors', []) if d.get('to') == area]
pts += [('examine ' + e['id'], e['x'], e['y'], e.get('r')) for e in a.get('examine', [])]
bad = common.validate(a, P, pts)
for b in bad:
    print('INVALID', *b)
print(area, len(pts), 'points,', len(bad), 'invalid')
if not bad:
    (common.A / 'data/maps.json').write_text(json.dumps(M, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('props refreshed')
