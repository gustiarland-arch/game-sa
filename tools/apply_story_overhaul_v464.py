#!/usr/bin/env python3
"""Apply Story Overhaul 3.0 to the existing offline LibGDX game.

Run AFTER any legacy tools/build_content.py invocation, since that generator
regenerates quest/story JSON. Idempotent, changes only recognized story nodes.
Original v4.6.3 source is preserved by distributing this generator along with
patched game data. No device save files are read or removed.
"""
import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
DATA = PROJECT / 'android/assets/data'


def lines(*items):
    return [{'s': speaker, 'e': emo, 't': text} for speaker, emo, text in items]


def L(s, t, emo='neutral'):
    return (s, emo, t)


def choice(text, flag, arland, sofia=None):
    if sofia is None: sofia = arland
    return {'text': text, 'flags': [flag],
            'byRoute': {'arland': lines(*arland), 'sofia': lines(*sofia)}}


def action(d, **fields):
    if 'otherwise' in fields: fields['else'] = fields.pop('otherwise')
    return {'do': d, **fields}


def interact(id_, area, x, y, label, actions, *, when=None, radius=95, route=None):
    a = {'id': id_, 'area': area, 'x': x, 'y': y, 'r': radius,
         'label': label, 'actions': actions}
    if when is not None: a['when'] = when
    if route: a['route'] = route
    return a


def step(id_, chapter, objective, interacts, **rest):
    return {'id': id_, 'chapter': chapter, 'quest': 'Q_' + id_,
            'objective': {'arland': objective[0], 'sofia': objective[1]},
            'interactables': interacts, **rest}


def scene(story, sid, title, chapter, route, dialogue, opts=None, flags=None, location=''):
    story['scenes'][sid] = {'title': title, 'chapter': chapter, 'route': route,
       'location': location, 'trigger': '', 'lines': lines(*dialogue),
       'flags': flags or [], 'choices': opts or [], 'note': 'Story Overhaul 3.0: The Empty Seat'}


def patch(s, sid, *, dialogue=None, choices=None):
    if sid not in s['scenes']:
        raise ValueError('Missing legacy scene: ' + sid)
    x = s['scenes'][sid]
    if dialogue is not None: x['lines'] = lines(*dialogue)
    if choices is not None: x['choices'] = choices
    x['note'] = 'Story Overhaul 3.0 revised dialogue; canon preserved.'


