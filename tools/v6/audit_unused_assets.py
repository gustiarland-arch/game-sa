"""v6 asset audit: which files under android/assets the game can never load.

Rules
  A. Character sheets superseded by the loader's own fallback chain in Assets.java
     (walk_v53 > v37 > v32 > walk_plus; idle_v53 > v37 > v32; *_8dir_v53 > *_8dir_v462;
     poses_v53 > poses). walk.png is always kept (frame() base sheet).
  B. Any other asset whose relative path, path-without-extension, file name and stem
     appear nowhere in runtime code (core/android java) or runtime data (assets/*.json).
Prints JSON {"superseded": [...], "unreferenced": [...], "bytes": n}. Never deletes.
"""
import json, os, re, sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
A = ROOT / 'android' / 'assets'
corpus = []
for base in (ROOT / 'core' / 'src' / 'main', ROOT / 'android' / 'src'):
    for p in base.rglob('*.java'):
        corpus.append(p.read_text(encoding='utf-8', errors='ignore'))
for p in A.rglob('*.json'):
    corpus.append(p.read_text(encoding='utf-8', errors='ignore'))
text = '\n'.join(corpus)
tokens = set(re.findall(r'[A-Za-z0-9_./-]+', text))

CHAINS = [['walk_v53', 'walk_v37', 'walk_v32', 'walk_plus'], ['idle_v53', 'idle_v37', 'idle_v32'],
          ['walk_8dir_v53', 'walk_8dir_v462'], ['idle_8dir_v53', 'idle_8dir_v462'], ['poses_v53', 'poses']]
superseded = []
for cdir in sorted((A / 'characters').iterdir()):
    if not cdir.is_dir():
        continue
    for chain in CHAINS:
        have = [n for n in chain if (cdir / (n + '.png')).exists()]
        superseded += [str((cdir / (n + '.png')).relative_to(A)) for n in have[1:]]

lits = set()
for base in (ROOT / 'core' / 'src' / 'main', ROOT / 'android' / 'src'):
    for q in base.rglob('*.java'):
        lits.update(m[1:-1] for m in re.findall(r'"(?:[^"\\\n]|\\.)*"', q.read_text(encoding='utf-8', errors='ignore')) if len(m) > 4)
prefixes = [l for l in lits if '/' in l and (l.endswith('_') or l.endswith('/'))]
suffixes = [l for l in lits if l.startswith('_') or (l.startswith('.') is False and l.endswith(('.png', '.ogg', '.wav')) and '/' not in l)]
unref = []
for p in sorted(A.rglob('*')):
    if not p.is_file() or p.suffix == '.json':
        continue
    rel = str(p.relative_to(A))
    if rel in superseded or rel.startswith('characters/'):
        continue  # characters are resolved by rule A (names are built at runtime)
    stem_rel = rel.rsplit('.', 1)[0]
    if rel in tokens or stem_rel in tokens or p.name in tokens or p.stem in tokens:
        continue
    # directory-built names: "<dir>/" + id + ext — accept if the stem occurs as a quoted id
    if ('"%s"' % p.stem) in text:
        continue
    if p.suffix == '.txt':
        continue  # licences and notices ship with their fonts
    if any(rel.startswith(x) for x in prefixes) or any(rel.endswith(x) for x in suffixes if len(x) > 4):
        continue  # name assembled at runtime from a literal prefix/suffix
    unref.append(rel)

size = sum((A / r).stat().st_size for r in superseded + unref)
json.dump({'superseded': superseded, 'unreferenced': unref, 'bytes': size}, sys.stdout, indent=1)
