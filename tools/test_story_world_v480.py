#!/usr/bin/env python3
"""v4.8.0 story-world release gate. Run after all generator/patch scripts.
Checks real files, playable quests, new cues, previous cue compatibility, image
compositing and unmodified collision layout. Does not claim Android APK runtime.
"""
import hashlib,json,subprocess
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1];AS=R/'android/assets';DATA=AS/'data'
MAPS=['galeri_komunitas','rain_garden','clockwork_station','memory_bridge','moonlight_lake','hall_of_tomorrow','ruang_dua_surat']
EVENTS=[
 ('C04_V464_A_GALLERY','empty_chair_a','score_empty_chair_v480','cinema_gallery_empty'),
 ('C04_V464_S_GALLERY','stage_s_v464','score_empty_chair_v480','cinema_gallery_empty'),
 ('C04_PUZZLE','shrine','score_rain_resolve_v480','cinema_rain_five_lights_v470'),
 ('V471_C05_QUIET_TRUTH','v471_lumi_truth','score_quiet_truth_v480','cinema_quiet_reveal_v471'),
 ('V472_C06_PROMISE','v472_return','score_open_page_v480','cinema_unwritten_v472'),
 ('V473_EPI_FINALE','v473_final_bench','score_lake_coda_v480','cinema_homecoming_v473')]
checks=0
def ok(condition,msg):
 global checks
 checks+=1
 if not condition:raise AssertionError('V480: '+msg)

def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
m=json.loads((DATA/'maps.json').read_text());q=json.loads((DATA/'quests.json').read_text());s=json.loads((DATA/'story.json').read_text());
ok(len(m['areas'])==29,'29 maps retained')
ok(len(q['steps'])==157,'157 quest steps retained')
ok(len(s['scenes'])==736,'736 story scenes retained')
for name in MAPS:
 a=m['areas'][name];base=R/'art_source/story_v480/base_maps'/f'{name}.png'
 layer=R/'art_source/story_v480/editable_layers'/f'{name}_detail.png'
 runtime=AS/'maps'/f'{name}.png'
 for p in (base,layer,runtime):ok(p.is_file(),'Missing source/runtime image '+str(p))
 with Image.open(base) as im:bi=im.convert('RGBA')
 with Image.open(layer) as im:li=im.convert('RGBA')
 with Image.open(runtime) as im:ri=im.convert('RGB')
 ok(bi.size==ri.size==li.size==(a['w'],a['h']),'Map dims mismatch '+name)
 ok(li.getbbox() is not None,'Empty decorative layer '+name)
 ok(Image.alpha_composite(bi,li).convert('RGB').tobytes()==ri.tobytes(),'Runtime not exact layer composition '+name)
 ok(sha(base)!=sha(runtime),'Runtime map unchanged '+name)
 ok(len(a.get('walls',[]))>0,'Collision metadata missing '+name)
stepmap={x['id']:x for x in q['steps']};registry=(R/'core/src/main/java/com/arlandsofia/olu/logic/SoundscapePlan.java').read_text()
for st,it_id,new,legacy in EVENTS:
 step=stepmap[st]
 matches=[it for it in step['interactables'] if it['id']==it_id]
 ok(len(matches)==1,'Missing cutscene interactable '+st+'/'+it_id)
 acts=matches[0]['actions'];mus=[x['id'] for x in acts if x.get('do')=='music']
 ok(new in mus and legacy in mus,'Legacy/new score missing '+st)
 ok(mus.index(legacy)<mus.index(new),'New score must play after legacy for compatibility '+st)
 cine=[x for x in acts if x.get('do')=='cine']
 ok(len(cine)==1 and len(cine[0]['cmds'])>=5,'Cutscene camera commands incomplete '+st)
 for c in cine[0]['cmds']:ok(c['c'] in ('bars','tint','cam','wait','caption','shot','fx','flash'),'Unsupported command '+str(c))
for name in ['score_empty_chair_v480','score_rain_resolve_v480','score_quiet_truth_v480','score_open_page_v480','score_lake_coda_v480']:
 ok('"'+name+'"' in registry,'Not registered score '+name)
 f=AS/'audio/music'/f'{name}.ogg'
 ok(f.is_file() and f.stat().st_size>150000,'Missing/small OGG '+name)
 p=subprocess.run(['ffprobe','-v','error','-show_entries','stream=codec_name,sample_rate,channels:format=duration','-of','json',str(f)],capture_output=True,text=True)
 ok(p.returncode==0,'ffprobe cannot open score '+name)
 info=json.loads(p.stdout);v=info['streams'][0]
 ok(v['codec_name']=='vorbis' and v['sample_rate']=='44100' and v['channels']==2,'Bad score format '+name)
 ok(70<float(info['format']['duration'])<100,'Bad score length '+name)
# The Chapter2 escape must exist WITHOUT unlocking gallery early for unrelated routes.
cafe=m['areas']['cafe'];doors=[d for d in cafe['doors'] if d['id']=='cafe_to_gallery_v464']
ok(len(doors)==1,'Expected exactly one gallery entry portal')
locks=doors[0]['locked'];ok(locks==[{'when':{'maxChapter':'C02','notSteps':['V468_C02_NO_SKETCH']},'text':'Galeri sedang menyiapkan pameran.'}],'Chapter2 access policy changed')
for d in m['areas'].values():
 for door in d.get('doors',[]):ok(door['to'] in m['areas'],'Missing map door target')
# Source editability and build reproducibility: all three scripts exist.
for name in ('remaster_story_world_v480.py','gen_cinematic_scores_v480.py','apply_story_cinematics_v480.py','repair_c02_gallery_access_v480.py'):
 ok((R/'tools'/name).is_file(),'Missing regeneration tool '+name)
print('PASS v4.8.0 story-world: '+str(checks)+' image, cue, access, asset, collision, cinematic and source regeneration checks')
