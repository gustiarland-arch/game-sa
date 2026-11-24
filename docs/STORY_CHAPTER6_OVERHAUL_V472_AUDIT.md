# PRIVATE DRAFT — STORY CHAPTER 6 / OUR TOMORROW (v4.7.2)

Status: **Checkpoint Chapter 6 selesai untuk source dan pengujian headless, belum rilis APK.**

## Kontrak cerita yang dipertahankan

- Dua POV Arland/Sofia tetap memiliki pilihan dan refleksi personal berbeda, tetapi satu kejadian canon akhir `C06-X01` dan satu epilog bersama.
- Konflik The Empty Seat tidak dibatalkan: hari galeri tetap menampilkan niat baik Arland, kehadiran yang terlewat, dan keberanian Sofia. Tidak ada perpisahan tragis/bad ending.
- The Quiet bukan monster: dua ingatan dapat berdampingan tanpa disamakan. Chapter 5 sudah mengungkapkannya; Chapter 6 mengujinya melalui tindakan dan proyeksi masa depan.
- Halaman masa depan tetap kosong karena masa depan belum ditentukan; **bukan** karena pemain gagal mengisi halaman.
- Semua 1980 file sumber v4.6.6 dipertahankan. **1616 aset media dari v4.6.6 identik CRC32**, tidak ditimpa.
- Save schema dan ID scene/step lama tidak dihapus. Save lama yang sudah melewati tahap baru dapat menyelesaikan finale lama. Save yang masih di `C06_Q_REVEAL` akan masuk rangkaian Chapter 6 baru.

## Audit sebelum upgrade

- Chapter 6 lama sudah memiliki tiga kelopak, puzzle Arland/Sofia, surat, Pohon Harapan, dan ending.
- Tiga kemungkinan masa depan sempurna hanya disebut lewat dialog, belum dapat dikunjungi dan dibandingkan.
- Pilihan spesifik Chapter 5 dan respons saat melihat masa depan belum punya konsekuensi adegan yang cukup kuat.
- Belum ada lokasi asli yang memvisualisasikan ilusi masa depan, dan jumlah peta masih 27.
- Pengujian visual historis mengunci jumlah peta tepat 27, padahal konten baru harus boleh menambah area.

## Implementasi pada draft

| Bagian | Implementasi nyata |
|---|---|
| Balai Hari Esok | Satu area/map orisinal editable melalui generator Python (`1920×1280`), 2 pintu resiprokal, collision, lokasi spawn, registrasi efek native dan ambient, soundtrack khusus. Area ke-28. |
| Ilusi masa depan | Tiga objek yang harus dikunjungi: DATE (kencan tanpa pilihan), PRESENCE (janji yang memaksa sempurna), AGREEMENT (semua setuju tanpa suara). Dialog Arland/Sofia berbeda, setiap ilusi punya dua pilihan nyata. |
| Refleksi personal | Arland: hadir, mendengar, meminta bantuan. Sofia: berani bicara, memilih ruang, bangga pada keberanian. Masing-masing tiga pilihan disimpan sebagai flags dan ditanggapi kembali di akhir. |
| Four-panel memory alignment | 4 interaksi yang harus dilakukan pemain: mural Chapter 1, pilihan kencan Chapter 2, hal-hal kecil Chapter 3, dua perspektif galeri serta janji Chapter 5. Tidak dapat di-skip dengan hanya membuka panel pertama. |
| Payoff | 12 adegan recall berdasarkan hasil 3 pilihan masa depan × 2 respons × 2 route; plus 2 scene personal akhir. Setiap jalur hanya menampilkan konsekuensi keputusan sebenarnya, bukan jawaban yang tidak dipilih. |
| Epilog continuity | 6 opsi janji akhir mendapat dialog lanjutan setelah festival, tanpa membuat ending lain. Save lama tanpa flags baru tetap menyelesaikan Epilog. |
| Aset/audio | 5 ikon pixel editable (`items/v472_c06_*.png`), 1 peta (`maps/hall_of_tomorrow.png`), 2 BGM OGG Vorbis orisinal, 1 WAV memory-glint. Registrasi audio dan efek atmosfer native. |
| Quest & scene | 6 quest step baru `V472_C06_*`, 55 adegan baru `V472-*`, seluruh original `C06_*`, `EPI_*`, dan `C06-X01` tetap ada. |
| Pembangunan ulang | `tools/build_all.sh` menjalankan patch, generasi gambar/audio, registrasi runtime, dan QA v472 dalam urutan yang tepat sesudah Chapter 5. Patch diulang dua kali dengan hash 6 file utama yang identik. |

## Hasil pengujian (source, bukan gameplay Android)

- **576 kombinasi dua route + 3 pilihan personal × 8 kombinasi respons ilusi × 3 flag Chapter 5 × 2 ending-response × 2 cancel/retry**: **101154 pemeriksaan** pada `QuestEngine` dan `ActionRunner` produksi, termasuk callback Epilog, old saves dan satu ending canon.
- **52 pemeriksaan collision-grid BFS**, titik interaksi dan pintu resiprokal.
- **203 pemeriksaan aset dan referensi**: termasuk 55 adegan, 6 quest step, 2 OGG Vorbis terdaftar, WAV, ikon, peta, katalog item.
- Logika source Prolog–Epilog: **28277 pemeriksaan** (`tools/test_logic.sh`).
- Regresi Chapter 1 **1780**; Chapter 2 **78314**; Chapter 3 **160568**; Chapter 4 **69947**; Chapter 5 **21234** pemeriksaan (suite terkait lulus).
- Kompatibilitas v4.6.5 dan v4.6.6, cutscene/UI **859**, romance **51**, touchscreen **750**, tablet **390**, audio **267**, cinematic audio **93** lulus.
- Patch `apply_story_chapter6_v472.py` + registrasi audio/atmosfer dijalankan dua kali: **6 file data/engine utama identik secara byte**. Tidak ada duplikasi scene, quest, memory, atau pintu.

## Batasan yang TIDAK diklaim selesai

- Build APK Gradle Android, GPU runtime, tes multi-device fisik, kontrol sentuh dalam cutscene, dan playthrough manusia 6 jam per route belum diverifikasi di lingkungan ini.
- **Prolog dan Epilog** masih membutuhkan audit bab tersendiri sesuai permintaan pengguna. Coda Epilog sudah tersambung, bukan berarti seluruh Epilog selesai diaudit.
- No ZIP distributed. No GitHub changes. The working tree remains a local private draft.
