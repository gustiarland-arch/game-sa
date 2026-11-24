# Release Status — v4.6.2 (source-only)

**Fokus:** Character Animation Overhaul (Arland/Sofia) + World Graphics 4.0 pada 22 area.

- Script generator/pipeline: `tools/gen_visual_v462.py`, `tools/build_all.sh`.
- LibGDX source: `Actor.java`, `Assets.java`, `WorldFx.java`, `GameScreen.java`.
- Pure Java rules: `logic/AnimationMathV462.java` dan `logic/WorldAtmosphereV462.java`.
- Aset baru: 4 sprite sheets, 7 pixel FX.
- Asli dipertahankan: map PNG 22 area, collision, story, quests, original character sprites, audio, save.
- Pengujian: `bash tools/test_visual_v462.sh`, `bash tools/test_visual_fx.sh`, `bash tools/test_character_logic_v37.sh`, dan regresi map/save/audio.
- **Batas validasi:** source/headless checks, bukan build atau screenshot Android. Target 60 FPS belum dibuktikan di perangkat.
- **Status GitHub:** tidak diubah; update ini hanya menghasilkan ZIP source.
