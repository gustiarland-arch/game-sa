# Arland & Sofia v4.4 — Romantic Environments + Android Tablet UI

**Status:** source update yang diuji secara headless. **Belum** APK yang diverifikasi pada GPU/ponsel/tablet Android.

## Apa yang diubah di runtime

Art pass khusus ditambahkan langsung pada 4 raster aktif:

| Area | PNG runtime | Layer baru | Fokus |
|---|---|---|---|
| Dermaga | `android/assets/maps/dermaga.png` | 4 RGBA | Kilau sungai, riak, tepian dan pencahayaan dermaga |
| Bukit Bintang | `android/assets/maps/bukit_bintang.png` | 4 RGBA | Ornamen astronomi/konstelasi, bunga senja |
| Memory Garden | `android/assets/maps/memory_garden.png` | 4 RGBA | Lingkaran kenangan, kelopak bercahaya, warna lavender |
| Eternal Garden | `android/assets/maps/eternal_garden.png` | 4 RGBA | Jalur perayaan, motif taman dan aksen lentera |

Sebanyak **25 tipe prop baru** dengan prefiks `v44_` diterapkan ke **147 penempatan prop**, mempertahankan `cw`, `ch`, `layer`, dimensi gambar, mask alpha, dan semua anchor x/y. Tidak ada objek collision baru; perubahan ini adalah art pass yang ditujukan untuk kompatibilitas dengan quest/save lama, **bukan redraw handcrafted penuh**.

Peta lain **18/22** serta **88 file di direktori audio (termasuk file pendukung)** diverifikasi identik dengan baseline v4.3. Data spawn, door, examine, NPC, quest, dan collision **tidak diubah**.

## Tablet Android — perbaikan nyata

- `AdaptiveLayoutV44.java`: geometri murni yang dapat diuji tanpa OpenGL; menu utama 3×2 pada layar 16:9 lebar dan 2×3 pada tablet 4:3/16:10.
- `SlotScreen.java`: kartu save 3×2 pada landscape lebar agar baris tidak terlalu pendek; 2×3 pada rasio tablet sehingga ruang vertical lebih besar. Untuk game baru (3 slot), susunan dua kolom.
- `SettingsPanel.java`: panel memakai posisi berdasarkan safe inset yang disuplai pemilik screen (bukan asumsi layar utuh). Berlaku untuk Pengaturan dari title maupun Pause.
- `TitleScreen.java`, `SettingsScreen.java`, `GameScreen.java`: integrasi layout tersebut ke runtime.
- Test `tools/test_tablet_v44.sh`: enam profil landscape termasuk 16:9, 16:10, 4:3, inset kiri/kanan dan atas/bawah, memeriksa bounding box, ukuran tombol, dan overlap.

Orientasi yang ditargetkan tetap **landscape**. Efek nyata notch, keyboard, resize multi-window dan scaling font **belum diverifikasi di tablet fisik**.

## Cara mengedit dan meregenerasi

- Layer edit: `art_source/world_v44/editable_layers/<map>_{materials,landmarks,details,lighting}.png` (16 total).
- Map baseline v4.3: `art_source/world_v44/baseline_maps/` (4 PNG).
- Prop baseline v4.3: `art_source/world_v44/baseline_props/` (25 PNG).
- Manifest historis dan hash aktif: `art_source/world_v44/v43_manifest.json`, `docs/V44_WORLD_MANIFEST.json`.
- Generator raster: `python3 -I tools/world_redesign_v44.py`.
- Setelah regenerasi data cerita: `python3 -I tools/world_redesign_v44.py --metadata-only` memulihkan tipe prop dalam JSON tanpa menimpa background yang sudah diubah.
- Pratinjau sebelum/sesudah yang dibuat dari **background + prop proyek**: `docs/preview/v44_four_maps_before_after.jpg`. **Bukan screenshot emulator.**

## Pengujian dan batasan

```bash
bash tools/test_tablet_v43.sh
bash tools/test_tablet_v44.sh
python3 -I tools/test_world_v44.py
python3 -I tools/test_v43_world.py
python3 -I tools/test_maps_v4_navigation.py
bash tools/test_controls_v28.sh
bash tools/test_settings_ui_v24.sh
bash tools/test_logic.sh
```

`test_logic.sh` menjalankan regenerasi data serta pemeriksaan layout yang dapat memakan waktu panjang; apabila timeout, jalankan `LogicSelfTest` secara terpisah seperti dijelaskan di README. Tes visual v4.4 mengunci hash gambar dan audio, memvalidasi keutuhan 22 PNG, seluruh posisi & data collision, serta mask transparansi prop baru.

**Keperluan rilis yang masih terbuka:** full Gradle/Android compile, pengujian grafik GPU, tes touchscreen/notch tablet, performa/FPS dan memori, serta uji collision/spawn langsung di perangkat. Catatan bahwa 22 map sudah art-pass bukan berarti semua telah menjadi ilustrasi handcrafted seperti referensi yang diinginkan.

## Pembersihan source

Hanya cache `__pycache__`, file `.pyc`, dan direktori hasil tes yang dapat dibentuk ulang yang boleh dibuang. Semua `art_source`, `android/assets`, `core`, source gradle, `tools`, layer edit, audio, dan dokumentasi aktif disimpan. Jangan menghapus `baseline_maps` atau `baseline_props` karena dibutuhkan untuk regenerasi deterministik.
