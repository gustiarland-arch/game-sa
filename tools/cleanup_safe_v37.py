#!/usr/bin/env python3
"""Conservative source cleanup. ONLY disposable caches/temp files, NEVER art source.
Dry-run by default. --apply additionally removes disposable cache files/empty dirs.
"""
from pathlib import Path
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parent.parent
parser=argparse.ArgumentParser()
parser.add_argument('--apply',action='store_true')
args=parser.parse_args()
protected={'android','core','art_source','gradle','docs'}
allowed_names={'.DS_Store','Thumbs.db'}
allowed_suffixes={'.pyc','.pyo','.tmp','.swp'}
results=[]
for f in ROOT.rglob('*'):
 if not f.is_file():continue
 rel=f.relative_to(ROOT)
 # Runtime content and user assets are protected by construction.
 if rel.parts[0] in protected:continue
 if f.name not in allowed_names and f.suffix not in allowed_suffixes:continue
 results.append({'path':str(rel),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
 if args.apply: f.unlink()
if args.apply:
 for d in sorted(ROOT.rglob('__pycache__'),key=lambda x:len(x.parts),reverse=True):
  if d.parts[len(ROOT.parts)] in protected:continue
  if d.is_dir() and not any(d.iterdir()):d.rmdir()
report={'policy':'remove only transient cache files outside android/core/art_source/gradle/docs',
        'applied':args.apply,'removed_count':len(results) if args.apply else 0,
        'removed_bytes':sum(x['bytes'] for x in results) if args.apply else 0,
        'candidates':results}
(ROOT/'docs/CLEANUP_AUDIT_V3.7.json').write_text(json.dumps(report,indent=2)+'\n')
print('V3.7 SAFE CLEANUP:',len(results),'disposable files found; applied:',args.apply)
