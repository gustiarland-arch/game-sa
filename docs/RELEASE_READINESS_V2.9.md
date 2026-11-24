# Arland & Sofia: Our Little Universe v2.9.0 — Release Readiness

**Status: SOURCE RELEASE CANDIDATE / BELUM LAYAK DIKLAIM SUDAH RILIS.**
Tanggal: 23 November 2026. Genre: petualangan naratif romantis, 2 route, native Android Java + libGDX, 100% offline.

## Perubahan nyata v2.9

1. **12 pencapaian offline dan progres lintas slot.** Tab `Prestasi` baru di Memory Book: bermain 2 menit, menyelesaikan chapter, pet 4 hewan, 3 aksi berdua, 3 minigame romansa, 5 event dunia, 3 momen, 3 kencan, kedekatan 75, 3 keping kenangan, tamat Chapter 6 di dua route. `GlobalProgress` schema 2; migrasi schema 1 tetap didukung. Prestasi tidak memberi barang/power karena ditujukan sebagai target bermain, bukan farming.
2. **Save lebih tangguh.** File utama dengan CRC, `.tmp`, `.bak`, `.bak2`, pemeriksaan isi semantik termasuk route & slot, perlindungan data dari versi game lebih baru, deteksi berkas tidak bisa dibaca, serta pengujian kegagalan tulis/backup. Menulis file utama tidak dilakukan bila cadangan gagal. `GdxFileIO` tidak lagi fallback dengan copy/delete yang berpotensi menimpa file bagus bila rename gagal. Saat menyimpan gagal, UI tidak mengaku berhasil dan pemain tidak dipaksa keluar ke menu.
3. **Mulai game gagal -> tetap di menu slot** dengan pesan error. Memori global diperbarui hanya jika save slot berhasil.
4. **Menu Pause > Cara bermain** di dalam game, berlaku untuk joystick/tombol, Memory Book, pengaturan, interaksi, dan simpan manual.
5. **Loading ringan.** Dekorasi 22 peta tidak dimuat seluruhnya saat startup; prop disiapkan per area aktif melalui `Assets.warmArea`. Ini mengurangi jumlah tekstur awal, tetapi waktu loading area/performa riil Android masih harus diukur.
6. **Audit asset statis** semua 22 peta, 25 pose, 25 atlas jalan, 86 audio, UI PNG, AndroidManifest, source config. `docs/ASSET_SHA256_V2.9.json` menyimpan hash file source asset agar perubahan tidak disengaja bisa dideteksi.
7. **Baseline Play 2026**: API 36 (Android 16) dengan AGP 8.10.0, Gradle 8.11.1, libGDX 1.14.2, Java 17 untuk build dan Java 11 untuk source. Ini perubahan dependency **yang belum berhasil dikompilasi atau diuji runtime di lingkungan pengembangan ini**.
8. **Signing aman berbasis environment** dan GitHub Actions `release-candidate.yml` untuk signed APK/AAB; tidak menyertakan sertifikat privat atau password.

## Semua file tetap di satu proyek

- `core/src/main/java/...` — gameplay, save, prestasi, UI, engine.
- `android/assets/maps` — 22 peta.
- `android/assets/characters` — atlas karakter dan portrait.
- `android/assets/audio/music` — 40 BGM, termasuk 7 komposisi cutscene.
- `android/assets/audio/ambience` — 14 ambience.
- `android/assets/audio/sfx` — 32 efek.
- `tools/` — generator dan tes.
- `.github/workflows/build-apk.yml` — build APK debug.
- `.github/workflows/release-candidate.yml` — signed APK dan AAB release, memerlukan keystore sendiri.

## Menjalankan tes source

Di direktori `ArlandSofia`:

```bash
bash tools/test_logic.sh
bash tools/test_release_v29.sh
python3 tools/release_audit_v29.py
bash tools/test_controls_v28.sh
bash tools/test_romance_ui.sh
python3 tools/test_audio_v24.py android/assets/audio
bash tools/test_audio_manager.sh
bash tools/test_soundscape_plan.sh
python3 tools/test_visual_v21.py android/assets
python3 tools/test_world_v23.py
python3 tools/test_couple_v22.py
python3 tools/test_cinema_v25.py
python3 tools/test_story_v26.py
python3 tools/test_world_events_v27.py
bash tools/test_visual_fx.sh
```

Butuh JDK 17, Python 3, Pillow, ffmpeg/ffprobe. Semua tes di atas **bukan** pengujian APK pada perangkat.

## Build Android yang perlu diverifikasi

