# Menjalankan Arland & Sofia v4.6.0 di Android Studio

Source ini **bukan APK**. Ini proyek Android native LibGDX (Java/Gradle) yang bisa dibuka dan dikembangkan di Android Studio.

## Cara menjalankan di Windows

1. Ekstrak ZIP sampai terlihat `settings.gradle`, `build.gradle`, `gradlew.bat`, `core/`, dan `android/` dalam **satu folder**.
2. Buka Android Studio > **Open** dan pilih folder yang memuat `settings.gradle` (jangan pilih `android/` saja).
3. Pastikan Gradle JDK menggunakan **JDK 17**. Di Android Studio: Settings > Build, Execution, Deployment > Build Tools > Gradle > Gradle JDK.
4. Izinkan Gradle Sync pertama kali mengunduh komponen yang belum terpasang. Koneksi internet dibutuhkan untuk **setup developer**, bukan untuk game saat dimainkan.
5. Gunakan Android SDK Platform 36 dan Build Tools yang kompatibel. Izinkan instalasi jika Android Studio memintanya.
6. Pilih konfigurasi modul **android**. Hubungkan HP Android dengan USB debugging atau jalankan Android Emulator, lalu klik Run.
7. Untuk membuat APK debug: buka Terminal di root proyek dan jalankan `gradlew.bat :android:assembleDebug` (Windows) atau `./gradlew :android:assembleDebug` (Linux/macOS).
8. Hasil APK, **jika build sukses**, berada di `android/build/outputs/apk/debug/android-debug.apk`.

## Fitur yang terintegrasi

- Route Arland/Sofia tetap punya cerita, side quest, map, audio, dan ending canon yang sama.
- Fitur Romance Simulation 3.0 dapat dibuka dari **menu Jeda saat bermain**, setelah save game berhasil.
- Simulasi memilih route dan **slot yang sedang aktif**, sehingga progresnya tidak tertukar.
- Hari, janji, dan batas kencan mengikuti **waktu dunia asli**, tidak ada tombol skip hari untuk memperbanyak hadiah.
- Pilihan dialog, janji, kencan, hadiah, dan momen khusus tersimpan dalam namespace terpisah. Slot baru/hapus slot mereset data romance slot itu saja.
- Living World v4.6 meningkatkan rutinitas NPC berdasarkan waktu/cuaca, menghindari tembok dan aktor lain tanpa teleport.
- Layout lama mendukung landscape HP/tablet dengan safe inset/notch.

## Pengujian yang sudah dilakukan pada source

- Compile test pure-JDK untuk 48 assertion Romance Simulation (PASS).
- Pure-JDK 9 assertion Living World NPC (PASS).
- Integritas 22 peta, audio, dan properti v4.4: 2.197 assertion (PASS).
- Responsive/tablet layout: 390 pemeriksaan (PASS).
- Regresi dua route, story, quest, save schema lama, ekonomi dan aktivitas: 24.686 pemeriksaan (PASS).
- Navigasi 22 area: 131 pemeriksaan (PASS).
- Java 11 syntax parse pada seluruh kode sumber Android/core: PASS.
- Pengecekan struktur file Android, JSON data, dan XML: PASS.

**Belum diuji:** kompilasi penuh APK melalui Android Gradle Plugin serta jalannya pada perangkat/emulator, karena Android SDK dan dependency Gradle tidak tersedia di lingkungan verifikasi ini. Tidak ada klaim bahwa semua perangkat bebas bug. Jika proses Gradle Sync/Run gagal, gunakan pesan Build Output Android Studio untuk diagnosis yang tepat.

## Menjaga progres lama

Jangan menghapus data aplikasi saat menguji upgrade jika ingin mempertahankan save sebelumnya. Simpan backup dulu. `SaveStore` dunia mempertahankan CRC/schema 8 dan tidak diganti oleh fitur romance. Jika mengalami masalah save baru, gunakan slot kosong dan cadangkan progres lama.
