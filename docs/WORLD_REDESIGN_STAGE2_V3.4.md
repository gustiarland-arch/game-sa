# Arland & Sofia v3.4.0 — Romantic & Fantasy Environment, World Redesign Tahap 2

**Status yang dapat diverifikasi:** 5 peta dan 30 sprite prop diperbarui pada **PNG runtime asli** (`android/assets/maps` dan `android/assets/props`), 20 PNG layer editable serta 35 baseline v3.3 tersedia. Ini **art pass prosedural + desain ornamen khusus lokasi**, bukan klaim bahwa seluruh area sudah digambar ulang manual. Tidak mengubah gameplay, JSON peta, collision, audio, route, quest, atau schema save. **APK Android dan FPS HP belum terverifikasi** karena Gradle/SDK tidak tersedia di lingkungan ini.

## Area yang diselesaikan pada tahap 2

| Area (ID) | Identitas baru | Perubahan aset runtime |
|---|---|---|
| Riverside (`riverside`) | Tepi sungai senja, rumput hijau hangat, kilau air, tepian berbuih, garis dekor batu menuju perahu | Palet hijau/teal; ratusan glint/riak yang di-mask hanya pada air; bangku, dermaga, kapal, batu dan ornamen jalan tetap pada koordinat lama |
| Dermaga (`dermaga`) | Dermaga kayu bernuansa amber, air lebih gelap, bidang pantulan lampu, motif kompas pada tanah, papan dan baut baru | Penambahan motif nautika, garis pantulan, revisi `bridge_dpier.png`, `bridge_dplat.png`, `rowboat*.png`, `pier_post.png`, `fishing_hut.png` |
| Bukit Bintang (`bukit_bintang`) | Suasana petang kehijauan, jalur observatorium berbintang, mandala rasi bintang, pencahayaan lebih redup | Latar lebih dingin, ukiran konstelasi di area observasi, detail kubah observatorium, teleskop, pagar dan lentera |
| Memory Garden (`memory_garden`) | Lantai ungu dengan konsentrasi sihir dekat poros memori, lingkaran kenangan, debu cahaya | Palette lavender, motif lingkaran memori, lampu & flora, sprite pohon mimpi/kristal/gerbang lebih kontras |
| Eternal Garden (`eternal_garden`) | Taman terakhir hijau pastel, cincin kenangan di area pohon harapan dan jalur utama | Variasi vegetasi, detail permukaan air dan perhiasan jalur, highlight pada `wishing_tree.png`, `gazebo_e.png`, gerbang dan bangku |

**Tidak berubah:** peta `plaza`, `taman_kota`, `cafe` hasil tahap 1 tetap biner identik. Secara kumulatif, **8 dari 22 peta** telah mendapat art pass khusus pada tahap 1–2. Sisanya masih memakai art pass v3.2; jangan mengklaim semua 22 area sudah direpaint secara manual.

## Aset yang benar-benar berubah dan dipakai engine

- **Map background**: `android/assets/maps/{riverside,dermaga,bukit_bintang,memory_garden,eternal_garden}.png` dipanggil melalui `data/maps.json`, path lama tetap.
- **30 sprite prop**: bridge_pier, bridge_dpier, bridge_dplat, pier_post, rowboat, rowboat_b, rowboat_rv, fishing_hut, fence_bb, observatory, telescope, chest_bb, stone_lantern_bb, stone_lantern_bb2, tree_dream, tree_lantern, crystal, pedestal_book, arch_flowers, arch_flowers_e, arch_flowers_e2, wishing_tree, gazebo_e, stone_bench, lantern_post, signpost_w3, tree_oak, rock, mushrooms, bush_d. Semua dipakai sebagai tipe prop pada lima area; beberapa juga dipakai area lain (visualnya ikut diperbarui tanpa mengubah collision).
- **Layer edit**: `art_source/world_stage2/editable_layers/<nama-map>/00_ground_palette.png`, `01_water_and_garden.png`, `02_landmark_details.png`, `03_atmosphere.png` (empat layer per area, transparan RGBA dengan ukuran sama persis seperti map).
- **Baseline**: `art_source/world_stage2/v33_unmodified/maps/` dan `props/`, untuk membandingkan atau rollback sebelum tahap ini.
- `art_source/world_stage2/stage2_manifest.json` mencatat dimensi, banyak piksel berbeda, alpha prop terjaga dan hash PNG hasil.
- `docs/ASSET_SHA256_V3.3.json` memuat hash 656 asset runtime pada proyek v3.3.0 sebelum perubahan ini.

