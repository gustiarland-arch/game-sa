# v2.8 — Android Touchscreen, Landscape UI & Render Optimization

## Ruang lingkup

Dikembangkan langsung dari ZIP/source v2.7.0, tanpa mengganti engine Java/LibGDX. Tidak ada naskah, route, quest, peta, collision, sprite, musik, atau efek suara yang dihapus. **Progress save schema 6 tidak diubah**. Pengaturan `settings.json` menggunakan schema 3 dengan nilai awal yang kompatibel dengan schema 1/2.

## Pengaturan baru di menu

Menu **Pengaturan** dipisah menjadi tiga tab, agar target sentuh tidak terlalu kecil di layar lanskap.

- **Audio**: Volume musik, ambience, efek, mode soundtrack, dan suara langkah.
- **Tampilan**: Kecepatan teks, penanda misi, kualitas visual, kamera halus.
- **Kontrol**: Ukuran kontrol, transparansi kontrol, **tangan dominan** Kanan/Kiri, **joystick** Melayang/Tetap, dan **sensitivitas joystick** 70–150%.

Mode **Kanan** (default) menempatkan joystick di kiri dan AKSI/LARI di kanan. **Kiri** mencerminkan posisi joystick serta tombol aksi/lari. **Melayang** (default) memunculkan joystick di tempat jari pertama menyentuh sisi joystick; **Tetap** menempatkannya pada posisi tetap dan hanya menerima sentuhan di sekitar alasnya.

Semua kontrol memakai `getSafeInsetLeft/Right/Bottom()` agar tidak menabrak tepi yang tertutup notch/navigation bar. Hit-test menggunakan koordinat viewport UI terproyeksi, bukan piksel layar mentah.

Logika pemetaan jari berada pada `core/src/main/java/com/arlandsofia/olu/logic/TouchInputModel.java` (pure Java), sedangkan renderer sprite joystick ada di `game/TouchControls.java`. Tiga pointer berbeda dapat menjalankan arah, LARI, dan AKSI secara bersamaan; satu pointer tidak dapat mengambil alih tombol yang ditahan jari lain. Deadzone analog 18% mencegah character drift ketika jari sedikit bergeser. Tombol AKSI memicu tepat satu peristiwa per tap.

Untuk mengubah ukuran dasar joystick, radius dan tombol, edit `TouchInputModel.layout()`. Untuk mengubah grafik dan warna tombol, ganti gambar `android/assets/ui/joy_base.png`, `joy_knob.png`, `btn_action.png`, `btn_round.png`, `btn_round_on.png` dengan nama/ukuran yang sesuai. Pengaturan dan teks UI: `ui/SettingsPanel.java`.

## Performa rendering

- **Prop lantai** yang berada di luar kamera sekarang disaring sebelum dipanggil ke SpriteBatch, sama dengan prop layer lain.
- Culling tambahan untuk sprite interaksi, NPC kota, hewan, dan aktor cutscene yang berada jauh di luar kamera. Ini **tidak** mengubah collision, jadwal, AI, atau spawn; hanya melewati proses menggambar saat tidak terlihat.
- Ukuran tekstur untuk culling disimpan sebagai dimensi ringan per prop/area (`propMetrics`) termasuk varian alternatifnya. Cache dibersihkan saat berganti area; tekstur asli tetap dimiliki dan dibuang oleh Assets sesuai lifecycle awal.
- Daftar marker interaksi untuk renderer digunakan ulang antarfame alih-alih membuat `new ArrayList` tiap frame. Pool depth sorting lama tetap dipertahankan.
- `GameScreen.pause/resume` kini memanggil lifecycle parent yang mengontrol `AudioManager`, sehingga musik dan ambience dijeda serta dilanjutkan saat aplikasi keluar/masuk background.

**Tidak ada angka FPS yang diklaim**: optimasi ini diuji lewat inspeksi kode dan pengujian logika, bukan benchmark GPU pada HP.

## Build APK Android

- Kode tersedia lengkap dalam ZIP bersama **semua 86 audio, 22 peta, animasi dan data cerita**.
- Untuk build memakai komputer dengan **JDK 17, Android SDK 35**, dan akses internet pertama kali guna mengunduh **Gradle 8.11.1 / AGP 8.7.3 / LibGDX 1.13.1**.
- Perintah di root: `./gradlew :android:assembleDebug` pada Linux/macOS, atau `gradlew.bat :android:assembleDebug` pada Windows. APK debug hasil sukses seharusnya di `android/build/outputs/apk/debug/android-debug.apk`.
- GitHub Actions `.github/workflows/build-apk.yml` menjalankan regression suite dan melakukan build; artifact bernama `ArlandSofia-v2.8-debug-apk` jika workflow berhasil.
- **Status sesi ini:** percobaan build terhenti sebelum kompilasi dengan `UnknownHostException: services.gradle.org`; Android SDK juga tidak tersedia di lingkungan kerja ini. Java syntax parse/headless test tidak membuktikan APK maupun layar touch benar-benar berjalan pada perangkat.

## Pengujian yang tersedia

- `bash tools/test_controls_v28.sh`: model multi-touch, safe inset/landscape, handedness, floating/fixed, deadzone, sensitivitas, menu/tab/settings serialization.
- `bash tools/test_logic.sh`: kedua route hingga epilog, side quest, ekonomi, romance, save dan migrasi, serta world events.
- `bash tools/test_visual_fx.sh`, `bash tools/test_audio_manager.sh`, `python3 tools/test_world_events_v27.py`: regresi renderer effect, stream audio, dan event dunia.

## Kompatibilitas

Save progress: **schema 6**, tidak naik dan tetap kompatibel dengan v2.7. Settings: schema **3**, `fromMap()` membaca data lama dan memberi default `leftHanded=false`, `floatingJoystick=true`, `joystickSensitivity=1.0`. Bila ingin memakai save dari versi lama, tetap buat backup di perangkat sebelum update APK. Karena gameplay dan bab tidak berubah, tidak perlu mengulang cerita.
