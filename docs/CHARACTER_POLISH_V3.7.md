# v3.7.0 — Character Motion & Visual Depth (tahap 5)

**Status:** perubahan source dan assets terpasang; validasi headless lulus; belum ada bukti rendering GPU/APK Android. Game **tidak diklaim siap rilis**.

## Apa yang berubah

1. **50 atlas karakter baru** (`walk_v37.png`, `idle_v37.png`) untuk **25 karakter**, setiap atlas memiliki 4 arah; walk 16 fase/arah, idle 8 fase/arah, dari sumber `walk_v32.png` dan `idle_v32.png`. Ini variasi dan retiming pixel-level prosedural, **bukan spritesheet yang digambar manual frame demi frame**.
2. `Assets.walkFrame` dan `Assets.idleFrame` memilih atlas v3.7 terlebih dahulu; fallback atlas v3.2, lalu sprite lama (`walk_plus`/`walk.png`). Aset versi lama tidak ditimpa.
3. `Actor.update/draw` kini memutar animasi berjalan dengan akumulasi waktu yang lebih konsisten (16 fase/detik jalan dan 22 fase/detik sprint), membatasi timer tiap 16 fase, dan menyesuaikan ritme bob. **Perbaikan bug idle:** sprite kepala tidak lagi digambar dua kali yang menyebabkan ghosting.
4. **Depth/shadow:** `fx/contact_shadow_v37.png` untuk pemain, companion, NPC, serta contact shadow objek yang mempunyai collision footprint. Komponen `logic/WorldLightingV37.java` menghitung arah bayangan sederhana saat siang dan opasitas saat hujan, malam, serta interior. Kualitas Hemat menghilangkan shadow prop tambahan.
5. **Layering air:** kilau/riak air berada di antara lantai dan sprite karakter sehingga tidak menutupi wajah pemain.
6. **Tidak ada perubahan** pada 22 map, prop lama, data collision, quest, save schema 7, naskah cerita, musik dan efek suara (86 aset). Tidak ada perubahan gameplay mekanik.

## Edit aset melalui VS Code

- Sprite utama: `android/assets/characters/arland/walk_v37.png`, `idle_v37.png`; Sofia serupa; NPC mengikuti folder masing-masing.
- Ukuran atlas wajib: walk **768×288** dan idle **384×288** (masing-masing 48×72 per fase, 4 baris arah: depan/kiri/kanan/belakang).
- Aset generator (tidak menimpa sumber): `python3 tools/character_polish_v37.py`. **Perhatian:** generator mengulang atlas v3.7 dari v3.2. Jika sudah mengedit atlas v3.7 secara manual, cadangkan perubahan sebelum menjalankannya.
- Bayangan: `android/assets/fx/contact_shadow_v37.png` (96×36 RGBA).
- Runtime/pengaturan: `core/src/main/java/com/arlandsofia/olu/{Assets.java,game/Actor.java,screens/GameScreen.java,logic/WorldLightingV37.java}`.

## Pemeriksaan

```bash
python3 tools/character_polish_v37.py
python3 tools/test_character_v37.py
bash tools/test_character_logic_v37.sh
bash tools/test_logic.sh
python3 tools/test_visual_v32.py
python3 tools/test_world_redesign_stage1.py
python3 tools/test_world_redesign_stage2.py
python3 tools/test_world_redesign_stage3.py
python3 tools/test_world_redesign_stage4.py
./gradlew :android:assembleDebug
```

Jangan menganggap test headless, pemeriksaan sintaks, ataupun pratinjau spritesheet sebagai pengujian OpenGL/Android nyata. Build perangkat masih mensyaratkan Android SDK, distribusi Gradle, dan tes terhadap renderer penuh. Cek file asli setelah build di `android/build/outputs/apk/debug/` jika berhasil.

## Pembersihan

Jalankan `python3 tools/cleanup_safe_v37.py` (dry run) atau `--apply`; kebijakan menghapus **hanya cache sementara terverifikasi di luar `android`, `core`, `art_source`, `gradle`, dan `docs`**. Layer editable, generator tahap lama, preview terdokumentasi, serta backup asli **tidak dihapus**. Catatan terperinci: `docs/CLEANUP_AUDIT_V3.7.json`.

## Tahap berikutnya

Fokus setelah ini adalah **Android render verification + art direction manual** untuk protagonis, sebelum melabeli source sebagai kualitas siap rilis. Sprite v3.7 merupakan animasi prosedural tingkat lanjut, tetapi belum mendekati redraw HD-2D kualitas studio.
