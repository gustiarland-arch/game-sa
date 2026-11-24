"""Dunia hidup v1.4: jadwal harian NPC, warga tambahan, dialog sesuai jam/cuaca, misi sampingan warga, dan sebaran hewan.
Di-exec dari build_content.py (memakai helper & daftar NPCS/SIDE/SIDE_QUESTS/ITEMS/ENTRIES/SPEAKERS milik file itu).
Titik jadwal ditulis kira-kira; build_content men-snap ke sel terjangkau terdekat (lihat snap_schedules)."""

H = 'hujan'
def at(t, area=None, pt=None, dir='down', wander=0, weather=None, hidden=False):
    e = {'at': t}
    if hidden: e['hidden'] = True
    else: e.update({'area': area, 'x': pt[0], 'y': pt[1], 'dir': dir, 'wander': wander})
    if weather: e['weather'] = weather if isinstance(weather, list) else [weather]
    return e
def home(n): return (n['area'], (n['x'], n['y']), n['dir'])
def N(i): return NPCS[NPC_IDX(i)]

def flavor(npc_id, d):
    """sisipkan dialog suasana sebelum dialog yang hanya bergantung chapter (dialog misi tetap prioritas)."""
    ds = N(npc_id)['dialogs']
    for k, x in enumerate(ds):
        if set(x['when']) <= {'chapters', 'minChapter'}: ds.insert(k, d); return
    ds.insert(len(ds) - 1, d)
def hrs(a, b, **kw): w = {'hours': [a, b]}; w.update(kw); return w

# ------------------------------------------------------------------ jadwal warga lama
def sched(i, entries, wander=0):
    n = N(i); n['schedule'] = entries; n['wander'] = wander
a, p_, d_ = home(N('raka'))
sched('raka', [at('06:00', 'riverside', (700, 690), 'right', 120), at('07:30', a, p_, d_),
               at('14:30', 'plaza', (1330, 790), 'left', 40), at('15:15', a, p_, d_), at('22:00', hidden=True)], wander=30)
a, p_, d_ = home(N('melati'))
sched('melati', [at('06:00', 'plaza', (520, 1000), 'down', 60), at('08:00', a, p_, d_),
                 at('12:00', 'jalan_kota', (700, 820), 'down', 40), at('13:00', a, p_, d_),
                 at('18:00', 'perumahan', (1170, 600), 'down', 50), at('20:30', hidden=True)], wander=24)
a, p_, d_ = home(N('juna'))
sched('juna', [at('06:00', hidden=True), at('09:30', a, p_, d_), at('17:30', 'jalan_kota', (1100, 810), 'down', 80),
               at('18:30', a, p_, d_), at('23:30', hidden=True)], wander=30)
a, p_, d_ = home(N('sari'))
sched('sari', [at('06:00', 'taman_kota', (560, 460), 'down', 40), at('06:00', a, p_, d_, 30, weather=H),
               at('09:00', a, p_, d_, 50), at('16:30', 'perumahan', (860, 900), 'down', 30), at('16:30', hidden=True, weather=H),
               at('19:30', hidden=True)])
a, p_, d_ = home(N('dito'))
sched('dito', [at('06:00', 'perumahan', (1000, 760), 'down', 90), at('07:30', hidden=True),
               at('12:30', a, p_, d_, 110), at('12:30', 'arcade', (480, 470), 'up', 50, weather=H),
               at('17:30', 'perumahan', (1000, 760), 'down', 90), at('19:00', hidden=True)])
a, p_, d_ = home(N('udin'))
sched('udin', [at('06:00', 'dermaga', (1400, 540), 'down', 40), at('10:30', a, p_, d_, 30),
               at('15:00', 'cafe', (300, 520), 'right', 0), at('16:00', a, p_, d_, 30),
               at('19:00', hidden=True), at('06:00', 'cafe', (300, 520), 'right', 0, weather=H)])
