# Story Overhaul draft — Chapter 4 / The Empty Seat & Even When It Rains

**Status:** DRAFT CHECKPOINT, implementing and passing headless source QA; **not** an APK release or verified on physical Android hardware. **Version:** Chapter pass v4.7.0. **Distribution:** none — no ZIP and no GitHub publication until all chapters, Prologue and Epilogue are approved.

## Previously agreed narrative → playable work

| Agreement | Actual integration in game source |
|---|---|
| Galeri Komunitas and Sofia's first exhibition | `C04_V464_S_GALLERY` supported by new `V470_C04_S_PREP`: player physically arranges the artwork and practices one of three presentations; gallery stage then has branch dialogue. |
| Arland chooses how to handle projector and promise | `C04_V464_A_PROJECTOR` chooses 3 distinct, **playable** steps `V470_C04_A_WARN`, `V470_C04_A_SILENT`, `V470_C04_A_HELP` (+ `...HELP_OUT`); all lead to the canonical empty-chair event with different reflections; no instant rewriting of the past. |
| The Empty Seat emotional stakes | New cutscene cinematic cue, ambient music, Sofia's stage and Arland's late arrival; route-specific personal witness/sketch quests `V470_C04_A_AFTER` and `V470_C04_S_AFTER` and collectible ticket/sketch. |
| C02 and C03 decisions have consequences | Existing route invitation/promise flags and half-letter choices now trigger additional actual gallery and rain dialogue. |
| Five lanterns rather than two | `C04_LIGHTS` requires **all five distinct interactables**. Their flags prevent repeated counting. Shrine `C04_PUZZLE` gates the lantern mini-game; weather forced to rain while in Rain Garden independently of day. |
| Dedicated location rather than reuse C05 map | **24th real map** `maps/rain_garden.png`, 1920 × 1280, editable procedural pixel source `tools/gen_chapter4_map_v470.py`, collision-safe, altar + five glow landmarks, entry/return door via Taman Kota. Old `lantern_field` remains and is used for Chapter 5. |
| Old C04 saves must not be softlocked | Legacy save rescue door from **Lantern Field → Rain Garden only during C04**; portal destination never immediately triggers another door. All original quest step IDs and save schema retained. |
| Non-instant reconciliation | Separate two-action route quests `V470_C04_A_PROOF` and `V470_C04_S_PROOF` require Arland's new agenda + listening to Sofia's presentation, or Sofia's boundary note + respectful memory handling; only then `C04_V465_SECOND_TALK` and handoff to C05. |
| Cinematic & music | Three original OGG cues and a paper-note SFX, all registered in `SoundscapePlan.java` and invoked through actual quest actions. Five original 192px RGBA memory icons. |
| Consequences persist | Route and decision flags, souvenirs and `memory_book.json` items unlock; `Progress` save/load headless checks protect serialized state and chapter transition. |

## Headless QA / source audit

- `bash tools/test_chapter4_v470.sh`: **324 C04 route and choice paths** checked, **69,947 assertions** using the actual `QuestEngine` and `ActionRunner`; 104 navigation/portal/area-lock and collision checks; 756 media, story, audio, reference checks.
- `bash tools/test_logic.sh`: **26,943** checks. Full automated Prologue → Epilogue logic walkthrough for **both routes**, including romance, side quests, save/load, the new C04 area and existing C05 progression.
- Prior-chapter tests: C01 1,759+, C02 78,314, C03 160,568 assertions passed, plus legacy story and epilogue suites.
- Additional CI-type checks: cinematic, audio manager, sound references, Android touch simulation, tablet size profiles, and map/portal navigation passed.
- Running both Chapter 4 data patches again yields **byte-identical** `story.json`, `quests.json`, `maps.json`, `memory_book.json`. No duplicate scenes, steps, or doors.
- Comparison to v4.6.6 baseline full ZIP: **all 1,980 baseline files are present; all 1,616 original image/audio media remain byte-identical**. New files are additive.

## Build reproducibility

`tools/build_all.sh` regenerates C04 story, Rain Garden map metadata, standalone pixel map, memories and tracks in order. `tools/test_logic.sh` also re-applies map patch **when the optional build/anchors.json source is available**; without the anchors it verifies the shipped draft JSON instead of clobbering it with incomplete generated data.

## Remaining technical validation — not claimed complete

- A full Android APK build and actual device installation/runtime were **not available** in this environment. Must verify memory, GPU texture handling, on-screen safe-areas and touch interaction on physical Android phones/tablets.
- 6-hour playable length per route is a **design target**, not measured. Headless duration calculation is an estimate, not a timed human playtest.
- Entire story is **not final**: Prologue, Chapter 5, Chapter 6, Epilogue each await their dedicated detailed overhaul and their own checkpoint.

## Source locations

- `tools/apply_story_chapter4_v470.py`
- `tools/apply_story_chapter4_rain_garden_v470.py`
- `tools/gen_chapter4_map_v470.py`
- `tools/gen_chapter4_assets_v470.py`
- `tools/gen_chapter4_audio_v470.py`
- `tools/tests/V470ChapterFourTest.java`
- `tools/tests/V470ChapterFourNavigationTest.java`
- `tools/test_chapter4_assets_v470.py`
- `android/assets/{data/story.json,data/quests.json,data/maps.json,data/memory_book.json,maps/rain_garden.png}`
