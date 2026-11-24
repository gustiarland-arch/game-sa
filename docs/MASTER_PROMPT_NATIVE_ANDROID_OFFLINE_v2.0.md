# MASTER PROMPT v2.0 — ARLAND & SOFIA: OUR LITTLE UNIVERSE
## NATIVE ANDROID • GRADLE • 100% OFFLINE APK • STORY-DRIVEN PIXEL ART RPG

### 1. PERAN, TUJUAN, DAN INPUT
Bertindak sebagai Senior Android Game Engineer, Kotlin/Java Developer, LibGDX Engineer, Pixel Artist, Narrative Designer, UI/UX Designer, QA Engineer, dan Gradle Build Engineer.

Gunakan ZIP v0.4 sebagai **REFERENSI SOURCE LAMA DAN ASET**, serta `ARLAND_SOFIA_Story_Bible_Naskah_Dialog_v1.0.docx` sebagai sumber narasi pengembangan. Jangan mengarang detail pribadi sebagai fakta. Audit file dan pertahankan aset, karakter, peristiwa canon, struktur route, dan sistem gameplay yang masih relevan.

**TARGET WAJIB: APK ANDROID NATIVE YANG 100% BISA DIMAINKAN OFFLINE.** Saya tidak mau game web. Jangan membuat PWA, website game, HTML5 Canvas, Phaser, Capacitor, Cordova, React Native WebView, TWA, WebView wrapper, atau memuat halaman HTML/JS sebagai engine gameplay.

### 2. KEPUTUSAN TEKNOLOGI
Gunakan **LibGDX dengan Kotlin atau Java**, project Gradle yang dapat dibuka langsung di Android Studio. Rekomendasi struktur `core/` (gameplay, rendering, maps, dialogue) dan `android/` (Android launcher dan APK), dengan Gradle Wrapper dan Android Manifest yang benar. Gunakan OpenGL/game rendering native LibGDX; tidak bergantung browser atau WebView.

Boleh memakai Tiled/TMX atau format tilemap lokal; pisahkan tile art dari data collision, zone, depth, dan interaksi. Pilih versi Android Gradle Plugin, Kotlin/JDK, Android SDK, LibGDX yang saling kompatibel; dokumentasikan versi aktual yang dipakai. Jangan mengklaim build berhasil tanpa output Gradle yang terverifikasi.

### 3. MAKNA 100% OFFLINE
Ketika APK sudah terpasang, seluruh cerita, map, sprite, musik, dialog, quest, puzzle, save, settings dan mini-game berjalan **tanpa internet sejak peluncuran pertama**. Semua aset harus dikemas di dalam APK/asset pack lokal, bukan diunduh saat runtime. Jangan ada CDN, remote config, backend, login, sinkronisasi cloud, iklan, analitik pihak ketiga, telemetry, remote API, atau permintaan internet runtime. Jangan menyertakan Android `INTERNET` permission kecuali benar-benar ada alasan teknis, dan untuk target ini tidak ada alasan yang diterima. Periksa final merged manifest.

Catatan: **pengunduhan SDK, Gradle, library, atau dependency ketika menyiapkan mesin developer bukan bagian dari runtime game**. Siapkan Gradle offline mode setelah dependensi diperoleh dan jika diminta buat paket cache/lockfile; APK yang dihasilkan harus tetap offline mandiri.

### 4. KONSEP GAME TIDAK BOLEH BERUBAH
Judul: Arland & Sofia: Our Little Universe. Genre: cozy pixel art romance adventure / story-driven RPG / light life simulation. Kamera **top-down 3/4 view seperti sudut eksplorasi Stardew Valley**, tetapi semua peta, karakter, UI, ikon, dialog, musik dan desain harus orisinal. Landscape Android-first. Bahasa Indonesia natural. **Bukan fighting game, bukan side-scrolling platformer, dan bukan visual novel statis**.

Karakter Arland memakai kacamata, rambut hitam pendek, hoodie putih; Sofia memakai hijab abu-abu dan outfit gelap. Keduanya harus menjadi karakter yang playable, punya sifat/voice berbeda, portrait, emote, animasi 4 arah, dan route personal.

### 5. DUA ROUTE, SATU CERITA UTAMA
New Game wajib menawarkan ARLAND ROUTE atau SOFIA ROUTE; setiap route punya adegan pembuka, objective pribadi, item, dialog, monolog, side quest, clue, dan cutscene unik. Event canon (pertemuan, buku, puzzle, kenangan, ending) harus sinkron pada kedua route. Hindari hanya mengganti nama dialog. Pertahankan satu canon ending dan buat bonus two-sided memory setelah dua route tamat. Simpan progress tiap route secara terpisah.

### 6. ALUR CERITA DAN DATA
Pakai Story Bible DOCX yang disertakan. Struktur: Prologue—The Book of Us; Chapter 1—The Beginning of Us; Chapter 2—A Little Date; Chapter 3—The Little Things; Chapter 4—Even When It Rains; Chapter 5—Across the Stars; Chapter 6—Our Tomorrow; Epilogue—To Be Continued.

Pertahankan baseline story v0.4: Arland membawa bunga kertas, Sofia membawa kartu pos, keduanya bertemu di plaza, menemukan Memory Book, mengumpulkan tiga shards di Memory Garden, melanjutkan Chapter 1 dengan note/bookmark, mural, puzzle simbol tiga urutan ARLAND: BUNGA–BUKU–BINTANG dan SOFIA: BINTANG–BUKU–BUNGA, menerima satu surat bersama dan menuju tepi danau. Semuanya adalah draft fiksi sampai fakta hubungan dikonfirmasi.

