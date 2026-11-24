# Draft — Chapter 3: The Little Things / story overhaul v4.6.9

**Checkpoint:** Chapter 3 content and headless narrative integration **complete for this pass**. No APK/device certification. **Private working draft**; do not distribute a ZIP or push to GitHub before all chapters, Prologue and Epilogue have their own reviews.

## Story agreement checklist

| Previously discussed beat | Actual implemented data and gameplay |
|---|---|
| The Little Things should deepen daily intimacy before the conflict | Original cooking, picnic, market errands, gifts and partners remain. Added unique playable private memory activities and new route-exclusive dialogue. |
| Arland tries to show love through actions; learns not everything requires a perfect fix | New **frame repair + scrapbook ordering mini-game** with personal response (keep repaired scar or reinforce frame), return a borrowed bowl to Pak Harun, and follow-up dialogues. |
| Sofia values presence and wants to express needs without feeling guilty | New **scrapbook assembly mini-game** with two reflection choices; return Bu Laras' book; three existing Memory Corner decoration choices now have bespoke consequence scenes. |
| Choices from Chapter 2 should still matter | 3 invitations (Arland) and 3 acceptance/postponement/refusal outcomes (Sofia) have private Chapter-3 callbacks; all three photobooth poses have exclusive cooking conversations. |
| A warm shared kitchen and park picnic | Original native cooking mini-game stays playable/retriable; original recipe/packing objectives and picnic remain. Added shared reflection that foreshadows the empty chair. |
| The incomplete letter hints at The Quiet and Chapter-4 emotional needs | New mandatory **physical half-letter quest** with two personal decisions per route, a collectible, an instrumental cue and a private memory. The letter intentionally does **not** reveal The Quiet prematurely. |
| Sofia's gallery showing and Arland's promise are the conflict setup | Original canon invitation and 3 response variants remain. New gallery invitation, its own 2 response choices, revised projector/sketch reflection choices, and third mandatory setup objective. Empty-seat foreshadowing cinematic closes the chapter. |
| Both routes must reach the same shared canon and Chapter 4 | All tested paths complete `C03` and transition to original `C04_A_WAKE` or `C04_S_WAKE`. Neither route receives the other's exclusive items. |
| Story remembered after save/load | The choice flags, route collectibles, chapter completion and start of C04 survive `Progress` serialization without schema changes. |

## Concrete source changes

- `tools/apply_story_chapter3_v469.py`: deterministic, idempotent JSON patch. Adds **25 new story scenes** (19 original C03 expansion + 6 callbacks to v468 decisions); **four new narrative quest steps** and extra interactions within preserved canon steps. Reuses the same previous 23 maps.
- `android/assets/data/story.json`: route-specific dialogue, garden/cooking callbacks, half-letter choices, gallery invitation and audiovisual closing.
- `android/assets/data/quests.json`: route-specific memory minigames, neighbor errands, real half-letter quest, 3-objective gallery, preserved original market, cooking and picnic.
- `android/assets/data/memory_book.json`: 23 new original Chapter-3 memory entries + five catalogued story collectibles, with branch-exclusive choices marked optional.
- `tools/gen_chapter3_assets_v469.py`: **4 editable-code pixel-art RGBA icons**, 192×192, for photo frame, scrapbook, half-letter, invitation.
- `tools/gen_chapter3_audio_v469.py`: **2 original OGG/Vorbis instrumental cues** and **1 original mono WAV**. All IDs registered in `SoundscapePlan.java`, not just stored in assets.
- `core/src/main/java/com/arlandsofia/olu/logic/SoundscapePlan.java`: additive music/SFX registration; original track names retained.
- `tools/tests/V469ChapterThreeTest.java`, `V469ChapterThreeNavigationTest.java`, `test_chapter3_assets_v469.py`, `test_chapter3_v469.sh`: mandatory quest playthroughs, saves, original content retention, accessibility, asset refs and cross-route outcomes.
- `tools/build_all.sh`, `tools/test_logic.sh`: route C03 patch applied **after C01/C02 patches**, preventing data regeneration from discarding the draft.
- Original `V464StoryBranchTest` updated to explicitly require third (invitation) task and check that the old two interactions alone **do not** end the chapter.

## Bugs found and fixed during Chapter-3 audit

1. Repeated clicking on strawberries/honey/mint and flowers/lights/frame could increase quest counters multiple times: per-item completion flags now match existing hide conditions.
2. **Real full-game softlock** in `C03_A_KITCHEN` (and potential Sofia equivalent): when the previous stage is completed while the player is already in the kitchen, an `enterArea`-only transition never triggers. Both now provide explicit reachable and repeat-safe **start-cooking interactables**. This was discovered by the long-route full-simulation, not by static tests.
3. Existing gallery test expected two tasks; updated and validated **three tasks** without bypassing the existing scene or deleting old tests.
4. Original C03 route-specific market dialogue was temporarily dropped by the new personal quest transition; restored and tested for both routes.
5. The initial half-letter interaction position was unreachable under the **strict 6px footprint collision test** even though a looser 14px simulator accepted it. Moved to the reachable existing recipe station. Full layout audit now has zero errors.
6. Story patch initially became non-idempotent after the kitchen fix; updated to support both pristine data and a previously patched project. Three JSON files now match their SHA-256 values after repeated application.

## Verified QA evidence

- **864** real headless Chapter-3 complete narrative combinations from C03 opening to C04 entry, **160,568 Java assertions** including route-only choices, inherited C02 flags, cooking + scrapbook minigames, collectible awards, cutscene execution, autosave-state serialization, cancellation/retry, and legacy saves.
- **67** collision-grid accessibility checks and **1,697** story/dialogue/asset/audio/reference checks for Chapter 3.
- Strict `tools/check_layout.py` across 23 maps and all story interactions: **zero errors**.
- Full `LogicSelfTest` auto-simulation from Prologue to Epilogue for both routes: **26,337 checks passed**; no new C03 softlock, economy, romance, save migration and original side stories exercised.
- Chapter-1 QA: **1,750** quest/canon assertions + 23 navigation + 643 static; Chapter-2 QA: **78,314** real runtime checks + 27 navigation + 2,439 static. Earlier conflict/story tests also passed: v464 505, v465 545 and 11 navigation, v466 403, cross-file refs 7,010.
- Cinematic/UI smoke 7 + layout 859; romance 51; tablet 390; controls 750; audio manager 956; chapter 2 and 3 assets validated. Legacy audio/story/cinema tests passed.
- Source integrity relative to v4.6.6 full ZIP: **1,980/1,980 old files present, 1,616/1,616 old audio/image files byte-identical**, `SaveStore.java`, `Progress.java`, `maps.json`, `props.json` unchanged.
- Running `python3 tools/apply_story_chapter3_v469.py` twice results in identical SHA-256 for `story.json`, `quests.json` and `memory_book.json`.

## Remaining gates that cannot honestly be called finished

- **No Android APK build**: local Android SDK/complete Gradle environment unavailable; no proof of device GPU rendering, touchscreen timings or audio mixing on hardware.
- The Story Bible's target of **about 6 hours per route is unverified**. Headless automated reading/time estimates are not a measured human playthrough; story breadth and pacing require real users.
- Chapter-4 pass must integrate the newly persisted promise/letter/gallery flags into post-conflict drama, without making earlier choices invalidate the canon missed-gallery incident. Chapter-5/6/Epilogue must ensure those exact choices have emotional payoff.
- Prologue still requires its own final audit. No export, ZIP packaging or GitHub changes are authorized at this stage.
