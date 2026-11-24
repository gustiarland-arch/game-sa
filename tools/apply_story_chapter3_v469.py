#!/usr/bin/env python3
"""Idempotent Chapter 3: The Little Things v4.6.9 *local draft*.

Apply after v4.6.8. Adds actual route-specific memory activities, a neighbor
errand, a two-sided half-letter, Chapter-2 callbacks and exhibition preparation.
Story canon/route/start/end IDs and save schema are not changed. Run with
python3 tools/apply_story_chapter3_v469.py, never as a substitute for APK QA.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'android/assets/data'
def A(d,**kw):return {'do':d,**kw}
def Cond(flag,yes,no=None):return A('if',when={'flags':[flag]},then=yes,**{'else':no or []})
def Route(rt,yes,no=None):return A('if',when={'route':rt},then=yes,**{'else':no or []})
def Line(w,t,e='neutral'):return {'s':w,'t':t,'e':e}
def Scene(s,id,title,route,place,lines,choices=None,flags=None):
    s['scenes'][id]={'title':title,'chapter':'C03','route':route,'location':place,
        'lines':[Line(*x) for x in lines], 'choices':choices or [],'flags':flags or [],
        'trigger':'Chapter 3 narrative quest v4.6.9 local draft'}
def Ch(text,flag,a,s):return {'text':text,'flags':[flag], 'byRoute':{'arland':[Line(*i) for i in a], 'sofia':[Line(*i) for i in s]}}
def It(id,area,x,y,label,acts,rt=None,r=78,**kw):
    v={'id':id,'area':area,'x':x,'y':y,'r':r,'label':label,'actions':acts,**kw}
    if rt:v['route']=rt
    return v
def Step(id,objective,items,quest='Q_V469_C03_MEMORIES'):
    return {'id':id,'chapter':'C03','quest':quest,'objective':{'arland':objective.get('arland','Aktivitas pribadi Sofia (route lain)'), 'sofia':objective.get('sofia','Aktivitas pribadi Arland (route lain)')},'interactables':items}
def mem(book,id,route,flag,title,text,icon,typ='fictional_memory'):
    book['entries'].append({'id':id,'chapter':'C03','route':route,'type':typ,'unlock':flag,
        'icon':'items/'+icon+'.png','title':title,'text':text})

def apply():
    story=json.loads((DATA/'story.json').read_text('utf-8'));q=json.loads((DATA/'quests.json').read_text('utf-8'))
    book=json.loads((DATA/'memory_book.json').read_text('utf-8'))
    steps={a['id']:a for a in q['steps']}
    required=('C03_A_IDEA','C03_S_CORNER','C03_FREE','C03_A_INGREDIENTS','C03_S_DECOR',
        'C03_S_ARRANGE','C03_COOK','C03_V26_DETAILS','C03_PICNIC','C03_V464_GALLERY_PREP',
        'C04_A_WAKE','C04_S_WAKE')
    assert all(i in steps for i in required), 'missing legacy C03/C04 quest anchor'
    assert 'V468-C02-S-REPLY' in story['scenes'],'apply Chapter-2 patch before Chapter-3 patch'
    assert 'V464-C03-PROMISE' in story['scenes'],'gallery canon must exist'
    story['meta']['chapter3Overhaul']='v4.6.9 draft / two-view memories, gallery promise, half-letter'

    # Dedicated playable route activities in existing rooms, not scripted-only montage.
    Scene(story,'V469-C03-A-FRAME-BEGIN','Bingkai yang Bisa Diperbaiki','arland','arland_room',[
      ('narrator','Foto kencan terselip di antara buku dan bingkai kayu yang retak. Satu sudutnya hampir lepas.'),
      ('arland','Aku ingat waktu kami tertawa gara-gara foto buram ini.'),
      ('arland','Aku bisa merapikan bingkai. Tapi nggak harus membuat fotonya sempurna.'),
      ('narrator','Urutkan potongan kenangan dulu, lalu pasang foto di bingkai dengan hati-hati.')],
      [Ch('Simpan bekas retaknya sebagai bagian cerita','V469_A_FRAME_SCAR',
        [('arland','Retaknya nggak hilang. Tapi ini tetap foto kami.','senyum')], [('arland','Retaknya bagian dari kenangan juga.')]),
       Ch('Perbaiki bagian belakang supaya bertahan lama','V469_A_FRAME_REPAIR',
        [('arland','Yang penting foto ini aman disimpan, nggak harus tanpa cela.','serius')],[('arland','Aku akan jaga foto ini.')])])
    Scene(story,'V469-C03-A-FRAME-DONE','Foto yang Tetap Berarti','arland','arland_room',[
       ('narrator','Arland menyelesaikan susunan foto. Bingkainya sekarang kuat, masih menyimpan jejak retaknya.'),
       ('arland','Mungkin yang dirawat bukan bendanya. Tapi kesempatan buat ingat hari itu.'),
       ('narrator','Ia menyelipkan selembar catatan kecil di belakangnya.')],flags=['V469_A_FRAME_DONE'])
    Scene(story,'V469-C03-S-SCRAP-BEGIN','Halaman yang Ingin Dijaga','sofia','sofia_room',[
       ('narrator','Sofia mengeluarkan tiket arcade, foto, kartu pos, dan selembar kertas kosong.'),
       ('sofia','Aku suka foto kami. Tapi ada beberapa hal yang nggak bisa masuk ke kamera.'),
       ('narrator','Susun kenangan di scrapbook. Biarkan ada ruang kosong untuk cerita yang belum datang.')],
       [Ch('Tulis percakapan yang paling diingat','V469_S_SCRAP_WORDS',
          [('sofia','Ada kalimat-kalimat pendek yang aku ingat lebih lama daripada tempatnya.','senyum')],
          [('sofia','Aku ingin ingat cara kami saling mendengar.','senyum')]),
        Ch('Gambar dua kursi dengan ruang di antaranya','V469_S_SCRAP_SPACE',
          [('sofia','Dua orang nggak harus menempel setiap saat supaya tetap dekat.','senyum')],
          [('sofia','Aku suka ruang kecil yang bikin kami tetap bisa jadi diri sendiri.','senyum')])])
    Scene(story,'V469-C03-S-SCRAP-DONE','Bukan Hanya Foto','sofia','sofia_room',[
       ('narrator','Sofia menata halaman sampai urutannya terasa pas; ia menempel foto tanpa menutup tulisan.'),
       ('sofia','Kalau suatu hari lupa, aku ingin melihat ini dan ingat perasaannya, bukan cuma harinya.'),
       ('narrator','Di ujung halaman, tinta membentuk garis seperti cahaya lentera lalu memudar.')],flags=['V469_S_SCRAP_DONE'])

    # Chapter-2 timing/consent choices receive a concrete next-chapter scene.
    for key,lines in {
     'YES': [('sofia','Kemarin aku ikut karena memang mau. Senang bisa pilih waktuku sendiri.'),
             ('narrator','Sofia menempel foto hari itu di halaman pertama scrapbook.')],
     'LATER': [('sofia','Kalau kemarin dipaksakan, mungkin aku nggak akan sempat cerita sebanyak itu.'),
               ('narrator','Sofia menempel kartu jadwal ulang di samping foto.')],
     'NO': [('sofia','Waktu sendiri kemarin membantuku menyelesaikan gambar dua kursi.'),
            ('narrator','Sketsa dari galeri menjadi halaman pembuka scrapbook milik Sofia.')],
    }.items():
        Scene(story,'V469-C03-S-DATE-'+key,'Kenangan dari Pilihan Sendiri','sofia','sofia_room',lines)
    for key,lines in {
      'SIMPLE':[('arland','Aku senang kemarin bisa ngajak Sofia tanpa bikin semuanya rumit.'),
                ('narrator','Ia merapikan foto, mengingat jawabannya sendiri.')],
      'CARE':[('arland','Kadang ajakan yang baik dimulai dengan bertanya apa seseorang sudah cukup istirahat.'),
              ('narrator','Arland melihat kotak pertolongan kecil di atas meja.')],
      'OPEN':[('arland','Aku senang waktu kami memilih rencana bareng, bukan karena aku yang menentukan semuanya.'),
              ('narrator','Ia melipat kertas rencana kencan untuk disimpan.')],
    }.items():
        Scene(story,'V469-C03-A-INVITE-'+key,'Cara Mengajak yang Diingat','arland','arland_room',lines)

    Scene(story,'V469-C03-A-NEIGHBOR','Mangkuk yang Dipinjamkan','arland','perumahan',[
       ('narrator','Arland membawa kembali mangkuk pinjaman kepada Pak Harun di gang dekat rumah.'),
       ('harun','Lho, dibalikin juga? Kemarin kamu kelihatan sibuk sekali.'),
       ('arland','Iya, Pak. Kalau sesuatu udah saya janjiin, harusnya saya ingat.'),
       ('harun','Kadang orang bukan menunggu barangnya, Land. Mereka menunggu kabarmu.'),
       ('narrator','Arland mengangguk. Ia pikir semua janji mudah dipenuhi jika sudah punya niat.')],
       flags=['V469_A_NEIGHBOR_DONE'])
    Scene(story,'V469-C03-S-NEIGHBOR','Buku yang Dikembalikan','sofia','perpustakaan',[
       ('narrator','Sofia mengembalikan buku sketsa pinjaman Bu Laras.'),
       ('laras','Kamu menandai halaman tentang ruang kosong di lukisan.'),
       ('sofia','Aku lagi belajar nggak buru-buru mengisi semua bagian yang masih kosong.'),
       ('laras','Kalau kamu ingin seseorang hadir di pameran nanti, kamu boleh bilang seberapa pentingnya itu.'),
       ('sofia','Iya, Bu. Kadang aku takut permintaanku terdengar merepotkan.')],
       flags=['V469_S_NEIGHBOR_DONE'])

    # Add dialogue with physical return errand, not NPC schedule dependent.
    Scene(story,'V469-C03-COOK-CALLBACK-LAUGH','Rasa Hari yang Lucu','shared','dapur',[
        ('arland','Masih inget foto kita yang ketawa nggak berhenti?'),
        ('sofia','Iya. Roti ini juga nggak harus cantik buat bikin kita senang.','tertawa')])
    Scene(story,'V469-C03-COOK-CALLBACK-LOOK','Mata yang Menjawab','shared','dapur',[
        ('sofia','Di foto kita saling lihat, bukan lihat kamera.'),
        ('arland','Aku ingat. Ternyata perhatian kecil bisa bikin semuanya terasa dekat.','senyum')])
    Scene(story,'V469-C03-COOK-CALLBACK-BLUR','Yang Tidak Kabur','shared','dapur',[
        ('arland','Fotonya agak kabur. Tapi sore itu aku ingat jelas.'),
        ('sofia','Aku juga. Bukan karena hasil fotonya, tapi karena kita di sana.')])
    Scene(story,'V469-C03-CORNER-PHOTO','Foto di Tengah','sofia','sofia_room',[
        ('sofia','Aku pilih foto untuk bagian tengah. Biar waktu lelah, aku ingat kami pernah ketawa sampai sakit perut.'),
        ('narrator','Sofia merapikan ujung kertas agar cahaya foto tidak menutupi tulisan kenangan.')])
    Scene(story,'V469-C03-CORNER-FLOWER','Bunga di Tengah','sofia','sofia_room',[
        ('sofia','Bunga ini belum tentu bertahan lama. Tapi maksud di baliknya masih bisa kusimpan.'),
        ('narrator','Di bawah bunga kering, Sofia menulis tanggal yang tidak akan dilupakan.')])
    Scene(story,'V469-C03-CORNER-BOOK','Halaman di Tengah','sofia','sofia_room',[
        ('sofia','Aku taruh Memory Book di tengah, tapi aku ingin tetap bisa menulis di buku milikku sendiri.'),
        ('narrator','Satu halaman tiba-tiba berubah lebih pucat; Sofia memutuskan tidak menebak penyebabnya dulu.')])

    Scene(story,'V469-C03-HALF-A','Di Balik Catatan Resep','arland','dapur',[
        ('narrator','Di balik kertas resep ada separuh surat. Tinta pada kata terakhir pudar, seolah terhapus udara.'),
        ('arland','"Aku nggak butuh sesuatu yang besar..." Sisanya hilang.'),
        ('arland','Apa aku terlalu sering berpikir bahwa melakukan banyak hal selalu berarti hadir?'),
        ('narrator','Pemain memilih cara Arland menyimpan kalimat yang belum selesai, bukan menebak isi surat.')],
        [Ch('Simpan surat dan tanyakan ketika Sofia siap','V469_A_LETTER_ASK',
            [('arland','Aku bakal tanya langsung saat waktunya tepat. Bukan menyimpulkan sendiri.','serius')],
            [('arland','Aku akan denger dulu sebelum menebak.')]),
         Ch('Tulis pertanyaan di belakang resep','V469_A_LETTER_NOTE',
            [('arland','Kalimat yang nggak selesai tetap harus punya tempat untuk dijawab.','senyum')],
            [('arland','Aku tidak ingin melupakan pertanyaan penting ini.')])],flags=['HALF_LETTER_FOUND'])
    Scene(story,'V469-C03-HALF-S','Sisi Kertas yang Belum Selesai','sofia','dapur',[
        ('narrator','Di bawah kertas resep, Sofia melihat tulisan tangannya yang belum pernah selesai.'),
        ('sofia','"Aku nggak butuh sesuatu yang besar..." Kenapa aku berhenti nulis waktu itu?'),
        ('sofia','Mungkin aku takut kalau bilang aku cuma butuh ditemani, itu terdengar merepotkan.'),
        ('narrator','Tinta memudar sebelum kalimat selesai. Sofia menyimpan kertasnya tanpa memaksa jawaban.')],
        [Ch('Tulis kebutuhan dengan jujur','V469_S_LETTER_HONEST',
           [('sofia','Aku ingin seseorang hadir dan dengar ceritaku sampai selesai. Itu bukan permintaan yang salah.','serius')],
           [('sofia','Aku berhak bilang apa yang penting bagiku.')]),
         Ch('Simpan ruang agar nanti bisa bicara','V469_S_LETTER_WAIT',
           [('sofia','Aku butuh waktu. Tapi nanti aku akan coba ngomong, bukan hanya diam.','senyum')],
           [('sofia','Aku nggak harus sempurna waktu cerita.')])],flags=['HALF_LETTER_FOUND'])
    Scene(story,'V469-C03-PICNIC-REFLECTION','Makan yang Dibuat Berdua','shared','taman_kota',[
       ('narrator','Satu potong roti sedikit gosong. Sofia mengambilnya duluan.'),
       ('arland','Aku tadinya mau bikin yang rapi. Malah jadi begini.'),
       ('sofia','Aku senang kita bisa masak bareng, Land. Bukan karena rotinya mirip yang di foto resep.'),
       ('arland','Aku mau ingat kalimat itu. Kadang aku terlalu sibuk memperbaiki semuanya.'),
       ('narrator','Sejenak Memory Book menampilkan gambar kursi kecil tanpa seorang pun di atasnya.')],
       flags=['V469_C03_PICNIC_REFLECTED'])
    Scene(story,'V469-C03-GALLERY-CARD','Kartu Kecil Bertuliskan Nama','shared','galeri_komunitas',[
       ('narrator','Di meja pendaftaran ada undangan pameran dan jadwal dimulainya presentasi.'),
       ('sofia','Aku masih agak gugup. Tapi aku senang akhirnya bisa nunjukin gambarku.'),
       ('arland','Aku dengar acaranya mulai tepat waktu. Aku mau ada di sini untuk dengerin kamu.'),
       ('narrator','Pemain menaruh undangan di samping kursi yang disiapkan. Tidak ada teka-teki yang harus dipaksakan.')],
       [Ch('Tanyakan bagian presentasi yang paling membuat gugup','V469_GALLERY_ASK',
          [('arland','Bagian mana yang paling bikin kamu gugup? Aku pengen ngerti.'),('sofia','Waktu harus cerita kenapa aku gambar kursi itu.','khawatir')],
          [('sofia','Aku takut pas harus cerita di depan orang. Tapi aku ingin kamu tahu rasanya.'),('arland','Aku akan mendengarkan.')]),
        Ch('Catat waktu dan tempat duduk dengan jelas','V469_GALLERY_SCHEDULE',
          [('arland','Aku tulis jam dan tempat duduk. Jangan sampai cuma di kepala.'),('sofia','Makasih. Aku bakal cari kamu dari panggung.')],
          [('sofia','Jamnya sudah kutulis. Aku pengen kita sama-sama ingat.'),('arland','Aku catat juga, Sof.')])],flags=['V469_GALLERY_CARD_DONE'])
    Scene(story,'V469-C03-PROJECTOR-REFLECT','Niat yang Mulai Terburu-buru','arland','galeri_komunitas',[
        ('arland','Seandainya proyektor lama ini bisa menampilkan sketsa Sofia bergerak...'),
        ('narrator','Arland menengok kursi yang tadi ia bantu siapkan.'),
        ('arland','Aku bilang aku datang buat dia. Semoga aku nggak melupakan apa yang sebenarnya dia minta.'),
        ('narrator','Kabel proyektor tampak aus. Arland mencatat masalah itu, bukan memperbaikinya sekarang.')],
        [Ch('Catat batas waktu sebelum mencoba membantu','V469_A_GALLERY_TIMER',
         [('arland','Aku harus mengutamakan janji datang, bukan mengerjakan semua hal sendiri.','serius')],
         [('arland','Aku akan catat waktunya dulu.')]),
         Ch('Tanyakan izin sebelum membuat perubahan pada karya','V469_A_GALLERY_PERMISSION',
         [('arland','Kalau aku mau bantu, aku harus tanya Sofia dulu. Ini karya dia.','serius')],
         [('arland','Karyanya milik Sofia; aku nggak boleh berasumsi.')])])
    Scene(story,'V469-C03-SKETCH-REFLECT','Halaman yang Belum Siap Dibaca','sofia','galeri_komunitas',[
        ('sofia','Ternyata gantung satu gambar di depan orang aja butuh keberanian.'),
        ('narrator','Sofia melihat sketsa dua kursi. Ia masih belum yakin bisa menjelaskan mengapa gambarnya penting.'),
        ('sofia','Aku mau Arland lihat hasil kerjaku. Tapi aku juga perlu bilang kalau kehadirannya penting buatku.')],
        [Ch('Sampaikan harapan secara langsung','V469_S_GALLERY_DIRECT',
         [('sofia','Land, aku pengen kamu ada di situ waktu aku mulai ngomong. Aku gugup.','serius'),('arland','Aku dengar, Sof.')],
         [('sofia','Aku butuh kamu duduk di sana, Land. Itu penting buatku.','serius')]),
         Ch('Tulis pesan pendek di undangan','V469_S_GALLERY_CARD',
         [('sofia','Aku tulis satu kalimat di belakang undangannya, supaya aku nggak kehilangan kata.','senyum')],
         [('sofia','Kalau gugup, surat kecil ini akan bantu aku cerita nanti.')])])
    Scene(story,'V469-C03-GALLERY-FORESHADOW','Sebelum Galeri Menjadi Sepi','shared','galeri_komunitas',[
       ('narrator','Sore itu, semua kursi masih kosong. Tidak ada yang tahu kursi mana yang akan paling diingat.'),
       ('sofia','Makasih sudah bantu hari ini, Land.'),
       ('arland','Aku senang bisa bantu. Besok aku pengen lihat kamu cerita tentang gambarmu.'),
       ('narrator','Kamera tertahan sebentar pada kartu nama di sebuah kursi.'),
       ('narrator','Satu garis tinta pada halaman Memory Book memudar, lalu berhenti seperti sedang menunggu kalimat berikutnya.')],
       flags=['V469_C03_GALLERY_PREPARED'])

    # Source chapters 1–2 remembered during mandatory Chapter-3 cooking.
    for st in ['C03_A_IDEA','C03_S_CORNER']:
        old=steps[st]['interactables'][0]
        if st=='C03_A_IDEA':
            old['actions']=[A('scene',id='C03-A00'),
                Cond('V468_A_INVITE_SIMPLE',[A('scene',id='V469-C03-A-INVITE-SIMPLE')]),
                Cond('V468_A_INVITE_CARE',[A('scene',id='V469-C03-A-INVITE-CARE')]),
                Cond('V468_A_INVITE_OPEN',[A('scene',id='V469-C03-A-INVITE-OPEN')]),
                A('step',id='V469_C03_A_FRAME')]
        else:old['actions']=[A('scene',id='C03-S00'),A('scene',id='C03-S01'),
                Cond('V468_S_REPLY_YES',[A('scene',id='V469-C03-S-DATE-YES')]),
                Cond('V468_S_REPLY_LATER',[A('scene',id='V469-C03-S-DATE-LATER')]),
                Cond('V468_S_REPLY_NO',[A('scene',id='V469-C03-S-DATE-NO')]),
                A('step',id='V469_C03_S_SCRAP')]
    newsteps=[
       Step('V469_C03_A_FRAME',{'arland':'Susun foto dan perbaiki bingkai di meja Arland'},[
           It('v469_frame','arland_room',711,388,'Rapikan bingkai foto',[
             A('scene',id='V469-C03-A-FRAME-BEGIN'), A('minigame',id='scrapbook'),
             A('scene',id='V469-C03-A-FRAME-DONE'),A('scene',id='C03-FREE@$ROUTE'),A('item',id='v469_frame'),
             A('step',id='C03_FREE')],rt='arland')]),
       Step('V469_C03_S_SCRAP',{'sofia':'Susun halaman scrapbook secara interaktif'},[
           It('v469_scrap','sofia_room',505,686,'Susun halaman kenangan',[
             A('scene',id='V469-C03-S-SCRAP-BEGIN'),A('minigame',id='scrapbook'),
             A('scene',id='V469-C03-S-SCRAP-DONE'),A('scene',id='C03-FREE@$ROUTE'),A('item',id='v469_scrapbook'),
             A('step',id='C03_FREE')],rt='sofia')]),
       Step('V469_C03_NEIGHBOR',{'arland':'Kembalikan mangkuk pinjaman ke Pak Harun di perumahan',
            'sofia':'Kembalikan buku sketsa ke Bu Laras di perpustakaan'},[
           It('v469_return_a','perumahan',510,555,'Kembalikan mangkuk Pak Harun',[
             A('scene',id='V469-C03-A-NEIGHBOR'),A('item',id='v469_neighbor_note'),A('step',id='C03_A_INGREDIENTS')],rt='arland',r=110),
           It('v469_return_s','perpustakaan',602,510,'Kembalikan buku Bu Laras',[
             A('scene',id='V469-C03-S-NEIGHBOR'),A('item',id='v469_neighbor_note'),A('step',id='C03_S_DECOR')],rt='sofia',r=110)]),
       Step('V469_C03_HALF_LETTER',{'arland':'Baca catatan di balik resep setelah memasak',
          'sofia':'Periksa separuh surat yang ditemukan di dapur'},[
           It('v469_half_a','dapur',385,380,'Baca potongan surat',[
              A('music',id='cinema_small_things_v469'),A('sfx',id='v469_pencil'),
              A('scene',id='V469-C03-HALF-A'),A('item',id='v469_half_letter'),
              A('step',id='C03_PICNIC')],rt='arland'),
           It('v469_half_s','dapur',385,380,'Baca catatan yang belum selesai',[
              A('music',id='cinema_small_things_v469'),A('sfx',id='v469_pencil'),
              A('scene',id='V469-C03-HALF-S'),A('item',id='v469_half_letter'),
              A('step',id='C03_PICNIC')],rt='sofia')])
    ]
    # C03 free activity retains its two-stop original counter logic.
    free=steps['C03_FREE']['complete']['actions']
    free[:]=[A('flag',id='C03_FREE_DONE'),A('toast',text='Pasar mulai sepi. Ada satu janji kecil yang harus diselesaikan.'),
            A('step',id='V469_C03_NEIGHBOR')]
    # Original ingredient/decor interactions could be tapped repeatedly. Mark the
    # exact hideIfFlag after success, without altering original item/counter IDs.
    for sid in ('C03_A_INGREDIENTS','C03_S_DECOR'):
        for it in steps[sid]['interactables']:
            fl=it['hideIfFlag']
            it['actions']=[a for a in it['actions'] if not(a.get('do')=='flag' and a.get('id')==fl)]
            it['actions'].append(A('flag',id=fl))
    # Real scrapbook result influences later private dialogue during arrangement.
    arrange=steps['C03_S_ARRANGE']['interactables'][0]
    arrange['actions']=[A('scene',id='C03-S02'),
       Cond('C03_CORNER_PHOTO',[A('scene',id='V469-C03-CORNER-PHOTO')]),
       Cond('C03_CORNER_FLOWER',[A('scene',id='V469-C03-CORNER-FLOWER')]),
       Cond('C03_CORNER_BOOK',[A('scene',id='V469-C03-CORNER-BOOK')]),
       A('flag',id='V469_S_CORNER_ARRANGED'),A('sfx',id='sparkle'),A('step',id='C03_S_KITCHEN')]
    # FIX critical pre-existing softlock: if the last collected ingredient is
    # inside the kitchen, an enterArea-only quest cannot advance (the player is
    # ALREADY inside the target area). Explicit player-triggered interactions
    # work both when entering from the street and when resuming a saved step.
    for kitchen_id,scene_id,object_id in [
        ('C03_A_KITCHEN','C03-A01','v469_kitchen_arrive_a'),
        ('C03_S_KITCHEN','C03-S06','v469_kitchen_arrive_s')]:
        kitchen=steps[kitchen_id]
        actions=kitchen['enterArea']['actions'] if 'enterArea' in kitchen else kitchen['interactables'][0]['actions']
        kitchen.pop('enterArea',None)
        kitchen['interactables']=[It(object_id,'dapur',385,380,
            'Temui pasangan dan mulai memasak',actions,r=76)]
    # Cooking minigame already exists and can be retried. Add photo memory and
    # actual C02 perspective callbacks once only on successful completion.
    cook=steps['C03_COOK']['interactables'][0]
    cook['actions']=[A('minigame',id='cooking'),
       Cond('V468_C02_PHOTO_LAUGH',[A('scene',id='V469-C03-COOK-CALLBACK-LAUGH')]),
       Cond('V468_C02_PHOTO_LOOK',[A('scene',id='V469-C03-COOK-CALLBACK-LOOK')]),
       Cond('V468_C02_PHOTO_BLUR',[A('scene',id='V469-C03-COOK-CALLBACK-BLUR')]),
       A('scene',id='C03-X01'),A('item',id='roti_lapis'),A('flag',id='C03_COOKED'),
       A('step',id='C03_V26_DETAILS')]
    steps['C03_V26_DETAILS']['complete']['actions']=[A('flag',id='V26_C03_FINISHED'),
      A('step',id='V469_C03_HALF_LETTER')]
    picnic=steps['C03_PICNIC']['interactables'][0]
    picnic['actions']=[A('scene',id='C03-X02'),A('scene',id='V469-C03-PICNIC-REFLECTION'),
        A('removeItem',id='roti_lapis'),A('scene',id='V464-C03-PROMISE'),
        A('warp',area='galeri_komunitas',x=480,y=532,dir='up'),
        A('step',id='C03_V464_GALLERY_PREP')]
    gallery=steps['C03_V464_GALLERY_PREP']
    originals={it['id']:it for it in gallery['interactables']}
    seat=originals['gallery_seat']; projector=originals['gallery_projector']
    seat['actions']=[A('scene',id='V464-C03-SEAT'),A('flag',id='V464_PREP_SEAT_DONE'),
                      A('count',id='v464_gallery_prep',add=1)]
    projector['actions']=[Route('arland',[A('scene',id='V464-C03-PROJECTOR'),
          A('scene',id='V469-C03-PROJECTOR-REFLECT')],
          [A('scene',id='V464-C03-SKETCH'),A('scene',id='V469-C03-SKETCH-REFLECT')]),
          A('flag',id='V464_PREP_ART_DONE'),A('count',id='v464_gallery_prep',add=1)]
    card=It('v469_gallery_card','galeri_komunitas',480,320,'Atur undangan dan jadwal galeri',[
        A('scene',id='V469-C03-GALLERY-CARD'),A('item',id='v469_gallery_invitation'),
        A('flag',id='V469_GALLERY_INVITE_DONE'),A('count',id='v464_gallery_prep',add=1)],r=115,
        when={'notFlags':['V469_GALLERY_INVITE_DONE']})
    gallery['interactables']=[seat,projector,card]
    gallery['objective']={'arland':'Tata kursi, catat undangan, dan periksa proyektor di Galeri Komunitas (0/3)',
       'sofia':'Tata kursi, siapkan karya, dan catat undangan galeri (0/3)'}
    gallery['complete']['count']=3
    old_complete=gallery['complete']['actions']
    idx=next(i for i,a in enumerate(old_complete) if a.get('do')=='chapterEnd')
    gallery['complete']['actions']=[A('music',id='cinema_gallery_promise_v469'),
       A('cine',cmds=[{'c':'bars','on':True,'t':0.45},
                        {'c':'shot','type':'wide','x':480,'y':335,'zoom':1.16,'t':1.2},
                        {'c':'fx','id':'book','x':480,'y':320,'t':1.6},
                        {'c':'wait','t':0.9},{'c':'bars','on':False,'t':0.45}]),
       A('scene',id='V469-C03-GALLERY-FORESHADOW'),A('scene',id='V464-C03-END'),
       *old_complete[idx:]]

    # New memories live as separate optional flags; old unlock behavior unchanged.
    book['entries']=[x for x in book['entries'] if not x['id'].startswith('v469_c03_')]
    for iid,title,icon,desc in [
       ('v469_frame','Bingkai yang Tetap Berarti','v469_c03_frame','Bingkai foto dengan retak kecil yang tidak perlu disembunyikan.'),
       ('v469_scrapbook','Scrapbook Sofia','v469_c03_scrapbook','Halaman kenangan yang ditata sendiri oleh Sofia.'),
       ('v469_half_letter','Separuh Surat di Balik Resep','v469_c03_letter','Kalimat yang belum sempat diselesaikan dan bukan untuk ditebak.'),
       ('v469_neighbor_note','Catatan Tetangga','v469_c03_scrapbook','Benda pinjaman yang dikembalikan bersama sebuah pelajaran tentang janji.'),
       ('v469_gallery_invitation','Undangan Galeri','v469_c03_invitation','Jadwal pameran dan satu kursi yang disiapkan untuk Arland.')]:
        book['items'][iid]={'name':title,'icon':'items/'+icon+'.png','desc':desc}
    for route,flag,title,text,icon in [
      ('arland','V469_A_FRAME_DONE','Bingkai yang Dirawat','Yang rusak bisa diperbaiki tanpa menghapus cerita yang pernah terjadi.','v469_c03_frame'),
      ('sofia','V469_S_SCRAP_DONE','Halaman yang Milik Sofia','Tidak semua hal yang berharga perlu dijelaskan kepada orang lain.','v469_c03_scrapbook'),
      ('arland','V469_A_NEIGHBOR_DONE','Janji Mengembalikan','Arland diingatkan bahwa menepati janji berarti juga memberi kabar.','v469_c03_letter'),
      ('sofia','V469_S_NEIGHBOR_DONE','Kata yang Berani Dikatakan','Sofia mulai berani menyampaikan kebutuhan sebelum merasa kecewa.','v469_c03_letter'),
      ('shared','HALF_LETTER_FOUND','Kalimat yang Terputus','"Aku nggak butuh sesuatu yang besar..." — sisanya belum disampaikan.','v469_c03_letter'),
      ('shared','V469_C03_GALLERY_PREPARED','Kursi yang Belum Terisi','Sebuah nama, sebuah janji, dan tempat duduk yang belum menjadi kenangan.','v469_c03_invitation')]:
        mem(book,'v469_c03_'+flag.lower(),route,flag,title,text,icon)
    for rt,cases in [
      ('arland',[('V469_A_FRAME_SCAR','Retak yang Disimpan'),('V469_A_FRAME_REPAIR','Sudut yang Dikuatkan'),
                 ('V469_A_LETTER_ASK','Pertanyaan yang Akan Didengar'),('V469_A_LETTER_NOTE','Pertanyaan di Resep'),
                 ('V469_A_GALLERY_TIMER','Jam yang Dicatat'),('V469_A_GALLERY_PERMISSION','Izin yang Dipikirkan')]),
      ('sofia',[('V469_S_SCRAP_WORDS','Kata di Scrapbook'),('V469_S_SCRAP_SPACE','Ruang pada Halaman'),
                ('V469_S_LETTER_HONEST','Aku Boleh Meminta'),('V469_S_LETTER_WAIT','Waktu untuk Bercerita'),
                ('V469_S_GALLERY_DIRECT','Aku Butuh Kamu Hadir'),('V469_S_GALLERY_CARD','Pesan pada Undangan')])]:
        for flag,title in cases:mem(book,'v469_c03_'+flag.lower(),rt,flag,title,
             'Pilihan pribadi ini mengubah bagaimana tokoh menyimpan kenangan dan berbicara pada chapter berikutnya.',
             'v469_c03_letter','optional_story_branch')
    for flag,title in [('V469_GALLERY_ASK','Bertanya Sebelum Menebak'),('V469_GALLERY_SCHEDULE','Waktu yang Tercatat')]:
        mem(book,'v469_c03_'+flag.lower(),'shared',flag,title,
            'Mereka mencoba mempersiapkan sesuatu tanpa kehilangan kesempatan untuk saling mendengar.',
            'v469_c03_invitation','optional_story_branch')
    for flag,title in [('C03_CORNER_PHOTO','Foto di Tengah'),('C03_CORNER_FLOWER','Bunga di Tengah'),
                       ('C03_CORNER_BOOK','Buku di Tengah')]:
        mem(book,'v469_c03_'+flag.lower(),'sofia',flag,title,
           'Sofia menentukan apa yang paling ingin ia lihat setiap pagi.','v469_c03_scrapbook','optional_story_branch')
    # Add only new steps. Deterministic order and idempotency under rebuild.
    q['steps']=[st for st in q['steps'] if not st['id'].startswith('V469_C03_')]
    where=next(i for i,st in enumerate(q['steps']) if st['id']=='C03_A_IDEA')
    q['steps'][where:where]=newsteps
    for name,data in [('story.json',story),('quests.json',q),('memory_book.json',book)]:
        (DATA/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8')
    print('PASS: Chapter-3 story patch complete: 4 playable quest stages + route-only choices + gallery prep + half letter')
if __name__=='__main__':apply()
