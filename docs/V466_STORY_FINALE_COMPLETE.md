# Arland & Sofia — v4.6.6 Story Overhaul 3.2

## Tujuan rilis

Melengkapi Story Overhaul 3.1 tanpa mengganti secara sembrono sistem save, area, scene canon, atau cerita lain. Cerita tetap **dua route, satu ending bahagia**. Semua adegan dan situasi merupakan fiksi, bukan klaim kejadian nyata.

## Fitur yang sudah masuk ke gameplay

1. **Chapter 6 — surat/halaman pilihan Arland.** Pemain memilih satu dari tiga sikap: hadir, mendengarkan, atau belajar bersama. Setiap pilihan ditulis sebagai flag pada save route Arland, dan membuka dialog khusus.
2. **Chapter 6 — catatan pilihan Sofia.** Pemain memilih satu dari tiga sikap: berani mengutarakan kebutuhan, memberi ruang, atau menghargai keberanian diri. Dialog, flags dan isi surat berbeda dari route Arland.
3. **Chapter 6 — dua surat, satu halaman kosong.** Adegan tambahan diletakkan *sebelum* adegan canon `C06-X01` dan `C06-X03`. Ending utama tidak dihapus atau diduplikasi.
4. **Epilog reaktif.** Enam coda kecil mengingat pilihan personal di Chapter 6. Alur lama dari Festival Lentera dan adegan danau tetap dimainkan.
5. **Kompatibilitas old save.** Pemain yang sudah sampai Epilog lewat versi lebih lama dan tidak mempunyai flag surat v4.6.6 mendapatkan adegan refleksi yang aman dan tetap dapat menyelesaikan epilog.
6. **Galeri pascakredit yang dapat dimainkan.** Pada step `EPI_FREE`, tersedia hotspot sekali jalan di Galeri Komunitas untuk Arland maupun Sofia. Kegiatan ini memicu percakapan baru serta menambah satu memori; repeat-farming dicegah dengan flag.
7. **Memory Book.** Tiga entri baru: Surat di Balik Bunga (Arland), Catatan di Samping Kursi (Sofia), dan Hari ketika Mereka Kembali (epilog bersama). Ikon pixel-art disimpan sebagai PNG terpisah dan dapat diganti.
8. **Musik orisinal 28,8 detik.** `cinema_letter_tomorrow.ogg` dipicu pada epilog dan benar-benar diregistrasi di `SoundscapePlan` agar audio engine mengenali ID-nya.

## Fitur v4.6.5 yang dipertahankan

- Prolog–Chapter 6–Epilog, 23 area termasuk Galeri Komunitas, seluruh quest lama, The Quiet, misi personal dua route.
- Konflik The Empty Seat, penundaan rekonsiliasi, aksi pembuktian bersama di Chapter 5, dan pilihan kencan yang diingat di ending.
- Sistem save `Progress.SCHEMA=8` dan `SaveStore`, NPC, romance, cinematic/UI, 22 area original, audio dan aset visual versi sebelumnya.
- Tidak ada penghapusan paksa file save pada perangkat. Untuk merasakan ulang semua pilihan, mulai **New Game** di slot baru.

## Pengembangan dan regenerasi data

- `python3 tools/apply_story_finale_v466.py`: patch cerita idempotent, jalankan sesudah `apply_story_completion_v465.py`.
- `python3 tools/gen_story_assets_v466.py`: regenerasi tiga ikon kenangan pixel-art orisinal.
- `python3 tools/gen_story_audio_v466.py`: regenerasi musik instrumental orisinal (butuh NumPy dan FFmpeg untuk *authoring*; game Android tidak membutuhkan keduanya).
- `bash tools/test_story_finale_v466.sh`: tes Java headless + validator JSON/PNG/OGG.
- `bash tools/test_story_complete_v465.sh`: kompatibilitas semua percabangan v4.6.4–v4.6.5.
- `bash tools/build_all.sh`: menjalankan seluruh generator dan versi QA terkini. Backup data yang diedit manual sebelum menjalankan generator penuh.

## Verifikasi dan keterbatasan

Verifikasi cerita menguji flags, pilihan, scene-route, quest, kembali ke galeri, mencegah replay, save roundtrip, old-save fallback, dan konsistensi `story.json` / `quests.json` / `memory_book.json`. Generator v4.6.6 dicek menghasilkan hasil yang sama ketika dipanggil berulang kali. Pengujian regresi yang lain ada di `tools/release_qa_v465.sh`.

**Belum bisa dinyatakan 100% siap rilis** tanpa build `:android:assembleDebug` / `assembleRelease`, pengujian gerak/animasi/audio Android di perangkat nyata, dan playthrough dua route dari awal sampai epilog. Tes Java headless bukan pengganti verifikasi APK.
