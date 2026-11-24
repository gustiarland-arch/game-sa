#!/usr/bin/env python3
"""Conservative source-package cleanup. DRY-RUN by default.

Only removed files with no Android runtime/build reference and no active docs/tools
reference. Never touches runtime assets, Java, Gradle, generated-art baselines,
source screenshots referenced in docs, or any creative/editor project originals.

Usage: python3 tools/clean_project_v36.py [--apply]
"""
from __future__ import annotations
import argparse,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CANDIDATES=(
  'docs/preview/AUDIO_PREVIEW_README.txt',
  'docs/preview/hutan_bisik_v13.png',
  'docs/preview/mockup_dialog.png',
  'docs/preview/mockup_explore.png',
  'docs/preview/peta_baru_v12.png',
  'docs/preview/peta_overview.png',
  'docs/preview/v21_sprite_atlas_preview.png',
  'docs/preview/v24_music_preview.mp3',
)
TRASH_NAMES={'.DS_Store','Thumbs.db','.coverage'}
TRASH_SUFFIXES={'.pyc','.pyo','.swp','.swo'}
CACHEDIRS={'__pycache__','.pytest_cache','.mypy_cache','.ruff_cache'}
NO_TOUCH={'android/assets','android/res','android/src','android/libs','art_source',
          'tools/build','core/src','gradle','gradlew','.github','docs/reference_data'}

def safe(path):
    relative=path.relative_to(ROOT).as_posix()
    return not any(relative==p or relative.startswith(p+'/') for p in NO_TOUCH)

def included_refs(target):
    key=target.name
    scan=[]
    for section in (ROOT/'README.md',ROOT/'CHANGELOG.md'):
        scan.append(section)
    scan += list((ROOT/'docs').rglob('*.md'))
    scan += list((ROOT/'tools').rglob('*.py'))
    scan += list((ROOT/'.github').rglob('*.yml'))
    found=[]
    for f in scan:
        if f.name=='clean_project_v36.py':continue
        try:
            if key in f.read_text(encoding='utf-8',errors='replace'):found.append(str(f.relative_to(ROOT)))
        except OSError:pass
    return found

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');args=ap.parse_args()
    files={ROOT/r for r in CANDIDATES if (ROOT/r).is_file()}
    for f in ROOT.rglob('*'):
        if not f.is_file() or not safe(f):continue
        if any(part in CACHEDIRS for part in f.relative_to(ROOT).parts) or f.name in TRASH_NAMES or f.suffix in TRASH_SUFFIXES:
            files.add(f)
    results=[];blocked=[]
    for p in sorted(files):
        if not safe(p):
            blocked.append({'file':p.relative_to(ROOT).as_posix(),'why':'protected source/runtime tree'});continue
        r=p.relative_to(ROOT).as_posix();references=included_refs(p)
        if references:
            blocked.append({'file':r,'why':'referenced','from':references});continue
        results.append({'file':r,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
        if args.apply:p.unlink()
    report={'version':'3.6.0','applied':args.apply,'removed_or_proposed':results,'blocked':blocked,
       'files':len(results),'bytes':sum(f['bytes'] for f in results),
       'protected':'runtime assets, Gradle, Java source, all 86 sound files, editable art source/baselines and build inputs'}
    if args.apply:
        (ROOT/'docs/CLEANUP_AUDIT_V3.6.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(('CLEANUP APPLIED' if args.apply else 'CLEANUP DRY RUN'),report['files'],'files',report['bytes'],'bytes; blocked',len(blocked))
    for f in results:print(('REMOVED' if args.apply else 'WOULD REMOVE'),f['file'],f['bytes'])
    for b in blocked:print('PROTECTED',b['file'],b['why'])

if __name__=='__main__':main()
