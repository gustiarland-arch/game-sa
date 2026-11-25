"""v6 story text: per-location lines that replace the shared v4.9/v5.0 template lines.

VIEW[area] = (arrive, pause, (line_pov, emo), (line_partner, emo), close)
  In the Arland route Arland says line_pov and Sofia answers; in the Sofia route the roles swap.
DISC_CLOSE[area] = closing narration of the optional World Trace (v4.9) scene.
"""

VIEW = {
    'PLAZA': (
        "Anak tangga batu menuntun kalian ke balkon di atas taman belakang. Air mancur di bawah berkilau seperti koin yang dilempar.",
        "Lonceng kecil di menara plaza berdentang sekali. Orang-orang di bawah tidak menengok, tetapi kalian berdua menghitungnya.",
        ("Kalau nanti kita lupa jalan pulang, kita naik ke sini dulu, ya. Semua jalan kelihatan dari balkon ini.", 'senyum'),
        ("Setuju. Tempat janjian cadangan: balkon plaza, dekat pot lavender.", 'tertawa'),
        "Balkon plaza kini tercatat sebagai tempat janjian rahasia kalian."),
    'TAMAN_KOTA': (
        "Dari teras batu, kolam koi terbentang seperti cermin yang dibingkai pohon. Bayangan gazebo jatuh tepat di tengah air.",
        "Seekor koi oranye naik ke permukaan, lalu menyelam lagi. Riaknya sampai ke pinggir kolam sebelum hilang.",
        ("Pulau kecil di tengah itu kayaknya cocok buat piknik berdua. Sayang nggak ada jembatannya.", 'penasaran'),
        ("Justru itu yang bikin istimewa. Ada tempat yang cukup dilihat saja.", 'senyum'),
        "Pemandangan kolam koi dari teras tersimpan di Memory Book."),
    'RIVERSIDE': (
        "Papan dek kayu berderit pelan. Danau melebar sampai ke pulau kecil yang ditumbuhi pohon willow.",
        "Seorang bapak di gubuk pancing melambaikan tangan. Perahu dayungnya bergoyang mengikuti ombak.",
        ("Pulau itu kelihatan dekat, tapi pasti jauh kalau didayung.", 'penasaran'),
        ("Kalau suatu hari kita sewa perahu, kamu yang dayung, aku yang bawa bekal.", 'tertawa'),
        "Senja di dek danau tersimpan di Memory Book."),
    'DERMAGA': (
        "Tiang-tiang dermaga berdiri berderet seperti barisan penjaga. Air di bawahnya beralih warna dari hijau ke biru tua.",
        "Tali tambat berderit setiap ombak datang. Burung camar hinggap di tong kayu, lalu terbang lagi.",
        ("Dulu aku pikir dermaga cuma tempat orang pergi. Ternyata juga tempat orang menunggu.", 'serius'),
        ("Dan tempat orang pulang. Jangan lupa bagian itu.", 'senyum'),
        "Pemandangan ujung dermaga tersimpan di Memory Book."),
    'HUTAN_BISIK': (
        "Teras batu di lereng hutan ditumbuhi lumut. Dari atas, sungai kecil terlihat berkelok di antara batang-batang pinus.",
        "Daun-daun berbisik ditiup angin. Untuk sesaat, kalian sama-sama diam supaya tidak memotong suaranya.",
        ("Kalau aku tersesat di hutan ini, aku cukup ikuti suara sungai, kan?", 'penasaran'),
        ("Atau ikuti suaraku. Aku pasti manggil namamu duluan.", 'senyum'),
        "Bisikan hutan dari teras batu tersimpan di Memory Book."),
    'BUKIT_BINTANG': (
        "Jalan setapak berpagar menanjak ke kubah observatorium. Bunga-bunga kecil di lereng berkilau seperti bintang yang jatuh terlalu rendah.",
        "Teleskop tua berputar sedikit tertiup angin. Langit di atas bukit sudah mulai berganti warna.",
        ("Aku coba hitung bintangnya, tapi selalu keliru di angka dua puluh.", 'tertawa'),
        ("Nggak apa-apa. Kita mulai lagi dari satu, bareng-bareng.", 'senyum'),
        "Langit dari puncak bukit tersimpan di Memory Book."),
    'JALAN_KOTA': (
        "Dari teras toko, jalan kota terlihat seperti sungai lampu. Mobil-mobil berhenti di lampu merah, lalu mengalir lagi.",
        "Suara bel sepeda dan obrolan pedagang naik sampai ke atas. Kota ini tidak pernah benar-benar diam.",
        ("Biasanya aku lewat jalan ini sambil lihat ponsel. Ternyata ramai sekali, ya.", 'kaget'),
        ("Makanya, sesekali angkat kepala. Siapa tahu ada yang melambai ke kamu.", 'senyum'),
        "Keramaian jalan kota dari teras tersimpan di Memory Book."),
    'PERUMAHAN': (
        "Dari teras halaman, atap-atap rumah tersusun rapi. Asap tipis keluar dari cerobong rumah ujung.",
        "Seseorang menyiram tanaman, sepeda anak-anak bersandar di pagar. Sore di perumahan berjalan pelan.",
        ("Rumah-rumah ini kelihatan biasa saja dari jalan. Dari atas, tiap atap punya cerita.", 'penasaran'),
        ("Termasuk rumah kita nanti. Atapnya warna apa, ya?", 'malu'),
        "Atap-atap perumahan saat sore tersimpan di Memory Book."),
    'PERPUSTAKAAN': (
        "Mezanin kayu berderit di bawah sepatu. Lampu-lampu baca hijau di bawah menyala seperti pulau kecil di lautan rak.",
        "Seseorang menutup buku pelan-pelan. Debu halus melayang di cahaya jendela.",
        ("Dari sini aku bisa lihat meja tempat kita pertama kali belajar bareng.", 'senyum'),
        ("Yang kamu malah ketiduran di atas buku sejarah itu?", 'tertawa'),
        "Pemandangan rak-rak perpustakaan dari mezanin tersimpan di Memory Book."),
    'CAFE': (
        "Panggung kecil di sudut kafe ternyata cukup tinggi untuk melihat semua meja. Aroma kopi naik bersama cahaya senja.",
        "Barista menyalakan lampu gantung satu per satu. Musik akustik pelan mengisi ruangan.",
        ("Meja dekat jendela itu selalu kosong pas kita datang. Kayak memang disisakan.", 'penasaran'),
        ("Mungkin memang disisakan. Aku pernah titip pesan ke Bu Melati.", 'malu'),
        "Senja di panggung kecil kafe tersimpan di Memory Book."),
    'TOKO_BUNGA': (
        "Dari panggung kayu di toko bunga, deretan pot terlihat seperti palet cat. Mawar, lili, dan aster bersandar satu sama lain.",
        "Bel pintu berbunyi. Seorang pembeli memilih seikat bunga kecil tanpa ragu.",
        ("Aku selalu bingung milih bunga. Semua kelihatan cocok.", 'bingung'),
        ("Pilih yang bikin kamu ingat sesuatu. Itu biasanya yang paling cocok.", 'senyum'),
        "Warna-warni toko bunga dari atas tersimpan di Memory Book."),
    'ARCADE': (
        "Dek lampu arcade berpendar ungu dan biru. Bunyi koin dan tombol bercampur seperti lagu yang belum selesai.",
        "Di bawah, dua anak bersorak karena skor baru. Mesin capit berkedip menunggu pemain berikutnya.",
        ("Dari atas, mesin capit itu kelihatan curang banget.", 'tertawa'),
        ("Ya sudah, nanti kita coba sekali lagi. Kalau kalah, kamu traktir minum.", 'senang'),
        "Lampu-lampu arcade dari dek atas tersimpan di Memory Book."),
    'GALERI_KOMUNITAS': (
        "Mezanin galeri menghadap dinding lukisan warga kota. Dari jarak ini, semua bingkai terlihat seperti satu mozaik besar.",
        "Pemandu galeri memadamkan satu lampu sorot, lalu menyalakan yang lain. Warna lukisan ikut berubah.",
        ("Kalau lukisan kita dipajang di sini, kamu mau gambar apa?", 'penasaran'),
        ("Dua orang di bangku taman. Nggak usah wajah, cukup bayangannya.", 'senyum'),
        "Mozaik lukisan warga dari mezanin tersimpan di Memory Book."),
    'GUA_KRISTAL': (
        "Tangga kristal memantulkan cahaya ke dinding gua. Kolam di bawah memantulkan semuanya kembali, dua kali lebih terang.",
        "Tetes air jatuh dari langit-langit dan berdenting di kristal. Gemanya berputar sebelum hilang.",
        ("Gua ini dingin, tapi warnanya bikin hangat.", 'kaget'),
        ("Seperti beberapa orang yang aku kenal. Kelihatannya pendiam, padahal hangat.", 'senyum'),
        "Cahaya kristal dari tangga gua tersimpan di Memory Book."),
    'MEMORY_GARDEN': (
        "Dari teras taman ingatan, lingkaran cahaya di tanah terlihat utuh. Jalan-jalan bercahaya bertemu di tengahnya.",
        "Kelopak bunga melayang tanpa angin. Setiap kelopak membawa kilasan kecil dari hari-hari yang sudah lewat.",
        ("Lingkaran itu kayak jam tanpa jarum.", 'penasaran'),
        ("Mungkin karena kenangan nggak perlu diukur waktunya.", 'senyum'),
        "Lingkaran cahaya taman ingatan tersimpan di Memory Book."),
    'RAIN_GARDEN': (
        "Pijakan batu basah oleh hujan. Dari atas, lima lentera taman berjajar seperti kalimat yang menunggu titik.",
        "Hujan mereda sebentar. Suara tetesnya berubah dari deras menjadi pelan, seperti orang yang menurunkan suara.",
        ("Waktu hujan begini, aku suka lupa mau bilang apa.", 'malu'),
        ("Nggak apa-apa. Aku tunggu sampai kamu ingat lagi.", 'senyum'),
        "Taman hujan dari pijakan atas tersimpan di Memory Book."),
    'LANTERN_FIELD': (
        "Dari teras, ladang lentera terlihat seperti langit yang dibalik. Lingkaran cahaya di tengah berdenyut pelan.",
        "Satu lentera terlepas dan naik perlahan. Lentera lain seperti mengangguk mengantarnya.",
        ("Lentera yang terbang itu mau ke mana, ya?", 'penasaran'),
        ("Ke tempat orang yang menunggunya. Semoga sampai.", 'senyum'),
        "Ladang lentera dari teras tersimpan di Memory Book."),
    'STARFALL_VILLAGE': (
        "Dari atap cahaya, pondok-pondok bintang terlihat berderet mengelilingi alun-alun. Jalan desa berkilau seperti debu bintang.",
        "Seseorang di desa menyalakan lampu gantung. Satu per satu, rumah lain ikut menyala.",
        ("Desa ini kecil, tapi rasanya semua orang saling kenal.", 'senyum'),
        ("Kayak kita. Dunianya kecil, tapi penuh.", 'malu'),
        "Lampu-lampu desa bintang jatuh tersimpan di Memory Book."),
    'STAR_PATH': (
        "Dari pijakan tinggi, jalur bintang terlihat berkelok seperti tanda tangan di langit. Kristal di tepinya berdenyut bergantian.",
        "Satu bintang lewat di atas kepala, cukup dekat untuk mendengar desisnya.",
        ("Jalannya zigzag begini, pasti yang bikin suka belok mendadak.", 'tertawa'),
        ("Persis kamu kalau lagi cari jalan pintas.", 'tertawa'),
        "Jalur bintang dari pijakan atas tersimpan di Memory Book."),
    'HALL_OF_TOMORROW': (
        "Dari balkon balai, tiga jendela besar memperlihatkan tiga langit yang berbeda. Lantainya memantulkan ketiganya sekaligus.",
        "Jam besar di dinding berdetak sekali, lalu diam. Rasanya waktu memberi kalian jeda.",
        ("Tiga masa depan, dan aku cuma kepikiran satu hal: kamu ada di semuanya.", 'jatuh_cinta'),
        ("Kalau begitu, apa pun jendelanya, kita lihat bareng.", 'malu'),
        "Tiga jendela dari balkon balai tersimpan di Memory Book."),
    'ETERNAL_GARDEN': (
        "Dari pelataran, jalan sakura membentang sampai pohon harapan. Kolam pantul di bawahnya menyimpan langit sore.",
        "Kelopak sakura jatuh ke kolam dan berputar pelan. Gazebo di ujung taman terlihat seperti menunggu tamu.",
        ("Taman ini rasanya bukan akhir. Lebih kayak halaman pertama.", 'serius'),
        ("Kalau begitu, kita tulis halaman berikutnya pelan-pelan.", 'senyum'),
        "Taman abadi dari pelataran tersimpan di Memory Book."),
}

