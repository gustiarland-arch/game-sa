#!/usr/bin/env python3
"""Fix real softlock on Sofia Chapter 2 refusal branch.
Only the dedicated independent-sketch step may enter the gallery during C02.
Other early chapters remain locked; C03+ normal entrance unchanged.
"""
import json
from pathlib import Path
D=Path(__file__).resolve().parents[1]/'android/assets/data/maps.json'
m=json.loads(D.read_text(encoding='utf-8'))
cafe=m['areas']['cafe'];doors=[x for x in cafe['doors'] if x['id']=='cafe_to_gallery_v464'];assert len(doors)==1
l=doors[0]['locked'];assert len(l)==1 and 'when' in l[0]
l[0]['when']={'maxChapter':'C02','notSteps':['V468_C02_NO_SKETCH']}
D.write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('PASS: gallery unlocked only during C02 independent Sofia sketch; all other story gates retained')
