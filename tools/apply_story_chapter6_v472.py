#!/usr/bin/env python3
"""Chapter 6: Our Tomorrow / The Unwritten Page. Private additive draft patch.

Rebuild order: after apply_story_chapter5_v471.py. Never rename old quest/scene IDs.
Save slots written by older versions can still resume in their existing step; the
old C06 reveal forwards to the additional arc before returning to C06_LETTER.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'android/assets/data'
V='V472'
def a(do,**kwargs):return {'do':do,**kwargs}
def line(w,t,e='neutral'):return {'s':w,'t':t,'e':e}
def cond(flag,yes,no=None):return a('if',when={'flags':[flag]},then=yes,**{'else':no or []})
def by_route(yes,no):return a('if',when={'route':'arland'},then=yes,**{'else':no})
def shot(title,sub,focus='partner',z=1.26):return a('cine',cmds=[{'c':'bars','on':True,'t':.4},{'c':'shot','focus':focus,'zoom':z,'frame':'intimate','t':1.4,'bars':False},{'c':'caption','text':title,'sub':sub,'t':3.1},{'c':'bars','on':False,'t':.4}])
def sc(db,key,title,location,dialogues,route='shared',choices=(),flags=()):
 db['scenes'][key]={'title':title,'chapter':('EPI' if key.startswith('V472-EPI-') else 'C06'),'route':route,'location':location,
  'trigger':'v4.7.2 real quest chapter6','lines':[line(*d) for d in dialogues],
  'choices':list(choices),'flags':list(flags)}
def choice(label,flag,dialogues):
 return {'text':label,'flags':[flag],'byRoute':{r:[line(*x) for x in dialogues] for r in ('arland','sofia')}}
def it(key,area,x,y,label,actions,rt=None,hide=None,need=None,icon=None):
 obj={'id':key,'area':area,'x':x,'y':y,'r':100,'label':label,'actions':actions}
 if rt:obj['route']=rt
 if hide:obj['hideIfFlag']=hide
 if need:obj['when']={'flags':[need]}
 if icon:obj['sprite']={'image':'items/v472_c06_'+icon+'.png','x':x,'y':y-15,'bob':True}
 return obj
def step(key,objective,items,complete=None):
 o={'id':key,'chapter':'C06','quest':'Q_V472_C06','objective':{'arland':objective,'sofia':objective},'interactables':items}
 if complete:o.update({'counter':complete['counter'],'counterMax':complete['count'],'complete':complete})
 return o
def memory(db,id,title,desc,flag,icon,route='shared',kind='fictional_memory'):
 db['entries'].append({'id':'v472_c06_'+id,'chapter':'C06','route':route,'type':kind,
                       'unlock':flag,'icon':'items/v472_c06_'+icon+'.png','title':title,'text':desc})
def apply():
 s=json.loads((DATA/'story.json').read_text());q=json.loads((DATA/'quests.json').read_text());m=json.loads((DATA/'maps.json').read_text());b=json.loads((DATA/'memory_book.json').read_text())
 steps={x['id']:x for x in q['steps']}
 for key in ('C06_Q_REVEAL','C06_LETTER','C06_FINAL','EPI_FEST_LEPAS'):
  assert key in steps,key
 assert 'V471-C05-QUIET-REVEAL' in s['scenes'],'Apply Chapter5 first'
 # Deterministic replacement of our owned content; all original IDs survive.
 s['scenes']={k:v for k,v in s['scenes'].items() if not k.startswith('V472-')}
 q['steps']=[x for x in q['steps'] if not x['id'].startswith('V472_C06_')]
 b['entries']=[x for x in b['entries'] if not x['id'].startswith('v472_c06_')]
 for k in list(b['items']):
  if k.startswith('v472_c06_'):del b['items'][k]
 s['meta']['chapter6Overhaul']='v4.7.2 private draft; three futures, 2 route viewpoints, four memories and one canon ending'
 
 sc(s,'V472-C06-HALL-OPEN','Balai Hari yang Belum Datang','eternal_garden',[
  ('narrator','Tiga pintu di belakang Pohon Harapan menyala. Pada masing-masing pintu, hari esok tampak terlalu sempurna.'),
  ('lumi','Kalian sudah memahami kenangan. Tapi apakah kalian ingin menyerahkan masa depan pada buku yang tidak pernah membiarkan kalian salah?'),
  ('sofia','Aku penasaran, tapi aku nggak mau kehilangan kebebasan memilih.'),
  ('arland','Kalau begitu, kita lihat bersama. Tanpa janji untuk mengambil apa pun dari sana.')])
 sc(s,'V472-C06-HALL-INTRO','Tiga Masa Depan yang Terlalu Rapi','hall_of_tomorrow',[
  ('narrator','Balai itu tidak menampilkan hari yang akan terjadi. Ia menampilkan hari yang mungkin terjadi bila semua hal dipaksa sempurna.'),
  ('sofia','Kita bahkan nggak bisa lihat bekas hujan di jendela.'),
  ('arland','Tempatnya bagus. Tapi kenapa rasanya kita cuma mengikuti naskah orang lain?')])
 futures=[
  ('DATE','Kencan Tanpa Kesalahan','Semua kursi terisi dan semua foto sempurna.',
   'Sofia tersenyum pada jam yang tidak pernah terlambat; tak ada satu pun pilihan tentang kapan ia ingin pergi.'),
  ('PRESENCE','Janji yang Selalu Tepat','Sebuah kalender mencatat setiap janji berhasil.',
   'Arland selalu datang tepat waktu, tetapi ia tak pernah boleh mengakui bahwa dirinya lelah atau butuh bantuan.'),
  ('AGREEMENT','Hari Tanpa Salah Paham','Dua bayangan selalu mengangguk bersamaan.',
   'Mereka tidak pernah bertengkar. Mereka juga tidak pernah mengatakan apa yang sebenarnya mereka inginkan.')]
 for suffix,title,intro,impact in futures:
  for route in ('arland','sofia'):
   tag='A' if route=='arland' else 'S'
   lines=[('narrator',intro),('narrator',impact)]
   if suffix=='DATE':
    lines += [('arland','Boleh jadi semuanya berjalan mulus. Tapi apakah Sofia benar-benar boleh bilang tidak?') if route=='arland'
              else ('sofia','Aku boleh senang berkencan, tapi aku juga harus boleh memilih hari lain.')]
   elif suffix=='PRESENCE':
    lines += [('arland','Aku ingin menepati janji. Tapi aku juga harus belajar meminta bantuan sebelum terlambat.') if route=='arland'
              else ('sofia','Aku nggak mau Arland merasa harus selalu sempurna hanya agar aku bahagia.')]
   else:
    lines += [('arland','Kalau aku selalu menebak jawaban Sofia, aku nggak akan pernah belajar mendengarkan.') if route=='arland'
              else ('sofia','Kalau semuanya disetujui begitu saja, suaraku malah nggak ada artinya.')]
   sc(s,'V472-C06-ILLUSION-'+suffix+'-'+tag,title,'hall_of_tomorrow',lines,route,[
    choice('Lihat bagian yang hilang dari gambaran ini','V472_'+suffix+'_'+tag+'_SEE',[
     ('narrator','Ada bagian yang sengaja tak digambar oleh halaman masa depan: pilihan dan perasaan mereka sendiri.')]),
    choice('Tolak masa depan yang memaksa semuanya sempurna','V472_'+suffix+'_'+tag+'_REFUSE',[
     (route,'Aku ingin tetap punya ruang buat mengambil keputusan yang nggak selalu mudah.')])])
 sc(s,'V472-C06-THREE-FUTURES','Ketika Sempurna Terasa Sunyi','hall_of_tomorrow',[
  ('narrator','Ketiga proyeksi memudar. Tidak ada satu pun yang memberikan kesempatan untuk tumbuh atau meminta maaf.'),
  ('sofia','Aku nggak mau menghapus hari galeri. Aku ingin mengingat keberanian, kekecewaan, dan perubahan setelahnya.'),
  ('arland','Aku juga. Aku ingin datang karena aku memilih hadir, bukan karena jam di buku melarangku terlambat.'),
  ('lumi','Jika begitu, buktikan bahwa kalian mampu menyimpan dua kenangan tanpa menyamakan keduanya.')])
 # Two personal reflection chapters with 3 meaningful player choices.
 sc(s,'V472-C06-ARLAND-REFLECTION','Surat Arland untuk Masa Depan','hall_of_tomorrow',[
  ('narrator','Arland meletakkan bunga kertas lama di sebelah catatan galeri yang sudah kusut.'),
  ('arland','Aku pernah percaya kejutan bisa menggantikan kehadiran. Padahal Sofia hanya meminta aku datang.'),
  ('sofia','Aku nggak butuh kamu selalu benar, Land. Aku butuh kita bisa bilang kalau sesuatu terasa berat.'),
  ('arland','Kalau besok aku mulai merasa harus memperbaiki segalanya sendiri, apa yang harus kuingat?')], 'arland',[
   choice('Duduk dan mendengarkan sampai selesai','V472_A_FUTURE_LISTEN',[
    ('arland','Sebelum menawarkan solusi, aku akan tanya apa yang kamu butuhkan.'),('sofia','Kadang ditemani itu sudah berarti banyak.')]),
   choice('Hadir sesuai janji, tanpa menggantinya dengan kejutan','V472_A_FUTURE_PRESENT',[
    ('arland','Aku akan menjaga waktumu dan ngabarin sebelum semuanya terlambat.'),('sofia','Terima kasih, Land. Itu yang dulu pengen aku dengar.')]),
   choice('Berani meminta bantuan sebelum semuanya kacau','V472_A_FUTURE_HELP',[
    ('arland','Aku juga punya batas. Aku nggak perlu sembunyikan itu.'),('sofia','Kita bisa cari jalan bareng, tanpa kamu menanggung semuanya sendiri.')])])
 sc(s,'V472-C06-SOFIA-REFLECTION','Halaman Sofia yang Berani Dibaca','hall_of_tomorrow',[
  ('narrator','Sofia membuka dua gambar: kursi kosong yang pernah membuatnya sedih, dan bangku tempat mereka belajar bicara lagi.'),
  ('sofia','Aku ingin mengingat diriku yang tetap berdiri di galeri. Bukan hanya kursinya yang kosong.'),
  ('arland','Aku bangga karena kamu menyelesaikan presentasinya. Maaf aku baru tahu betapa beratnya hari itu.'),
  ('sofia','Kalau nanti ada hari sulit, bagian mana dari diriku yang ingin tetap kujaga?')], 'sofia',[
   choice('Mengatakan perasaanku tanpa takut merepotkan','V472_S_FUTURE_VOICE',[
    ('sofia','Aku boleh mengucapkan apa yang aku butuh, bahkan kalau suaraku gemetar.'),('arland','Aku mau mendengar tanpa menebak-nebak.')]),
   choice('Meminta ruang tanpa menghilang dari hubungan','V472_S_FUTURE_SPACE',[
    ('sofia','Aku bisa minta waktu sendiri, lalu kembali bicara saat siap.'),('arland','Aku akan hormati itu tanpa memaksamu langsung baik-baik saja.')]),
   choice('Bangga pada langkahku, meski tak ada yang menyaksikan','V472_S_FUTURE_COURAGE',[
    ('sofia','Presentasi itu juga milikku. Dan aku nggak mau mengecilkan keberanianku sendiri.'),('arland','Aku nggak ingin keberhasilanmu bergantung pada apakah aku hadir.')])])
 sc(s,'V472-C06-REAL-C01','Mural yang Menunjukkan Dua Arah','hall_of_tomorrow',[
  ('narrator','Pada panel pertama, bunga-buku-bintang berdampingan dengan bintang-buku-bunga. Dua arah, satu surat.'),
  ('arland','Kita sejak awal nggak selalu melihat petunjuk yang sama.'),('sofia','Tapi kita sama-sama berusaha memahami.')])
 for k,text in [('LISTEN','Aku dulu ingin benar-benar mendengar.'),('RECORD','Aku menyimpan petunjuk itu agar kita tidak kehilangan cerita.'),('TRACE','Aku mencoba mencari jejak yang tersembunyi.')]:
  sc(s,'V472-C06-C01-'+k,'Pilihan di Kafe Senja','hall_of_tomorrow',[( 'arland' if k!='LISTEN' else 'sofia',text)])
 sc(s,'V472-C06-REAL-C02','Kencan yang Memang Dipilih','hall_of_tomorrow',[
  ('narrator','Di panel kedua, bingkai foto tetap memuat cahaya lentera yang tidak ada saat pemotretan.'),
  ('sofia','Yang kuingat bukan fotonya sempurna. Aku ingat kita punya pilihan dan kamu menghargainya.')])
 for k,text in [('YES','Aku memilih ikut karena memang mau.'),('LATER','Aku memilih besok dan keinginanku dihormati.'),('NO','Aku memilih sendiri dulu. Dan hari itu tetap berarti.')]:
  sc(s,'V472-C06-C02-'+k,'Sofia Mengingat Pilihannya','hall_of_tomorrow',[('sofia',text)],'sofia')
 sc(s,'V472-C06-REAL-C03','Hal-Hal Kecil yang Tidak Hilang','hall_of_tomorrow',[
  ('narrator','Bingkai yang sempat rusak, masakan pertama, scrapbook dan surat setengah jadi muncul berdampingan.'),
  ('arland','Aku ingat sekarang. Merawat sesuatu bukan berarti mengendalikan semuanya.'),
  ('sofia','Dan hal kecil tetap berarti, bahkan kalau nggak ada orang lain yang melihat.')])
 sc(s,'V472-C06-REAL-C04','Dua Gambar pada Satu Halaman','hall_of_tomorrow',[
  ('narrator','Proyektor yang menyala dan kursi kosong muncul sekaligus. Tidak ada yang dihapus atau ditutup.'),
  ('sofia','Aku sedih hari itu. Tapi aku juga bangga karena tetap berani.'),
  ('arland','Aku yang tidak hadir. Dan aku mau mengingatnya supaya pilihan besok berbeda.')])
 for id,who,msg in [('TIME','arland','Aku ingin menepati waktu, bukan menjadikan keterlambatan sebagai cerita heroik.'),
                   ('ASK','arland','Aku belajar bertanya sebelum menebak apa yang Sofia butuhkan.'),
                   ('HELP','arland','Aku mulai berani meminta bantuan saat tidak sanggup.'),
                   ('PRESENT','sofia','Aku berhak meminta kehadiran tanpa merasa terlalu banyak menuntut.'),
                   ('SPACE','sofia','Aku belajar memilih ruang tanpa harus menutupi perasaanku.'),
                   ('LISTEN','sofia','Aku ingin suaraku didengar, bahkan kalau aku belum menemukan kalimat yang tepat.')]:
  sc(s,'V472-C06-C05-'+('A' if who=='arland' else 'S')+'-'+id,
    'Jembatan yang Mengubah Cara Kami Melangkah','hall_of_tomorrow',[(who,msg)],who)
 sc(s,'V472-C06-TWO-VOICES','Dua Urutan yang Tidak Harus Sama','hall_of_tomorrow',[
  ('narrator','Empat panel menyatu tanpa menjadikan salah satunya lebih benar. Retaknya tetap terlihat, tetapi tidak memutus jembatan.'),
  ('lumi','Kalian tidak mengalahkan kenangan yang sulit. Kalian belajar menempatkannya dengan jujur.'),
  ('arland','Boleh kita simpan dua gambar itu, Sof?'),('sofia','Boleh. Aku ingin keduanya tetap ada.')],flags=['V472_C06_ALIGNED'])
 sc(s,'V472-C06-PROMISE','Dua Langkah, Tanpa Jaminan Sempurna','hall_of_tomorrow',[
  ('narrator','Pintu keluar muncul. Di atasnya tertulis: Besok bukan halaman yang sudah terisi.'),
  ('sofia','Kalau suatu hari nanti kita lupa apa yang rasanya penting, kita bisa saling cerita lagi.'),
  ('arland','Kalau ceritanya berbeda, kita dengar dua-duanya.'),
  ('sofia','Dan kalau ada hari yang nggak mudah?'),('arland','Kita belajar lagi, pelan-pelan. Nggak perlu pura-pura sempurna.')])
 sc(s,'V472-C06-PAYOFF-ARLAND','Arland Memilih Kehadiran','eternal_garden',[
  ('narrator','Bunga kertas Arland tak berubah menjadi benda mewah. Bekas lipatannya tetap terlihat.'),
  ('arland','Aku ingin membuat banyak hari baik. Tapi kalau ada hari yang sulit, aku mau tetap hadir.')],'arland')
 sc(s,'V472-C06-PAYOFF-SOFIA','Sofia Menyimpan Keberaniannya','eternal_garden',[
  ('narrator','Sofia menaruh gambar kursi kosong di samping gambar dirinya yang tetap berdiri di depan galeri.'),
  ('sofia','Aku nggak perlu menghapus salah satu gambar untuk mengingat bahwa aku berani.')],'sofia')
 for flag,route,label,body in [('V472_A_FUTURE_LISTEN','arland','Dengar sampai selesai','Aku tidak selalu harus memperbaiki yang sedang Sofia ceritakan.'),
   ('V472_A_FUTURE_PRESENT','arland','Datang tanpa kejutan','Kehadiran yang dijanjikan tidak tergantikan oleh kejutan paling bagus.'),
   ('V472_A_FUTURE_HELP','arland','Belajar meminta bantuan','Arland tidak harus menanggung semua kesulitan sendirian.'),
   ('V472_S_FUTURE_VOICE','sofia','Berani mengucapkan','Sofia tidak perlu menunggu seseorang menebak perasaannya.'),
   ('V472_S_FUTURE_SPACE','sofia','Ruang untuk pulang','Sofia bisa mengambil waktu tanpa memendam semua hal selamanya.'),
   ('V472_S_FUTURE_COURAGE','sofia','Bangga pada diri sendiri','Keberanian Sofia bukan sesuatu yang bergantung pada kursi penonton.')]:
  suffix=flag.removeprefix('V472_')
  sc(s,'V472-ECHO-'+suffix,label,'eternal_garden',[('narrator',body),
      (route,'Itu yang ingin aku bawa ke hari-hari berikutnya.')],route)
 # End-of-game coda is varied but canon remains exactly one; safely inserted before credits.
 for f,t in [('V472_A_FUTURE_LISTEN','Kadang satu percakapan cukup untuk membuat hari yang sulit terasa lebih ringan.'),
             ('V472_A_FUTURE_PRESENT','Aku masih ingat kita berjanji saling hadir, bukan saling mengesankan.'),
             ('V472_A_FUTURE_HELP','Sekarang kita lebih berani mengakui kalau butuh bantuan.'),
             ('V472_S_FUTURE_VOICE','Aku berani mengatakan hal-hal yang dulu hanya kutulis sendiri.'),
             ('V472_S_FUTURE_SPACE','Kita belajar bahwa memberi ruang tidak berarti menjauh selamanya.'),
             ('V472_S_FUTURE_COURAGE','Aku masih bangga dengan diriku pada hari itu.')]:
  sc(s,'V472-EPI-'+f[5:],'Kenangan yang Dibawa Pulang','taman_kota', [('sofia' if '_S_' in f else 'arland',t)],'sofia' if '_S_' in f else 'arland')
 # Three illusion decisions remain distinct at the emotional climax: no fake choices.
 recall_text={
  'DATE':('Dulu kita bisa memilih kapan dan bagaimana mau berkencan.',
          'Aku nggak ingin ada jadwal sempurna kalau kita kehilangan hak bilang tidak.'),
  'PRESENCE':('Aku ingin mengingat waktumu dan batas kita, bukan jam yang sempurna.',
              'Kita boleh membuat janji dan juga boleh mengakui saat butuh pertolongan.'),
  'AGREEMENT':('Kita boleh beda pendapat dan tetap saling menghormati.',
               'Aku tak mau diam hanya demi terlihat selalu rukun.')}
 for name,(observed,rejected) in recall_text.items():
  for route,tag in [('arland','A'),('sofia','S')]:
   for answer,txt in [('SEE',observed),('REFUSE',rejected)]:
    sc(s,'V472-C06-RECALL-'+name+'-'+tag+'-'+answer,'Yang Kami Pilih untuk Diingat',
       'eternal_garden',[(route,txt),
       ('narrator','Kenangan itu tetap memiliki bekas yang tidak dipoles menjadi sempurna.')],route)
 # New real quest sequence. No timed wait or artificial energy cost.
 new=[]
 new.append(step('V472_C06_HALL_ENTRY','Temukan balai masa depan di balik Pohon Harapan',[
  it('v472_hall_gate','eternal_garden',1190,700,'Masuki Balai Hari Esok',[
   a('scene',id='V472-C06-HALL-OPEN'),shot('The Unwritten Page','Tak ada masa depan yang bisa dijamin sempurna'),
   a('warp',area='hall_of_tomorrow',x=180,y=1080,dir='up'),a('music',id='cinema_hall_v472'),
   a('scene',id='V472-C06-HALL-INTRO'),a('step',id='V472_C06_FUTURES')],icon='hall')]))
 illusions=[]
 for name,_,_,_ in futures:
  coords={'DATE':(410,880),'PRESENCE':(960,460),'AGREEMENT':(1510,880)}
  x,y=coords[name];f='V472_C06_SEEN_'+name
  illusions.append(it('v472_future_'+name.lower(),'hall_of_tomorrow',x,y,'Lihat masa depan: '+name.lower(),[
   by_route([a('scene',id='V472-C06-ILLUSION-'+name+'-A')],
            [a('scene',id='V472-C06-ILLUSION-'+name+'-S')]),
   a('sfx',id='v472_memory_glint'),a('flag',id=f),a('count',id='v472_c06_futures',add=1)],hide=f,icon='mirror'))
 new.append(step('V472_C06_FUTURES','Periksa tiga masa depan sempurna dan apa yang hilang darinya',illusions,
    {'counter':'v472_c06_futures','count':3,'actions':[
      a('scene',id='V472-C06-THREE-FUTURES'),a('music',id='cinema_unwritten_v472'),
      by_route([a('step',id='V472_C06_REFLECT_A')],[a('step',id='V472_C06_REFLECT_S')])]}))
 for route,tag in [('arland','A'),('sofia','S')]:
  id='V472-C06-ARLAND-REFLECTION' if route=='arland' else 'V472-C06-SOFIA-REFLECTION'
  new.append(step('V472_C06_REFLECT_'+tag,'Tulis satu hal yang ingin dijaga untuk hari esok',[
   it('v472_reflect_'+tag.lower(),'hall_of_tomorrow',930,900,'Baca dan tulis surat pribadi',[
    a('scene',id=id),a('flag',id='V472_C06_REFLECT_'+tag+'_DONE'),
    a('item',id='v472_c06_future_note'),a('step',id='V472_C06_ALIGN')],rt=route,icon='flower' if route=='arland' else 'sketch')]))
 panels=[]
 details=[('C01',450,620,'Mural Kafe Senja'),('C02',750,410,'Foto Kencan'),('C03',1210,410,'Bingkai dan Surat'),('C04',1500,620,'Kursi Kosong dan Jembatan')]
 for ch,x,y,label in details:
  actions=[]
  if ch=='C01':
   for flag,key in [('V467_C01_CHOOSE_LISTEN','LISTEN'),('V467_C01_CHOOSE_RECORD','RECORD'),('V467_C01_CHOOSE_TRACE','TRACE')]:actions.append(cond(flag,[a('scene',id='V472-C06-C01-'+key)]))
  elif ch=='C02':
   for flag,key in [('V468_S_REPLY_YES','YES'),('V468_S_REPLY_LATER','LATER'),('V468_S_REPLY_NO','NO')]:actions.append(cond(flag,[a('scene',id='V472-C06-C02-'+key)]))
  actions.append(a('scene',id='V472-C06-REAL-'+ch))
  if ch=='C04':
   for t in ('A','S'):
    for f in (['TIME','ASK','HELP'] if t=='A' else ['PRESENT','SPACE','LISTEN']):
     actions.append(cond('V471_'+t+'_CHOOSE_'+f,[a('scene',id='V472-C06-C05-'+t+'-'+f)]))
  f='V472_C06_ALIGNED_'+ch
  actions += [a('flag',id=f),a('sfx',id='v472_memory_glint'),a('count',id='v472_c06_panels',add=1)]
  panels.append(it('v472_align_'+ch.lower(),'hall_of_tomorrow',x,y,'Selaraskan '+label,actions,hide=f,icon='page'))
 new.append(step('V472_C06_ALIGN','Selaraskan empat kenangan tanpa menyamakan dua sudut pandang',panels,
    {'counter':'v472_c06_panels','count':4,'actions':[
      shot('Dua Suara','Kenangan tidak harus sama untuk tetap jadi milik bersama'),
      a('scene',id='V472-C06-TWO-VOICES'),a('item',id='v472_c06_two_sides'),
      a('step',id='V472_C06_PROMISE')]}))
 new.append(step('V472_C06_PROMISE','Dengarkan pasangan, kemudian buka jalan kembali ke Eternal Garden',[
  it('v472_listen','hall_of_tomorrow',690,970,'Dengarkan pasangan tanpa memotong',[
   a('scene',id='V472-C06-PROMISE'),a('flag',id='V472_C06_LISTEN_DONE')],hide='V472_C06_LISTEN_DONE',icon='flower'),
  it('v472_return','hall_of_tomorrow',1370,970,'Kembali ke Pohon Harapan',[
   a('sfx',id='v472_memory_glint'),a('music',id='cinema_unwritten_v472'),
   shot('Our Tomorrow','Halaman terakhir masih menunggu untuk dibuka'),
   a('flag',id='V472_C06_READY'),a('warp',area='eternal_garden',x=960,y=710,dir='up'),
   a('step',id='C06_LETTER')],need='V472_C06_LISTEN_DONE',icon='hall')]))
 # Keep original C06 reveal and finale IDs and narratively move the new arc between them.
 reveal=next(i for i in steps['C06_Q_REVEAL']['interactables'] if i['id']=='q_reveal')
 rewired=0
 for action in reveal['actions']:
  if action.get('do')=='step' and action.get('id') in ('C06_LETTER','V472_C06_HALL_ENTRY'):
   action['id']='V472_C06_HALL_ENTRY';rewired+=1
 assert rewired==1,'C06 reveal handoff changed; inspect before reapplying'
 # Add payoff scenes immediately before original shared canon finale, not after credits.
 final=next(i for i in steps['C06_FINAL']['interactables'] if i['id']=='pages')
 actions=[x for x in final['actions'] if not x.get('v472')]
 idx=next(i for i,x in enumerate(actions) if x.get('do')=='scene' and x.get('id')=='C06-X01')
 inserts=[dict(by_route([a('scene',id='V472-C06-PAYOFF-ARLAND')],[a('scene',id='V472-C06-PAYOFF-SOFIA')]),v472=True)]
 for fl in ('V472_A_FUTURE_LISTEN','V472_A_FUTURE_PRESENT','V472_A_FUTURE_HELP',
            'V472_S_FUTURE_VOICE','V472_S_FUTURE_SPACE','V472_S_FUTURE_COURAGE'):
  inserts.append(dict(cond(fl,[a('scene',id='V472-ECHO-'+fl[5:])]),v472=True))
 # Recall player response to each projected future, independently for both routes.
 for name,_,_,_ in futures:
  for tag in ('A','S'):
   for answer in ('SEE','REFUSE'):
    fl='V472_'+name+'_'+tag+'_'+answer
    inserts.append(dict(cond(fl,[a('scene',id='V472-C06-RECALL-'+name+'-'+tag+'-'+answer)]),v472=True))
 actions[idx:idx]=inserts
 final['actions']=actions
 # Epilogue callbacks, inserted before its existing emotional closure; not a second ending.
 fest=next(i for i in steps['EPI_FEST_LEPAS']['interactables'] if i['id']=='fest_release')
 actions=[x for x in fest['actions'] if not x.get('v472')]
 index=next(i for i,x in enumerate(actions) if x.get('do')=='chapterEnd')
 callbacks=[]
 for fl in ('V472_A_FUTURE_LISTEN','V472_A_FUTURE_PRESENT','V472_A_FUTURE_HELP',
            'V472_S_FUTURE_VOICE','V472_S_FUTURE_SPACE','V472_S_FUTURE_COURAGE'):
  callbacks.append(dict(cond(fl,[a('scene',id='V472-EPI-'+fl[5:])]),v472=True))
 actions[index:index]=callbacks
 fest['actions']=actions
 # Original hall map art is generated separately from the editable code in gen_chapter6_assets_v472.py.
 m['areas']['hall_of_tomorrow']={'name':'Balai Hari Esok — Three Futures','image':'maps/hall_of_tomorrow.png',
  'w':1920,'h':1280,'spawn':[180,1080],'indoor':False,'music':'memory','ambient':'magic_chimes',
  'walls':[[0,0,20,1280],[1900,0,20,1280],[0,0,1920,20],[0,1260,1920,20]],
  'ellipses':[],'props':[],'gates':[],'animals':[],'water':[],'examine':[],
  'storyVersion':'v472_c06_emotional_finale','visualStyle':'dreamlike_three_perfect_futures',
  'doors':[{'id':'v472_hall_to_garden','rect':[75,1200,140,52], 'to':'eternal_garden','tx':960,'ty':710,
            'label':'Kembali ke Eternal Garden','dir':'down'}]}
 garden=m['areas']['eternal_garden'];garden['doors']=[x for x in garden.get('doors',[]) if x.get('id')!='v472_garden_to_hall']
 garden['doors'].append({'id':'v472_garden_to_hall','rect':[1170,690,95,60],
  'to':'hall_of_tomorrow','tx':180,'ty':1080,'label':'Balai Hari Esok','dir':'right',
  'locked':[{'when':{'maxChapter':'C05'},'text':'Halaman masa depan belum terbuka.'}]})
 b['items'].update({
  'v472_c06_future_note':{'name':'Catatan Masa Depan','desc':'Keinginan yang dipilih sendiri, bukan masa depan yang dipaksakan.','icon':'items/v472_c06_flower.png'},
  'v472_c06_two_sides':{'name':'Dua Versi, Satu Halaman','desc':'Kursi kosong dan kehadiran besok tidak menghapus satu sama lain.','icon':'items/v472_c06_page.png'}})
 for id,title,desc,fl,icon,rt,kind in [
  ('future_hall','Balai Hari Esok','Tiga hari yang terlalu sempurna ternyata tidak memberi ruang untuk memilih.','V472_C06_READY','hall','shared','fictional_memory'),
  ('cafe','Dua Arah di Kafe Senja','Dua urutan simbol tetap membuka satu surat yang sama.','V472_C06_ALIGNED_C01','page','shared','fictional_memory'),
  ('date','Kencan yang Dipilih','Bahagia tidak berarti menghapus hak untuk menunda atau menolak.','V472_C06_ALIGNED_C02','mirror','shared','fictional_memory'),
  ('little','Perhatian yang Tidak Dipaksa','Masakan, bingkai dan surat yang tak selesai tetap berarti.','V472_C06_ALIGNED_C03','flower','shared','fictional_memory'),
  ('gallery','Dua Gambar Tidak Dihapus','Satu kenangan bisa memuat keberanian, niat baik dan kesedihan sekaligus.','V472_C06_ALIGNED_C04','sketch','shared','fictional_memory'),
  ('aligned','Halaman yang Diterima','Mereka tidak harus mengingat kejadian dengan cara sama.','V472_C06_ALIGNED','page','shared','fictional_memory')]:memory(b,id,title,desc,fl,icon,rt,kind)
 for t,rt,opts in [('a','arland',['LISTEN','PRESENT','HELP']),('s','sofia',['VOICE','SPACE','COURAGE'])]:
  for fl in opts:
   memory(b,'future_'+t+'_'+fl.lower(),'Janji Kecil untuk Esok','Keputusan personal yang diingat saat penutupan cerita.',
    'V472_'+t.upper()+'_FUTURE_'+fl,'flower' if rt=='arland' else 'sketch',rt,'optional_story_branch')
 for name,_,_,_ in futures:
  memory(b,'illusion_'+name.lower(),'Masa Depan yang Bukan Jaminan','Satu gambaran indah yang kehilangan pilihan.',
   'V472_C06_SEEN_'+name,'mirror','shared','fictional_memory')
 # Choice-exclusive collectible memories do not falsely count as required completion.
 for name,_,_,_ in futures:
  for route,tag in [('arland','A'),('sofia','S')]:
   for answer in ('SEE','REFUSE'):
    memory(b,'future_'+name.lower()+'_'+tag.lower()+'_'+answer.lower(),
           'Masa Depan '+name.title(),'Cara '+route+' menanggapi proyeksi masa depan.',
           'V472_'+name+'_'+tag+'_'+answer,'mirror',route,'optional_story_branch')
 q['steps'] += new
 for name,obj in [('story.json',s),('quests.json',q),('maps.json',m),('memory_book.json',b)]:
  (DATA/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('PASS: Chapter6 original hall, three alternate futures, personal reflections, four memory alignments, two-route finale; %d new quest steps, %d new scenes'%(len(new),sum(k.startswith('V472-') for k in s['scenes'])))
if __name__=='__main__':apply()
