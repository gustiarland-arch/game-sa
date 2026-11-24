# Arland & Sofia: Our Little Universe v2.4 — Music & Soundscape

**Status:** source implemented / assets generated / automated headless tests pass. Native Android APK **has not been compiled/tested on a device** in this environment. Do not treat this as a runtime FPS/audio latency report.

## Jumlah dan lokasi aset

| Kategori | Lama (dipertahankan) | Baru v2.4 | Total |
|---|---:|---:|---:|
| BGM / soundtrack (`android/assets/audio/music/*.ogg`) | 8 | 25 | **33** |
| Ambience loop (`android/assets/audio/ambience/*.ogg`) | 0 | 14 | **14** |
| SFX (`android/assets/audio/sfx/*.wav`) | 3 | 25 | **28** |
| **TOTAL** | **11** | **64** | **75** |

Semua BGM tambahan merupakan lagu instrumental **asli berbasis sintesis prosedural**, bukan lagu komersial, stem, hasil scraping, atau salinan musik dari game lain. Sumber komposisi ada di `tools/gen_soundscape_v24.py`, tidak ada input audio eksternal. Aset audio yang dihasilkan telah dikemas di ZIP ini sehingga **tidak perlu menjalankan generator untuk memainkan game atau mengedit aset**.

### Musik: area dan konteks

| Lokasi atau suasana | Musik |
|---|---|
| Menu utama | `menu_theme` |
| Kamar Arland / Sofia (pagi / sore) | `home_morning`, `home_evening` |
| Plaza / Jalan Kota (pagi / sore / malam) | `city_morning`, `city_evening`, `city_night` |
| Taman Kota (siang / senja) | `park_blossom`, `park_sunset` |
| Tepi danau / dermaga (siang / malam) | `lake_breeze`, `lake_moon` |
| Toko bunga | `flower_shop` |
| Kafe dan dapur | `cafe_waltz` |
| Perpustakaan | `library_whisper` |
| Arcade | `arcade_neon` |
| Distrik perumahan | `neighborhood_day` |
| Memory Garden | `memory_bloom` |
| Lantern Field | `lantern_glow` |
| Hutan Bisik | `whisper_woods` |
| Arsip rahasia | `archive_mystery` |
| Star Path | `star_road` |
| Starfall Village | `star_village` |
| Bukit Bintang | `hill_stars` |
| Gua Kristal | `crystal_echo` |
| Eternal Garden | `eternal_promise` |
| Hujan outdoor (kecuali world magis) | `rain_lullaby` |

Track cerita/quest yang secara eksplisit menetapkan musik **selalu didahulukan** dan 8 musik lama (`town`, `memory`, `cafe`, `rain`, `night`, `star`, `tender`, `game`) tetap bisa diputar. Menu **Pengaturan → Soundtrack beragam: Dinamis/Klasik** mengembalikan pemilihan musik lokasi lama bila pemain menghendaki, tanpa menghapus file baru.

### Ambience mandiri (14 loop)

`birds_morning`, `city_day`, `wind_leaves`, `park_birds`, `lake_water`, `cafe_room`, `library_room`, `rain_outdoor`, `rain_window`, `night_crickets`, `forest_wind`, `magic_chimes`, `cave_drips`, `arcade_hum`.

Ambience dikendalikan **secara independen** dari musik, termasuk perpindahan halus saat berganti area/cuaca dan `null` saat lokasi tidak membutuhkan ambience. Berhenti saat kembali ke menu utama. Musik dan ambience masing-masing memiliki crossfade (±1,3 detik untuk BGM; ±2,2 detik untuk ambience) sehingga perpindahan tidak tiba-tiba.

### SFX tambahan (25 file)

`step_grass`, `step_stone`, `step_wood`, `door_open`, `door_close`, `bell_shop`, `coin`, `gift`, `heart`, `hug`, `selfie`, `highfive`, `quest_complete`, `scene_transition`, `notification`, `splash`, `bird_chirp`, `cat_meow`, `dog_bark`, `duck_quack`, `wind_gust`, `rain_drop`, `lantern`, `page_turn`, `menu_confirm`.

SFX yang telah dihubungkan langsung: langkah berdasarkan permukaan dengan volume rendah dan cooldown; perpindahan area/pintu; elus hewan (suara sesuai jenis tertentu); pembelian barang/koin; hadiah/kencan/interaksi pasangan; pemeriksaan buku/objek; klik menu; peristiwa quest dan sebagian efek cutscene. SFX lain disertakan sebagai **library siap pakai** untuk event tambahan mendatang, jadi jangan menganggap semua 25 telah memiliki trigger gameplay khusus.

