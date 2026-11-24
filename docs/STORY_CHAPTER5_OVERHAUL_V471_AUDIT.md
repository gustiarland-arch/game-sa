# Story Overhaul draft — Chapter 5 / Across the Stars

**Checkpoint:** v4.7.1 private draft, integrated after Chapters 1–4. **Distribution:** none. Do not export a ZIP or update GitHub until Prologue, Chapter 6 and Epilogue are audited and approved.

## Narrative contract and implemented gameplay

| Story requirement | Integrated into playable source |
|---|---|
| Conflicting first impressions and two routes | Existing Star Path / Lantern Field route entrances, Starfall Village, compass vs pages and route puzzles are kept. New Arland clockwork observations and Sofia etched memories are separate three-object stages with route-specific native mini-games. |
| The Empty Seat is not resolved by a gift | Arland sees projector, schedule, message timing; Sofia sees her own courage and the empty seat. Moonlight Lake remembers exact Chapter 4 projector or personal-boundary choices and asks for a new decision, persisted to flags. |
| Clockwork Station | Original 1920×1280 pixel-art map, walkable stations, 3 route-specific observations, retryable native minigame and 2 physical gear switches. Cancel/retry is not a softlock. |
| Moonlight Lake | Original area/map, portrait/dialogue, two-step listening/writing mechanic, personal reflection choices, two-perspective cinematic soundtrack cue. |
| Memory Bridge | Original area/map, five different constellation fragments, four stages revisiting previous chapters, shared native constellation minigame and a separate bridge-restoration sequence. |
| The Quiet reveal | The Keeper/Lumi shows intent vs impact from the same gallery day; players see the loss of context from earlier choices, make one of three interpretations, and preserve both accounts rather than defeating a villain. |
| Earned reconciliation without perfect memory | Two distinct repair interactions, a route-specific emotional farewell, restored bridge and a foreshadowed **unopened** Eternal Garden page. One canon ending is preserved. |
| Chapter 1–4 decisions truly remembered | Chapter 1 cafe choice, Chapter 2 consent (Sofia), Chapter 3 gallery invitation, Chapter 4 projector/boundary choices branch into Chapter 5 dialogue. New flags, collectibles and 20 chapter-specific Memory Book entries persist to Chapter 6. |
| Save compatibility / no skipped required story | Original C05 quest/scene IDs remain intact. A player resuming at the old `C05_Q_ECHO` ending sees a gentle pointer to the new Clockwork Station, not an irreversible skip. No automatic save deletion. |
| Sound / UI / art | 3 original instrumental OGG cues, 1 WAV chime, five editable pixel-art memory icons, 3 new original pixel-art map backdrops; music/FX registered in actual SoundscapePlan and WorldAtmosphere so these locations are not blank defaults. |

## Primary source and integrations

- `tools/apply_story_chapter5_v471.py`: deterministic, additive story/quest/map/Memory Book patch.
- `tools/gen_chapter5_maps_v471.py`: original 240×160 nearest-neighbor maps expanded to 1920×1280.
- `tools/gen_chapter5_assets_v471.py`: editable 192px RGBA item icons.
- `tools/gen_chapter5_audio_v471.py`: original 26-second cue beds and a chime, Vorbis OGG + WAV.
- `tools/patch_chapter5_audio_v471.py`: registered, idempotent soundtrack and ambience patch.
- `tools/patch_chapter5_world_v471.py`: idempotent atmosphere profile registration for all 27 maps.
- `tools/tests/V471ChapterFiveTest.java`: real `ActionRunner`, `QuestEngine`, `Progress`, `StoryDb`, `MapDb` integration checks.
- `tools/tests/V471ChapterFiveNavigationTest.java`: collision-grid BFS, doors, return points and original IDs.
- `tools/test_chapter5_assets_v471.py`: references, images, scene speaker/dialogue, item catalogue, OGG/WAV media, conditions.
- `tools/build_all.sh`: runs Chapter 5 after Chapter 4 on regenerated story data; no changes to remote repo.

## Latest source QA (23 November 2026)

- Chapter 5: **108 engine branch walkthroughs / 21,234 assertions** covering both routes, memories, choices, native minigames including cancellation/retry, five fragments, four-stage alignment, reveal, C06 handoff and legacy save at the prior endpoint.
- Collision and portal: **139 BFS/source checks**, including 3 new maps and 7 new portals; no tested warp destination blocked or immediate bounce.
- Static dialogue/art/sound: **1,036 checks**.
- Full Prologue → Epilogue: **27,674 headless Java assertions**, two routes including romance, economics, old-save loading, Chapter 5 and end-game transitions.
- Chapter 1–4 and old v4.6.4–6 finale suites: all passed after updates; no historic check silently discarded.
- World graphics: 219 visual-motion/theme checks, 390 tablet-layout checks, 750 Android-touch checks, 859 cinematic/UI interpolation checks, 267 original-audio checks and 93 cinematic audio integration checks passed.
- Original source integrity: **all 1,980 files from v4.6.6** remain; **all 1,616 v4.6.6 image/audio files SHA-256-identical**. New media is additive.
- Regeneration: running the chapter patch and two engine registration patches twice results in **identical hashes** of `story.json`, `quests.json`, `maps.json`, `memory_book.json`, `SoundscapePlan.java`, and `WorldAtmosphereV462.java`.

## Important verification limits / next steps

- **NOT verified**: compiled Android APK, GPU runtime, physical Android phone/tablet interaction, memory pressure, actual measured duration per route, multi-hour human playthrough, or complete `tools/build_all.sh` rebuild requiring missing optional map anchor files. A headless pass is not a proof of an Android game free of bugs.
- **Next**: Chapter 6 must remember the *specific* Chapter 5 choices and the two versions of the conflict through a believable emotional finale and the same single canon ending. Epilogue and Prologue still need dedicated story audits.
