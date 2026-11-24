# v4.3.0 — QA & release status

## Fitur implementasi

1. Four-area art pass: Plaza Kota, Taman Kota, Kafe Senja, Riverside; world bounds dan collision **tidak diubah**.
2. 20 varian prop terpisah; 59 instance menggunakan sprite v4.3 dengan anchor/hitbox asli.
3. 16 layer RGBA dan 4 baseline map di `art_source/world_v43`; generator deterministik.
4. Android tablet: menu utama, route cards, pause, joystick dan cover-image memperhatikan rasio/safe inset.
5. Metadata 4.3 dan GitHub Actions diperbarui; audio tidak dipisahkan, tetap satu ZIP.

## Pemeriksaan yang dilakukan

- Logika story & gameplay: 24.686 checks (dua route, epilog, quest, minigame, ekonomi, romansa).
- Tablet UI model: 312 asersi pada 6 profil rasio/inset (16:9, 16:10, 4:3, ultrawide).
- World asset/geometry: 1.036 checks, 18 peta lain, 86 aset audio tetap identik.
- History map v4: 302, navigasi 131, v4.1 regression 5.247, v4.2 regression 667.
- Controls: 750, Settings: 126, input romansa smoke lulus.
- Java 11 parse: 57 file lulus; **parse dan stub tests bukan kompilasi Android/LibGDX yang sesungguhnya**.
- Regenerasi: 26 aset/data file diulang, hash konsisten.

## Batasan sebelum publikasi

- `./gradlew :android:assembleDebug --offline` tetap mencoba Gradle 8.11.1 dan gagal `UnknownHostException: services.gradle.org`; belum ada APK dari v4.3.
- Jangan menyebut sudah diuji di tablet. Perlu uji nyata 8–12 inci: 16:10, 4:3, notch, resize, multitouch, input UI, scaling teks serta FPS.
- Pembaruan visual ini adalah art-pass yang terpasang pada source, **belum penggambaran ulang manual lengkap layout bergaya Sea of Stars**.
- Permintaan layar tablet ditargetkan pada **landscape**; layar portrait dan foldable tabletop perlu pengujian tersendiri.
- Dokumentasi `docs/ANDROID_TABLET_V4.3.md` dan `docs/WORLD_REDESIGN_V4.3.md`.
