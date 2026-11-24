# Audit v4.8.0 — Story World & Cinematic

## Hasil audit source
1. **Seluruh konten cerita** sejak v4.7.4 dipertahankan: Prolog, Chapter 1–6 dan epilog; 736 scene, 157 step, 29 area, 287 Memory Book. Tidak ada ending alternatif atau penghapusan otomatis save.
2. **Visual runtime**: `android/assets/maps/{galeri_komunitas,rain_garden,clockwork_station,memory_bridge,moonlight_lake,hall_of_tomorrow,ruang_dua_surat}.png`. Ketujuh layer editable ada di `art_source/story_v480/editable_layers/`, dengan file original dari v4.7.4 di `art_source/story_v480/base_maps/`. Generator deterministik: `python3 tools/remaster_story_world_v480.py`. Tidak mengubah matriks tabrakan maupun portal.
3. **Audio orisinal**: `android/assets/audio/music/score_{empty_chair,rain_resolve,quiet_truth,open_page,lake_coda}_v480.ogg`, stereo 44.1 kHz Vorbis, 75–88 detik. Komposisi/nota dapat diedit di `tools/gen_cinematic_scores_v480.py` dan `art_source/story_v480/scorebook.json`. Audio dihubungkan ke `SoundscapePlan.java`, bukan hanya disimpan.
4. **Cinematic**: enam interaksi quest memakai shot kamera, tint, efek, caption dan skor musik baru. ID soundtrack lama tetap terpicu untuk kompatibilitas. Script: `tools/apply_story_cinematics_v480.py`.
5. **Bug gameplay diperbaiki**: gallery `cafe_to_gallery_v464` tetap terkunci sampai Chapter 3, *kecuali* selama langkah `V468_C02_NO_SKETCH` di Sofia Route; perbaikan idempotent di `tools/repair_c02_gallery_access_v480.py`. Ini merupakan bug yang ditemukan saat `tools/test_logic.sh`.
6. **Regenerasi**: `tools/build_all.sh` menjalankan empat skrip patch baru dan tes tambahan. `tools/test_logic.sh` juga menjaga data v4.7.4/v4.8 ketika generator dasar digunakan.

## Bukti pemeriksaan
- `bash tools/test_logic.sh` — dua route Prolog sampai Epilog: 29.064 pemeriksaan berhasil setelah bug galeri diperbaiki.
- Tes route C04: 324 jalur, 70.273 pemeriksaan. C05: 108 jalur, 21.234 pemeriksaan. C06: 576 jalur, 101.466 pemeriksaan.
- Tes Epilog: 36 jalur / 3.376 pemeriksaan; Prolog: 96 jalur / 12.465 pemeriksaan; tes Chapter 1–3 juga lulus.
- Tes UI/sinematik 859 pemeriksaan, tablet 390 pemeriksaan, kontrol 126 pemeriksaan; tes audio/media dan romansa lulus.
- `python3 tools/test_story_world_v480.py`: cek pixel art, komposit layer, musik Vorbis, registrasi, kompatibilitas, collision, portal, cutscene, dan sumber generator.
- ZIP CRC/integritas diperiksa pada final packaging terpisah dari pengujian di atas.

## Belum bisa diklaim
- Full Gradle Android build / instalasi APK / performa FPS di GPU ponsel / uji touch Android langsung: belum tersedia Android SDK/Gradle di lingkungan pembuatan.
- Penilaian artistik final, seluruh kemungkinan interaksi manual, keberlanjutan main 6 jam, dan 0 bug: memerlukan playtest manusia.
- Semua contoh cerita bersifat fiksi; perubahan konten eksplisit sebaiknya ditinjau pembuat game.

## Membuka proyek
Ekstrak ZIP → buka folder `ArlandSofia` di Android Studio → siapkan JDK 17, Android SDK 36 dan Gradle dependencies → Sync → modul `android` → Run pada emulator/HP. Jangan menganggap tes headless setara build APK.

## Batas proses regenerasi penuh
Percobaan menjalankan `bash tools/build_all.sh` pada salinan source tidak selesai dalam batas proses di lingkungan ini. Proses generator aset/musik legacy memerlukan komputasi panjang; karena itu **tes regenerasi penuh belum boleh ditandai lulus**. Empat generator/patch **khusus v4.8.0** sudah dijalankan ulang, hash peta/data/source tetap identik, dan regresi source per chapter lulus. Pengujian build APK juga tetap tertunda.