Pindahkan dialog, quest, event, flag, map metadata ke data lokal yang editable (JSON atau aset data setara). Gunakan ID scene, ID quest, event canon dan flags sebagaimana pada Story Bible. Tambahkan mode replay untuk chapter yang diselesaikan, tanpa merusak progres.

### 7. GAMEPLAY REAL EXPLORATION
Implementasikan karakter bergerak 4 arah dan diagonal ternormalisasi, sprint, idle, animasi, kamera mengikuti pemain, collision kaki karakter, object interaction, pathfinding/follow companion, pengurutan render berdasarkan koordinat Y, layer foreground, door transitions, zona, ambient effects, NPC dialog, quest marker non-intrusif, mini-game dan Memory Book.

Bangun dunia dari tilemap atau scene data yang benar, **jangan sekadar menjadikan PNG latar sebagai map tanpa collision/interaksi**. Mulai dari kamar Arland, kamar Sofia, Plaza Kota, Memory Garden, Kafe Senja dan Tepi Danau. Lokasi tambahan: taman, toko bunga, arcade, Star Path, Lantern Field, Eternal Garden.

### 8. UI & CONTROLS ANDROID
Layar utama, pemilihan karakter, 2 slot save, settings, HUD objective, dialog portrait dengan text reveal opsional/skip, joystick kiri, tombol aksi/sprint kanan, Memory Book dan Pause. Multi-touch wajib; safe area/cutout, resolusi dan rasio bervariasi, ukuran kontrol dapat disesuaikan. Gunakan pixel-perfect/nearest-neighbor untuk sprite; hindari UI terlalu kecil. Lock landscape, immersive mode yang tidak mengganggu gesture navigasi sistem.

### 9. AUDIO, ASSETS, DAN EDITABILITY
Pertahankan sprite/potret Arland–Sofia dari source v0.4 sebagai referensi awal. Optimalkan sprite sheet dengan ukuran frame seragam, naming, atlas, dan animasi konsisten. Semua aset lokal dan mudah diganti di `android/assets/` atau folder asset build yang terdokumentasi. Musik harus orisinal/berlisensi, offline, dan tidak di-stream. Buat referensi daftar asset yang tersedia dan yang belum dibuat. Hindari mengubah desain karakter secara acak.

### 10. SAVE DAN PRIVASI
Simpan file lokal di private app storage, versi schema + migrasi + atomic write + validasi kerusakan. Dua route berbeda. Save game web v0.4 saat ini menggunakan `localStorage`, **JANGAN berjanji dapat dibaca APK native otomatis**. Bila ingin kompatibilitas, buat fitur impor JSON eksplisit dengan pilihan pengguna; jika belum, jelaskan keterbatasan. Tidak boleh ada unggahan file/foto/telemetry ke server.

### 11. PRIORITAS TAHAPAN
**v0.5 – Native Foundation:** buat proyek LibGDX+Gradle Android yang buildable; port input, camera, maps, collision, sprites, route select, dialog, Prologue+Chapter 1, inventory/quest, puzzle, Memory Book dan local save. Jangan mulai Chapter 2 sebelum alur awal benar-benar playable.
**v0.6 – Cozy World:** NPC, indoor/outdoor zones, companion pathfinding, animasi, interaction polish.
**v0.7 – Chapter 2:** dua route, date adventure, photobooth minigame, item kenangan.
**v0.8 – Chapters 3–4:** cooking/decor, hujan dan dua perspektif, puzzle tambahan.
**v0.9 – Chapters 5–6 & Epilogue:** Memory Realm lengkap, finale, bonus route dan free roam.
**v1.0 – Release Hardening:** optimasi perangkat, save compatibility, QA, accessibility, audio, asset polish, signed APK/AAB jika signing credentials tersedia.

### 12. TESTING NON-NEGOTIABLE
Jalankan unit/static tests logika quest/flag, uji manual dua route dari New Game sampai Chapter 1, save/reload, pause/resume, rotasi, force-close, bad save recovery, berbagai DPI, input multi-touch, dan tes perangkat Android dengan airplane mode sejak instalasi. Pastikan tidak ada network request atau internet permission. Validasi bahwa tidak ada tombol dummy, black screen, broken font, missing resource, softlock, collision tembus, map transition rusak, atau crash saat backgrounding.

### 13. OUTPUT WAJIB
1. **Satu ZIP source project Android native lengkap** siap dibuka di Android Studio (`settings.gradle`, `gradlew`, Gradle Wrapper, `core/`, `android/`, asset dan data cerita).
2. **APK debug hasil build nyata**, jika Android SDK dan build tool tersedia; sertakan status build dan path yang diverifikasi. Jangan berpura-pura APK tersedia bila belum dibuat.
3. README Bahasa Indonesia: langkah buka project, Sync Gradle, Run, Build APK, lokasi source/asset/dialog, cara ganti logo/sprite/peta.
4. CHANGELOG pengembangan serta daftar fitur selesai, sebagian, belum, dan pengujian aktual.
5. Story Bible DOCX harus dipertahankan sebagai dokumen desain yang dapat diedit dan tidak disalin sebagai data fakta pribadi tanpa konfirmasi.

**INSTRUKSI TERAKHIR:** Jangan membuat web game lagi, jangan membungkus source HTML dengan WebView, jangan mengubah konsep menjadi platformer side-scrolling. Lanjutkan source v0.4 sebagai referensi migrasi, bukan sebagai runtime. Kerjakan implementasi sungguhan hingga Android native APK offline yang dapat dimainkan, dengan Arland dan Sofia sebagai dua protagonis dan satu kisah cinta utama.
