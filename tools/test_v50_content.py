#!/usr/bin/env python3
"""Static QA for source v5.0; no Android SDK/GPU required."""
import re
from pathlib import Path
import json,struct,sys
R=Path(__file__).resolve().parents[1]; A=R/'android/assets'
q=json.loads((A/'data/quests.json').read_text(encoding='utf-8'))
s=json.loads((A/'data/story.json').read_text(encoding='utf-8'))
m=json.loads((A/'data/maps.json').read_text(encoding='utf-8'))
checks=0
def assertq(condition,text):
 global checks
 checks+=1
 if not condition:raise AssertionError(text)
assertq(len(m['areas'])==29,'29 original areas preserved')
assertq(len(q['steps'])==157,'157 original main story steps preserved')
assertq(len(s['scenes'])>=874,'added route-specific cinematic scenes present')
assertq(len(q.get('worldDiscoveries',[]))==29,'29 existing v4.9 discoveries unchanged')
assets=[p for p in A.rglob('*') if p.is_file()]
areas=0
for area,meta in m['areas'].items():
 for t in meta.get('elevationPlatforms',[]):
  areas+=1
  assertq(t['rise']>0,'rise positive '+area)
  assertq(t['x']>=0 and t['y']>=0,'terrain coordinates positive '+area)
  assertq(t['x']+t['w']<=meta['w'] and t['y']+t['h']+t['stairLength']<=meta['h'],'terrace in map bounds '+area)
  for key in ('image','front'):
   name=t[key];f=A/name
   assertq(f.is_file() and f.stat().st_size>180,'art exists '+name)
   data=f.read_bytes()[:24]
   assertq(data[:8]==b'\x89PNG\r\n\x1a\n','PNG signature '+name)
   width,height=struct.unpack('>II',data[16:24]);assertq((width,height)==(t['w']+40,t['h']+t['stairLength']+64),'PNG dimensions '+name)
  it=next((i for i in q['side'] if i['id']=='V50_VIEW_'+area.upper()),None)
  assertq(it is not None,'panorama playable '+area)
  assertq(t['x']<it['x']<t['x']+t['w'] and t['y']<it['y']<t['y']+t['h'],'panorama actually on terrace '+area)
  for who in ('ARLAND','SOFIA'):
   scene=s['scenes'].get('V50-VIEW-'+area.upper()+'-'+who)
   assertq(scene is not None,'route scene '+area+who)
   assertq(len(scene['lines'])>=6,'dialogue content '+area+who)
assertq(areas==0,'v6: stair platforms removed')
# v6: each panorama is a ground viewpoint now; it must still exist with both route scenes
for area in ('plaza','taman_kota','riverside','hutan_bisik','bukit_bintang'):
  it=next((i for i in q['side'] if i['id']=='V50_VIEW_'+area.upper()),None)
  assertq(it is not None and it['area']==area,'panorama playable '+area)
  for who in ('ARLAND','SOFIA'):
    assertq(len(s['scenes']['V50-VIEW-'+area.upper()+'-'+who]['lines'])>=6,'dialogue content '+area+who)
for id in ('v50_plaza_ascent','v50_rain_reflections','v50_starlit_steps','v50_tomorrow_horizon','v50_cafe_highlight'):
 assertq((A/'audio/music'/f'{id}.ogg').stat().st_size>2000,'new score '+id)
for id in ('v50_highland_breeze','v50_memory_air'):
 assertq((A/'audio/ambience'/f'{id}.ogg').stat().st_size>2000,'new ambience '+id)
for id in ('v50_stair_foot','v50_stair_enter','v50_view_wind','v50_memory_shimmer','v50_panoramic_reveal'):
 assertq((A/'audio/sfx'/f'{id}.wav').stat().st_size>100,'new SFX '+id)
manifest=(R/'android/AndroidManifest.xml').read_text()
assertq('android.permission.INTERNET" tools:node="remove"' in manifest,'offline manifest explicitly removes INTERNET permission')
java=(R/'core/src/main/java/com/arlandsofia/olu/logic/Progress.java').read_text()
assertq('SCHEMA = 8' in java,'save schema preserved')
assertq(re.search(r"appVersionName = '5\.\d+\.\d+'",(R/'build.gradle').read_text()) is not None,'v5.0+ version')
print(f'V5.0 CONTENT QA PASSED: {checks} assertions, {areas} elevation areas, {len(s["scenes"])} scenes, {len(assets)} asset files')
