#!/usr/bin/env python3
"""Deterministic static checks for v5.1. No Android SDK required."""
from pathlib import Path
from PIL import Image
import json, hashlib, collections
R=Path(__file__).resolve().parents[1];A=R/'android/assets';D=A/'data'
m=json.loads((D/'maps.json').read_text(encoding='utf-8'));q=json.loads((D/'quests.json').read_text(encoding='utf-8'))
p=json.loads((D/'props.json').read_text(encoding='utf-8'))['props'];s=json.loads((D/'story.json').read_text(encoding='utf-8'))
sites=json.loads((R/'tools/v51_environment_sites.json').read_text(encoding='utf-8'))
checks=0
def need(ok,msg):
 global checks
 checks+=1
 if not ok:raise AssertionError(msg)
need(len(m['areas'])==29,'29 original maps')
need(len(s['scenes'])==874,'874 story scenes unchanged')
need(len(q['steps'])==157,'157 story steps unchanged')
need(len(sites)==21,'21 curated sites')
need('SCHEMA = 8' in (R/'core/src/main/java/com/arlandsofia/olu/logic/Progress.java').read_text(),'save schema unchanged')
need(any(v in (R/'build.gradle').read_text() for v in ("appVersionName = '5.1.0'","appVersionName = '5.2.0'")),'version')
need('android.permission.INTERNET" tools:node="remove"' in (R/'android/AndroidManifest.xml').read_text(),'offline')
usage=collections.Counter()
for name,a in m['areas'].items():
 need((A/a['image']).is_file(),'original map preserved '+name)
 need(len(a.get('props',[]))>0,'props '+name)
 need('environmentV51' in a,'environment notes '+name)
 for entry in a['props']:
  if entry['type'].startswith('v51_'):
   usage[entry['type']]+=1
   need(entry['type'] in p,'defined prop '+entry['type'])
   need((A/p[entry['type']]['image']).is_file(),'prop asset '+entry['type'])
   need(0<entry['x']<a['w'] and 0<entry['y']<a['h'],'decor inside map '+name)
 for t in a.get('elevationPlatforms',[]):
  need(name in sites,'only curated platforms '+name)
  site=sites[name]
  for f in ('x','y','w','h','rise','stairWidth'):
   need(t[f]==site[f],f'{name} terrace {f} matches design')
  need(t['stairLength']==site['stair'],'stairs length')
  need(t['y']+t['h']+t['stairLength']+15<a['h'],'stairs foot map bounds')
  need(t['w']>t['stairWidth']+28,'railing clear width')
  for k in ('image','front'):
   f=A/t[k]
   need(f.is_file(),str(f))
   with Image.open(f) as image:
    need(image.mode=='RGBA','alpha for editable layer '+str(f))
    need(image.size==(t['w']+40,t['h']+t['stairLength']+64),'correct render dimensions '+str(f))
    need(image.getbbox() is not None,'non-empty image '+str(f))
  iid='V50_VIEW_'+name.upper()
  it=next((it for it in q['side'] if it['id']==iid),None)
  need(it is not None and t['x']<it['x']<t['x']+t['w'] and t['y']<it['y']<t['y']+t['h'],'viewpoint on terrace '+name)
for key in sites:
 a=m['areas'][key];need(len(a['elevationPlatforms'])==1,'exactly one terrace '+key)
 need(usage['v51_approach_'+key]==1,'one connecting approach path '+key)
 need(len(sites[key]['reason'])>25,'visual placement rationale '+key)
for k in p:
 if k.startswith('v51_') and not k.startswith('v51_approach_'):
  need(usage[k]>0,'environment art is integrated, not unused '+k)
expected=33+21*3
new=[x for x in list((A/'maps/environment_v51').glob('*.png'))+list((A/'props/environment_v51').glob('*.png'))]
need(len(new)==expected,f'expected {expected} new image files; got {len(new)}')
for f in new:
 need(f.stat().st_size>120,'non-placeholder art '+f.name)
 with Image.open(f) as im:
  need(im.mode=='RGBA' and im.getbbox() is not None,'transparent real art '+f.name)
need(len(q['worldDiscoveries'])==29,'v4.9 discoveries preserved')
print(f'V5.1 ENVIRONMENT QA PASSED: {checks} checks; {len(sites)} walkable terraces; 33 new props; {len(new)} image assets; {sum(usage.values())} map prop placements; {len(m["areas"])} dressed areas')
