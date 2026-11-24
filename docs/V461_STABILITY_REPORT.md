# Arland & Sofia v4.6.1 — Stability & Integration Report

**Tanggal:** 23 November 2026  |  **Basis:** v4.6.0 full Android Studio source | **Fokus:** perbaikan nyata tanpa pengurangan fitur.

## Perubahan pada kode

1. `RomanceEngineV45.syncWorldDay`: sekarang menolak sinkronisasi ke hari yang lebih lama tanpa mengubah state. Mencegah reward tanggal/dialog ganda akibat rollback save utama.
2. `LivingWorldV46.wanderTarget`: overload dengan sequence waypoint per NPC. Pilihan lokasi berikutnya bervariasi walau jam game masih pada jendela waktu yang sama. Jalur tetap memeriksa collision sepanjang segmen.
3. `GameScreen.updateNpcs`: menambahkan sequence waypoint yang diperbarui saat NPC memilih tujuan baru; tidak ada teleportasi saat jalur terhalang.
4. `RomanceV45Screen`: gesture swipe mengikuti pointer utama; sentuhan jari lain tidak membalik halaman; gesture dibersihkan pada cancel. Menampilkan pesan jika save cerita utama lebih tua dari save romance.
5. `RomanceSaveV45.resetSlot` dan `SlotScreen`: penanganan kegagalan reset storage dengan pesan eksplisit saat membuat atau menghapus slot.
6. `docs/V44_WORLD_MANIFEST.json`: memperbaiki satu checksum props yang tertinggal, dengan memeriksa kecocokan byte asli terhadap ZIP v4.4; data runtime tidak diubah.
7. `build.gradle`, `OluGame.VERSION`: versi 4.6.1, Android versionCode 47.

## Regresi yang telah diperiksa

| Pemeriksaan | Hasil |
|---|---|
| Romance `tools/test_romance_v46.sh` | PASS — 51 assertions (termasuk rollback) |
| Living World `tools/test_living_world_v46.sh` | PASS — 12 assertions (termasuk repeat waypoint) |
| Tablet layout `tools/test_tablet_v44.sh` | PASS — 390 checks |
| Save migrations `tools/test_maps_v4_save.sh` | PASS — 38 assertions |
| World visual and audio `python3 tools/test_world_v44.py` | PASS — 2.197 checks |
| Audio engine `bash tools/test_audio_manager.sh` | PASS — 956 checks |
| Map audit `python3 tools/test_maps_v4.py` | PASS — 302 checks |
| Romance overlay `bash tools/test_romance_ui.sh` | PASS — smoke input |
| Legacy UI type check `bash tools/test_v30_ui_compile.sh` | PASS — stubs |
| All Java 11 source `tools/JavaSyntaxCheck.java` | PASS — 61 file syntaxes |
| RomanceV45Screen + save service | PASS — Java 11 type check menggunakan stubs (bukan real LibGDX runtime) |
| Full logic (`tools/test_logic.sh`) | Log salinan QA berakhir dengan **SEMUA LULUS: 24686 pemeriksaan** |
| ZIP integrity | Dicatat setelah pembuatan ZIP final |

## Yang masih memerlukan Android Studio/perangkat

**Belum diklaim selesai:** Build debug/release melalui AGP 8.10.0 dan Gradle 8.11.1; runtime OpenGL/LibGDX, performa RAM/FPS, uji sentuhan fisik Android pada perangkat berbeda, uji enam jam tiap route, ending, dan uji migration terhadap semua save riil pengguna. Alat offline/stubs tidak menggantikan pengujian ini.

## Menjalankan

1. Ekstrak ZIP dan buka **root proyek** yang berisi `settings.gradle` di Android Studio.
2. Gunakan JDK 17, Android SDK 36, lalu Gradle Sync dan jalankan modul `android`.
3. Jalankan script regression di atas bila mengubah Java/JSON/assets; lakukan backup save pengguna sebelum pengujian pada perangkat.
4. Source, 22 map, visual editable, audio, story dan kedua route tetap ada dalam paket.

Tidak ada perubahan GitHub pada proses penyempurnaan ZIP ini.
