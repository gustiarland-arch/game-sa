# Arland & Sofia v3.3.0 — World Redesign, Tahap 1

**Status:** 3 area benchmark direnovasi pada **file PNG runtime yang digunakan engine**, tanpa mengubah data map atau logika. Source ini belum diuji melalui APK Android nyata. **Ini bukan redesign manual 22 area dan belum setara ilustrasi artist RPG HD-2D referensi.**

## Cakupan yang nyata

| Area | Art direction baru | Implementasi source |
|---|---|---|
| **Plaza Kota** (`plaza`) | Halaman batu bernuansa sandstone, inlay melingkar dekat air mancur, medallion pada jalur, detail genteng dan fasad bangunan, warna taman lebih dalam, pencahayaan hangat | `android/assets/maps/plaza.png`, `props/fountain.png`, `props/bld_*.png`, props pohon/bangku/lampu, 4 PNG layer terpisah |
| **Taman Kota** (`taman_kota`) | Material jalan lebih bervariasi, dedaunan/hamparan bunga, detail permukaan kolam dan daun teratai, perubahan atap/tiang gazebo menjadi kayu-terrakota, mandala sekitar gazebo, refleksi lembut | `android/assets/maps/taman_kota.png`, `props/gazebo.png`, `bridge_park.png`, flora dan props lain, 4 layer |
| **Kafe Senja** (`cafe`) | Dinding berpanel, lampu gantung, parket herringbone, ornamen lantai area duduk, sorot cahaya jendela, finishing meja/kounter/lemari dan pintu | `android/assets/maps/cafe.png`, props interior, 4 layer |

**Hasil yang benar-benar berubah:** 3 latar peta dan 29 sprite prop; 12 layer PNG transparan sebagai master yang bisa diedit. Ketiga latar digabung ke path PNG yang dipanggil engine yang sudah ada. Tidak perlu membuat atau mengubah JSON peta.

## Lokasi source dan editing

- Edit generator dalam `tools/world_redesign_stage1.py` (palet, jenis material, komposisi ornamen, lighting, detil props). Tool ini tidak memerlukan internet.
- Editable layers ada di `art_source/world_stage1/editable_layers/<plaza|taman_kota|cafe>/` dengan urutan `00_ground_palette.png`, `01_materials.png`, `02_landmarks.png`, `03_lighting.png`.
- Baseline v3.2 yang *belum diedit oleh tahap ini* tersimpan di `art_source/world_stage1/v32_unmodified/maps/` dan `props/` untuk semua file yang diperbarui.
- Runtime final hasil gabungan ada di `android/assets/maps/` dan `android/assets/props/`. Untuk mengganti langsung lewat VS Code atau editor pixel art, ubah PNG runtime. **Jangan jalankan generator setelah mengubah PNG secara manual**, kecuali ingin mengganti file editan dengan hasil procedurally-generated.
- Untuk regenerate semua map tahap ini: `python3 tools/world_redesign_stage1.py` dari root proyek. Generator deterministik (hasil byte PNG identik saat input dan versi Pillow sama).
- Untuk melihat pratinjau dari source: `python3 tools/preview_world_stage1.py`. File `docs/preview/v33_stage1_before_after.jpg` membandingkan **aset asli setelah prop digambar ke peta**, bukan screenshot emulator.
- `bash tools/build_all.sh` menjalankan pipeline lengkap, termasuk generator v3.2 dan tahap 1 v3.3. Memerlukan Pillow, NumPy, fontTools, dan tool audio yang dijelaskan pada README.

## Batas kompatibilitas dan collision

- **Resolusi semua map tidak berubah**; `data/maps.json` serta `data/props.json` identik byte-per-byte dengan v3.2. Spawn, pintu, collision, alur quest, anchor, route, area terbuka, NPC dan event dunia sama.
- Siluet alfa setiap 29 prop **identik pixel-per-pixel** dengan v3.2. Recolor dan detail berada di dalam bentuk sprite lama; tidak menambah area tabrakan baru.
- **19 peta di luar benchmark tidak diubah** pada tahap ini. Penyesuaian art direction area lain dilakukan bertahap setelah tiga benchmark ditinjau.
- Seluruh 86 file musik/SFX/ambience dan dua katalog audio JSON tidak dimodifikasi. Save schema tetap 7.
- Menu, atlas 25 karakter, cutscene, seluruh ilustrasi v3.2, 398 adegan, serta konten game lain tetap dibawa utuh.

## Uji yang dapat direproduksi

```bash
python3 tools/test_visual_v32.py
python3 tools/test_world_redesign_stage1.py
python3 tools/check_layout.py android/assets
bash tools/test_logic.sh
bash tools/test_controls_v28.sh
bash tools/test_romance_ui.sh
```

`test_world_redesign_stage1.py` membandingkan file runtime terhadap *bundled* `docs/ASSET_SHA256_V3.2.json`, memastikan perubahan tepat pada 3 peta dan 29 prop, 12 layer tersedia, seluruh sisa data audio/gameplay tetap sama, serta alpha, dimensi, dan sumber proyek utuh. Berkas `tools/test_logic.sh` melindungi `mural_new.png` saat generator konten dijalankan agar tes **tidak meninggalkan** perubahan aset sampingan.

**Penting:** tes tersebut bersifat statis, headless, dan render komposit di Python. Tes belum memverifikasi GPU, FPS, cutscene runtime, atau kompilasi APK Android nyata. Kualitas visual yang setara contoh referensi akan membutuhkan produksi ulang ilustrasi dan spritesheet artistik, bukan sekadar perubahan prosedural ini.

## Tahap selanjutnya yang belum dilakukan

1. **Tahap 2:** Riverside, Dermaga, Bukit Bintang, Memory Garden, Eternal Garden (air, refleksi, ruang romantis).
2. **Tahap 3:** Starfall Village, Star Path, Gua Kristal, Lantern Field, Hutan Bisik (dunia magis dan kedalaman foreground).
3. **Tahap 4:** Perumahan, Jalan Kota, Kamar Arland dan Sofia, Perpustakaan, Arcade, Dapur, Ruang Arsip, Toko Bunga dan area tersisa. Audit total 22 peta dan siluet props.
4. **Wajib sebelum rilis:** build APK debug/release Android yang berhasil, pengujian perangkat dan performa GPU, QA seluruh konten, evaluasi visual langsung di layar landscape, audio, migrasi save dan kompatibilitas Android.
