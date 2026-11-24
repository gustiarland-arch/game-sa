# Status rilis source v4.6.0

Proyek: Arland & Sofia: Our Little Universe
Platform: Android native / LibGDX, offline
Jenis paket: source lengkap, bukan APK

## Termasuk
- Source asli dan aset editable seluruh 22 map dari baseline v4.4.
- Modul Romance Simulation 3.0: kencan, kepercayaan, hadiah, janji, dan momen berbasis keputusan.
- Living World 3.0: waypoint NPC deterministik, menghindari tabrakan/teleport, interaksi waktu/cuaca.
- Berkas Gradle, source utama, tests, audio, data narasi, dan folder aset.
- Dua route (Arland/Sofia) serta satu canon ending dipertahankan.

## Pemeriksaan pada paket ini
- `bash tools/test_living_v46.sh`: PASS, 9 assertions.
- `bash tools/test_romance_v46.sh`: PASS, 48 assertions.
- `bash tools/test_tablet_v44.sh`: PASS, 390 checks, enam profil layar.

## Belum terverifikasi
- Build APK Android (`:android:assembleDebug`) dan uji perangkat sebenarnya.
- Pengujian UI Android/LibGDX menyeluruh.
- Seluruh suite regresi/asset di lingkungan ini.

Untuk rilis publik, lakukan build dengan Android SDK/JDK yang didukung, lalu tes kedua route,
save slot lama, seluruh peta dan layar HP/tablet. Jangan menyatakan siap produksi sebelum itu.
