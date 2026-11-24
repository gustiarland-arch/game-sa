# v5.2.0 — Full-World Navigation, Camera & Collision Repair

**Sumber:** v5.1.0 Natural Environment Remaster (seluruh proyek LibGDX/Android Studio).  
**Jenis rilis:** perbaikan menyeluruh navigasi/komposisi kamera, **bukan** repaint ulang seluruh background pixel-art.

## Masalah yang ditemukan

- Kamera eksplorasi `640×360` membuat furnitur dan properti dunia tampak terlalu dominan, terutama pada ruangan awal.
- Petunjuk kompas lama menunjukkan arah garis lurus yang dapat menerobos furnitur, pagar, atau dinding.
- Data v5.1 memasukkan 4 dekorasi bertema luar ruang ke **masing-masing kamar** protagonis; beberapa area lain memiliki dekorasi yang tidak sesuai tema.
- Audit grid konservatif menemukan **7 titik interaksi** yang sulit/tidak dapat dijangkau dari spawn utama dan **1 koordinat pendaratan pintu galeri → kafe** di dalam collision properti.
- Pergerakan sebelumnya mengecek target dan midpoint terbatas; lintasan karakter bisa melalui objek tipis jika frame delta tinggi.

## Perbaikan yang diterapkan

1. **29/29 area diaudit:** skema peta, spawn, tujuan pintu, semua quest dan side interaksi; area dengan masalah diperbaiki sesuai tempatnya. Tidak menambah lorong pintas palsu.
2. **Zoom gameplay lebih masuk akal:** world viewport `760×428`, dengan skala eksplorasi default *Seimbang* (`1.20x`, `1.254x` untuk interior). Preset *Dekat*, *Seimbang*, *Lebar* pada Pengaturan → Tampilan. UI/hitbox sentuh tidak diperkecil. Zoom cutscene tetap diatur terpisah.
3. **Petunjuk jalur aman:** pathfinding A* mencari jalan mengitari collision nyata dan elevasi; mengubah petunjuk dari garis lurus menjadi "Jalur" saat perlu memutar. Dihitung paling sering setiap 0,65 detik, bukan per frame.
4. **Pemulihan posisi:** save lama, posisi datang dari pintu, dan jadwal NPC yang bertabrakan dengan properti dicari posisi berdiri terdekat yang legal. Save schema **8** tetap sama.
5. **Swept collision:** gerakan pemain, NPC dan pendamping mengecek lintasan, termasuk obstacle tipis. Tidak ada perpindahan otomatis menembus furnitur.
6. **Penataan lingkungan:** 4 dekorasi yang salah tema dikeluarkan dari masing-masing kamar; beberapa dekorasi lain di interior serta banner kafe dari alam fantasi dibersihkan. Aset lama tetap disimpan agar dapat diedit kembali. Seluruh **21 pelataran/tangga yang ada di v5.1 dipertahankan**.
7. **Tujuh interaksi dikoreksi:** dua di Taman Kota, dua di Tepi Danau (epilog), tiga di Toko Bunga. Sprite penanda objek yang terkait digeser bersama pemicunya tanpa mengubah naskah, quest flag, ending, atau sistem reward.
8. **Pintu galeri → kafe:** landing `480,350` menggantikan titik lama yang tertutup etalase.

## QA yang dapat direproduksi

Jalankan `bash tools/test_v52_release.sh` pada lingkungan dengan JDK 11+ dan Python 3. Untuk pemeriksaan aset v5.0/v5.1 tersedia Pillow. Pemeriksaan keseluruhan meliputi:

- **40.445 pemeriksaan logika**: kedua route, cerita, save/replay, quest, mini-game, waktu dan NPC.
- **588 pemeriksaan akses statis**: 29 map, ratusan interaksi dan 51 tujuan pintu; tidak ada titik tidak terjangkau pada model grid 16-pixel dari spawn utama.
- **20 pemeriksaan kamera/navigasi Java**: termasuk rute ponsel pertama pada kedua karakter dan save pengaturan lama.
- **138 pemeriksaan UI Pengaturan**, **390 pemeriksaan layout tablet**, **859 pemeriksaan UI/cinematic**.
- **335 validasi konten elevasi v5.0** dan **1.269 validasi lingkungan/aset v5.1**.

**Batasan penting:** grid pemeriksaan statis merupakan pendekatan konservatif, bukan bukti semua rute per jam/cuaca/flag sudah diuji pada perangkat. Tidak ada build APK, simulasi render GL, atau playtest fisik yang berhasil dalam lingkungan ini karena distribusi Gradle/Android SDK tidak tersedia secara offline. Skrip `gradlew` akan memerlukan Android Studio/SDK/Gradle yang tersedia pada PC developer. Video/preview map hanya untuk diagnosis, bukan bukti gameplay v5.2 sudah berjalan pada perangkat.

## Kompatibilitas dan aset

- Project tetap native LibGDX, 100% offline saat runtime, tanpa fitur jaringan tambahan.
- Save schema 8 dan ID route/step/canon scene dipertahankan; pengaturan baru `cameraDistance` memiliki nilai default untuk settings.json lama.
- Semua PNG, OGG, WAV, font, dan aset v5.1 tetap disertakan. Tidak menghapus asset penting atau mengubah texture sumber.
- Konten dapat diedit dalam `android/assets/data/maps.json`, `quests.json`, `props.json` dan `core/src/main/java/com/arlandsofia/olu/`.
- Jangan jalankan generator map lama tanpa meninjau perubahan v5.2, karena dapat mengembalikan koordinat collision/quest yang sudah diperbaiki.

## Pengujian perangkat yang masih perlu

Mulai route Sofia dan Arland dari New Game, ikuti petunjuk ponsel, jalan mengitari furnitur, masuk/keluar galeri dan kafe, lanjutkan quest di Taman Kota serta epilog Tepi Danau. Uji joystick multi-touch, pause/resume, Android landscape dan tablet dengan berbagai aspect ratio, save lama, serta performa pathfinding saat bergerak di hutan/bukit. Catat area dan waktu jika masih ada benda yang bertumpuk.
