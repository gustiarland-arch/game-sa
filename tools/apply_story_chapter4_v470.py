#!/usr/bin/env python3
"""Chapter 4 narrative+playable quest audit, v4.7.0 LOCAL DRAFT ONLY.

Apply after Chapter 1/2/3 patches. Deterministic, additive: preserves old scene IDs,
saves, 23 maps, and chapter transitions, while restoring The Empty Seat's agency.
"""
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
DATA=R/'android/assets/data'
def A(d,**kwargs):return dict(do=d,**kwargs)
def If(flag,actions,otherwise=None):return A('if',when={'flags':[flag]},then=actions,**{'else':otherwise or []})
def line(w,t,e='neutral'):return dict(s=w,t=t,e=e)
def scene(s,id,title,route,where,lines,choices=None,flags=None):
 s['scenes'][id]=dict(title=title,chapter='C04',route=route,location=where,trigger='v4.7.0 draft playable story',
   lines=[line(*l) for l in lines],choices=choices or [],flags=flags or [])
def choice(t,flag,response):return dict(text=t,flags=[flag],byRoute={r:[line(*l) for l in response] for r in ('arland','sofia')})
def it(id,area,x,y,label,actions,route=None,rad=110,flag=None,sprite=None):
 d=dict(id=id,area=area,x=x,y=y,r=rad,label=label,actions=actions)
 if route:d['route']=route
 if flag:d['hideIfFlag']=flag
 if sprite:d['sprite']=dict(image='items/'+sprite+'.png',x=x,y=y-8,bob=False)
 return d
def step(id,title,interactions,quest='Q_V470_C04'):
 return dict(id=id,chapter='C04',quest=quest,objective={'arland':title,'sofia':title},interactables=interactions)
def memory(book,id,route,flag,title,desc,icon):
 book['entries'].append(dict(id=id,chapter='C04',route=route,type='fictional_memory',unlock=flag,
                              icon='items/'+icon+'.png',title=title,text=desc))
def movie(title,caption,focus='player',zoom=1.22):
 return A('cine',cmds=[{'c':'bars','on':True,'t':.45},{'c':'shot','focus':focus,'zoom':zoom,'frame':'intimate','t':1.4,'bars':False},
                      {'c':'caption','text':title,'sub':caption,'t':2.9},{'c':'bars','on':False,'t':.35}])
