# Arland & Sofia — Story Expansion v2.6.0

## Tujuan dan prinsip

Perluasan naskah interaktif untuk game offline native Android yang sudah ada. Semua peristiwa utama dan ending canon dari versi 2.5 tetap sama. Arland dan Sofia harus mengalami **perjalanan berbeda dalam Chapter 5** tetapi bertemu kembali di satu titik cerita yang sama. Naskah yang ditambahkan adalah **draft fiksi**, bukan klaim peristiwa nyata.

## Penambahan main quest

| Chapter | Langkah baru | Gameplay dan cerita |
|---|---|---|
| C03 | `C03_V26_DETAILS` | Setelah memasak, periksa catatan resep dan kemas bekal; dialog dan reaksi berbeda menurut karakter, dua interaksi wajib |
| C04 | `C04_V26_RECONCILE`, `C04_V26_VOW` | Memilih mengunjungi dua titik di taman setelah hujan, lalu menulis janji berdua; cutscene dengan kamera, kelopak dan musik rekonsiliasi |
| C05 Arland | `C05_V26_A_SURVEY`, `C05_V26_A_KEY` | Periksa bangku, rumah tengah dan lapangan; kumpulkan 3 jejak, susun simbol di puzzle code-lock khusus Arland |
| C05 Sofia | `C05_V26_S_NOTES`, `C05_V26_S_COMPOSE` | Temukan 3 potongan tulisan yang tertinggal, lalu urutkan 4 halaman di puzzle khusus Sofia |
| C05 shared | `C05_V26_NIGHT_TALK`, `C05_V26_STARGAZE` | Kedua jalur menyatu; percakapan, pilihan yang tersimpan dan cutscene dengan soundtrack `star_road`; lalu lanjut ke `C05_Q_ECHO` lama |

Pemain yang sudah menyelesaikan Chapter terkait pada save v2.5 kemungkinan akan melewati konten baru pada route lama, karena save menyimpan posisi langkah aktif. Gunakan replay chapter atau mulai route baru untuk memainkan seluruh cerita tambahan. Tidak ada reset save otomatis.

## Empat side quest baru

| ID | Judul | Route | Alur | Hadiah |
|---|---|---|---|---|
| `SQ_V26_MAP_A` | Peta untuk Dito | Arland | Kak Nara → Plaza → Kafe → Riverside → Kak Nara | `denah_dito` |
| `SQ_V26_CARDS_S` | Tiga Kartu Cerita | Sofia | Bu Laras → Plaza → Toko Bunga → Halte → Bu Laras | `kartu_klub_baca` |
| `SQ_V26_LISTEN` | Tiga Cerita Setelah Hujan | Bersama | Nenek Sari → Kafe → Perpustakaan → Halte Perumahan → Nenek Sari | `kumpulan_cerita_hujan` |
| `SQ_V26_LAMPS` | Peta Lampu Kota | Bersama | Kak Bayu → Halte Jalan Kota → Riverside → Bukit Bintang → Kak Bayu | `peta_lampu_kota` |

Masing-masing quest memakai flag `START`, tiga tahap, dan `DONE` untuk menghindari pengulangan hadiah. Entri Memory Book dibuka dengan flag `DONE`. Dua side quest route-only tidak ditampilkan sebagai quest yang wajib diselesaikan karakter lain.

## Cara mengedit lewat VS Code

- Naskah tambahan: `tools/content/naskah_story_v26.txt`. Format `=== SCENE-ID | Judul | arland/sofia/shared | C03/C04/C05`; baris `arland(senyum): ...`, `narrator: ...`, `? Pilihan | FLAG` dan respons `B>`.
- Alur dan interaksi: `tools/build_content.py`. Cari `v2.6` untuk main steps dan side quest. **Jangan mengubah identifier flag atau item tanpa menyesuaikan referensi lain**.
- Puzzle baru: definisi `v26_night_compass` / `v26_night_pages` pada `MINIGAMES` di `build_content.py`, factory pada `core/.../game/minigame/Games.java`. Kedua puzzle memakai mekanisme yang telah ada, bukan game terpisah yang belum diimplementasikan.
- Memory Book dan item: `ITEMS` serta `ENTRIES` di `build_content.py`; ikon memakai PNG lokal lama (dapat diganti manual di `android/assets/items/`).
- Jalankan `python3 -I tools/build_content.py` untuk memperbarui JSON, lalu `bash tools/test_logic.sh` dan `python3 tools/test_story_v26.py`. Generator penuh `bash tools/build_all.sh` dapat menimpa aset yang pernah diedit manual—backup dulu.
- Semua 86 audio berada langsung di `android/assets/audio/` **dalam satu ZIP source lengkap**. Tidak ada paket terpisah yang dibutuhkan.

## Hasil verifikasi dan batasan

Alur kedua route sampai Epilog, puzzle, quest sampingan, replay chapter, save schema 5, ekonomi, dan romansa diperiksa oleh test Java headless. Validasi data baru: `tools/test_story_v26.py`. Jumlah konten: **372 scene, 1.835 baris dialog, 93 step utama, 135 interaksi sampingan, 25 sidequest katalog, 75 item, 115 Memory Book entries**.

**Estimasi simulator:** ±90–91 menit alur utama dan ±219–221 menit jika semua quest sampingan serta eksplorasi diselesaikan pada satu route. Ini bukan hasil playtest, dan target enam jam per route belum tercapai.

**Belum dibuktikan:** berhasilnya kompilasi APK, pengujian di perangkat fisik, kualitas audio pada HP, dan FPS. Jika Gradle wrapper/distribusi tidak dapat diakses, proses berhenti sebelum kompilasi; itu tidak bisa dipakai sebagai bukti source Android sudah berhasil dibangun.
