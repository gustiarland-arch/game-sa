# v2.3 — Living World & Pixel-Art Polish

## Sumber dan ruang lingkup

- **Sumber**: ZIP source v2.2.0. Tidak merombak engine Java/LibGDX, quest, dua route, atau story canon.
- **Output grafis**: 22 `android/assets/maps/*.png` diberi 8.471 microdetail piksel. Dunia tetap 22 area yang sama, tidak ada pintu/prop solid baru.
- **Generator**: `tools/polish_world_v23.py` membaca `tools/build/maps_base.json`. Seed SHA-256 per ID map untuk hasil deterministik. Memakai masker warna sederhana (rumput, dunia bintang, gua, interior), menghindari area spawn, pintu dan anchors. Metadata PNG `world_polish_v23=1` menjadikan script aman dijalankan berulang pada input yang sudah dipoles.
- **Jika ingin reset ke dasar**: jalankan `python3 tools/build_maps.py`, lalu `python3 tools/polish_world_v23.py android/assets`, lalu `python3 tools/build_content.py` untuk regenerasi data quest/map. Jangan jalankan `build_maps.py` saja bila ingin mempertahankan lapisan dekorasi v2.3.

## Rendering

- `screens/GameScreen.java`: culling prop sudah dilakukan sebelum daftar depth-sort dibangun. Preset kualitas tertinggi memakai cached `TextureRegion` untuk menggerakkan bagian atas pohon, dengan batang tetap diam. Mode Seimbang dan Hemat menampilkan pohon statis.
- `game/WorldFx.java`: `drawSceneAtmosphere()` menambah butiran cahaya dengan intensitas berbeda untuk gua, arsip, taman, dan dunia bintang; tidak mengalokasikan array per frame.
- `game/Actor.java` + `Assets.java`: pose `read`, `water`, `sweep` (baris 13–15, indeks nol) ditambahkan di akhir daftar pose; pose lama tetap pada indeks sebelumnya. `GameScreen.npcIdleActivity()` memilih pose berdasarkan NPC.

## Pratinjau

Jalankan `python3 tools/preview_world_v23.py` untuk membuat `docs/preview/v23_world_asset_preview.png` (komposit dari texture peta dan props; bukan hasil menjalankan Android). Preview tidak menampilkan actor, animasi, cuaca, atau UI. Animasi pohon dapat dilihat setelah source berhasil dibuild sebagai APK.

## Validasi

```bash
python3 tools/test_world_v23.py
python3 tools/test_couple_v22.py
python3 tools/test_visual_v21.py android/assets
bash tools/test_visual_fx.sh
bash tools/test_romance_ui.sh
bash tools/test_logic.sh
./gradlew :android:assembleDebug
```

Opsional perbandingan 22 peta dengan versi sebelumnya: `python3 tools/test_world_v23.py --baseline /path/to/ArlandSofia_Native_Android_v2.2.0_source.zip`.

> **Catatan status:** uji data, JPEG/PNG, pose, input stub, dan parser sintaks Java bukan uji build Android asli. Gradle wrapper belum dapat mengunduh Gradle 8.11.1 di lingkungan pembuatan ini. Lakukan build melalui Android Studio/JDK 17 + internet pada mesin Anda atau GitHub Actions, kemudian cek rendering/performa pada perangkat.

## Cara edit lewat VS Code

- Warna, motif, distribusi dekorasi: `tools/polish_world_v23.py` dan file gambar `android/assets/maps/*.png`.
- Animasi NPC: `tools/gen_poses.py`; ubah daftar nama pose dengan urutan sama pada `Assets.POSES`.
- Efek atmosfer: `core/src/main/java/com/arlandsofia/olu/game/WorldFx.java`.
- Kualitas dan pemilihan gerak kanopi: `screens/GameScreen.java`.
- Agar hasil PNG manual tidak tertimpa, jangan langsung jalankan `tools/build_all.sh` setelah mengedit file aset final tanpa menyimpan hasil edit sebagai sumber baru.
