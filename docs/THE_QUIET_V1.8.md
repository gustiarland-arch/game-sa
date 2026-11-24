# Pengembangan Cerita v1.8.0 — The Quiet dan Dua Sudut Pandang

## Arah cerita

*The Quiet* dalam draft fiksi ini bukan musuh fisik. Pak Wira menamai kesunyian yang muncul ketika cerita berharga tidak pernah dibagikan. Pemain mempelajari bahwa mengenang seseorang bukan berarti memperbaiki semua kehilangan. Epilog menutup kisah Pak Wira dan Nenek Sari dengan mengembalikan halaman lama sambil menghormati pilihan Sari untuk bercerita.

**Penting:** Tambahan ini terintegrasi dalam main story Chapter 1/4/5/6/Epilog, bukan dialog sampingan yang hanya tercantum di JSON. Ending canon dan nama chapter tidak diubah.

## Alur bermain

| Chapter | Route Arland | Route Sofia | Pertemuan |
|---|---|---|---|
| C01 | Membaca denah Pak Wira di stoples barat ruang arsip | Menelaah catatan pinggir di stoples timur | Kembali ke Bu Laras dan dermaga |
| C04 | Membaca ulang surat Wira di halte setelah menemukan kotak surat | Menulis respons pada surat Sari di meja perpustakaan | Bertemu di taman saat hujan dan ke Lantern Field |
| C05 | Menafsirkan denah dan simbol pada bangku Starfall Village | Menafsirkan empat garis sebagai tahapan percakapan | Masuk ke Eternal Garden bersama |
| C06 | Memeriksa kolam, gazebo, bangku; membuka kunci simbol bunga–buku–bintang | Memeriksa bangku, gazebo, kolam; menyusun halaman mendengar–mengingat–bercerita–tidak sendirian | Memahami *The Quiet*, memilih respons, lalu menjalankan ending pohon yang sudah ada |
| EPI | Refleksi Arland tentang mendengar tanpa terburu-buru | Refleksi Sofia tentang memberi ruang pada rindu | Menyerahkan halaman Pak Wira kepada Sari dan lanjut Festival Lentera |

### Pilihan tanpa memecah ending

Adegan `Q-C06-REVEAL` memiliki dua pilihan: ingin mendengar cerita Sari, atau ingin menyimpan halamannya dengan hati-hati. Flag `Q_CHOICE_LISTEN` / `Q_CHOICE_KEEP` tersimpan. Keduanya mengarah ke satu penutup bersama sehingga route lama dan ending utama tidak berubah.

## Data, integrasi dan perawatan

- `tools/content/naskah_quiet_v18.txt` — 20 scene mentah / 22 scene hasil build (dua scene `me/partner` otomatis menjadi dua route).
- `tools/build_content.py` — 11 step baru, flag, progres penyelidikan, item, Memory Book, minigame config. `quiet_cipher` memakai `type=code`, `quiet_pages` memakai `type=pages`.
- `core/src/main/java/com/arlandsofia/olu/game/minigame/Games.java` — mendukung ID baru, tetap memakai implementasi minigame yang sudah ada.
- `core/src/test/java/com/arlandsofia/olu/LogicSelfTest.java` — assertions main story: setiap scene baru benar-benar dikunjungi, 3 jejak per route, minigame route tidak tertukar, pilihan tersimpan, halaman diserahkan, dan save state pertengahan quest bertahan setelah reload.
- `android/assets/data/*.json` adalah **output generator**, jangan edit langsung. Regenerasi `python3 -I tools/build_content.py`; untuk perubahan layout jalankan `python3 -I tools/check_layout.py android/assets`.
- **Tidak ada perubahan save schema** (`Progress.SCHEMA=4`). ID flag dan counter baru tersimpan otomatis di save setiap route dan slot, tanpa izin jaringan.

## Save lama dan replay

Jika pemain sudah melewati Chapter 1/4/5/6 pada v1.7, game tidak secara paksa mundur. Jalankan mode replay chapter untuk menyaksikan adegan baru; replay bersifat terpisah dari progres save utama menurut mekanisme proyek. Untuk save yang sedang berada sebelum tahap yang disisipkan, lanjutkan bermain seperti biasa. Cadangkan file save sebelum memasang APK baru.

## Yang diuji, dan apa yang belum

| Pengujian yang benar-benar dijalankan | Hasil |
|---|---|
| `bash tools/test_logic.sh` | 22.547 pemeriksaan lulus, termasuk The Quiet pada dua route, semua side quest, save pertengahan, ekonomi dan romansa |
| `bash tools/test_romance_ui.sh` | Uji callback UI lama lulus, tanpa pengujian renderer |
| `./gradlew --offline :android:assembleDebug` | Gagal mengunduh Gradle 8.11.1 sebelum compile (`UnknownHostException`) |
| APK, animasi, sentuhan minigame baru, performa Android | **Belum terverifikasi** |

Estimasi durasi cerita utama **81–83 menit per route**, dan semua aktivitas sekitar **177–181 menit per route** menurut simulator. Target **6 jam per route belum tercapai**. Hasil estimator bukan durasi uji pemain.
