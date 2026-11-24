# Arland & Sofia v4.0 — Sembilan Map, Collision dan Koordinat

Seluruh koordinat dalam **piksel gambar dengan titik (0,0) di kiri atas; X ke kanan, Y ke bawah**.
Semua gambar runtime berukuran **1200 × 896 px**, memakai filter **Nearest** dari `Assets.java`.
Kolom `rect` menggunakan urutan `[x, y, width, height]`. Radius trigger menggunakan piksel.
Untuk data lengkap machine-readable (termasuk seluruh 9 matriks obstacle): `docs/MAPS_V4_MAPPING.json` dan `android/assets/data/maps.json`.

## Penting: pemetaan nama gambar unggahan

Berkas ZIP pengguna bernama tidak sesuai dengan isi visualnya. Gambar dipetakan berdasarkan isi yang diperiksa, tanpa memakai `01_jalan_kota.png` yang berupa collage perbandingan.

| ID map game | Nama asal di ZIP | File runtime |
|---|---|---|
| `jalan_kota` | `04_arcade.png` | `android/assets/maps/jalan_kota.png` |
| `perumahan` | `03_perpustakaan.png` | `android/assets/maps/perumahan.png` |
| `perpustakaan` | `08_dapur.png` | `android/assets/maps/perpustakaan.png` |
| `arcade` | `09_ruang_arsip.png` | `android/assets/maps/arcade.png` |
| `toko_bunga` | `02_perumahan.png` | `android/assets/maps/toko_bunga.png` |
| `arland_room` | `10_extra_map.png` | `android/assets/maps/arland_room.png` |
| `sofia_room` | `05_toko_bunga.png` | `android/assets/maps/sofia_room.png` |
| `dapur` | `07_sofia_room.png` | `android/assets/maps/dapur.png` |
| `ruang_arsip` | `06_arland_room.png` | `android/assets/maps/ruang_arsip.png` |

## Spawn, portal dan interaction zones

Legenda: `spawnPoint` adalah titik kaki pemain; `arrival` adalah titik kaki setelah pindah map. **Jangan** tempatkan arrival di dalam portal lain.

### Jalan Kota — `jalan_kota`

- Resolusi: **1200 × 896**
- SpawnPoint: **(604, 559)**
- Collision: **12 rectangle/alcove mask**, 1 foreground Y-sort overlay dengan collision terpisah.

**Portals**

| ID portal | Trigger rect | Tujuan map | Arrival (X,Y) |
|---|---|---|---|
| `street_to_res` | `[1159, 465, 41, 100]` | `perumahan` | **(65, 517)** |
| `street_to_plaza` | `[0, 465, 42, 100]` | `plaza` | **(1870, 705)** |
| `door_florist` | `[225, 309, 72, 45]` | `toko_bunga` | **(601, 774)** |
| `door_arcade` | `[905, 307, 82, 48]` | `arcade` | **(600, 776)** |

**Interaction zones — investigasi dan cerita utama**

| Trigger ID | Pusat (X,Y) | Radius | Keterangan |
|---|---|---|---|
| `examine:bakery` | (495, 355) | 56 | Toko Roti Hangat |
| `examine:vending` | (757, 345) | 56 | Mesin minuman |

**NPC dan side/event**: 1 NPC lokasi, 16 interaksi opsional. Koordinat lengkapnya ada di `android/assets/data/quests.json`.

### Distrik Perumahan — `perumahan`

- Resolusi: **1200 × 896**
- SpawnPoint: **(65, 525)**
- Collision: **7 rectangle/alcove mask**, 1 foreground Y-sort overlay dengan collision terpisah.

**Portals**

| ID portal | Trigger rect | Tujuan map | Arrival (X,Y) |
|---|---|---|---|
| `res_to_street` | `[0, 475, 36, 87]` | `jalan_kota` | **(354, 489)** |
| `door_library` | `[640, 304, 76, 40]` | `perpustakaan` | **(601, 780)** |

**Interaction zones — investigasi dan cerita utama**

| Trigger ID | Pusat (X,Y) | Radius | Keterangan |
|---|---|---|---|
| `examine:res_garden` | (220, 553) | 56 | Kebun warga |
| `examine:res_house_c` | (205, 548) | 56 | Rumah merah muda |
| `examine:res_bench` | (728, 554) | 56 | Bangku halte |
| `halte` | (727, 546) | 70 | `C04_A_HALTE` — Berteduh di halte |
| `mbox` | (690, 543) | 56 | `C04_A_MAILBOX` — Kotak surat tua |
| `q_a_reply` | (727, 546) | 72 | `C04_Q_A_REPLY` — Dengarkan hujan |

