# Arland & Sofia: Our Little Universe — v3.0.0

**Status: SOURCE RELEASE CANDIDATE; BELUM SIAP RILIS PUBLIK.**
23 November 2026 — Java + LibGDX native Android, landscape, offline, dua protagonis, satu ending canon.

## Fitur baru yang benar-benar ada di source

1. **Riwayat Dialog per slot**: maksimal 72 baris terakhir, menampilkan nama pembicara dan hari cerita; tersedia lewat tombol **Riwayat** di Dialog, tombol **Riwayat dialog** pada Jeda, atau tombol `H` saat eksplorasi/dialog. Teks dicatat saat ditampilkan (termasuk pilihan dialog). Overlay mendukung halaman Baru/Lama; cutscene dan pengetikan dialog berhenti sementara overlay dibuka.
2. **Kompas Misi**: ketika `Pengaturan > Tampilan > Petunjuk` aktif dan ada marker quest utama di area sekarang, HUD menampilkan arah mata angin + jarak perkiraan. Ini **bukan GPS/rute pathfinding** dan tidak membuka lokasi cerita yang dikunci; sistem memilih marker valid yang terdekat.
3. **Jelajah di Memory Book**: tab baru menampilkan 22 area dan apakah sudah pernah dikunjungi pada slot/route tersebut; menandai saat area dimasuki, tidak mengubah pintu, collision, atau gate. Tidak mengklaim map fog-of-war atau peta seluruh dunia.
4. **Autosave reguler 90 detik waktu gameplay bebas** (bukan waktu berlalu di cutscene, puzzle, overlay). Penyimpanan juga tetap terjadi pada event penting seperti versi sebelumnya. Kegagalan save tidak mengirim pesan sukses.
5. **Save schema 7**: mempertahankan field lama dan menambah `dialogueHistory` / `visitedAreas`. Save schema 1–6 dimigrasikan saat dibaca. Riwayat disanitasi dan dibatasi untuk menjaga ukuran berkas; slot `.bak`/`.bak2` tetap ada.
6. **Perlindungan backup**: file utama yang lulus checksum tetapi gagal validasi isi tidak dirotasi ke backup. Penulisan dengan `step` kosong ditolak. File utama dengan schema lebih baru tidak ditimpa oleh aplikasi ini.
7. **Pemeriksaan kandidat rilis**: audit hash aset v2.9 → v3.0, pemeriksaan source, skrip pemeriksa native ELF 16KB plus unit test sintetis, workflow CI untuk APK debug serta signed AAB. Kunci signing tetap di GitHub secrets.

## Yang dipertahankan

- 398 adegan cerita, 1.991 baris dialog, 93 langkah main story, 25 side quest katalog (22 sesuai route), 14 event dunia, 6 minigame romantis, 8 aksi pasangan.
- 22 peta, 25 karakter/NPC, 129 entri Memory Book, 86 audio (**40 musik, 14 ambience, 32 efek**) di `android/assets/audio/`.
- Dua route Arland dan Sofia tetap berbeda tetapi menuju ending canon yang sama.
- Kontrol joystick Android, kualitas grafik Hemat/Seimbang/Sinematik, pengaturan audio, mode replay, dan 12 pencapaian global.
- Seluruh source, aset, audio, pengujian, dokumentasi, Gradle wrapper, dan workflow dalam **satu ZIP**.

## Cara membangun dan menguji

Syarat: Java/JDK 17, Android SDK API 36, Build Tools 36, Gradle 8.11.1 (wrapper), akses jaringan untuk dependency awal.

```
./gradlew :core:test :android:assembleDebug
```

Windows PowerShell:

```
.\gradlew.bat :core:test :android:assembleDebug
```

APK debug di `android/build/outputs/apk/debug/` **hanya bila build sukses**. Tidak ada APK hasil build yang disertakan dalam ZIP ini. *Jangan menghapus aplikasi lama dari HP demi update versi*, karena save lokal dapat ikut terhapus. Selalu backup file save melalui mekanisme pengujian yang aman sebelum migrasi.

Tes headless:

```
bash tools/test_logic.sh
bash tools/test_v30.sh
bash tools/test_dialogue_ui_v30.sh
python3 tools/test_native_16k_v30.py
python3 tools/release_audit_v30.py
bash tools/test_controls_v28.sh
python3 tools/test_android_v28.py
python3 tools/test_world_events_v27.py
```

`tools/verify_native_16k_v30.py` hanya boleh dijalankan pada APK sungguhan, diikuti `zipalign -c -P 16 -v 4 <APK>` serta tes perangkat memori 16 KB. Unit test sintetis **tidak** membuktikan native `libgdx.so` terkompilasi aman.

## Status pengujian v3.0

- Headless dua route sampai epilog: **25.024 pemeriksaan lulus**.
- Model/dialog/save/backup: **19 + 44 pemeriksaan**.
- Dialog overlay: **6 pemeriksaan** terhadap stub UI, bukan OpenGL.
- Source/package audit: **1.374 pemeriksaan**, 583 aset sebelumnya identik dengan v2.9.
- Regresi visual 22 area, animasi pasangan, minigame, audio 86 file, kontrol UI: lulus pada pengujian source/aset.
- Pemeriksaan native 16 KB sintetis: lulus, real binary belum tersedia.
- **Build APK Android tidak berhasil:** Gradle wrapper gagal mengunduh Gradle 8.11.1 (`UnknownHostException: services.gradle.org`). Source belum terkompilasi terhadap dependensi LibGDX sebenarnya di lingkungan ini.

## Blocker sebelum Play Store / distribusi umum

1. [ ] Android Gradle build debug dan signed release AAB sukses tanpa error compile/link/native packaging.
2. [ ] Periksa native alignment dari APK nyata (ELF PT_LOAD + zipalign 16KB), serta jalankan di emulator/perangkat 16KB.
3. [ ] Jalankan daftar skenario `docs/V3_DEVICE_QA.md` di perangkat Android rendah, menengah, tinggi; ukur FPS, RAM, VRAM, dan baterai minimal 30 menit per device.
4. [ ] Main manual route Arland dan Sofia sampai epilog tanpa softlock, termasuk save/load/migrasi, area yang terkunci, cutscene, dan minigame.
5. [ ] Uji migrasi schema 6 → 7 di perangkat dengan **update tanpa uninstall**, serta recovery `.bak` saat terjadi force close/storage full.
6. [ ] Tinjau legal semua gambar/font/audio dan sumber aset pihak ketiga; lisensi game sendiri harus diputuskan developer.
7. [ ] Siapkan halaman Play Store dengan screenshot **APK aktual**, AAB signed, content rating, privacy policy, data safety dan testing tertutup yang berlaku.
8. [ ] Periksa ulang estimasi durasi: simulator sekitar **3 jam 40 menit per route** untuk seluruh konten, belum mencapai target 6 jam per route; playtesting sesungguhnya belum dilakukan.

**Keputusan QA:** v3.0.0 adalah kemajuan source dan prototipe kompleks, tetapi **tidak boleh disebut production ready / sudah layak rilis** sampai semua blocker perangkat dan distribusi diselesaikan.
