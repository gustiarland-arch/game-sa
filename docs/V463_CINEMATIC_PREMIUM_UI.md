# v4.6.3 — Cinematic Cutscene 2.0 & Premium UI/UX 2.0

**Jenis rilis:** source lengkap untuk Android Studio (belum dinyatakan APK production-ready).  
**Basis:** v4.6.2 Character & World Overhaul.  
**Batas perubahan:** source UI, algoritma kamera/cutscene, dan lima perintah kamera pada data quest. Seluruh map, audio, sprite, collision, cerita, route, dan save lama tetap dipertahankan.

## Cinematic Cutscene 2.0

Perubahan benar-benar terintegrasi pada `CutscenePlayer.java`:

- Kamera mengikuti tween halus berbasis durasi dan easing yang sama pada refresh rate berbeda.
- `shot` baru mendukung fokus `player`, `partner`, atau `couple`, dengan framing `wide`, `intimate`, `close`, serta parameter zoom manual. Titik tengah pasangan dihitung dari dua aktor saat keduanya tersedia.
- Arah zoom mengikuti implementasi yang benar pada `GameScreen` (`worldCam.zoom = 1 / cine.zoom()`): nilai di atas satu memperbesar gambar.
- Zoom, waktu animasi, jumlah partikel, dan kecepatan gerakan diberi batas yang aman. Titik gerakan yang tidak lengkap diabaikan, bukan crash.
- Transisi `fade` dan kamera menggunakan easing yang lebih lembut; follow kamera dan pemulihan setelah cutscene menggunakan damping frame-rate independent.
- Caption ribbon mengikuti lebar layar, dengan ornamen/letterbox pixel-art lama. Tidak mengganti satu pun adegan, flag, ending, atau musik.
- Lima adegan kanonis menggunakan `shot`: `C01_PIER`, `C04_V26_VOW`, `C05_V26_NIGHT_TALK`, `C06_Q_REVEAL`, dan `EPI_FEST_LEPAS`. Hanya perintah `cam` terakhir yang mengikuti player dalam masing-masing scene yang diubah, tanpa urutan dialog, tindakan quest, atau durasi aslinya diubah.
- Bila konten quest diregenerasi oleh `tools/build_content.py`, jalankan `python3 tools/apply_v463_cinematic.py`; perintah tersebut sekarang juga tercantum di `tools/build_all.sh`.

## Premium UI/UX 2.0

- Geometri responsif baru `PremiumLayoutV463.java`: panel dialog, kontrol riwayat/lewati, serta maksimal delapan pilihan, dengan dua kolom ketika ruang memadai. Memperhitungkan inset aman kiri, kanan, dan bawah.
- `DialogBox`: label jawaban bernomor, navigasi D-pad/keyboard dengan highlight, Enter untuk memilih, teks responsif dan portrait yang ukurannya dibatasi agar tidak menutupi dialog.
- Input touch pointer ditangkap per interaksi. Jari kedua tidak boleh mengambil alih tombol atau melewati dialog tanpa sengaja; touch-cancel membersihkan pointer yang aktif.
- `Ui.button`: aksen dan bayangan halus, fokus lebih jelas, tulisan otomatis diperkecil saat terlalu panjang. Tetap menggunakan NinePatch/aset UI asli yang dapat diedit.
- `BaseScreen`: transisi fade cepat untuk menu, secara otomatis dikurangi ketika kualitas visual rendah.
- `TitleScreen`: keterangan save dipindahkan ke panel terpisah di atas grid tombol agar tidak menumpuk tombol pada perangkat landscape atau tablet.
- `RouteSelectScreen`: penegasan bingkai kartu dan warna tiap protagonis.
- `SlotScreen`: header slot dan judul tujuan diatur agar tidak melewati tepi kartu.

## Pengujian yang berhasil

- `bash tools/test_v463_cinematic_ui.sh`: 7 runtime camera smoke assertions dan 859 geometry/motion checks.
- `bash tools/test_v30_ui_compile.sh`: DialogBox dan overlay di-typecheck terhadap stub LibGDX.
- `bash tools/test_romance_v46.sh`: 51 assertions.
- `bash tools/test_living_world_v46.sh`: 12 assertions.
- `bash tools/test_tablet_v44.sh`: 390 layout checks.
- `bash tools/test_controls_v28.sh`: 750 input checks; disertai 126 settings checks.
- `python3 tools/test_story_v26.py`: 395 pemeriksaan cerita dan route.
- `python3 tools/test_maps_v4_navigation.py`: 131 navigation checks.
- `python3 tools/test_visual_v462.py`: 22 map profiles, 4 hero sprite atlases, 7 atmosphere FX.
- `python3 tools/test_cinema_v25.py`: 93 pemeriksaan sinematik/audio.
- `bash tools/test_maps_v4_save.sh`: 38 pemeriksaan migrasi save.
- `java JavaSyntaxCheck`: semua 65 file Java runtime diparse untuk Java 11.

## Keterbatasan yang harus dinyatakan

- Test `tools/test_logic.sh` tidak dapat dilanjutkan karena `tools/build/anchors.json` tidak ada dalam source ZIP baseline; **bukan** hasil test lulus.
- Belum ada verifikasi `:android:assembleDebug`, OpenGL, FPS, kompatibilitas GPU, maupun seluruh gameplay sampai ending pada perangkat Android. Pengujian headless dan stub tidak menjamin hasil akhir di HP/tablet.
- Aset baru dalam update ini bersifat **algoritma/komposisi UI**, bukan redesign ilustrasi cutscene atau penggantian sprite karakter dengan gambar baru.

**Prinsip:** kedua route, satu canon ending, cerita, map 22 area, audio, save schema, dan aset artistik lama tetap utuh. Folder grafis/aset dapat diedit dengan IDE sesuai struktur semula.
