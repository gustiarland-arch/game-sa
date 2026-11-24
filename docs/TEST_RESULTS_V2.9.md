# Catatan Uji Source v2.9.0 — 23 November 2026

Berikut hasil uji yang benar-benar dijalankan pada source v2.9.0 di lingkungan headless Linux. **Ini bukan bukti build Android berhasil atau game sudah layak rilis.**

| Pemeriksaan | Hasil |
|---|---|
| `bash tools/test_logic.sh` | **PASS 25.024** pemeriksaan logika, cerita Arland/Sofia sampai epilog, side quest, save, waktu, event, puzzle, romansa |
| `bash tools/test_release_v29.sh` | **PASS 39** asersi save rusak/backup/io-failure/migrasi/prestasi; parse-only 48 file Java; UI renderer tidak dikompilasi terhadap LibGDX riil |
| `python3 tools/release_audit_v29.py` | **PASS 784** asersi statis; **583 aset**, **485 PNG**, **86 audio**, **22 peta**; SHA256 manifest tercatat |
| `bash tools/test_controls_v28.sh` | **PASS 750** input/multitouch + **126** settings UI checks; wrapper controls type-checked dengan stub |
| `bash tools/test_romance_ui.sh` | PASS input overlay romansa |
| `bash tools/test_audio_manager.sh` | **PASS 956** headless audio state checks |
| `bash tools/test_soundscape_plan.sh` | **PASS 1.376** penjadwalan musik |
| `python3 tools/test_audio_v24.py android/assets/audio` | **PASS 267** pemeriksaan audio bawaan v2.4 termasuk ffprobe codec dan durasi |
| `python3 tools/test_visual_v21.py android/assets` | **PASS 112** pemeriksaan visual |
| `python3 tools/test_world_v23.py` | **PASS 463** pemeriksaan peta/pose |
| `python3 tools/test_couple_v22.py` | **PASS 528** pemeriksaan aset/pose/aksi berdua |
| `python3 tools/test_cinema_v25.py` | **PASS 93** pemeriksaan audio sinematik, game, portrait |
| `python3 tools/test_story_v26.py` | **PASS 395** pemeriksaan perluasan cerita |
| `python3 tools/test_world_events_v27.py` | **PASS 315** pemeriksaan event dunia |
| `python3 tools/test_android_v28.py` | **PASS 115** pemeriksaan fitur lama/paket |
| `bash tools/test_visual_fx.sh` | PASS Java parse-only 50 file + WorldFx headless smoke |
| Gradle wrapper `./gradlew --version` | **FAIL / BLOCKED** pada unduhan Gradle (`services.gradle.org`), SDK Android tidak tersedia. Tidak dapat memverifikasi kompilasi, penggabungan manifest, APK/AAB atau signing. |

Semua verifikasi file internal selesai, tetapi **kemampuan OpenGL, FPS, memory usage, 16 KB native libraries, perangkat ber-notch, audio Bluetooth dan perilaku Android 16 tetap BELUM DIUJI**. Rincian langkah manual ada di `docs/DEVICE_QA_CHECKLIST_V2.9.md`.