def apply():
    s = json.loads((DATA / 'story.json').read_text(encoding='utf-8'))
    q = json.loads((DATA / 'quests.json').read_text(encoding='utf-8'))
    b = json.loads((DATA / 'memory_book.json').read_text(encoding='utf-8'))
    maps = json.loads((DATA / 'maps.json').read_text(encoding='utf-8'))

    # Keep old known IDs to avoid missing legacy scenes in side quests or saves.
    s['meta']['storyOverhaul'] = '3.0 - The Promise We Almost Forgot / The Empty Seat'
    s['meta']['storyOverhaulVersion'] = '4.6.4'
    s['meta']['canonEnding'] = 'One shared happy ending - To Be Continued'
    s['meta']['legacyScenesRetainedForSaveCompatibility'] = True
    s['chapters'] = [
       {'id':'PRO','title':'Prolog — The Book of Us'},
       {'id':'C01','title':'Chapter 1 — The Beginning of Us'},
       {'id':'C02','title':'Chapter 2 — A Little Date'},
       {'id':'C03','title':'Chapter 3 — The Little Things'},
       {'id':'C04','title':'Chapter 4 — The Empty Seat'},
       {'id':'C05','title':'Chapter 5 — Across the Stars'},
       {'id':'C06','title':'Chapter 6 — Our Tomorrow'},
       {'id':'EPI','title':'Epilog — To Be Continued'}]
    q['chapters'] = [dict(c) if isinstance(c,dict) else c for c in q['chapters']]
    for ch in q['chapters']:
        if ch.get('id') == 'C04': ch['title'] = 'The Empty Seat'

    # PROLOG / C1: foreshadow, no premature tragedy.
    if not any('Di belakang bunga kertas' in l['t'] for l in s['scenes']['P-X01']['lines']):
      patch(s, 'P-X01', dialogue=lines_to_tuple(s['scenes']['P-X01']['lines']) + [
       L('narrator', 'Di belakang bunga kertas, ada tulisan yang terlalu kecil untuk dibaca dalam cahaya senja.'),
       L('sofia','Nanti aku baca pelan-pelan, ya. Aku mau inget semuanya.', 'senyum')])
    if not any('Satu kalimat di surat tua' in l['t'] for l in s['scenes']['C01-X02']['lines']):
      patch(s, 'C01-X02', dialogue=lines_to_tuple(s['scenes']['C01-X02']['lines']) + [
       L('narrator','Satu kalimat di surat tua tampak dari dua arah, seperti ditulis dua orang pada hari yang sama.'),
       L('sofia','Kita sama-sama di sana, tapi ternyata yang kita inget bisa beda.', 'penasaran'),
       L('arland','Kalau begitu jangan cuma lihat dari sisiku, Sof.', 'senyum')])

    # CHAPTER 2: actual story choices, not cosmetic-only; each unlocks its own short quest.
    scene(s, 'V464-C02-WALK-A', 'Mengajak Sofia', 'C02', 'arland', [
       L('narrator','Arland melihat taman di ujung jalan. Ia ingin mengajak Sofia, tetapi takut mengganggu jadwalnya.'),
       L('arland','Sof, kalau hari ini kita sempat, aku mau ngajak kamu jalan. Tapi kamu yang pilih waktunya.'),
       L('sofia','Makasih udah nanya dulu. Aku suka kalau kita bisa rencanain bareng.', 'senyum')],
       [choice('Ajak jalan ke taman sekarang','V464_WALK_PARK', [L('arland','Ke taman sekarang, kalau kamu nggak keberatan?', 'malu'),L('sofia','Yuk, sebentar aja. Aku masih pengen lihat pohon bunganya.', 'senang')]),
        choice('Tawarkan waktu besok','V464_WALK_LATER', [L('arland','Kalau kamu capek, kita bisa pergi besok.', 'senyum'),L('sofia','Besok boleh. Hari ini kita duduk sebentar dulu, ya.', 'lega')]),
        choice('Tanyakan kebutuhan Sofia dahulu','V464_WALK_ASK', [L('arland','Sebenarnya kamu lagi pengen apa, Sof?', 'penasaran'),L('sofia','Ditemenin ngobrol sebentar aja udah cukup.', 'senyum')])])
    scene(s, 'V464-C02-WALK-S', 'Pilihan Sofia', 'C02', 'sofia', [
       L('arland','Sof, aku mau ngajak jalan ke taman. Tapi kalau kamu lagi pengen sendiri juga nggak apa-apa.'),
       L('narrator','Sofia memilih jawabannya sendiri. Arland tidak memaksanya mengiyakan.')],
       [choice('Iya, aku ikut','V464_WALK_PARK',[L('sofia','Boleh, ayo. Aku pengen lihat langit sore.', 'senyum'),L('arland','Aku tunggu kamu siap. Nggak perlu buru-buru.', 'senang')]),
        choice('Hari ini aku belum bisa','V464_WALK_SOLO',[L('sofia','Maaf, hari ini aku butuh waktu buat gambarku dulu.', 'serius'),L('arland','Oke, Sof. Makasih udah bilang jujur. Kita ketemu pas kamu siap.', 'senyum')]),
        choice('Kalau besok saja?','V464_WALK_LATER',[L('sofia','Besok aja, Land? Hari ini aku masih banyak yang harus disiapin.', 'malu'),L('arland','Besok juga hari yang bagus. Kita rencanain pelan-pelan.', 'senyum')])])
    scene(s, 'V464-C02-PARK', 'Jalan yang Dipilih', 'C02', 'shared', [
       L('narrator','Mereka berjalan sambil menghitung lampu taman yang menyala satu per satu.'),
       L('sofia','Tadi aku kepikiran, lucu juga ya... jalan tanpa tujuan ternyata bisa sesenang ini.', 'senyum'),
       L('arland','Karena tujuannya ketemu kamu.', 'malu'),
       L('sofia','Gombal, tapi lumayan.', 'tertawa')], flags=['V464_INTERLUDE_DONE'])
    scene(s, 'V464-C02-LATER', 'Nggak Harus Hari Ini', 'C02', 'shared', [
       L('narrator','Mereka duduk di dekat jendela kafe. Rencana taman boleh ditunda; obrolan tidak harus berhenti.'),
       L('sofia','Makasih nggak maksa, Land.', 'senyum'),
       L('arland','Aku pengen kita sama-sama nyaman. Kalau besok, ya besok.', 'senyum')], flags=['V464_INTERLUDE_DONE'])
    scene(s, 'V464-C02-SOLO', 'Waktu untuk Diri Sendiri', 'C02', 'sofia', [
       L('narrator','Sofia membuka buku sketsanya di sudut arcade. Ia menggambar dua kursi menghadap danau.'),
       L('sofia','Ternyata bilang nggak hari ini juga bisa tanpa bikin seseorang merasa ditolak.', 'lega'),
       L('arland_msg','Gambarnya semoga lancar, ya. Kita ketemu di kafe nanti.'),
       L('sofia','Dia ngerti. Aku seneng.', 'senyum')], flags=['V464_INTERLUDE_DONE'])
    scene(s, 'V464-C02-ASK', 'Mendengarkan Dulu', 'C02', 'arland', [
       L('narrator','Arland memilih duduk dan mendengarkan, tanpa menebak apa yang Sofia inginkan.'),
       L('sofia','Aku lagi nyiapin sesuatu yang belum berani kutunjukin, Land.', 'malu'),
       L('arland','Kalau suatu hari siap, aku mau lihat. Aku nggak akan buru-buru.', 'senyum')], flags=['V464_INTERLUDE_DONE'])
    scene(s, 'V464-C02-GALLERY-TEASE', 'Satu Gambar yang Belum Selesai', 'C02', 'shared', [
       L('narrator','Di dalam tas Sofia, sudut halaman buku sketsanya tampak sedikit terlipat.'),
       L('arland','Itu kamu gambar sendiri?'),
       L('sofia','Iya. Minggu depan ada pameran kecil di galeri komunitas. Aku agak gugup.', 'malu'),
       L('arland','Boleh aku lihat kalau sudah jadi?'),
       L('sofia','Nanti. Kalau sudah siap.', 'senyum')], flags=['V464_GALLERY_MENTIONED'])

    scene(s, 'V464-C06-WALK-PARK', 'Taman yang Kita Pilih', 'C06', 'shared', [
       L('sofia','Aku masih inget taman waktu kita bilang iya buat jalan bareng.'),
       L('arland','Waktu itu aku cuma pengen satu sore sama kamu. Sekarang aku tahu betapa berharganya waktu itu.', 'senyum')])
    scene(s, 'V464-C06-WALK-LATER', 'Rencana yang Boleh Berubah', 'C06', 'shared', [
       L('sofia','Kita pernah nunda jalan ke taman, ya?'),
       L('arland','Iya. Ternyata waktu yang ditunda nggak berarti perasaan yang ditolak.'),
       L('sofia','Makasih dulu kamu nggak memaksa.', 'lega')])
    scene(s, 'V464-C06-WALK-SOLO', 'Waktu yang Diberikan', 'C06', 'sofia', [
       L('sofia','Aku pernah bilang nggak bisa ikut. Kamu tetap mempercayai aku.'),
       L('arland','Aku pengen kamu punya ruang jadi diri sendiri juga, Sof.'),
       L('sofia','Karena itu, waktu kita bersama justru terasa lebih berarti.', 'senyum')])
    scene(s, 'V464-C06-WALK-ASK', 'Pertanyaan Kecil', 'C06', 'arland', [
       L('arland','Dulu aku tanya kamu pengen apa, bukan langsung nebak.'),
       L('sofia','Aku inget. Aku seneng kamu masih nanya begitu sekarang.', 'senyum')])

    # CHAPTER 3: one promise forms the spine of the emotional conflict.
    scene(s, 'V464-C03-PROMISE', 'Janji di Antara Sketsa', 'C03', 'shared', [
       L('narrator','Sofia mengeluarkan undangan galeri yang terlipat rapi. Di sampulnya ada lukisan dua orang di bawah langit sore.'),
       L('sofia','Land, hari Sabtu aku nunjukin gambar-gambarku. Aku pengen kamu ada di sana.', 'malu'),
       L('arland','Tentu. Aku mau lihat hasil kerja keras kamu.', 'senyum'),
       L('sofia','Janji, ya? Aku bakal gugup banget kalau berdiri di depan banyak orang.'),
       L('arland','Janji. Aku datang buat kamu. Bukan cuma buat gambarnya.', 'serius'),
       L('narrator','Sofia menyisakan satu kursi untuk Arland. Janji kecil itu tidak dicatat sebagai hadiah—melainkan sesuatu yang harus dijaga.')],
       [choice('Catat jam acara bersama','V464_PROMISE_TIME',[L('arland','Aku tulis jamnya supaya nggak kelewat.', 'serius'), L('sofia','Makasih, Land. Itu berarti buat aku.', 'lega')]),
        choice('Tanyakan apa yang paling Sofia butuhkan','V464_PROMISE_LISTEN',[L('arland','Nanti kamu butuh apa dariku?'),L('sofia','Cuma duduk di situ, Land. Aku pengen lihat kamu pas aku gugup.', 'senyum')]),
        choice('Janjikan kehadiran tanpa kejutan','V464_PROMISE_SIMPLE',[L('arland','Aku datang. Nggak perlu macam-macam.', 'serius'),L('sofia','Iya. Itu aja udah cukup.', 'lega')])], flags=['V464_GALLERY_PROMISED'])
    scene(s, 'V464-C03-SEAT', 'Tempat yang Disiapkan', 'C03', 'shared', [
       L('narrator','Di sisi dekat jendela ada kursi kayu tunggal. Sofia menempelkan kartu nama kecil: ARLAND.'),
       L('sofia','Dari sini kamu bisa lihat gambarku yang paling aku suka.', 'senyum'),
       L('arland','Aku akan duduk di sini. Aku bakal tepuk tangan paling kenceng.', 'tertawa'),
       L('narrator','Kamera tertahan sejenak pada kursi itu. Masih kosong, tapi penuh harapan.')], flags=['V464_SEAT_PREPARED'])
    scene(s, 'V464-C03-PROJECTOR', 'Rencana Kejutan', 'C03', 'arland', [
       L('narrator','Di sudut galeri terdapat proyektor lama yang hanya menampilkan garis-garis putih.'),
       L('arland','Kalau aku bisa bikin sketsanya bergerak, pasti Sofia senang.'),
       L('narrator','Proyektor itu sudah usang. Tidak ada janji untuk memperbaikinya.'),
       L('arland','Aku cuma bantu sebentar. Yang penting tetap datang tepat waktu.', 'serius')], flags=['V464_PROJECTOR_SEEN'])
    scene(s, 'V464-C03-SKETCH', 'Gambar yang Berani Ditunjukkan', 'C03', 'sofia', [
       L('narrator','Sofia menggantung sketsanya sendiri. Satu gambar memperlihatkan bunga kertas dari prolog.'),
       L('sofia','Aku sering takut gambarku nggak cukup bagus buat dilihat orang.'),
       L('arland','Aku suka karena kamu yang bikin. Ceritanya cuma ada di gambar kamu.', 'senyum'),
       L('sofia','Aku bakal ingat kalimat itu.', 'lega')], flags=['V464_SKETCH_PREPARED'])
    scene(s, 'V464-C03-END', 'Sebelum Hari Besar', 'C03', 'shared', [
       L('narrator','Galeri sepi. Lampu dipadamkan satu demi satu.'),
       L('sofia','Besok rasanya bakal lama banget.', 'khawatir'),
       L('arland','Aku bakal ada di sana.', 'serius'),
       L('narrator','Di Memory Book, sebuah halaman baru tercetak: satu kursi, satu janji, dan banyak hal yang belum mereka tahu.')], flags=['V464_GALLERY_REHEARSAL_DONE'])

    # CHAPTER 4: no betrayal, death, manipulation, or forced breakup.
    scene(s, 'V464-C04-A-MORNING', 'Hari yang Terlalu Penuh', 'C04', 'arland', [
       L('narrator','Hari acara galeri. Arland bangun lebih pagi dan memeriksa jam pada ponselnya.'),
       L('arland','Hari ini aku harus datang. Sofia udah nungguin acara ini lama.'),
       L('narrator','Sebuah pesan masuk: proyektor yang hendak dipakai tiba-tiba rusak lagi.'),
       L('arland','Aku bisa benerin. Nggak akan lama... seharusnya.', 'khawatir')], flags=['V464_GALLERY_DAY'])
    scene(s, 'V464-C04-A-PROJECTOR', 'Pilihan Arland', 'C04', 'arland', [
       L('narrator','Proyektor menyala sebentar lalu mati. Jam di dinding terasa bergerak terlalu cepat.'),
       L('arland','Aku ingin nunjukin dukungan buat Sofia. Tapi aku juga udah janji hadir.')],
       [choice('Kirim kabar sebelum lanjut','V464_A_WARN',[L('arland','Aku mungkin terlambat. Aku minta maaf, Sof. Kamu nggak perlu nunggu.', 'serius'),L('narrator','Pesan terkirim, tetapi waktu terus berjalan.')]),
        choice('Tetap berusaha menyelesaikan kejutan','V464_A_SILENT',[L('arland','Satu percobaan lagi. Aku yakin masih keburu.', 'khawatir'),L('narrator','Ponsel diletakkan. Arland tidak melihat jam lagi.')]),
        choice('Minta bantuan dan tetap menuju galeri','V464_A_HELP',[L('arland','Aku nggak bisa ngerjain semuanya sendiri. Aku minta bantuan dulu.', 'serius'),L('narrator','Bantuan datang, tetapi jarak dan waktu tetap tidak bisa diulang.')])])
    scene(s, 'V464-C04-A-LATE', 'Kursi yang Tidak Ditempati', 'C04', 'arland', [
       L('narrator','Arland tiba ketika tepuk tangan sudah berakhir. Beberapa pengunjung sedang pulang.'),
       L('arland','Aku telat...', 'khawatir'),
       L('narrator','Di dekat jendela, kursi bertanda namanya masih kosong.'),
       L('arland','Aku bikin sesuatu yang katanya buat dia... tapi justru nggak ada waktu dia butuh aku.', 'sedih'),
       L('narrator','Sebuah sketsa tertinggal di meja: sepasang sepatu di bawah payung, disertai ruang kosong di sebelahnya.')], flags=['V464_SEAT_EMPTY'])
    scene(s, 'V464-C04-A-HONEST', 'Tak Bisa Mengulang Jam', 'C04', 'arland', [
       L('arland','Aku harus minta maaf tanpa menjadikan kejutan itu alasan.'),
       L('narrator','Arland melipat tiket galerinya. Ia tidak membuangnya, karena tidak ingin melupakan pelajaran hari ini.')], flags=['V464_ARLAND_REALIZES'])
    scene(s, 'V464-C04-S-MORNING', 'Hari Pertama Berani', 'C04', 'sofia', [
       L('narrator','Sofia merapikan ujung hijabnya di cermin. Presentasi pertama karyanya dimulai sebentar lagi.'),
       L('sofia','Aku takut lupa ngomong apa. Tapi kalau Arland ada di kursi dekat jendela, mungkin aku lebih berani.', 'khawatir'),
       L('narrator','Ia memasukkan buku sketsa kecil ke tas, lalu berangkat.')], flags=['V464_GALLERY_DAY'])
    scene(s, 'V464-C04-S-PRESENT', 'Satu Kursi Kosong', 'C04', 'sofia', [
       L('narrator','Galeri ramai. Sofia berdiri di samping lukisan pertamanya. Ia melihat ke kursi dekat jendela.'),
       L('narrator','Kursi itu belum terisi.'),
       L('sofia','Terima kasih udah datang. Aku gambar ini karena... ada orang yang ngajarin aku kalau usaha kecil juga berarti.', 'serius'),
       L('narrator','Sofia berhasil menyelesaikan presentasinya. Orang-orang bertepuk tangan.'),
       L('narrator','Sofia tersenyum, tetapi matanya kembali mencari satu wajah yang belum muncul.'),
       L('sofia','Aku bisa, Land... aku beneran bisa. Sayang kamu nggak lihat.', 'sedih')], flags=['V464_SEAT_EMPTY'])
    scene(s, 'V464-C04-S-AFTER', 'Setelah Tepuk Tangan', 'C04', 'sofia', [
       L('narrator','Pengunjung sudah pulang. Sofia berdiri di depan kursi yang tadi ia sisakan.'),
       L('sofia','Aku tahu Arland sayang aku. Justru itu kenapa aku sedih.'),
       L('sofia','Aku nggak butuh hadiahnya. Aku cuma pengen dia ada saat aku bilang, "ini gambarku".', 'sedih')],
       [choice('Ambil waktu sendiri dulu','V464_S_SPACE',[L('sofia','Aku perlu pulang sebentar. Nggak mau ngomong sambil masih berat hati.', 'serius')]),
        choice('Katakan dengan jujur rasa kecewa','V464_S_SPEAK',[L('sofia','Nanti kalau ketemu, aku mau bilang kenapa ini sakit buat aku.', 'serius')]),
        choice('Gambar kursi kosong dalam buku','V464_S_DRAW',[L('narrator','Sofia menggambar kursi itu tanpa menghapusnya.'),L('sofia','Biar aku inget rasanya, bukan buat menyalahkan dia.', 'sedih')])])
    scene(s, 'V464-C04-SEAT-REFLECT-A', 'Arland Membaca Pesannya', 'C04', 'arland', [
       L('arland','Sof, maaf banget. Aku tahu pesanku nggak mengganti kehadiran aku.'),
       L('narrator','Arland melihat tanggal di ponselnya. Tidak ada tombol untuk mengulang hari.')])
    scene(s, 'V464-C04-SEAT-REFLECT-S', 'Sofia Memegang Buku', 'C04', 'sofia', [
       L('sofia','Aku mau marah. Tapi aku juga nggak mau dia cuma mengerti karena aku diam.'),
       L('narrator','Ia menutup buku sketsanya sambil mengatur napas.')])
    patch(s,'C04-X00', dialogue=[
       L('narrator','Hujan membasahi halte. Arland dan Sofia akhirnya berdiri di tempat yang sama, dengan jarak yang terasa asing.'),
       L('arland','Sof... maaf. Aku terlambat ke galeri.', 'sedih'),
       L('sofia','Iya. Aku tahu.', 'serius'),
       L('arland','Aku lagi memperbaiki proyektor buat gambarmu. Aku mau bikin kejutan.'),
       L('sofia','Aku tahu kamu niat baik, Land. Tapi aku nggak minta gambarku dibikin lebih bagus.', 'sedih'),
       L('arland','Aku cuma pengen kamu bahagia.'),
       L('sofia','Hari ini aku cuma pengen kamu ada di sana.', 'sedih'),
       L('narrator','Arland mencoba mencari kata-kata. Tak ada kalimat yang bisa mengembalikan acara tadi.'),
       L('sofia','Aku beberapa kali lihat pintu. Aku sisain satu kursi buat kamu.'),
       L('sofia','Aku bukan sedih karena nggak dapat hadiah. Aku sedih karena kamu udah janji.', 'sedih'),
       L('arland','Aku salah. Aku dengerin, Sof. Tanpa nyela.', 'serius'),
       L('sofia','Aku mau pulang dulu. Kita ngomong lagi kalau udah sama-sama siap.', 'serius'),
       L('narrator','Arland mengangguk, tidak memaksa. Hujan masih turun. Memory Book kehilangan warna pada satu halaman, lalu membuka portal ke Lantern Field.')], choices=[
       choice('Hormati Sofia dan beri waktu','V464_REPAIR_SPACE',[L('arland','Oke, Sof. Aku tunggu sampai kamu siap bicara.', 'serius'),L('sofia','Makasih.', 'lega')]),
       choice('Akui kesalahan tanpa membela diri','V464_REPAIR_OWN',[L('arland','Aku nggak datang seperti yang kujanjikan. Aku nggak mau cari alasan.', 'serius'),L('sofia','Itu yang ingin aku dengar, Land.', 'sedih')]),
       choice('Tawarkan untuk menulis perasaan dulu','V464_REPAIR_LETTER',[L('arland','Kalau sekarang terlalu berat, boleh aku tulis yang belum sanggup kujelasin?', 'malu'),L('sofia','Boleh. Tapi nanti kita tetap harus ngobrol, ya.', 'serius')])])
    patch(s,'C04-X01', dialogue=[
       L('narrator','Di Lantern Field, dua cahaya terakhir menyala ketika mereka berhenti menebak isi kepala masing-masing.'),
       L('sofia','Land, aku butuh kamu dengerin, bukan langsung nyari cara memperbaiki semuanya.', 'serius'),
       L('arland','Aku dengar. Waktu aku nggak ada, kamu merasa sendirian di hari pentingmu.', 'serius'),
       L('sofia','Iya. Dan aku juga mau belajar ngomong sebelum semuanya numpuk.'),
       L('arland','Aku nggak minta kamu langsung nggak sedih. Aku cuma ingin benerin caraku hadir.'),
       L('narrator','Lentera kembali bercahaya. Namun kursi pada halaman galeri tetap kosong: sebagian luka perlu waktu untuk dipahami.')], choices=[
       choice('Buat rencana hadir yang nyata','V464_PLAN_PRESENT',[L('arland','Lain kali kita tulis waktunya, dan aku datang sebelum acaranya mulai.', 'serius'),L('sofia','Aku mau lihat kamu menepati itu, bukan cuma dengar janjinya.', 'senyum')]),
       choice('Dengarkan sampai Sofia selesai bicara','V464_PLAN_LISTEN',[L('arland','Kamu masih mau cerita bagian yang paling berat, Sof?', 'serius'),L('sofia','Iya. Makasih udah nggak buru-buru nutup pembicaraan.', 'lega')])])
    patch(s, 'C04-X03', dialogue=[
       L('narrator','Hujan reda. Di permukaan kolam, pantulan dua orang itu belum sepenuhnya jelas.'),
       L('sofia','Aku masih sedih kalau inget kursi itu.'),
       L('arland','Aku ngerti. Kita nggak harus pura-pura udah baik-baik aja.'),
       L('lumi','Memulihkan cahaya bukan berarti menghapus hari yang menyakitkan.', 'serius'),
       L('narrator','Sebuah lentera kecil menyala untuk pertama kalinya. Yang lain masih menunggu percakapan berikutnya.')])
    patch(s, 'V26-C04-VOW', dialogue=[
       L('narrator','Arland dan Sofia duduk di bangku taman. Tidak bergandengan tangan seperti biasanya.'),
       L('arland','Aku nggak akan bilang semuanya selesai malam ini.'),
       L('sofia','Aku juga belum siap melupakan semuanya. Tapi aku mau kita sama-sama belajar.'),
       L('arland','Aku janji, kalau ada sesuatu yang penting buat kamu, aku tanya dulu apa yang kamu butuh.', 'serius'),
       L('sofia','Dan aku janji bakal bilang kalau aku kecewa. Nggak menunggu sampai kamu nebak.'),
       L('narrator','Mereka duduk diam, mendengar suara daun setelah hujan. Itu bukan akhir masalah—melainkan awal saling memahami.')])

    # CHAPTER 5: reveal the two real memories, not a magic cure.
    scene(s, 'V464-C05-MEMORY-A', 'Dua Sisi, Satu Hari — Arland', 'C05', 'arland', [
       L('narrator','Memory Bridge memperlihatkan Arland dengan tangan kotor oli, berusaha menyalakan proyektor.'),
       L('arland','Aku pikir kalau kejutannya sempurna, Sofia bakal tahu aku sayang.'),
       L('lumi','Itu bagian ingatanmu. Sekarang lihat apa yang terjadi di tempat lain.'),
       L('narrator','Di sisi lain, Sofia sedang berdiri di depan lukisannya dan melirik kursi bertanda nama Arland.'),
       L('arland','Aku nggak pernah lihat ini. Aku baru ngerti betapa sendirinya dia waktu itu.', 'sedih')], flags=['V464_QUIET_TWO_SIDES'])
    scene(s, 'V464-C05-MEMORY-S', 'Dua Sisi, Satu Hari — Sofia', 'C05', 'sofia', [
       L('narrator','Memory Bridge menunjukkan kursi kosong yang tidak pernah berhenti Sofia perhatikan.'),
       L('sofia','Waktu itu aku cuma bisa lihat kursinya. Aku nggak tahu apa yang Arland coba buat.'),
       L('lumi','Sekarang lihat bagian lain dari hari yang sama.'),
       L('narrator','Di sisi lain, Arland menahan panik di depan proyektor rusak, yakin masih ada waktu memperbaiki semuanya.'),
       L('sofia','Niatnya tulus... tapi aku tetap butuh dia hadir. Dua hal itu bisa benar bersamaan.', 'sedih')], flags=['V464_QUIET_TWO_SIDES'])
    scene(s, 'V464-C05-REPAIR', 'Hadir di Hari Biasa', 'C05', 'shared', [
       L('narrator','Di depan jembatan bintang, Arland berhenti sebelum mendahului Sofia.'),
       L('arland','Kamu mau jalan duluan, atau bareng aku?', 'senyum'),
       L('sofia','Bareng, tapi pelan-pelan.', 'senyum'),
       L('narrator','Ia tidak langsung meraih tangan Sofia. Ia menunggu Sofia mengulurkan tangannya sendiri.'),
       L('sofia','Makasih udah tanya.', 'lega')], flags=['V464_REPAIR_GROWING'])
    patch(s,'C05-X03',dialogue=[
       L('lumi','Selamat datang di Starfall Village. Setiap bintang di sini menyimpan lebih dari satu sudut pandang.'),
       L('sofia','Kalau seseorang berniat baik, kenapa kenangannya masih bisa menyakitkan?'),
       L('lumi','Karena niat dan dampak adalah dua suara yang berbeda. Keduanya perlu didengar.', 'serius'),
       L('arland','Aku nggak bisa mengubah hari itu. Tapi aku bisa belajar dari hari itu.'),
       L('lumi','Itulah yang selama ini ditunggu The Quiet. Bukan kenangan yang sempurna.')])
    patch(s,'C05-X04',dialogue=[
       L('narrator','Gerbang Eternal Garden terbuka. Dua jejak cahaya melintasi ambangnya.'),
       L('sofia','Aku masih kadang inget hari di galeri itu.'),
       L('arland','Aku juga. Tapi aku senang kamu mau cerita, walau pelan-pelan.'),
       L('sofia','Aku senang kamu sekarang mau denger sampai selesai.', 'senyum'),
       L('arland','Boleh jalan bareng?'),
       L('sofia','Boleh. Kita nggak perlu buru-buru.', 'senyum')])

    # CHAPTER 6: conditional payoffs retain a single canon ending.
    scene(s, 'V464-C06-EMPTY-SEAT', 'Gambar yang Tidak Dihapus', 'C06', 'shared', [
       L('narrator','Eternal Garden memunculkan gambar kursi kosong. Di sebelahnya tumbuh halaman baru: dua orang duduk melihat matahari terbenam.'),
       L('sofia','Aku pernah sedih banget waktu bikin gambar ini.', 'sedih'),
       L('arland','Aku ingat. Dan aku nggak akan berpura-pura itu nggak terjadi.'),
       L('sofia','Aku nggak mau menghapus yang lama. Itu juga bagian dari cerita kita.', 'lega'),
       L('arland','Kalau gitu kita simpan dua-duanya. Yang membuat kita sedih, dan yang bikin kita belajar.'),
       L('narrator','Warna kembali ke kedua gambar sekaligus. Halaman lama tidak hilang.')], flags=['V464_SEAT_RESTORED'])
    scene(s, 'V464-C06-MEMORY-WALK', 'Pilihan yang Mengubah Hari', 'C06', 'shared', [
       L('narrator','Mereka melihat ulang kencan kecil yang pernah ditunda, diterima, atau diganti percakapan sederhana.'),
       L('sofia','Ternyata bukan tempatnya yang bikin aku ingat.'),
       L('arland','Tapi cara kita saling ngasih ruang.', 'senyum')])
    scene(s, 'V464-C06-PAYOFF-WARN', 'Kabar yang Datang Terlambat', 'C06', 'shared', [
       L('sofia','Aku masih inget pesanmu waktu itu. Aku menghargai kamu ngabarin, meski aku tetap sedih.'),
       L('arland','Sekarang aku tahu, ngabarin bukan pengganti hadir. Tapi itu tanggung jawabku.'),
       L('sofia','Iya. Kita belajar dua-duanya.', 'lega')])
    scene(s, 'V464-C06-PAYOFF-SILENT', 'Kalimat yang Dulu Tidak Dikirim', 'C06', 'shared', [
       L('arland','Kalau bisa mengulang, aku bakal kirim kabar. Bukan diam karena takut kejutannya gagal.'),
       L('sofia','Aku nggak butuh kamu nggak pernah salah. Aku butuh kamu berani bilang apa yang terjadi.'),
       L('arland','Aku sudah belajar itu dari kamu.', 'lega')])
    scene(s, 'V464-C06-PAYOFF-HELP', 'Tidak Harus Sendirian', 'C06', 'shared', [
       L('arland','Hari itu aku belajar minta bantuan. Aku cuma terlambat menyadari waktunya.'),
       L('sofia','Sekarang kalau kita kewalahan, kita bisa bilang. Nggak perlu saling menebak.'),
       L('arland','Iya. Kita satu tim.', 'senyum')])
    scene(s, 'V464-C06-PAYOFF-DRAW', 'Sketsa yang Disimpan', 'C06', 'sofia', [
       L('sofia','Aku nggak nyangka gambar kursi kosong itu akhirnya jadi gambar yang bisa kulihat tanpa takut.'),
       L('arland','Aku mau terus lihat gambarmu—dan hadir, bukan cuma bilang akan datang.'),
       L('sofia','Itu cukup, Land.', 'lega')])
    scene(s, 'V464-C06-PAYOFF-SPACE', 'Memberi Ruang', 'C06', 'sofia', [
       L('sofia','Makasih waktu itu kamu nggak maksa aku langsung baik-baik aja.'),
       L('arland','Aku juga belajar bahwa kasih sayang nggak berarti kita harus terus bicara saat belum siap.'),
       L('sofia','Tapi kita selalu balik untuk saling dengar.', 'senyum')])
    scene(s, 'V464-C06-PAYOFF-SPEAK', 'Berani Mengatakan', 'C06', 'sofia', [
       L('sofia','Aku senang akhirnya bisa bilang aku kecewa, tanpa takut kamu pergi.'),
       L('arland','Aku justru mau tahu yang sebenarnya kamu rasain.'),
       L('sofia','Jadi aku nggak perlu menyimpan semuanya sendirian lagi.', 'lega')])
    patch(s,'C06-X01', dialogue=[
       L('narrator','Memory Book membuka halaman masa depan yang tidak pernah ada: semua janji ditepati, semua hari berjalan sesuai rencana.'),
       L('sofia','Cantik, tapi... rasanya bukan kita.'),
       L('arland','Kalau nggak boleh salah, kita juga nggak akan pernah belajar dari kesalahan.'),
       L('sofia','Hari di galeri itu sedih. Tapi aku nggak mau menghapus bagian hidup kita hanya karena nggak sempurna.'),
       L('arland','Aku nggak mau janji bahwa semua hari nanti bakal mudah. Aku cuma mau terus belajar hadir.'),
       L('sofia','Dan aku mau terus berani cerita, bahkan kalau rasanya sulit.'),
       L('narrator','Mereka memilih membiarkan halaman terakhir kosong. Bukan karena cerita hilang, melainkan karena masa depan belum ditulis.'),
       L('narrator','Di bagian bawah halaman, dua nama tertulis berdampingan: Arland & Sofia — To Be Continued.')],
       choices=[choice('Kita tulis sedikit demi sedikit','V464_CANON_GENTLE',[L('arland','Satu hari, satu cerita. Kita nggak perlu tahu semuanya sekarang.'),L('sofia','Asal kita saling cerita, ya.', 'senyum')]),
                choice('Biar halaman ini tetap terbuka','V464_CANON_OPEN',[L('sofia','Kita simpan ruang buat semua hal yang belum kita kenal.'),L('arland','Termasuk diri kita yang masih belajar.', 'senyum')])])
    patch(s,'C06-X03', dialogue=[
       L('lumi','Kalian tidak pernah harus menghapus satu kenangan agar bisa terus bersama.'),
       L('sofia','Aku mau bawa yang baik, yang sedih, semuanya.'),
       L('arland','Karena semua itu bagian dari kita.'),
       L('narrator','The Quiet tidak lagi membuat halaman hilang. Ia memudar ketika kedua suara bisa didengarkan.'),
       L('lumi','Pergilah. Ada banyak hari yang masih menunggu kalian.', 'senyum'),
       L('narrator','Cahaya taman berubah menjadi pagi yang hangat. Sebuah pintu pulang terbuka.')])
    patch(s,'EPI-X01', dialogue=[
       L('narrator','Beberapa waktu berlalu. Mereka berjalan ke danau seperti pada hari-hari biasa.'),
       L('sofia','Land, kamu ingat sketsa kursi di galeri itu?'),
       L('arland','Ingat. Aku juga ingat gambar yang kamu bikin sesudahnya.'),
       L('sofia','Aku nggak menghapus gambar pertama. Soalnya itu juga cerita kita.'),
       L('arland','Aku senang kamu masih mau menggambar hari-hari kita.'),
       L('sofia','Halaman terakhirnya masih kosong.', 'senyum'),
       L('arland','Berarti kita belum selesai menulis.', 'senyum'),
       L('sofia','Nggak perlu buru-buru, ya?'),
       L('arland','Nggak. Kita masih punya banyak hari.'),
       L('narrator','Langit menghangat. Dua orang berjalan berdampingan. Our story isn\'t over. We\'re still writing it.')])

    # Alternative activities reach the same C02 date step via distinct actual interactables.
    steps = {x['id']: x for x in q['steps']}
    def replace_actions(step_id, interact_id, new_actions):
        candidates=[i for i in steps[step_id]['interactables'] if i['id']==interact_id]
        if len(candidates)!=1: raise AssertionError('Unexpected quest interactable: '+step_id+'/'+interact_id)
        candidates[0]['actions']=new_actions

    for i in steps['C02_TO_CAFE']['interactables']:
        if i['id']=='date':
            i['actions']=[action('scene',id='C02-X00'),action('scene',id='C02-X01'),
                action('if',when={'route':'arland'},then=[action('scene',id='V464-C02-WALK-A')],otherwise=[action('scene',id='V464-C02-WALK-S')]),
                action('scene',id='V464-C02-GALLERY-TEASE'),action('companion',on=True),action('step',id='C02_V464_INTERLUDE')]

    interludes=[
        interact('v464_park','taman_kota',1030,670,'Jalan bersama di taman',[
          action('scene',id='V464-C02-PARK'),action('step',id='C02_DATE')],when={'flags':['V464_WALK_PARK']}),
        interact('v464_later','cafe',650,420,'Duduk dan rencanakan besok',[
          action('scene',id='V464-C02-LATER'),action('step',id='C02_DATE')],when={'flags':['V464_WALK_LATER']}),
        interact('v464_solo','arcade',520,620,'Selesaikan gambar Sofia',[
          action('scene',id='V464-C02-SOLO'),action('step',id='C02_DATE')],when={'flags':['V464_WALK_SOLO']},route='sofia'),
        interact('v464_ask','cafe',700,390,'Dengarkan cerita Sofia',[
          action('scene',id='V464-C02-ASK'),action('step',id='C02_DATE')],when={'flags':['V464_WALK_ASK']},route='arland'),
        interact('v464_recover','cafe',400,430,'Lanjutkan kencan',[
          action('scene',id='V464-C02-LATER'),action('step',id='C02_DATE')],
          when={'notFlags':['V464_WALK_PARK','V464_WALK_LATER','V464_WALK_SOLO','V464_WALK_ASK']})]
    q['steps']=[x for x in q['steps'] if x['id'] not in ('C02_V464_INTERLUDE','C03_V464_GALLERY_PREP','C04_V464_A_PROJECTOR','C04_V464_A_GALLERY','C04_V464_S_GALLERY','C04_V464_S_REFLECT')]
    q['steps'].append(step('C02_V464_INTERLUDE','C02',('Lakukan rencana jalan atau obrolan pilihanmu','Selesaikan aktivitas pribadi atau jalan bersama'),interludes))

    # New playable prep step before entering C4; uses new gallery map and collision.
    old = steps['C03_PICNIC']['interactables'][0]['actions']
    assert any(x.get('do')=='chapterEnd' for x in old) or any(x.get('id')=='C03_V464_GALLERY_PREP' for x in old)
    replace_actions('C03_PICNIC','picnic',[
       action('scene',id='C03-X02'),action('removeItem',id='roti_lapis'),
       action('scene',id='V464-C03-PROMISE'),
       action('warp',area='galeri_komunitas',x=480,y=532,dir='up'),
       action('step',id='C03_V464_GALLERY_PREP')])
    prep=[
       interact('gallery_seat','galeri_komunitas',290,410,'Siapkan kursi untuk Arland',[
         action('scene',id='V464-C03-SEAT'),action('flag',id='V464_PREP_SEAT_DONE'),action('count',id='v464_gallery_prep',add=1)],when={'notFlags':['V464_PREP_SEAT_DONE']},radius=110),
       interact('gallery_projector','galeri_komunitas',705,405,'Periksa sudut proyektor',[
         action('if',when={'route':'arland'},then=[action('scene',id='V464-C03-PROJECTOR')],otherwise=[action('scene',id='V464-C03-SKETCH')]),
         action('flag',id='V464_PREP_ART_DONE'),action('count',id='v464_gallery_prep',add=1)],when={'notFlags':['V464_PREP_ART_DONE']},radius=110)]
    q['steps'].append(step('C03_V464_GALLERY_PREP','C03',('Siapkan kursi dan lihat proyektor di galeri','Tata gambar dan kursi di galeri komunitas'),prep,
      complete={'counter':'v464_gallery_prep','count':2,'actions':[
          action('scene',id='V464-C03-END'), action('chapterEnd',chapter='C03'),
          action('companion',on=False), action('warp',area='$ROOM',x=480,y=440,dir='down'),
          action('chapterCard',chapter='C04'), action('if',when={'route':'arland'},
              then=[action('step',id='C04_A_WAKE')],otherwise=[action('step',id='C04_S_WAKE')])]}))

    replace_actions('C04_A_WAKE','phone4',[
        action('sfx',id='page'),action('scene',id='V464-C04-A-MORNING'),action('step',id='C04_V464_A_PROJECTOR')])
    replace_actions('C04_S_WAKE','phone4',[
        action('sfx',id='page'),action('scene',id='V464-C04-S-MORNING'),
        action('warp',area='galeri_komunitas',x=480,y=530,dir='up'),action('step',id='C04_V464_S_GALLERY')])

    # A branch: player actually operates projector in own room, then travels to venue.
    q['steps'].append(step('C04_V464_A_PROJECTOR','C04',
         ('Putuskan sikap saat proyektor rusak di meja','Proyektor sedang diperbaiki'),
         [interact('projector_v464','arland_room',730,420,'Perbaiki proyektor atau kirim kabar',[
             action('scene',id='V464-C04-A-PROJECTOR'),action('flag',id='V464_PROMISE_MISSED'),
             action('warp',area='galeri_komunitas',x=480,y=530,dir='up'),action('step',id='C04_V464_A_GALLERY')],radius=100)]))
    q['steps'][-1]['interactables'][0]['sprite']={'image':'items/v464_projector.png','x':730,'y':410,'bob':False}
    q['steps'].append(step('C04_V464_A_GALLERY','C04',
         ('Temukan kursi kosong setelah acara galeri','Pameran selesai'),
         [interact('empty_chair_a','galeri_komunitas',290,410,'Lihat kursi bertuliskan ARLAND',[
             action('music',id='cinema_gallery_empty'), action('cine',cmds=gallery_cine(False)),
             action('scene',id='V464-C04-A-LATE'),action('scene',id='V464-C04-A-HONEST'),
             action('if',when={'flags':['V464_A_WARN']},then=[action('scene',id='V464-C04-SEAT-REFLECT-A')],otherwise=[]),
             action('warp',area='cafe',x=400,y=270,dir='down'),action('step',id='C04_A_CAFE')],radius=110)]))
    q['steps'].append(step('C04_V464_S_GALLERY','C04',
         ('Sampaikan cerita di depan pengunjung galeri','Mulai presentasi sketsa di galeri'),
         [interact('stage_s_v464','galeri_komunitas',520,320,'Mulai presentasi gambar Sofia',[
             action('music',id='cinema_gallery_empty'), action('cine',cmds=gallery_cine(True)),
             action('scene',id='V464-C04-S-PRESENT'),action('step',id='C04_V464_S_REFLECT')],radius=115)]))
    q['steps'].append(step('C04_V464_S_REFLECT','C04',
        ('Lihat kembali kursi yang kosong','Putuskan apa yang Sofia lakukan setelah acara'),
        [interact('chair_s_v464','galeri_komunitas',290,410,'Renungkan kursi yang kosong',[
            action('scene',id='V464-C04-S-AFTER'),action('scene',id='V464-C04-SEAT-REFLECT-S'),
            action('warp',area='cafe',x=400,y=270,dir='down'),action('step',id='C04_S_CAFE')],radius=110)]))

    # Retain old rain chapter quest/lantern mechanics but make their story consistent.
    # The Empty Seat event occurs before older C04 quest nodes. Avoid older statements
    # that suggest Arland had a dead phone instead of missing the gallery.
    for sid in ['C04-A00','C04-A02','C04-A01','C04-S00','C04-S02','C04-S01','C04-A-HALTE','C04-S-LIBRARY','C04-S-LETTER']:
        if sid in s['scenes']:
            patch(s,sid,dialogue=reframe_legacy(sid))

    # Additional game cutscenes and route memory scene at C05+C06.
    for x in q['steps']:
        if x['id']=='C05_MEET':
            for it in x['interactables']:
                if it['id']=='meet5':
                    it['actions'] = [action('scene',id='C05-X02'),action('companion',on=True),
                        action('if',when={'route':'arland'},then=[action('scene',id='V464-C05-MEMORY-A')],otherwise=[action('scene',id='V464-C05-MEMORY-S')]),
                        action('cine',cmds=memory_cine()),action('scene',id='C05-X03'),action('scene',id='V464-C05-REPAIR'),
                        action('step',id='C05_STARMAP')]
        elif x['id']=='C06_FINAL':
            for it in x['interactables']:
                if it['id']=='pages':
                    old_actions=it['actions']
                    idx=next(i for i,a in enumerate(old_actions) if a.get('do')=='scene' and a.get('id')=='C06-X01')
                    # Run the actual existing page puzzle first; conditional montage only after success.
                    inserted=[action('music',id='cinema_our_tomorrow'),
                       action('cine',cmds=finale_cine()),
                       action('scene',id='V464-C06-EMPTY-SEAT'),
                       action('scene',id='V464-C06-MEMORY-WALK'),
                       action('if',when={'flags':['V464_WALK_PARK']},then=[action('scene',id='V464-C06-WALK-PARK')],otherwise=[]),
                       action('if',when={'flags':['V464_WALK_LATER']},then=[action('scene',id='V464-C06-WALK-LATER')],otherwise=[]),
                       action('if',when={'flags':['V464_WALK_SOLO']},then=[action('scene',id='V464-C06-WALK-SOLO')],otherwise=[]),
                       action('if',when={'flags':['V464_WALK_ASK']},then=[action('scene',id='V464-C06-WALK-ASK')],otherwise=[]),
                       action('if',when={'flags':['V464_A_WARN']},then=[action('scene',id='V464-C06-PAYOFF-WARN')],otherwise=[]),
                       action('if',when={'flags':['V464_A_SILENT']},then=[action('scene',id='V464-C06-PAYOFF-SILENT')],otherwise=[]),
                       action('if',when={'flags':['V464_A_HELP']},then=[action('scene',id='V464-C06-PAYOFF-HELP')],otherwise=[]),
                       action('if',when={'flags':['V464_S_DRAW']},then=[action('scene',id='V464-C06-PAYOFF-DRAW')],otherwise=[]),
                       action('if',when={'flags':['V464_S_SPACE']},then=[action('scene',id='V464-C06-PAYOFF-SPACE')],otherwise=[]),
                       action('if',when={'flags':['V464_S_SPEAK']},then=[action('scene',id='V464-C06-PAYOFF-SPEAK')],otherwise=[])]
                    # Always reconstruct the complete montage. Earlier runs already
                    # contain most v4.6.4 scenes; keeping that stale prefix would
                    # silently drop the Chapter 2 choices during a second apply.
                    original_lead = [a for a in old_actions[:idx]
                                     if a.get('do') not in ('scene', 'if', 'cine', 'music')]
                    it['actions'] = original_lead + inserted + old_actions[idx:]

    # Gallery map requires a real pixel art background and matching collision.
    maps['areas']['galeri_komunitas']={
        'name':'Galeri Komunitas — Satu Kursi Kosong','image':'maps/galeri_komunitas.png',
        'w':960,'h':640,'music':'cafe','ambient':'rain_window','spawn':[480,530],
        'indoor':True,
        'walls':[[0,0,960,84],[0,0,80,640],[880,0,80,640],[0,614,375,26],[585,614,375,26],
                 [155,115,130,52],[668,115,138,52],[403,106,150,37]],
        'ellipses':[], 'props':[], 'gates':[], 'animals':[], 'water':[],
        'doors':[{'id':'gallery_exit','label':'Kembali ke Kafe Senja','rect':[433,606,94,33],
                  'to':'cafe','tx':400,'ty':290,'dir':'down'}],
        'examine':[{'id':'gallery_art','label':'Lihat sketsa Sofia','x':520,'y':300,'r':95,
           'lines':{'arland':[{'s':'arland','e':'senyum','t':'Dia gambar semua ini dengan hati-hati.'}],
                    'sofia':[{'s':'sofia','e':'senyum','t':'Gambarku mungkin sederhana, tapi ini bagian dari diriku.'}]}}],
        'storyVersion':'v4.6.4', 'visualStyle':'original_16bit_gallery'}
    # Door from cafe is accessible beyond main chapter and not used to bypass quest sequence.
    cafe=maps['areas']['cafe']
    cafe['doors']=[d for d in cafe['doors'] if d.get('id')!='cafe_to_gallery_v464']
    cafe['doors'].append({'id':'cafe_to_gallery_v464', 'label':'Galeri Komunitas',
                           'rect':[80,430,70,70], 'to':'galeri_komunitas',
                           'tx':480, 'ty':525, 'dir':'up',
                           'locked':[{'when':{'maxChapter':'C02'},'text':'Galeri sedang menyiapkan pameran.'}]})

    # Audience is real in-world NPCs while Sofia presents. After the event,
    # their step conditions disappear, leaving the deliberately empty hall.
    new_guests = [
       {'id':'v464_gallery_guest_laras','name':'Bu Laras','sprite':'laras','area':'galeri_komunitas','x':245,'y':502,'dir':'up','wander':0,
        'when':{'steps':['C04_V464_S_GALLERY']}},
       {'id':'v464_gallery_guest_raka','name':'Kak Raka','sprite':'raka','area':'galeri_komunitas','x':705,'y':510,'dir':'up','wander':0,
        'when':{'steps':['C04_V464_S_GALLERY']}},
       {'id':'v464_gallery_guest_tika','name':'Tika','sprite':'tika','area':'galeri_komunitas','x':610,'y':488,'dir':'up','wander':0,
        'when':{'steps':['C04_V464_S_GALLERY']}}]
    q['townNpcs']=[n for n in q['townNpcs'] if not n.get('id','').startswith('v464_gallery_guest_')]
    q['townNpcs'].extend(new_guests)

    # Memorable artifacts are separate flags, not fake romance meters.
    entry_specs=[
      ('v464_invitation','C03','shared','V464_GALLERY_PROMISED','items/v464_gallery_ticket.png','Undangan yang Dijaga','Sofia meminta Arland hadir di galeri. Ia tidak meminta hadiah; cukup seseorang yang duduk di kursi dekat jendela.'),
      ('v464_empty_seat','C04','shared','V464_SEAT_EMPTY','items/v464_empty_seat.png','Kursi yang Kosong','Arland tidak hadir saat Sofia menyampaikan cerita gambar pertamanya. Niat baik tidak menghapus rasa kecewa.'),
      ('v464_projector','C04','arland','V464_ARLAND_REALIZES','items/v464_projector.png','Proyektor dan Sebuah Janji','Arland belajar bahwa membuat kejutan tidak sama dengan hadir ketika dibutuhkan.'),
      ('v464_sketch','C04','sofia','V464_SEAT_EMPTY','items/v464_sketch.png','Sketsa yang Tidak Dihapus','Sofia boleh kecewa. Ia juga boleh memilih kapan akan bercerita dan bagaimana menyimpan ingatannya.'),
      ('v464_two_sides','C05','shared','V464_QUIET_TWO_SIDES','items/v464_two_sides.png','Dua Sisi, Satu Hari','Satu pihak memperbaiki proyektor; pihak lain melihat kursi kosong. Keduanya nyata, tetapi hanya dipahami ketika didengarkan bersama.'),
      ('v464_seat_healed','C06','shared','V464_SEAT_RESTORED','items/v464_seat_healed.png','Gambar yang Tidak Dihapus','Mereka tidak menghapus hari yang menyakitkan. Mereka belajar menghadirkan hari baru di sebelahnya.'),
    ]
    b['entries']=[e for e in b['entries'] if not str(e.get('id','')).startswith('v464_')]
    for id_,chapter,route,unlock,icon,title,text in entry_specs:
        b['entries'].append({'id':id_,'chapter':chapter,'route':route,
                            'type':'fictional_memory','unlock':unlock,'icon':icon,
                            'title':title,'text':text})
    b.setdefault('items',{}).update({
        'v464_gallery_ticket':{'name':'Undangan Galeri','icon':'items/v464_gallery_ticket.png',
            'desc':'Sebuah undangan yang tidak harus ditepati dengan hadiah, melainkan dengan kehadiran.'},
        'v464_empty_seat_art':{'name':'Sketsa Kursi Kosong','icon':'items/v464_empty_seat.png',
            'desc':'Dua gambar: yang pertama tidak dihapus, yang kedua dibuat setelah mereka belajar mendengar.'}})

    # Retain legacy files and schemas; all canon ending IDs remain unchanged.
    for file_name,data in [('story.json',s),('quests.json',q),('memory_book.json',b),('maps.json',maps)]:
        (DATA / file_name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Story Overhaul patched: {len(s["scenes"])} scenes, {len(q["steps"])} steps, '
          f'{len(maps["areas"])} maps, {len(b["entries"])} memories')


