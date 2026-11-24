#!/usr/bin/env python3
"""EPILOGUE v4.7.3: playable memory walk, bittersweet lakeside ending and dual-route bonus.

Idempotent against draft source and safe for older saves: existing step and scene IDs are retained,
while EPI_FEST_LEPAS now enters a real memory walk before the existing chapter-end action.
"""
import json
from pathlib import Path
from copy import deepcopy
R=Path(__file__).resolve().parents[1];D=R/'android/assets/data'; V='V473'

def ac(do,**kw):return dict(do=do,**kw)
def ln(w,t,e='neutral'):return dict(s=w,t=t,e=e)
def route(a,b):return ac('if',when={'route':'arland'},then=a,**{'else':b})
def fl(flag,acts):return ac('if',when={'flags':[flag]},then=acts,**{'else':[]})
def scene(db,key,title,place,dialogues,r='shared',choices=None,flags=None):
 db['scenes'][key]={'title':title,'chapter':'EPI','route':r,'location':place,'trigger':'v4.7.3 Epilogue chapter playable',
                    'lines':[ln(*row) for row in dialogues],'choices':choices or [],'flags':flags or []}
def choice(text,flag,response):return {'text':text,'flags':[flag],'byRoute':{r:[ln(*x) for x in response] for r in ('arland','sofia')}}
def it(id,place,x,y,label,actions,**extra):
 obj={'id':id,'area':place,'x':x,'y':y,'r':105,'label':label,'actions':actions};obj.update(extra);return obj
def step(id,description,items,**extra):
 obj={'id':id,'chapter':'EPI','quest':'Q_V473_EPI_MEMORY_WALK','objective':{'arland':description,'sofia':description},'interactables':items};obj.update(extra);return obj

