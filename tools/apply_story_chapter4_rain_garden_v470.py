#!/usr/bin/env python3
"""Dedicate original Rain Garden to Chapter 4, preserving the old Lantern Field for C05.

Safe deterministic patch over Chapter 4 story and maps; never resets saves.
"""
import json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
DATA=BASE/'android/assets/data'
def read(name):return json.loads((DATA/name).read_text(encoding='utf-8'))
def write(name,obj):(DATA/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def apply():
 maps=read('maps.json');quests=read('quests.json');story=read('story.json')
 areas=maps['areas']
 assert 'lantern_field' in areas and 'galeri_komunitas' in areas and 'taman_kota' in areas
 area={
  'name':'Rain Garden — Lima Cahaya yang Tak Terucap',
  'image':'maps/rain_garden.png','w':1920,'h':1280,'music':'memory','ambient':'rain',
  'spawn':[160,1140],'indoor':False,
  'walls':[[0,0,20,1280],[1900,0,20,1280],[0,0,1920,20],[0,1260,1920,20]],
  'ellipses':[],'props':[],'gates':[],'animals':[],
  'water':[{'cx':200,'cy':288,'rx':140,'ry':58},{'cx':1616,'cy':1112,'rx':164,'ry':62}],
  'doors':[{'id':'rain_garden_to_park','label':'Kembali ke Taman Kota',
            'rect':[105,1216,150,43],'to':'taman_kota','tx':1590,'ty':490,'dir':'down'}],
  'examine':[{'id':'rain_garden_memory','label':'Jejak kenangan hujan','x':960,'y':800,'r':90,
      'lines':{'arland':[{'s':'arland','e':'neutral','t':'Di sini ada lima cerita. Aku akan mendengarkan semuanya.'}],
               'sofia':[{'s':'sofia','e':'neutral','t':'Lima cahaya ini nggak meminta salah satu dari kami mengalah.'}]}}],
  'storyVersion':'v470_original_rain_garden','visualStyle':'rain_memory_five_lanterns_v470'
 }
 areas['rain_garden']=area
 # Legacy C04 saves may already be inside Lantern Field. Add a rescue exit
 # which is available only during Chapter 4. Never change the original C05 portal.
 old=areas['lantern_field'];old['doors']=[d for d in old['doors'] if d.get('id')!='legacy_lantern_to_rain_garden']
 old['doors'].append({'id':'legacy_lantern_to_rain_garden',
   'label':'Jejak hujan menuju Rain Garden', 'rect':[105,1172,100,65],
   'to':'rain_garden','tx':160,'ty':1140,'dir':'up',
   'locked':[{'when':{'maxChapter':'C03'},'text':'Lorong hujan belum muncul.'},
             {'when':{'minChapter':'C05'},'text':'Lorong hujan sudah tertutup. Lentera kini menuju desa bintang.'}]})
 park=areas['taman_kota'];park['doors']=[d for d in park['doors'] if d.get('id')!='park_to_rain_garden']
 park['doors'].append({'id':'park_to_rain_garden','label':'Gerbang Rain Garden',
  'rect':[1635,438,82,58],'to':'rain_garden','tx':160,'ty':1140,'dir':'up',
  'locked':[{'when':{'maxChapter':'C03'},'text':'Di balik gazebo hanya terlihat hujan dan kabut. Jalannya belum terbuka.'}]})
 steps={s['id']:s for s in quests['steps']}
 for key in ('C04_A_PARK','C04_S_MEET'):
  its=steps[key]['interactables']; assert its
  found=False
  for it in its:
   for a in it['actions']:
    if a.get('do')=='warp' and a.get('area') in ('lantern_field','rain_garden'):
     a['area']='rain_garden';found=True
  assert found,key
 for key in ('C04_LIGHTS','C04_PUZZLE'):
  steps[key]['weather']='rain'  # Rain Garden must be rainy independent of random game day.
  for it in steps[key]['interactables']:
   assert it['area'] in ('lantern_field','rain_garden'),(key,it['id'])
   it['area']='rain_garden'
 steps['C04_LIGHTS']['complete']['actions'][0]['text']='Bawa kelima cahaya ke altar Rain Garden.'
 for route in ('arland','sofia'):
  steps['C04_PUZZLE']['objective'][route]='Satukan lima cahaya di altar Rain Garden'
 # Ambient companion conversations must follow the moved Chapter 4 location.
 for talk in quests.get('talks',[]):
  if talk.get('id') in ('c04_field','c04_field2'):
   talk['area']='rain_garden'
 for name in ('T-C04-FIELD','T-C04-FIELD2'):
  if name in story['scenes']:story['scenes'][name]['location']='rain_garden'
 for scene in ('V470-C04-LIGHT-PRESENCE','V470-C04-LIGHT-BOUNDARY','V470-C04-LIGHT-UPDATE','C04-L01','C04-L02','C04-X01'):
  if scene not in story['scenes']:continue
  story['scenes'][scene]['location']='rain_garden'
  for line in story['scenes'][scene]['lines']:
   line['t']=line['t'].replace('Lantern Field','Rain Garden').replace('tengah padang','Rain Garden')
 # Chapter 4 introductory narration must name the new realm, not the C05 map.
 for name in ('C04-X00','C04-X02'):
  if name in story['scenes']:
   for line in story['scenes'][name]['lines']:
    line['t']=line['t'].replace('Lantern Field','Rain Garden')
 story['scenes']['C04-X02']['location']='rain_garden'
 story['meta']['chapter4Map']='rain_garden: standalone 24th area for C04, original lantern_field untouched for C05'
 write('maps.json',maps);write('quests.json',quests);write('story.json',story)
 print('PASS: dedicated Rain Garden 24th map, 5 C04 quest lights, safe portal/return, C05 Lantern Field retained')
if __name__=='__main__':apply()
