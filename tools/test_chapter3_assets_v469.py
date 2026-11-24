#!/usr/bin/env python3
"""Static cross-reference checks for C03 narrative, assets and audio. Draft QA."""
import json,wave,subprocess
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'android/assets/data';AS=ROOT/'android/assets'
s=json.loads((D/'story.json').read_text('utf-8'))
q=json.loads((D/'quests.json').read_text('utf-8'))
b=json.loads((D/'memory_book.json').read_text('utf-8'))
step={x['id']:x for x in q['steps']};n=0

def ok(v,msg):
 global n
 n+=1
 if not v:raise AssertionError('C03 static #'+str(n)+' '+msg)
ok('chapter3Overhaul' in s['meta'],'C03 version mark exists')
ok(len({x['id'] for x in q['steps']})==len(q['steps']),'all quest IDs unique')
for id in ['C03_A_IDEA','C03_S_CORNER','C03_FREE','V469_C03_A_FRAME','V469_C03_S_SCRAP','V469_C03_NEIGHBOR',
 'V469_C03_HALF_LETTER','C03_A_INGREDIENTS','C03_S_DECOR','C03_S_ARRANGE','C03_COOK','C03_V26_DETAILS','C03_PICNIC',
 'C03_V464_GALLERY_PREP','C04_A_WAKE','C04_S_WAKE']:
 ok(id in step,'chapter flow step exists '+id)
for id,sc in s['scenes'].items():
 if sc.get('chapter')!='C03':continue
 ok(bool(sc.get('lines')),'scene contains dialogue '+id)
 ok(sc.get('route') in ('arland','sofia','shared'),'route valid '+id)
 for ln in sc['lines']:
  ok(ln['s'] in s['speakers'],'registered speaker in '+id+':'+ln['s'])
  ok(ln.get('e','neutral') in s['emotions'],'registered emotional expression '+id)
  ok(bool(ln['t'].strip()),'meaningful dialogue not empty '+id)
 for ch in sc.get('choices',[]):
  ok(bool(ch['text'].strip()),'choice text '+id)
  if id.startswith('V469-') or id in ('C03-S02','V464-C03-PROMISE'):
   ok(len(ch.get('flags',[]))==1,'new/story choice exclusive flag '+id)
  for rt in ('arland','sofia'):
   ok(len(ch.get('byRoute',{}).get(rt,[]))>0,'choice response exists '+id+rt)
   if not ch.get('byRoute',{}).get(rt): continue
   for ln in ch['byRoute'][rt]:ok(ln['s'] in s['speakers'],'choice speaker valid '+id)
allowed={'scene','step','flag','unflag','if','item','removeItem','count','setCount','minigame','puzzle',
         'warp','music','sfx','cine','chapterEnd','companion','chapterCard','toast','emote','credits'}
def refs(actions,where):
 for a in actions:
  typ=a.get('do');ok(typ in allowed,'known action '+str(typ)+' '+where)
  if typ=='if':refs(a.get('then',[]),where+' YES');refs(a.get('else',[]),where+' NO')
  elif typ=='scene':ok(a['id'] in s['scenes'] or '$ROUTE' in a['id'],'resolved scene '+a['id'])
  elif typ=='step':ok(a['id'] in step,'resolved step '+a['id'])
  elif typ=='minigame':ok(a['id'] in q['minigames'],'registered native minigame '+a['id'])
  elif typ=='music':ok((AS/'audio/music'/(a['id']+'.ogg')).exists(),'music file '+a['id'])
  elif typ=='sfx':ok((AS/'audio/sfx'/(a['id']+'.wav')).exists(),'SFX file '+a['id'])
  elif typ=='cine':
   ok(bool(a.get('cmds')),'nonempty cutscene '+where)
   for c in a['cmds']:ok(c.get('c') in ('bars','shot','wait','fx','cam','face','say','fade','tint','move','emote','pose','flash','caption'),
                  'cine directive '+str(c.get('c')))
for sid,st in step.items():
 if st.get('chapter')!='C03':continue
 for it in st.get('interactables',[]):refs(it['actions'],sid+'/'+it['id'])
 for k in ('complete','enterArea'):
  if k in st:refs(st[k]['actions'],sid+'/'+k)
for sid in ('C03_A_INGREDIENTS','C03_S_DECOR'):
 for it in step[sid]['interactables']:
  ok(any(a.get('do')=='flag' and a.get('id')==it['hideIfFlag'] for a in it['actions']),
      'single-collection guard '+it['id'])
for sid in ('V469_C03_A_FRAME','V469_C03_S_SCRAP'):
 it=step[sid]['interactables'][0]
 ok(any(a['do']=='minigame' for a in it['actions']),'playable memory minigame '+sid)
 ok(it['actions'][-1]['do']=='step','retriable quest continuation '+sid)
ok(step['C03_V464_GALLERY_PREP']['complete']['count']==3,'three unique gallery jobs mandatory')
ok(len(step['C03_V464_GALLERY_PREP']['interactables'])==3,'gallery interactions all separate')
for m in [x for x in b['entries'] if x['id'].startswith('v469_c03_')]:
 ok(m['chapter']=='C03','memory chapter '+m['id'])
 ok(m['route'] in ('shared','arland','sofia'),'memory route '+m['id'])
 ok((AS/m['icon']).is_file(),'Memory Book art '+m['id'])
 ok(bool(m['unlock']) and bool(m['text'].strip()),'memory unlock and unique meaning '+m['id'])
for name in ('frame','scrapbook','letter','invitation'):
 path=AS/'items'/('v469_c03_'+name+'.png')
 ok(path.is_file(),'pixel art file '+name)
 with Image.open(path) as im:
  ok(im.mode=='RGBA' and im.size==(192,192),'editable transparent 192px icon '+name)
  im.verify()
for iid in ('v469_frame','v469_scrapbook','v469_half_letter','v469_gallery_invitation','v469_neighbor_note'):
 ok(iid in b['items'],'catalogue collectible '+iid)
 ok((AS/b['items'][iid]['icon']).is_file(),'collectible asset '+iid)
j=(ROOT/'core/src/main/java/com/arlandsofia/olu/logic/SoundscapePlan.java').read_text('utf-8')
for id in ('cinema_small_things_v469','cinema_gallery_promise_v469'):
 ok(('"'+id+'"') in j,'audio registered '+id)
 file=AS/'audio/music'/(id+'.ogg');ok(file.is_file() and file.stat().st_size>3000,'original OGG file '+id)
 p=subprocess.run(['ffprobe','-v','error','-show_entries','stream=codec_name,sample_rate','-of','json',str(file)],capture_output=True,text=True,check=True)
 meta=json.loads(p.stdout);ok(meta['streams'][0]['codec_name']=='vorbis','OGG Vorbis decodable '+id)
ok('"v469_pencil"' in j,'soft pencil sound registered')
with wave.open(str(AS/'audio/sfx/v469_pencil.wav')) as w:
 ok(w.getnchannels()==1 and w.getframerate()==22050 and w.getnframes()>0,'valid PCM mono SFX')
print('PASS: '+str(n)+' C03 story/audio/memory/action cross-reference and asset assertions')
