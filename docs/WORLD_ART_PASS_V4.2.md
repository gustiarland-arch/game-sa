# Arland & Sofia — v4.2 World Art Direction & Sprite Matte Cleanup

## Status dan batasan

Ini adalah **art pass komposit/ilustrasi prosedural terarah terhadap 13 latar v4.1**, bukan redraw manual penuh yang identik dengan kualitas sembilan ilustrasi map v4.0. Perubahan v4.2 benar-benar terpasang pada PNG runtime, bukan sekadar mockup. Nine map v4.0 yang berasal dari unggahan asli tidak diubah.

Tidak ada perubahan world bounds, collision, titik spawn, portal, NPC, quest, ataupun save schema. Semua audio lama dipertahankan.

## Apa yang dikerjakan

| Map | Identitas ilustrasi v4.2 | Materi yang digarap |
|---|---|---|
| Plaza Kota | Hearth of the City | Mandala batu di tengah plaza, ornamen cobblestone, festival lights |
| Taman Kota | Blossom Pavilion | Riak/teratai di kolam, kelopak, aksen tepian tanaman |
| Riverside | Blue Riverbank | Kilau air, sapuan buih pantai, lampu gantung |
| Dermaga | Lighthouse Pier | Sambungan papan dermaga, kilau air, lampu gantung |
| Kafe Senja | Sunset Parlour | Bingkai jendela, pola lantai parket, cahaya masuk, inlay kayu |
| Bukit Bintang | Celestial Overlook | Kompas observatorium, titik rasi bintang dan efek debu cahaya |
| Memory Garden | Garden of Recollections | Mandala kenangan, kelopak dan lingkaran magis |
| Eternal Garden | Garden of Promises | Ukiran tangga ke pohon harapan, mandala bunga |
| Star Path | Road Between Stars | Lentera dan aksen jalan galaksi |
| Starfall Village | Lantern Village | Ornamen alun-alun, pola cahaya dan desa |
| Lantern Field | Festival of Wishes | Pola lantai festival dan untaian lentera |
| Hutan Bisik | Whispering Canopy | Aksen air terjun/sungai, dedaunan dan cahaya kunang-kunang |
| Gua Kristal | Crystal Reverie | Mandala kristal, retakan bercahaya dan pantulan mineral |

**Perbaikan nyata yang penting:** 33 sprite landmark hasil crop atlas lama masih membawa matte putih/pucat. v4.2 menghilangkan matte tersebut sehingga tidak lagi tampak seperti gambar persegi di atas tanah. Dimensi gambar, ID sprite, collision footprint (`cw`, `ch`), serta layer rendering tidak berubah.

## Lokasi aset dan cara edit dengan VS Code

- Runtime: `android/assets/maps/<map_id>.png` (13 PNG yang sudah dikomposit). 
- Runtime prop: `android/assets/props/v41_*.png` (33 sprite dibersihkan transparansinya).
- Baseline sebelum update: `art_source/world_v42/baseline_maps/` dan `art_source/world_v42/baseline_props/`.
- Layer yang dapat diedit per lokasi: `art_source/world_v42/editable_layers/<map_id>_material.png`, `_scenery.png`, `_illumination.png` (masing-masing RGBA resolusi native).
- `tools/world_repaint_v42.py`: generator dari baseline v4.1 yang deterministik, menggunakan Pillow dan numpy.
- `tools/clean_landmark_alpha_v42.py`: alpha cleanup; hanya Pillow dan numpy, tanpa SciPy.
- `docs/V42_WORLD_MANIFEST.json`: ukuran, jalur layer, hash runtime yang dapat diverifikasi.
- `docs/V42_ASSET_DIFF.json`: daftar file yang benar-benar berubah serta metrik per map.
- `docs/V42_BASELINE_AUDIT.json`: hash data, 9 map handcrafted dan seluruh audio sebagai pembanding.

Untuk regenerasi gambar v4.2 dari baseline: `python3 tools/world_repaint_v42.py && python3 tools/clean_landmark_alpha_v42.py`. Jika mengedit PNG runtime langsung, **jangan jalankan generator**, karena gambar runtime akan kembali mengikuti baseline+layer generator. Edit file `art_source` atau generator untuk desain permanen.

Untuk memverifikasi tanpa menimpa aset: `python3 tools/test_v42_world.py`, `python3 tools/world_repaint_v42.py --verify-only`, dan `python3 tools/clean_landmark_alpha_v42.py --verify`.

Bila menjalankan `tools/build_all.sh`, pipeline berjalan dari pembuatan v3.x sampai perombakan sembilan map v4, komposit v4.1, kemudian art pass v4.2. Backup baseline tidak boleh dihapus sebagai "file sampah", karena generator memerlukannya untuk menjaga hasil yang tidak menumpuk lapisan secara berulang.

## Uji dan batasan sebelum rilis

- `tools/test_v42_world.py`: memeriksa tepat 13 map tergambar, 39 layer, 9 map handcrafted identik, 33 sprite dengan alpha yang tidak membesar, seluruh data dan audio lama identik.
- `tools/test_maps_v4.py`, `tools/test_maps_v41_remaining.py`, `tools/test_maps_v4_navigation.py`: memeriksa map/portal/navigasi.
- `LogicSelfTest` secara headless: kedua route dan sistem lama.
- **APK Android asli dan render GPU belum diverifikasi.** Uji pada perangkat tetap wajib sebelum rilis.
- Untuk mencapai kualitas yang benar-benar setara 9 map handcrafted, masih diperlukan penggambaran ulang ilustrasi yang lebih mendalam, penempatan furnitur/struktur baru dan, bila geometri berubah, pembaruan collision + navigasi yang diuji ulang.
