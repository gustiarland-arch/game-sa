# Dukungan layar tablet Android — v4.3

- Game tetap Android native Java + libGDX dengan **orientasi landscape**.
- Layout v4.3 mengikuti ruang UI ExtendViewport, bukan ukuran layar tetap.
- Profil diuji secara headless: telepon 16:9, tablet 16:10, 4:3, perangkat dengan inset/notch, dan ultrawide.
- Menu pemilihan route sekarang dipusatkan secara vertikal pada layar tinggi (4:3).
- Title/Route panorama menggunakan `Ui.imageCover`, sehingga proporsi ilustrasi terjaga (cropping, bukan stretching).
- Pause menu mengukur tinggi layar dan safe insets sebelum menempatkan baris.
- Joystick dan tombol aksi memakai `AdaptiveLayoutV43.controlScale` serta safe area.
- Panel Settings memanfaatkan ruang ekstra tablet tanpa mengubah format save.
- `AndroidManifest.xml` mengizinkan resize aplikasi; tetap meminta `sensorLandscape`.
- **Belum diverifikasi secara runtime** di tablet Android atau emulator: screenshot perangkat/FPS dan multi-window harus diuji setelah APK dapat dibangun.

Uji headless: `bash tools/test_tablet_v43.sh`.
