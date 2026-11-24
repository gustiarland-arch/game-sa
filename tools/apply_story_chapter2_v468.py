#!/usr/bin/env python3
"""Chapter 2 Overhaul v4.6.8 draft. Apply after v4.6.7 chapter-1 patch.

Idempotent JSON story/quest/book update. No deletion of legacy story IDs or saves.
Real consent-respecting accept/postpone/decline routes, route-specific errands,
original photo canon, Chapter-1 callbacks, and cross-chapter story flags.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'android/assets/data'

def A(cmd, **kw): return {'do':cmd, **kw}
def C(flag, then, otherwise=None): return A('if',when={'flags':[flag]},then=then, **{'else':otherwise or []})
def route(r,then,otherwise=None): return A('if',when={'route':r},then=then,**{'else':otherwise or []})
def L(w,t,e='neutral'): return {'s':w,'t':t,'e':e}
def choice(text,flag, r_a, r_s):
    return {'text':text,'flags':[flag], 'byRoute':{
        'arland':[L(*row) for row in r_a],
        'sofia':[L(*row) for row in r_s]}}

def scene(story,id,title,route,lines,place='',choices=None,flags=None):
    story['scenes'][id]={'title':title,'route':route,'chapter':'C02','location':place,
        'trigger':'V468 interactive story','lines':[L(*x) for x in lines],
        'choices':choices or [],'flags':flags or [],
        'note':'Draft Chapter 2 Overhaul: not new canon ending.'}

def step(id, objective, interactions, quest='Q_V468_C02_DECISION', **kw):
    return {'id':id,'chapter':'C02','quest':quest,
        'objective':objective,'interactables':interactions,**kw}

def point(id,area,x,y,label,acts,route_id=None,**kw):
    out={'id':id,'area':area,'x':x,'y':y,'r':90,'label':label,'actions':acts,**kw}
    if route_id:out['route']=route_id
    return out

# Original full-day activity minigames remain, but alternative routes choose
# WHEN and HOW to reunite rather than pretending Sofia accepted immediately.

def apply():
    story=json.loads((DATA/'story.json').read_text(encoding='utf-8'))
    quests=json.loads((DATA/'quests.json').read_text(encoding='utf-8'))
    book=json.loads((DATA/'memory_book.json').read_text(encoding='utf-8'))
    steps={x['id']:x for x in quests['steps']}
    assert all(k in steps for k in ('C02_PHONE','C02_FREE','C02_A_FLORIST','C02_S_OUTFIT',
             'C02_S_PRINT','C02_TO_CAFE','C02_V464_INTERLUDE','C02_DATE','C02_SUNSET'))
    assert all(k in story['scenes'] for k in ('C02-X01','C02-X02','C02-X03','C02-X04',
          'V464-C02-WALK-A','V464-C02-WALK-S','V464-C02-LATER','V464-C02-GALLERY-TEASE'))
    story['meta']['chapter2Overhaul']='v4.6.8 draft / choice-respecting three date schedules, route memory and Lantern clue'

    scene(story,'V468-C02-A-INVITE','Menawarkan Waktu, Bukan Meminta Jawaban','arland',[
        ('narrator','Pesan Sofia belum terbaca. Arland menatap tiga versi kalimat yang ia ketik lalu hapus.'),
        ('arland','Aku pengen jalan sama Sofia, tapi aku nggak mau dia merasa harus selalu bilang iya.'),
        ('narrator','Ia memilih bagaimana menyampaikan ajakan, lalu menekan Kirim.')], 'arland_room', [
        choice('Ajak secara langsung dan sederhana','V468_A_INVITE_SIMPLE',
               [('arland','Sof, nanti kalau sempat, mau jalan bareng aku? Kalau kamu lagi sibuk nggak apa-apa.','senyum')],
               [('arland','Sof, nanti kalau sempat, mau jalan bareng aku?','senyum')]),
        choice('Tanya dulu apakah Sofia ingin istirahat','V468_A_INVITE_CARE',
               [('arland','Kalau kamu capek, kita bisa jalan lain hari. Hari ini kamu butuh istirahat nggak?','senyum')],
               [('arland','Kalau capek, kita bisa lain hari.','senyum')]),
        choice('Ceritakan rencana, lalu serahkan waktu padanya','V468_A_INVITE_OPEN',
               [('arland','Aku kepikiran taman sama photobooth. Tapi kamu bebas pilih kapan dan mau yang mana.','senyum')],
               [('arland','Aku kepikiran taman sama photobooth. Kamu bebas pilih kapan.','senyum')])])
    scene(story,'V468-C02-S-REPLY','Sofia yang Memilih','sofia',[
        ('narrator','Ponsel Sofia berbunyi saat ia sedang menyelesaikan sebuah sketsa. Arland mengajaknya jalan sore.'),
        ('sofia','Aku senang dia ngajak. Tapi aku juga harus jujur sama jadwalku dan perasaanku.'),
        ('narrator','Jawaban ini adalah keputusan Sofia sendiri, bukan ukuran seberapa besar ia menyayangi Arland.')],
        'sofia_room',[
        choice('Aku mau ikut sore ini','V468_S_REPLY_YES',
               [('sofia','Aku mau ikut. Sampai nanti ya!','senang')],
               [('sofia','Iya, Land, aku ikut sore ini. Aku juga mau cerita sesuatu.','senyum')]),
        choice('Besok saja ya, hari ini aku perlu waktu','V468_S_REPLY_LATER',
               [('sofia','Kalau besok gimana? Aku pengen selesaikan beberapa hal dulu.','senyum')],
               [('sofia','Besok ya? Hari ini aku lagi perlu waktu buat gambar dan istirahat.','senyum')]),
        choice('Maaf, aku tidak ingin jalan hari ini','V468_S_REPLY_NO',
               [('sofia','Maaf, hari ini aku nggak bisa ikut. Aku butuh waktu sendiri dulu.','neutral')],
               [('sofia','Maaf, Land. Hari ini aku mau sendiri dulu. Makasih sudah ngajak.','neutral')])])
    scene(story,'V468-C02-A-REPLY','Jawaban yang Dihargai','arland',[
        ('narrator','Sofia membalas pesan. Ia mengatakan bahwa ia bisa bertemu sebentar hari ini.'),
        ('sofia','Aku bisa sore ini, Land. Tapi kita jalan santai aja, ya.'),
        ('arland','Boleh. Kamu juga boleh bilang kalau tiba-tiba butuh istirahat.'),
        ('narrator','Arland menyimpan ponsel. Ajakan yang baik tidak mengikat siapa pun.')],'arland_room')
    scene(story,'V468-C02-S-LATER-START','Boleh Meminta Besok','sofia',[
        ('narrator','Sofia duduk di kafe, mengatur kembali jadwalnya tanpa merasa harus meminta maaf karena butuh waktu.'),
        ('sofia','Aku mau ketemu Arland kalau aku bisa hadir sepenuhnya. Bukan karena merasa nggak enak menolak.'),
        ('narrator','Ia menandai hari berikutnya di kartu jadwal kecil.')], 'cafe')
    scene(story,'V468-C02-S-LATER-NOTE','Pesan untuk Esok','sofia',[
        ('sofia','Land, aku sudah lebih longgar besok. Mau ketemu di kafe? Aku yang datang duluan.'),
        ('arland','Boleh banget. Makasih udah bilang dengan jelas. Aku nggak keberatan nunggu.'),
        ('narrator','Sofia menyiapkan kartu kecil sebagai penanda: menunda bukan berarti menghilang.')], 'cafe',flags=['V468_C02_LATER_NOTE_DONE'])
    scene(story,'V468-C02-S-NO-START','Tidak Hari Ini','sofia',[
        ('narrator','Sofia memesan minuman sendiri. Ponsel di meja tidak terus-menerus ia periksa.'),
        ('sofia','Aku sayang Arland. Tapi aku juga butuh sore yang tenang untuk diriku.'),
        ('narrator','Dari jendela kafe, terlihat pintu Galeri Komunitas yang baru saja dicat.'),
        ('sofia','Kalau aku lanjut menggambar di sana, mungkin ide yang tadi buntu bisa jalan lagi.')], 'cafe')
    scene(story,'V468-C02-S-NO-SKETCH','Gambar yang Boleh Diselesaikan Sendiri','sofia',[
        ('narrator','Galeri masih kosong. Sofia memilih duduk dekat jendela, jauh dari keramaian.'),
        ('sofia','Dua kursi, satu meja... tapi kali ini aku mau menggambar ruang di antara keduanya.'),
        ('narrator','Di kertas, ia menyisakan tempat untuk sesuatu yang belum ia ketahui.'),
        ('sofia','Aku nggak harus mengisi semua ruang kosong hari ini.'),
        ('narrator','Sofia menyimpan sketsa itu sebagai kenangan pribadi, bukan sebuah hadiah yang wajib diberikan.')],
        'galeri_komunitas',flags=['V468_C02_SOLO_SKETCH_DONE'])
    scene(story,'V468-C02-S-NEW-INVITE','Mengajak Kembali karena Ingin','sofia',[
        ('narrator','Sore semakin sepi. Setelah waktunya sendiri, Sofia akhirnya ingin bertemu Arland.'),
        ('sofia','Aku nggak mau orang lain yang menentukan kapan aku siap. Sekarang aku tahu aku pengen ketemu dia.'),
        ('narrator','Sofia memilih ajakan baru dengan bahasanya sendiri.')], 'sofia_room',[
        choice('Besok, mau lihat hasil gambarku di taman?','V468_S_REINVITE_PARK',
               [('sofia','Besok kita lihat taman? Aku mau tunjukin gambar baruku.','senyum')],
               [('sofia','Besok boleh ke taman? Aku pengen cerita soal gambar hari ini.','senyum')]),
        choice('Besok, mau temani aku ke photobooth?','V468_S_REINVITE_PHOTO',
               [('sofia','Besok mau cari foto yang lucu di arcade?','senang')],
               [('sofia','Kalau besok, boleh temani aku foto? Aku yang ngajak sekarang.','senyum')])])
    scene(story,'V468-C02-S-REUNION','Janji yang Dipilih Bersama','sofia',[
        ('narrator','Hari baru. Arland sudah tiba di Kafe Senja, tetapi ia menunggu Sofia memilih tempat duduk sendiri.'),
        ('arland','Makasih udah ngajak hari ini, Sof. Kemarin aku nggak keberatan kok.'),
        ('sofia','Makasih udah ngerti. Aku jadi pengen jalan karena memang mau, bukan karena harus.'),
        ('arland','Kita mulai pelan-pelan aja. Mau ke taman atau lihat foto dulu?'),
        ('sofia','Boleh dua-duanya. Tapi kalau capek kita istirahat, ya.'),
        ('narrator','Mereka berangkat di hari yang mereka sepakati bersama.')], 'cafe',flags=['V468_C02_REUNITED'])
    scene(story,'V468-C02-SOFT-SKETCH','Persiapan Pameran Kecil','shared',[
        ('sofia','Aku lagi gambar sesuatu buat pameran komunitas. Bukan sesuatu yang besar, cuma penting buatku.'),
        ('arland','Kalau nanti kamu siap nunjukin, aku mau lihat. Aku nggak akan mengatur gambar kamu.'),
        ('sofia','Makasih. Nanti aku kabarin kapan acaranya.'),
        ('narrator','Sofia menandai satu halaman dengan simbol kursi kecil. Halaman itu tidak dibuka sekarang.')],
        'cafe',flags=['V468_C02_EXHIBITION_FORESHADOW'])

    # Rework the earlier in-cafe choices to be non-contradictory with the
    # actual yes/later/no response on the phone.
    walk_a=story['scenes']['V464-C02-WALK-A']
    walk_a['lines']=[L('arland','Sof, buat sore ini kamu mau jalan santai atau ngobrol dulu?'),
                     L('sofia','Pelan-pelan aja. Aku senang kalau kita bisa memutuskan bareng.'),
                     L('narrator','Pilih kegiatan yang terasa nyaman, bukan nilai cinta.')]
    walk_a['choices']=[
      choice('Ajak jalan ke taman','V464_WALK_PARK',[('arland','Taman dulu, ya. Aku bawa air minum.','senyum')],[('arland','Taman dulu, ya.')]),
      choice('Duduk dan mengobrol dulu','V464_WALK_LATER',[('arland','Kita nggak perlu buru-buru. Duduk sebentar, yuk.','senyum')],[('arland','Duduk sebentar dulu, yuk.')]),
      choice('Dengarkan ide Sofia sebelum menentukan rute','V464_WALK_ASK',[('arland','Kamu lagi pengen apa hari ini, Sof?','senyum')],[('arland','Kamu pengen apa hari ini?')])]
    walk_s=story['scenes']['V464-C02-WALK-S']
    walk_s['lines']=[L('arland','Sof, makasih ya sudah mau jalan hari ini.'),
                     L('sofia','Aku memang pengen ikut. Tapi aku juga mau pilih caranya.'),
                     L('narrator','Sofia memilih kegiatan sore yang nyaman baginya.')]
    walk_s['choices']=[
      choice('Jalan di taman dulu','V464_WALK_PARK',[('sofia','Taman dulu, ya.','senyum')],[('sofia','Taman dulu, Land. Biar ada udara segar.','senang')]),
      choice('Selesaikan satu sketsa kecil, lalu jalan','V464_WALK_SOLO',[('sofia','Aku selesaiin gambar sebentar ya.','senyum')],[('sofia','Aku mau selesaikan satu sketsa, lalu kita jalan.','senyum')]),
      choice('Ngobrol di kafe sebelum jalan','V464_WALK_LATER',[('sofia','Kita duduk dulu di kafe?','senyum')],[('sofia','Duduk sebentar dulu, boleh? Ada yang mau aku ceritakan.','senyum')])]
    for sid,text in [
      ('V464-C02-LATER',[
         ('narrator','Mereka menyisihkan waktu untuk duduk tanpa melihat jam. Jalan-jalan tidak harus serba cepat.'),
         ('sofia','Aku suka kalau kamu nggak buru-buru, Land.'),
         ('arland','Aku juga suka kalau kamu bilang apa yang kamu butuh.'),
         ('narrator','Setelah minum, keduanya siap melanjutkan sore itu.')]),
      ('V464-C02-SOLO',[
         ('narrator','Sofia menyelesaikan garis terakhir di buku sketsanya. Arland memilih menunggu tanpa bertanya terus.'),
         ('sofia','Makasih sudah nunggu. Yang ini penting buatku.'),
         ('arland','Aku senang lihat kamu serius menggambar. Ayo, kita jalan kalau kamu sudah siap.'),
         ('narrator','Sofia menutup buku itu sendiri, lalu berdiri sambil tersenyum.')])]:
       story['scenes'][sid]['lines']=[L(*x) for x in text]

    # Original C02 scene is preserved but deepened; the two secret photo
    # viewpoints are shown as a physical glitch, not a lore reveal.
    scene(story,'V468-C02-CH1-LISTEN','Aku Mendengar, Bukan Menebak','shared',[
        ('sofia','Masih inget surat kafe? Aku senang kamu mau mendengar sebelum menarik kesimpulan.'),
        ('arland','Aku ternyata suka terburu-buru kalau sedang penasaran. Sekarang aku mau denger versi kamu.'),
        ('narrator','Dua orang duduk melihat danau, masing-masing menyimpan versi yang berharga.')], 'taman_kota')
    scene(story,'V468-C02-CH1-RECORD','Dua Cerita di Satu Kertas','shared',[
        ('sofia','Aku masih simpan catatan yang kita tulis dua sisi itu.'),
        ('arland','Yang bunga dan bintang? Jangan dilipat dulu, aku mau tambah cerita sore ini.'),
        ('narrator','Pada halaman yang sama, ada cukup tempat untuk dua tulisan.')], 'taman_kota')
    scene(story,'V468-C02-CH1-TRACE','Huruf yang Masih Memudar','shared',[
        ('sofia','Sejak surat itu, aku sering lihat tinta di buku ini seperti kehilangan warna.'),
        ('arland','Aku juga lihat. Tapi nggak semua yang aneh harus kita jawab hari ini.'),
        ('narrator','Di sudut halaman, satu garis pudar tampak seperti lentera kecil.')], 'taman_kota')
    scene(story,'V468-C02-GAZEBO','Yang Dihargai dari Hari Ini','shared',[
        ('narrator','Mereka duduk di dekat gazebo saat angin membawa aroma bunga dan suara air.'),
        ('sofia','Land, hal paling seru dari hari ini menurut kamu apa?'),
        ('arland','Aku mau jawab, tapi kayaknya aku perlu tahu dulu apa yang berarti buat kamu.'),
        ('narrator','Cara mereka menyampaikan perhatian bisa berbeda, tanpa ada jawaban yang dianggap salah.')],
        'taman_kota',[
        choice('Aku suka kita bisa tertawa bareng','V468_C02_GAZEBO_LAUGH',
            [('arland','Aku suka pas kita ketawa gara-gara hal sepele.','tertawa'),('sofia','Aku juga. Rasanya ringan.')],
            [('sofia','Aku suka kalau kita bisa ketawa tanpa harus lucu terus.','tertawa'),('arland','Aku setuju. Rasanya enak.')]),
        choice('Aku suka kita bisa diam tanpa canggung','V468_C02_GAZEBO_QUIET',
            [('arland','Aku suka diam sebentar di sini. Nggak merasa harus selalu melakukan sesuatu.'),('sofia','Aku nyaman sama kamu bahkan saat kita nggak ngomong.')],
            [('sofia','Aku nyaman meski nggak ada yang harus diomongin.'),('arland','Kita nggak perlu isi setiap detik, ya.')]),
        choice('Aku suka ketika kamu mendengarkan','V468_C02_GAZEBO_LISTEN',
            [('arland','Aku suka waktu kita saling mendengarkan tanpa berebut cerita.'),('sofia','Aku juga. Jadi lebih berani cerita.')],
            [('sofia','Aku suka waktu kamu dengerin aku sampai selesai.'),('arland','Aku mau belajar terus.')])])
    scene(story,'V468-C02-PHOTO-CHOICE','Foto yang Tidak Harus Sempurna','shared',[
        ('juna','Sebelum dicetak, pilih foto yang paling kalian suka! Bukan yang paling rapi.'),
        ('narrator','Tiga foto menampilkan tiga versi bahagia yang sama-sama nyata.'),
        ('arland','Aku kelihatan gugup di semuanya.'),
        ('sofia','Bagus dong. Berarti nggak dibuat-buat.')], 'arcade',[
        choice('Simpan foto saat keduanya tertawa','V468_C02_PHOTO_LAUGH',
              [('arland','Yang ini! Kita sama-sama ketawa sampai matanya nyipit.','tertawa')],
              [('sofia','Yang ini. Nggak rapi, tapi kita kelihatan bahagia.','tertawa')]),
        choice('Simpan foto saat saling menoleh','V468_C02_PHOTO_LOOK',
              [('arland','Kita malah nggak lihat kameranya, ya.','malu')],
              [('sofia','Aku suka yang ini. Kita saling lihat, bukan menunggu hitungan.','senyum')]),
        choice('Simpan foto pertama yang sedikit buram','V468_C02_PHOTO_BLUR',
              [('arland','Foto pertama buram, tapi aku inget kenapa kita ketawa.','senyum')],
              [('sofia','Justru foto buram ini yang paling kerasa seperti kita.','senyum')])])
    scene(story,'V468-C02-PHOTO-LANTERN','Cahaya yang Tidak Ada','shared',[
        ('narrator','Mesin photobooth berhenti berdengung. Pada cetakan kedua muncul cahaya lentera di belakang mereka.'),
        ('sofia','Land, di belakang kita ada apa? Tadi nggak ada lampu di sudut sana.'),
        ('arland','Aku ingat cahaya dari kiri, bukan kanan. Kamu lihat di mana?'),
        ('sofia','Di kananmu. Tapi di foto... dua-duanya muncul.'),
        ('narrator','Untuk sesaat, sudut kertas kehilangan warna. Lalu cahaya kembali, tanpa menyisakan jawaban.'),
        ('arland','Kita simpan dua salinannya. Mungkin nanti baru ngerti maksudnya.'),
        ('sofia','Iya. Jangan sampai cuma satu yang kita percaya.')], 'arcade',flags=['V468_C02_LANTERN_CLUE'])
    scene(story,'V468-C02-PAYOFF-YES','Sore yang Langsung Dipilih','sofia',[
        ('sofia','Aku senang tadi bilang iya karena memang ingin jalan.'),
        ('arland','Aku juga senang kamu nyaman cerita begitu. Makasih sudah bilang.')], 'riverside')
    scene(story,'V468-C02-PAYOFF-LATER','Kencan yang Tidak Dipaksa','sofia',[
        ('sofia','Kalau kemarin kita maksa ketemu, aku mungkin malah nggak bisa menikmati hari ini.'),
        ('arland','Besok ternyata tetap bisa indah. Aku nggak perlu selalu minta sekarang.')], 'riverside')
    scene(story,'V468-C02-PAYOFF-NO','Datang karena Memilih','sofia',[
        ('sofia','Aku sempat bilang nggak. Sekarang aku senang kita bisa jalan tanpa merasa bersalah.'),
        ('arland','Aku nggak pernah nganggep itu berarti kamu nggak sayang.'),
        ('narrator','Sofia menyimpan gambar yang dibuatnya sendirian. Ia tidak kehilangan apa-apa karena menolak satu ajakan.')], 'riverside')
    for name, lines in {
      'LAUGH':[('sofia','Aku masih denger suara kita ketawa dari foto itu.'),('arland','Aku malu, tapi itu foto favoritku.')],
      'LOOK':[('arland','Di foto kita malah saling lihat, bukan kamera.'),('sofia','Karena yang ada di depan kita lebih menarik.')],
      'BLUR':[('sofia','Fotonya buram, tapi aku ingat persis rasanya.'),('arland','Nggak semua yang bagus harus tajam, ya.')]
    }.items():
        scene(story,'V468-C02-PHOTO-MEMORY-'+name,'Foto yang Dipilih','shared',lines,'riverside')
    scene(story,'V468-C02-C01-AFTER','Dua Versi, Satu Sore','shared',[
        ('arland','Surat kafe itu masih bikin aku mikir, Sof.'),
        ('sofia','Aku juga. Setidaknya hari ini kita belajar kalau satu kejadian bisa terasa beda.'),
        ('narrator','Kenangan baru tidak menghapus yang lama. Ia memberi ruang untuk membacanya kembali.')], 'riverside')
    scene(story,'V468-C02-PHOTO-TECH','Mesin yang Hampir Mati','shared',[
        ('juna','Aduh, sekringnya longgar lagi. Bisa bantu aku cek panelnya di sebelah mesin?'),
        ('arland','Boleh. Tapi Sofia duluan yang pilih foto, aku bantu mesin sebentar aja.'),
        ('sofia','Aku tunggu di sini. Jangan sampai kejutan kecil bikin kamu lupa waktunya, ya.'),
        ('arland','Iya. Aku denger.'),
        ('narrator','Mesin kembali menyala. Arland tidak melupakan bahwa Sofia menunggu.')], 'arcade', flags=['V468_C02_PHOTO_FIXED'])

    # Rebuild C02 phone entry with actual reply at start rather than at the cafe.
    for it in steps['C02_PHONE']['interactables']:
        if it['route']=='arland':
            it['actions']=[A('sfx',id='page'),A('scene',id='V468-C02-A-INVITE'),
                A('scene',id='V468-C02-A-REPLY'),A('scene',id='C02-A00'),
                A('scene',id='C02-FREE@$ROUTE'),A('step',id='C02_FREE')]
        else:
            it['actions']=[A('sfx',id='page'),A('scene',id='V468-C02-S-REPLY'),
                           A('scene',id='C02-S00'),A('step',id='C02_S_OUTFIT')]

    # Sofia's first route-specific progression must be resolved BEFORE the
    # partner NPC is placed by C02_TO_CAFE. A decline never summons Arland to
    # the cafe and a postponed visit never accidentally becomes a same-day date.
    sofia_print=next(x for x in steps['C02_S_PRINT']['interactables'] if x['id']=='juna_print')
    sofia_print['actions']=[A('scene',id='C02-S02'),A('item',id='foto_kecil'),A('sfx',id='sparkle'),
       C('V468_S_REPLY_NO',[A('scene',id='V468-C02-S-NO-START'),A('step',id='V468_C02_NO_SKETCH')],
         [C('V468_S_REPLY_LATER',[A('scene',id='V468-C02-S-LATER-START'),
                                  A('step',id='V468_C02_LATER_NOTE')],
            [A('step',id='C02_TO_CAFE')])])]
    # The old Sofia introduction assumed she initiated the original invite.
    # It now confirms that her response belongs to her, not to the game.
    story['scenes']['C02-S00']['lines']=[
       L('sofia','Arland ngajak jalan. Aku senang, tapi aku mau jawab sesuai keadaan hari ini.'),
       L('sofia','Aku nggak harus selalu bilang iya supaya dia tahu aku sayang.'),
       L('narrator','Sofia menyiapkan harinya dengan tenang. Pilihannya tidak menghapus kisah mereka.')]

    # Existing native bouquet minigame is now a required Arland preparation
    # challenge rather than a decorative flower-selection dialogue.
    florist=next(x for x in steps['C02_A_FLORIST']['interactables'] if x['id']=='florist')
    florist['actions']=[A('scene',id='C02-A01'),A('minigame',id='bouquet'),
       A('item',id='bunga_pita'),A('flag',id='V468_C02_BOUQUET_MADE'),
       A('sfx',id='sparkle'),A('step',id='C02_TO_CAFE')]

    # Route distinctions are crucial: a declined invitation is NOT a date.
    # Old saves at C02_TO_CAFE without V468 flags use the old safe shared path.
    cafe=next(x for x in steps['C02_TO_CAFE']['interactables'] if x['id']=='date')
    normal_cafe=[A('scene',id='C02-X00'),A('scene',id='C02-X01'),
        route('arland',[A('scene',id='V464-C02-WALK-A')],[A('scene',id='V464-C02-WALK-S')]),
        A('scene',id='V464-C02-GALLERY-TEASE'),A('scene',id='V468-C02-SOFT-SKETCH'),
        A('companion',on=True),A('step',id='C02_V464_INTERLUDE')]
    cafe['actions']=[
        route('sofia',[
          C('V468_S_REPLY_NO',[A('scene',id='V468-C02-S-NO-START'),
              A('step',id='V468_C02_NO_SKETCH')],
            [C('V468_S_REPLY_LATER',[A('scene',id='V468-C02-S-LATER-START'),
                  A('step',id='V468_C02_LATER_NOTE')],normal_cafe)])
        ],normal_cafe)]

    # These are physical objectives in distinct maps, with an honest passage
    # of one in-game day. No invisible penalty for saying "not today".
    extra_steps=[
        step('V468_C02_LATER_NOTE',
             {'arland':'Tulis pesan untuk besok','sofia':'Tulis jadwal baru dan temui Arland besok'},
             [point('v468_later_note','cafe',655,408,'Tulis kartu rencana besok',[
                A('scene',id='V468-C02-S-LATER-NOTE'),A('item',id='v468_date_note'),
                A('restUntilTomorrow'),A('warp',area='sofia_room',x=609,y=740,dir='down'),
                A('step',id='V468_C02_REUNION')],route_id='sofia')]),
        step('V468_C02_NO_SKETCH',
             {'arland':'Gambar sendiri di Galeri Komunitas','sofia':'Kunjungi Galeri Komunitas dan selesaikan sketsamu sendiri'},
             [point('v468_solo_sketch','galeri_komunitas',530,327,'Menggambar di galeri',[
                A('music',id='cinema_date_choices_v468'),
                A('scene',id='V468-C02-S-NO-SKETCH'),A('item',id='v468_independent_sketch'),
                A('step',id='V468_C02_NO_REINVITE')],route_id='sofia')]),
        step('V468_C02_NO_REINVITE',
             {'arland':'Pikirkan jadwal baru','sofia':'Pulang dan putuskan sendiri apakah ingin mengajak Arland besok'},
             [point('v468_solo_note','sofia_room',735,433,'Menulis pesan dengan tenang',[
                A('scene',id='V468-C02-S-NEW-INVITE'),A('flag',id='V468_S_REINVITE_BY_CHOICE'),
                A('restUntilTomorrow'),A('step',id='V468_C02_REUNION')],route_id='sofia')]),
        step('V468_C02_REUNION',
             {'arland':'Temui pasangan di kafe','sofia':'Temui Arland di Kafe Senja pada hari yang baru'},
             [point('v468_reunion','cafe',841,560,'Temui Arland sesuai janji',[
                A('music',id='cinema_date_choices_v468'),
                A('scene',id='V468-C02-S-REUNION'),A('scene',id='C02-X00'),
                A('scene',id='C02-X01'),A('scene',id='V464-C02-GALLERY-TEASE'),
                A('scene',id='V468-C02-SOFT-SKETCH'),A('companion',on=True),
                A('step',id='C02_DATE')],route_id='sofia')],
             npcs=[{'who':'arland','area':'cafe','x':840,'y':560,'dir':'left'}])
    ]

    # The in-cafe original C02 choices still have three different playable
    # branch steps, but are no longer allowed to contradict a prior answer.
    gazebo=next(x for x in steps['C02_DATE']['interactables'] if x['id']=='gazebo')
    gazebo['actions']=[A('scene',id='V468-C02-GAZEBO'),
        C('V467_C01_RESULT_LISTEN',[A('scene',id='V468-C02-CH1-LISTEN')],[]),
        C('V467_C01_RESULT_RECORD',[A('scene',id='V468-C02-CH1-RECORD')],[]),
        C('V467_C01_RESULT_TRACE',[A('scene',id='V468-C02-CH1-TRACE')],[]),
        A('scene',id='C02-X03'),A('count',id='date_spots',add=1),A('sfx',id='sparkle')]
    booth=next(x for x in steps['C02_DATE']['interactables'] if x['id']=='booth')
    photo_actions=[
        A('minigame',id='photobooth'),
        A('scene',id='V468-C02-PHOTO-CHOICE'),
        A('scene',id='C02-X02'),
        A('music',id='cinema_date_choices_v468'),
        A('sfx',id='photo_lantern_v468'),
        A('cine',cmds=[
            {'c':'bars','on':True,'t':.24},
            {'c':'shot','focus':'couple','frame':'intimate','zoom':1.2,'t':1.15,'bars':False},
            {'c':'fx','kind':'glow','on':'player','t':2.0},
            {'c':'wait','t':.32},{'c':'bars','on':False,'t':.3}]),
        A('scene',id='V468-C02-PHOTO-LANTERN'),
        A('item',id='foto_berdua'),A('item',id='v468_lantern_photo'),
        A('count',id='date_spots',add=1),A('sfx',id='sparkle')]
    # Arland must actually repair the machine before using the photo stage;
    # Sofia may use the machine normally. Old saves at C02_DATE are safe too.
    booth['actions']=[route('arland',[
        C('V468_C02_PHOTO_FIXED',photo_actions,[A('step',id='V468_C02_PHOTO_REPAIR')])
    ],photo_actions)]

    # A real two-part interactive repair is playable as Arland (no placeholder
    # "fixing" in dialogue). The legacy Sofia photobooth story works unchanged.
    # Tech repair is a bonus on the actual date, triggered before photobooth
    # from its own playable task, never blocks Sofia from playing her route.
    photo_repair_step=step('V468_C02_PHOTO_REPAIR',
       {'arland':'Periksa panel mesin photobooth agar bisa dipakai lagi',
        'sofia':'Periksa panel mesin photobooth agar bisa dipakai lagi'},
       [point('v468_photo_panel','arcade',342,400,'Periksa sekring photobooth',[
          A('scene',id='V468-C02-PHOTO-TECH'),A('flag',id='V468_C02_PHOTO_FIXED'),
          A('step',id='C02_DATE')],route_id='arland')])
    # The repair branch occurs only if Arland reaches booth before repairing.
    # Since it replaces the booth interaction for that special step, first
    # interaction must be a distinct stage, not automatically show the photo.
    # Legacy saves already in C02_DATE remain safe and can use normal booth.
    extra_steps.append(photo_repair_step)
    # The original C02_DATE step is retained. The native photobooth remains
    # reachable on all old saves; only the unmodified Arland narrative asks
    # the player to repair the panel first.

    # The original sunset now references choices and exchanges gifts only for
    # the correct route (the baseline unguarded route-key was ignored by Runner).
    pier=next(x for x in steps['C02_SUNSET']['interactables'] if x['id']=='pier')
    previous=pier['actions']
    end_idx=next(i for i,x in enumerate(previous) if x.get('do')=='chapterEnd')
    rest=previous[end_idx:]
    pier['actions']=[
       C('V468_S_REPLY_YES',[A('scene',id='V468-C02-PAYOFF-YES')],[]),
       C('V468_S_REPLY_LATER',[A('scene',id='V468-C02-PAYOFF-LATER')],[]),
       C('V468_S_REPLY_NO',[A('scene',id='V468-C02-PAYOFF-NO')],[]),
       C('V468_C02_PHOTO_LAUGH',[A('scene',id='V468-C02-PHOTO-MEMORY-LAUGH')],[]),
       C('V468_C02_PHOTO_LOOK',[A('scene',id='V468-C02-PHOTO-MEMORY-LOOK')],[]),
       C('V468_C02_PHOTO_BLUR',[A('scene',id='V468-C02-PHOTO-MEMORY-BLUR')],[]),
       C('V467_C01_RESULT_LISTEN',[A('scene',id='V468-C02-C01-AFTER')],[]),
       C('V467_C01_RESULT_RECORD',[A('scene',id='V468-C02-C01-AFTER')],[]),
       C('V467_C01_RESULT_TRACE',[A('scene',id='V468-C02-C01-AFTER')],[]),
       A('scene',id='C02-X04'),
       route('arland',[A('removeItem',id='bunga_pita'),A('item',id='foto_kecil')],
         [A('removeItem',id='foto_kecil'),A('item',id='bunga_pita')]),
       *rest]

    # Canon C02-X04 line "thanks for inviting me first" is inaccurate when
    # Arland invited Sofia. Keep the existing emotional moment, adapt wording.
    sc=story['scenes']['C02-X04']
    sc['lines']=[L('narrator','Senja memantul di permukaan danau. Di tas mereka ada foto dengan kilau yang belum bisa dijelaskan.'),
         L('arland','Aku bawa sesuatu. Nggak sebesar kejutan orang lain, tapi aku pilih sendiri.'),
         L('sofia','Bunga dari Toko Bu Melati? Aku suka warnanya. Makasih, Land.','senyum'),
         L('sofia','Aku juga bawa foto langit waktu kita ketemu. Masih inget warna sorenya?'),
         L('arland','Inget. Bahkan aku ingat kamu sempat berhenti jalan cuma buat lihat langit.'),
         L('sofia','Mungkin hal kecil itu lebih lama tinggal di kepala daripada yang kita kira.'),
         L('narrator','Memory Book perlahan hangat. Halaman kencan berwarna jingga; salah satu sudutnya tetap sedikit pudar.'),
         L('arland','Makasih sudah mau cerita, termasuk waktu kita nggak melihat hal yang sama.'),
         L('sofia','Makasih juga sudah dengar, dan nggak membuat semuanya harus sempurna.'),
         L('narrator','Buku sketsa Sofia terselip di samping foto. Di sudutnya ada gambar kursi kosong kecil.'),
         L('sofia','Minggu depan aku akan tampilkan gambar di Galeri Komunitas. Aku agak gugup.'),
         L('arland','Aku ingin datang, Sof. Kalau nanti waktunya sudah pasti, kasih tahu aku ya.'),
         L('sofia','Iya, nanti aku ingetin. Yang aku butuh bukan kejutan besar, kok.'),
         L('narrator','Mereka duduk lebih lama, tanpa mengetahui bahwa suatu hari satu kursi di galeri akan menjadi kenangan yang sulit dilupakan.')]

    # New editable icons / meaningful memory-book entries. Flags persist in
    # schema 8; later chapter passes will deliberately pay them off in C03–C06.
    for iid,name,icon,description in [
       ('v468_lantern_photo','Foto dengan Jejak Lentera','items/v468_c02_lantern.png',
        'Kilau di dua sisi cetakan, meski di ruangan tidak ada lentera.'),
       ('v468_date_note','Catatan untuk Esok','items/v468_c02_calendar.png',
        'Waktu yang diminta dengan jujur, bukan penolakan terhadap orangnya.'),
       ('v468_independent_sketch','Sketsa Ruang Kosong','items/v468_c02_sketch.png',
        'Sofia menyelesaikan gambar sendiri tanpa harus menjelaskan mengapa butuh waktu.')]:
        book['items'][iid]={'name':name,'icon':icon,'desc':description}
    book['entries']=[x for x in book['entries'] if not x['id'].startswith('v468_c02_')]
    for route_id in ('arland','sofia'):
        for key,flag,title,desc,icon in [
           ('pose_laugh','V468_C02_PHOTO_LAUGH','Foto Ketawa','Dua orang tertawa tanpa memedulikan hasil fotonya.','v468_c02_lantern.png'),
           ('pose_look','V468_C02_PHOTO_LOOK','Foto Saling Menoleh','Mata mereka saling menemukan, bukan melihat hitungan kamera.','v468_c02_lantern.png'),
           ('pose_blur','V468_C02_PHOTO_BLUR','Foto Sedikit Buram','Ada hal yang tetap jelas sekalipun gambarnya tidak tajam.','v468_c02_lantern.png'),
           ('lantern','V468_C02_LANTERN_CLUE','Lentera yang Tak Ada','Di cetakan foto kedua muncul dua pantulan lentera dari arah berbeda.','v468_c02_lantern.png')]:
            book['entries'].append({'id':'v468_c02_'+route_id+'_'+key,'chapter':'C02',
             'route':route_id,'type':('fictional_memory' if key=='lantern' else 'optional_story_branch'),'unlock':flag,
             'icon':'items/'+icon,'title':title,'text':desc})
        for key,flag,title,desc in [
           ('gazebo_laugh','V468_C02_GAZEBO_LAUGH','Tawa di Gazebo','Bercanda bisa menjadi cara berani bercerita.'),
           ('gazebo_quiet','V468_C02_GAZEBO_QUIET','Sunyi yang Nyaman','Kebersamaan tidak harus dipenuhi kata-kata.'),
           ('gazebo_listen','V468_C02_GAZEBO_LISTEN','Didengar Sampai Selesai','Mendengarkan adalah sebuah tindakan, bukan skor cinta.')]:
            book['entries'].append({'id':'v468_c02_'+route_id+'_'+key,
             'chapter':'C02','route':route_id,'type':('fictional_memory' if key=='lantern' else 'optional_story_branch'),'unlock':flag,
             'icon':'items/v468_c02_calendar.png','title':title,'text':desc})
    for k,flag,title,desc,icon in [
        ('sofia_postponed','V468_C02_LATER_NOTE_DONE','Janji yang Dijadwalkan Ulang',
         'Sofia meminta waktu hingga besok dan Arland menghormatinya.','v468_c02_calendar.png'),
        ('sofia_declined','V468_C02_SOLO_SKETCH_DONE','Sore Sofia Sendiri',
         'Menolak satu ajakan tidak mengurangi hangatnya hubungan.','v468_c02_sketch.png'),
        ('sofia_reinvited','V468_S_REINVITE_BY_CHOICE','Ajakan Sofia yang Baru',
         'Sofia kembali mengajak karena ia benar-benar ingin.','v468_c02_calendar.png')]:
        book['entries'].append({'id':'v468_c02_'+k,'chapter':'C02','route':'sofia',
          'type':'optional_story_branch','unlock':flag,'icon':'items/'+icon,'title':title,'text':desc})

    # Insert only newly authored steps; script can run repeatedly without
    # duplicating or accumulating old variants in-place.
    quests['steps']=[x for x in quests['steps'] if not x['id'].startswith('V468_C02_')]
    insert_idx=next(i for i,x in enumerate(quests['steps']) if x['id']=='C02_V464_INTERLUDE')+1
    quests['steps'][insert_idx:insert_idx]=extra_steps
    for fname,payload in [('story.json',story),('quests.json',quests),('memory_book.json',book)]:
        (DATA/fname).write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('PASS Chapter 2 patch: accept / postpone / decline route, 3 gazebo decisions, 3 photo choices, original canon preserved')

if __name__ == '__main__':apply()
