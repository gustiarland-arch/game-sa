# v5.3.0 – Motion Animation & Individual NPC Identities

## Ruang lingkup
Source berasal dari full-source v5.2.0 (World Collision & Camera Repair).
Update ini sengaja **tidak mengacak map, ukuran collision, objek quest, atau cerita**.

| Komponen | v5.2 | v5.3 |
|---|---|---|
| Atlas walking | 16 fase per arah | 24 fase per arah |
| Atlas idle | 8 fase per arah | 12 fase per arah |
| POV playable | 8 arah | 8 arah, atlas 24/12 |
| NPC berbeda visual | dominan palet ulang | 22 aksesori/seragam individual |
| NPC movement | kecepatan rutin relatif serupa | speed, bounce, cadence, gesture spesifik |
| Save schema | 8 | 8, tidak berubah |
| Map/quest/collision | semua v5.2 | dipertahankan |

## Prinsip teknis
- Seluruh sprite dihasilkan dalam resolusi asli 48×72/frame; nearest-neighbor tidak berubah.
- `MotionPersonalityV53.java` memisahkan profil gerakan dari data gameplay.
- `Actor.java` merender gerakan visual tanpa menggeser hitbox kaki.
- `GameScreen.java` memakai multiplier kecepatan NPC; pemain dan pasangan tidak mendapat
  perubahan kecepatan gerak fisik.
- `Assets.java` memuat `*_v53.png` jika tersedia, fallback ke atlas sebelumnya.
- Semua aset lama tetap ada agar dapat dikembalikan jika perlu.

## Pengujian
Buka log pengujian di `docs/` setelah proses QA selesai.
Tes sumber/headless tidak menggantikan build Android, inspeksi grafis, maupun playtest.

## Hasil pengujian sumber (23 November 2026)
- `bash tools/test_v53_release.sh`: exit status **0** (lulus).
- 629 pemeriksaan kepribadian gerak, 676 pemeriksaan struktur atlas.
- 231 pemeriksaan animasi/grafis dasar.
- 20 pemeriksaan navigasi/kamera v5.2.
- 40.445 pemeriksaan logika cerita/save/quest dan NPC sebelumnya.
- Typecheck Java untuk `Actor` menggunakan **minimal LibGDX stubs**, bukan build Android.
- Seluruh 29 peta, dialog, quest, audio, dan sprite lama terjaga.
- Belum ada pengujian pada APK atau perangkat fisik; Gradle distribution tidak tersedia offline.

## Aset hasil
- 76 PNG v5.3 di `android/assets/characters/<karakter>/*_v53.png`
- Sumber regenerasi: `tools/build_npc_motion_v53.py` (Pillow)
- Reproduksi dan verifikasi: `tools/test_motion_v53.sh`
- Gaya individu: `docs/MOTION_NPC_V53_ASSET_MANIFEST.json`

- `versionName=5.3.0`, `versionCode=130` (> v5.2), agar Android menerima update APK.
