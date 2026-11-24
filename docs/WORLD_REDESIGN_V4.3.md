# Art pass v4.3 — Plaza / Taman Kota / Kafe Senja / Riverside

Versi awal: v4.2. **Empat map runtime** mendapatkan pengerjaan visual terhadap lantai, pola batu, ornamen, iluminasi, dan riak air. **20 prop** memiliki varian tampilan khusus (`v43_*.png`) yang memakai anchor dan hitbox persis sama.

## File yang dapat diedit
- `android/assets/maps/{plaza,taman_kota,cafe,riverside}.png` (dipakai langsung oleh game).
- `art_source/world_v43/baseline_maps/` (empat PNG dari source v4.2).
- `art_source/world_v43/baseline_props/` (20 sprite original v4.2).
- `art_source/world_v43/editable_layers/` (16 layer PNG RGBA: terrain/detail/decor/lighting).
- `tools/world_redesign_v43.py` (generator deterministik, output PNG atomik).
- `android/assets/data/{maps,props}.json` (59 penempatan prop; data collision, portal, quest dan save tidak dimodifikasi).

Regenerasi visual: `python3 tools/world_redesign_v43.py`.
Regenerasi metadata setelah konten lama: `python3 tools/world_redesign_v43.py --metadata-only`.
Lakukan generator setelah `maps_v41_remaining.py` agar referensi sprite baru tidak tertimpa.

## Keterbatasan
Pembaruan ini merupakan **art pass prosedural terarah**, belum penggambaran ulang manual seluruh arsitektur dan layout seperti screenshot Sea of Stars. Layout dunia dan hitbox dipertahankan untuk keamanan misi; tidak ada klaim bahwa perspektif 2.5D dan seluruh visual sudah setara referensi. Semua area membutuhkan uji visual dalam APK sebelum rilis.
