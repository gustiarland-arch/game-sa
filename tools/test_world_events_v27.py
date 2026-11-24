#!/usr/bin/env python3
"""Regresi statis v2.7. Hasil tidak membuktikan Android runtime atau FPS."""
import json
import re
from pathlib import Path

R=Path(__file__).resolve().parents[1]
A=R/'android/assets'
q=json.loads((A/'data/quests.json').read_text(encoding='utf-8'))
s=json.loads((A/'data/story.json').read_text(encoding='utf-8'))
b=json.loads((A/'data/memory_book.json').read_text(encoding='utf-8'))
m=json.loads((A/'data/maps.json').read_text(encoding='utf-8'))['areas']
num=0
def ck(v,msg):
    global num
    num+=1
    assert v,msg

events=q['worldEvents']; ck(len(events)==14,'must have 14 events')
ck(len(s['scenes'])==398,'26 new route-authored scenes')
ck(len(q['steps'])==93,'existing main story steps preserved')
ck(len(q['sideQuests'])==25,'all sidequests preserved')
ck(len(b['entries'])==129,'14 new Memory Book entries')
ck(len(q['side'])==149,'14 new side interaction markers')
seen=set()
for e in events:
    ck(e['id'] not in seen,('duplicate',e['id']));seen.add(e['id'])
    ck(e['area'] in m,('area',e['id']))
    ck(0<=e['x']<=m[e['area']]['w'] and 0<=e['y']<=m[e['area']]['h'],('coordinates',e['id']))
    ck(e['r']>=50,('tap radius',e['id']))
    ck(0 <= e['affection'] <= 8 and 0<=e['coins']<=12,('reward',e['id']))
    ck(e['minChapter'] in ('C02','C03','C04','C05'),('chapter',e['id']))
    ck(len(e['hours'])==2,('time window',e['id']))
    ck(len(e['scenes'])==(1 if e['route'] else 2),('POV scenes',e['id']))
    for route,sceneid in e['scenes'].items():
        ck(route in ('arland','sofia') and (not e['route'] or e['route']==route),('route lock',e['id']))
        sc=s['scenes'].get(sceneid)
        ck(sc is not None and sc['route']==route,('scene missing',sceneid))
        ck(len(sc['lines'])>=6,('scene authored',sceneid))
        ck(all(line['s'] in s['speakers'] for line in sc['lines']),('speaker',sceneid))
    unlocked='WORLD_EVENT_'+e['id'].upper()+'_ONCE'
    ck(sum(1 for x in b['entries'] if x['unlock']==unlocked)==1,('Memory Book',e['id']))
    markers=[x for x in q['side'] if x['id']=='WE27_'+e['id'].upper()]
    ck(len(markers)==1,('marker',e['id']))
    it=markers[0]
    ck(it['when']=={'worldEventReady':e['id']},('event gating',e['id']))
    ck(it['area']==e['area'] and it['x']==e['x'] and it['y']==e['y'],('map binding',e['id']))
    ck([x['do'] for x in it['actions']]==['sfx','if','worldEvent','sfx'],('completion actions',e['id']))
    ck(it['actions'][2]['id']==e['id'],('reward id',e['id']))
ck(sum(x['route']=='arland' for x in events)==1,'one Arland exclusive event')
ck(sum(x['route']=='sofia' for x in events)==1,'one Sofia exclusive event')
ck(len([k for k in s['scenes'] if k.startswith('WE27-')])==26,'count authored scenes')
for typ,ext,expected in [('music','ogg',40),('ambience','ogg',14),('sfx','wav',32)]:
    ck(len(list((A/'audio'/typ).glob('*.'+ext)))==expected,('all prior audio assets remain',typ))
ck(int(re.search(r'SCHEMA\s*=\s*(\d+)', (R/'core/src/main/java/com/arlandsofia/olu/logic/Progress.java').read_text()).group(1)) >= 6, 'schema >= 6')
ck((R/'tools/content/world_events_v27.py').exists(), 'generator definitions')
ck((R/'tools/content/naskah_world_v27.txt').exists(), 'editable dialogue')
print(f'WORLD EVENTS v2.7 OK: {num} pemeriksaan, 14 event, 26 scenes, 86 audio assets')