a, p_, d_ = home(N('pos'))
sched('pos', [at('06:00', hidden=True), at('08:00', a, p_, d_, 20), at('10:00', 'jalan_kota', (1880, 830), 'right', 60),
              at('12:00', 'perumahan', (1290, 600), 'down', 80), at('14:00', a, p_, d_, 40), at('17:00', hidden=True)])
a, p_, d_ = home(N('laras'))
sched('laras', [at('06:00', 'perumahan', (900, 640), 'down', 60), at('08:00', a, p_, d_, 40), at('20:00', hidden=True)])
a, p_, d_ = home(N('bayu'))
sched('bayu', [at('06:00', a, p_, d_, 60), at('12:00', 'riverside', (1000, 700), 'down', 60), at('14:00', a, p_, d_, 60),
               at('21:00', hidden=True), at('06:00', 'cafe', (660, 520), 'left', 0, weather=H)])
a, p_, d_ = home(N('nara'))
sched('nara', [at('06:00', hidden=True), at('10:00', 'perpustakaan', (1180, 690), 'left', 40), at('16:00', hidden=True),
               at('18:00', a, p_, d_, 30), at('18:00', 'perpustakaan', (1180, 690), 'left', 40, weather=H)])

# dialog suasana warga lama (jam & cuaca)
flavor('raka', D(hrs('06:00', '07:30'), [chat('raka', 'Lari pagi dulu sebelum buka kafe. Biji kopinya juga butuh pemiliknya segar.', 'senang')]))
flavor('raka', D(hrs('14:30', '15:15'), [chat('raka', 'Lima belas menit istirahat. Barista juga perlu minum yang bukan kopi.', 'tertawa')]))
flavor('raka', D({'weatherIs': [H]}, [chat('raka', 'Hujan begini cokelat panas laku keras. Mau satu? Hangat sampai ke hati.', 'senyum')]))
flavor('melati', D(hrs('06:00', '08:00'), [chat('melati', 'Bunga plaza harus disiram sebelum matahari tinggi. Pagi, Nak.', 'senyum')]))
flavor('melati', D(hrs('12:00', '13:00'), [chat('melati', 'Makan siang di kios kecil ini. Bunga-bunga di toko bisa menunggu sebentar.', 'senyum')]))
flavor('melati', D(hrs('18:00', '20:30'), [chat('melati', 'Pulang dulu. Rumah juga punya pot-pot yang menunggu disiram.', 'neutral')]))
flavor('juna', D(hrs('17:30', '18:30'), [chat('juna', 'Cari angin dulu. Mata perlu lihat sesuatu selain layar.', 'senang')]))
flavor('sari', D(hrs('06:00', '09:00', weatherIs=['cerah', 'berangin', 'berawan']), [chat('sari', 'Senam pagi, Nak. Lutut Nenek sudah tua, tapi semangatnya belum.', 'tertawa')]))
flavor('sari', D(hrs('16:30', '19:30'), [chat('sari', 'Duduk di sini sore-sore, Nenek bisa lihat semua jendela menyala satu per satu.', 'senyum')]))
flavor('dito', D(hrs('06:00', '07:30'), [chat('dito', 'Dito mau sekolah! Kata Bu Guru hari ini ada gambar bebas!', 'senang')]))
flavor('dito', D(hrs('17:30', '19:00'), [chat('dito', 'Sebentar lagi dipanggil Ibu makan. Main petak umpet sekali lagi, Kak?', 'tertawa')]))
flavor('dito', D({'weatherIs': [H]}, [chat('dito', 'Ibu nggak bolehin main di taman kalau hujan. Jadi Dito ke arcade, hehe.', 'tertawa')]))
flavor('udin', D(hrs('06:00', '10:30', weatherIs=['cerah', 'berangin', 'berawan']), [chat('udin', 'Ikan paling lapar waktu subuh. Bapak juga.', 'tertawa')]))
flavor('udin', D(hrs('15:00', '16:00'), [chat('udin', 'Kopi sore di Kafe Senja. Kebiasaan tiga puluh tahun, Nak.', 'senyum')]))
flavor('udin', D({'weatherIs': [H]}, [chat('udin', 'Hujan. Joran istirahat, Bapak juga. Kopi di sini lebih enak kalau dengar hujan.', 'senyum')]))
flavor('pos', D(hrs('10:00', '14:00'), [chat('pos', 'Rute siang: Jalan Kota, lalu Perumahan. Kaki Bapak sudah hafal semua lubang di jalan.', 'senang')]))
flavor('laras', D(hrs('06:00', '08:00'), [chat('laras', 'Jalan pagi dulu sebelum membuka perpustakaan. Buku tidak suka penjaga yang mengantuk.', 'senyum')]))
flavor('bayu', D(hrs('12:00', '14:00'), [chat('bayu', 'Mengecek perahu sewa di tepi danau. Satu dayungnya hilang lagi, entah ke mana.', 'neutral')]))
flavor('bayu', D({'weatherIs': [H]}, [chat('bayu', 'Dermaga tutup kalau hujan. Jadi saya numpang kopi di sini.', 'tertawa')]))
flavor('nara', D(hrs('10:00', '16:00'), [chat('nara', 'Siang hari aku baca peta bintang lama di sini. Malamnya baru mencocokkan dengan langit.', 'senyum')]))
flavor('nara', D({'weatherIs': [H]}, [chat('nara', 'Langit tertutup awan. Malam ini bintangnya kubaca dari buku saja.', 'sedih')]))