def apply():
 s=json.loads((D/'story.json').read_text());q=json.loads((D/'quests.json').read_text());m=json.loads((D/'maps.json').read_text());b=json.loads((D/'memory_book.json').read_text()); steps={x['id']:x for x in q['steps']}
 assert all(x in steps for x in ('EPI_FEST_LEPAS','EPI_FREE','C06_FINAL'))
 assert 'V472-C06-HALL-INTRO' in s['scenes'],'Apply Chapter6 before Epilogue'
 # Recover the original finale callbacks on reapply: no loss or duplication.
 fest=next(x for x in steps['EPI_FEST_LEPAS']['interactables'] if x['id']=='fest_release')
 current=fest['actions']; oldfinal=steps.get('V473_EPI_FINALE')
 if oldfinal:
  oldactions=oldfinal['interactables'][0]['actions']
  coda=[deepcopy(a) for a in oldactions if a.get('v473_moved_coda')]
  assert coda and any(a.get('id')=='V465-EPI-LAKE' for a in coda),'Lost legacy Epilogue coda'
 else:
  i=next(i for i,a in enumerate(current) if a.get('do')=='music' and a.get('id')=='cinema_letter_tomorrow')
  coda=[dict(deepcopy(a),v473_moved_coda=True) for a in current[i:-2]]
  assert current[-2]['do']=='chapterEnd' and current[-1]['do']=='step'
 # Remove only v473-owned objects; older IDs/saves remain valid.
 s['scenes']={k:v for k,v in s['scenes'].items() if not k.startswith('V473-')}
 q['steps']=[x for x in q['steps'] if not x['id'].startswith('V473_EPI_')]
 b['entries']=[x for x in b['entries'] if not x['id'].startswith('v473_')]
 for k in list(b['items']):
  if k.startswith('v473_'):del b['items'][k]
 s.setdefault('meta',{})['epilogueOverhaul']='v4.7.3: optional historic festival; playable post-festival memory walk, lakeside canon coda, dual-route two-letters chapter'

 scene(s,'V473-EPI-FEST-FAREWELL','Setelah Lampion Terbang','taman_kota',[
  ('narrator','Lentera semakin jauh. Musik festival terdengar perlahan dari belakang, tetapi Arland dan Sofia belum ingin pulang.'),
  ('sofia','Kita bisa lihat lagi tempat-tempat kecil yang bikin semua ini terasa nyata?'),
  ('arland','Boleh. Kali ini nggak ada kejutan. Aku cuma ingin jalan di samping kamu.'),
  ('narrator','Pemain bebas berjalan menuju lokasi kenangan berikutnya. Tidak ada hitung mundur atau hukuman.')])
 scene(s,'V473-EPI-PLAZA','Plaza yang Tidak Lagi Sama','plaza',[
  ('narrator','Tempat mereka bertukar bunga kertas dan kartu pos masih ramai. Tidak ada portal atau cahaya yang mendesak mereka pergi.'),
  ('sofia','Dulu aku deg-degan waktu mau menyerahkan kartu itu. Kupikir kamu bakal langsung bisa baca pikiranku.'),
  ('arland','Aku malah sibuk ngelihatin bunga kertas yang nyaris lepas pitanya.'),
  ('sofia','Ternyata kita sama-sama gugup, ya.')],choices=[
   choice('Ingat hadiah yang bentuknya tidak sempurna','V473_PLAZA_GIFT',[
     ('arland','Aku masih ingat lipatannya yang miring.'),('sofia','Aku ingat kamu mengulurkan tangan sambil senyum malu.')]),
   choice('Ingat keberanian untuk bertemu','V473_PLAZA_COURAGE',[
     ('sofia','Aku datang walau takut kata-kataku salah.'),('arland','Untung kamu datang. Kita jadi punya hari-hari setelahnya.')])])
 scene(s,'V473-EPI-PLAZA-A','Catatan di Belakang Bunga','plaza',[
  ('arland','Aku dulu ingin semua hadiah terlihat hebat. Sekarang aku ingin bisa hadir bahkan saat nggak membawa apa-apa.'),
  ('sofia','Aku senang dengarnya. Tapi kamu tetap boleh bikin bunga miring lagi, kok.')],'arland')
 scene(s,'V473-EPI-PLAZA-S','Kartu Pos yang Masih Dibawa','plaza',[
  ('sofia','Aku bisa tulis yang aku rasakan, tapi bilang langsung masih membuatku gugup.'),
  ('arland','Aku mau denger, walau kamu harus mengulangnya pelan-pelan.')],'sofia')
 scene(s,'V473-EPI-CAFE','Surat yang Dibaca Berdua','cafe',[
  ('narrator','Kotak surat Kafe Senja tetap berada di sudut yang sama. Di belakang bar, Kak Raka sibuk menata gelas.'),
  ('arland','Dulu aku lihat bunga duluan. Aku yakin petunjukku paling jelas.'),
  ('sofia','Aku malah lihat bintang. Kita hampir melewatkan surat yang sama.'),
  ('arland','Untung akhirnya kita mau membandingkan catatan, bukan saling membuktikan siapa benar.')],choices=[
   choice('Dengarkan ulang ingatan pasangan','V473_CAFE_LISTEN',[
     ('sofia','Ternyata kamu lebih gugup daripada yang kukira.'),('arland','Dan ternyata kamu sudah punya petunjuk yang belum kulihat.')]),
   choice('Tulis dua versi dalam satu halaman','V473_CAFE_TWO_SIDES',[
     ('arland','Boleh nggak dua kalimat kita beda tapi sama-sama disimpan?'),('sofia','Itu kan inti bukunya dari awal.')])])
 scene(s,'V473-EPI-CAFE-A','Arland dan Surat Lama','cafe',[
  ('arland','Aku mau belajar bertanya dulu, bukan buru-buru menunjukkan jawabanku.'),
  ('sofia','Kadang jawaban yang lain justru bikin suratnya lengkap.')],'arland')
 scene(s,'V473-EPI-CAFE-S','Sofia dan Pembatas Bintang','cafe',[
  ('sofia','Aku nggak mau terus menyembunyikan pendapatku hanya karena beda.'),
  ('arland','Kamu nggak harus setuju denganku. Kita masih bisa jalan berdua.')],'sofia')
 scene(s,'V473-EPI-GALLERY','Dua Gambar yang Tetap Ada','galeri_komunitas',[
  ('narrator','Di dekat jendela, Sofia melihat gambar kursi kosong yang tidak pernah ia buang.'),
  ('sofia','Aku masih ingat rasanya menoleh ke pintu waktu kamu nggak datang.'),
  ('arland','Aku juga ingat apa yang kulewatkan. Kejutanku tidak membuat janji itu kembali.'),
  ('sofia','Aku nggak mau pura-pura hari itu nggak terjadi.'),
  ('arland','Kita nggak perlu menghapusnya. Ada hal yang harus kujaga setelah hari itu.')],choices=[
   choice('Biarkan gambar kursi kosong tetap dipajang','V473_GALLERY_KEEP',[
    ('sofia','Gambar ini juga menceritakan keberanianku tampil meski kecewa.'),('arland','Aku bangga kamu tetap menyelesaikan presentasinya.')]),
   choice('Letakkan gambar kebersamaan di sebelahnya','V473_GALLERY_PAIR',[
    ('sofia','Sekarang ada dua gambar. Yang sedih nggak harus hilang.'),('arland','Dan yang baru bukan alasan buat melupakan janji.')])])
 scene(s,'V473-EPI-GALLERY-A','Arland di Depan Kursi','galeri_komunitas',[
  ('arland','Hari itu aku memilih memperbaiki proyektor daripada datang. Aku nggak akan menyebutnya sekadar telat.'),
  ('sofia','Makasih sudah berani mengakuinya. Aku nggak minta kamu selalu sempurna.')],'arland')
 scene(s,'V473-EPI-GALLERY-S','Sofia di Depan Lukisan','galeri_komunitas',[
  ('sofia','Hari itu aku sedih. Tapi keberanianku berdiri di depan orang-orang juga nyata.'),
  ('arland','Iya, Sof. Itu milikmu. Aku ingin merayakannya tanpa mengambil alih.')],'sofia')
 for flag,text in (
  ('V468_S_REPLY_YES','Kencan itu berawal dari jawaban iya yang kamu pilih sendiri.'),
  ('V468_S_REPLY_LATER','Kamu bilang besok saja, dan kita akhirnya belajar bahwa menunggu bukan menolak selamanya.'),
  ('V468_S_REPLY_NO','Kamu pernah bilang tidak, lalu kita belajar bahwa batasan bukan berarti tidak sayang.'),
  ('V470_S_NEED_PRESENT','Aku ingin hadir secara nyata, bukan menggantinya dengan kejutan.'),
  ('V470_S_NEED_UPDATE','Aku ingin memberi kabar sebelum semuanya terlambat.'),
  ('V470_S_NEED_LISTEN','Aku ingin mendengar perasaanmu sampai selesai.'),
  ('V471_QUIET_REVEALED','The Quiet memudar ketika dua suara akhirnya diberi tempat.')
 ):
  scene(s,'V473-EPI-RECALL-'+flag,'Pilihan yang Masih Diingat','riverside', [('narrator',text)])
 scene(s,'V473-EPI-LAKE-PHOTO','Foto yang Tidak Perlu Diulang','riverside',[
  ('narrator','Di tepi danau, foto photobooth jatuh dari halaman buku. Ada lentera kecil di sudutnya.'),
  ('arland','Ingat foto pertama yang nggak sesuai rencana?'),
  ('sofia','Iya. Aku malah suka karena di situlah kita ketawa beneran.'),
  ('narrator','Pemain boleh meneliti detail kenangan tanpa mengulang kencan atau mengambil fotonya kembali.')])
 scene(s,'V473-EPI-LAKE-LETTER-A','Surat yang Tidak Dibacakan Keras','riverside',[
  ('narrator','Arland membaca kembali catatannya tanpa mencoba mengubah bagian yang salah.'),
  ('arland','Aku masih belajar. Tapi aku pengen terus hadir ketika kamu membutuhkan aku.'),
  ('sofia','Kita belajar bareng, ya. Kalau kamu bingung, bilang aja.')],'arland')
 scene(s,'V473-EPI-LAKE-LETTER-S','Halaman yang Tetap Dibuka','riverside',[
  ('narrator','Sofia membuka sketsa dua kursi: yang pernah kosong, dan yang kini ditempati bersama.'),
  ('sofia','Aku nggak mau kehilangan keberanian untuk cerita kalau ada yang bikin sedih.'),
  ('arland','Dan aku mau mendengar, termasuk ketika jawabannya nggak seperti yang kubayangkan.')],'sofia')
 scene(s,'V473-EPI-LAKE-END','Banyak Hari yang Belum Ditulis','riverside',[
  ('narrator','Langit berubah jingga. Tidak ada portal yang mengajak mereka pergi. Tidak ada jawaban yang harus dipilih dengan terburu-buru.'),
  ('sofia','Land, halaman terakhirnya masih kosong.'),
  ('arland','Berarti masih banyak yang bisa kita tulis.'),
  ('sofia','Nggak perlu buru-buru, ya?'),
  ('arland','Nggak. Kita masih punya banyak hari.'),
  ('narrator','Mereka duduk berdampingan. Kamera pelan-pelan menjauh; suara air dan musik menjadi penutup.')])
 scene(s,'V473-EPI-OLD-SAVE','Kenangan yang Berlanjut','riverside',[
  ('narrator','Mereka belum mengumpulkan semua catatan baru, tetapi masih bisa menikmati sore dan mengisi halaman berikutnya.'),
  ('sofia','Kita nggak harus buru-buru mengingat semuanya sekaligus.'),('arland','Kita bisa cerita lagi kapan pun.')])
 scene(s,'V473-EPI-POST-PLAZA','Bunga untuk Hari Biasa','plaza',[
  ('sofia','Hari ini kamu nggak bawa kejutan apa-apa?'),('arland','Cuma waktu untuk jalan sama kamu.'),
  ('sofia','Itu justru rencana bagus.')])
 scene(s,'V473-EPI-POST-CAFE','Kopi dan Dua Sudut Pandang','cafe',[
  ('arland','Kamu ingat surat itu dari bagian yang mana?'),('sofia','Dari saat kamu akhirnya mau denger versi aku.'),
  ('arland','Besok kalau kita berbeda pendapat lagi, tolong ingatkan aku ya.')])
 scene(s,'V473-EPI-POST-LAKE','Sore yang Tidak Hilang','riverside',[
  ('narrator','Air danau berkilau biasa saja. Itulah yang membuat hari ini terasa berbeda.'),
  ('sofia','Kita nggak perlu petualangan ajaib setiap hari.'),('arland','Iya. Duduk di sini juga sudah cukup.')])
 scene(s,'V473-EPI-BONUS-OPEN','The Other Side of the Page','ruang_dua_surat',[
  ('narrator','Setelah kedua kisah ditamatkan, sebuah ruang kecil terbuka di galeri. Dua meja menunggu di dalamnya.'),
  ('lumi','Tak satu pun surat mengubah apa yang terjadi. Bacalah keduanya agar kalian bisa melihat hal yang terlewat.'),
  ('narrator','Buku ini tidak memilih siapa yang paling benar.')])
 scene(s,'V473-EPI-BONUS-LETTER-A','Surat yang Tak Pernah Dikirim Arland','ruang_dua_surat',[
  ('narrator','Di atas meja pertama, ada rancangan surat dengan beberapa kalimat dicoret.'),
  ('arland','Aku takut terlihat nggak bisa ngasih yang terbaik. Jadi aku sibuk membetulkan sesuatu yang bukan masalahnya.'),
  ('arland','Sof, kalau nanti aku lupa bertanya, tolong bilang. Aku mau belajar mendengarkan sebelum keadaan jadi sunyi.'),
  ('narrator','Tulisan di akhir surat berbunyi: hadir lebih penting daripada selalu punya jawaban.')])
 scene(s,'V473-EPI-BONUS-LETTER-S','Surat yang Tak Pernah Dibacakan Sofia','ruang_dua_surat',[
  ('narrator','Meja kedua menyimpan halaman buku sketsa dengan gambar pintu galeri yang tertutup.'),
  ('sofia','Aku tetap ingin kamu datang, meski tahu kamu berniat baik. Dua perasaan itu bisa ada bersamaan.'),
  ('sofia','Aku juga ingin belajar meminta ditemani tanpa takut dikira merepotkan.'),
  ('narrator','Di belakang halaman tercatat: keberanian tak berkurang meski tak disaksikan orang yang ditunggu.')])
 scene(s,'V473-EPI-BONUS-CHOICE','Dua Surat, Satu Hari','ruang_dua_surat',[
  ('narrator','Kedua surat diletakkan berdampingan. Di antaranya masih ada ruang kosong.'),
  ('sofia','Dulu kita pikir cuma ada satu cerita yang paling benar.'),
  ('arland','Sekarang kita tahu dua cerita bisa lengkap tanpa harus sama persis.'),
  ('lumi','Kenangan dua sisi terbuka. Esok tetap milik kalian, bukan milik buku.')],choices=[
   choice('Simpan kedua surat tanpa menyunting isinya','V473_BONUS_KEEP',[
    ('sofia','Kita simpan apa adanya.'),('arland','Biar besok kita masih bisa belajar darinya.')]),
   choice('Tambahkan halaman kosong untuk cerita selanjutnya','V473_BONUS_NEW_PAGE',[
    ('arland','Aku ingin masih ada ruang buat berubah.'),('sofia','Kita tulis pelan-pelan, sama-sama.')])])

 new=[]
 new.append(step('V473_EPI_PLAZA','Kembali ke Plaza Kota dan kenang pertemuan pertama',[
  it('v473_plaza_memory','plaza',960,640,'Bunga kertas dan kartu pos',[
    ac('scene',id='V473-EPI-PLAZA'),route([ac('scene',id='V473-EPI-PLAZA-A')],[ac('scene',id='V473-EPI-PLAZA-S')]),
    ac('flag',id='V473_EPI_PLAZA_DONE'),ac('item',id='v473_legacy_page'),ac('sfx',id='page'),ac('step',id='V473_EPI_CAFE')],sprite={'image':'items/v473_page.png','x':960,'y':625,'bob':True})]))
 new.append(step('V473_EPI_CAFE','Datang ke Kafe Senja dan baca kembali surat dua sisi',[
  it('v473_cafe_memory','cafe',410,340,'Surat dua sisi di meja kafe',[
    ac('scene',id='V473-EPI-CAFE'),route([ac('scene',id='V473-EPI-CAFE-A')],[ac('scene',id='V473-EPI-CAFE-S')]),
    ac('flag',id='V473_EPI_CAFE_DONE'),ac('sfx',id='page'),ac('step',id='V473_EPI_GALLERY')],sprite={'image':'items/v473_letter.png','x':410,'y':325,'bob':True})]))
 new.append(step('V473_EPI_GALLERY','Kembali ke Galeri Komunitas dan dengarkan dua sisi hari itu',[
  it('v473_gallery_memory','galeri_komunitas',440,390,'Dua gambar di samping kursi',[
    ac('music',id='cinema_homecoming_v473'),ac('cine',cmds=[{'c':'bars','on':True,'t':.25},{'c':'shot','focus':'partner','zoom':1.25,'frame':'intimate','t':1.35,'bars':False},{'c':'caption','text':'The Empty Seat','sub':'Tidak semua kenangan harus dihapus','t':2.5},{'c':'bars','on':False,'t':.3}]),
    ac('scene',id='V473-EPI-GALLERY'),route([ac('scene',id='V473-EPI-GALLERY-A')],[ac('scene',id='V473-EPI-GALLERY-S')]),
    ac('flag',id='V473_EPI_GALLERY_DONE'),ac('sfx',id='v473_letter_fold'),ac('step',id='V473_EPI_LAKE_MEMORIES')],sprite={'image':'items/v473_chair.png','x':440,'y':370,'bob':True})]))
 new.append(step('V473_EPI_LAKE_MEMORIES','Pergi ke tepi danau; lihat foto dan baca surat bersama',[
  it('v473_lake_photo','riverside',820,600,'Foto kencan lama',[
    ac('scene',id='V473-EPI-LAKE-PHOTO'),ac('flag',id='V473_LAKE_PHOTO'),ac('sfx',id='page')],hideIfFlag='V473_LAKE_PHOTO',sprite={'image':'items/v473_photo.png','x':820,'y':580,'bob':True}),
  it('v473_lake_letter','riverside',1030,600,'Surat dari Eternal Garden',[
    route([ac('scene',id='V473-EPI-LAKE-LETTER-A')],[ac('scene',id='V473-EPI-LAKE-LETTER-S')]),
    ac('flag',id='V473_LAKE_LETTER'),ac('sfx',id='v473_letter_fold')],hideIfFlag='V473_LAKE_LETTER',sprite={'image':'items/v473_letter.png','x':1030,'y':580,'bob':True}),
  it('v473_lake_ready','riverside',950,770,'Duduk bersama setelah mengingat semuanya',[
    ac('scene',id='V473-EPI-LAKE-PHOTO') if False else ac('step',id='V473_EPI_FINALE')],when={'flags':['V473_LAKE_PHOTO','V473_LAKE_LETTER']},sprite={'image':'items/v473_sunset.png','x':950,'y':760,'bob':True})]))
 # All pre-v473 callbacks happen at the *real* quiet lake finale, once, in their original order.
 finale=[ac('music',id='cinema_homecoming_v473'),ac('cine',cmds=[
  {'c':'bars','on':True,'t':.4},{'c':'shot','focus':'partner','zoom':1.13,'frame':'wide','t':2,'bars':False},
  {'c':'caption','text':'To Be Continued','sub':'Kita masih punya banyak hari','t':4.3},
  {'c':'fx','kind':'petals','on':'player','t':3.6},{'c':'bars','on':False,'t':.5}]),
  ac('scene',id='V473-EPI-LAKE-END')]
 for flag in ('V468_S_REPLY_YES','V468_S_REPLY_LATER','V468_S_REPLY_NO','V470_S_NEED_PRESENT',
              'V470_S_NEED_UPDATE','V470_S_NEED_LISTEN','V471_QUIET_REVEALED'):
  finale.append(fl(flag,[ac('scene',id='V473-EPI-RECALL-'+flag)]))
 for flag in ('V473_PLAZA_GIFT','V473_PLAZA_COURAGE','V473_CAFE_LISTEN','V473_CAFE_TWO_SIDES','V473_GALLERY_KEEP','V473_GALLERY_PAIR'):
  finale.append(fl(flag,[ac('toast',text='Kenangan keputusan lama tersimpan dalam halaman baru.')]))
 finale.extend(coda)
 finale += [ac('flag',id='V473_EPI_COMPLETE'),ac('chapterEnd',chapter='EPI'),ac('step',id='EPI_FREE')]
 new.append(step('V473_EPI_FINALE','Duduk bersama di tepi danau untuk menutup perjalanan',[
  it('v473_final_bench','riverside',950,770,'Halaman terakhir yang masih kosong',finale,
     sprite={'image':'items/v473_sunset.png','x':950,'y':748,'bob':True})]))
 new.append(step('V473_EPI_BONUS_ENTER','Masuk Ruang Dua Surat; baca dua sudut pandang yang belum pernah dibuka',[
  it('v473_bonus_arland','ruang_dua_surat',300,370,'Surat Arland yang belum terkirim',[
    ac('scene',id='V473-EPI-BONUS-LETTER-A'),ac('flag',id='V473_BONUS_A'),ac('count',id='v473_letters',add=1),ac('sfx',id='v473_letter_fold')],hideIfFlag='V473_BONUS_A',sprite={'image':'items/v473_letter.png','x':300,'y':348,'bob':True}),
  it('v473_bonus_sofia','ruang_dua_surat',650,370,'Surat Sofia yang belum dibacakan',[
    ac('scene',id='V473-EPI-BONUS-LETTER-S'),ac('flag',id='V473_BONUS_S'),ac('count',id='v473_letters',add=1),ac('sfx',id='v473_letter_fold')],hideIfFlag='V473_BONUS_S',sprite={'image':'items/v473_letter.png','x':650,'y':348,'bob':True})],counter='v473_letters',counterMax=2,
  complete={'counter':'v473_letters','count':2,'actions':[ac('step',id='V473_EPI_BONUS_CLOSE')]}))
 new.append(step('V473_EPI_BONUS_CLOSE','Satukan dua surat tanpa menghapus salah satunya',[
  it('v473_bonus_page','ruang_dua_surat',480,450,'Dua surat, satu halaman kosong',[
   ac('music',id='cinema_dual_letters_v473'),ac('cine',cmds=[
     {'c':'bars','on':True,'t':.3},{'c':'cam','x':480,'y':430,'zoom':1.3,'t':1.3},
     {'c':'caption','text':'The Other Side of the Page','sub':'Dua versi, satu tempat pulang','t':3},
     {'c':'bars','on':False,'t':.3}]),ac('scene',id='V473-EPI-BONUS-CHOICE'),
   ac('item',id='v473_two_letters'),ac('flag',id='V473_BONUS_DONE'),
   ac('warp',area='galeri_komunitas',x=700,y=540,dir='down'),ac('step',id='EPI_FREE')],
   when={'flags':['V473_BONUS_A','V473_BONUS_S']},sprite={'image':'items/v473_page.png','x':480,'y':420,'bob':True})]))
 # Preserve old Festival activity and the ending's original cutscene; insert actual traversal before terminal coda.
 fest['actions']=[deepcopy(a) for a in current[:4]]+[ac('scene',id='V473-EPI-FEST-FAREWELL'),ac('step',id='V473_EPI_PLAZA')]
 free=steps['EPI_FREE']
 free['interactables']=[it for it in free.get('interactables',[]) if not it['id'].startswith('v473_')]
 for key,place,x,y,sceneid,flag in [
   ('v473_post_plaza','plaza',980,630,'V473-EPI-POST-PLAZA','V473_POST_PLAZA'),
   ('v473_post_cafe','cafe',425,350,'V473-EPI-POST-CAFE','V473_POST_CAFE'),
   ('v473_post_lake','riverside',900,720,'V473-EPI-POST-LAKE','V473_POST_LAKE')]:
  free['interactables'].append(it(key,place,x,y,'Kenangan kecil setelah petualangan',[
   ac('scene',id=sceneid),ac('flag',id=flag),ac('sfx',id='page')],when={'notFlags':[flag]}))
 free['interactables'].append(it('v473_bonus_gate','galeri_komunitas',770,510,'Buka bonus dua surat (dua route tamat)',[
    ac('music',id='cinema_dual_letters_v473'),ac('scene',id='V473-EPI-BONUS-OPEN'),
    ac('step',id='V473_EPI_BONUS_ENTER'),ac('warp',area='ruang_dua_surat',x=480,y=510,dir='up')],
    when={'bothRoutesCompleted':True,'notFlags':['V473_BONUS_DONE']}))
 # Map: original pixel-art two-letter library, with safe return door for mid-bonus saves.
 m['areas']['ruang_dua_surat']={'name':'Ruang Dua Surat','image':'maps/ruang_dua_surat.png','w':960,'h':640,
  'spawn':[480,510],'indoor':True,'music':'memory','ambient':'magic_chimes',
  'walls':[[0,0,960,64],[0,0,55,640],[905,0,55,640],[0,616,430,24],[530,616,430,24]],
  'ellipses':[],'props':[],'gates':[],'animals':[],'water':[],'examine':[],
  'storyVersion':'v473_epilogue_two_routes','visualStyle':'quiet_archive_pixelart',
  'doors':[{'id':'v473_letters_exit','label':'Kembali ke Galeri Komunitas','rect':[430,590,100,50],
            'to':'galeri_komunitas','tx':700,'ty':540,'dir':'down'}]}
 gallery=m['areas']['galeri_komunitas'];gallery['doors']=[d for d in gallery.get('doors',[]) if d['id']!='v473_gallery_to_letters']
 gallery['doors'].append({'id':'v473_gallery_to_letters','label':'Ruang Dua Surat','rect':[770,455,80,65],
    'to':'ruang_dua_surat','tx':480,'ty':510,'dir':'up','locked':[
     {'when':{'maxChapter':'C06'},'text':'Ruang Dua Surat hanya terbuka setelah cerita tamat.'},
     {'when':{'bothRoutesCompleted':False},'text':'Selesaikan Chapter 6 di route Arland dan Sofia dahulu.'}]})
 b['items']['v473_legacy_page']={'name':'Halaman Plaza','desc':'Kenangan yang indah karena dua orang sama-sama berani datang.','icon':'items/v473_page.png'}
 b['items']['v473_two_letters']={'name':'Dua Surat yang Utuh','desc':'Versi Arland dan Sofia tersimpan bersama, tidak saling menimpa.','icon':'items/v473_letter.png'}
 records=[
  ('plaza','Plaza yang Baru Dipahami','Kenangan dari pertemuan pertama yang kini dapat dilihat dari dua sisi.','V473_EPI_PLAZA_DONE','page','shared','fictional_memory'),
  ('cafe','Surat Dua Sisi','Arland dan Sofia akhirnya menyimpan dua urutan dan dua suara.','V473_EPI_CAFE_DONE','letter','shared','fictional_memory'),
  ('gallery','Gambar yang Tidak Dihapus','Kursi kosong dan keberanian Sofia tetap hadir bersama kenangan baru.','V473_EPI_GALLERY_DONE','chair','shared','fictional_memory'),
  ('lake','Sore yang Belum Selesai','Foto lama, surat danau, dan halaman masa depan yang masih kosong.','V473_EPI_COMPLETE','sunset','shared','fictional_memory'),
  ('two_letters','The Other Side of the Page','Dua surat hanya tersedia setelah kedua route Chapter 6 tamat.','V473_BONUS_DONE','letter','shared','postgame_memory')]
 for key,title,desc,flag,icon,rt,kind in records:
  b['entries'].append({'id':'v473_epi_'+key,'chapter':'EPI','route':rt,'type':kind,
                      'unlock':flag,'icon':'items/v473_'+icon+'.png','title':title,'text':desc})
 for flag,title in [('V473_POST_PLAZA','Bunga untuk Hari Biasa'),('V473_POST_CAFE','Dua Gelas di Kafe'),('V473_POST_LAKE','Sore yang Tidak Hilang')]:
  b['entries'].append({'id':'v473_'+flag.lower(),'chapter':'EPI','route':'shared','type':'postgame_memory',
                      'unlock':flag,'icon':'items/v473_page.png','title':title,'text':'Satu hari kecil setelah kisah besar selesai.'})
 for flag,title in [('V473_PLAZA_GIFT','Hadiah yang Tetap Miring'),('V473_PLAZA_COURAGE','Keberanian Bertemu'),
                    ('V473_CAFE_LISTEN','Mendengarkan Dua Sisi'),('V473_CAFE_TWO_SIDES','Dua Versi Disimpan'),
                    ('V473_GALLERY_KEEP','Kursi yang Tidak Dihapus'),('V473_GALLERY_PAIR','Dua Gambar Berdampingan'),
                    ('V473_BONUS_KEEP','Dua Surat Apa Adanya'),('V473_BONUS_NEW_PAGE','Satu Halaman Baru')]:
  b['entries'].append({'id':'v473_branch_'+flag.lower(),'chapter':'EPI','route':'shared','type':'optional_story_branch',
                      'unlock':flag,'icon':'items/v473_letter.png','title':title,'text':'Keputusanmu mengubah cara kenangan ini diceritakan.'})
 b['bonus']['text']='Tamatkan Chapter 6 dari route Arland dan Sofia, lalu masuk ke Ruang Dua Surat melalui Galeri Komunitas untuk memainkan bab bonus dua perspektif.'
 q['steps'].extend(new)
 for filename,obj in (('story.json',s),('quests.json',q),('maps.json',m),('memory_book.json',b)):
  (D/filename).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
 print('APPLIED v4.7.3 Epilogue: ',len(new),'playable quest steps;',sum(k.startswith('V473-') for k in s['scenes']),'scenes; ',len(m['areas']),'maps; ',len(b['entries']),'memories')
if __name__=='__main__':apply()
