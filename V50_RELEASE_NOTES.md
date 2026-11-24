# Arland & Sofia: Our Little Universe — v5.0.0
## Cinematic Vertical World Overhaul | FULL ANDROID STUDIO SOURCE

Turunan langsung dari ZIP source v4.9.0, menggunakan engine LibGDX Java native.
**Bukan APK**; buka proyek `ArlandSofia/` di Android Studio, install Android SDK 36/JDK yang didukung, Gradle Sync, lalu build Android sesuai panduan `README.md`. Runtime game tetap offline.

### Fitur yang sudah diintegrasikan di source

- **21 lokasi map 2.5D** dengan pelataran bertingkat, tangga dari lantai bawah ke atas, foreground railing/occlusion, ketinggian visual karakter, collision sisi pelataran, dan ramp yang bisa dilalui. Ketinggian dan koordinat bisa diedit melalui `tools/v50_terraces.json`; gambar RGBA editable di `android/assets/maps/elevation/` (42 PNG).
- Sistem gerak pemain, pelacakan pendamping, NPC, kamera, dan bunyi langkah mempertimbangkan elevasi. Elevasi hanya visual/aturan gerak; posisi dunia, jalur cerita dan format save **tetap kompatibel schema 8**.
- **21 interaksi panorama opsional** di puncak tangga. Tiap panorama memiliki rangkaian camera shot, subtitle, efek partikel, audio cue, dan scene POV Arland/Sofia. **42 scene baru**, tujuh baris per route. Semua reward tercatat sebagai flag dalam slot yang sama, tidak mengubah canon ending.
- **11 titik cinematic** narasi yang sudah ada diperkaya dengan VFX baru tanpa menghapus arah kamera, musik, quest, atau cerita lama. **19 scene lama** diperluas dengan **38 baris dialog** tentang mendengar, memberi ruang, dan dua perspektif.
- VFX baru untuk cutscene: `mist`, `fireflies`, `aurora`, `rainlight`. Atmosfer berkilau di pelataran malam/magis memakai setting visualQuality yang sudah ada.
- **12 aset audio baru yang dibangun secara orisinal dan offline**: lima OGG score (plaza, hujan, bintang, masa depan, kafe), dua OGG ambience, dan lima WAV SFX (dua tangga, angin, shimmer, panorama). Semuanya diregistrasi di `SoundscapePlan`, audio game tetap menggunakan BGM + ambience + FX terpisah.
- Memory Book > Jelajah menampilkan progres **panorama** dan petunjuk lokasi tangga di samping penemuan v4.9.

### Batas dan hal yang dipertahankan

- 29 area asli, 157 node main quest, dua route Arland/Sofia, satu canon ending, desain karakter, semua aset dan data cerita v4.9 tetap ada. Semua konten panorama tambahan opsional dan tidak memblokir cerita utama.
- Fitur elevasi **2.5D**: masih game top-down, bukan engine 3D atau sistem lantai bebas bertumpuk. Pelataran menggunakan satu jalur tangga; ini tidak mengubah seluruh kontur 29 area menjadi terrain 3D.
- Aset PNG merupakan sumber editable asli; untuk mengubah bentuk tangga cukup edit `maps/elevation/v50_<area>_terrace.png` dan `..._front.png` dengan editor grafis. Perubahan footprint yang besar perlu penyesuaian `tools/v50_terraces.json` dan collision.
- `tools/v50_generate_vertical_world.py` membuat art/metadata dari sumber JSON, memerlukan Pillow **hanya pada PC developer**. Script story idempotent: `tools/v50_apply_cinematic_story.py`; script dialog: `tools/v50_expand_emotional_dialogue.py`. Proyek Android tidak memerlukan Python.
- Jangan menjalankan pipeline generator historis `tools/build_all.sh` untuk menimpa JSON shipped v5.0 sebelum penambahan v5.0 diintegrasikan ke pipeline. Data runtime v5 berada di `android/assets/data/`.

### Pemeriksaan yang selesai dan yang belum

- `bash tools/test_v50_release.sh`: pengujian Java headless (termasuk jalur menaiki/menuruni seluruh 21 tangga, penghalang sisi, 2 route, quest, save), compile stub UI/cutscene, layout tablet, tes NPC dan validasi aset/data.
- OGG Vorbis diperiksa dengan `ffprobe`, WAV dibaca sebagai PCM. ZIP penuh dicek CRC dan file lama yang tidak diedit dibandingkan terhadap v4.9.
- **Belum memverifikasi** kompilasi Android Gradle, APK, FPS di perangkat, handling GPU/tekstur, dan playtest sentuh pada HP/tablet nyata. Mesin audit ini tidak bisa mengunduh distribusi Gradle yang belum tersedia (DNS services.gradle.org tidak bisa diakses); pengguna tetap harus menjalankan build di Android Studio.

### Mulai

1. Ekstrak ZIP lalu buka folder `ArlandSofia` di Android Studio.
2. Pastikan JDK 17 atau 21 yang kompatibel dengan Gradle/AGP, SDK 36, dan koneksi hanya saat **setup build** untuk mengunduh dependency.
3. Gradle Sync, kemudian `gradlew.bat :android:assembleDebug` di Windows. APK debug biasanya di `android/build/outputs/apk/debug/`.
4. New Game route Arland atau Sofia; lanjutkan ke C02 untuk panorama awal. Di 21 area terpilih, dekati tangga dari bawah, naik, lalu tekan AKSI pada marker panorama.
5. Uji save, replay, compass, cutscene, tangga turun, landscape HP/tablet, dan airplane mode sejak pertama kali APK dijalankan.
