# Arland & Sofia: Our Little Universe v5.3.0 — Character Motion & NPC Identity

**Native Android / LibGDX, full source** based on v5.2.0. Semua route Arland dan Sofia,
satu canon ending, quest, map, cutscene, audio, navigasi, dan save schema 8 dipertahankan.

## Update v5.3
- **Animasi 25 karakter**: sprite gerak 24 fase/direction, idle 12 fase/direction
  (mempertahankan sprite pixel-art lama dan siap diganti/edit).
- **Arland & Sofia**: 8-arah dengan 24 fase gerak dan 12 fase idle.
  Perpindahan gerak/diam memakai easing; efek langkah/sway/napas dan belokan dibedakan.
- **22 NPC non-playable** kini memiliki aksesori/seragam profesi berbeda dalam
  lembar `walk_v53.png`, `idle_v53.png`, dan `poses_v53.png`.
  Sprite asli (`walk_v37`, `idle_v37`, `poses`) tidak ditimpa.
- **NPC memiliki gaya gerak berbeda**: usia/peran memengaruhi cadence, gesture,
  langkah dan kecepatan berjalan. Tidak mengubah ukuran collision atau quest.
- Animasi seluruhnya asset lokal; **tetap offline** tanpa internet atau akun.

## Cara pakai
1. Extract ZIP. Buka folder `ArlandSofia` di Android Studio (folder dengan `settings.gradle`).
2. Sync Gradle, jalankan Build APK. Gunakan app ID/signing key yang sesuai agar save lama aman.
3. Jalankan pengujian di Linux/macOS: `bash tools/test_motion_v53.sh`;
   `bash tools/test_character_logic_v37.sh`; `bash tools/test_logic.sh`;
   `bash tools/test_v52_navigation.sh`.
4. Edit identitas NPC di `tools/build_npc_motion_v53.py`, lalu jalankan skripnya
   untuk meregenerasi sprite v5.3 dari atlas dasar v5.2.

**Keterbatasan QA**: Source/atlas diperiksa tanpa runtime LibGDX dan tanpa Android APK build.
Visual harus diuji di perangkat; cocokkan animasi saat berbelok, sprint, tangga,
NPC berdialog, dan pergantian map setelah Gradle Sync.

## Dokumen rilis
Baca `V53_RELEASE_NOTES.md`, `docs/MOTION_NPC_V53_ASSET_MANIFEST.json`, dan
`CHANGELOG.md`. Arsip v5.3 juga menyertakan seluruh dokumen dan aset versi sebelumnya.