# ------------------------------------------------------------------ warga tambahan
for sid, nm in [('rini', 'Bu Rini'), ('harun', 'Pak Harun'), ('tika', 'Tika'), ('eko', 'Mas Eko'), ('wulan', 'Bu Wulan'), ('darmo', 'Kakek Darmo')]:
    SPEAKERS[sid] = {'name': nm, 'portrait': None, 'style': 'npc', 'sprite': sid}
TOWNW = {'minChapter': 'C01'}
NPCS.append({'id': 'rini', 'name': 'Bu Rini', 'sprite': 'rini', 'area': 'jalan_kota', 'x': 620, 'y': 820, 'dir': 'down', 'when': TOWNW, 'wander': 20,
    'schedule': [at('06:00', 'jalan_kota', (620, 820), 'down', 20), at('14:00', 'plaza', (1360, 620), 'down', 30), at('17:00', 'perumahan', (1580, 600), 'down', 40), at('19:00', hidden=True),
                 at('06:00', 'cafe', (420, 560), 'right', 0, weather=H)],
    'dialogs': [
        D({'flags': ['SQ_KUE_DARMO'], 'notFlags': ['SQ_KUE_DONE']}, [say([('rini', 'senang', 'Kakek Darmo bilang kuenya enak? Syukurlah. Ini, bawa satu kotak untuk kalian berdua.')]),
            say([('arland', 'senyum', 'Terima kasih, Bu Rini. Nanti kami makan berdua di dermaga.')], route='arland'), say([('sofia', 'senyum', 'Terima kasih, Bu Rini! Yang hijau masih jadi favoritku.')], route='sofia'), *fl('SQ_KUE_DONE'), rm('kotak_kue'), it('kue_lapis'), sfx()]),
        D({'minChapter': 'C02', 'notFlags': ['SQ_KUE_START'], 'hours': ['06:00', '14:00']}, [say([('rini', 'neutral', 'Nak, boleh minta tolong? Kakek Darmo di dermaga belum sarapan. Antar kue ini, ya.'), ('rini', 'senyum', 'Dia biasanya di ujung dermaga sampai siang. Hati-hati, kotaknya masih hangat.')]),
            *fl('SQ_KUE_START'), it('kotak_kue'), toast('Misi sampingan: Kue untuk Kakek Darmo')]),
        D({'flags': ['SQ_KUE_START'], 'notFlags': ['SQ_KUE_DARMO']}, [chat('rini', 'Kakek Darmo di dermaga, Nak. Kalau sudah siang, kadang dia pindah ke Tepi Danau.', 'neutral')]),
        D(hrs('06:00', '09:00'), [chat('rini', 'Kue lapis, kue cucur, nagasari! Masih hangat, baru diangkat subuh tadi.', 'senang')]),
        D(hrs('14:00', '17:00'), [chat('rini', 'Sisa dagangan pagi, Nak. Separuh harga untuk yang senyum.', 'tertawa')]),
        D({'weatherIs': [H]}, [chat('rini', 'Hujan, jadi Bu Rini titip dagangan di kafe Kak Raka. Pembelinya malah lebih banyak.', 'senyum')]),
        D({}, [chat('rini', 'Bu Rini sudah jualan kue di jalan ini sejak kalian masih kecil. Kalian dulu suka yang warna hijau.', 'senyum')])]})
