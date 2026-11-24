# Living Romance — Panduan v2.2.0

## Prinsip

Mengembangkan source Java/LibGDX v2.1 **tanpa rewrite**. Dua route berbeda sudut pandang, satu ending canon. Semua aksi romantis bersifat opsional. Gameplay tidak memakai internet atau layanan eksternal.

## Memainkan

1. Mainkan minimal sampai Chapter 2, ajak Arland/Sofia sebagai companion.
2. Dekati pasangan ketika tidak sedang dalam misi/cutscene. Jika ada dialog `♥ Ngobrol` yang belum diselesaikan pada area tersebut, selesaikan terlebih dahulu.
3. Pilih `♥ Waktu Berdua` → tab **Aksi Berdua**. Halaman berikutnya memakai tombol `>`.
4. Tekan `Lakukan` bila tersedia. Bila belum, panel menjelaskan jam, lokasi, cuaca atau affection yang diperlukan.
5. Untuk **Gandengan Tangan**, mode berpasangan aktif sesudah cutscene sampai dipilih `Lepaskan`, companion keluar, atau save terpisah. Memilihnya kembali di hari yang sama hanya mengaktifkan mode; bonus tidak diulang.

## Katalog aksi

| ID | Aksi | Area yang didukung | Jam | Min hati | Bonus |
|---|---|---|---|---:|---:|
| `gandengan` | Bergandengan tangan | Plaza, Taman Kota, Tepi Danau, Perumahan, Bukit Bintang | 07:00–02:00 | 0 | +2 |
| `pelukan` | Pelukan hangat | Plaza, Taman Kota, Tepi Danau, Bukit Bintang, Starfall Village | 07:00–02:00 | 20 | +4 |
| `bersandar` | Bersandar di bahu | Taman Kota, Tepi Danau, Bukit Bintang, Starfall Village | 08:00–01:00 | 15 | +3 |
| `selfie` | Foto berdua | Plaza, Taman Kota, Tepi Danau, Bukit Bintang | 08:00–22:00 | 10 | +2 |
| `tos` | Tos penyemangat | Area mana pun jika companion aktif | 07:00–02:00 | 0 | +1 |
| `menari` | Menari kecil | Plaza, Taman Kota, Starfall Village | 09:00–23:00 | 40 | +4 |
| `lihat_senja` | Menikmati senja | Tepi Danau, Bukit Bintang | 16:00–19:00 | 20 | +3 |
| `janji_bintang` | Janji bintang | Bukit Bintang, Starfall Village | 18:00–01:00, cerah/berawan | 60 | +5 |

Waktu 25:00/26:00 adalah jam dunia melewati tengah malam, sesuai sistem game yang sudah ada. Seluruh aksi punya dua adegan berbeda menurut route pemain, ditambah delapan entri Memory Book.

## Source yang bisa diedit

- **Daftar aksi, jam, syarat, bonus**: `tools/content/romance.py` (`ROMANCE['coupleActions']`)
- **Naskah**: `tools/content/naskah_couple_v22.txt`
- **Kelas parser**: `core/src/main/java/com/arlandsofia/olu/logic/QuestDb.java` (`CoupleAction`)
- **Validasi dan anti-spam**: `core/src/main/java/com/arlandsofia/olu/logic/QuestEngine.java`
- **Panel**: `core/src/main/java/com/arlandsofia/olu/game/RomanceOverlay.java`
- **Aktor dan animasi**: `tools/gen_poses.py` → `characters/<nama>/poses.png`, `Actor.java`, `CutscenePlayer.java` perintah `pair`, `GameScreen.java` (gandengan dalam eksplorasi)
- **Save**: `logic/Progress.java` schema 5. Save versi 1–4 dimigrasi otomatis.

Perintah membuat ulang data setelah mengedit naskah: `python3 tools/build_content.py`. Setelah mengubah pose: `python3 tools/gen_poses.py android/assets`. Generator menyimpan delapan pose lama pada indeks yang sama agar cutscene sebelumnya tetap valid. **Sheet asli `walk.png` tetap disimpan**.

## Pengujian dan batasannya

```sh
bash tools/test_logic.sh
bash tools/test_romance_ui.sh
python3 tools/test_couple_v22.py
python3 tools/test_visual_v21.py
bash tools/test_visual_fx.sh
./gradlew :core:test :android:assembleDebug
```

Empat uji pertama serta smoke test berbasis stub bukan pengganti build APK asli. Di lingkungan sesi pengembangan, unduhan Gradle 8.11.1 gagal karena DNS `services.gradle.org`, sebelum kompilasi. QA perangkat Android (sprite clipping, animasi sepasang karakter, stabilitas frame rate, touch pada rasio layar berbeda) **masih diperlukan**.

## Kompatibilitas

Schema save game meningkat dari 4 ke **5** untuk `coupleActionDays`, `coupleActionCounts`, `holdingHands`. Semua field yang ada sejak v2.1 tetap dipertahankan. `holdingHands` hanya diterapkan jika companion aktif saat save dibuka. Save v2.2 belum tentu dapat dibuka oleh v2.1; buat backup sebelum mengganti APK. Tidak ada APK dalam source ZIP.