**NPC dan side/event**: 1 NPC lokasi, 5 interaksi opsional. Koordinat lengkapnya ada di `android/assets/data/quests.json`.

### Perpustakaan Kota — `perpustakaan`

- Resolusi: **1200 × 896**
- SpawnPoint: **(602, 789)**
- Collision: **19 rectangle/alcove mask**, 1 foreground Y-sort overlay dengan collision terpisah.

**Portals**

| ID portal | Trigger rect | Tujuan map | Arrival (X,Y) |
|---|---|---|---|
| `perpustakaan_out` | `[545, 816, 110, 70]` | `perumahan` | **(676, 370)** |
| `lib_to_archive` | `[1071, 335, 66, 90]` | `ruang_arsip` | **(594, 782)** |

**Interaction zones — investigasi dan cerita utama**

| Trigger ID | Pusat (X,Y) | Radius | Keterangan |
|---|---|---|---|
| `examine:lib_globe` | (161, 290) | 56 | Bola dunia |
| `examine:lib_sofa` | (154, 365) | 56 | Sofa baca |
| `examine:lib_clock` | (586, 393) | 56 | Jam dinding |
| `examine:lib_shelf_w` | (395, 370) | 56 | Rak sejarah kota |
| `laras1` | (615, 388) | 66 | `C01_LARAS` — Bicara dengan Bu Laras |
| `libbook1` | (720, 593) | 56 | `C01_BOOKS` — Ensiklopedia bunga |
| `libbook2` | (737, 366) | 56 | `C01_BOOKS` — Buku tentang buku |
| `libbook3` | (1091, 570) | 56 | `C01_BOOKS` — Peta langit malam |
| `libtable` | (346, 485) | 60 | `C01_TABLE` — Meja baca |
| `laras2` | (615, 388) | 66 | `C01_LARAS2` — Bicara dengan Bu Laras |
| `laras4` | (615, 388) | 66 | `C04_S_LIBRARY` — Bicara dengan Bu Laras |
| `read4` | (330, 692) | 60 | `C04_S_READ` — Baca surat di sofa |
| `q_s_reply` | (330, 692) | 70 | `C04_Q_S_REPLY` — Tulis di kertas |

**NPC dan side/event**: 1 NPC lokasi, 6 interaksi opsional. Koordinat lengkapnya ada di `android/assets/data/quests.json`.

### Arcade Bintang — `arcade`

- Resolusi: **1200 × 896**
- SpawnPoint: **(595, 751)**
- Collision: **20 rectangle/alcove mask**, 1 foreground Y-sort overlay dengan collision terpisah.

**Portals**

| ID portal | Trigger rect | Tujuan map | Arrival (X,Y) |
|---|---|---|---|
| `arcade_out` | `[545, 819, 110, 66]` | `jalan_kota` | **(900, 382)** |

**Interaction zones — investigasi dan cerita utama**

| Trigger ID | Pusat (X,Y) | Radius | Keterangan |
|---|---|---|---|
| `examine:cabinet_e` | (307, 246) | 56 | Mesin game |
| `f2_juna` | (700, 737) | 70 | `C02_FREE` — Bicara dengan Bang Juna |
| `juna_print` | (700, 737) | 70 | `C02_S_PRINT` — Bicara dengan Bang Juna |
| `booth` | (522, 391) | 64 | `C02_DATE` — Photobooth |
| `frame` | (707, 738) | 70 | `C03_S_DECOR` — Minta bingkai |

**NPC dan side/event**: 1 NPC lokasi, 3 interaksi opsional. Koordinat lengkapnya ada di `android/assets/data/quests.json`.

### Toko Bunga Melati — `toko_bunga`

- Resolusi: **1200 × 896**
- SpawnPoint: **(612, 776)**
- Collision: **17 rectangle/alcove mask**, 1 foreground Y-sort overlay dengan collision terpisah.

**Portals**

| ID portal | Trigger rect | Tujuan map | Arrival (X,Y) |
|---|---|---|---|
| `toko_bunga_out` | `[546, 817, 120, 70]` | `jalan_kota` | **(260, 386)** |

**Interaction zones — investigasi dan cerita utama**

