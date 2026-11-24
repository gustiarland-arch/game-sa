#!/usr/bin/env python3
"""One-shot idempotent v4.9 data integration. Does not regenerate source v4.8 assets."""
from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
assets = root/'android/assets/data'
qp = assets/'quests.json'; sp = assets/'story.json'; bp = assets/'memory_book.json'
q=json.loads(qp.read_text('utf-8')); st=json.loads(sp.read_text('utf-8')); book=json.loads(bp.read_text('utf-8'))

# All original scenes, routes, and canon events remain untouched.
for eid, event in list(st['scenes'].items()):
    if eid.startswith('V49-WE-'):
        lines = event.get('lines', [])
        if len(lines)<6:
            # additional exchange so each world event has the same narrative depth
            route=event['route']; other='sofia' if route=='arland' else 'arland'
            lines.insert(-1, {'s':other,'e':'penasaran','t':'Kalau besok lewat sini lagi, apa kita akan menemukan sesuatu yang berbeda?'})
            lines.insert(-1, {'s':route,'e':'senyum','t':'Boleh dicoba. Yang penting kita tidak melewatkan hari ini.'})
            if len(lines)<6:
                lines.insert(-1, {'s':'narrator','e':'neutral','t':'Angin bergerak pelan, membawa suara kota yang akrab.'})

existing={e['id'] for e in book['entries']}
icon='items/symbol_star.png'
for d in q['worldDiscoveries']:
    id='v49_discovery_'+d['area']
    if id not in existing:
        book['entries'].append({'id':id,'chapter':d['minChapter'],'route':'shared',
            'type':'world_discovery','unlock':d['flag'],'icon':icon,
            'title':d['title'],'text':'Penemuan di '+d['area'].replace('_',' ')+'. '+d['hint']})
        existing.add(id)
for e in q['worldEvents']:
    if not e['id'].startswith('v49_'):continue
    id='v49_event_'+e['id']
    if id not in existing:
        book['entries'].append({'id':id,'chapter':e['minChapter'],'route':'shared',
            'type':'world_event','unlock':'WORLD_EVENT_'+e['id'].upper()+'_ONCE',
            'icon':icon,'title':e['title'],
            'text':'Momen harian di '+e['area'].replace('_',' ')+'. Kenangan pertama tetap tersimpan.'})
        existing.add(id)
if 'v49_atlas_bonus' not in existing:
    book['entries'].append({'id':'v49_atlas_bonus','chapter':'EPI','route':'shared',
      'type':'optional_bonus','unlock':'V49_WORLD_ATLAS_UNLOCK','icon':icon,
      'title':'Atlas Kenangan Kecil',
      'text':'Semua jejak dunia ditemukan. Dua sudut pandang mengungkapkan satu kisah, tanpa akhir baru.'})

q['_v49']='29 unique discoveries / 18 timed events / 14 route-dependent Memory Echo configurations.'
for filename,obj in ((qp,q),(sp,st),(bp,book)):
    filename.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('v4.9 additions integrated:',len(q['worldDiscoveries']),'secrets,',len([x for x in q['worldEvents'] if x['id'].startswith('v49_')]),
      'new daily events,',len(book['entries']),'memory entries,',len(st['scenes']),'scenes')