NPCS.append({'id': 'harun', 'name': 'Pak Harun', 'sprite': 'harun', 'area': 'taman_kota', 'x': 1300, 'y': 800, 'dir': 'left', 'when': TOWNW, 'wander': 60,
    'schedule': [at('06:00', 'taman_kota', (1300, 800), 'left', 90), at('11:00', 'plaza', (520, 1000), 'down', 60), at('13:00', 'taman_kota', (700, 560), 'down', 90),
                 at('17:00', 'perumahan', (1700, 1080), 'down', 30), at('18:30', hidden=True), at('06:00', hidden=True, weather=H)],
    'dialogs': [
        D({'flags': ['PET_CAT', 'PET_DOG', 'PET_DUCK'], 'notFlags': ['SQ_HEWAN_DONE'], 'anyFlags': ['SQ_HEWAN_START']}, [say([('harun', 'senang', 'Kucing, anjing, sampai bebek mau kalian elus? Hewan-hewan kota ini percaya sama kalian.'), ('harun', 'senyum', 'Ini kantong biji bunga. Taburkan di mana saja kalian suka.')]), *fl('SQ_HEWAN_DONE'), it('biji_bunga'), sfx()]),
        D({'minChapter': 'C02', 'notFlags': ['SQ_HEWAN_START']}, [say([('harun', 'neutral', 'Taman ini bukan cuma untuk manusia, Nak. Ada kucing, anjing, bebek di kolam, burung, kelinci, tupai.'), ('harun', 'senyum', 'Coba kenali mereka. Elus seekor kucing, seekor anjing, dan seekor bebek, lalu ceritakan ke Bapak.')]),
            *fl('SQ_HEWAN_START'), toast('Misi sampingan: Teman Berbulu')]),
        D({'flags': ['SQ_HEWAN_START'], 'notFlags': ['SQ_HEWAN_DONE']}, [chat('harun', 'Kucing suka di plaza dan perumahan, anjing di taman, bebek di kolam dan danau. Dekati pelan-pelan.', 'neutral')]),
        D(hrs('06:00', '09:00'), [chat('harun', 'Rumput dipangkas pagi-pagi supaya embunnya tidak ikut terbuang. Begitu kata ayah Bapak.', 'senyum')]),
        D({'weatherIs': ['berangin']}, [chat('harun', 'Angin begini, daun gugur lebih cepat dari sapu Bapak. Ya sudah, kita berlomba.', 'tertawa')]),
        D({}, [chat('harun', 'Tiga puluh tahun merawat taman ini. Pohon-pohonnya sudah seperti anak sendiri.', 'senyum')])]})