DISC_CLOSE = {
    'ARLAND_ROOM': "Kertas itu dilipat lagi dan diselipkan ke halaman Memory Book, di antara catatan-catatan kecil lainnya.",
    'SOFIA_ROOM': "Benda kecil itu kembali ke tempatnya, tetapi ceritanya kini ikut tersimpan di Memory Book.",
    'PLAZA': "Suara air mancur menutup momen itu. Satu jejak kecil plaza masuk ke Memory Book.",
    'JALAN_KOTA': "Keramaian jalan kembali terdengar. Jejak kecil itu kini tercatat di Memory Book.",
    'PERUMAHAN': "Lampu teras tetangga menyala. Jejak kecil dari perumahan tersimpan di Memory Book.",
    'TAMAN_KOTA': "Seekor koi muncul ke permukaan, seolah ikut menyaksikan. Jejak itu tersimpan di Memory Book.",
    'RIVERSIDE': "Riak danau menyapu tepi pasir. Jejak kecil dari tepi danau tersimpan di Memory Book.",
    'DERMAGA': "Tali tambat berderit sekali lagi. Jejak kecil dari dermaga tersimpan di Memory Book.",
    'HUTAN_BISIK': "Daun-daun berbisik lagi, kali ini terdengar seperti setuju. Jejak itu tersimpan di Memory Book.",
    'BUKIT_BINTANG': "Teleskop berderit pelan tertiup angin. Jejak kecil dari bukit tersimpan di Memory Book.",
    'PERPUSTAKAAN': "Halaman buku dibalik di meja sebelah. Jejak kecil dari perpustakaan tersimpan di Memory Book.",
    'RUANG_ARSIP': "Map arsip ditutup rapat. Jejak kecil dari ruang arsip tersimpan di Memory Book.",
    'CAFE': "Mesin kopi mendesis di belakang meja. Jejak kecil dari kafe tersimpan di Memory Book.",
    'DAPUR': "Aroma masakan masih tertinggal. Jejak kecil dari dapur tersimpan di Memory Book.",
    'TOKO_BUNGA': "Bel pintu berbunyi pelan. Jejak kecil dari toko bunga tersimpan di Memory Book.",
    'ARCADE': "Mesin arcade berkedip seperti memberi tanda setuju. Jejak kecil itu tersimpan di Memory Book.",
    'GALERI_KOMUNITAS': "Lampu sorot galeri berpindah ke bingkai lain. Jejak kecil itu tersimpan di Memory Book.",
    'RUANG_DUA_SURAT': "Dua amplop di meja seakan bergeser lebih dekat. Jejak kecil itu tersimpan di Memory Book.",
    'GUA_KRISTAL': "Kristal berdenting sekali, lalu sunyi. Jejak kecil dari gua tersimpan di Memory Book.",
    'MEMORY_GARDEN': "Kelopak cahaya melayang ke halaman Memory Book dan berhenti di sana.",
    'RAIN_GARDEN': "Hujan turun sedikit lebih pelan. Jejak kecil dari taman hujan tersimpan di Memory Book.",
    'LANTERN_FIELD': "Satu lentera menyala lebih terang sebentar. Jejak kecil itu tersimpan di Memory Book.",
    'CLOCKWORK_STATION': "Roda gigi berputar satu kali lagi. Jejak kecil dari stasiun jam tersimpan di Memory Book.",
    'MOONLIGHT_LAKE': "Bulan di permukaan danau bergoyang lalu tenang. Jejak kecil itu tersimpan di Memory Book.",
    'MEMORY_BRIDGE': "Papan jembatan bercahaya di bawah langkah kalian. Jejak kecil itu tersimpan di Memory Book.",
    'STARFALL_VILLAGE': "Lampu desa berkelip bergantian. Jejak kecil dari desa bintang tersimpan di Memory Book.",
    'STAR_PATH': "Sebuah bintang jatuh di ujung jalur. Jejak kecil itu tersimpan di Memory Book.",
    'HALL_OF_TOMORROW': "Jam besar di balai berdetak sekali. Jejak kecil itu tersimpan di Memory Book.",
    'ETERNAL_GARDEN': "Kelopak sakura jatuh di atas halaman Memory Book, menandai jejak kecil itu.",
}