1. Install JDK 17, Android SDK API 36, Build Tools 36, Android Studio dan Gradle wrapper yang tercantum; jangan menjalankan Gradle dari folder induk yang salah.
2. `./gradlew :core:test :android:assembleDebug` (Windows: `gradlew.bat :core:test :android:assembleDebug`).
3. Pasang APK debug **melalui update tanpa uninstall**, karena data save berada di private storage dan backup Android dimatikan. Saat pertama kali, pilih route Arland dan Sofia; coba audio serta tombol aman/notch.
4. Untuk Play, siapkan upload keystore di luar proyek dan set environment `OLU_RELEASE_KEYSTORE`, `OLU_RELEASE_ALIAS`, `OLU_RELEASE_STORE_PASSWORD`, `OLU_RELEASE_KEY_PASSWORD`. Kemudian `./gradlew :android:assembleRelease :android:bundleRelease`. Jangan bagikan file kunci/password, jangan commit ke repo.
5. Di GitHub Actions: isi **secrets** `OLU_RELEASE_KEYSTORE_BASE64`, `OLU_RELEASE_ALIAS`, `OLU_RELEASE_STORE_PASSWORD`, `OLU_RELEASE_KEY_PASSWORD`, lalu jalankan `Release Candidate (signed AAB)` secara manual. Workflow juga mengecek APK signed dan permission jaringan.
6. Uji **16 KB native ELF/page size** untuk `libgdx.so` serta semua `.so` hasil final; dukungan Play **BELUM TERBUKTI**. Gunakan tools Android `zipalign`, Android Studio APK Analyzer, `llvm-readelf`, dan emulator/perangkat 16 KB. Jangan submit ke Play sebelum lulus.

## Blocker wajib sebelum publikasi (bukan selesai hanya dengan script)

- [ ] `:android:assembleDebug` / `:android:bundleRelease` **berhasil** di Android SDK asli (belum: akses Gradle/SDK di lingkungan ini gagal).
- [ ] Uji runtime dan frame-time/FPS pada minimum **3 kelas perangkat** (RAM rendah, menengah, modern); berulang 30–60 menit.
- [ ] Validasi 16 KB memory pages **native `.so`** dan zip alignment 16 KB pada APK/AAB.
- [ ] Semua dialog/puzzle/quest Arland dan Sofia dimainkan manual di perangkat tanpa softlock; tes rotate landscape + background/resume + notifikasi panggilan + force-close.
- [ ] Uji migrasi save nyata dari v2.7/v2.8 di perangkat (tanpa uninstall), serta kondisi storage penuh/akses privat gagal.
- [ ] Tes audio dengan speaker/headset/Bluetooth, transisi track dan pause/resume tidak menumpuk audio.
- [ ] Tes cutout/notch, tombol UI, joystick, Accessibility text, dan navigasi tombol fisik.
- [ ] Audit performa memori GPU: setiap peta 2048–2560px membutuhkan ~12–20 MB RGBA; cache karakter/props juga memakai VRAM. Sesuaikan perangkat minimum jika perlu.
- [ ] Lakukan penyuntingan konten untuk kualitas dialog, typo, konsistensi karakter dan pacing; target 6 jam/route **belum tercapai** (simulasi ~3 jam 40 menit/route untuk full content).
- [ ] Audit legal aset, font, musik, hak visual/karakter, dan kebijakan privasi. Source audio baru bersifat prosedural; pastikan seluruh source pihak ketiga berlisensi untuk distribusi.
- [ ] Siapkan listing Play Store: screenshot nyata dari APK, ikon, banner/feature graphic, kebijakan privasi URL, rating konten, data safety, pengujian tertutup sesuai eligibility, serta identitas developer.
- [ ] Test signed AAB melalui internal testing sebelum rilis publik. **Jangan menyebut ini production ready tanpa hasil di atas.**

## Sumber aturan resmi (ditinjau 23 November 2026)

- Target API Android 16/API 36 untuk aplikasi baru dan update Play (ketentuan umum telepon Android): https://developer.android.com/google/play/requirements/target-sdk
- Kompatibilitas AGP/Gradle dan SDK 36: https://developer.android.com/build/releases/about-agp ; https://developer.android.com/build/releases/agp-8-10-0-release-notes
- Ukuran halaman native 16 KB: https://developer.android.com/guide/practices/page-sizes
- libGDX stable 1.14.2: https://libgdx.com/dev/versions/

## Perubahan yang sengaja tidak dilakukan

- Tidak menghapus sistem 14 event dunia, 6 minigame berdua, 21+ side quest, route canon, NPC, save lama, atau 86 audio.
- Tidak mengubah save schema 6 karena field state gameplay tidak berubah; `GlobalProgress` tersendiri berkembang menjadi schema 2.
- Tidak menyertakan APK/AAB/keystore palsu. ZIP adalah source, **bukan artefak aplikasi teruji**.