NPCS.append({'id': 'tika', 'name': 'Tika', 'sprite': 'tika', 'area': 'taman_kota', 'x': 1160, 'y': 600, 'dir': 'left', 'when': TOWNW, 'wander': 100,
    'schedule': [at('06:00', 'perumahan', (1100, 780), 'down', 80), at('07:30', hidden=True), at('12:30', 'taman_kota', (1160, 600), 'left', 120),
                 at('12:30', 'arcade', (560, 470), 'up', 40, weather=H), at('17:30', 'perumahan', (1100, 780), 'down', 80), at('19:00', hidden=True)],
    'dialogs': [
        D(hrs('06:00', '07:30'), [chat('tika', 'Tika nunggu Dito. Dia selalu telat, padahal rumahnya cuma sebelah!', 'serius')]),
        D({'weatherIs': [H]}, [chat('tika', 'Dito kalah terus main mesin capit. Tika sudah dapat dua boneka!', 'tertawa')]),
        D({'flags': ['PET_RABBIT']}, [chat('tika', 'Kakak bisa pegang kelinci? Dia selalu lari kalau Tika dekati. Curang!', 'kaget')]),
        D({}, [chat('tika', 'Kakak tahu nggak? Kelinci di taman ini suka sembunyi di dekat semak. Tapi jangan lari, nanti dia kabur.', 'senang')])]})
NPCS.append({'id': 'eko', 'name': 'Mas Eko', 'sprite': 'eko', 'area': 'riverside', 'x': 500, 'y': 690, 'dir': 'right', 'when': TOWNW, 'wander': 220,
    'schedule': [at('06:00', 'riverside', (700, 690), 'right', 260), at('08:00', hidden=True), at('17:00', 'taman_kota', (1000, 560), 'down', 200),
                 at('18:30', 'jalan_kota', (1000, 820), 'down', 160), at('20:00', hidden=True), at('06:00', hidden=True, weather=H)],
    'dialogs': [
        D(hrs('06:00', '08:00'), [chat('eko', 'Lima kilo keliling danau tiap pagi! Mau ikut? Ayo, ayo, jangan malas!', 'senang')]),
        D(hrs('17:00', '20:00'), [chat('eko', 'Pulang kerja langsung lari. Kepala penuh angka, harus dikuras keringat.', 'tertawa')]),
        D({}, [chat('eko', 'Kalian sering kelihatan jalan berdua. Bagus, olahraga paling murah itu jalan bareng orang yang disayang.', 'senyum')])]})
NPCS.append({'id': 'wulan', 'name': 'Bu Wulan', 'sprite': 'wulan', 'area': 'perumahan', 'x': 1450, 'y': 600, 'dir': 'down', 'when': TOWNW, 'wander': 40,
    'schedule': [at('06:00', 'perumahan', (1450, 600), 'down', 40), at('09:00', 'jalan_kota', (760, 820), 'down', 60), at('10:30', 'perumahan', (1450, 600), 'down', 40),
                 at('16:00', 'taman_kota', (1050, 520), 'down', 50), at('17:30', 'perumahan', (1450, 600), 'down', 30), at('20:00', hidden=True),
                 at('09:00', 'perumahan', (1450, 600), 'down', 20, weather=H)],
    'dialogs': [
        D(hrs('09:00', '10:30'), [chat('wulan', 'Belanja pagi. Bu Melati selalu kasih setangkai bunga gratis kalau Bu Wulan beli sayur di sebelahnya.', 'senyum')]),
        D(hrs('16:00', '17:30'), [chat('wulan', 'Menjemput Tika dari taman. Anak itu kalau sudah main lupa pulang, persis ayahnya.', 'tertawa')]),
        D({'weatherIs': [H]}, [chat('wulan', 'Jemuran belum diangkat! Eh, maaf, Nak. Hujannya datang tiba-tiba.', 'kaget')]),
        D({}, [chat('wulan', 'Kalau lewat sini sore-sore, mampir. Bu Wulan masak sayur asem kebanyakan terus.', 'senyum')])]})
