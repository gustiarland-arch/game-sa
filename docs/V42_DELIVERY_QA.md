# v4.2 — Catatan pengiriman dan gerbang kualitas

**Fondasi:** seluruh source v4.1.0 dipertahankan.

## Perubahan source nyata

- `android/assets/maps/`: 13 background baru (komposit tiga layer ilustrasi per area).
- `android/assets/props/v41_*.png`: 33 sprite landmark diperbaiki matte/transparansinya, ID dan footprint collision tidak berubah.
- `art_source/world_v42/`: backup baseline, total 39 editable layer RGBA, 33 baseline sprite.
- `tools/world_repaint_v42.py`, `tools/clean_landmark_alpha_v42.py`: generator deterministik, menulis PNG atomik.
- `tools/test_v42_world.py`: 667 pemeriksaan visual, 13+9 area, seluruh data dan aset audio.
- `tools/build_all.sh`, `tools/test_logic.sh`, `.github/workflows`: pembaruan pipeline regenerasi dan uji v4.x.

## Tes yang benar-benar dijalankan

- `LogicSelfTest`: 24.686 pemeriksaan lulus setelah Java core logic dikompilasi terpisah.
- `tools/test_maps_v4.py`: 302 pemeriksaan lulus.
- `tools/test_maps_v41_remaining.py`: 5.247 pemeriksaan lulus.
- `tools/test_maps_v4_navigation.py`: 131 target/portal dari spawn terjangkau.
- `tools/test_v42_world.py`: 667 pemeriksaan lulus.
- `tools/release_audit_v4.py`: 764 pemeriksaan statis lulus.
- `bash tools/test_controls_v28.sh`: 750 kontrol dan 126 pemeriksaan menu pengaturan lulus.
- `bash tools/test_romance_ui.sh`: smoke test input romansa lulus.
- Regenerasi dua kali: output 13 PNG memiliki SHA-256 identik, tanpa efek berulang.

## Batasan dan interpretasi

- Uji headless tidak mencakup hasil render pada GPU Android, konsistensi visual di berbagai rasio layar, maupun kinerja FPS.
- Upaya `./gradlew :android:assembleDebug --offline` masih berhenti ketika Gradle Wrapper mencoba mengunduh distribusi, **sebelum kompilasi aplikasi**. APK belum terverifikasi.
- Ini adalah tahap **scenic art polish + alpha cleanup**, bukan 13 redraw manual penuh. Untuk menyamai sembilan map handcrafted v4, perlu pengembangan ilustrasi komposisi map per lokasi dan tes collision baru bila geometri berubah.
- Tidak ada data/komponen runtime lama yang dihapus. Baseline dan generator dipertahankan agar source dapat diregenerasi.
