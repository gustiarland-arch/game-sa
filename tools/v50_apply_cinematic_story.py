#!/usr/bin/env python3
"""Idempotent playable v5.0 story/world patch on shipped v4.9 JSON.
Preserves original quest/canon nodes, does not regenerate old story or old map art.
"""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
Q=R/'android/assets/data/quests.json';S=R/'android/assets/data/story.json'
SPEC=R/'tools/v50_terraces.json'
VIEW={
'plaza':('Anak Tangga di Plaza','Dari sini ternyata bundaran di plaza terlihat seperti halaman terbuka.','Aku suka melihat orang datang dan pergi dari sisi yang lebih tenang.','Kita memang bertemu di bawah, tetapi pemandangannya berbeda dari atas.','C02'),
'taman_kota':('Teras di Atas Kolam','Dari atas, jalur setapak ini tampak seperti gambar yang belum selesai.','Riak kolamnya berubah ketika kita tidak melihat dari tepi.','Taman yang sama bisa terasa seperti tempat baru.','C02'),
'riverside':('Dek Riak Senja','Aku kira danau cuma membentang lurus, ternyata tikungannya jauh juga.','Aku ingin duduk sebentar dan menghitung lampu di seberang.','Tempat yang tinggi tidak selalu harus lebih jauh dari rumah.','C03'),
'dermaga':('Tangga Kayu ke Senja','Dari anak tangga ini aku bisa melihat ujung dermaga.','Airnya mengulang warna langit seperti halaman kedua.','Kalau turun lagi, jangan sampai terburu-buru.','C03'),
'cafe':('Panggung Kecil Senja','Ternyata kafe ini punya sudut tinggi yang tidak pernah kuperhatikan.','Tempat duduk di sini seperti panggung untuk cerita sederhana.','Aku suka suaramu terdengar jelas di sini.','C02'),
'star_path':('Pijakan Menuju Bintang','Dari tingkat ini pola jalurnya baru kelihatan utuh.','Aku melihat simbol kecil yang tadi tertutup bayangan.','Dua sisi jalan itu ternyata saling melengkapi.','C05'),
'bukit_bintang':('Observatorium Kecil','Coba lihat garis cahaya di balik bukit itu.','Aku lebih mudah menemukan rasi bintang dari sini.','Tidak setiap bintang harus paling terang agar terlihat.','C03'),
'memory_garden':('Teras Ingatan','Ada jejak langkah yang hanya terlihat dari sini.','Taman ini menyimpan lebih dari satu cara mengingat.','Kenangan kecil tidak perlu bersaing dengan kenangan besar.','C03'),
'lantern_field':('Teras Lentera','Nyala lentera ini membentuk rute yang berbeda dari bawah.','Urutan warnanya lebih mudah dibaca di tempat tinggi.','Kadang kita harus pindah sudut untuk menemukan petunjuk.','C05'),
'starfall_village':('Atap Cahaya Starfall','Lihat, jalan desa ini seperti susunan kartu pos.','Ada lentera kecil di balik rumah yang tadi tidak kelihatan.','Malam di desa ini lebih hangat daripada yang kuduga.','C05'),
'eternal_garden':('Pelataran Hari Esok','Dari sini halaman kosong itu seperti undangan untuk terus melangkah.','Aku tidak ingin menuliskan sesuatu hanya agar terlihat selesai.','Aku lebih suka menulisnya sedikit demi sedikit bersama.','C06'),
'rain_garden':('Pijakan dalam Hujan','Air menuruni setiap anak tangga seperti menghitung jeda.','Suara hujan di tempat tinggi terdengar berbeda.','Aku ingin mendengar kalimatmu sampai selesai.','C04'),
'hutan_bisik':('Teras Akar Tua','Akar pohon ini menahan tanah seperti sebuah janji.','Bunyi dedaunan terdengar lebih pelan dari atas.','Bukan hutan yang berubah; cara kita mendengarnya.','C05'),
'gua_kristal':('Tangga Kristal','Ada warna yang tidak terlihat dari mulut gua.','Cahaya di sudut ini membuat kristal seperti bernapas.','Tidak perlu mengambilnya agar kita bisa mengingatnya.','C05'),
'hall_of_tomorrow':('Balkon Tiga Hari','Tiga jendela, tetapi tidak ada yang memaksaku memilih satu akhir.','Aku ingin masa depan tetap punya ruang untuk berubah.','Yang kita pilih sekarang adalah saling mendengarkan.','C06'),
'perumahan':('Teras Halaman Tetangga','Aku bisa melihat lampu rumah satu demi satu.','Setiap jendela menyimpan cerita yang berbeda.','Pulang tidak selalu berarti berhenti berjalan.','C03'),
'jalan_kota':('Teras di Jalan Kota','Tadi di bawah jalan ini terasa ramai sekali.','Dari sini, langkah orang-orang seperti irama pelan.','Kita bisa turun dan ikut berjalan kapan saja.','C02'),
'toko_bunga':('Panggung Bunga','Dari sini terlihat siapa yang rajin merawat setiap pot.','Rangkaian bunga yang kecil pun punya tempat sendiri.','Aku suka kalau kamu memilihnya tanpa terburu-buru.','C02'),
'perpustakaan':('Mezanin Buku','Dari atas, rak-raknya seperti labirin kecil.','Ada judul buku yang lebih mudah kubaca dari sini.','Kalau bingung, kita bisa menuruni tangga pelan-pelan.','C03'),
'arcade':('Dek Lampu Arcade','Mesinnya terlihat seperti bintang-bintang kecil dari atas.','Kita bisa menghitung lampu yang menyala bersama.','Permainan tidak harus selalu soal skor.','C03'),
'galeri_komunitas':('Mezanin Galeri','Lukisan yang sama punya warna lain dari sisi ini.','Kursi kosong di bawah terlihat lebih kecil, tapi perasaanku tetap sama.','Aku ingin tinggal sebentar untuk memahaminya.','C04')
}
TRACK={'city':'v50_plaza_ascent','garden':'v50_plaza_ascent','wood':'v50_cafe_highlight',
       'cafe':'v50_cafe_highlight','forest':'v50_rain_reflections',
       'night':'v50_starlit_steps','star':'v50_starlit_steps','memory':'v50_starlit_steps',
       'future':'v50_tomorrow_horizon','crystal':'v50_starlit_steps'}

