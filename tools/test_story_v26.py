#!/usr/bin/env python3
"""Regresi data v2.6: dua POV, alur baru, minigame, album, audio; tidak membuktikan Android runtime."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'android'/'assets'
q=json.loads((A/'data/quests.json').read_text(encoding='utf-8'))
s=json.loads((A/'data/story.json').read_text(encoding='utf-8'))
b=json.loads((A/'data/memory_book.json').read_text(encoding='utf-8'))
count=0
def verify(x, message):
    global count
    count+=1
    if not x: raise AssertionError(message)

verify(len(s['scenes'])>=372, 'seluruh 372 scene v2.6 dipertahankan')
verify(len(q['steps'])>=93 and {'C04_V465_SECOND_TALK','C05_V465_PROOF'} <= {x['id'] for x in q['steps']}, '93 quest baseline dan tambahan story baru')
verify(len(q['sideQuests'])==25, 'total 25 sidequest (22 akses per route)')
verify(len(b['entries'])>=115, '115 entri Memory Book v2.6 dipertahankan')
verify(len(q['minigames'])>=20, 'minigame lama + v2.6')
new_ids={k:v for k,v in s['scenes'].items() if k.startswith('V26-')}
verify(len(new_ids)==41, '41 scene tambahan setelah split dua route')
for sid, scene in new_ids.items():
    verify(scene['chapter'] in ('C02','C03','C04','C05'), ('chapter',sid))
    verify(scene['route'] in ('arland','sofia','shared'),('route',sid))
    verify(len(scene['lines'])>=3, ('naskah terlalu pendek',sid))
    for line in scene['lines']:
        verify(line['s'] in s['speakers'],('pembicara',sid,line['s']))
    for option in scene.get('choices',[]):
        verify(bool(option.get('flags')), ('choice tanpa flag',sid))
steps={st['id']:st for st in q['steps']}
for st in ['C03_V26_DETAILS','C04_V26_RECONCILE','C04_V26_VOW',
           'C05_V26_A_SURVEY','C05_V26_A_KEY','C05_V26_S_NOTES','C05_V26_S_COMPOSE',
           'C05_V26_NIGHT_TALK','C05_V26_STARGAZE']:
    verify(st in steps and steps[st].get('interactables'),('story step kosong',st))
for route in ('A','S'):
    st=steps['C05_V26_'+route+('_SURVEY' if route=='A' else '_NOTES')]
    verify(st['counterMax']==3,('petunjuk C05',route))
    verify(len(st['interactables'])==3,('3 interaksi',route))
    for a in st['interactables']:
        verify(a['route']==('arland' if route=='A' else 'sofia'),('route hanya diri sendiri',route,a['id']))
for id_,kind in [('v26_night_compass','code'),('v26_night_pages','pages')]:
    verify(q['minigames'][id_]['type']==kind, ('minigame baru',id_))
    verify(('case "'+id_+'"') in (ROOT/'core/src/main/java/com/arlandsofia/olu/game/minigame/Games.java').read_text(),('factory runtime',id_))
side={k['id']:k for k in q['sideQuests']}
for id_,route in [('SQ_V26_MAP_A','arland'),('SQ_V26_CARDS_S','sofia'),('SQ_V26_LISTEN',None),('SQ_V26_LAMPS',None)]:
    verify(id_ in side,('quest',id_))
    verify(side[id_].get('route')==route,('route',id_))
    prefix={'SQ_V26_MAP_A':'v26_sqa_', 'SQ_V26_CARDS_S':'v26_sqs_', 'SQ_V26_LISTEN':'v26_sql_', 'SQ_V26_LAMPS':'v26_sqf_'}[id_]
    verify(sum(1 for it in q['side'] if it['id'].startswith(prefix))==5,('quest harus punya 5 lokasi interaksi',id_))
unlocks={m['unlock'] for m in b['entries']}
for flag in ['V26_C03_FINISHED','V26_AFTER_RAIN','V26_C05_A_SOLVED','V26_C05_S_SOLVED',
             'V26_C05_TOGETHER','SQ_V26_MAP_A_DONE','SQ_V26_CARDS_S_DONE',
             'SQ_V26_LISTEN_DONE','SQ_V26_LAMPS_DONE']:
    verify(flag in unlocks,('album tidak bisa dibuka',flag))
for category,suffix,n in [('music','*.ogg',40),('ambience','*.ogg',14),('sfx','*.wav',32)]:
    verify(len(list((A/'audio'/category).glob(suffix)))>=(n+2 if category=='music' else n),('audio hilang',category))
for path in ['audio/music/star_road.ogg','audio/music/cinema_reconciliation.ogg',
             'audio/sfx/quest_complete.wav','audio/sfx/paper_fold.wav']:
    verify((A/path).is_file(),('cuenya harus ada',path))
verify('schema' not in q or q['schema'] in (None,5),'tidak mengubah schema quest')
print(f'STORY EXPANSION v2.6 OK: {count} pemeriksaan; 41 adegan v2.6 terpelihara, quest/scene v4.6.5 ditambahkan, 4 side quest v2.6, 2 minigame route')
