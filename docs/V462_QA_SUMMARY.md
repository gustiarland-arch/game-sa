# QA v4.6.2 — Hasil Pengujian Lokal (source/headless)

Tanggal: 23 November 2026. Basis: paket ZIP v4.6.1 Stability Polish. **Tidak ada push ke GitHub.**

## Pengujian yang lulus

| Pengujian | Hasil |
|---|---|
| Arah gerak 8 arah, blend berdasarkan waktu, anggaran FX & 22 profil area | 191 assertion PASS |
| Aset visual baru | 4 atlas (2 tokoh × walk/idle) + 7 PNG FX valid |
| Java source parsing | 67 berkas Java syntactically valid (Java 11) |
| WorldFx type-check & render calls stub | PASS (bukan OpenGL) |
| Actor & lighting type-check + smoke | PASS (bukan OpenGL) |
| Living World v4.6 | 12 assertions PASS |
| Romance v4.6 | 51 assertions PASS |
| Tablet & safe-inset layouts | 390 checks PASS |
| Save migration | 38 assertions PASS |
| Kontrol sentuh, settings UI | 750 touch assertions + 126 layout/input checks PASS |
| World art v4.4 | 2.197 pemeriksaan PASS |
| Navigasi map | 131 portal/target checks PASS |
| Audio source legacy v2.4 | 267 pemeriksaan PASS |
| Audit byte-preservation source v4.6.1 | 717 aset asli IDENTIK, 22 map & 88 audio termasuk |

`tools/test_character_v37.py` adalah pemeriksaan historis berbasis hash v3.6, dan tidak kompatibel dengan map v4.6 yang sudah berubah sejak versi 4.0. Ketika dicoba, tes ini berhenti pada `maps/arcade.png`, tetapi SHA-256 file tersebut cocok persis dengan basis v4.6.1; tes v4.4 world-art yang sesuai versi berjalan lulus.

## Batasan penting

Tidak ada SDK Android / Gradle distribution yang tersedia secara offline. Karena itu **belum dijalankan build APK, benchmark FPS, uji ponsel/tablet fisik, cutscene penuh, atau pengujian GPU**. Atlas diagonal merupakan adaptasi prosedural pixel-preserving dari arah kardinal, bukan sprite yang dilukis manual. Efek tambahan v4.6.2 merupakan lapisan runtime non-destruktif; background PNG asli 22 map belum direpaint lagi.

Verifikasi sumber: `docs/V462_SOURCE_AUDIT.json` dan screenshot atlas sumber: `docs/preview/v462_character_world_assets.png` (bukan tangkapan layar aplikasi).