> Catatan penting: grafik baru berupa detail baked pada background/PNG dan prop; riak/pantulan di sini adalah tekstur statis yang tetap terlihat saat permainan berjalan. Ini **bukan shader refleksi real-time**. Gerakan air yang sudah tersedia di engine tetap bekerja terpisah. Tidak mengubah collision peta atau membuat elevasi baru yang dapat dinaiki.

## Cara melihat dan mengedit

Pratinjau `docs/preview/v34_stage2_before_after.jpg` berisi 5 pasang komposit background **beserta prop runtime** untuk membandingkan versi. `v34_stage2_five_areas.jpg` berisi semua 5 area setelah perubahan. **Bukan screenshot APK atau hasil rendering GPU Android.**

Untuk mengedit langsung, ubah PNG di `android/assets/maps/` atau `android/assets/props/` memakai editor gambar, lalu simpan. Untuk mengedit master prosedural, ubah palet/ornamen pada `tools/world_redesign_stage2.py` dan jalankan dari direktori root proyek:

```bash
python3 tools/world_redesign_stage2.py
python3 tools/preview_world_stage2.py
python3 tools/test_world_redesign_stage2.py
```

`world_redesign_stage2.py` menggunakan gambar baseline v3.3, **bukan output hasil run sebelumnya**, sehingga dapat dijalankan ulang tanpa menumpuk warna/filter. Jika sudah mengedit PNG runtime secara manual, generator akan menimpanya; ubah generator atau backup karya manual terlebih dahulu.

`bash tools/build_all.sh` menjalankan tahapan v3.2 → v3.3 → v3.4; jangan menghapus file `art_source` sebelum build. Generator memerlukan Pillow dan NumPy. Semua sumber aset serta source aplikasi dibawa dalam ZIP yang sama.

## Gerbang verifikasi yang tersedia

```bash
python3 tools/test_world_redesign_stage1.py
python3 tools/test_world_redesign_stage2.py
python3 tools/test_visual_v32.py
python3 tools/check_layout.py android/assets
bash tools/test_logic.sh
bash tools/test_controls_v28.sh
bash tools/test_romance_ui.sh
```

`test_world_redesign_stage2.py` memastikan **tepat 5 map dan 30 prop berubah**, semua 656 asset asli masih ada, **86 file audio tetap identik**, **5 JSON game/collision identik**, PNG map tetap ukuran asli, alpha seluruh 30 prop sama piksel-per-piksel, 20 layer master tersedia dan tiap map benar-benar berubah pada ratusan ribu piksel. `test_logic.sh` berjalan headless ke epilog Arland/Sofia; tidak menguji gambar yang benar-benar tampil pada OpenGL.

## Hambatan sebelum rilis Android

APK debug atau signed AAB **belum dapat diverifikasi** di lingkungan ini karena Gradle/Android SDK tidak tersedia. Sebelum distribusi publik, wajib lakukan kompilasi Java/LibGDX/Android asli, menjalankan build pada HP nyata landscape, cek alpha blending, posisi prop/pintu/interaksi, FPS & temperatur, tes lifecycle audio, serta migrasi save schema 7. Klaim standar Sea of Stars / HD-2D komersial tidak otomatis terpenuhi oleh art pass ini; dibutuhkan art direction, ilustrasi ulang dan playtest artistik lebih lanjut.