def apply():
 s=json.loads((DATA/'story.json').read_text('utf-8'));q=json.loads((DATA/'quests.json').read_text('utf-8'));b=json.loads((DATA/'memory_book.json').read_text('utf-8'))
 steps={x['id']:x for x in q['steps']}
 need=('C04_A_WAKE','C04_S_WAKE','C04_V464_A_PROJECTOR','C04_V464_A_GALLERY','C04_V464_S_GALLERY',
       'C04_V464_S_REFLECT','C04_A_PARK','C04_S_MEET','C04_LIGHTS','C04_PUZZLE','C04_V26_VOW',
       'C04_V465_A_REFLECT','C04_V465_S_REFLECT','C04_V465_SECOND_TALK')
 assert all(k in steps for k in need),'legacy Chapter4 step anchor missing'
 assert 'V469-C03-HALF-A' in s['scenes'],'Chapter3 patch must apply first'
 s['meta']['chapter4Overhaul']='v4.7.0 local draft: The Empty Seat / five-lantern repair arc'

 # Explicit setup callbacks: Chapter-3 promise/invitation and Chapter-2 consent are meaningful.
 for id,title,lines in [
  ('V470-C04-PROMISE-TIME','Jam yang Pernah Dicatat',[
    ('narrator','Arland pernah mencatat waktu acara Sofia dan berkata akan datang lebih awal.'),
    ('arland','Catatan itu masih ada. Aku yang nggak mengikuti hal yang sudah kutulis.')]),
  ('V470-C04-PROMISE-LISTEN','Janji Mendengarkan',[
    ('narrator','Saat di galeri beberapa hari lalu, Arland berjanji akan mendengarkan cerita Sofia.'),
    ('sofia','Aku ingin dia di sini mendengar ceritaku, bahkan kalau gambarnya nggak sempurna.')]),
  ('V470-C04-PROMISE-SIMPLE','Janji Kecil',[
    ('narrator','Di antara lukisan, ada kartu janji sederhana: hadir dan menyaksikan bersama.'),
    ('arland','Aku lupa bahwa melakukan hal kecil tepat waktu jauh lebih berarti.')]),
  ('V470-C04-INVITE-ASK','Undangan yang Meminta Kehadiran',[
    ('narrator','Undangan galeri masih terbuka. Sofia pernah bilang jelas bahwa kehadiran Arland penting baginya.'),
    ('sofia','Aku sudah berani minta ditemani. Aku ingin perasaan itu dianggap serius.')]),
  ('V470-C04-INVITE-SCHEDULE','Undangan yang Menyimpan Jam',[
    ('narrator','Di undangan ada tanggal dan jam yang disepakati bersama. Tak ada keraguan tentang kapan acara dimulai.'),
    ('arland','Aku tahu waktunya sejak awal. Aku seharusnya memprioritaskan janji itu.')])]:
  scene(s,id,title,'shared','galeri_komunitas',lines)
 for id,route,flag,lines in [
  ('V470-C04-C02-S-YES','sofia','V468_S_REPLY_YES',[('sofia','Waktu itu aku memilih ikut karena aku ingin. Kali ini aku juga memilih meminta kamu hadir.')]),
  ('V470-C04-C02-S-LATER','sofia','V468_S_REPLY_LATER',[('sofia','Aku pernah bilang kalau aku butuh waktu. Arland menghargainya. Sekarang aku ingin ia ingat waktu yang kami sepakati.')]),
  ('V470-C04-C02-S-NO','sofia','V468_S_REPLY_NO',[('sofia','Waktu aku memilih sendiri, dia menghormatinya. Hari ini aku memilih ditemani, dan rasanya berbeda.')]),
  ('V470-C04-C02-A-SIMPLE','arland','V468_A_INVITE_SIMPLE',[('arland','Aku pernah mengajaknya jalan tanpa memaksa. Kenapa hari ini aku justru sibuk memaksakan kejutan?')]),
  ('V470-C04-C02-A-CARE','arland','V468_A_INVITE_CARE',[('arland','Aku pernah bertanya apakah Sofia lelah. Seharusnya kali ini aku juga bertanya apa yang ia perlukan.')]),
  ('V470-C04-C02-A-OPEN','arland','V468_A_INVITE_OPEN',[('arland','Dulu kami membuat rencana bersama. Hari ini aku mengubah rencana sendiri tanpa bertanya.')])]:
  scene(s,id,'Ingat Pilihan Sebelumnya',route,'galeri_komunitas',lines)

 # A choice truly changes the playable task; even warning/help don't magically erase the missed event.
 scene(s,'V470-C04-A-WARN','Kabar yang Tidak Mengganti Kehadiran','arland','arland_room',[
   ('narrator','Pesan sudah terkirim. Arland membaca ulang kata-katanya dan menyadari belum memberi kepastian kapan ia tiba.'),
   ('arland','Ngabarin itu perlu. Tapi aku juga harus jujur kalau acara ini sudah hampir dimulai.'),
   ('narrator','Ia menambahkan perkiraan waktu, tanpa meminta Sofia menunggunya.')],flags=['V470_A_WARN_DONE'])
 scene(s,'V470-C04-A-FUSE','Proyektor dan Jam Dinding','arland','arland_room',[
   ('narrator','Baut kecil di belakang proyektor longgar. Arland memperbaiki sambungan dengan hati-hati.'),
   ('arland','Aku terus bilang satu percobaan lagi, padahal aku bisa berhenti dan pergi.'),
   ('narrator','Lampu indikator menyala. Ketika menoleh, jarum jam sudah melewati awal acara.')],flags=['V470_A_FUSE_DONE'])
 scene(s,'V470-C04-A-TEST','Gambar yang Akhirnya Menyala','arland','arland_room',[
   ('narrator','Proyeksi sketsa akhirnya tampak jelas di dinding yang kosong.'),
   ('arland','Bagus... tapi Sofia nggak butuh layar ini untuk berani menunjukkan karyanya.'),
   ('narrator','Arland mematikan proyektor dan bergegas pergi. Waktu yang lewat tidak bisa diputar kembali.')],flags=['V470_A_TEST_DONE'])
 scene(s,'V470-C04-A-HELP','Meminta Bantuan','arland','arland_room',[
   ('arland','Pak Harun, boleh tolong lihat proyektor ini? Aku harus ke acara Sofia.'),
   ('harun','Tinggalkan saja. Tapi segera kabari kalau kamu terlambat. Orang menunggu kabar, bukan alat.'),
   ('narrator','Arland menitipkan kunci, namun saat keluar ia terjebak jalanan yang padat karena hujan.')],flags=['V470_A_HELP_DONE'])
 scene(s,'V470-C04-A-HELP-OUT','Bukan Perkara Proyektor','arland','perumahan',[
   ('narrator','Di depan gang, Arland berhenti di bawah papan jadwal angkutan. Waktu presentasi sudah lewat.'),
   ('arland','Aku sudah minta bantuan, tapi terlambat mengambil keputusan. Itu tetap tanggung jawabku.'),
   ('narrator','Ia menuju galeri tanpa berharap dapat mengulang bagian yang terlewat.')],flags=['V470_A_HELP_ARRIVED'])
 scene(s,'V470-C04-A-WARN-SEEN','Pesan yang Tiba','arland','galeri_komunitas',[
   ('narrator','Di galeri, Arland tahu pesannya sempat dibaca sebelum presentasi berakhir.'),
   ('arland','Aku sudah memberi kabar. Tapi kabar bukan pengganti kursi yang kujanjikan.')])
 scene(s,'V470-C04-A-SILENT-SEEN','Kabar yang Tidak Ada','arland','galeri_komunitas',[
   ('narrator','Ponselnya menunjukkan beberapa draf pesan yang tak pernah terkirim.'),
   ('arland','Aku cuma fokus ke apa yang mau kubuat, sampai lupa orang yang ingin kutemani.')])
 scene(s,'V470-C04-A-HELP-SEEN','Terlambat Mengubah Rencana','arland','galeri_komunitas',[
   ('narrator','Kunci proyektor masih dititipkan. Arland sudah mencoba meminta bantuan, tetapi terlambat menyadari prioritasnya.'),
   ('arland','Lain kali aku akan memutuskan lebih awal, bukan saat semuanya hampir selesai.')])

 # Playable Sofia prep: two independent physical interactions before her presentation.
 scene(s,'V470-C04-S-NOTE','Catatan di Belakang Bingkai','sofia','galeri_komunitas',[
   ('narrator','Sofia merapikan kartu pos, foto, dan catatan pembuka di meja galeri.'),
   ('sofia','Aku ingin orang lihat gambarku. Aku juga berharap satu orang tertentu duduk di sana.'),
   ('narrator','Nama Arland tertulis di kursi dekat jendela. Sofia membiarkannya tetap kosong.')],flags=['V470_S_NOTE_DONE'])
 scene(s,'V470-C04-S-REHEARSE','Kalimat Pertama','sofia','galeri_komunitas',[
   ('narrator','Sofia mencoba mengucapkan satu kalimat sebelum tamu masuk. Suaranya sedikit bergetar.'),
   ('sofia','Aku bisa mulai dari sesuatu yang jujur. Bukan dari sesuatu yang sempurna.')],choices=[
     choice('Mulai dari bunga kertas yang pernah diterima','V470_S_OPEN_FLOWER',[
       ('sofia','Gambar pertama ini tentang seseorang yang membuatku sadar perhatian nggak harus mahal.','serius')]),
     choice('Mulai dari proses membuat sketsa','V470_S_OPEN_WORK',[
       ('sofia','Dulu aku sering sembunyiin gambar yang belum selesai. Hari ini aku mau berani nunjukin.','serius')]),
     choice('Mulai dari ucapan terima kasih untuk pengunjung','V470_S_OPEN_GUESTS',[
       ('sofia','Terima kasih sudah datang. Aku sedikit gugup, tapi senang kalian mau lihat.','malu')])],flags=['V470_S_REHEARSAL_DONE'])
 scene(s,'V470-C04-S-PRESENT-FLOWER','Bunga di Atas Kertas','sofia','galeri_komunitas',[
   ('narrator','Sofia menampilkan gambar bunga kertas yang belum sempurna lipatannya.'),
   ('sofia','Ada hadiah yang diingat bukan karena bentuknya, tapi karena seseorang meluangkan waktunya.')])
 scene(s,'V470-C04-S-PRESENT-WORK','Berani Tidak Sempurna','sofia','galeri_komunitas',[
   ('sofia','Aku sering memperbaiki gambar berkali-kali sampai takut menunjukkannya.'),
   ('narrator','Ia membuka halaman yang masih ada coretan pensil, dan melanjutkan dengan suara lebih tenang.')])
 scene(s,'V470-C04-S-PRESENT-GUESTS','Orang yang Benar-Benar Hadir','sofia','galeri_komunitas',[
   ('sofia','Makasih sudah meluangkan waktu datang. Aku ingin belajar menghargai orang yang hadir.'),
   ('narrator','Sofia tersenyum pada para pengunjung sebelum sekilas menatap kursi dekat jendela.')])

 # Gallery aftermath physically playable from each perspective; emotional choice doesn't erase initial hurt.
 scene(s,'V470-C04-A-WITNESS','Mendengar Hari yang Tidak Dilihat','arland','galeri_komunitas',[
   ('laras','Sofia gemetar waktu kalimat pertamanya, Land. Tapi ia lanjut sampai selesai.'),
   ('arland','Aku perlu dengar ceritanya, bukan cuma lihat hasil gambarnya.'),
   ('laras','Dia tersenyum waktu orang-orang bertepuk tangan. Kamu boleh bangga padanya, sambil tetap mengakui kamu tak hadir.')],flags=['V470_A_WITNESS'])
 scene(s,'V470-C04-A-TICKET','Tiket yang Terlipat','arland','galeri_komunitas',[
   ('narrator','Di bawah kursi terdapat sebuah tiket acara yang terlipat.'),
   ('arland','Tanggal dan jamnya jelas. Aku yang membiarkan hal lain mengambil semua waktuku.'),
   ('narrator','Arland menyimpan tiket untuk mengingat satu janji yang tidak terpenuhi.')],flags=['V470_A_TICKET'])
 scene(s,'V470-C04-S-SKETCH','Kursi di Antara Garis','sofia','galeri_komunitas',[
   ('narrator','Sofia menggambar kursi yang kosong pada halaman terpisah.'),
   ('sofia','Aku nggak mau menghapus gambar ini. Tapi aku juga nggak mau satu kursi menentukan seluruh hariku.'),
   ('narrator','Di sampingnya ia menulis: Aku berhasil menyelesaikan presentasi itu.')],flags=['V470_S_SKETCH'])
 scene(s,'V470-C04-S-LIGHT','Pameran yang Tetap Miliknya','sofia','galeri_komunitas',[
   ('narrator','Sofia mengemas lukisan terakhir dan mematikan lampu meja galeri.'),
   ('sofia','Aku sedih Arland nggak datang. Tapi aku juga boleh bangga sama apa yang sudah aku kerjakan.'),
   ('narrator','Ia mengucapkan terima kasih kepada penjaga yang membantu menata ruangan.')],flags=['V470_S_LIGHT'])

 # The half-letter is no longer a dead-end collectible and can change the rain conversation.
 for id,route,flag,lines in [
  ('V470-C04-LETTER-A-ASK','arland','V469_A_LETTER_ASK',[('arland','Aku menemukan setengah surat kemarin. Aku belum tahu isinya, jadi aku mau bertanya, bukan menebak.'),('sofia','Makasih. Tapi hari ini aku perlu kamu dengar dulu apa yang aku rasain.')]),
  ('V470-C04-LETTER-A-NOTE','arland','V469_A_LETTER_NOTE',[('arland','Kemarin aku menulis catatan supaya nggak lupa nanya perasaan Sofia.'),('arland','Nyatanya aku terlalu sibuk dengan rencanaku sendiri. Hari ini aku mau dengerin.')]),
  ('V470-C04-LETTER-S-HONEST','sofia','V469_S_LETTER_HONEST',[('sofia','Aku pernah nulis: aku boleh meminta ditemani, dan itu bukan berarti aku merepotkan.'),('arland','Kamu nggak merepotkan, Sof. Aku yang perlu belajar mendengarkan.')]),
  ('V470-C04-LETTER-S-WAIT','sofia','V469_S_LETTER_WAIT',[('sofia','Aku butuh waktu sebelum cerita semuanya. Aku nggak mau memaksa diriku sendiri.'),('arland','Boleh. Aku nggak akan menagih jawaban sekarang.')])]:
  scene(s,id,'Surat yang Tidak Rampung',route,'taman_kota',lines)
 scene(s,'V470-C04-LETTER-LEGACY','Halaman yang Belum Dibaca','shared','taman_kota',[
   ('narrator','Ada perasaan yang pernah tertinggal dalam surat. Sekarang keduanya memilih tidak menebak isi hati yang lain.')])

 # Five emotional lanterns rather than the two mechanically available before audit.
 scene(s,'V470-C04-LIGHT-PRESENCE','Cahaya Kehadiran','shared','lantern_field',[
   ('narrator','Sebuah lentera memperlihatkan dua gambaran: proyektor yang menyala dan kursi yang kosong.'),
   ('sofia','Kadang aku cuma ingin ada seseorang yang menyaksikan aku berani.'),
   ('arland','Dan aku malah sibuk bikin sesuatu yang kupikir lebih penting.'),
   ('narrator','Lentera pulih ketika mereka sama-sama mengakui kejadian itu, tanpa mencari siapa yang lebih benar.')],flags=['V470_LIGHT_PRESENCE'])
 scene(s,'V470-C04-LIGHT-BOUNDARY','Cahaya Memberi Ruang','shared','lantern_field',[
   ('narrator','Sebuah cahaya kecil padam setiap kali ada suara yang memaksanya segera terang.'),
   ('sofia','Aku boleh perlu waktu. Bukan berarti aku ingin pergi selamanya.'),
   ('arland','Aku bisa tetap peduli tanpa memintamu cepat merasa baik-baik saja.'),
   ('narrator','Ketika tak ada yang memaksa, cahaya itu kembali stabil.')],flags=['V470_LIGHT_BOUNDARY'])
 scene(s,'V470-C04-LIGHT-UPDATE','Cahaya Kabar','shared','lantern_field',[
   ('narrator','Jam kecil di dalam lentera berhenti tepat sebelum acara galeri.'),
   ('arland','Mengabari orang itu bukan hal tambahan setelah selesai. Itu bagian dari menjaga janji.'),
   ('sofia','Aku juga mau bilang dengan jelas kalau suatu hari aku butuh ditemani.'),
   ('narrator','Jarum jam bergerak lagi, tanpa menghapus waktu yang pernah terlewat.')],flags=['V470_LIGHT_UPDATE'])

 # Recovery must be played, not a single scene and romantic gift.
 scene(s,'V470-C04-A-AGENDA','Janji yang Bisa Diperiksa','arland','arland_room',[
   ('narrator','Arland menuliskan jadwal galeri dan satu pengingat: beri kabar ketika rencana berubah.'),
   ('arland','Aku nggak bisa membuktikan apa-apa hanya dengan bilang akan berubah.'),
   ('narrator','Ia menyisakan ruang kosong untuk memastikan Sofia juga setuju dengan rencana berikutnya.')],flags=['V470_A_AGENDA'])
 scene(s,'V470-C04-A-HEAR','Mendengar Tanpa Memperbaiki','arland','galeri_komunitas',[
   ('narrator','Arland meminta Bu Laras mengulang cerita tentang momen Sofia berdiri di depan lukisannya.'),
   ('laras','Dia ragu, lalu menemukan suaranya sendiri. Penonton bertepuk tangan karena karyanya, bukan karena kejutan apa pun.'),
   ('arland','Aku akan bilang aku bangga padanya. Tanpa mengalihkan pembicaraan ke proyektor.')],flags=['V470_A_HEAR'])
 scene(s,'V470-C04-S-BOUNDARY','Batas yang Boleh Diucapkan','sofia','sofia_room',[
   ('narrator','Di buku catatan, Sofia menulis apa yang ia butuhkan sebelum kembali bertemu Arland.'),
   ('sofia','Kalau aku sedang kecewa, aku boleh bilang. Dan kalau belum siap bicara, aku boleh minta waktu.'),
   ('narrator','Ia melipat halaman itu, lalu memilih kata yang paling sesuai dengan perasaannya.')],choices=[
     choice('Aku butuh kamu hadir, bukan membuat semuanya sempurna','V470_S_NEED_PRESENT', [('sofia','Aku ingin bilang jelas apa yang kubutuhkan, bukan berharap dia menebak.')]),
     choice('Aku mau kita saling mengabari saat rencana berubah','V470_S_NEED_UPDATE', [('sofia','Kalau waktunya berubah, aku ingin tahu sebelum semuanya jadi tebakan.')]),
     choice('Aku ingin didengar sampai selesai, tanpa dipaksa lekas pulih','V470_S_NEED_LISTEN', [('sofia','Aku boleh butuh waktu. Perasaanku tetap penting.')])],flags=['V470_S_BOUNDARY'])
 scene(s,'V470-C04-S-LETTER','Bukan Menghapus Kursi','sofia','galeri_komunitas',[
   ('narrator','Sofia menempel sketsa kursi kosong berdampingan dengan gambar barunya.'),
   ('sofia','Aku bisa mengingat hari yang sakit tanpa menganggap semua hari nanti akan sama.'),
   ('narrator','Ia membawa kedua gambar itu untuk percakapan yang belum selesai.')],flags=['V470_S_LETTER'])
 scene(s,'V470-C04-RESOLVE-A','Mendengar Kesempatan Kedua','arland','taman_kota',[
   ('arland','Aku sudah dengar bagian presentasimu yang kulewatkan. Aku bangga kamu tetap menyelesaikannya.'),
   ('sofia','Terima kasih sudah benar-benar tanya. Aku nggak ingin hari itu dilupakan, tapi juga nggak mau terus diam.')])
 scene(s,'V470-C04-RESOLVE-S','Kalimat yang Berani Diucapkan','sofia','taman_kota',[
   ('sofia','Aku bisa bangga sama presentasiku dan tetap sedih kamu nggak ada.'),
   ('arland','Iya. Aku nggak mau membantah salah satunya. Dua-duanya benar buat kamu.')])
 scene(s,'V470-C04-RESOLVE-WARN','Kabar Tidak Menghapus Rasa Kecewa','arland','taman_kota',[
   ('sofia','Aku sempat baca pesanmu. Aku senang kamu mengabari, tapi aku tetap sedih kursinya kosong.'),
   ('arland','Iya. Lain kali aku akan merencanakan lebih baik, bukan hanya mengabari ketika sudah terlambat.')])
 scene(s,'V470-C04-RESOLVE-SILENT','Pesan yang Tidak Terkirim','arland','taman_kota',[
   ('arland','Aku nggak ngasih kabar sama sekali. Aku sadar itu bikin kamu tambah menunggu.'),
   ('sofia','Makasih udah mengakuinya. Aku ingin kita bisa bicara sebelum semuanya terlambat.')])
 scene(s,'V470-C04-RESOLVE-HELP','Terlambat Meminta Tolong','arland','taman_kota',[
   ('arland','Aku akhirnya minta bantuan, tapi terlambat. Aku perlu tahu kapan berhenti memaksakan semuanya sendiri.'),
   ('sofia','Boleh minta bantuan, Land. Aku juga ingin kamu tanya apa yang sebenarnya aku perlukan.')])
 for id,flag,lines in [
  ('V470-C04-RESOLVE-SPACE','V464_S_SPACE',[('sofia','Aku perlu waktu untuk tenang. Terima kasih nggak mendesak aku bicara saat itu.')]),
  ('V470-C04-RESOLVE-SPEAK','V464_S_SPEAK',[('sofia','Aku senang akhirnya berani bilang kalau hari itu penting buatku.')]),
  ('V470-C04-RESOLVE-DRAW','V464_S_DRAW',[('sofia','Aku masih menyimpan sketsa kursi kosong. Bukan untuk menyalahkan, tapi untuk ingat.')])]:
  scene(s,id,'Kata-kata yang Diingat','sofia','taman_kota',lines)
 scene(s,'V470-C04-HANDOFF','Belum Sempurna, Tetapi Bergerak','shared','taman_kota',[
   ('narrator','Mereka tidak berpura-pura kesedihannya sudah hilang. Keduanya memilih berjalan pulang dengan langkah yang tidak selalu sama.'),
   ('sofia','Aku belum mau semuanya balik kayak sebelum kejadian. Tapi aku mau kita terus belajar.'),
   ('arland','Aku juga. Kalau ada yang nggak nyaman, kita ngomong. Nggak harus ditebak.'),
   ('narrator','Memory Book menyimpan kursi kosong itu tanpa menghapusnya. Halaman berikutnya menunjukkan langit yang dipenuhi bintang.')],flags=['V470_C04_REPAIR_EARNED'])

 # Insert genuine new steps after existing anchors, maintaining quest and save IDs.
 n=[]
 arrive=[movie('The Empty Seat','Yang terlewat tak bisa diulang',zoom=1.28),A('music',id='cinema_empty_seat_v470'),A('warp',area='galeri_komunitas',x=480,y=530,dir='up'),A('step',id='C04_V464_A_GALLERY')]
 n.append(step('V470_C04_A_WARN','Kirim kabar yang jelas sebelum berangkat ke galeri',[
  it('v470_a_message','arland_room',721,398,'Kirim perkiraan waktu kedatangan',[A('sfx',id='notification'),A('scene',id='V470-C04-A-WARN'),A('item',id='v470_message'),*arrive],'arland',85,sprite='v470_c04_letter')]))
 n.append(step('V470_C04_A_SILENT','Periksa sambungan lalu nyalakan proyektor',[
  it('v470_a_fuse','arland_room',695,430,'Periksa sambungan proyektor',[A('scene',id='V470-C04-A-FUSE'),A('count',id='v470_a_repair',add=1),A('sfx',id='page')],'arland',93,'V470_A_FUSE_DONE'),
  it('v470_a_screen','arland_room',760,450,'Tes kembali gambar di proyektor',[A('scene',id='V470-C04-A-TEST'),A('count',id='v470_a_repair',add=1),A('sfx',id='sparkle')],'arland',90,'V470_A_TEST_DONE',sprite='v470_c04_projector')]))
 n[-1]['interactables'][-1]['when']={'flags':['V470_A_FUSE_DONE']}
 n[-1]['counter']='v470_a_repair';n[-1]['counterMax']=2;n[-1]['complete']={'counter':'v470_a_repair','count':2,'actions':arrive}
 n.append(step('V470_C04_A_HELP','Titipkan proyektor lalu segera menuju galeri',[
  it('v470_a_call','arland_room',721,398,'Telepon untuk minta bantuan',[A('scene',id='V470-C04-A-HELP'),A('warp',area='perumahan',x=510,y=540,dir='down'),A('step',id='V470_C04_A_HELP_OUT')],'arland',85)]))
 n.append(step('V470_C04_A_HELP_OUT','Periksa jadwal dan berangkat dari gang',[
  it('v470_a_depart','perumahan',440,450,'Cek waktu, lalu menuju galeri',[A('scene',id='V470-C04-A-HELP-OUT'),*arrive],'arland',92)]))
 n.append(step('V470_C04_S_PREP','Siapkan kartu presentasi dan latih kalimat pertama',[
  it('v470_s_note','galeri_komunitas',730,385,'Susun kartu dan catatan karya',[A('scene',id='V470-C04-S-NOTE'),A('count',id='v470_s_prep',add=1),A('sfx',id='page')],'sofia',100,'V470_S_NOTE_DONE',sprite='v470_c04_letter'),
  it('v470_s_rehearse','galeri_komunitas',520,320,'Coba kalimat pertama di depan panggung',[A('scene',id='V470-C04-S-REHEARSE'),A('count',id='v470_s_prep',add=1),A('sfx',id='v469_pencil')],'sofia',105,'V470_S_REHEARSAL_DONE')]))
 n[-1]['counter']='v470_s_prep';n[-1]['counterMax']=2;n[-1]['complete']={'counter':'v470_s_prep','count':2,'actions':[A('step',id='C04_V464_S_GALLERY')]}
 n.append(step('V470_C04_A_AFTER','Dengar cerita presentasi Sofia dan simpan tiket galeri',[
  it('v470_a_witness','galeri_komunitas',760,360,'Dengarkan kisah dari Bu Laras',[A('scene',id='V470-C04-A-WITNESS'),A('count',id='v470_a_after',add=1)],'arland',110,'V470_A_WITNESS'),
  it('v470_a_ticket','galeri_komunitas',290,410,'Ambil tiket acara di bawah kursi',[A('sfx',id='v470_paper_note'),A('scene',id='V470-C04-A-TICKET'),A('item',id='v470_ticket'),A('count',id='v470_a_after',add=1)],'arland',110,'V470_A_TICKET',sprite='v470_c04_seat')]))
 n[-1]['counter']='v470_a_after';n[-1]['counterMax']=2;n[-1]['complete']={'counter':'v470_a_after','count':2,'actions':[A('warp',area='cafe',x=400,y=270,dir='down'),A('step',id='C04_A_CAFE')]}
 n.append(step('V470_C04_S_AFTER','Simpan sketsa dan tutup pameran dengan tenang',[
  it('v470_s_sketch','galeri_komunitas',290,410,'Gambar kursi yang kosong',[A('sfx',id='v470_paper_note'),A('scene',id='V470-C04-S-SKETCH'),A('item',id='v470_empty_chair_sketch'),A('count',id='v470_s_after',add=1)],'sofia',110,'V470_S_SKETCH',sprite='v470_c04_seat'),
  it('v470_s_lights','galeri_komunitas',760,365,'Bereskan lukisan dan ucapkan terima kasih',[A('scene',id='V470-C04-S-LIGHT'),A('count',id='v470_s_after',add=1)],'sofia',100,'V470_S_LIGHT')]))
 n[-1]['counter']='v470_s_after';n[-1]['counterMax']=2;n[-1]['complete']={'counter':'v470_s_after','count':2,'actions':[A('warp',area='cafe',x=400,y=270,dir='down'),A('step',id='C04_S_CAFE')]}
 n.append(step('V470_C04_A_PROOF','Buktikan perubahan lewat agenda dan mendengarkan',[
  it('v470_a_agenda','arland_room',721,398,'Tulis jadwal dan pengingat yang nyata',[A('sfx',id='v470_paper_note'),A('scene',id='V470-C04-A-AGENDA'),A('item',id='v470_new_promise'),A('count',id='v470_a_proof',add=1)],'arland',85,'V470_A_AGENDA',sprite='v470_c04_letter'),
  it('v470_a_listen','galeri_komunitas',760,360,'Dengarkan cerita lengkap presentasi Sofia',[A('scene',id='V470-C04-A-HEAR'),A('count',id='v470_a_proof',add=1)],'arland',110,'V470_A_HEAR')]))
 n[-1]['counter']='v470_a_proof';n[-1]['counterMax']=2;n[-1]['complete']={'counter':'v470_a_proof','count':2,'actions':[A('step',id='C04_V465_SECOND_TALK')]}
 n.append(step('V470_C04_S_PROOF','Tulis batas pribadi dan rawat kenangan yang tidak sempurna',[
  it('v470_s_boundaries','sofia_room',701,386,'Tuliskan apa yang Sofia butuhkan',[A('sfx',id='v470_paper_note'),A('scene',id='V470-C04-S-BOUNDARY'),A('item',id='v470_new_promise'),A('count',id='v470_s_proof',add=1)],'sofia',90,'V470_S_BOUNDARY',sprite='v470_c04_letter'),
  it('v470_s_art','galeri_komunitas',290,410,'Simpan kedua gambar tanpa menghapus yang lama',[A('scene',id='V470-C04-S-LETTER'),A('count',id='v470_s_proof',add=1)],'sofia',110,'V470_S_LETTER',sprite='v470_c04_seat')]))
 n[-1]['counter']='v470_s_proof';n[-1]['counterMax']=2;n[-1]['complete']={'counter':'v470_s_proof','count':2,'actions':[A('step',id='C04_V465_SECOND_TALK')]}

 # Existing projector scene gives choice, leading to actual separate playable branches.
 pro=steps['C04_V464_A_PROJECTOR']['interactables'][0]
 pro['actions']=[A('scene',id='V464-C04-A-PROJECTOR'),A('flag',id='V464_PROMISE_MISSED'),
   If('V464_A_WARN',[A('step',id='V470_C04_A_WARN')],
      [If('V464_A_SILENT',[A('step',id='V470_C04_A_SILENT')],[A('step',id='V470_C04_A_HELP')])])]
 # Before gallery, Sofia physically prepares and chooses how to start her talk.
 sf=steps['C04_S_WAKE']['interactables'][0]['actions']
 assert sf[-1].get('id') in ('C04_V464_S_GALLERY','V470_C04_S_PREP')
 sf[-1]['id']='V470_C04_S_PREP'
 # Additional scenes follow existing flags and never unlock false chronology.
 gallery_setup=[
    If('V464_PROMISE_TIME',[A('scene',id='V470-C04-PROMISE-TIME')],
      [If('V464_PROMISE_LISTEN',[A('scene',id='V470-C04-PROMISE-LISTEN')],
        [If('V464_PROMISE_SIMPLE',[A('scene',id='V470-C04-PROMISE-SIMPLE')])])]),
    If('V469_GALLERY_ASK',[A('scene',id='V470-C04-INVITE-ASK')],
      [If('V469_GALLERY_SCHEDULE',[A('scene',id='V470-C04-INVITE-SCHEDULE')])])]
 for gallery_key,action_id,kind in [('C04_V464_A_GALLERY','V464-C04-A-LATE','arland'),
                                    ('C04_V464_S_GALLERY','V464-C04-S-PRESENT','sofia')]:
  acts=steps[gallery_key]['interactables'][0]['actions']
  if not any(a.get('do')=='if' and a.get('when',{}).get('flags')==['V464_PROMISE_TIME'] for a in acts):
   at=next(i for i,a in enumerate(acts) if a.get('do')=='scene' and a.get('id')==action_id)
   opt=(If('V468_A_INVITE_SIMPLE',[A('scene',id='V470-C04-C02-A-SIMPLE')],
        [If('V468_A_INVITE_CARE',[A('scene',id='V470-C04-C02-A-CARE')],
           [If('V468_A_INVITE_OPEN',[A('scene',id='V470-C04-C02-A-OPEN')])])]) if kind=='arland' else
        If('V468_S_REPLY_YES',[A('scene',id='V470-C04-C02-S-YES')],
        [If('V468_S_REPLY_LATER',[A('scene',id='V470-C04-C02-S-LATER')],
           [If('V468_S_REPLY_NO',[A('scene',id='V470-C04-C02-S-NO')])])]))
   acts[at:at]=[*gallery_setup,opt]

 # Branch callbacks displayed within the actual gallery after players' live choices.
 ar=steps['C04_V464_A_GALLERY']['interactables'][0]['actions']
 j=next((i for i,a in enumerate(ar) if a.get('do')=='warp' and a.get('area')=='cafe'),None)
 if j is not None:ar[j:j+2]=[
   If('V464_A_WARN',[A('scene',id='V470-C04-A-WARN-SEEN')],
      [If('V464_A_SILENT',[A('scene',id='V470-C04-A-SILENT-SEEN')],[A('scene',id='V470-C04-A-HELP-SEEN')])]),
   A('step',id='V470_C04_A_AFTER')]
 stage=steps['C04_V464_S_GALLERY']['interactables'][0]['actions']
 j=next(i for i,a in enumerate(stage) if a.get('do')=='scene' and a.get('id')=='V464-C04-S-PRESENT')
 if not any(a.get('do')=='if' and a.get('when',{}).get('flags')==['V470_S_OPEN_FLOWER'] for a in stage):stage[j+1:j+1]=[If('V470_S_OPEN_FLOWER',[A('scene',id='V470-C04-S-PRESENT-FLOWER')],
    [If('V470_S_OPEN_WORK',[A('scene',id='V470-C04-S-PRESENT-WORK')],[A('scene',id='V470-C04-S-PRESENT-GUESTS')])])]
 final=steps['C04_V464_S_REFLECT']['interactables'][0]['actions']
 j=next((i for i,a in enumerate(final) if a.get('do')=='warp' and a.get('area')=='cafe'),None)
 if j is not None: final[j:j+2]=[A('step',id='V470_C04_S_AFTER')]
 # Listening experience changes when half-letter from Chapter 3 was found.
 for key in ('C04_A_PARK','C04_S_MEET'):
   acts=steps[key]['interactables'][0]['actions'];j=next(i for i,a in enumerate(acts) if a.get('do')=='scene' and a.get('id')=='C04-X00')
   callback=([If('V469_A_LETTER_ASK',[A('scene',id='V470-C04-LETTER-A-ASK')],
              [If('V469_A_LETTER_NOTE',[A('scene',id='V470-C04-LETTER-A-NOTE')],[A('scene',id='V470-C04-LETTER-LEGACY')])])]
       if key=='C04_A_PARK' else [If('V469_S_LETTER_HONEST',[A('scene',id='V470-C04-LETTER-S-HONEST')],
              [If('V469_S_LETTER_WAIT',[A('scene',id='V470-C04-LETTER-S-WAIT')],[A('scene',id='V470-C04-LETTER-LEGACY')])])])
   if not any(a.get('do')=='music' and a.get('id')=='cinema_empty_seat_v470' for a in acts):acts[j:j]=[A('music',id='cinema_empty_seat_v470'),movie('Di Bawah Hujan','Ada janji yang belum dipahami',focus='couple'),*callback]
 # 5 lanterns; original two remain fully reachable and hide after flags.
 lights=steps['C04_LIGHTS']
 for name,x,y,sid,flag in [('presence',840,1050,'PRESENCE','V470_LIGHT_PRESENCE'),
                            ('boundary',1080,570,'BOUNDARY','V470_LIGHT_BOUNDARY'),
                            ('update',850,360,'UPDATE','V470_LIGHT_UPDATE')]:
   if not any(i['id']=='v470_light_'+name for i in lights['interactables']):lights['interactables'].append(it('v470_light_'+name,'lantern_field',x,y,
     {'presence':'Cahaya Kehadiran','boundary':'Cahaya Memberi Ruang','update':'Cahaya Memberi Kabar'}[name],
     [A('scene',id='V470-C04-LIGHT-'+sid),A('count',id='cahaya',add=1),A('sfx',id='lantern')],rad=72,flag=flag,
       sprite='v470_c04_lantern'))
 lights['counterMax']=5;lights['complete']['count']=5
 lights['objective']={'arland':'Pulihkan lima lentera: mendengar, jujur, hadir, ruang, kabar',
                      'sofia':'Pulihkan lima lentera: mendengar, jujur, hadir, ruang, kabar'}
 s['scenes']['C04-X01']['lines'][0]['t']='Di Lantern Field, kelima cahaya menyala saat mereka menerima dua versi dari hari yang sama.'
 puzzle_act=steps['C04_PUZZLE']['interactables'][0]['actions']
 if not any(a.get('do')=='music' and a.get('id')=='cinema_rain_five_lights_v470' for a in puzzle_act): puzzle_act.insert(0,A('music',id='cinema_rain_five_lights_v470'))
 # After previous gallery revisit, there must be active accountability exercises before reuniting.
 for key,next_step in [('C04_V465_A_REFLECT','V470_C04_A_PROOF'),('C04_V465_S_REFLECT','V470_C04_S_PROOF')]:
   act=steps[key]['interactables'][0]['actions']
   j=next(i for i,a in enumerate(act) if a.get('do')=='step' and a.get('id') in ('C04_V465_SECOND_TALK',next_step))
   act[j]['id']=next_step
 meet=steps['C04_V465_SECOND_TALK']['interactables'][0]['actions']
 j=next(i for i,a in enumerate(meet) if a.get('do')=='scene' and a.get('id')=='V465-C04-SECOND-TALK')
 if not any(a.get('do')=='music' and a.get('id')=='cinema_listen_again_v470' for a in meet):meet[j:j]=[A('music',id='cinema_listen_again_v470'),
     If('V470_A_AGENDA',[A('scene',id='V470-C04-RESOLVE-A')],[A('scene',id='V470-C04-RESOLVE-S')]),
     If('V464_A_WARN',[A('scene',id='V470-C04-RESOLVE-WARN')],
       [If('V464_A_SILENT',[A('scene',id='V470-C04-RESOLVE-SILENT')],
         [If('V464_A_HELP',[A('scene',id='V470-C04-RESOLVE-HELP')])])]),
     If('V464_S_SPACE',[A('scene',id='V470-C04-RESOLVE-SPACE')],
       [If('V464_S_SPEAK',[A('scene',id='V470-C04-RESOLVE-SPEAK')],
          [If('V464_S_DRAW',[A('scene',id='V470-C04-RESOLVE-DRAW')])])])]
 j=next(i for i,a in enumerate(meet) if a.get('do')=='chapterEnd' and a.get('chapter')=='C04')
 if not any(a.get('do')=='scene' and a.get('id')=='V470-C04-HANDOFF' for a in meet):meet[j:j]=[A('scene',id='V470-C04-HANDOFF'),A('item',id='v470_two_sides')]
 # narrative book (choice exclusivity and replay handled by flags)
 b['entries']=[x for x in b['entries'] if not x.get('id','').startswith('v470_c04_')]
 for args in [
  ('v470_c04_empty_seat','shared','V464_SEAT_EMPTY','Satu Kursi Kosong','Sofia berhasil berdiri di depan karyanya. Satu kursi tetap tidak terisi.','v470_c04_seat'),
  ('v470_c04_half_letter','shared','HALF_LETTER_FOUND','Surat yang Belum Selesai','Kata yang belum selesai ditulis kini menjadi undangan untuk mendengarkan.','v470_c04_letter'),
  ('v470_c04_five_lights','shared','V470_LIGHT_UPDATE','Lima Cahaya Rain Garden','Mendengar, jujur, hadir, ruang, dan memberi kabar adalah lima hal yang mereka pelajari.','v470_c04_lantern'),
  ('v470_c04_growth','shared','V470_C04_REPAIR_EARNED','Janji yang Dijaga Lewat Tindakan','Hari itu tidak dapat diulang; mereka belajar pelan-pelan mengembalikan kepercayaan.','v470_c04_promise'),
  ('v470_c04_a_witness','arland','V470_A_WITNESS','Cerita dari Kursi Belakang','Arland mendengar perayaan Sofia dari orang yang benar-benar berada di sana.','v470_c04_seat'),
  ('v470_c04_s_presentation','sofia','V470_S_REHEARSAL_DONE','Keberanian Sofia','Bahkan saat kursi kosong, Sofia tetap menyelesaikan cerita di hadapan pengunjung.','v470_c04_promise')]:memory(b,*args)
 for id,rt,flag,title in [
  ('v470_c04_a_warn','arland','V470_A_WARN_DONE','Pesan yang Dikirim'),
  ('v470_c04_a_silent','arland','V470_A_TEST_DONE','Proyektor yang Terlambat'),
  ('v470_c04_a_help','arland','V470_A_HELP_ARRIVED','Berani Meminta Bantuan'),
  ('v470_c04_s_flower','sofia','V470_S_OPEN_FLOWER','Pembuka dengan Bunga'),
  ('v470_c04_s_work','sofia','V470_S_OPEN_WORK','Pembuka dengan Karya'),
  ('v470_c04_s_guests','sofia','V470_S_OPEN_GUESTS','Pembuka dengan Pengunjung')]:
  memory(b,id,rt,flag,title,'Satu pilihan mengubah cara mereka menjalani hari yang sulit.','v470_c04_letter')
  b['entries'][-1]['type']='optional_story_branch'
 # Every collected quest artifact must exist in MemoryBook's item registry too.
 for itemid,title,desc,icon in [
  ('v470_message','Pesan Sebelum Acara','Kabar yang dikirim sebelum sampai ke galeri.','letter'),
  ('v470_ticket','Tiket Acara Galeri','Tiket kecil yang tertinggal di bawah kursi kosong.','seat'),
  ('v470_empty_chair_sketch','Sketsa Kursi Kosong','Gambar Sofia: hari yang berharga, walaupun satu tempat tetap kosong.','seat'),
  ('v470_new_promise','Catatan untuk Hari Berikutnya','Bukan janji sempurna; sebuah kebiasaan kecil yang dapat dibuktikan.','promise'),
  ('v470_two_sides','Dua Sisi Satu Hari','Mereka memilih mengingat dua sisi, bukan menghapus sisi yang menyakitkan.','lantern')]:
  b['items'][itemid]={'name':title,'desc':desc,'icon':'items/v470_c04_'+icon+'.png'}
 # do not lose id and save references, replace only this pass' steps.
 q['steps']=[x for x in q['steps'] if not x['id'].startswith('V470_C04_')]+n
 # Branch scenes execute as actions; only referenced available IDs. Never rewrite Progress schema.
 for name,obj in (('story.json',s),('quests.json',q),('memory_book.json',b)):
  (DATA/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('PASS: Chapter 4 v4.7.0 story patch: 5 lanterns, playable consequence paths, persistent reconciliation, route memories')
if __name__=='__main__':apply()
