# Visual Overhaul v2.0.0 — Arland & Sofia: Our Little Universe

## Tujuan dan batasan

Pembaruan melanjutkan v1.9.0 **tanpa mengganti engine LibGDX**, tidak mengubah save permainan schema 4, dan tidak menghapus naskah canon, dua route, mekanik ekonomi, atau Memory Book. Semua efek dibuat untuk permainan offline dan dapat disunting melalui VS Code dan aplikasi pengedit PNG. Fokus: lebih hidup, tetap nyaman pada Android menengah.

## Pengaturan kualitas

| Pilihan | Perubahan grafis | Untuk |
|---|---|---|
| Hemat (0) | Partikel dekoratif minimum, tanpa glow/riak/vignette tambahan, hujan ±48 garis per frame | GPU/RAM terbatas |
| Seimbang (1, default) | Glow kontekstual, percik air, langkah, kelopak, riak, hujan ±90 garis | Kebanyakan perangkat |
| Sinematik (2) | Glow lebih besar, foreground sakura lebih banyak, riak dan partikel lebih padat, vignette lembut, hujan ±140 garis | Perangkat lebih kuat |

*Kamera halus* adalah opsi terpisah. Keduanya tersimpan pada `Settings.toMap()/fromMap()` dan memiliki default untuk pengaturan versi lama; tidak mengubah progres cerita.

## Implementasi runtime

- `core/src/main/java/com/arlandsofia/olu/logic/CameraRig.java`: interpolasi mengikuti waktu, bukan jumlah frame. `reset()` saat berpindah area, `snap()` untuk awal dan shot kamera cutscene, `follow()` untuk eksplorasi.
- `core/src/main/java/com/arlandsofia/olu/game/WorldFx.java`: fixed pool 48 slot, siklus hidup partikel debu, cipratan langkah di bawah hujan, dan hati (khusus kedekatan tinggi dan pasangan berdekatan). Kelopak foreground, ripple air, serta vignette juga dirender dari sini.
- `core/src/main/java/com/arlandsofia/olu/screens/GameScreen.java`: integrasi pada loop update/render, preset quality, kondisi glow malam/hujan/ruangan, depth-sorting menggunakan objek pooled, dan culling prop yang tidak tampak di kamera. Efek digambar setelah karakter tetapi sebelum tint/cutscene.
- `core/src/main/java/com/arlandsofia/olu/game/DialogBox.java`: gerak potret sangat kecil pada mode sinematik dan pemisah halus saat dialog. Input, dialog, cutscene, dan callback tidak diubah.
- `core/src/main/java/com/arlandsofia/olu/ui/SettingsPanel.java`: delapan baris pengaturan, dua baris terakhir Kualitas visual dan Kamera halus. Tidak memakai server atau API eksternal.

## Mengedit aset visual

Aset lengkap tersimpan di `android/assets/fx/`:

| File | Efek | Generator |
|---|---|---|
| `vignette.png` | Bayangan tepi layar transparan | `tools/gen_visual_fx.py` |
| `dust.png` | Debu lembut pada langkah | `tools/gen_visual_fx.py` |
| `splash.png` | Cipratan air pada langkah | `tools/gen_visual_fx.py` |
| `ripple.png` | Riak pada area air | `tools/gen_visual_fx.py` |
| `petal.png` | Kelopak di foreground | `tools/gen_visual_fx.py` |
| `heart.png` | Hati kecil saat affection tinggi | `tools/gen_visual_fx.py` |

Untuk mengganti gambar manual, edit PNG di `android/assets/fx/` dengan transparansi RGBA dan pertahankan nama file. **Jangan jalankan generator setelah mengedit file secara manual**, karena akan menimpa modifikasi. Untuk mengganti bentuk melalui source, edit `tools/gen_visual_fx.py` kemudian jalankan `python3 tools/gen_visual_fx.py android/assets`. `bash tools/build_all.sh` akan menjalankan generator ini saat rebuild menyeluruh.

## Konten route terbaru

| Side quest | Route | Bab mulai | Lokasi berurutan | Hadiah |
|---|---|---|---|---|
| Sketsa Setelah Gerimis | Arland | C04 | Halte Jalan Kota → Tepi Dermaga → Meja Perpustakaan | Sketsa Gerimis + kenangan |
| Palet Langit Sofia | Sofia | C05 | Gazebo Taman Kota → Toko Bunga → Dek Bukit Bintang | Palet Langit + kenangan |

Misi khusus Arland/Sofia dari v1.9 dan v2.0 hanya tampil pada jurnal dan simulator route masing-masing. Flag, item, dan Memory Book memakai mekanisme save generik existing.

## Cara uji

Dari folder root `ArlandSofia/`:

```bash
python3 -I tools/build_content.py
python3 -I tools/check_layout.py android/assets
bash tools/test_logic.sh
bash tools/test_romance_ui.sh
bash tools/test_visual_fx.sh
./gradlew :android:assembleDebug
```

**Yang dapat dibuktikan oleh uji headless:** validitas data dan urutan quest, kompatibilitas state settings, perilaku numerik CameraRig, tersedianya enam aset PNG, parsing syntax Java, smoke method FX dengan stub.

**Yang belum dapat dibuktikan tanpa APK asli/perangkat:** build runtime Android/LibGDX, persepsi visual sebenarnya, fps rendah/tinggi, UI touch, jitter di GPU tertentu, jeda saat berpindah map, dan thermal/performa baterai. Build pada lingkungan sesi ini tertahan di unduhan Gradle 8.11.1 (`UnknownHostException`). Jangan menganggap smoke test sebagai QA Android selesai.

## Prioritas QA perangkat saat APK tersedia

1. Perangkat resolusi 16:9 dan 20:9, termasuk safe inset kamera/notch.
2. Semua preset kualitas pada area kota terang, malam, hujan Chapter 4, Gua Kristal, dan Eternal Garden.
3. Kamera halus saat belok, berlari, masuk pintu, keluar gua, dan sinematik yang mengubah zoom.
4. Efek di lokasi berair: tidak ada riak di daratan, tidak terjadi glitch di sisi layar.
5. Test save dari v1.8/v1.9 dengan inventory dan slot yang sudah ada, lalu replay chapter baru.
6. Validasi profiling: FPS, RAM Java, VRAM/texture, spike GC, dan waktu load map.
