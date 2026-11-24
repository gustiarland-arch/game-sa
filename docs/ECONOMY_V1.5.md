# Modul Ekonomi & Pekerjaan — v1.5.0

Game tetap 2D native, offline, lanskap, Bahasa Indonesia. Sistem ekonomi dibuka mulai Chapter 2.

## Aktivitas pemain

| Tempat | Aktivitas | Hadiah / harga | Waktu permainan |
|---|---|---|---|
| Kafe Senja | Belanja: kopi, kukis, roti | 12 / 16 / 20 koin | C02+ |
| Kafe Senja | Shift barista (Tuang Teh) | +20 koin, skor ≥1 | 08:00–21:00 |
| Toko Bunga Melati | Belanja: tulip, mawar, buket | 12 / 18 / 25 koin | C02+ |
| Toko Bunga Melati | Shift rangkai bunga (8 tahap) | +22 koin, skor ≥1 | 08:00–19:00 |
| Kios Bu Rini (Jalan Kota) | Belanja: permen, kue, kartu | 8 / 15 / 10 koin | C02+ |
| Halte Distrik Perumahan | Terima 3 surat dari Pak Pos | +28 koin setelah surat ketiga | 07:00–19:00 untuk mulai |

Tiga alamat pengiriman: Plaza Kota (dekat bangku barat), Jalan Kota (dekat toko roti), Tepi Danau (dekat bangku timur). Ikuti label interaksi dan HUD kurir. Pekerjaan punya limit satu upah per hari. Pembayaran menggunakan koin fiksi, bukan uang sungguhan.

## Arsitektur

- **Definisi konten:** `tools/content/economy.py` dieksekusi oleh `tools/build_content.py`; katalog `shops`/`jobs` menjadi bagian `quests.json`. Jangan edit JSON assets langsung.
- **Peta:** memakai anchor yang sudah ada; tidak mengubah props/collision/membuat map baru.
- **Logika:** `QuestDb.Shop`, `QuestDb.Job`, `QuestEngine.purchase`, `completeWork`, `startDelivery`, `deliver`; pemeriksaan saldo dan waktu dilakukan di game.
- **Presentasi:** `ShopOverlay.java` untuk transaksi item; `ActionRunner` mengelola `shop`, `work`, `deliveryStart`, `deliveryDrop`; `GameScreen` hanya menghubungkan UI dan HUD.
- **Persistensi:** `Progress` schema 2 (coins, jobDays, deliveryStartDay, deliveryDays); schema 1 bermigrasi menjadi saldo awal 12 koin.
- **Memori & tas:** barang berada dalam items dan 3 entri Memory Book baru terbuka saat upah pertama dari tiap pekerjaan.

## Cara uji

`bash tools/test_logic.sh` menjalankan generator, layout, kompilasi Java headless dan 21.409+ pemeriksaan. Tidak memerlukan Android SDK; shim pada `tools/stubs/logic` **hanya untuk pemeriksaan logika**.

Uji APK sebenarnya di mesin Android SDK: `./gradlew :core:test :android:assembleDebug`. Uji di HP: beli, keluar toko, force-close/relaunch, saldo/item tetap, pembatasan upah harian, tidur, serta kurir yang belum selesai. Verifikasi izin jaringan tetap dilarang sesuai workflow CI.
