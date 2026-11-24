# Arland & Sofia — v5.1.0 Natural Environment Remaster

**Jenis paket:** satu ZIP source Android Studio lengkap, bukan patch/APK. Turunan source v5.0.0.

## Yang dibenahi

- **21 penempatan elevasi diperiksa ulang:** tidak lagi dipilih semata karena area kosong; koordinat dipandu oleh jalur, pelataran, jalan kota, pantai, atau ruang interior yang tergambar pada PNG map asli.
- **21 tangga tetap berfungsi sebagai jalur naik-turun:** collision dan pembatas tepi memakai `ElevationV50.canStep`, actor lift dan foreground depth. Jenis material berbeda untuk batu, kayu, kafe, hutan, dunia memori.
- **96 PNG orisinal baru:** 21 lantai platform, 21 foreground tepi/railing, 21 approach path, dan 33 aset prop independen (bangku, lampu, pot bunga, batu, railing, dinding tebing, jembatan, ramp, fountain, papan, pilar, dll.).
- **Seluruh 29 area mendapat dekorasi** dan daftar prop di data map; ada 194 penempatan prop baru, termasuk 21 jalur penghubung.
- **21 panorama v5.0 tetap interaktif**, lokasi penandanya mengikuti posisi pelataran baru. Source `story.json`, musik/SFX, dan save schema 8 dipertahankan.
- **Masalah nyata yang ditemukan:** jalur tangga Star Path memotong prop batu, dekorasi awal perpustakaan memotong titik jadwal Bu Laras. Keduanya dipindahkan dan pengujian diulang.

## 21 area — alasan penempatan

| Area | Konsep integrasi | Koordinat kiri-atas |
|---|---|---|
| `plaza` | Plaza sisi utara — pelataran panggung menghadap lingkaran utama | (765, 450) |
| `jalan_kota` | Beranda toko di sisi jalur pedestrian | (545, 305) |
| `taman_kota` | Teras pemandang di luar lengkung jalan danau | (1085, 355) |
| `riverside` | Dek menghadap danau, akses dari jalan tepi air | (1060, 490) |
| `cafe` | Panggung pertunjukan di sisi belakang ruang kafe | (625, 345) |
| `toko_bunga` | Podium buket di dekat counter bunga | (745, 280) |
| `arcade` | Panggung hadiah di depan deretan mesin | (550, 225) |
| `memory_garden` | Teras Memory Garden — ujung tangga menyentuh cabang jalur timur | (1005, 555) |
| `lantern_field` | Dek lentera menuju lingkaran cahaya | (845, 340) |
| `star_path` | Observatorium Star Path — pangkal tangga tepat pada jalur zig-zag bercahaya | (1155, 390) |
| `starfall_village` | Teras terhubung jalan utama desa | (985, 470) |
| `eternal_garden` | Pijakan sisi selatan lingkar taman akhir | (915, 545) |
| `perumahan` | Beranda rumah menyambung trotoar | (935, 315) |
| `perpustakaan` | Mezanin kecil di sisi rak buku | (640, 370) |
| `dermaga` | Teras kayu dari jalan menuju tepi danau | (895, 225) |
| `hutan_bisik` | Panggung akar dekat persimpangan jalur hutan | (1095, 765) |
| `bukit_bintang` | Pelataran pandang di sisi jalur observatorium | (995, 560) |
| `gua_kristal` | Pelataran batu di tepi jalur kristal | (765, 270) |
| `galeri_komunitas` | Podium karya seni di jalur galeri | (350, 185) |
| `rain_garden` | Jembatan batu di jalur cahaya Rain Garden | (1205, 455) |
| `hall_of_tomorrow` | Balkon ruang masa depan yang terhubung lorong | (910, 530) |

## Edit aset sendiri

- Gambar struktur: `android/assets/maps/environment_v51/*.png`
- Semua dekorasi: `android/assets/props/environment_v51/*.png`
- Template lokasi dan alasan desain: `tools/v51_environment_sites.json`
- Prop rendering dan collision: `android/assets/data/props.json`
- Penempatan pada map: `android/assets/data/maps.json`
- Untuk membuat ulang PNG + metadata setelah mengedit posisi: `python3 tools/v51_environment_overhaul.py` (butuh Pillow di PC; bukan di APK)
- Untuk melihat komposit perubahan tanpa menjalankan game: `python3 tools/v51_preview_comparison.py`
- Setelah edit, selalu jalankan `bash tools/test_v51_release.sh`. Jangan jalankan generator v5.0 lama karena akan mengembalikan letak tangga awal.

## Bukti uji yang dilakukan

- `bash tools/test_logic.sh`: **40.477** pemeriksaan lulus, mencakup eksplorasi dua route, rute tangga, collision, save, quest, story, NPC berjadwal.
- `python3 tools/test_v51_environment.py`: **1.365** validasi konten + seluruh aset PNG baru dan penempatannya.
- `python3 tools/test_v50_content.py`: **335** validasi konten kompatibilitas v5.0.
- Uji UI/cutscene v3.0 dan v4.6.3 serta layout tablet: lulus; layout tablet **390** pemeriksaan.
- **Belum dilakukan:** build APK Gradle, jalan di HP/tablet fisik, benchmark FPS, uji ergonomi tangga dengan joystick, dan inspeksi setiap sudut peta saat gameplay. Preview adalah komposit PNG, bukan screenshot APK.

## Batas desain

Ini game top-down **2.5D**, bukan 3D berbasis mesh. Platform yang tampak lebih tinggi memakai lift sprite, dinding penahan, railing dan pembatas collision. Detail relief lingkungan sekarang lebih beragam, tetapi peta datar dasar masih dipakai; pemolesan manual artis tetap diperlukan untuk 1:1 kelihatan organik pada seluruh potongan peta.

**Satu canon ending, dua route, semua aset lama, dan data save tidak dihapus.**