| Trigger ID | Pusat (X,Y) | Radius | Keterangan |
|---|---|---|---|
| `examine:shelf_w_e` | (272, 410) | 56 | Rak bunga |
| `florist` | (828, 460) | 70 | `C02_A_FLORIST` — Bicara dengan Bu Melati |
| `dried` | (671, 352) | 70 | `C03_S_DECOR` — Minta bunga kering |
| `f5_melati` | (828, 460) | 70 | `C05_FREE` — Bicara dengan Bu Melati |
| `f5_melati_done` | (828, 460) | 70 | `C05_FREE` — Lapor ke Bu Melati |

**NPC dan side/event**: 1 NPC lokasi, 8 interaksi opsional. Koordinat lengkapnya ada di `android/assets/data/quests.json`.

### Kamar Arland — `arland_room`

- Resolusi: **1200 × 896**
- SpawnPoint: **(620, 762)**
- Collision: **17 rectangle/alcove mask**, 1 foreground Y-sort overlay dengan collision terpisah.

**Portals**

| ID portal | Trigger rect | Tujuan map | Arrival (X,Y) |
|---|---|---|---|
| `arland_room_out` | `[552, 819, 105, 68]` | `plaza` | **(360, 460)** |

**Interaction zones — investigasi dan cerita utama**

| Trigger ID | Pusat (X,Y) | Radius | Keterangan |
|---|---|---|---|
| `examine:a_window` | (400, 250) | 56 | Jendela |
| `examine:a_clock` | (620, 357) | 56 | Jam dinding |
| `examine:a_poster` | (515, 290) | 56 | Poster |
| `examine:a_frame` | (908, 379) | 56 | Foto pemandangan |
| `phone` | (721, 398) | 64 | `PRO_PHONE` — Lihat ponsel |
| `gift` | (514, 376) | 64 | `PRO_GIFT` — Bunga kertas |
| `note` | (206, 489) | 64 | `C01_NOTE` — Rak buku |
| `phone2` | (721, 398) | 64 | `C02_PHONE` — Lihat ponsel |
| `idea` | (711, 388) | 64 | `C03_A_IDEA` — Meja kerja |
| `phone4` | (721, 398) | 64 | `C04_A_WAKE` — Ponsel |
| `phone5` | (721, 398) | 64 | `C05_A_START` — Ponsel |

**NPC dan side/event**: 0 NPC lokasi, 0 interaksi opsional. Koordinat lengkapnya ada di `android/assets/data/quests.json`.

### Kamar Sofia — `sofia_room`

- Resolusi: **1200 × 896**
- SpawnPoint: **(609, 783)**
- Collision: **16 rectangle/alcove mask**, 1 foreground Y-sort overlay dengan collision terpisah.

**Portals**

| ID portal | Trigger rect | Tujuan map | Arrival (X,Y) |
|---|---|---|---|
| `sofia_room_out` | `[548, 819, 104, 70]` | `plaza` | **(960, 460)** |

**Interaction zones — investigasi dan cerita utama**

| Trigger ID | Pusat (X,Y) | Radius | Keterangan |
|---|---|---|---|
| `examine:s_window` | (834, 241) | 56 | Jendela |
| `examine:s_vanity` | (737, 372) | 56 | Meja rias |
| `examine:s_sofa` | (392, 682) | 56 | Sofa |
| `examine:s_frame` | (710, 290) | 56 | Foto |
| `phone` | (701, 386) | 64 | `PRO_PHONE` — Lihat ponsel |
| `gift` | (713, 384) | 64 | `PRO_GIFT` — Kartu pos |
| `note` | (339, 500) | 64 | `C01_NOTE` — Rak buku |
| `phone2` | (701, 386) | 64 | `C02_PHONE` — Ambil ponsel |
| `wardrobe` | (883, 695) | 64 | `C02_S_OUTFIT` — Lemari pakaian |
| `corner` | (505, 686) | 64 | `C03_S_CORNER` — Kotak kenangan |
| `arrange` | (505, 686) | 64 | `C03_S_ARRANGE` — Tata sudut kenangan |
| `phone4` | (701, 386) | 64 | `C04_S_WAKE` — Ponsel |
| `book5` | (505, 691) | 64 | `C05_S_START` — Memory Book |

**NPC dan side/event**: 0 NPC lokasi, 0 interaksi opsional. Koordinat lengkapnya ada di `android/assets/data/quests.json`.

### Dapur Kafe — `dapur`

- Resolusi: **1200 × 896**
- SpawnPoint: **(592, 770)**
- Collision: **16 rectangle/alcove mask**, 1 foreground Y-sort overlay dengan collision terpisah.

