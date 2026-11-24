# v3.2 — Hasil pengujian source dan batasan rilis

Rilis source: **3.2.0**, engine tetap Java/LibGDX, tanpa layanan online.

## Pengujian yang dilakukan

- `bash tools/test_logic.sh`: **25.024** pemeriksaan logika lulus, kedua route Arland/Sofia, epilog, side quest, simpan/migrasi, ekonomi/romansa/minigame.
- `python tools/test_visual_v32.py`: **1.371** pemeriksaan, termasuk 22 peta dan 256 prop memiliki dimensi/alpha sesuai baseline, 25 karakter mempunyai 12-frame walk dan 6-frame idle atlas, 12 cinematic stills, semua file JSON cerita/gameplay dan audio tetap identik SHA-256.
- `python tools/release_audit_v32.py`: **1.172** pemeriksaan statis source dan seluruh aset (86 audio, 22 peta, workflow, metadata Android). Ini bukan build.
- `bash tools/test_release_v29.sh`: **44** pemeriksaan ketahanan save & prestasi; 51 file Java lulus parser sintaks.
- `bash tools/test_controls_v28.sh`: **750** pemeriksaan multitouch serta 126 pemeriksaan UI/pengaturan.
- `bash tools/test_v30_ui_compile.sh`: pemeriksaan tipe Java untuk komponen DialogueHistoryOverlay, MemoryBookOverlay, dan DialogBox melalui stub.
- `bash tools/test_dialogue_ui_v30.sh`: **6** pemeriksaan input riwayat dialog.
- `bash tools/test_audio_manager.sh`: **956** pemeriksaan headless pemutaran suara, transisi dan pause.
- `bash tools/test_romance_ui.sh`, `bash tools/test_visual_fx.sh`, `python tools/test_world_events_v27.py`: **lulus**.
- `python tools/visual_overhaul_v32.py`: keluaran gambar deterministik pada pemeriksaan hash ulangan, baseline original disertakan.

## Yang belum terbukti

- **APK/AAB Android nyata belum dikompilasi**; lingkungan kerja tidak memuat Android SDK/Gradle distributions.
- Pixel-art render, layout cutscene, kinerja GPU, FPS, ROM/RAM perangkat, status Play Store, alignment native 16 KB belum diuji pada hardware.
- Beberapa visual generator masih memerlukan review artis pixel art agar layak kualitas komersial.
- Target durasi enam jam **per route** dan uji playthrough manusia belum terverifikasi.

**Status**: source visual overhaul terintegrasi dan lulus tes headless/statik. **Bukan APK siap instal atau sertifikasi layak rilis publik.**
