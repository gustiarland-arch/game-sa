# Panduan Karakter & World Graphics v4.6.2

## Atlas 8 arah (48×72 px per frame)

Folder `android/assets/characters/{arland,sofia}/`: `walk_8dir_v462.png` (768×576) dan `idle_8dir_v462.png` (384×576). Baris: **down, down-left, left, up-left, up, up-right, right, down-right**; 16 frame untuk jalan dan 8 untuk idle.

Baris diagonal dihasilkan dari ilustrasi 4 arah yang sudah ada dengan pergeseran piksel nearest-neighbor. Ini **bukan lukisan sprite diagonal manual**; untuk kualitas akhir setara game premium, edit baris diagonal langsung dengan Aseprite/LibreSprite. File PNG editable, atlas 4 arah/poses tetap sebagai cadangan. Setiap kali generator dijalankan, empat atlas v462 akan ditimpa; simpan hasil edit manual sebelum regenerate.

## Ekspresi & animasi

`Actor.java`: aturan facing 8 arah saat bergerak, 16 fase jalan, 8 idle, gelombang langkah, campuran gerak yang tidak bergantung FPS, dan gestur kosmetik `shy`, `excited`, `ponder`. Cutscene lama tetap memakai animasi pose asal dan arah kardinal; schema save tidak diubah. Reaksi companion memanfaatkan afeksi dari sistem yang sudah ada.

## Profil lingkungan — 22 area

`WorldAtmosphereV462.java` menyediakan enam kategori: HOME, CITY, GARDEN, WATER, STAR, CAVE. Pemetaan: HOME (`arland_room`, `sofia_room`, `cafe`, `dapur`, `toko_bunga`, `arcade`, `perpustakaan`, `ruang_arsip`), CITY (`plaza`, `jalan_kota`, `perumahan`), GARDEN (`taman_kota`, `memory_garden`, `eternal_garden`, `hutan_bisik`), WATER (`riverside`, `dermaga`), STAR (`lantern_field`, `star_path`, `starfall_village`, `bukit_bintang`), CAVE (`gua_kristal`).

Lapisan belakang berupa kabut, berkas matahari; foreground berisi kelopak, daun, kunang-kunang, dan tetesan hujan; air memiliki glint tambahan. Efek aktif mengikuti jam/cuaca dan dimatikan pada visualQuality=0, minimal pada preset 1, lengkap pada preset 2. Ke-22 PNG map tidak diubah agar collision, spawn, pintu, quest dan save tetap aman.

FX editable di `android/assets/fx/v462_*.png` (tujuh berkas). Ubah PNG secara langsung atau edit kode Pillow di `tools/gen_visual_v462.py`. Generator dapat dijalankan dari root proyek: `python3 tools/gen_visual_v462.py`.

## Pengujian

`bash tools/test_visual_v462.sh` memverifikasi delapan arah, waktu animasi, kualitas grafis, 22 profil, dan ukuran PNG. `bash tools/test_visual_fx.sh` mengompilasi renderer WorldFx terhadap stub LibGDX; ini **bukan** pengujian FPS atau render GPU Android. Wajib uji HP/tablet Android sebelum mengklaim bebas bug.

Tidak ada perubahan pada naskah canon ending, dua route, sistem simpan, 22 map asli, atau audio.
