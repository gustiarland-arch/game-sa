# RELEASE STATUS — v4.9.0 Living World & Gameplay Expansion

## Cakupan riil

- Basis arsip: v4.8.0 Full Source Story World Remaster, tanpa penghapusan assets Java atau data save lama.
- 29 area asli; tambahan satu penemuan per area, bersyarat chapter C02–C06, satu kali per save dan masing-masing berinteraksi dengan sistem ActionRunner, dialogue, dan Memory Book.
- 14 minigame bertipe `v49_echo`, tiga putaran urutan empat simbol, pola khusus route (Arland/Sofia), bisa diulang bila salah dan dibatalkan tanpa softlock.
- 18 event suasana baru berdasarkan area/jam/partner; anti-farming satu kali per hari game; memori pertama tetap disimpan setelah pergantian hari.
- 96 naskah scene tambahan: 58 discovery + 36 daily event + 2 bonus atlas. Ending canon, petualangan utama, cutscene lama, dan dialog lama tidak diubah.
- 48 entri Memory Book baru dan progres penemuan di tab Jelajah; 29/29 memberi bonus `Atlas Kenangan Kecil` tanpa akhir cerita alternatif.
- Save schema 8 tidak berubah, flags/counters disimpan memakai mekanisme existing; save per route dan slot tetap terpisah.
- Versi Android: name `4.9.0`, versionCode `90`, tetap offline dan tidak memerlukan layanan eksternal.

## Pengujian yang dikerjakan

- `bash tools/test_logic.sh` — **LULUS 32.147 checks** (cek peta/collision, jalur cerita dua POV, side quest, memori, event, scene, reward dan save/load).
- `bash tools/test_v30_ui_compile.sh` — **LULUS** typecheck komponen UI, termasuk Memory Book.
- Typecheck Java 11 untuk `Games`, `Minigame`, dan `MinigameOverlay` — **LULUS** melalui GDX/UI stub compile-only sementara.
- Dua titik penanda penemuan (riverside dan dermaga) dipindahkan ke area tak terhalang setelah pemeriksaan collision; posisi lama aktor dan peta tidak berubah.
- Build Gradle Android/instalasi APK/tes FPS/tes device touch/tab & durasi sesi 6 jam — **BELUM TERVERIFIKASI**. QA headless bukan pengganti playtest fisik.

## Cara pakai

1. Ekstrak ZIP, lalu buka folder `ArlandSofia` (berisi `settings.gradle`) dalam Android Studio.
2. Sync Gradle menggunakan JDK 17, Android SDK API 36, dan plugin sesuai `build.gradle`.
3. Jalankan modul `android`, uji dua route, dan coba jejak baru dari Chapter 2 seterusnya. Tidak diperlukan internet saat game sudah terinstal.
4. Backup save pengguna sebelum memasang build baru; tidak ada migrasi schema baru. New Game disarankan untuk mencoba seluruh konten narasi terbaru.

**Editability:** Semua skenario & syarat aktivitas ada di `android/assets/data/*.json`; logic interaktif ada di `core/src/main/java/com/arlandsofia/olu/`; minigame Echo di `game/minigame/Games.java` + `logic/EchoPatternV49.java`. Script generator historis tidak boleh dianggap sumber JSON v4.9 tanpa integrasi konten v4.9.
