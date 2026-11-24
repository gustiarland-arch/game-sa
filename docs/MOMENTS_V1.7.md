# Sistem Momen Harian — v1.7.0

**Game:** Arland & Sofia: Our Little Universe (Android native LibGDX, Java 11, offline).

## Tujuan

Memperkaya interaksi Arland dan Sofia di sela cerita utama. Aktivitas momen harian tersedia **mulai Chapter 2**, bila companion aktif dan pemain berada dekat pasangannya. Sistem tidak menambah route/ending baru, tidak memerlukan izin internet, dan tidak menggunakan pembayaran sungguhan.

## Cara memainkan

1. Ajak pasangan mengikuti pemain (companion) setelah Chapter 2.
2. Dekati pasangan sampai aksi **♥ Waktu Berdua** muncul. Bila ada percakapan opsional yang belum dibuka, selesaikan terlebih dahulu.
3. Buka tab **Momen Harian**, lihat syarat tiap kegiatan. Aktivitas tersedia hanya pada area dan rentang jam yang benar; aktivitas tertentu membutuhkan cuaca atau tingkat kedekatan tertentu.
4. Pilih **Lakukan**. Momen gratis, membuka dialog serta animasi efek hati, menambah kedekatan 3–8 poin, dan mencatat pertama kali ke Memory Book. **Hanya satu momen di seluruh katalog per hari game**. Tidur/ganti hari untuk kesempatan baru.

## Katalog momen

| ID | Judul | Area | Jam | Cuaca | Minimum hati | Hadiah hati |
|---|---|---|---|---|---:|---:|
| `pagi_kafe` | Cerita Sebelum Sibuk | Kafe Senja | 07:00–11:00 | Apa pun | 0 | +3 |
| `genggam_tangan` | Berjalan Sambil Bergandengan | Plaza Kota | 09:00–19:00 | Apa pun | 10 | +4 |
| `kucing_taman` | Mengamati Kucing Taman | Taman Kota | 09:00–17:00 | Cerah / berawan | 0 | +4 |
| `berteduh` | Berteduh Saat Hujan | Kafe Senja | 10:00–21:00 | Hujan | 5 | +6 |
| `halaman_kecil` | Membaca Bergantian | Perpustakaan | 10:00–18:00 | Apa pun | 20 | +5 |
| `senja_danau` | Diam Menikmati Senja | Tepi Danau | 16:00–19:00 | Apa pun | 15 | +5 |
| `hati_ke_hati` | Saling Mendengarkan | Tepi Danau | 19:00–24:00 | Apa pun | 40 | +7 |
| `malam_hening` | Janji Kecil di Bukit | Bukit Bintang | 19:00–01:00* | Cerah / berawan | 60 | +8 |

*Waktu akhir 01:00 adalah 25:00 menurut jam dunia: sesudah tengah malam pada hari game yang sama.*

Setiap judul mempunyai dua dialog: satu saat memainkan route Arland dan satu saat memainkan route Sofia. Seluruhnya adalah **adegan fiksi**. Kencan berbayar dan hadiah tetap merupakan aktivitas terpisah dari momen gratis.

## Arsitektur

- Sumber katalog: `tools/content/romance.py` → `ROMANCE['moments']`. Sumber adegan: `tools/content/naskah_moments.txt`.
- Generator: `python3 -I tools/build_content.py` → `android/assets/data/quests.json`, `story.json`, `memory_book.json`. Jangan edit JSON output manual.
- Java: `QuestDb.MomentActivity` (parsing), `QuestEngine.momentBlock/startMoment/momentActions` (logika murni), `RomanceOverlay` (tab ketiga). `GameScreen` tetap memakai callback overlay lama dan otomatis `saveNow()` sebelum menampilkan adegan.
- Save: `Progress.SCHEMA = 4`. `lastMomentDay = -1` untuk pemain yang belum melakukan momen; `momentCounts` untuk jumlah per jenis momen. Save lama schema 1/2/3 dimigrasi. Data game dari slot lain tidak bercampur.
- Kenangan: 8 untuk momen pertama kali plus 1 untuk milestone kedekatan 80. Flag milestone hanya dibuka sekali dan scene milestone memiliki flag `ROM_BOND_80_SCENE` sesudah ditampilkan.

## Validasi dan keterbatasan

| Pengujian yang benar-benar dijalankan | Hasil |
|---|---|
| `bash tools/test_logic.sh` — generator, layout, Java headless | **Lulus: 22.069 pemeriksaan**, kedua route menamatkan cerita, 17 side quest, 8 momen, 3 kencan, 3 hadiah, milestone 20/50/80 |
| `bash tools/test_romance_ui.sh` — klik tombol menggunakan stub UI | **Lulus**: tab ketiga, momen gratis, pembatasan sehari, hari berikutnya, hadiah, kencan |
| `./gradlew :core:test :android:assembleDebug --stacktrace` | **Gagal sebelum kompilasi**: `UnknownHostException: services.gradle.org` saat mengunduh Gradle 8.11.1. Build/QA HP belum dapat diverifikasi. |

Target 6 jam cerita per route belum tercapai; momen harian sifatnya opsional dan dapat diulang, bukan penambah alur utama. Tidak ada klaim performa HP hingga APK dibangun dan diuji secara nyata.