NPCS.append({'id': 'darmo', 'name': 'Kakek Darmo', 'sprite': 'darmo', 'area': 'dermaga', 'x': 1700, 'y': 520, 'dir': 'down', 'when': TOWNW, 'wander': 0,
    'schedule': [at('06:00', 'dermaga', (1700, 520), 'down', 0), at('12:00', 'riverside', (1520, 690), 'down', 10), at('17:30', hidden=True),
                 at('06:00', 'cafe', (420, 600), 'right', 0, weather=H)],
    'dialogs': [
        D({'flags': ['SQ_KUE_START'], 'notFlags': ['SQ_KUE_DARMO']}, [say([('darmo', 'kaget', 'Kue dari Rini? Wah, masih hangat.'), ('darmo', 'senyum', 'Dulu istri Kakek juga jualan kue di jalan itu. Rini muridnya. Rasanya sama persis.'),
            ('darmo', 'senyum', 'Bilang terima kasih ke Rini. Bilang juga, Kakek masih ingat resepnya.')]), *fl('SQ_KUE_DARMO'), sfx(), toast('Kembali ke Bu Rini')]),
        D(hrs('06:00', '12:00'), [chat('darmo', 'Kakek tidak memancing ikan, Nak. Kakek memancing ketenangan. Ikannya bonus.', 'senyum')]),
        D({'weatherIs': [H]}, [chat('darmo', 'Hujan. Kakek pernah melamar nenek di bawah hujan seperti ini. Dia bilang "iya" sambil basah kuyup.', 'tertawa')]),
        D({}, [chat('darmo', 'Danau ini lebih tua dari kota. Kalau kalian diam cukup lama, ia bercerita.', 'neutral')])]})

# warga latar: mengisi kota pagi-malam (satpam ronda, pelajar, penjual balon, oma jalan sore, ojek pangkalan)
for sid, nm in [('darto', 'Pak Darto'), ('rara', 'Rara'), ('bimo', 'Bimo'), ('ujang', 'Pak Ujang'), ('ina', 'Oma Ina'), ('tigor', 'Bang Tigor')]:
    SPEAKERS[sid] = {'name': nm, 'portrait': None, 'style': 'npc', 'sprite': sid}
def walker(i, nm, area, pt, sched_, dialogs, wander=40):
    NPCS.append({'id': i, 'name': nm, 'sprite': i, 'area': area, 'x': pt[0], 'y': pt[1], 'dir': 'down', 'when': TOWNW, 'wander': wander, 'schedule': sched_, 'dialogs': dialogs})
walker('darto', 'Pak Darto', 'plaza', (960, 960), [at('06:00', hidden=True), at('19:00', 'plaza', (960, 960), 'down', 360), at('21:00', 'jalan_kota', (1000, 760), 'down', 400),
        at('22:30', 'perumahan', (1000, 700), 'down', 360), at('24:00', 'plaza', (960, 640), 'down', 360), at('25:00', 'riverside', (960, 680), 'down', 300)], [
    D(hrs('19:00', '23:00'), [chat('darto', 'Ronda dulu, Nak. Kota kecil begini, yang dijaga bukan cuma rumah, tapi rasa aman.', 'serius')]),
    D(hrs('23:00', '26:00'), [chat('darto', 'Sudah larut. Pulang, istirahat. Besok kota ini masih di sini, kok.', 'neutral')]),
    D({}, [chat('darto', 'Malam ini tenang. Cuma kucing yang ribut di atap.', 'senyum')])])
walker('rara', 'Rara', 'plaza', (900, 900), [at('06:00', 'perumahan', (1240, 760), 'down', 40), at('06:45', 'jalan_kota', (800, 760), 'right', 200), at('07:15', hidden=True),
        at('15:00', 'plaza', (900, 900), 'down', 80), at('15:00', 'cafe', (560, 480), 'down', 0, weather=H), at('17:00', 'taman_kota', (1000, 520), 'down', 120), at('18:45', hidden=True)], [
    D(hrs('06:00', '07:15'), [chat('rara', 'Telat, telat, telat! Bimo, cepetan! Gerbang sekolah tutup jam tujuh!', 'kaget')]),
    D(hrs('15:00', '17:00'), [chat('rara', 'Kami belajar kelompok. Eh, maksudnya... ngobrol kelompok. Hehe.', 'tertawa')]),
    D({}, [chat('rara', 'Kakak berdua lucu, deh. Kayak di komik yang Rara baca.', 'senang')])])
