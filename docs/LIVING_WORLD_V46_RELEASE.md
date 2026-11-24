# Arland & Sofia: Our Little Universe — v4.6 Living World 3.0

## Integrasi dari source asli

Versi ini dibangun di atas keseluruhan source v4.4 Android native LibGDX.
Source lama untuk 22 map, jalan cerita, route Arland/Sofia, cutscene, audio,
save schema 8, aset visual dan resource editable tidak dibuang.

## Yang diperbaiki

1. `GameScreen` membuka Romance Simulation 3.0 dari menu jeda memakai
   route dan slot asli. Sebelum beralih, save game utama harus sukses.
2. Slot game baru, ditimpa atau dihapus mereset **hanya** state romance
   pada slot terkait; tidak merusak route lain.
3. NPC berjalan lebih perlahan saat hujan dan malam, memilih waypoint
   deterministik yang tidak menembus collision, serta menghindari NPC lain.
4. NPC yang terhalang tidak lagi teleport menembus map; posisi dan target
   disesuaikan mengikuti collider asli.
5. Pose idle NPC menyesuaikan tugas, jam dan cuaca memakai spritesheet lama,
   tanpa menciptakan aset grafis pengganti.
6. Siklus waktu, cuaca, ambience, collision, peta 22 area, dan
   perubahan jadwal NPC yang sudah dimiliki game tetap dipakai.
7. Mesin v4.5 terikat hari dunia agar bonus dialog/janji tidak bisa
   digandakan dengan maju hari di menu khusus saat bermain.

## Penyimpanan

- `SaveStore` game utama tetap memakai schema lama dan backup CRC.
- `RomanceSaveV45` menyimpan namespace terpisah per route dan slot.
- Jangan menaikkan schema `Progress` tanpa migrasi eksplisit.
- Aset save pengguna tidak disimpan di repository.

## Verifikasi

- `bash tools/test_living_v46.sh` — unit NPC Java tanpa LibGDX.
- `bash tools/test_tablet_v44.sh` — unit layout tablet lama.
- `python3 tools/test_world_v44.py` — integritas world art 4.4.
- `bash tools/test_logic.sh` — regresi cerita, data dan save (lebih berat).
- `./gradlew :android:assembleDebug` — memerlukan JDK17/SDK Android/akses
  dependency Gradle. Belum dianggap lulus sampai ada hasil build.

**Belum terverifikasi di emulator/perangkat Android.**
Klaim lulus unit test bukan berarti APK sudah stabil di seluruh perangkat.

## Alur release GitHub

GitHub `main` harus berisi seluruh source, `android/assets`, dan `art_source`,
bukan hanya modul romance. Gunakan staging branch terverifikasi sebelum
menggantikan branch `main`; tidak perlu memakai Draft PR.

## Hasil integrasi source v4.6.0 final ZIP (23 November 2026)

- Implementasi lengkap engine `RomanceEngineV45` yang terikat jam dunia, termasuk enam kencan, empat hadiah spesial, tiga janji dengan konsekuensi, empat momen khusus dan riwayat keputusan.
- `RomanceV45Screen` menggunakan sistem UI/game font asli, input sentuh HP/tablet, navigasi halaman, serta fitur kembali ke gameplay tanpa mematikan `GameScreen`.
- `RomanceSaveV45` menyimpan per-route/per-slot, memvalidasi schema, dan mencegah penimpaan save lama yang tidak kompatibel.
- `GameScreen` meneruskan route, slot, dan hari dunia yang benar; tombol Jeda serta perbaikan NPC dibuat dalam source yang sama.
- Perbaikan regresi metadata empat area v4.4, sehingga integritas 22 peta tetap lulus.
- Semua source, sprite, audio, data JSON, layer gambar editable, Gradle wrapper, dan alat pemeriksaan disertakan di ZIP.

**Batasan:** pengujian kode dan aset offline lulus, tetapi build APK/perangkat Android belum bisa diverifikasi tanpa Android SDK + dependensi Gradle.

Lihat `docs/ANDROID_STUDIO_V46_SETUP.md` untuk membuka source di Android Studio.
