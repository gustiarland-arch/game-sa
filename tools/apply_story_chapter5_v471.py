#!/usr/bin/env python3
"""Chapter 5 / Across the Stars complete narrative + playable mechanics.
LOCAL DRAFT ONLY. Deterministic and idempotent over the previous chapter patches.
Do not remove original IDs: old save slots must be able to resume past C05 steps.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'android/assets/data'
def act(do,**kw):return {'do':do,**kw}
def ln(w,t,e='neutral'):return {'s':w,'t':t,'e':e}
def cond(flag,yes,no=None):return act('if',when={'flags':[flag]},then=yes,**{'else':no or []})
def route(a,s):return act('if',when={'route':'arland'},then=a,**{'else':s})
def cine(title,sub,zoom=1.24):return act('cine',cmds=[{'c':'bars','on':True,'t':.35},{'c':'shot','focus':'partner','zoom':zoom,'frame':'intimate','t':1.5,'bars':False},{'c':'caption','text':title,'sub':sub,'t':3.0},{'c':'bars','on':False,'t':.45}])
def scene(db,key,title,location,lines,rt='shared',choices=(),flags=()):
 db['scenes'][key]={'title':title,'chapter':'C05','route':rt,'location':location,'trigger':'v4.7.1 playable chapter5 original',
  'lines':[ln(*x) for x in lines],'flags':list(flags),'choices':list(choices)}
def choose(text,flag,answers):
 return {'text':text,'flags':[flag],'byRoute':{r:[ln(*x) for x in answers] for r in ('arland','sofia')}}
def it(key,area,x,y,label,actions,rt=None,once=None,need=None,icon=None):
 o={'id':key,'area':area,'x':x,'y':y,'r':95,'label':label,'actions':actions}
 if rt:o['route']=rt
 if once:o['hideIfFlag']=once
 if need:o['when']={'flags':[need],'notFlags':[once]} if once else {'flags':[need]}
 if icon:o['sprite']={'image':'items/v471_c05_'+icon+'.png','x':x,'y':y-16,'bob':True}
 return o
def step(key,desc,items,complete=None,route_name=None,onstart=None):
 o={'id':key,'chapter':'C05','quest':'Q_V471_C05','objective':{'arland':desc,'sofia':desc},'interactables':items}
 if complete:o['complete']=complete;o['counter']=complete['counter'];o['counterMax']=complete['count']
 if onstart:o['onStart']=onstart
 return o
def mem(db,key,title,text,flag,icon,rt='shared',kind='fictional_memory'):
 db['entries'].append({'id':key,'chapter':'C05','route':rt,'type':kind,'unlock':flag,'icon':'items/v471_c05_'+icon+'.png','title':title,'text':text})
def patch():
 s=json.loads((DATA/'story.json').read_text());q=json.loads((DATA/'quests.json').read_text());b=json.loads((DATA/'memory_book.json').read_text());m=json.loads((DATA/'maps.json').read_text())
 steps={x['id']:x for x in q['steps']}
 assert 'V470_C04_REPAIR_EARNED' in json.dumps(s,ensure_ascii=False),'Chapter4 patch must be applied before C05'
 assert 'C05_V26_STARGAZE' in steps and 'C05_Q_ECHO' in steps and 'C05_STARMAP' in steps
 assert {'starfall_village','eternal_garden','lantern_field','rain_garden'}<=set(m['areas'])
 s['meta']['chapter5Overhaul']='v4.7.1 local draft: clockwork, moonlight, memory bridge, earned reveal'
 # Character-flaw callback in two separate routes. No cheating/forced drama; consequences are legible.
 scene(s,'V471-C05-ENTRY','Langit yang Tidak Menyalahkan','starfall_village',[
  ('narrator','Jauh di atas Starfall Village, sebuah jam bintang tersendat. Jembatan yang terlihat kemarin kini hanya separuh.'),
  ('sofia','Aku masih takut mengulang hari di galeri.'),('arland','Aku juga. Tapi aku mau membuktikan bahwa aku bisa hadir, bukan cuma minta kesempatan.'),
  ('lumi','Kalian tak perlu memutuskan siapa yang paling benar. Mesin ini hanya bergerak bila kedua kisah diberi tempat.')])
 scene(s,'V471-C05-A-GEAR-1','Roda Gigi Janji','clockwork_station',[
  ('narrator','Roda pertama memperlihatkan jadwal pameran yang sudah ditulis lama sebelum acara.'),
  ('arland','Waktunya sudah jelas. Aku yang tidak membagi waktu dan membiarkan Sofia menunggu.')],'arland')
 scene(s,'V471-C05-A-GEAR-2','Roda Gigi Keputusan','clockwork_station',[
  ('narrator','Roda kedua menggemakan bunyi mesin proyektor ketika lampu galeri sudah padam.'),
  ('arland','Aku memilih memperbaiki alat, padahal ada orang yang lebih membutuhkan kehadiranku.')],'arland')
 scene(s,'V471-C05-A-GEAR-3','Roda Gigi Kabar','clockwork_station',[
  ('narrator','Roda ketiga berputar setengah; ujungnya adalah pesan yang sempat dikirim atau tidak pernah terkirim.'),
  ('arland','Mengabari tidak menghapus kesedihan orang lain. Tapi diam membuatnya makin sulit.')],'arland')
 scene(s,'V471-C05-S-ETCH-1','Ukiran yang Tetap Ada','clockwork_station',[
  ('narrator','Pada sisi pertama roda jam, Sofia melihat siluet dirinya berdiri di depan gambar.'),
  ('sofia','Aku gugup, tetapi aku tetap menyelesaikan presentasinya. Itu juga bagian dari ingatanku.')],'sofia')
 scene(s,'V471-C05-S-ETCH-2','Ukiran Kursi Kosong','clockwork_station',[
  ('narrator','Sisi kedua hanya memperlihatkan satu kursi yang tidak ditempati.'),
  ('sofia','Aku boleh kecewa tanpa merasa bersalah karena berharap seseorang datang.')],'sofia')
 scene(s,'V471-C05-S-ETCH-3','Ukiran yang Belum Selesai','clockwork_station',[
  ('narrator','Sisi terakhir memuat dua garis yang tidak pernah tersambung di hari galeri.'),
  ('sofia','Aku tidak mau luka itu jadi seluruh ceritaku. Tapi aku juga tidak ingin pura-pura lupa.')],'sofia')
 scene(s,'V471-C05-CLOCK-DONE','Jam yang Bergerak Lagi','clockwork_station',[
  ('narrator','Ketika tiga bagian tersusun, jarum jam akhirnya bergerak. Waktu yang terlewat tidak berputar kembali.'),
  ('lumi','Memperbaiki tidak berarti mengulang masa lalu. Kalian sedang memilih apa yang dilakukan sesudahnya.')])
 scene(s,'V471-C05-A-REFLECT','Pantulan Niat','moonlight_lake',[
  ('narrator','Di air danau, Arland melihat dirinya membawa proyektor yang akhirnya menyala. Di belakangnya, ada kursi kosong.'),
  ('arland','Aku ingin membahagiakan Sofia. Tapi aku tak boleh membuat niatku menghapus perasaannya.')],'arland')
 scene(s,'V471-C05-S-REFLECT','Pantulan Keberanian','moonlight_lake',[
  ('narrator','Sofia melihat kursi kosong—lalu pantulan beralih ke wajahnya yang tetap berbicara sampai akhir acara.'),
  ('sofia','Aku masih sedih tentang hari itu. Tapi hari itu juga membuktikan bahwa aku berani.')],'sofia')
 scene(s,'V471-C05-MOON-MIRROR','Pantulan yang Tidak Sama','moonlight_lake',[
  ('narrator','Dua pantulan tampak pada air yang sama. Mereka tidak saling menimpa; masing-masing perlahan menjadi lebih jelas.'),
  ('lumi','Tak ada pantulan yang harus dihapus agar pantulan lain dapat terlihat.')])
 scene(s,'V471-C05-MOON-C04-WARN','Kabar yang Tidak Membatalkan Rasa Sedih','moonlight_lake',[
  ('arland','Aku sempat mengirim kabar. Tapi aku ingin belajar menjaga waktunya lebih dulu, bukan hanya mengumumkan keterlambatan.')],'arland')
 scene(s,'V471-C05-MOON-C04-SILENT','Pesan yang Tidak Pernah Sampai','moonlight_lake',[
  ('arland','Waktu aku diam, Sofia harus menebak sendiri. Aku tidak mau membiarkannya menunggu begitu lagi.')],'arland')
 scene(s,'V471-C05-MOON-C04-HELP','Berani Tidak Menanggung Sendiri','moonlight_lake',[
  ('arland','Aku mencoba meminta bantuan, tapi terlambat. Berikutnya aku ingin tahu kapan berhenti dan hadir.')],'arland')
 for k,fl,t in [('PRESENT','V470_S_NEED_PRESENT','Aku ingin kehadiran, bukan kesempurnaan.'),('UPDATE','V470_S_NEED_UPDATE','Aku ingin diberi kabar sebelum terlambat.'),('LISTEN','V470_S_NEED_LISTEN','Aku ingin didengar sampai selesai dan boleh butuh waktu.')]:
  scene(s,'V471-C05-MOON-S-'+k,'Apa yang Sofia Butuhkan','moonlight_lake',[('sofia',t)],'sofia')
 scene(s,'V471-C05-A-CHOICE','Belajar Hadir','moonlight_lake',[
  ('arland','Aku nggak bisa mengulang hari itu. Tapi aku bisa memilih cara hadir di hari-hari berikutnya.')],rt='arland',choices=[
  choose('Aku akan menepati waktu, sekalipun tanpa kejutan','V471_A_CHOOSE_TIME',[('arland','Aku akan mencatat waktu dan benar-benar datang.')]),
  choose('Aku akan bertanya apa yang Sofia butuhkan','V471_A_CHOOSE_ASK',[('arland','Aku ingin dengar jawabannya, meski berbeda dari bayanganku.')]),
  choose('Aku akan berhenti menyelesaikan semuanya sendirian','V471_A_CHOOSE_HELP',[('arland','Aku boleh meminta bantuan sebelum telanjur kehilangan momen.')])])
 scene(s,'V471-C05-S-CHOICE','Menjaga Suara Sendiri','moonlight_lake',[
  ('sofia','Aku nggak harus menyembunyikan apa yang aku perlukan hanya agar tak merepotkan siapa-siapa.')],rt='sofia',choices=[
  choose('Aku akan bilang saat butuh ditemani','V471_S_CHOOSE_PRESENT',[('sofia','Aku boleh mengajak seseorang hadir untuk momen pentingku.')]),
  choose('Aku boleh meminta waktu untuk menenangkan diri','V471_S_CHOOSE_SPACE',[('sofia','Menunggu sampai siap bicara juga bentuk kejujuran.')]),
  choose('Aku ingin kami belajar saling mendengar','V471_S_CHOOSE_LISTEN',[('sofia','Aku ingin jujur tanpa harus mengubah siapa pun jadi sempurna.')])])
 scene(s,'V471-C05-MOON-TOGETHER','Dua Suara di Danau','moonlight_lake',[
  ('sofia','Aku nggak mau kenangan yang berat itu hilang begitu saja.'),
  ('arland','Aku juga nggak. Aku ingin kita ingat apa yang berubah setelahnya.'),
  ('narrator','Dari air muncul peta jembatan yang terbuat dari lima pecahan konstelasi.')])
 fragments=[
  ('PRESENCE','Kehadiran','Sebuah kursi kosong tampak bersebelahan dengan Arland yang akhirnya mau duduk dan mendengarkan.'),
  ('VOICE','Suara','Dua kalimat yang pernah dipendam kini terbaca tanpa saling menutupi.'),
  ('TIME','Waktu','Waktu terlambat tetap tercatat, namun jalan baru terbentuk di sebelahnya.'),
  ('SPACE','Ruang','Satu cahaya memilih diam sejenak, dan yang lain tetap menunggu tanpa mendesak.'),
  ('TOMORROW','Esok','Cahaya terakhir menyisakan ruang kosong: tidak ada yang tahu hari esok secara pasti.')]
 for k,title,desc in fragments:
  scene(s,'V471-C05-FRAGMENT-'+k,'Konstelasi '+title,'memory_bridge',[
   ('narrator',desc),('lumi','Bagian ini tidak menuntut kalian sepakat. Ia meminta kalian melihat sesuatu yang sebelumnya terlewat.')])
 # Four playable bridge alignments revisit earlier chapters, not just arbitrary collection.
 scene(s,'V471-C05-BRIDGE-C01','Urutan yang Tidak Sama','memory_bridge',[
  ('narrator','Bunga, buku, bintang. Dari sisi lain: bintang, buku, bunga. Kedua urutan membuka surat yang sama.'),
  ('sofia','Kalau awal perjalanan saja kita melihat arah berbeda, kenapa aku pernah berharap sisanya selalu sama?')])
 scene(s,'V471-C05-BRIDGE-C02','Kencan dan Ruang Memilih','memory_bridge',[
  ('narrator','Di pecahan kedua, terdapat tiga foto: kencan yang langsung terjadi, rencana yang diundur, dan hari ketika seseorang memilih sendiri.'),
  ('arland','Waktu seseorang bilang tidak, aku bisa tetap menghargainya. Perasaan tidak hilang karena sebuah jawaban.')])
 scene(s,'V471-C05-BRIDGE-C03','Tangan yang Menyiapkan Undangan','memory_bridge',[
  ('narrator','Pecahan ketiga memperlihatkan sebuah jadwal pameran dan surat setengah jadi yang belum berani dibaca.'),
  ('sofia','Dulu aku harus belajar berani meminta ditemani. Sekarang aku ingin terus bisa mengatakannya.')])
 scene(s,'V471-C05-BRIDGE-C04','Kursi yang Tidak Dihapus','memory_bridge',[
  ('narrator','Pecahan keempat membiarkan gambar kursi kosong tetap ada, meskipun di sebelahnya muncul percakapan setelah hujan.'),
  ('arland','Aku tidak boleh menggunakan permintaan maaf untuk meminta dia melupakan hari itu.'),
  ('sofia','Dan aku tidak harus memilih antara kecewa atau tetap menyayanginya.')])
 scene(s,'V471-C05-BRIDGE-C01-LISTEN','Jejak Pilihan Kafe','memory_bridge',[
  ('narrator','Pilihan mendengarkan di Kafe Senja muncul lagi: tidak semua makna harus ditemukan sendirian.')])
 scene(s,'V471-C05-BRIDGE-C01-RECORD','Jejak Mencatat','memory_bridge',[
  ('narrator','Catatan di Kafe Senja tetap dapat dibaca; beberapa pengertian memang membutuhkan waktu.')])
 scene(s,'V471-C05-BRIDGE-C01-TRACE','Jejak Menelusuri','memory_bridge',[
  ('narrator','Petunjuk yang ditelusuri di Kafe Senja menjadi tanda bahwa dua jalan bisa bertemu.')])
 scene(s,'V471-C05-BRIDGE-S-YES','Kencan yang Disetujui','memory_bridge',[
  ('sofia','Waktu itu aku mau ikut. Aku senang karena memang pilihanku sendiri.')],'sofia')
 scene(s,'V471-C05-BRIDGE-S-LATER','Hari yang Dipilih Ulang','memory_bridge',[
  ('sofia','Waktu aku minta besok, Arland menunggu. Itu salah satu cara dia menunjukkan rasa hormat.')],'sofia')
 scene(s,'V471-C05-BRIDGE-S-NO','Hari untuk Diri Sendiri','memory_bridge',[
  ('sofia','Waktu aku memilih sendiri dulu, ia tidak memaksaku. Itu tetap kenangan yang berarti.')],'sofia')
 scene(s,'V471-C05-BRIDGE-PROMISE','Undangan yang Tidak Sia-sia','memory_bridge',[
  ('narrator','Kalender galeri tetap menyimpan jam acara. Janji yang terlambat tidak hilang begitu saja.'),
  ('arland','Sofia sudah berani mengundangku. Aku ingin ingat keberaniannya, bukan cuma kegagalanku.')])
 scene(s,'V471-C05-QUIET-REVEAL','The Quiet: Bukan Musuh','memory_bridge',[
  ('narrator','Di atas jurang, foto dari hari galeri terbelah menjadi dua: proyektor yang akhirnya menyala dan kursi yang tetap kosong.'),
  ('lumi','The Quiet tidak menciptakan luka kalian. Ia terlihat saat satu bagian cerita terus dibiarkan tak terdengar.'),
  ('sofia','Jadi kenanganku tidak salah hanya karena Arland mengingat hari itu dengan cara lain?'),
  ('lumi','Tidak. Dan niat Arland tidak menghapus dampak tindakannya.'),
  ('arland','Kalau begitu, biarkan kedua sisinya tetap ada. Aku tidak ingin menghilangkan yang pernah Sofia rasakan.')],choices=[
   choose('Kita dengarkan kedua kenangan sampai selesai','V471_QUIET_LISTEN',[('sofia','Aku mau kita mendengar dua-duanya, bukan memilih satu yang paling mudah.')]),
   choose('Kita simpan luka dan perubahan yang sudah terjadi','V471_QUIET_REMEMBER',[('arland','Kita nggak perlu menutupi yang terjadi untuk melanjutkan cerita.')]),
   choose('Kita berani melangkah tanpa tahu semuanya','V471_QUIET_FUTURE',[('sofia','Kalau nanti salah lagi, kita boleh belajar lagi. Nggak harus sempurna.')])])
 scene(s,'V471-C05-BRIDGE-MEND','Jembatan Dua Versi','memory_bridge',[
  ('narrator','Potongan pertama dipasang tanpa mengubah warna aslinya. Potongan lain menerima cahaya yang berbeda.'),
  ('lumi','Kalian tidak sedang membangun satu cerita tanpa retak. Kalian sedang membangun jalan yang cukup kuat untuk kedua langkah.')])
 scene(s,'V471-C05-BRIDGE-STEP','Berjalan Saling Mendengar','memory_bridge',[
  ('narrator','Jembatan pulih, tetapi garis sambungnya tetap terlihat. Keduanya melangkah tanpa terburu-buru.'),
  ('arland','Sof, aku masih belajar. Kalau aku keliru lagi, tolong bilang, ya.'),
  ('sofia','Aku akan bilang. Dan aku ingin kamu juga cerita kalau takut atau bingung.'),
  ('narrator','Di ujung jembatan, sebuah pintu menuju Eternal Garden menyala; halaman terakhir tetap tertutup.')],flags=['V471_BRIDGE_RESTORED'])
 scene(s,'V471-C05-FINAL-A','Langkah Arland','memory_bridge',[
  ('arland','Aku dulu mengira membantu berarti selalu melakukan sesuatu. Sekarang aku tahu, kadang yang dibutuhkan adalah duduk dan hadir.')],'arland')
 scene(s,'V471-C05-FINAL-S','Langkah Sofia','memory_bridge',[
  ('sofia','Aku dulu berharap dia mengerti tanpa aku bicara. Sekarang aku tahu suaraku juga layak didengar.')],'sofia')
 scene(s,'V471-C05-HANDOFF','Kunci yang Tidak Mengunci Masa Depan','starfall_village',[
  ('lumi','Gerbang Eternal Garden akan terbuka ketika kalian siap. Halaman berikutnya belum memberikan jawaban.'),
  ('sofia','Kalau aku takut sama masa depan, boleh nggak kita jalani pelan-pelan?'),
  ('arland','Boleh. Kita nggak harus tahu akhir semua hal untuk tetap berjalan bersama.')])
 # Update end of old Chapter5 stargaze: new adventure follows; keep old step IDs for saves.
 star=steps['C05_V26_STARGAZE']['interactables'][0]['actions']
 assert any(a.get('do')=='step' and a.get('id') in ('C05_Q_ECHO','V471_C05_CLOCK_ENTRY') for a in star)
 for a in star:
  if a.get('do')=='step' and a['id'] in ('C05_Q_ECHO','V471_C05_CLOCK_ENTRY'):a['id']='V471_C05_CLOCK_ENTRY'
 # Legacy save at the old C05 ending must not skip a newly mandatory chapter arc.
 # Instead of deleting that old step ID, route it into the new clock sequence once.
 scene(s,'V471-C05-LEGACY-PATH','Ada Halaman yang Masih Tersisa','starfall_village',[
  ('narrator','Peta bintang belum lengkap. Sebuah stasiun jam kini terlihat di tepi desa.'),
  ('lumi','Kalian sudah menemukan jalan, tetapi belum mendengar semua cerita di dalamnya.'),
  ('arland','Kalau begitu kita kembali sebentar. Aku tidak mau melewati bagian yang belum dipahami.')])
 old_echo=steps['C05_Q_ECHO']['interactables'][0]
 orig=old_echo['actions']
 if len(orig)==1 and orig[0].get('do')=='if' and orig[0].get('when')=={'flags':['V471_BRIDGE_RESTORED']}:
  orig=orig[0]['then']
 old_echo['actions']=[cond('V471_BRIDGE_RESTORED',orig,[
    act('scene',id='V471-C05-LEGACY-PATH'),act('step',id='V471_C05_CLOCK_ENTRY')])]
 # 13+ new playable sequential quest stages, not just scenes.
 new=[]
 new.append(step('V471_C05_CLOCK_ENTRY','Temukan Clockwork Station dari peta yang memudar di Starfall Village',[
  it('v471_clock_gate','starfall_village',1430,890,'Masuki Clockwork Station',[
   act('music',id='cinema_clockwork_v471'),act('scene',id='V471-C05-ENTRY'),
   cine('Clockwork Station','Waktu yang terlewat tak bisa diputar kembali'),
   act('warp',area='clockwork_station',x=170,y=1090,dir='up'),
   route([act('step',id='V471_C05_CLOCK_A')],[act('step',id='V471_C05_CLOCK_S')])],icon='clock')]))
 for rt,tag in [('arland','A'),('sofia','S')]:
  keys=['GEAR-1','GEAR-2','GEAR-3'] if rt=='arland' else ['ETCH-1','ETCH-2','ETCH-3']
  positions=[(450,880),(960,360),(1480,880)]
  l=[]
  for idx,((x,y),k) in enumerate(zip(positions,keys),1):
   fl=f'V471_C05_{tag}_CLOCK_{idx}'
   l.append(it(f'v471_{tag.lower()}_clock_{idx}','clockwork_station',x,y,'Periksa bagian jam ke-'+str(idx),[
    act('scene',id='V471-C05-'+tag+'-'+k),act('sfx',id='v471_memory_chime'),act('flag',id=fl),
    act('count',id=f'v471_clock_{tag.lower()}',add=1)],rt=rt,once=fl,icon='clock'))
  new.append(step('V471_C05_CLOCK_'+tag,'Temukan tiga kenangan pada jam dari sudut pandang '+('Arland' if tag=='A' else 'Sofia'),l,
   {'counter':f'v471_clock_{tag.lower()}','count':3,'actions':[
    act('scene',id='V471-C05-CLOCK-DONE'),act('step',id='V471_C05_CLOCK_PUZZLE_'+tag)]}))
  # Native minigame stays a retriable interaction: cancellation cannot consume
  # the completed counter and leave the player with no available action.
  new.append(step('V471_C05_CLOCK_PUZZLE_'+tag,'Selesaikan puzzle jam yang boleh dibatalkan dan dicoba ulang',[
   it('v471_clock_puzzle_'+tag.lower(),'clockwork_station',960,870,'Susun ulang bagian jam',[
    act('minigame',id='v26_night_compass' if tag=='A' else 'v26_night_pages'),
    act('flag',id=f'V471_CLOCK_{tag}_DONE'),act('item',id='v471_clock_piece'),
    act('step',id='V471_C05_CLOCK_SWITCHES')],rt=rt,icon='clock')]))
 new.append(step('V471_C05_CLOCK_SWITCHES','Atur kedua sakelar untuk menggerakkan Clockwork Station',[
  it('v471_clock_switch_one','clockwork_station',680,610,'Putar sakelar kiri',[
   act('flag',id='V471_CLOCK_SWITCH_ONE'),act('count',id='v471_switches',add=1),act('sfx',id='v471_memory_chime')],once='V471_CLOCK_SWITCH_ONE',icon='clock'),
  it('v471_clock_switch_two','clockwork_station',1300,610,'Putar sakelar kanan',[
   act('flag',id='V471_CLOCK_SWITCH_TWO'),act('count',id='v471_switches',add=1),act('sfx',id='v471_memory_chime')],once='V471_CLOCK_SWITCH_TWO',icon='clock')],
  {'counter':'v471_switches','count':2,'actions':[
   act('scene',id='V471-C05-CLOCK-DONE'),act('warp',area='moonlight_lake',x=170,y=1070,dir='up'),
   route([act('step',id='V471_C05_MOON_A')],[act('step',id='V471_C05_MOON_S')])]}))
 for rt,tag in [('arland','A'),('sofia','S')]:
  acts=[act('scene',id='V471-C05-'+tag+'-REFLECT')]
  if rt=='arland':
   for fl,sc in [('V464_A_WARN','WARN'),('V464_A_SILENT','SILENT'),('V464_A_HELP','HELP')]:acts.append(cond(fl,[act('scene',id='V471-C05-MOON-C04-'+sc)]))
  else:
   for fl,sc in [('V470_S_NEED_PRESENT','PRESENT'),('V470_S_NEED_UPDATE','UPDATE'),('V470_S_NEED_LISTEN','LISTEN')]:acts.append(cond(fl,[act('scene',id='V471-C05-MOON-S-'+sc)]))
  acts += [act('scene',id='V471-C05-'+tag+'-CHOICE'),act('item',id='v471_reflection'),act('step',id='V471_C05_MOON_SHARED')]
  new.append(step('V471_C05_MOON_'+tag,'Lihat kenangan dari sudut pandang '+('Arland' if tag=='A' else 'Sofia')+' di Moonlight Lake',[
   it('v471_moon_reflect_'+tag.lower(),'moonlight_lake',890,730,'Periksa pantulan kenangan',acts,rt=rt,icon='mirror')]))
 new.append(step('V471_C05_MOON_SHARED','Lengkapi dua sisi pantulan bersama pasangan',[
  it('v471_moon_listen','moonlight_lake',620,520,'Dengarkan pantulan pasangan',[
   act('scene',id='V471-C05-MOON-MIRROR'),act('flag',id='V471_MOON_LISTEN'),act('count',id='v471_moon_part',add=1)],once='V471_MOON_LISTEN',icon='mirror'),
  it('v471_moon_note','moonlight_lake',1320,520,'Catat dua suara di Memory Book',[
   act('scene',id='V471-C05-MOON-TOGETHER'),act('flag',id='V471_MOON_NOTE'),act('count',id='v471_moon_part',add=1)],once='V471_MOON_NOTE',icon='book')],
  {'counter':'v471_moon_part','count':2,'actions':[
   act('music',id='cinema_two_sides_v471'),cine('Dua suara, satu danau','Kedua kisah layak didengarkan'),
   act('warp',area='memory_bridge',x=180,y=1090,dir='up'),act('step',id='V471_C05_BRIDGE_FRAGMENTS')]}))
 coords=[(365,1020),(680,740),(960,520),(1260,740),(1570,1020)]
 items=[]
 for (k,title,desc),(x,y) in zip(fragments,coords):
  fl='V471_FRAGMENT_'+k
  items.append(it('v471_fragment_'+k.lower(),'memory_bridge',x,y,'Pulihkan konstelasi '+title,[
   act('scene',id='V471-C05-FRAGMENT-'+k),act('sfx',id='v471_memory_chime'),
   act('flag',id=fl),act('item',id='v471_star_fragment'),act('count',id='v471_fragments',add=1)],once=fl,icon='star'))
 new.append(step('V471_C05_BRIDGE_FRAGMENTS','Kumpulkan lima fragmen konstelasi di Memory Bridge',items,
  {'counter':'v471_fragments','count':5,'actions':[
   act('toast',text='Lima konstelasi terkumpul. Selaraskan empat ingatan pada jembatan.'),act('step',id='V471_C05_BRIDGE_SEQUENCE')]}))
 # Four-stage bridge puzzle follows real memories from Chapters 1–4.
 sequences=[]
 for i,(part,x,y) in enumerate([('C01',440,650),('C02',710,490),('C03',1240,490),('C04',1500,650)],1):
  actions=[]
  if i==1:
   for flag,label in [('V467_C01_CHOOSE_LISTEN','LISTEN'),('V467_C01_CHOOSE_RECORD','RECORD'),('V467_C01_CHOOSE_TRACE','TRACE')]:
    actions.append(cond(flag,[act('scene',id='V471-C05-BRIDGE-C01-'+label)]))
  if i==2:
   for flag,label in [('V468_S_REPLY_YES','YES'),('V468_S_REPLY_LATER','LATER'),('V468_S_REPLY_NO','NO')]:
    actions.append(cond(flag,[act('scene',id='V471-C05-BRIDGE-S-'+label)]))
  if i==3:
   actions.append(cond('V469_GALLERY_INVITE_DONE',[act('scene',id='V471-C05-BRIDGE-PROMISE')]))
  actions += [act('scene',id='V471-C05-BRIDGE-'+part),act('sfx',id='v471_memory_chime'),
              act('flag',id='V471_BRIDGE_PANEL_'+part),act('count',id='v471_panels',add=1)]
  sequences.append(it('v471_bridge_panel_'+str(i),'memory_bridge',x,y,'Susun ingatan Bab '+str(i),actions,
                      once='V471_BRIDGE_PANEL_'+part,icon='book'))
 new.append(step('V471_C05_BRIDGE_SEQUENCE','Selaraskan empat kenangan dari Chapter 1–4',sequences,
  {'counter':'v471_panels','count':4,'actions':[act('step',id='V471_C05_BRIDGE_PUZZLE')]}))
 new.append(step('V471_C05_BRIDGE_PUZZLE','Selesaikan puzzle urutan kenangan di jembatan (boleh dicoba ulang)',[
  it('v471_bridge_alignment','memory_bridge',960,690,'Selaraskan dua urutan kisah',[
   act('minigame',id='starmap_bukit'),act('flag',id='V471_BRIDGE_ALIGNED'),
   act('step',id='V471_C05_QUIET_TRUTH')],icon='book')]))
 new.append(step('V471_C05_QUIET_TRUTH','Temui Penjaga Lentera dan pahami dua sisi kenangan',[
  it('v471_lumi_truth','memory_bridge',960,420,'Bicara dengan Penjaga Lentera',[
   act('music',id='cinema_quiet_reveal_v471'),cine('The Quiet','Bukan musuh. Bagian cerita yang belum didengarkan',1.33),
   act('scene',id='V471-C05-QUIET-REVEAL'),act('flag',id='V471_QUIET_REVEALED'),
   act('item',id='v471_two_views'),act('step',id='V471_C05_BRIDGE_RESTORE')],icon='book')]))
 new.append(step('V471_C05_BRIDGE_RESTORE','Sambungkan dua sisi Memory Bridge tanpa menghapus retaknya',[
  it('v471_bridge_mend','memory_bridge',700,480,'Pasang pecahan pertama',[
   act('scene',id='V471-C05-BRIDGE-MEND'),act('flag',id='V471_BRIDGE_MEND'),act('sfx',id='v471_memory_chime')],once='V471_BRIDGE_MEND',icon='star'),
  it('v471_bridge_step','memory_bridge',1290,480,'Letakkan dua kenangan berdampingan',[
   act('scene',id='V471-C05-BRIDGE-STEP'),act('flag',id='V471_BRIDGE_RESTORED'),act('item',id='v471_bridge_memory'),act('step',id='V471_C05_FINAL_WALK')],once='V471_BRIDGE_RESTORED',need='V471_BRIDGE_MEND',icon='star')]))
 new.append(step('V471_C05_FINAL_WALK','Melangkah bersama dan kembali ke Starfall Village',[
  it('v471_final_walk','memory_bridge',960,940,'Berjalan berdua ke gerbang berikutnya',[
   route([act('scene',id='V471-C05-FINAL-A')],[act('scene',id='V471-C05-FINAL-S')]),
   act('scene',id='V471-C05-HANDOFF'),act('warp',area='starfall_village',x=60,y=640,dir='right'),
   act('step',id='C05_Q_ECHO')],icon='star')]))
 # Three new walkable locations. Door chain supports exploration; no automatic instant re-trigger.
 def area(name,image,music,ambient,spawn):
  return {'name':name,'image':'maps/'+image+'.png','w':1920,'h':1280,'music':music,'ambient':ambient,
   'spawn':spawn,'indoor':False,'walls':[[0,0,20,1280],[1900,0,20,1280],[0,0,1920,20],[0,1260,1920,20]],
   'ellipses':[],'props':[],'gates':[],'animals':[],'water':[],'doors':[],'examine':[],
   'storyVersion':'v471_chapter5_original','visualStyle':'memory_two_perspectives_v471'}
 def door(key,rect,to,tx,ty,label,lock=None):
  d={'id':key,'rect':rect,'to':to,'tx':tx,'ty':ty,'label':label,'dir':'up'}
  if lock:d['locked']=lock
  return d
 clock=area('Clockwork Station — Waktu yang Tidak Bisa Kembali','clockwork_station','star','magic_chimes',[170,1090])
 moon=area('Moonlight Lake — Dua Pantulan','moonlight_lake','memory','lake_water',[170,1070])
 bridge=area('Memory Bridge — Lima Konstelasi','memory_bridge','star','magic_chimes',[180,1090])
 clock['doors']=[door('clock_to_village',[80,1200,130,55],'starfall_village',1250,920,'Kembali ke Starfall Village'),
                 door('clock_to_moon',[1680,60,140,60],'moonlight_lake',190,1050,'Ke Moonlight Lake',[{'steps':['V471_C05_CLOCK_A','V471_C05_CLOCK_S','V471_C05_CLOCK_SWITCHES'],'text':'Kedua sakelar harus diatur dahulu.'}])]
 moon['doors']=[door('moon_to_clock',[65,1195,145,65],'clockwork_station',260,1090,'Kembali ke Clockwork Station'),
                door('moon_to_bridge',[1650,65,145,60],'memory_bridge',185,1090,'Ke Memory Bridge',[{'steps':['V471_C05_MOON_A','V471_C05_MOON_S','V471_C05_MOON_SHARED'],'text':'Dengarkan dua pantulan dahulu.'}])]
 bridge['doors']=[door('bridge_to_moon',[65,1195,140,65],'moonlight_lake',250,1090,'Kembali ke Moonlight Lake'),
                  door('bridge_to_village',[1700,60,120,60],'starfall_village',1250,920,'Kembali ke Desa',[{'steps':['V471_C05_BRIDGE_FRAGMENTS','V471_C05_QUIET_TRUTH','V471_C05_BRIDGE_RESTORE'],'text':'Kenangan belum dipulihkan.'}])]
 m['areas']['clockwork_station']=clock;m['areas']['moonlight_lake']=moon;m['areas']['memory_bridge']=bridge
 village=m['areas']['starfall_village'];village['doors']=[d for d in village.get('doors',[]) if d.get('id')!='v471_village_to_clock']
 village['doors'].append(door('v471_village_to_clock',[1700,1040,140,70],'clockwork_station',190,1070,'Clockwork Station',[
  {'when':{'maxChapter':'C04'},'text':'Mesin waktu belum muncul.'}]))
 # Save rescue when loading existing C05 end-of-village step still works; preserve original ID.
 # Fixed item catalogue keys preserve save compatibility.
 b['items'].update({
  'v471_clock_piece':{'name':'Komponen Jam Kenangan','desc':'Roda yang bergerak lagi tanpa memutar kembali waktu yang terlewat.','icon':'items/v471_c05_clock.png'},
  'v471_reflection':{'name':'Pantulan Dua Sisi','desc':'Satu permukaan danau menyimpan dua versi rasa.','icon':'items/v471_c05_mirror.png'},
  'v471_star_fragment':{'name':'Pecahan Konstelasi','desc':'Lima cahaya yang tidak menghapus bagian yang terluka.','icon':'items/v471_c05_star.png'},
  'v471_two_views':{'name':'Dua Sisi Hari Galeri','desc':'Niat baik dan perasaan terluka tetap sama-sama nyata.','icon':'items/v471_c05_book.png'},
  'v471_bridge_memory':{'name':'Jembatan Dua Versi','desc':'Jembatan pulih, tetapi sambungannya tetap terlihat.','icon':'items/v471_c05_star.png'}})
 b['entries']=[x for x in b['entries'] if not x['id'].startswith('v471_c05_')]
 for key,title,desc,flag,icon,rt,typ in [
  ('clock_a','Waktu yang Diakui','Arland belajar membedakan niat dan dampaknya.','V471_CLOCK_A_DONE','clock','arland','fictional_memory'),
  ('clock_s','Keberanian di Hari Galeri','Sofia mengingat presentasi yang tetap berhasil.','V471_CLOCK_S_DONE','clock','sofia','fictional_memory'),
  ('moon_a','Arland Memilih Hadir','Masa lalu tidak diulang, tetapi pilihan esok dapat berubah.','V471_A_CHOOSE_TIME','mirror','arland','optional_story_branch'),
  ('moon_s','Sofia Boleh Bicara','Sofia berhak menyampaikan kebutuhan dan perasaannya.','V471_S_CHOOSE_PRESENT','mirror','sofia','optional_story_branch'),
  ('bridge','Jembatan Dua Suara','Kenangan tidak harus sama untuk tetap menjadi milik bersama.','V471_BRIDGE_RESTORED','star','shared','fictional_memory'),
  ('truth','The Quiet','The Quiet tidak menciptakan luka; ia memperlihatkan yang tidak terdengar.','V471_QUIET_REVEALED','book','shared','fictional_memory')]:
  mem(b,'v471_c05_'+key,title,desc,flag,icon,rt,typ)
 for k,title in [('PRESENCE','Kehadiran'),('VOICE','Suara'),('TIME','Waktu'),('SPACE','Ruang'),('TOMORROW','Esok')]:
  mem(b,'v471_c05_fragment_'+k.lower(),'Konstelasi '+title,'Salah satu dari lima aspek hubungan yang tidak boleh dihapus.','V471_FRAGMENT_'+k,'star')
 for typ,flags,rt in [('a',['TIME','ASK','HELP'],'arland'),('s',['PRESENT','SPACE','LISTEN'],'sofia')]:
  for fl in flags:mem(b,'v471_c05_choice_'+typ+'_'+fl.lower(),'Pilihan untuk Hari Esok','Jalan yang dipilih mengubah cara menjalin kepercayaan.','V471_'+typ.upper()+'_CHOOSE_'+fl,'book',rt,'optional_story_branch')
 for fl in ('LISTEN','REMEMBER','FUTURE'):
  mem(b,'v471_c05_quiet_'+fl.lower(),'Memahami The Quiet','Satu interpretasi tanpa menghapus versi lain.','V471_QUIET_'+fl,'book','shared','optional_story_branch')
 q['steps']=[x for x in q['steps'] if not x['id'].startswith('V471_C05_')]+new
 for name,obj in [('story.json',s),('quests.json',q),('maps.json',m),('memory_book.json',b)]:
  (DATA/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('PASS: Chapter5 3 new areas, route-specific clocks/reflection, 5 constellation fragments, Quiet reveal and branch memory, %d steps'%len(new))
if __name__=='__main__':patch()