# Existing main-story anchors gain cinematic visual depth without deleting old directions.
MAIN_ANCHORS=[
 ('PRO_GO_PLAZA',None, 'enterArea','fireflies','v50_plaza_ascent'),
 ('C01_SUNSET','pierend','interactables','mist','v50_plaza_ascent'),
 ('V468_C02_REUNION','v468_reunion','interactables','fireflies','v50_cafe_highlight'),
 ('C03_V464_GALLERY_PREP','gallery_seat','interactables','mist','v50_cafe_highlight'),
 ('C04_V464_A_GALLERY','empty_chair_a','interactables','mist','v50_rain_reflections'),
 ('C04_V464_S_GALLERY','stage_s_v464','interactables','mist','v50_rain_reflections'),
 ('C04_PUZZLE','shrine','interactables','rainlight','v50_rain_reflections'),
 ('V471_C05_MOON_SHARED','v471_moon_listen','interactables','aurora','v50_starlit_steps'),
 ('V471_C05_QUIET_TRUTH','v471_lumi_truth','interactables','aurora','v50_starlit_steps'),
 ('V472_C06_PROMISE','v472_return','interactables','aurora','v50_tomorrow_horizon'),
 ('V473_EPI_FINALE','v473_final_bench','interactables','fireflies','v50_tomorrow_horizon'),
]