## Sistem kode

- `logic/SoundscapePlan.java`: peta 22 lokasi, kondisi jam/cuaca, override cerita, preset soundtrack klasik, daftar ID musik/ambience/SFX. Kode murni Java dapat diuji tanpa LibGDX.
- `AudioManager.java`: audio offline dengan dua kanal `Music` yang terpisah (`BGM`, `ambience`), crossfade volume, `duck()` ketika dialog/cutscene, `pauseAll()` ketika Android background, ambience di-mix lebih pelan daripada BGM agar tidak menutupi melodi, cleanup `dispose()` agar stream tidak menumpuk.
- `Assets.java`: **lazy-load SFX** saat efek pertama kali dimainkan, cache jika file gagal dimuat agar tidak spam error/IO.
- `GameScreen.java`: memetakan suara menurut lokasi/jam/cuaca, langkah dan interaksi, tanpa mengubah collision atau story logic. Quest override musik tetap digunakan.
- `ui/SettingsPanel.java` & `logic/Settings.java`: slider **Volume musik**, **Volume ambience**, **Volume efek**, toggle **Soundtrack beragam** dan **Suara langkah**. Pengaturan lama `settings.json` (schema 1) tetap dapat dimuat dengan default yang aman; schema settings sekarang 2. **Save progres/slot tetap schema 5**, tidak dimigrasikan.
- `android/assets/audio/soundscape_v24.json`: metadata aset baru, durasi, path, BPM, dan kategori untuk memudahkan edit.

## Mengganti musik / audio lewat VS Code

1. Buka folder source proyek `ArlandSofia/` di VS Code.
2. File musik lokasi ada di `android/assets/audio/music/`. Misalnya ganti `park_blossom.ogg` dengan file OGG Vorbis milik Anda dengan **nama yang sama**.
3. Jika mengganti ambience, gunakan `android/assets/audio/ambience/<id>.ogg`. Jika mengganti SFX, gunakan WAV PCM 16-bit di `android/assets/audio/sfx/<id>.wav`.
4. Musik akan diputar loop: supaya tidak terdengar jeda, edit awal dan akhir audio agar dapat bersambung. Contoh konversi:

   ```bash
   ffmpeg -i musik_saya.wav -c:a libvorbis -q:a 3 android/assets/audio/music/park_blossom.ogg
   ffmpeg -i suara_saya.wav -ar 22050 -ac 1 -c:a pcm_s16le android/assets/audio/sfx/gift.wav
   ```

5. Untuk **menambah ID baru**, perbarui array `SoundscapePlan.MUSIC`, `AMBIENTS`, atau `SFX` dan `SoundscapePlan.musicFor(...)`, lalu sertakan file yang cocok. Jangan menaruh path di input pemain.
6. **Penting:** generator membuat ulang aset procedural dan akan menimpa file v2.4 yang namanya sama. Simpan perubahan aset kustom di luar target generator atau nonaktifkan langkah `gen_soundscape_v24.py` di `tools/build_all.sh` jika ingin mempertahankan audio buatan sendiri.

## Reproduksi generator & tes

```bash
python3 -m pip install numpy scipy Pillow fontTools
# ffmpeg/ffprobe harus tersedia di PATH
python3 tools/gen_soundscape_v24.py android/assets/audio
python3 tools/test_audio_v24.py android/assets/audio
bash tools/test_soundscape_plan.sh
bash tools/test_audio_manager.sh
bash tools/test_settings_ui_v24.sh
bash tools/test_logic.sh
bash tools/test_romance_ui.sh
```

`gen_music2.py` membuat ulang 8 track klasik. `gen_soundscape_v24.py` menambah 25 BGM + 14 ambience + 25 SFX dan tidak menyentuh file klasik.

**Batasan penting:** test audio v2.4 memvalidasi codec/durasi/file, pemilihan soundtrack, perilaku audio engine dengan stub (`Music` dan `Sound` tiruan), serta tombol UI; **bukan** tes volume suara sebenarnya pada HP atau sinkronisasi engine OpenGL/Android. Perlu kompilasi `:android:assembleDebug` dan playtest perangkat untuk validasi runtime sesungguhnya. Jika distribusi Gradle tidak bisa diunduh karena DNS, build terhenti sebelum kompilasi aplikasi.
