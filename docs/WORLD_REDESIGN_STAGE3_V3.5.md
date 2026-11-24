# Arland & Sofia v3.5.0 — Fantasy World Redesign, Tahap 3

**Status: 5 peta + 36 sprite prop runtime yang benar-benar berubah.** Lima area baru art pass: Starfall Village, Star Path, Gua Kristal, Lantern Field, Hutan Bisik. Semua asset dibuat dari versi source v3.4.0, bukan dari gambar referensi internet atau screenshot palsu. Ini desain ulang prosedural dengan ornamen lokasi, bukan penggambaran manual pixel art dengan kualitas Sea of Stars.

## Art direction per area

| Area | Perubahan nyata (dibakar ke background/prop PNG) | Fokus visual |
|---|---|---|
| Starfall Village | Repaint lembut jalan lavender, urat batu dan cincin mosaik di alun-alun, pendar lampu rumah, detail genteng dan bingkai jendela bangunan | Desa langit malam, rumah berwarna, jalur pusat desa |
| Star Path | Perbedaan warna antara jalur terang dan ruang gelap, bintang kecil, simbol/lingkaran konstelasi pada tanah di luar jalan | Perjalanan bintang terasa mistis |
| Gua Kristal | Retakan mineral bercahaya, ukiran simbol, rona cyan dan violet di pulau gua, garis pantulan di kolam | Kristal dan situs purba yang megah |
| Lantern Field | Variasi padang biru, bunga-bunga kecil, ukiran lingkaran festival pada plaza, pola jalan dan glow lentera | Romantis dan hangat dalam suasana malam |
| Hutan Bisik | Penanda jalur, daun gugur, rumput bersusun, tepian sungai dengan gelombang, detail pohon gelap dan jembatan | Hutan kaya tekstur, tetap jelas untuk eksplorasi |

### Aset yang dihasilkan

- **5 latar PNG yang dipakai runtime** pada `android/assets/maps/`, dengan nama dan resolusi lama; tidak membuat lokasi dummy.
- **36 sprite prop yang dipakai runtime** pada `android/assets/props/`: star_stone, bld_star_house0, bld_star_house1, bld_star_house2, pedestal_book_map, crystal_big, stalagmite_s0, stalagmite_s1, stalagmite_s2, stalagmite_s3, stalagmite_s4, stalagmite_s5, carving_flower, chest_gk, lantern_off, tree_dark, bush, bush_plain, bush_berry, stone_lantern, waterfall_hb, bridge_broken_hb, cave_entrance, carving_moon, tent, campfire, log_bench, log_bench_b, carving_star, mushroom_ring, chest, chest_hs, stone_lantern_e, signpost_e2, signpost_s2, signpost_hx.
- **25 layer transparan** pada `art_source/world_stage3/editable_layers/<map>/`, lima per map: `00_art_direction.png`, `01_surface_materials.png`, `02_environment_landmarks.png`, `03_path_edges_and_reflections.png`, `04_local_light.png`.
- **41 baseline v3.4 yang dipreservasi** di `art_source/world_stage3/v34_unmodified/`, untuk mengedit dari versi sebelum overhaul dan rollback.
- `art_source/world_stage3/stage3_manifest.json` melaporkan jumlah piksel yang berubah, dimensi tiap gambar dan hash PNG runtime. `docs/ASSET_SHA256_V3.4.json` merupakan snapshot semua hash runtime v3.4 (656 file).
- Pratinjau **sebelum–sesudah** dari komposit background + prop tersedia di `docs/preview/v35_stage3_before_after.jpg`, bukan screenshot APK.

### Konsistensi engine dan collision

Semua background dan prop ditimpa **di path yang telah dirujuk `data/maps.json` dan `data/props.json`**. Artinya tanpa perlu mengganti navigasi atau quest engine. Bentuk alpha semua sprite prop dipertahankan piksel demi piksel; ukuran masing-masing peta juga sama. Tidak ada koordinat spawn, warp, collision JSON, NPC, quest atau data save yang diubah. Visual baked tidak menciptakan tempat berjalan baru, elevasi baru, atau pencahayaan dinamis raytracing.

**Kompatibilitas versi lama:** save schema 7 seperti v3.0–v3.4. Meski data progres tidak diubah, buat backup save ketika pindah antar APK pengembangan. Peta 8 area dari tahap 1–2 tetap hash-identik. Secara kumulatif **13/22 map** telah menerima art pass khusus. Sembilan map lainnya masih menggunakan visual dasar v3.2.

### Mengedit di VS Code atau editor gambar

1. Lihat `docs/preview/v35_stage3_before_after.jpg` untuk titik visual yang berubah. Untuk penggantian cepat, edit PNG pada `android/assets/maps/` atau `android/assets/props/` dengan editor PNG; source tidak harus dipindahkan.
2. Untuk mengubah satu bagian tanpa mengganggu bagian lain, edit lima layer RGBA per map di `art_source/world_stage3/editable_layers/` memakai Krita, Aseprite, GIMP, atau editor lain yang mempertahankan alpha.
3. Jika ingin regenerasi via Python, sesuaikan palet/landmark/tekstur pada `tools/world_redesign_stage3.py`, lalu jalankan dari root proyek:

```bash
python3 tools/world_redesign_stage3.py
python3 tools/test_world_redesign_stage3.py
python3 tools/test_world_redesign_stage2.py
python3 tools/test_world_redesign_stage1.py
bash tools/test_logic.sh
```

**Perhatian:** generator selalu memakai baseline v3.4, bukan output terakhir, jadi tidak menumpuk efek. Ia **menimpa layer dan runtime PNG**; simpan backup jika telah menggambar manual langsung di file runtime. `bash tools/build_all.sh` menjalankan generator tahap 1–3 setelah data dan aset dasarnya dibuat.

### Hasil pengujian dan batasan

Uji visual `tools/test_world_redesign_stage3.py` memeriksa 656 file runtime tidak bertambah/hilang, tepat 5 peta + 36 prop dimodifikasi, alpha/ukuran prop identik, 25 layer valid, data collision/story/quest identik dan 86 audio sama persis. Pengujian logika headless melintasi kedua POV sampai epilog. **Ini bukan pengujian APK Android asli atau GPU**: Gradle/Android SDK masih dibutuhkan untuk build dan pengujian FPS, rendering alpha, RAM, interaksi/warping serta lifecycle audio langsung pada perangkat.
