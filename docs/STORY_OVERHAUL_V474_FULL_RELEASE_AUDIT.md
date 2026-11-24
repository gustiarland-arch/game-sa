# Arland & Sofia: Our Little Universe — Story Overhaul Full Source v4.7.4

**Status:** Source lengkap untuk Android Studio; **APK dan permainan pada perangkat nyata BELUM diverifikasi**. Pemeriksaan di bawah merupakan pengujian logika, source, aset, dan simulasi quest, bukan pengukuran performa atau bukti playtime enam jam.

**Tanggal:** 23 November 2026  
**Judul cerita:** *The Promise We Almost Forgot / The Empty Seat*  
**Platform sasaran:** LibGDX native Android, 100% offline setelah APK dibangun.  
**Struktur:** Pilih Arland atau Sofia, adegan dan keputusan yang berbeda, satu canon ending bahagia.

## Audit per chapter

| Bagian | Yang telah diintegrasikan pada data dan engine | Bukti pengujian |
| --- | --- | --- |
| **Prolog — The Book of Us** | Pilihan pesan awal, dua tahap craft hadiah per route, pertemuan Plaza, tiga shard dua perspektif, cutscene dan dua musik baru, dialog lanjutan di C01/Epilog | 96 simulasi / 12.465 pemeriksaan; 438 pemeriksaan media/referensi; save legacy |
| **Chapter 1 — The Beginning of Us** | Simbol dua urutan, quest pribadi kafe, tiga cabang surat dengan aktivitas berbeda, petunjuk awal The Quiet, kenangan dan keputusan yang kembali muncul | 1.789 pemeriksaan runtime, 23 navigasi, 653 aset |
| **Chapter 2 — A Little Date** | Ajakan diterima, dijadwalkan ulang, atau ditolak dengan kegiatan nyata dan konvergensi canon; photobooth, repair, pilihan pose, petunjuk lentera | 486 jalur / 78.314 pemeriksaan; 27 navigasi, 2.439 aset |
| **Chapter 3 — The Little Things** | Bingkai Arland, scrapbook Sofia, memasak dan Memory Corner, surat setengah jadi, undangan galeri, persiapan konflik | 864 jalur / 160.568 pemeriksaan; 67 navigasi, 1.697 aset |
| **Chapter 4 — Even When It Rains** | Peristiwa *The Empty Seat*, proyektor dan presentasi dari dua POV, lima lentera di peta Rain Garden, pemulihan hubungan yang perlu dimainkan | 324 jalur / 69.947 pemeriksaan; 104 navigasi, 756 aset |
| **Chapter 5 — Across the Stars** | Clockwork Station, Moonlight Lake, Memory Bridge, lima fragmen dan empat keselarasan kenangan, pengungkapan The Quiet melalui permainan | 108 jalur / 21.234 pemeriksaan; 139 navigasi, 1.044 aset |
| **Chapter 6 — Our Tomorrow** | Balai Hari Esok, tiga proyeksi yang dapat diperiksa, refleksi personal, empat panel kenangan, detail klimaks yang merespons keputusan pemain | 576 jalur / 101.466 pemeriksaan; 52 navigasi, 203 aset |
| **Epilog — To Be Continued** | Perjalanan kembali melalui Plaza, Kafe, Galeri, dan danau; akhir bahagia yang sama; bonus Ruang Dua Surat yang terbuka hanya setelah kedua route menyelesaikan C06 | 36 jalur / 3.376 pemeriksaan; 43 navigasi, 210 aset |

## Statistik source v4.7.4

- **736 scene** pada StoryDb, termasuk cerita utama, side story dan percakapan dunia.
- **157 quest step** pada QuestDb, termasuk aktivitas wajib masing-masing route.
- **29 area** termasuk Galeri Komunitas, Rain Garden, Clockwork Station, Moonlight Lake, Memory Bridge, Balai Hari Esok, dan Ruang Dua Surat.
- **287 entri Memory Book**. Beberapa entri hanya terbuka pada keputusan tertentu, bukan semua wajib dalam satu playthrough.
- **4 ikon pixel-art Prolog** dan **2 cue OGG instrumental Prolog baru**. Generator aslinya tersedia di folder `tools/`.

## Integritas, stabilitas dan kompatibilitas

- Semua **1.980 file** yang terdapat dalam ZIP baseline v4.6.6 masih ada dalam proyek ini.
- **807 aset PNG/JPEG/WebP/OGG/WAV Android baseline** yang diperiksa identik secara SHA-256; tidak diubah atau ditimpa.
- Perintah patch Prolog diuji tiga kali; `story.json`, `quests.json`, `maps.json`, dan `memory_book.json` dihasilkan dengan hash yang identik.
- Prolog lama tetap bisa dilanjutkan pada `PRO_GIFT`, `PRO_SHARDS`, dan `PRO_PORTAL`. Untuk pengalaman baru secara menyeluruh, mulailah slot permainan baru.
- Perintah `bash tools/test_logic.sh` lulus **29.080 pemeriksaan logika**. QA chapter, romance, audio, cutscene, sentuhan, dan enam profil HP/tablet juga lulus.
- APK Android belum berhasil dibangun di lingkungan ini: Gradle Wrapper 8.11.1 tidak tersedia dalam cache lokal, dan jaringan tidak dapat mengunduhnya. Karena itu **tidak ada klaim APK bebas bug, FPS tertentu, atau durasi enam jam teruji**.
- Desain, audio, icon dan cerita baru bersifat fiksi/orisinal untuk proyek game ini.

## Menjalankan source

1. Ekstrak arsip hingga folder `ArlandSofia` yang memuat `settings.gradle`, `core`, `android`, `tools`, `art_source` dan `gradlew`.
2. Buka folder `ArlandSofia` di Android Studio. Siapkan **Gradle JDK 17**, Android SDK API 36 dan koneksi untuk memperoleh dependensi Gradle/LibGDX satu kali.
3. Jalankan Gradle Sync lalu modul `android` pada emulator/perangkat. APK yang dibangun dimainkan offline.
4. Untuk tes logika tanpa Android SDK: `bash tools/test_prologue_v474.sh`, `bash tools/test_logic.sh`, atau tes per chapter di `tools/test_chapter*_v*.sh`.
5. Untuk meregenerasi konten: `bash tools/build_all.sh`; jalankan di environment dengan Python, Pillow, NumPy, ffmpeg, dan dependensi lainnya. Generator patch Prolog bersifat idempotent.

## Kriteria penerimaan yang masih memerlukan pengujian nyata

- Build debug/release APK dan pemasangan di Android dengan benar.
- UI, kontrol, orientation, dan performa pada beberapa HP dan tablet nyata.
- Playthrough manual kedua route termasuk semua keputusan dan retry mini-game.
- Validasi durasi waktu bermain, urutan cutscene, pacing emosi, tata suara dan pengalaman pemain.

Tidak ada perubahan GitHub selama sesi perombakan ini. File ZIP adalah **full source**, bukan APK terkompilasi atau bukti bahwa game telah memenuhi 100% kriteria perangkat nyata.
