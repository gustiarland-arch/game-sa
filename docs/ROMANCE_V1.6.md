# Modul Hadiah & Waktu Berdua — v1.6.0

## Tujuan
Menghubungkan sistem koin/pekerjaan v1.5 dengan aktivitas romantis Arland–Sofia tanpa mengubah ending canon. Seluruh transaksi memakai **koin fiksi offline**, tidak pernah pembayaran sungguhan.

## Cara memainkan

1. Selesaikan prolog dan Chapter 1, lalu masuk Chapter 2 atau setelahnya. Pastikan Arland/Sofia **sedang menjadi companion** (ikut berjalan).
2. Dekati pasangan dan tekan **AKSI**. Percakapan opsional yang belum dimainkan diberi prioritas sebagai **♥ Ngobrol**. Sesudahnya muncul **♥ Waktu Berdua**.
3. Tab **Berikan Hadiah** memuat 9 barang yang dijual di 3 toko. Beli barang, simpan di Tas, lalu berikan ke pasangan. Barang habis bila diterima dan bisa dibeli kembali. Nilai kedekatan +3 sampai +10 tergantung hadiah.
4. Tab **Ajak Kencan** memuat tiga aktivitas. Pemain harus berjalan ke area yang sesuai dengan pasangan. Diperiksa jam dunia, saldo, dan batas harian sebelum uang dipotong.
5. Kedekatan ditampilkan di HUD (`♥ N/100`), dan di panel Berdua. Pada nilai 20 dan 50, Memory Book menampilkan kenangan tambahan dan sistem memutar dialog milestone.

## Harga & hadiah

| Kencan | Lokasi | Jam dunia | Biaya | Kedekatan |
|---|---|---|---:|---:|
| Piknik Sederhana | Taman Kota | 08.00–18.00 | 8 koin | +10 |
| Ngopi Berdua | Kafe Senja | 10.00–20.00 | 12 koin | +12 |
| Melihat Bintang | Bukit Bintang | 18.00–25.00 | 18 koin | +16 |

| Hadiah | Kedekatan |
|---|---:|
| Kopi Senja / Kukis Madu / Roti Kayu Manis | +4 / +5 / +5 |
| Tulip Kecil / Mawar Berpita / Buket Senja | +6 / +8 / +10 |
| Permen Stroberi / Kue Lapis / Kartu Bergambar | +3 / +5 / +7 |

**Aturan:** maksimal 1 hadiah + 1 kencan per hari dunia (hari berikutnya bisa lagi). Tidak boleh membeli/melakukan kencan bila saldo kurang; transaksi gagal tidak mengubah data. Kedekatan maksimum 100, tidak berkurang karena absen. Kencan selalu meminta companion aktif dan area/jam cocok. Route Arland dan Sofia mempunyai dialog **kencan berbeda**, dengan tiga tema hadiah dan dua adegan milestone.

## Struktur & integrasi

- Data mentah: `tools/content/romance.py` → `quests.json` (`romance.gifts`, `romance.dates`), naskah `tools/content/naskah_romance.txt` → `story.json`. Jalankan `python3 -I tools/build_content.py`, **jangan edit JSON yang digenerate**.
- Domain: `QuestDb.Gift`/`DateActivity` memetakan data; `QuestEngine.giveGift` dan `startDate` mengubah state secara terkontrol serta menghasilkan aksi cerita. Kedua metode menolak replay.
- UI: `RomanceOverlay` memakai `UiButton` dari LibGDX, dihubungkan dengan `GameScreen` ketika pasangan dekat. Keberhasilan disimpan segera; setelah itu `ActionRunner` menjalankan emote, cutscene, dan dialog.
- Save: `Progress.SCHEMA = 3`, field `affection`, `lastGiftDay`, `lastDateDay`, `dateCounts`, beserta flag kenangan. Schema v1.4=1 dan v1.5=2 tetap dibaca dengan migrasi default. Save per route/slot tetap terpisah.
- Buku kenangan: 6 entri baru untuk hadiah pertama, setiap lokasi kencan, dan milestone hubungan 20/50. Semua fiksi; tidak mengubah kisah utama.

## Pengujian

`bash tools/test_logic.sh`: generator, `check_layout.py`, kompilasi Java 11 dengan stub grafis terbatas, `LogicSelfTest` kedua route termasuk semua side quest, 9 hadiah, 3 kencan, batas harian, uang tidak negatif, migrasi dan round-trip save. `bash tools/test_romance_ui.sh` mengklik hadiah dan kencan dengan stub `Ui` / `Assets`.

**Tidak mencakup** build dengan LibGDX/AGP sesungguhnya, rendering, kontrol touch asli di Android, efek cutscene dalam runtime, performa, atau pengujian di HP. Untuk itu jalankan GitHub Actions/Android Studio dan lakukan playtest fisik. Gradle 8.11.1 gagal diunduh pada lingkungan pengembangan yang digunakan untuk update ini.
