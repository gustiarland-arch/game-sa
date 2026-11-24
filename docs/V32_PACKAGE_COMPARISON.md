# Perbandingan v3.0 vs v3.2 (berkas proyek, bukan ukuran APK)

| Ukuran | v3.0 | v3.2 (sebelum ZIP) |
|---|---:|---:|
| Berkas source (termasuk docs & art_source) | 790 | 1174 (termasuk dokumen ini) |
| Gambar PNG runtime `android/assets` | 485 | 558 |
| Audio runtime (OGG/WAV/MP3) | 86 | 86 (identik SHA-256) |
| Peta runtime | 22 | 22 dirombak gambar dasar, nama/ukuran/collision tetap |
| Sprite walk 12-frame per arah | 0 | 25 atlas |
| Sprite idle 6-frame per arah | 0 | 25 atlas |
| Ilustrasi cutscene baru | 0 | 12 |

- Berkas baru yang dibuat: 383 sebelum laporan ini, yang sebagian besar adalah baseline gambar v3.0 yang sengaja dicopy ke `art_source/visual_v32_base` agar bisa digenerasi ulang.
- Berkas lama yang dimodifikasi: 312, termasuk 22 map PNG, 256 PNG prop, 21 PNG portrait, serta kode renderer, UI, dokumentasi dan build.
- Berkas v3.0 yang dihapus: **0**.
- Perbedaan ukuran ZIP final dihitung dari arsip hasil pengemasan, bukan klaim target ukuran.
- Visual example: `docs/preview/v32_before_after_actual_assets.jpg` (komposit raster dan prop asli, *bukan screenshot emulator*).
