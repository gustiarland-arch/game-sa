# v3.2.0 — Ultimate Visual Overhaul (implementasi source)

**Status:** perubahan aset dan integrasi renderer telah dibuat; **belum ada APK yang berhasil dikompilasi/diuji pada perangkat nyata**. v3.2 bukan sertifikasi kelayakan rilis.

## Apa yang sungguh diubah

| Komponen | Perubahan sebenarnya | Pemakaian di game |
| --- | --- | --- |
| 22 peta (`android/assets/maps/*.png`) | Pewarnaan atmosfer area, variasi cahaya, dekorasi pixel art sesuai biome, ornamen permukaan; ukuran tetap | `GameScreen` me-render file peta yang sama seperti sebelumnya, kini isinya baru |
| 256 prop (`assets/props/*.png`) | Penguatan contrast/ink, kilau, tekstur/aksen spesifik jenis tanaman, rumah, lampu, dan interior | `MapDb` menggunakan nama file dan titik jangkar yang sama; tidak ada perubahan collision/outline alpha |
| 25 atlas berjalan (`characters/*/walk_v32.png`) | 12 fase untuk 4 arah, bob/weight-shift dengan lengan/badan/kaki terpisah | `Assets.walkFrame()` memprioritaskan v3.2, fallback `walk_plus.png` |
| 25 atlas idle (`characters/*/idle_v32.png`) | 6 fase untuk 4 arah, detail napas dan blink ringan | `Actor.draw()` menggunakan `Assets.idleFrame()`; fallback `walk.png` |
| 21 portrait ekspresi | Penajaman/pemisahan warna halus + frame pastel gold untuk Arland/Sofia | Nama lama tetap, ditampilkan langsung oleh dialog dan menus |
| 6 UI ninepatch | Skin baru berukuran 64×64, edging pastel/gold lebih kaya | `Assets.loadCore()` memakai `ui/v32_*.png` |
| Panorama 2 lapis | Latar kota senja, jembatan, pepohonan dan lampu | `TitleScreen` dan `RouteSelectScreen` menggunakan berkas v3.2 secara langsung |
| Dialog & cutscene | Ribbon sinematik baru, bloom, ornamen, **12 ilustrasi pendek berbasis peta** yang dipilih melalui caption canon | `DialogBox` / `CutscenePlayer` memuat gambar baru saat adegan terjadi |

**Jujur soal cakupan:** ini merupakan *art pass pixel-art prosedural* yang memperindah seluruh dunia dan meningkatkan animasi, **bukan 22 peta yang digambar ulang secara manual satu per satu dari nol**. Generator dan baseline disertakan agar aset bisa diedit/diulang. Tidak ada simulasi Photoshop atau tangkapan layar emulator yang diklaim sebagai hasil nyata.

## Editing aset dengan VS Code

- Edit gambar final langsung di `android/assets/maps/`, `props/`, `characters/<nama>/walk_v32.png`, `idle_v32.png`, `ui/` atau `characters/<nama>/portraits/`.
- Edit generator `tools/visual_overhaul_v32.py` untuk palet area, kepadatan dekorasi, bentuk ornamen, kontras prop, sprite, serta frame UI. Baseline original dari v3.0 berada pada `art_source/visual_v32_base/` (22 peta, 256 prop, 21 potret). File ini sengaja tidak disimpan di `android/assets`, agar tidak membengkakkan APK.
- Gunakan `python3 tools/visual_overhaul_v32.py` setelah regenerasi konten/peta. **Perhatian:** perintah ini akan menimpa aset hasil manual edit pada folder target dengan hasil generator. Untuk edit manual, jangan jalankan generator ulang setelah mengganti PNG secara langsung.
- Sesudahnya jalankan `python3 tools/gen_cinematic_stills_v32.py` untuk menghasilkan ulang 12 stills. Jika ingin mengganti satu still secara manual, edit `android/assets/ui/v32_cinema/<id>.png` tanpa menjalankan generator lagi.
- Semua gambar menggunakan ukuran frame tetap agar aman untuk `TextureRegion` dan koordinat peta. **Jangan ubah dimensi `walk_v32` (576×288), `idle_v32` (288×288), atau koordinat dan ukuran peta** tanpa menyesuaikan engine/data.
- **Cara rebuild keseluruhan:** `bash tools/build_all.sh`. Paket audio lama juga ikut diregenerasi dari skrip lama. Jika hanya ingin gambar v3.2, jalankan dua generator visual v3.2 saja.
- Lihat `docs/preview/v32_real_asset_composite.jpg` untuk pratinjau komposit nyata enam lokasi hasil aset source. Ini bukan screenshot emulator.

## Konten dan kompatibilitas

- Dua route, 398 scene, seluruh chapter, ending canon, event dunia, minigame, 12 pencapaian, navigasi dan riwayat dialog **tidak diubah**.
- `data/quests.json`, `data/maps.json`, `data/story.json`, `data/props.json`, dan `data/memory_book.json` tetap identik dengan v3.0.
- Seluruh 86 berkas audio lama dan setiap lembar pose/sprite legacy tetap identik secara SHA-256.
- Save schema **tetap 7**; tidak ada migrasi save untuk art pass ini. Backup save sebelum mengganti build Android tetap disarankan.
- Nama/titik anchor prop, collision, pintu, geometri misi, dan gameplay tidak dimodifikasi.

## Pengujian dan batasan

- `python3 tools/test_visual_v32.py` memeriksa perubahan piksel 22 peta, 256 prop termasuk kesamaan alpha, 25 atlas animasi, 12 stills, hash seluruh file audio dan data gameplay.
- `python3 tools/release_audit_v32.py` melakukan audit static integrity / keberadaan aset / API versi; manifest SHA-256 keluaran di `docs/ASSET_SHA256_V3.2.json`.
- `bash tools/test_logic.sh`, `bash tools/test_release_v29.sh`, `bash tools/test_controls_v28.sh`, `bash tools/test_romance_ui.sh` untuk logika core, save, input dan UI lama.
- **Tetap wajib sebelum rilis**: Gradle + Android SDK nyata, APK debug/release tersigning, pemeriksaan native library 16 KB, pengukuran RAM dan FPS di beberapa perangkat, seluruh QA skenario 2 route, audit versi Android/platform dan hak cipta.

## Batasan estetika

Sprite v3.2 memanfaatkan arsitektur potret/sprite original, bukan ilustrasi artis baru untuk setiap frame. Jika ingin kualitas produksi lebih tinggi, layer per-frame harus direview dan retouch oleh animator pixel art, terutama pose samping, bayangan kaki, dan kesesuaian warna antar area.
