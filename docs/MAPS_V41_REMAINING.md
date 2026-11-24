# v4.1 — 13 Remaining Map Art Pass + Landmark Upgrade

**Jenis perubahan:** peningkatan visual nyata 13 peta *lama* (sudah dalam game); tidak mengganti sembilan ilustrasi hand-crafted v4.0 milik pengguna. Ini art pass prosedural dengan landmark bergaya 16-bit, **belum** penggambaran ulang manual seluruh lingkungan setara map buatan ilustrator.

## Yang sudah dikerjakan

- 13 PNG background runtime disusun ulang dengan layer visual **terpisah dan bisa diedit** (mosaik plaza, tepian air, kelopak, pencahayaan magis, pola rasi bintang, detail lantai kafe, dll).
- 81 penempatan prop landmark diubah menggunakan 33 **prop type baru**; seluruhnya menggunakan sistem Y-sort `sort` bawaan atau layer `floor` asli prop.
- Sprite-landmark baru berasal dari satu atlas gambar pixel-art orisinal yang disimpan sebagai source di `art_source/world_v41/pixel_landmarks_atlas.png`; tidak bergantung pada URL runtime.
- Penggantian setiap prop mempertahankan `x`, `y`, `cw`, `ch`, dan `layer` lama. Ukuran map, spawn, door IDs, gerbang, air, wall/ellipse collision, NPC dan koordinat interaksi **tidak berubah**.
- Sembilan map desain khusus v4.0, 86 file audio, data cerita, misi, dan Memory Book dipertahankan identik dengan source v4.0.
- Satu ZIP berisi source, gambar, seluruh audio, dan alat edit. Tidak ada paket aset kedua.

## Tiga belas lokasi

| Map ID | Tema & visual baru | Penempatan prop dengan gambar baru |
|---|---|---:|
| `plaza` | Air mancur baru, rumah Arland/Sofia lebih detail, motif paving dan pohon sakura | 10 |
| `taman_kota` | Gazebo kayu, warna pepohonan sakura, bunga dan riak kolam | 9 |
| `riverside` | Perahu detail, willow tepian air, kilau sungai | 6 |
| `cafe` | Meja makan, display makanan dan counter kayu dengan finishing serta pencahayaan hangat | 6 |
| `memory_garden` | Gerbang bunga, shrine kristal, pepohonan kenangan dan kelopak | 5 |
| `lantern_field` | Sakura dan lentera festival, lingkaran pusat yang bercahaya | 7 |
| `star_path` | Kristal dan batu rasi bintang, pola bintang di tanah | 8 |
| `starfall_village` | Tiga rumah desa baru, pohon magis dan mosaik plaza | 5 |
| `eternal_garden` | Pohon harapan, gazebo, gerbang bunga dan cahaya hangat | 4 |
| `dermaga` | Perahu dan pohon willow, refleksi air di sekitar dermaga | 4 |
| `hutan_bisik` | Air terjun, pintu gua, willow dan detail flora hutan | 5 |
| `bukit_bintang` | Observatorium, teleskop, pohon sakura dan detail konstelasi | 5 |
| `gua_kristal` | Kristal cyan-violet yang lebih detail dan urat mineral bercahaya | 7 |

## Cara mengedit aset di VS Code

1. Semua prop PNG baru: `android/assets/props/v41_*.png`. PNG tersebut **benar-benar di-load** melalui `android/assets/data/props.json` dan dipakai di `maps.json`.
2. Source atlas PNG untuk revisi desain: `art_source/world_v41/pixel_landmarks_atlas.png`.
3. Overlay dekorasi tiap lokasi: `art_source/world_v41/editable_layers/<map_id>_atmosphere.png`. Ini layer transparan yang dikompositkan ke background runtime.
4. Baseline gambar v4.0 ada di `art_source/world_v41/baseline_maps/`; jangan menghapusnya, karena digunakan untuk regenerasi deterministik tanpa efek bertumpuk.
5. Ubah mapping, crop sprite, atau posisi prop yang dipilih di `tools/maps_v41_remaining.py`; jalankan `python3 tools/maps_v41_remaining.py` **setelah** `python3 tools/maps_v4_upgrade.py` dan generator naskah.
6. Untuk regenerasi penuh: `bash tools/build_all.sh`. Jika kamu mengedit output `android/assets/` secara langsung, copy desainnya ke `art_source/world_v41/` sebelum regenerasi agar tidak tertimpa.
7. Untuk memeriksa: `python3 tools/test_maps_v41_remaining.py && python3 tools/test_maps_v4.py && python3 tools/test_maps_v4_navigation.py && bash tools/test_logic.sh`.

**Penting:** `maps_v4_upgrade.py` dipertahankan untuk 9 map pertama dan `maps_v41_remaining.py` baru diaplikasikan setelahnya. Jangan membalik urutannya.

## Batasan grafis / collision

- Pembaruan visual ini memakai dimensi dan geometry dari 13 peta lama; tidak mengganti perspektif, kontur walkable, atau semua bangunan dengan file background yang dibuat manual seperti 9 peta v4.0.
- Prop bergambar baru memakai *footprint collision* lama. Karena siluet artistik baru mungkin lebih lebar, pengujian manual di layar dibutuhkan untuk menemukan clipping atau kaki karakter yang masuk ke tepi ornamen.
- Pratinjau `docs/preview/v41_thirteen_maps_runtime_composite.jpg` adalah komposit background+prop dari source, **bukan** screenshot gameplay emulator.
- Build APK Android asli, FPS, dan kejadian draw order saat runtime belum diverifikasi di HP. Hasil headless tidak setara tes perangkat.