def main():
 q=json.loads(Q.read_text(encoding='utf-8'))
 s=json.loads(S.read_text(encoding='utf-8'))
 specs=json.loads(SPEC.read_text(encoding='utf-8'))
 if len(specs)!=len(VIEW):raise AssertionError('Terraces need narration for both POV')
 for area,spec in specs.items():
    title,ar,so,partner,chapter=VIEW[area]
    x=spec['x']+spec['w']*.5
    y=spec['y']+spec['h']*.45
    flag='V50_VIEW_'+area.upper()+'_DONE'
    sid='V50-VIEW-'+area.upper()
    for route in ('arland','sofia'):
       other='sofia' if route=='arland' else 'arland'
       s['scenes'][sid+'-'+route.upper()]={
           'title':title,'route':route,'chapter':chapter,'location':area,
           'trigger':'Panorama opsional: naik tangga menuju pelataran (v5.0)',
           'lines':[
             {'s':'narrator','e':'neutral','t':'Kalian menaiki tangga satu per satu. Tempat yang baru terlihat terbentang di sisi lain railing.'},
             {'s':route,'e':'penasaran','t':ar if route=='arland' else so},
             {'s':other,'e':'senyum','t':partner},
             {'s':'narrator','e':'neutral','t':'Angin lewat pelan. Kalian memilih menikmati pemandangan sebelum turun lagi.'},
             {'s':route,'e':'senyum','t':'Aku tidak menyangka tempat yang sama akan terasa sejauh ini berbeda.'},
             {'s':other,'e':'senyum','t':'Yang penting kita masih bisa pulang lewat jalan yang sama.'},
             {'s':'narrator','e':'neutral','t':'Satu panorama baru tersimpan. Jalan cerita utama tidak berubah.'}
           ],'flags':[]}
    style=spec['style']
    fx='aurora' if style in ('star','memory','night','future','crystal') else 'fireflies' if style in ('garden','forest') else 'mist'
    cmds=[
      {'c':'bars','on':True,'t':.65},
      {'c':'shot','focus':'player','zoom':1.26,'frame':'intimate','t':.75,'bars':True},
      {'c':'fx','kind':fx,'on':'player','t':4.8,'n':28},
      {'c':'sfx','id':'v50_view_wind'},
      {'c':'caption','text':title,'sub':'Panorama baru • '+area.replace('_',' ').title(),'t':2.5},
      {'c':'shot','focus':'couple','zoom':.86,'frame':'wide','t':1.4,'bars':False},
      {'c':'sfx','id':'v50_panoramic_reveal'},
      {'c':'bars','on':False,'t':.6}
    ]
    q['side']=[it for it in q['side'] if it.get('id')!='V50_VIEW_'+area.upper()]
    q['side'].append({
      'id':'V50_VIEW_'+area.upper(),'area':area,'x':round(x), 'y':round(y), 'r':49,
      'label':'✦ Panorama: '+title,'hideIfFlag':flag,'marker':True,
      'when':{'minChapter':chapter,'notFlags':[flag]},
      'actions':[
        {'do':'music','id':TRACK[style]},
        {'do':'cine','cmds':cmds},
        {'do':'if','when':{'route':'arland'},
          'then':[{'do':'scene','id':sid+'-ARLAND'}],
          'else':[{'do':'scene','id':sid+'-SOFIA'}]},
        {'do':'flag','id':flag},
        {'do':'count','id':'v50_panoramas','add':1},
        {'do':'sfx','id':'v50_memory_shimmer'},
        {'do':'toast','text':'Panorama: '+title+' tersimpan.'},
      ]
    })
 for step_id,item_id,kind,fx,score in MAIN_ANCHORS:
    step=next((x for x in q['steps'] if x['id']==step_id),None)
    if step is None:raise AssertionError('Story anchor missing '+step_id)
    if kind=='enterArea':actions=step.get('enterArea',{}).get('actions',[])
    else:
       it=next((x for x in step.get('interactables',[]) if x['id']==item_id),None)
       if it is None:raise AssertionError(f'Missing {step_id}:{item_id}')
       actions=it['actions']
    if any(x.get('v50Cinematic') for x in actions):continue
    # Existing authored cameras and quests stay untouched. Append one new art-directed FX
    # to the first native cine block or insert a small prelude before the first scene.
    cine=next((x for x in actions if x.get('do')=='cine'),None)
    addition=[{'c':'fx','kind':fx,'on':'player','t':4.6,'n':32},
              {'c':'sfx','id':'v50_memory_shimmer'}]
    if cine is not None:
       cine['cmds'][:0]=addition
       cine['v50Cinematic']=True
    else:
       idx=next((i for i,x in enumerate(actions) if x.get('do')=='scene'),0)
       actions.insert(idx,{'do':'cine','cmds':[
          {'c':'bars','on':True,'t':.55},
          {'c':'shot','focus':'player','zoom':1.2,'t':.9},
          *addition,{'c':'wait','t':.5},
          {'c':'bars','on':False,'t':.55}], 'v50Cinematic':True})
    # Don't replace old v4.8 scores or authored music, preserve old cue as fallback.
    # The new score is started before the cinematic moment.
    actions.insert(0,{'do':'music','id':score,'v50Cinematic':True})
 s['meta']['cinematicVerticalWorldVersion']='5.0.0'
 q['_v50_cinematic']='21 climbable optional panoramic cutscenes + 11 upgraded main narrative anchors; no canon divergence'
 Q.write_text(json.dumps(q,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 S.write_text(json.dumps(s,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 print('V5.0:',len(specs)*2,'new route-specific 7-line scenes,',len(specs),'playable viewpoint quests,',len(MAIN_ANCHORS),'main cutscene enhancements')

if __name__=='__main__':main()
