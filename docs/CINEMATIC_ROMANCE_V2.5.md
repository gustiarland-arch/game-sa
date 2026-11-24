# v2.5.0 — Cinematic Romance & Immersive Gameplay

## Apa yang benar-benar baru

v2.5 memperluas **source v2.4**, bukan proyek lain. Cerita canon Arland/Sofia, ending, area, collision, cutscene lama, game lama, ekonomi, toko, dan save yang sudah dipakai tetap dipertahankan.

### Enam permainan di Waktu Berdua → Main Bareng

| Kegiatan | Lokasi | Tipe gameplay | Status |
|---|---|---|---|
| Memancing berdua | Riverside, dermaga | `fishing` | Dibuka ulang dari minigame lama |
| Resep berdua | Kafe, dapur | `cooking` | Dibuka ulang dari minigame lama |
| Merangkai buket | Toko bunga | `bouquet` | **Baru**: putar jenis bunga pada empat batang sampai sesuai pesanan |
| Album cerita kita | Kafe, perpustakaan, kamar | `scrapbook` | **Baru**: pilih dua kartu untuk menukar urutan kronologis |
| Tangkap bintang | Bukit Bintang, Star Path | `starcatch` | Dibuka ulang dari minigame lama |
| Photobooth berdua | Arcade | `photobooth` | Dibuka ulang dari minigame lama |

Semua aktivitas tersedia sesudah pasangan menjadi companion dan fitur Waktu Berdua terbuka (setelah Chapter 2). Masing-masing kegiatan memiliki adegan penyelesaian khusus route Arland/Sofia (total 12 adegan), skor terakhir dan terbaik, bonus kedekatan **hanya saat skor memenuhi syarat dan sekali per kegiatan per hari**, serta flag Memory Book pada keberhasilan pertama. Setelah mengambil bonus harian, pemain tetap dapat mengulangi permainan untuk memperbaiki skor. Pembatalan atau kegagalan tidak menghadiahkan kedekatan.

**Kompatibilitas:** progress tetap memakai **schema save 5**. Rekor dan pengunci harian disimpan di map `Progress.counters`; tidak menimpa kunci save lama. Jangan menganggap file save dari versi baru akan selalu bisa dibaca versi lebih tua; backup sebelum pembaruan APK.

Source gameplay: `core/src/main/java/com/arlandsofia/olu/game/minigame/Games.java`, `core/src/main/java/com/arlandsofia/olu/game/RomanceOverlay.java`, `core/src/main/java/com/arlandsofia/olu/logic/{QuestEngine,ActionRunner,QuestDb}.java`. Katalog untuk diedit: `tools/content/romance_games_v25.py`, dialog: `tools/content/naskah_romgames_v25.txt`. Regenerasi data: `python3 -I tools/build_content.py`.

### Audio sinematik dan ekspresi

Tujuh komposisi orisinal yang dibuat menggunakan generator procedural lokal (manifest: `android/assets/audio/cinematic_v25.json`): `cinema_first_meet`, `cinema_memory_portal`, `cinema_rain_conflict`, `cinema_reconciliation`, `cinema_quiet`, `cinema_lantern_finale`, `cinema_our_tomorrow`. Musik dipicu dari tindakan cutscene/cerita yang cocok (pertemuan, portal, hujan, rekonsiliasi, The Quiet, Festival Lentera, dan kredit), bukan ditambahkan sebagai lagu acak yang menggantikan musik lokasi. Kanal audio dan crossfade v2.4 tetap digunakan.

Empat SFX WAV orisinal: `flower_pick`, `paper_fold`, `cinema_heartbeat`, `cinema_whoosh`; tiga ekspresi potret baru per karakter (`jatuh_cinta`, `khawatir`, `lega`) di `android/assets/characters/arland/portraits/` dan `characters/sofia/portraits/`. Ekspresi merupakan olahan pixel-art di atas potret asli yang telah ada, bukan artwork terpisah yang digambar tangan dari nol. Penggunaan di dialog dapat diedit lewat naskah, misalnya `sofia(jatuh_cinta): ...`.

Katalog total: **40 musik OGG (33 lama + 7 baru), 14 ambience OGG, 32 SFX WAV (28 lama + 4 baru) = 86 file audio**. Semua tersimpan **di satu ZIP source lengkap** `android/assets/audio/`, tidak perlu mengunduh paket audio lain. Musik dihasilkan lokal dan tanpa sampel lagu pihak lain.

### Mengganti dan meregenerasi

- Ganti file audio dengan ID/nama dan format yang sama di `android/assets/audio/music/` atau `audio/sfx/`, lalu build APK. OGG Vorbis untuk musik; PCM WAV untuk SFX.
- Ubah soundtrack/area/scene pada `tools/build_content.py` dan `core/src/main/java/com/arlandsofia/olu/logic/SoundscapePlan.java`.
- Regenerasi komposisi **baru saja**: `python3 tools/gen_cinema_audio_v25.py` (butuh numpy & ffmpeg). Regenerasi ekspresi dan SFX **baru saja**: `python3 tools/gen_cinema_fx_v25.py` (Pillow, numpy). **Jangan jalankan generator jika sudah mengganti file secara manual**, karena file dengan nama sama akan ditimpa.
- Semua generator: `bash tools/build_all.sh` (membuat ulang visual/peta/semua musik dan data; perlu Python Pillow, numpy, fontTools, ffmpeg). Backup perubahan aset manual sebelum menjalankannya.

### Pengujian dan batasan

- `bash tools/test_logic.sh`: simulasi progres kedua route, Memory Book, minigame, ekonomi, transaksi romantis, save lama, epilog.
- `bash tools/test_romance_ui.sh`: tab kelima + aksi minigame yang dipanggil dari UI.
- `bash tools/test_soundscape_plan.sh` + `bash tools/test_audio_manager.sh` + `bash tools/test_settings_ui_v24.sh`: peralihan soundtrack, efek, volume serta kanal audio tanpa memerlukan Android.
- `python3 tools/test_audio_v24.py android/assets/audio`: aset audio versi lama tetap utuh.
- `python3 tools/test_cinema_v25.py`: format/durasi audio v2.5, katalog 86 file, potret, minigame, cerita baru, dan hubungan perintah scene-audio.
- `python3 -I tools/check_layout.py android/assets`: peta/collision tetap dapat dijangkau.

**Belum setara dengan build/perangkat asli.** Logika headless dan pengujian sintaks tidak membuktikan animasi, layout, codec OGG, sinkronisasi audio, FPS, serta input layar sentuh pada Android. APK debug bisa dibangun di lingkungan dengan SDK/Gradle dan akses dependensi menggunakan `./gradlew :android:assembleDebug`. Jika distribusi Gradle tidak bisa diakses, jangan menyebutnya APK teruji.
