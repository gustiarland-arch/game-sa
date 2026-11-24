# Daftar Aset — v1.0

Semua aset dikemas di `android/assets/` (tanpa unduhan saat runtime). Dibuat ulang dengan `bash tools/build_all.sh`.

| Folder | Jumlah file | Ukuran | Sumber |
|---|---|---|---|
| `audio/` | 11 | 6.3 MB | gen_music2.py (8 lagu OGG orisinal) + SFX prototipe v0.4 |
| `animals/` | 10 | 44 KB | gen_animals.py (kucing ×4 warna, anjing, bebek, burung, ayam, kelinci, tupai; 4 frame) |
| `characters/` | 25 folder | 3.9 MB | lembar desain (extract_art) + gen_npcs (ganti palet + warna rambut; 23 NPC) |
| `data/` | 5 | 0.3 MB | build_maps.py + build_content.py |
| `fonts/` | 8 | 0.3 MB | gen_font.py (Inter OFL + DejaVu) |
| `items/` | 44 | 0.2 MB | gen_art.py + 3 ikon prototipe v0.4 |
| `maps/` | 15 | 6.0 MB | tools/build_maps.py (prosedural) |
| `props/` | 153 | 0.6 MB | tools/build_maps.py + tools/gen_art.py |
| `ui/` | 26 | 0.6 MB | gen_art.py + banner/kartu dari lembar desain |

## Belum dibuat / perlu diganti

- Sprite NPC orisinal (sekarang ganti palet & warna rambut dari sprite Arland/Sofia, jadi bentuk badan warga masih mirip).
- Animasi idle/jalan 8 frame/lari/duduk/interaksi untuk kedua karakter.
- Ekspresi Arland "Tersenyum" (sel di lembar desain berisi wajah Sofia).
- Variasi outfit (Casual/Date/Rumah/Spesial) sebagai sprite sheet.
- Musik final & SFX langkah, pintu, hujan.
- Pose couple/event untuk cutscene.

## Aset efek v2.0 (editable)

Enam aset RGBA dalam `android/assets/fx/`: `vignette.png` (256×256), `dust.png` (32×32), `splash.png` (28×28), `ripple.png` (48×20), `petal.png` (32×24), `heart.png` (28×28). Semuanya dibuat oleh `tools/gen_visual_fx.py` tanpa dependensi aset pihak ketiga. Anda bisa mengganti file PNG langsung untuk mengubah rupa game; jangan menjalankan ulang generator bila ingin mempertahankan hasil edit manual. Lihat `docs/VISUAL_OVERHAUL_V2.0.md`.
