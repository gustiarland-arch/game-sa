# Draft — Chapter 2 / A Little Date: interactive story overhaul v4.6.8

Status: **content/logic implemented and independently checked in the local draft**. **Not** an Android release. The user explicitly requested no ZIP, no GitHub change, and a single-chapter review workflow. Prologue/Chapters 3–6/Epilogue still require their own thorough audits.

## Story goals and actual baseline gaps

1. The previous "Sofia says no / postpone" choice at the cafe immediately returned to the same-day date activity. The choice existed as a flag but the story ignored its meaning.
2. Prior Chapter-1 route decisions did not affect Chapter-2 dialogue, making the two-sided letter memory unimportant after the pier.
3. The flower-arrangement activity for Arland was dialogue-only, despite an existing playable native `bouquet` minigame.
4. Arland's photobooth repair was referred to in dialogue but not a distinct task to perform.
5. The mysterious lantern appeared in the original Story Bible but the native Chapter-2 photo scene did not show the photo anomaly with audiovisual framing.
6. The scene at the pier used the wrong inviter line and the gift-exchange actions included a `route` key that the actual action engine does not inspect; without explicit conditions, both sides could receive both items.
7. The old `Memory Book` regression assumed every optional branch-exclusive memory becomes unlocked after beating the game, an invalid test invariant.

## Applied story and gameplay

- The invitation is authored at **the start of the route** instead of being contradictory after preparatory tasks. Arland chooses *how* to ask, with no forced control of Sofia's autonomy. Sofia chooses **yes, tomorrow, or no today**.
- Sofia **accepts**: after route-specific outfit/photo printing and two optional daytime errands, the original cafe date and 3 distinct same-day outings are playable.
- Sofia **postpones**: an authored writing task in the cafe, actual next in-game day (07:00), a new meeting objective, and a reunion scene. The romance date never happens on the original day.
- Sofia **declines**: a quiet cafe reflection, a **playable solo sketch in Galeri Komunitas**, a separate invitation step from her room, then a player-triggered reunion the following day. Refusal is not treated as lack of affection, does not impose a penalty, and does not force an immediate date.
- The main canon photo and pier sunset are retained for all paths; the rescheduled routes reach them only after the player completes the appropriate independent narrative content.
- At the gazebo the player chooses to express affection through laughter, silence, or active listening; each creates a distinct permanent flag and entry.
- The prior C01 **LISTEN, RECORD, TRACE** result produces **different conversations at the gazebo**, even when the Chapter-2 route is played from a saved checkpoint.
- Arland must **actually play the native `bouquet` minigame** to assemble the flower; a cancelled minigame leaves the quest open for retry.
- Arland's photobooth is linked to a new playable repair stage (`V468_C02_PHOTO_REPAIR`) before the `photobooth` minigame. Sofia can use the original photobooth normally. The minigame remains cancellable/retriable.
- In the booth the player chooses three different pictures, then a **new photo-lantern cinematic** plays; the two viewpoints on the impossible lantern are explicitly preserved. A distinct photo item goes into the bag/Memory Book.
- The original shared date scenes, both routes, Chapter-3 destination steps, the gallery foreshadow, and the single canon ending are retained. The sunset now refers to choice-specific Sofia scene and selected photo, and uses explicit **route-dependent gift exchange**.
- Seven new route-based memory selections plus shared observation and 3 Sofia-specific schedule/independence memories are available per appropriate flags (17 new Memory Book entries total). Branch-exclusive entries use the `optional_story_branch` category rather than being misrepresented as always unlocked.

## Source changes

- `tools/apply_story_chapter2_v468.py`: deterministic, idempotent story/quest/book generator; keeps existing IDs and scene transitions.
- `core/src/main/java/com/arlandsofia/olu/logic/QuestEngine.java`: `restUntilTomorrow` action, increments game-day once per consumed story step, resets to 07:00, keeps save schema 8.
- `core/src/main/java/com/arlandsofia/olu/logic/SoundscapePlan.java`: registers original date track and photo-lantern SFX.
- `tools/gen_chapter2_assets_v468.py`: three original editable-code pixel-art icons (transparent RGBA, 192×192).
- `tools/gen_chapter2_audio_v468.py`: one original 27.6s OGG/Vorbis melody and one 1.1s mono PCM WAV SFX.
- Data: `android/assets/data/{story,quests,memory_book}.json` modified; the original 23 maps/collisions and legacy assets are preserved.
- Rebuild: `tools/build_all.sh` now runs v467 and v468 patches *after* v466 story generation, and their headless QA.
- Tests: `tools/tests/V468ChapterTwoTest.java`, `V468ChapterTwoNavigationTest.java`, `tools/test_chapter2_assets_v468.py`, `tools/test_chapter2_v468.sh`; updated obsolete assumptions in historical test harnesses. **No ZIP packaged.**

## Verification performed

- **486 complete Chapter-2 route combinations**: 2 protagonists × 3 phone options × 3 in-cafe/return choices × 3 gazebo choices × 3 photo choices × 3 prior C01 decisions. Each walkthrough was exercised through the actual Java `QuestEngine` and `ActionRunner`, including mandatory errands, date/canon, save/load and handoff to Chapter 3. The code tests tally 78,314 assertions.
- 27 navigation-grid assertions for new plus original interactions (each physically approachable from relevant map spawn); 2,439 source story/audio/icon/ref checks.
- 1,746 Chapter-1 headless regression assertions, 473 historic branching tests, 533 historic C05 completion tests, 403 historic finale tests; both routes still complete their prior content.
- Complete headless logic: 26,060 assertions passed, including economics, NPC routines, save migrations, romance, and world.
- JSON patch run twice: `story.json`, `quests.json`, and `memory_book.json` all **SHA-256 byte-identical after second application**, so no duplicate quest/scene/memory entries.
- Original cinematic/UI smoke, original audio, map navigation and story references passed. The v2.5 soundtrack test was made additive so a new WAV cannot invalidate the preserved original 32 SFX.

## Limitations / follow-ups

- **A full Android/Gradle APK build, GPU rendering on real phone/tablet, touchscreen QA, and measured 50-minute Chapter-2 runtime are not yet verified** by these headless tests. "Maximum chapter implementation" refers to implemented content and available static/runtime tests, not a claim that it is flawless in every device.
- Chapter-3/4/5/6 passes must verify all v468 flags actually pay off later, especially the first gallery promise, choosing to wait, the solo sketch, and the photo mystery. Do not mark those future callbacks completed yet.
- The Prologue requires a separate full audit before a user-facing release.
- Keep this as a **private draft**. Do not send a ZIP and do not push to GitHub until all sections have passed their own narrative and device integration gates.
