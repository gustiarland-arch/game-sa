# Arland & Sofia v3.6 — World Redesign Tahap 4 + Safe Cleanup

## Implementasi visual nyata

Ini tahap akhir dari *art pass bertahap*, bukan klaim bahwa kualitas artwork telah menyamai game referensi komersial. Semua perubahan berada pada PNG yang benar-benar dimuat engine, dengan **nama aset yang sama** sehingga tidak perlu perubahan map collision, JSON, maupun Java renderer.

| Map | Arah desain | Keterangan |
|---|---|---|
| `jalan_kota` | Batu pedestrian, pola penyeberangan, tanaman | Lalu lintas dekoratif, tidak mengubah jalan yang bisa dilalui |
| `perumahan` | Jalan lingkungan, hamparan hijau, mandala paving | Fasad prop rumah juga diperhalus |
| `perpustakaan` | Parket klasik, simbol buku, cahaya keemasan | Ornamen rak dan meja baca |
| `arcade` | Lantai neon, medallion elektronik, layar berkilau | Detail mesin permainan dan photobooth |
| `toko_bunga` | Material terakota, pola flora, dinding mint | Rak dan bucket bunga lebih berkarakter |
| `arland_room` | Ruang biru-hangat, motif bintang, lantai kayu | Furnitur dan meja lebih detail |
| `sofia_room` | Ruang blush-pink, aksen bunga dan hati | Tempat tidur, meja dan lemari mendapat finishing baru |
| `dapur` | Keramik vintage, pola enkustik, pencahayaan hangat | Furnitur dapur dipoles |
| `ruang_arsip` | Lantai mistis violet, simbol arsip, ornamen logam | Rak, pedestal, dan cahaya magis |

Terdapat **9 peta baru dalam bentuk PNG runtime**, **57 prop direvisi**, **36 layer RGBA transparan** (`00_color_art_direction`, `01_new_materials`, `02_signature_environment`, `03_soft_light`), dan **66 baseline** aset v3.5 yang menjamin hasil dapat diregenerasi tanpa menumpuk filter.

Semua 22 peta sudah menerima visual pass tersendiri sejak v3.3–v3.6; perbaikan artistik tingkat studio masih dibutuhkan. Ilustrasi perbandingan dari *source asset composite* ada di `docs/preview/v36_stage4_before_after.jpg`. Ini **bukan screenshot emulator**.

## Mengedit di VS Code dan meregenerasi

- PNG runtime: `android/assets/maps/` dan `android/assets/props/`.
- Layer yang dapat diedit per peta: `art_source/world_stage4/editable_layers/<map>/`.
- Gambar baseline v3.5: `art_source/world_stage4/v35_unmodified/`.
- Generator: `python3 tools/world_redesign_stage4.py` dari root project; membutuhkan Python, Pillow, NumPy.
- Preview aktual: `python3 tools/preview_world_stage4.py`.
- Tes visual dan konservasi data: `python3 tools/test_world_redesign_stage4.py`.

Jika mengubah PNG hasil runtime secara manual, menjalankan generator lagi akan **menghasilkan ulang dari baseline** dan menimpa edit runtime. Lakukan kustomisasi pada generator/layer yang disimpan, atau simpan PNG manual Anda sebelum regenerasi.

## Pembersihan sampah aman

**Tidak ada penghapusan dari `android/assets`, `core/src`, `android/res`, `gradle`, `art_source`, `tools/build` atau audio.** Delapan file pratinjau historis tanpa referensi dokumen/tool serta satu `__pycache__` yang sempat terbentuk selama pembuatan source berhasil dikeluarkan dari ZIP. Total **9 file, 5.293.387 byte**. Daftar beserta checksum ada di `docs/CLEANUP_AUDIT_V3.6.json`.

Penting: baseline tahap 1/2/3/4 memang tampak duplikat, tetapi **diperlukan** oleh generator dan validasi art pass berurutan; jangan hapus. Sama halnya dengan Java test stubs, hasil data generator dan file Gradle wrapper. Script `tools/clean_project_v36.py` memakai *dry-run* secara default dan hanya boleh menghapus daftar file non-runtime atau cache standar bila `--apply` diberikan.

## Jaminan dan batasan QA

- Hash 656 berkas runtime v3.5 dibanding v3.6; hanya 9 background dan 57 prop yang berubah. Nama path runtime sama seluruhnya.
- Setiap prop yang diperbarui memiliki ukuran dan *alpha footprint* identik dengan v3.5; ini **bukan** jaminan collision bergerak sukses pada perangkat, karena renderer Android belum diuji.
- JSON lokasi dan collision, naskah, quest, Memory Book, serta 86 file audio dibanding hash dan tidak berubah.
- Tes logika, image decode, script cleanup, dan regenerasi source harus lulus sebelum packaging.
- **Belum boleh diklaim siap rilis** sampai APK Android berhasil dibangun dan lulus QA renderer, kontrol, save, audio, native 16 KB, dan FPS pada perangkat nyata. Riwayat build yang gagal hanya menunjukkan masalah dependensi/lisensi SDK, bukan bukti kode pasti bebas error.