walker('bimo', 'Bimo', 'plaza', (940, 910), [at('06:00', 'perumahan', (1280, 770), 'down', 40), at('06:50', 'jalan_kota', (760, 790), 'right', 200), at('07:20', hidden=True),
        at('15:00', 'plaza', (940, 910), 'left', 80), at('15:00', 'cafe', (600, 480), 'down', 0, weather=H), at('17:00', 'taman_kota', (1040, 540), 'down', 120), at('18:45', hidden=True)], [
    D(hrs('06:00', '07:20'), [chat('bimo', 'Rara bawel. Masih ada lima menit. ...Eh, tiga menit.', 'bingung')]),
    D({'weatherIs': [H]}, [chat('bimo', 'Hujan. Untung Kak Raka nggak ngusir kami walau cuma pesan satu es teh berdua.', 'tertawa')]),
    D({}, [chat('bimo', 'Kakak tahu cara menang di mesin capit? Bang Juna nggak mau kasih tahu.', 'penasaran')])])
walker('ujang', 'Pak Ujang', 'plaza', (1150, 860), [at('06:00', hidden=True), at('09:00', 'taman_kota', (1080, 500), 'down', 60), at('14:30', 'plaza', (1150, 860), 'down', 50),
        at('19:30', hidden=True), at('06:00', hidden=True, weather=H)], [
    D({}, [chat('ujang', 'Balon, balon! Bentuk bintang, kucing, hati. Yang hati laku keras kalau ada pasangan lewat.', 'tertawa')])])
walker('ina', 'Oma Ina', 'riverside', (700, 690), [at('06:00', 'riverside', (700, 690), 'right', 200), at('08:30', hidden=True), at('16:00', 'plaza', (560, 610), 'down', 20),
        at('18:30', hidden=True), at('06:00', hidden=True, weather=H)], [
    D(hrs('06:00', '08:30'), [chat('ina', 'Jalan pagi keliling danau. Dokter bilang bagus untuk jantung. Oma bilang bagus untuk gosip.', 'tertawa')]),
    D({}, [chat('ina', 'Sari itu teman Oma sejak SD. Dulu kami rebutan duduk di bangku ini juga.', 'senyum')])], wander=20)
walker('tigor', 'Bang Tigor', 'plaza', (1060, 1120), [at('06:00', hidden=True), at('07:00', 'plaza', (1060, 1120), 'up', 30), at('12:00', 'jalan_kota', (1900, 700), 'left', 20),
        at('13:00', 'plaza', (1060, 1120), 'up', 30), at('21:30', hidden=True), at('07:00', 'plaza', (1760, 600), 'down', 0, weather=H)], [
    D({'weatherIs': [H]}, [chat('tigor', 'Hujan begini penumpang banyak, tapi Abang berteduh dulu. Motor bisa basah, Abang jangan.', 'tertawa')]),
    D({}, [chat('tigor', 'Ojek, Dek? Bercanda. Kota sekecil ini, jalan kaki berdua lebih romantis.', 'tertawa')])], wander=30)

SIDE_QUESTS += [
    {'id': 'SQ_KUE', 'title': 'Kue untuk Kakek Darmo', 'desc': 'Antar kotak kue Bu Rini ke Kakek Darmo (dermaga pagi, Tepi Danau siang), lalu kembali ke Bu Rini.', 'startFlag': 'SQ_KUE_START', 'doneFlag': 'SQ_KUE_DONE', 'chapter': 'C02'},
    {'id': 'SQ_HEWAN', 'title': 'Teman Berbulu', 'desc': 'Elus seekor kucing, seekor anjing, dan seekor bebek, lalu ceritakan ke Pak Harun (penjaga taman).', 'startFlag': 'SQ_HEWAN_START', 'doneFlag': 'SQ_HEWAN_DONE', 'chapter': 'C02'},
]
ITEMS.update({
    'kotak_kue': ('Kotak Kue Bu Rini', 'items/fruit.png', 'Masih hangat. Untuk Kakek Darmo di dermaga.'),
    'kue_lapis': ('Kue Lapis Bu Rini', 'items/fruit.png', 'Sembilan lapis, resep turun-temurun dari istri Kakek Darmo.'),
    'biji_bunga': ('Kantong Biji Bunga', 'items/paper_flower.png', 'Dari Pak Harun. "Taburkan di mana saja kalian suka."'),
})