**Portals**

| ID portal | Trigger rect | Tujuan map | Arrival (X,Y) |
|---|---|---|---|
| `dapur_out` | `[540, 819, 122, 70]` | `cafe` | **(860, 280)** |

**Interaction zones — investigasi dan cerita utama**

| Trigger ID | Pusat (X,Y) | Radius | Keterangan |
|---|---|---|---|
| `examine:fridge_e` | (808, 388) | 56 | Kulkas |
| `fridge` | (820, 390) | 64 | `C03_A_INGREDIENTS` — Ambil stroberi |
| `stove` | (385, 380) | 64 | `C03_COOK` — Masak bersama |
| `v26_c03_recipe` | (385, 380) | 66 | `C03_V26_DETAILS` — Catatan di balik resep |
| `v26_c03_packing` | (385, 390) | 66 | `C03_V26_DETAILS` — Bungkus bekal berdua |

**NPC dan side/event**: 0 NPC lokasi, 5 interaksi opsional. Koordinat lengkapnya ada di `android/assets/data/quests.json`.

### Ruang Arsip Rahasia — `ruang_arsip`

- Resolusi: **1200 × 896**
- SpawnPoint: **(585, 756)**
- Collision: **18 rectangle/alcove mask**, 1 foreground Y-sort overlay dengan collision terpisah.

**Portals**

| ID portal | Trigger rect | Tujuan map | Arrival (X,Y) |
|---|---|---|---|
| `ruang_arsip_out` | `[542, 823, 114, 66]` | `perpustakaan` | **(1093, 462)** |

**Interaction zones — investigasi dan cerita utama**

| Trigger ID | Pusat (X,Y) | Radius | Keterangan |
|---|---|---|---|
| `examine:arc_jars` | (450, 385) | 56 | Stoples bercahaya |
| `examine:arc_jars_e` | (744, 378) | 56 | Stoples tanpa label |
| `pedestal` | (619, 566) | 60 | `C01_PEDESTAL` — Catatan di tiang batu |
| `q_a_map` | (420, 377) | 66 | `C01_Q_A_MAP` — Denah Pak Wira |
| `q_s_margin` | (741, 380) | 66 | `C01_Q_S_MARGIN` — Catatan pinggir |

**NPC dan side/event**: 0 NPC lokasi, 0 interaksi opsional. Koordinat lengkapnya ada di `android/assets/data/quests.json`.

## Kompatibilitas dan batasan

- Seluruh ID `door`, `quest`, `step`, `scene`, dan item dipertahankan.
- Objek furniture sudah tergambar di PNG; sprite prop lama disembunyikan pada sembilan area agar tidak menumpuk. Foreground object tertentu digunakan kembali sebagai overlay Y-sort tanpa hitbox ganda.
- Obstacle adalah matriks geometri yang ditentukan berdasarkan objek pada gambar, menggunakan rectangle majemuk untuk lekukan/alcove. Ini bukan collider pixel-perfect per piksel.
- Titik quest umum yang berada dalam obstacle dipindahkan ke posisi berdiri terdekat. Titik utama (buku, meja, komputer, kasir, dapur, papan investigasi) diberi anchor manual.
- Save schema 8 menambah `mapLayoutVersion=4` untuk migrasi posisi dari v3.x. Item, cerita, dan pilihan tetap tersimpan; posisi pada obstacle disnap ke titik legal saat resume.
- Build Android aktual dan visual runtime perlu diuji di perangkat. Tes headless tidak menguji kualitas perspektif, clipping pixel art, maupun gesture sentuh sebenarnya.

## Cara mengedit dan membangun ulang

1. Edit `art_source/maps_v4_input/<id>.png` untuk artwork (1200×896). Baseline v3.7 tersedia di `art_source/maps_v37_baseline/`.
2. Edit `GEOMETRY`, `POIS`, `TRIGGERS`, dan `FOREGROUND` dalam `tools/maps_v4_upgrade.py`.
3. Untuk regenerasi penuh jalankan `bash tools/build_all.sh`; script memasang layout v4 setelah generator map & konten lama selesai.
4. Jalankan `python3 tools/check_layout.py android/assets`, `python3 tools/test_maps_v4.py`, `bash tools/test_maps_v4_save.sh`, dan `bash tools/test_logic.sh`.
5. Build APK melalui Gradle/Android SDK pada mesin dengan dependensi tersedia. Jangan mengklaim APK lulus berdasarkan tes headless.
