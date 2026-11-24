# Arland & Sofia v4.6.5 — Story Overhaul 3.1

## Status

**Implemented in game data and Java-compatible runtime; headless-tested.** Source project is a complete editable Android Studio project, not a verified signed APK. Android GPU rendering, actual duration, playthrough pacing and device compatibility still require on-device tests. This document describes shipped functionality, not a future concept.

## Creative direction

**The Promise We Almost Forgot / The Empty Seat**. Warm and humorous first chapters, an emotionally realistic conflict about keeping a promise, an earned reconciliation and one positive canon ending. The Quiet is a metaphor for unheard perspectives, not a villain; neither protagonist is punished for asking for time or declining a date. This fictional story is not a biographical claim about real people.

- Arland: often communicates care through action and trying to fix things; must learn to ask what Sofia needs and actually show up.
- Sofia: wants to be heard and accompanied, not surprised with a bigger gift; learns she can express disappointment and set boundaries.
- Real consequences: flags, alternative playable activity and later dialogues, rather than superficial changes to displayed text.
- One canon ending: the last page remains open, and both choose to continue writing their story together.

## Complete chapter-by-chapter route integration

| Chapter | Player experience | Routed content / lasting consequence |
|---|---|---|
| Prologue — The Book of Us | Meet at the plaza, exchange handmade gifts, Memory Book and the first missing phrase | Small text on the paper flower and two viewpoints on memory foreshadow the later reveal |
| C01 — The Beginning of Us | Investigate the mural, café letter and two different orders of symbols | Recognize that the same day can mean different things to both characters |
| C02 — A Little Date | Actual accept/postpone/decline/ask choices followed by a distinct playable interaction | Four mutually meaningful decisions, `V464_WALK_*`, later recalled in C06 |
| C03 — The Little Things | The invitation to Sofia's gallery and the promise to attend, prepare seating/projector | New map, two actual interactive stations, new visual memories |
| C04 — The Empty Seat | Arland misses the exhibition while preparing a projector; Sofia presents before an empty reserved chair | Different route scenes, playable gallery, branch decisions, Rain Garden emotional conversation |
| C04 — After the Rain | The apology alone does not instantly repair trust; return to the gallery and undertake a route-specific reflective activity | Three personal response choices in each route, separate follow-up quest and a second dialogue with three options |
| C05 — Across the Stars | Understand two viewpoints and genuinely practice being present before proceeding to the starmap | Two playable listening/cooperation actions (`C05_V465_PROOF`), a kept promise flag and new Memory Book collectible |
| C06 — Our Tomorrow | Recall the invitation, the empty seat, follow-up decisions, and a bench made together | Conditional montage; if earlier data is from an older save, a fallback reflective scene plays; canon remains `C06-X01`/`C06-X03` |
| Epilogue — To Be Continued | Recognize past pain without erasing it, leave the last page open | Additional optional lakeside memory inserted before old chapter completion and free roam; no second ending |

## New map and editable assets

- `android/assets/maps/galeri_komunitas.png`: original 960×640 pixel-art gallery with Sofia's stage, projector and an empty seat.
- `android/assets/data/maps.json`: 22 old areas **plus** Galeri Komunitas (23 total). Door accessible from Kafe Senja; entrance, seats, presentation stage and projector were checked with navigation/collision tests.
- `android/assets/items/v464_*.png`: six gallery/memory collectibles.
- `android/assets/items/v465_bench_memory.png`: original newly generated memory icon; editable generator `tools/gen_story_assets_v465.py`.
- `android/assets/audio/music/cinema_gallery_empty.ogg`: original melancholic gallery score; generator `tools/gen_gallery_audio_v464.py`.
- `android/assets/audio/music/cinema_gallery_repair.ogg`: original 24-second reconciliation score; generator `tools/gen_story_audio_v465.py`.
- Cutscenes use existing `CutscenePlayer` commands: widescreen bars, partner framing, close-up, caption, ambient effects. Original art, dialog and collision data are not deleted from older areas.

## State and save compatibility

`Progress.SCHEMA` and the `SaveStore` format are unchanged. Route-specific choices and their lasting memory are stored in `Progress.flags`; player-selected quest steps remain in `Progress.step`; Memory Book unlocks reference flags rather than writing over old objects. Save slots and recovery files are not deleted or reset automatically.

Existing saves completed before C04 may not experience **every** new choice; for the complete new story begin a fresh slot. An older save in C06 without the new proof flag shows a valid alternative final reflection rather than becoming stuck. No guarantee of compatibility with arbitrary corrupted or third-party modified saves is made.

## Verified QA

| Test | Result |
|---|---|
| `bash tools/test_logic.sh` | 25,304 full headless logic assertions PASS |
| `bash tools/test_story_complete_v465.sh` | 457 branch + 493 completion + 11 navigation + 5,885 reference assertions PASS |
| `bash tools/test_v463_cinematic_ui.sh` | 859 motion/layout plus 7 cinematic smoke checks PASS |
| `bash tools/test_romance_v46.sh` | 51 romance assertions PASS |
| `bash tools/test_living_v46.sh` | 12 NPC assertions PASS |
| `bash tools/test_tablet_v44.sh` | 390 tablet layout assertions PASS |
| `bash tools/test_controls_v28.sh` | 750 touch assertions plus settings/UI smoke PASS |
| `bash tools/test_visual_v462.sh` | 196 animation/world assertions, plus 23 area visual-profile check PASS |
| `python3 tools/test_maps_v4_navigation.py` | 133 legacy map/portal/navigation checks PASS |
| `python3 tools/test_audio_v24.py` | 267 legacy audio checks PASS |
| `python3 tools/test_cinema_v25.py` | 93 cinematic/audio checks PASS |
| `python3 tools/test_story_v26.py` | 396 preserved old-story tests PASS |
| `docs/V465_BASELINE_MEDIA_AUDIT.json` | 793/793 original Android image/audio assets SHA-identical to v4.6.3 |
| `docs/V465_ENGINE_COMPATIBILITY_AUDIT.json` | Original save, route, quest, game-screen, and cutscene Java classes unchanged |

**Not verified:** Gradle Android debug/release APK compilation (SDK and cached Gradle distribution missing in this environment), real renderer/photobooth/cinematic performance, 60 FPS, physical Android tablet/phone playthrough, actual six-hour route time. These require build + on-device testing. A passing pure-Java test must not be described as proof of Android release readiness.

## Rebuild and edit instructions

1. Open root `ArlandSofia/` in Android Studio with JDK 17, Android SDK API 36 and Gradle 8.11.1 as configured.
2. To edit the story directly use `android/assets/data/story.json`, `quests.json`, `memory_book.json` and `maps.json` (UTF-8). Edit text, flags and scene IDs carefully; `tools/test_story_assets_v465.py` validates links.
3. To rebuild from original generators: run `bash tools/build_all.sh`. It regenerates the old content, then automatically reapplies `tools/apply_story_overhaul_v464.py` and `tools/apply_story_completion_v465.py`, plus the gallery art/music generators. It may repaint/edit generated assets; keep version control/backups when doing this.
4. After editing narrative sources run `bash tools/test_story_complete_v465.sh` and `bash tools/test_logic.sh`.
5. Build APK in Android Studio, then test each route with new/old saves on phones/tablets, manual navigation through the gallery, all three choice branches, skip/cancel in puzzles, and all endings.

**Historical audits:** Many `tools/test_v4*` scripts assert byte-for-byte equality of `data/*.json` with pre-overhaul snapshots or exactly 22 maps/40 music tracks. Those are historical baseline probes, not current release gates. New tests check that all original files and routes remain available while new story content is added.