def lines_to_tuple(seq):
    return [(x['s'],x.get('e','neutral'),x['t']) for x in seq]


def gallery_cine(speaker):
    caption = 'Hari Pameran' if speaker else 'Setelah Tepuk Tangan'
    subtitle = 'Berani menunjukkan karya' if speaker else 'Satu tempat yang tidak diisi'
    return [
      {'c':'bars','on':True,'t':0.55},
      {'c':'cam','x':475,'y':320,'zoom':1.17,'t':2.3},
      {'c':'caption','text':caption,'sub':subtitle,'t':3.0},
      {'c':'shot','focus':'player','zoom':1.3,'frame':'intimate','t':1.3,'bars':False},
      {'c':'bars','on':False,'t':0.65}]


def memory_cine():
    return [
      {'c':'bars','on':True,'t':0.35},
      {'c':'caption','text':'Dua Sisi, Satu Hari','sub':'Tidak ada satu ingatan yang cukup sendiri','t':3.1},
      {'c':'shot','focus':'player','zoom':1.23,'t':1.3,'frame':'intimate','bars':False},
      {'c':'fx','kind':'glow','on':'player','t':3.2},
      {'c':'bars','on':False,'t':0.5}]


def finale_cine():
    return [
      {'c':'bars','on':True,'t':0.5},
      {'c':'cam','x':960,'y':490,'zoom':1.3,'t':2.0},
      {'c':'caption','text':'Our Tomorrow','sub':'Satu cerita, dua suara, banyak hari lagi','t':3.5},
      {'c':'fx','kind':'petals','on':'player','t':4.4},
      {'c':'bars','on':False,'t':0.55}]