# ------------------------------------------------------------------ hewan per area (region [x,y,w,h], water = elips air dari peta)
ANIMALS = {
    'plaza': [{'type': 'cat_orange', 'n': 1, 'region': [200, 900, 1500, 300]}, {'type': 'bird', 'n': 4, 'region': [700, 560, 600, 400]},
              {'type': 'cat_calico', 'n': 1, 'region': [1200, 560, 600, 400], 'day': False}],
    'jalan_kota': [{'type': 'cat_grey', 'n': 1, 'region': [300, 700, 1500, 260], 'day': False}, {'type': 'bird', 'n': 3, 'region': [400, 640, 1200, 300]},
                   {'type': 'dog', 'n': 1, 'region': [900, 700, 900, 250]}],
    'taman_kota': [{'type': 'dog', 'n': 1, 'region': [800, 450, 900, 500]}, {'type': 'rabbit', 'n': 2, 'region': [150, 380, 700, 300]},
                   {'type': 'squirrel', 'n': 2, 'region': [1300, 300, 500, 400]}, {'type': 'bird', 'n': 5, 'region': [900, 450, 800, 500]},
                   {'type': 'duck', 'n': 3, 'water': 'taman_kota#0'}],
    'riverside': [{'type': 'duck', 'n': 4, 'water': 'riverside#0'}, {'type': 'bird', 'n': 3, 'region': [300, 600, 1400, 120]},
                  {'type': 'cat_black', 'n': 1, 'region': [300, 620, 1400, 100], 'day': False}],
    'perumahan': [{'type': 'cat_calico', 'n': 1, 'region': [200, 600, 1700, 300], 'day': False}, {'type': 'chicken', 'n': 3, 'region': [150, 1060, 450, 70]},
                  {'type': 'cat_orange', 'n': 1, 'region': [900, 820, 600, 120], 'day': False}, {'type': 'bird', 'n': 3, 'region': [600, 600, 1000, 300]}],
    'dermaga': [{'type': 'duck', 'n': 3, 'water': 'dermaga#0'}, {'type': 'cat_grey', 'n': 1, 'region': [1300, 480, 500, 80], 'day': False},
                {'type': 'bird', 'n': 3, 'region': [300, 440, 1400, 100]}],
    'hutan_bisik': [{'type': 'rabbit', 'n': 3, 'region': [300, 300, 2000, 1400]}, {'type': 'squirrel', 'n': 4, 'region': [300, 300, 2000, 1400]},
                    {'type': 'bird', 'n': 4, 'region': [300, 300, 2000, 1400]}],
    'bukit_bintang': [{'type': 'rabbit', 'n': 2, 'region': [300, 500, 1300, 600]}],
}
for aid, lst in ANIMALS.items():
    for spec in lst:
        if isinstance(spec.get('water'), str):
            ar, k = spec['water'].split('#'); w = MAPS[ar]['water'][int(k)]; spec['water'] = [w['cx'], w['cy'], w['rx'], w['ry']]

ENTRIES.append(E('m_hewan', 'C02', 'shared', 'fictional_memory', 'SQ_HEWAN_DONE', 'items/paper_flower.png', 'Teman Berbulu', 'Kucing, anjing, dan bebek kota yang mau dielus. Pak Harun bilang itu tanda percaya.'))
ENTRIES.append(E('m_kue', 'C02', 'shared', 'fictional_memory', 'SQ_KUE_DONE', 'items/fruit.png', 'Kue Hangat', 'Resep yang berpindah dari istri Kakek Darmo ke Bu Rini, lalu ke tangan kami.'))
