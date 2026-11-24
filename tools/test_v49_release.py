#!/usr/bin/env python3
"""v4.9 static content audit. Does not mutate source files."""
from pathlib import Path
import json

root=Path(__file__).resolve().parents[1]
data=root/'android/assets/data'
read=lambda p:json.loads((data/p).read_text(encoding='utf-8'))
quests=read('quests.json'); story=read('story.json'); memory=read('memory_book.json'); maps=read('maps.json')['areas']
checks=0
def check(test,msg):
    global checks
    checks += 1
    if not test:raise AssertionError(msg)

old_count=len([s for s in story['scenes'] if not s.startswith('V49-')])
check(old_count==736,'v4.8 preexisting scene count changed')
check(len(maps)==29,'original map count changed')
check(len(quests['steps'])==157,'original canonical step count changed')
check(len(quests['worldDiscoveries'])==29,'one secret per area missing')
check(len([e for e in quests['worldEvents'] if e['id'].startswith('v49_')])==18,'18 world events expected')
check(len([x for x in quests['minigames'] if x.startswith('v49_echo_')])==14,'14 echo games expected')
check(len([s for s in story['scenes'] if s.startswith('V49-')])==96,'96 new scenes expected')
check(len(memory['entries'])==335,'335 memory entries expected')
world_seen=set(); flags=set(); ids=set(); chapters=['PRO','C01','C02','C03','C04','C05','C06','EPI']
for d in quests['worldDiscoveries']:
    check(d['area'] in maps and d['area'] not in world_seen,'missing/duplicate discovery area')
    world_seen.add(d['area']);check(d['flag'] not in flags,'duplicate flag');flags.add(d['flag'])
    check(d['minChapter'] in chapters and chapters.index(d['minChapter'])>=2,'invalid chapter gate')
    it=next((s for s in quests['side'] if s['id']==d['id']),None)
    check(it is not None and it['area']==d['area'] and it['id'] not in ids,'discovery not wired/duplicate')
    ids.add(it['id'])
    for route,suffix in (('arland','A'),('sofia','S')):
        scene=story['scenes'].get('V49-DISC-'+d['area'].upper()+'-'+suffix)
        check(scene is not None and scene['route']==route and len(scene['lines'])>=4,'route discovery scene missing')
    check(any(x['unlock']==d['flag'] for x in memory['entries']),'discovery not included in Memory Book')
    if d['minigame']:
        game=quests['minigames'].get(d['minigame'])
        check(game is not None and game.get('type')=='v49_echo','minigame not connected')
        pats=game['patterns']
        for route in ('arland','sofia'):
            check([len(x) for x in pats[route]]==[3,4,5],'invalid echo pattern length')
            for stage in pats[route]:
                for n in stage:check(isinstance(n,int) and 0<=n<=3,'invalid echo symbol')
check(world_seen==set(maps),'not all original areas contain discoveries')
for ev in quests['worldEvents']:
    if not ev['id'].startswith('v49_'):continue
    check(ev['area'] in maps,'event area unknown')
    for route in ('arland','sofia'):
        sc=story['scenes'].get(ev['scenes'][route])
        check(sc is not None and sc['route']==route and len(sc['lines'])>=6,'event route script malformed')
    it_id='V49_WE_'+ev['id'][len('v49_'):].upper()
    it=next((x for x in quests['side'] if x['id']==it_id),None)
    check(it is not None and it['when']['worldEventReady']==ev['id'],'event not playable in area')
    check(any(x['unlock']=='WORLD_EVENT_'+ev['id'].upper()+'_ONCE' for x in memory['entries']),'event memory missing')
check(any(e['unlock']=='V49_WORLD_ATLAS_UNLOCK' for e in memory['entries']),'atlas bonus missing')
import xml.etree.ElementTree as ET
manifest=ET.parse(root/'android/AndroidManifest.xml').getroot()
android='{http://schemas.android.com/apk/res/android}'
tools='{http://schemas.android.com/tools}'
check(all(node.get(tools+'node')=='remove' for node in manifest.findall('uses-permission')
          if node.get(android+'name','').endswith(('INTERNET','ACCESS_NETWORK_STATE','ACCESS_WIFI_STATE'))),
      'network permission must be explicitly removed from merged manifest')
check("appVersionName = '4.9.0'" in (root/'build.gradle').read_text(),'version incorrect')
print('V4.9 STATIC ASSET/DATA AUDIT PASSED:',checks,'content checks')
