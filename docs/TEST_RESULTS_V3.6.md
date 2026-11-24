# Hasil Verifikasi Source v3.6.0

Tanggal: 23 November 2026. Hasil berikut berasal dari pengujian headless dan inspeksi aset; **bukan screenshot/gameplay Android nyata**.

| Pemeriksaan | Hasil |
|---|---:|
| Simulasi semua alur Arland dan Sofia, quest, ekonomi, romansa, save | 25.024 assertions lulus |
| World redesign tahap 4 (9 map, 57 prop, audio, metadata) | 1.194 lulus |
| World redesign tahap 3 | 1.672 lulus |
| World redesign tahap 2 | 1.597 lulus |
| World redesign tahap 1 | 1.392 lulus |
| Visual dasar v3.2 | 1.371 lulus |
| Audit statis Android/source/assets | 1.172 lulus |
| Visual v2.1 | 112 lulus |
| World v2.3 / pose dan layout | 463 lulus + layout OK |
| Couple pose | 528 lulus |
| Audio format v2.4 | 267 lulus |
| Cinematic audio v2.5 | 93 lulus |
| Quest v2.6 | 395 lulus |
| Event dunia v2.7 | 315 lulus |
| Multitouch Android v2.8 | 750 lulus |
| UI pengaturan | 126 lulus |
| Uji dialog, efekt, romansa, save recovery dan sintaks Java | Lulus pada tes yang tersedia |
| Regenerasi tahap 4 diulang | 102 file hasil, 102 hash sama |
| Audio asli v3.5 | Seluruh 86 identik secara SHA-256 |
| Peta + data quest/collision/save | Path dan checksum JSON tetap |
| Build APK Android | **Gagal sebelum kompilasi** (distribusi Gradle tidak tersedia/offline dan Android SDK tidak dikonfigurasi) |

Komparasi paket dengan v3.5: **9 background dan 57 PNG prop runtime berubah**. Tidak ada path dalam `android/assets` yang dihapus atau ditambahkan. Pembersihan hanya menyentuh pratinjau historis `docs/preview` serta satu cache terbuat saat validasi (lihat laporan cleanup).

**Blokir rilis yang masih terbuka:** Gradle/Android SDK, kompilasi dengan dependensi sebenarnya, pengujian APK pada perangkat, FPS/memori, penggunaan GPU, uji touch/audio/notification saat runtime, verifikasi 16 KB native library, dan signing serta kesiapan Play Store. Jangan menyebut proyek ini siap rilis publik hanya berdasarkan tes source.
