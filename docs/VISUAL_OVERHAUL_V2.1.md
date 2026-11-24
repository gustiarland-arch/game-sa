# Arland & Sofia — Visual Overhaul v2.1.0

## Tujuan dan cakupan

Update ini **mengembangkan source v2.0.0 yang sama**, bukan menulis ulang game. Proyek tetap Android native (Java 11 + LibGDX), offline, landscape. Semua 22 peta, collision, cutscene lama, route Arland/Sofia, cerita canon, 21 side quest unik (19 relevan tiap route), 3 toko/3 pekerjaan, save schema 4, quest sampingan, UI Memory Book, dan ending lama dipertahankan. Versi runtime, Gradle dan CI: **2.1.0 (versionCode 21)**.

## Perubahan implementasi

| Area | Source / aset | Dampak |
|---|---|---|
| Panorama menu | `ui/v21_skyline.png` + `v21_foreground.png`, `TitleScreen`, `RouteSelectScreen` | Ilustrasi kota senja, jalan, pepohonan, lampu, dan lapisan depan dengan parallax lambat. Banner karakter lama tetap utuh. |
| UI seluruh game | `ui/*_v21.png`, `Assets.loadCore()` | Enam skin nine-patch baru untuk panel, panel gelap dan tombol normal/tekan/utama/nonaktif. Sifat responsif dan handler tombol lama dipertahankan. |
| Pergerakan 25 aktor | `characters/*/walk_plus.png`, `Assets.walkFrame()`, `Actor.draw()` | Atlas 8 fase x 4 arah dari sheet lama, termasuk Arland dan Sofia. Durasi animasi mengikuti `anim` existing; fallback ke sheet 3 frame bila atlas tambahan tidak tersedia. **Animasi merupakan variasi frame turunan, belum animasi aksi tangan yang sepenuhnya baru.** |
| Percakapan | `DialogBox` + `ui/v21_dialog_ribbon.png`, `v21_bloom.png` | Kotak dialog masuk dengan gerak ringan, panel potret, warna nama pembicara, progress pembacaan, indikator lanjut dan tampilan pilihan yang lebih jelas. Tidak mengubah logika percakapan. |
| Cutscene penting | `CutscenePlayer.drawUi()` dan `tools/build_content.py` | Garis aksen pada letterbox, ribbon/caption sinematik, glow, dan beat FX baru di pertemuan Plaza, Memory Garden, Perpustakaan, pembacaan surat Sofia, reveal The Quiet, pelepasan lentera. Menggunakan perintah cine yang telah didukung engine, tidak mengubah pilihan atau ending. |
| Regenerasi | `tools/gen_visual_v21.py`, `tools/build_all.sh` | Sumber procedural orisinal untuk semua PNG di atas; file `walk.png` lama **tidak ditimpa**. |

## Mengedit di VS Code

- Ubah bentuk/gaya background, warna awan, panel, bingkai dan bloom pada `tools/gen_visual_v21.py`. Jalankan `python3 tools/gen_visual_v21.py android/assets` untuk regenerasi.
- Untuk desain sprite berjalan dasar, edit `android/assets/characters/<id>/walk.png` (3 frame 48×72 per arah, atlas 144×288), lalu regenerasi `walk_plus.png`. Alternatifnya gambar `walk_plus.png` secara manual (8 frame 48×72 per arah, atlas 384×288) untuk animasi profesional yang lebih unik. Generator akan menimpa `walk_plus.png` bila dijalankan kembali: simpan versi manual di luar output generator.
- Tema UI disematkan lewat enam lokasi di `Assets.loadCore()`. Bisa dikembalikan ke versi lama hanya dengan mengubah nama PNG ke `panel.png`, `panel_dark.png`, `button.png`, dll., tanpa mengubah handler event.
- Aset pratinjau: `docs/preview/v21_menu_asset_preview.png`. **Ini komposit statis dari aset game, bukan screenshot Android asli.**

## Pengujian yang dijalankan

1. `python3 tools/gen_visual_v21.py android/assets` menghasilkan dua layer menu, enam skin, ribbon, bloom, dan 25 atlas berjalan.
2. `python3 tools/test_visual_v21.py android/assets` — **112 pemeriksaan lulus**, memeriksa ukuran, alpha, minimal jumlah fase gerak, frame idle identik dengan sumber, keberadaan Arland/Sofia, serta scene/data utama.
3. `python3 -I tools/build_content.py` — 303 scene, 1.493 dialog, 84 step, 115 side interaction, 25 NPC, 71 item, 92 Memory Book.
4. `python3 -I tools/check_layout.py android/assets` — layout OK, termasuk jangkauan posisi interaksi/cutscene.
5. `bash tools/test_logic.sh` — **22.803 pemeriksaan lulus**, kedua route sampai epilog, 19 side quest tiap route, save/migrasi, story flags, ekonomi, romansa, jam/cuaca dan NPC.
6. `bash tools/test_visual_fx.sh` — **47 file Java diparse Java 11**, WorldFx smoke test di stub lulus.
7. `bash tools/test_romance_ui.sh` — input tab momen, gift dan date dengan stub lulus.
8. `./gradlew --offline :android:assembleDebug` — **gagal sebelum kompilasi**: wrapper belum bisa mengunduh Gradle 8.11.1 (`services.gradle.org`). Ini berarti belum ada uji APK, GPU, resolusi, sentuhan di HP asli, shader atau FPS nyata. Seluruh uji headless dan statis **tidak boleh dianggap bukti build Android berhasil**.

## Hal yang masih perlu setelah v2.1

- Build APK dengan JDK 17, Android SDK 35 dan Gradle 8.11.1 pada perangkat pengembang dengan dependensi tersedia, lalu jalankan pengujian di Android landscape ukuran berbeda.
- Selanjutnya buat **sprite atlas gambar manual** untuk 8 frame tangan/kaki yang benar-benar unik, pose interaksi dan idle emosi yang terpisah. Generator v2.1 merupakan pondasi transisi, belum setara sprite artis manual.
- Audit keterbacaan tombol dan kontras dialog di layar kecil; uji FPS di preset Hemat, Seimbang, Sinematik; tambahkan pilihan subtitle accessibility bila diperlukan.
- Jika target 6 jam **per route** masih diinginkan, perlu ekspansi cerita terpisah karena versi v2.1 tidak menambah dialog inti; estimator sekarang ±3,1 jam/route lengkap.
