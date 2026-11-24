# Living World Events — v2.7.0

## Tujuan

Menambahkan kegiatan harian yang dapat dimainkan langsung tanpa mengganti jalur Arland/Sofia, ending canon, 22 peta, NPC schedule, audio, minigame, ataupun sistem quest lama. Semua cerita merupakan **draft fiksi**.

## 14 event dunia

| ID | Tempat | Jam game | Cuaca | Min. chapter | POV |
|---|---|---|---|---|---|
| pagi_plaza | Plaza Kota | 07:00–10:00 | Cerah/berawan | C02 | Keduanya |
| kafe_catatan | Kafe Senja | 10:00–14:00 | Bebas | C03 | Keduanya |
| ikan_pondok | Taman Kota | 13:00–18:00 | Bebas | C02 | Keduanya |
| senja_danau | Tepi Danau | 16:00–19:00 | Cerah/berawan | C02 | Keduanya |
| perpustakaan_senyap | Perpustakaan | 09:00–17:00 | Bebas | C02 | Keduanya |
| melati_merangkai | Toko Bunga | 10:00–18:00 | Bebas | C02 | Keduanya |
| arcade_tiket | Arcade | 15:00–22:00 | Bebas | C03 | Keduanya |
| halte_hujan | Jalan Kota | 11:00–24:00 | Hujan | C04 | Keduanya |
| dermaga_papan | Dermaga | 16:00–19:00 | Bebas | C03 | Keduanya |
| hutan_gema | Hutan Bisik | 09:00–17:00 | Bebas | C05 | Keduanya |
| desa_bintang | Starfall Village | 18:00–24:00 | Bebas | C05 | Keduanya |
| bukit_teleskop | Bukit Bintang | 19:00–25:00 | Cerah/berawan | C03 | Keduanya |
| arlan_peta | Perumahan | 09:00–17:00 | Bebas | C03 | Arland |
| sofia_halaman | Perpustakaan | 10:00–17:00 | Bebas | C03 | Sofia |

### Cara bermain

1. Mainkan cerita hingga chapter minimum event dan aktifkan companion.
2. Pergi ke lokasi pada jam game dan cuaca yang cocok. Game menampilkan tulisan **✦ EVENT HARI INI** di bagian misi dan penanda khusus pada dunia bila petunjuk diaktifkan.
3. Dekati penanda, tekan **aksi**, dan ikuti dialog berdasarkan route pemain. Setelah dialog selesai, reward dicatat.
4. Tiap event memberi bonus sekali per hari game; event dapat dimainkan lagi pada hari berikutnya. Flag `WORLD_EVENT_<ID>_ONCE` membuka satu kenangan dan tidak pernah diulang sebagai item duplikat.

### Pengubahan melalui VS Code

- `tools/content/world_events_v27.py`: tambah/ubah id, title, area, anchor, hours, chapter, weather, route, coins, affection. Posisi event disaring agar tidak berada di collision. Event dimasukkan ke katalog `quests.worldEvents` serta `quests.side` otomatis.
- `tools/content/naskah_world_v27.txt`: edit adegan `WE27-<ID>-A` dan `WE27-<ID>-S` untuk dialog POV unik. Jangan hapus salah satu adegan yang dipakai event, agar generator memvalidasi semua referensi.
- `tools/build_content.py`: memanggil generator event setelah data map/anchor dimuat, menghasilkan JSON di `android/assets/data`. Jalankan `python3 -I tools/build_content.py` setelah edit.
- `core/src/main/java/.../logic/QuestDb.java`, `QuestEngine.java`, `Progress.java`, `ActionRunner.java`: katalog, validasi, hadiah, penyimpanan dan antrean scene. `screens/GameScreen.java`: penanda, prompt, HUD, rutinitas NPC.

### Save dan kompatibilitas

Schema progres bertambah **5 → 6**. `worldEventDays` dan `worldEventCounts` menggunakan map ID ke bilangan hari/total. Loading schema 1–5 menginisialisasi keduanya kosong sambil mempertahankan koin, item, kedekatan, quest, scene, serta snapshot. **Backup save** sebelum mengganti APK, karena versi lama tidak dapat membaca schema baru. Tidak ada jaringan, iklan, akun atau IAP.

### Pengujian

```
python3 -I tools/build_content.py
bash tools/test_logic.sh
python3 tools/test_world_events_v27.py
python3 tools/test_story_v26.py
bash tools/test_romance_ui.sh
python3 tools/test_cinema_v25.py
./gradlew :android:assembleDebug
```

`test_logic.sh` memverifikasi kedua route sampai ending, quest, event area/waktu/cuaca/route, daily anti-farming, Memory Book, migrasi save, dan sistem lama. Pengujian yang memakai stub **tidak menguji rendering, decoding musik, instalasi APK, atau FPS perangkat**. Dalam lingkungan ini, Gradle wrapper belum bisa mengunduh distribusi dari `services.gradle.org` sehingga APK asli belum dikompilasi.
