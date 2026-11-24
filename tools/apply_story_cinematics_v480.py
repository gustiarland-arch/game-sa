#!/usr/bin/env python3
"""Story-driven cinematic direction for five v4.8 emotional peaks.
Idempotent: writes explicit shots, waits and score IDs without adding duplicate actions.
Does not touch quest IDs, count flags, unlock conditions or save schema.
"""
from pathlib import Path
import json,re
R=Path(__file__).resolve().parents[1]
Q=R/'android/assets/data/quests.json'
SOUND=R/'core/src/main/java/com/arlandsofia/olu/logic/SoundscapePlan.java'

LEGACY_CUES={
 ('C04_V464_A_GALLERY','empty_chair_a'):['cinema_gallery_empty'],
 ('C04_V464_S_GALLERY','stage_s_v464'):['cinema_gallery_empty'],
 ('C04_PUZZLE','shrine'):['cinema_rain_five_lights_v470'],
 ('V471_C05_QUIET_TRUTH','v471_lumi_truth'):['cinema_quiet_reveal_v471'],
 ('V472_C06_PROMISE','v472_return'):['cinema_unwritten_v472'],
 ('V473_EPI_FINALE','v473_final_bench'):['cinema_homecoming_v473','cinema_letter_tomorrow'],
}

CUES={
 ('C04_V464_A_GALLERY','empty_chair_a'):('score_empty_chair_v480',[
 {'c':'bars','on':True,'t':.9},{'c':'tint','color':'29213c','a':.20,'t':1.3},
 {'c':'cam','x':294,'y':432,'zoom':1.37,'t':2.4},{'c':'wait','t':.8},
 {'c':'caption','text':'The Empty Seat','sub':'Satu kursi yang tetap kosong','t':3.8},
 {'c':'shot','focus':'player','zoom':1.17,'frame':'wide','t':2,'bars':False},
 {'c':'tint','a':0,'t':1.1},{'c':'bars','on':False,'t':.7}]),
 ('C04_V464_S_GALLERY','stage_s_v464'):('score_empty_chair_v480',[
 {'c':'bars','on':True,'t':.8},{'c':'cam','x':294,'y':432,'zoom':1.30,'t':2.2},
 {'c':'wait','t':1.0},{'c':'caption','text':'The Empty Seat','sub':'Tepuk tangan tidak mengisi kursi itu','t':3.7},
 {'c':'shot','focus':'player','zoom':1.30,'frame':'intimate','t':1.8,'bars':False},
 {'c':'bars','on':False,'t':.6}]),
 ('C04_PUZZLE','shrine'):('score_rain_resolve_v480',[
 {'c':'bars','on':True,'t':.5},{'c':'cam','x':960,'y':650,'zoom':1.03,'t':2.3},
 {'c':'fx','kind':'lanterns','x':960,'y':680,'t':2.7,'n':22},
 {'c':'caption','text':'Lima Cahaya','sub':'Yang tidak diucapkan layak didengarkan','t':3.8},
 {'c':'bars','on':False,'t':.5}]),
 ('V471_C05_QUIET_TRUTH','v471_lumi_truth'):('score_quiet_truth_v480',[
 {'c':'bars','on':True,'t':.7},{'c':'cam','x':990,'y':480,'zoom':1.10,'t':2.2},
 {'c':'tint','color':'1a294c','a':.3,'t':1.4},{'c':'wait','t':.6},
 {'c':'caption','text':'The Quiet','sub':'Dua suara. Satu kenangan yang utuh.','t':4.2},
 {'c':'fx','kind':'restore','x':1070,'y':595,'t':4.2,'n':28},
 {'c':'tint','a':0,'t':1.3},{'c':'shot','focus':'couple','frame':'intimate','t':1.7},
 {'c':'bars','on':False,'t':.7}]),
 ('V472_C06_PROMISE','v472_return'):('score_open_page_v480',[
 {'c':'bars','on':True,'t':.8},{'c':'cam','x':965,'y':590,'zoom':1.12,'t':2.3},
 {'c':'caption','text':'Our Tomorrow','sub':'Masa depan tidak harus sempurna','t':3.5},
 {'c':'fx','kind':'petals','x':980,'y':625,'t':3.2,'n':24},
 {'c':'shot','focus':'couple','zoom':1.10,'frame':'wide','t':2},
 {'c':'flash','color':'fff3db','t':.7},{'c':'bars','on':False,'t':.8}]),
 ('V473_EPI_FINALE','v473_final_bench'):('score_lake_coda_v480',[
 {'c':'bars','on':True,'t':1.1},{'c':'shot','focus':'couple','frame':'intimate','zoom':1.22,'t':2.1},
 {'c':'wait','t':.6},{'c':'shot','focus':'couple','frame':'wide','zoom':.93,'t':3.1},
 {'c':'fx','kind':'petals','on':'player','t':4.5,'n':35},
 {'c':'caption','text':'To Be Continued','sub':'Kita masih punya banyak hari','t':5.1},
 {'c':'bars','on':False,'t':1.2}])
}

def main():
 data=json.loads(Q.read_text(encoding='utf-8'))
 storyfile=R/'android/assets/data/story.json'
 story=json.loads(storyfile.read_text(encoding='utf-8'))
 story.setdefault('meta',{})['visualAudioPolishVersion']='4.8.0'
 storyfile.write_text(json.dumps(story,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 targets={(s,i):(a['id'], cmds) for (s,i),(a_id,cmds) in CUES.items() for a in [{'id':a_id}]}
 handled=set()
 for step in data['steps']:
  for it in step.get('interactables',[]):
   key=(step['id'],it['id'])
   if key not in CUES:continue
   score,cmds=CUES[key]
   actions=it['actions']
   # Keep all earlier score IDs and append the new emotional cue last. Historical
   # quest/cutscene playback and regression hooks still receive their original IDs.
   actions[:]=[a for a in actions if a.get('do')!='music']
   legacy=[{'do':'music','id':id} for id in LEGACY_CUES[key]]
   actions[:0]=legacy+[{'do':'music','id':score}]
   cine_indices=[j for j,a in enumerate(actions) if a.get('do')=='cine']
   if cine_indices:
    actions[cine_indices[0]]['cmds']=cmds
    for j in reversed(cine_indices[1:]):del actions[j]
   else:
    idx=next(j for j,a in enumerate(actions) if a.get('do')=='music')
    actions.insert(idx+1,{'do':'cine','cmds':cmds})
   handled.add(key)
 if handled!=set(CUES):raise AssertionError('Missing cinematic anchor(s): '+str(set(CUES)-handled))
 Q.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 text=SOUND.read_text(encoding='utf-8')
 anchor='"cinema_prologue_memory_v474"'
 ids=list(dict.fromkeys([v[0] for v in CUES.values()]))
 if not all(('"'+i+'"') in text for i in ids):
  assert anchor in text,'Sound registry changed'
  text=text.replace(anchor,anchor+', '+', '.join('"'+i+'"' for i in ids),1)
  SOUND.write_text(text,encoding='utf-8')
 print('PASS: 6 story cutscenes + 5 original soundtracks mapped to native engine and registry')

if __name__=='__main__':main()
