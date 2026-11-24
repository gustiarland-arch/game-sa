#!/usr/bin/env python3
"""Idempotent post-generation camera shot polish for five existing canonical scenes.
Does not add dialogue, reorder story actions, modify flags, or alter ending branches.
After tools/build_content.py regenerates quests.json, run this script again.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'android/assets/data/quests.json'
SCENES={
    'C01_PIER':.93,       # wider dock view
    'C04_V26_VOW':1.17,  # intimate vows
    'C05_V26_NIGHT_TALK':1.21,
    'C06_Q_REVEAL':1.13,
    'EPI_FEST_LEPAS':1.16,
}
# Some shipped builds have minor name differences; use the selected IDs only.
def modify():
    data=json.loads(PATH.read_text(encoding='utf-8'))
    changed=[]
    for step in data['steps']:
        if step['id'] not in SCENES: continue
        def visit(node):
            if isinstance(node,dict):
                if node.get('c') in ('cam','shot') and node.get('on',node.get('focus'))=='player':
                    # Only the final player-following shot in each scene gets the intimate framing.
                    matches.append(node)
                for value in node.values():visit(value)
            elif isinstance(node,list):
                for value in node:visit(value)
        matches=[]
        visit(step)
        if not matches: continue
        target=matches[-1]
        desired=SCENES[step['id']]
        if target.get('c')=='shot' and target.get('zoom')==desired: continue
        target.pop('on',None)
        target['c']='shot'
        target['focus']='player'
        target['frame']='wide' if step['id']=='C01_PIER' else 'intimate'
        target['zoom']=desired
        target['bars']=False # existing bars commands remain authoritative
        changed.append(step['id'])
    if changed:
        PATH.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return changed

if __name__=='__main__':
    result=modify()
    print('V4.6.3 shot conversion: '+(', '.join(result) if result else 'already applied / no matching scenes'))