def reframe_legacy(sid):
    revised={
      'C04-A00':[L('arland','Acara galeri hari ini. Sofia tadi bilang ia gugup.'),L('arland','Proyektor itu nggak boleh bikin aku lupa janjiku.'),L('narrator','Arland melirik jam—waktu terasa lebih cepat dari biasanya.')],
      'C04-A02':[L('raka','Sofia sudah selesai presentasi. Tadi dia sempat lihat ke pintu beberapa kali.'),L('arland','Aku datang telat, Kak.'),L('raka','Kalau kamu minta maaf, coba dengerin dulu apa yang dia rasakan, ya.')],
      'C04-A01':[L('narrator','Hujan menghantam atap halte. Arland meremas tiket galeri yang belum terpakai.'),L('arland','Aku bikin kejutan, padahal yang dia minta cuma aku datang.'),L('arland','Aku harus tanggung jawab. Tapi aku nggak boleh memaksa Sofia langsung memaafkan.', 'serius')],
      'C04-S00':[L('sofia','Aku menyiapkan semuanya. Aku berharap Arland melihatnya.'),L('narrator','Galeri sudah sepi, tetapi kursi bertanda namanya masih tampak di ingatan Sofia.'),L('sofia','Aku boleh kecewa. Dan nanti aku akan ceritakan alasannya.', 'serius')],
      'C04-S02':[L('raka','Tadi aku dengar pamerannya berjalan bagus, Sof.'),L('sofia','Iya, Kak. Aku berhasil. Cuma... ada seseorang yang nggak sempat lihat.'),L('raka','Selamat atas keberanianmu. Kecewanya juga boleh kamu rasakan.')],
      'C04-S01':[L('narrator','Hujan turun di gazebo. Sofia memeluk buku sketsanya.'),L('sofia','Aku masih ingin Arland mengerti, tapi aku juga butuh waktu buat tenang.'),L('narrator','Sebuah langkah mendekat dari balik hujan.')],
      'C04-A-HALTE':[L('narrator','Halte yang basah. Tiket galeri kusut dalam genggaman Arland.'),L('arland','Aku tidak bisa mengulang acaranya.'),L('arland','Aku masih bisa mendengar seluruh cerita Sofia, kalau ia sudah siap.')],
      'C04-S-LIBRARY':[L('laras','Kadang sebuah surat terasa berat karena penulisnya takut tidak dimengerti.'),L('sofia','Aku cuma pengen bisa bilang aku kecewa tanpa takut menyakiti dia.'),L('laras','Berkata jujur dengan lembut juga bentuk keberanian, Sofia.')],
      'C04-S-LETTER':[L('narrator','Sofia membalik halaman surat lama yang tersimpan di perpustakaan.'),
                      L('sari','Ada hari ketika kita berharap seseorang hadir, tetapi kursinya tetap kosong.'),
                      L('sofia','Iya... aku ngerti rasanya.'),
                      L('sari','Kekecewaan tidak harus disimpan sendirian.'),
                      L('sofia','Aku mau bicara ketika sudah siap.'),
                      L('narrator','Sofia menutup suratnya perlahan.'),
                      L('sofia','Aku akan coba. Pelan-pelan.')]
    }
    return revised[sid]


if __name__ == '__main__':
    apply()
