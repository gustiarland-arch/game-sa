# Checklist QA Manual Sebelum Rilis — Arland & Sofia v2.9

Tester mencatat perangkat, API, RAM, GPU, FPS/P90 frame time, suhu, build SHA256, dan hasil PASS/FAIL untuk tiap langkah. Pengujian source headless tidak menggantikan ini.

| ID | Skenario di perangkat | Status |
|---|---|---|
| D01 | Instal APK debug dari fresh install & tampil menu pertama | BELUM DIUJI |
| D02 | Login tidak diminta; permainan offline tanpa izin internet | BELUM DIUJI |
| D03 | Layar landscape, notch/punch-hole dan safe inset | BELUM DIUJI |
| D04 | Pilih route Arland dan buat slot 1 | BELUM DIUJI |
| D05 | Pilih route Sofia dan buat slot 1 tanpa menimpa Arland | BELUM DIUJI |
| D06 | Joystick floating & fixed, kidal/kanan, sensitivitas dan sprint 3 jari | BELUM DIUJI |
| D07 | Buka `Cara bermain`, Memory Book `Prestasi`, dan Pengaturan | BELUM DIUJI |
| D08 | Simpan, force-close, buka ulang, checkpoint tepat | BELUM DIUJI |
| D09 | Update APK v2.8 -> v2.9 tanpa uninstall, slot kedua route tetap ada | BELUM DIUJI |
| D10 | Buka 22 area: collision, portal, prop tidak hilang | BELUM DIUJI |
| D11 | 14 event dunia terikat jam/cuaca/route benar | BELUM DIUJI |
| D12 | 6 minigame berdua dan bonus sehari sekali | BELUM DIUJI |
| D13 | 8 aksi pasangan dan companion tidak menembus dinding | BELUM DIUJI |
| D14 | Animasi idle/walk/poses dan FX pada 3 preset grafis | BELUM DIUJI |
| D15 | 40 musik, 14 ambience, 32 SFX; crossfade dan mute | BELUM DIUJI |
| D16 | Tombol Home/background, resume tanpa freeze/audio tumpuk | BELUM DIUJI |
| D17 | Chapter 1–6 + epilog kedua route; ending canon konsisten | BELUM DIUJI |
| D18 | Prestasi offline tetap terbuka setelah pindah save/route | BELUM DIUJI |
| D19 | Simulasi penuhnya storage, pesan gagal simpan tidak berbohong | BELUM DIUJI |
| D20 | 16 KB page size device, `llvm-readelf` dan zipalign `.so` | BELUM DIUJI |
| D21 | Signed release APK, bundle AAB, cek permission dan signature | BELUM DIUJI |
| D22 | Sesi panjang 60 menit tanpa memory leak/softlock/crash | BELUM DIUJI |
| D23 | 30+ menit pada RAM 3–4 GB, FPS & temperatur dicatat | BELUM DIUJI |
| D24 | Ukuran APK/AAB, Play Console Android vitals, privacy/data safety | BELUM DIUJI |

**Gate:** rilis hanya setelah semua P0 (D01–D10, D15–D17, D19–D21) PASS, P1 ditangani atau diterima secara eksplisit, dan ada persetujuan QA konten/hak cipta.
