# Draft — Story Overhaul 3.3 / Chapter 1: The Beginning of Us

**Status:** Chapter 1 content/logic implemented and headless-tested in a local draft. **Not** an APK release. The user's requested workflow is **one chapter at a time; do not send a ZIP and do not push to GitHub** until all chapters and the epilogue are complete.

## Source baseline / integrity

- Source is based on actual `ArlandSofia_Our_Little_Universe_v4.6.6_STORY_FINALE_FULL_SOURCE.zip` (critical JSON/source hashes verified against the ZIP), not a blank recreated project.
- Preserved existing quest, scene and map IDs; two routes, 23 maps, old assets, story canon, and save schema remain intact.
- No existing content or assets deleted. No save files read, wiped or overwritten by the patch script.
- Added a conditional NPC scheduling rule in `QuestEngine` (inactive for all unmodified entries).

## Exact gaps discovered in pre-update Chapter 1

1. 27 Chapter-1 scenes existed but none had interactive dialogue decisions.
2. Two Story Bible beats — Arland helping the cafe barista with a mixed-up order and Sofia helping a customer find a missing letter — were absent as playable main-story objectives.
3. The chapter recorded two perspectives in dialogue but offered no player-driven way to hear, record or investigate them, nor a branch callback at the lake.
4. NPCs important to the cafe scene might not be visible at the actual time of the story due to free-roam schedules.
5. Memory Book did not distinguish the three possible ways the player interpreted the letter.

## Implemented narrative and gameplay

**Beginning:** Arland/Sofia each select one of two personal responses to their initial worries, stored under separate flags. These choices are acknowledged later in the pier scene.

**Plaza mural:** Original Arland flower-book-star and Sofia star-book-flower sequences are retained. The dialogue emphasizes that each has a truthful interpretation, not that one is mistaken.

**Cafe / personal quest:** Arland assists Kak Raka with the mixed-up order, or Sofia assists Rara with a missing letter. Each follows two actually playable interactions and awards a route-exclusive memory item. NPC placement is conditioned on the active quest and route, including different world-clock times.

**Three-symbol puzzle:** Remains playable using the original route-specific order. Letter discovery now triggers a short cinematic framing, an original OGG track, and a fuller story scene.

**Meaningful branching:** At the letter, choose to hear your partner, write down both perspectives, or investigate the fading ink. After the library/archive section, the choice opens one of three **different playable objectives** with a route-specific cutscene/dialogue, reward item, story flag and Memory Book entry.

**Library and archive:** The original shelf, three books, pedestal, route-specific archive clue and Bu Laras remain. Bu Laras reinforces the theme without prematurely explaining the mystery of The Quiet.

**Pier payoff:** Each of the three decisions generates different Arland/Sofia reflections. The opening choice is also remembered; the old romantic pier scene and shared chapter ending are preserved.

**Foreshadowing:** The Quiet manifests as fading ink and differences in perception without prematurely revealing its nature. Saved choice flags are available for later callbacks in the Chapter-2-to-6 audits. Do not represent those future callbacks as completed yet.

**Additive assets:** 3 original editable-code-generated pixel-art memory icons (192×192 RGBA), one original instrumental motif `cinema_two_sides_v467.ogg` (22.4 seconds, OGG/Vorbis), music registered in `SoundscapePlan`, plus source generators.

## Test gates already executed

- `tools/test_chapter1_v467.sh`: 1,741 runtime quest/choice/save/canon assertions, 23 navigation accessibility assertions, 643 static narrative/asset/audio assertions.
- Twelve full playable Chapter-1 combinations: 2 protagonists × 2 intro choices × 3 letter decisions, reaching the original Chapter 2 step (`C02_PHONE`) on every path.
- Legacy Chapter-1 save checkpoints without new flags continue via the original canonical path without softlock.
- Source data patch applied twice produces byte-identical JSON for `story.json`, `quests.json` and `memory_book.json`.
- Regression: 467 v4.6.4 story checks, 522 v4.6.5 story checks, 403 v4.6.6 finale checks, 6,342 cross-file story/asset checks, 12 Living World checks, 956 headless audio checks, 859 UI/cinematic layout checks, 136 map-navigation checks, and 38 save-migration checks.
- Verified against v4.6.6: no pre-existing project file removed; all pre-existing image/audio assets unchanged byte-for-byte; `maps.json`, `props.json`, `SaveStore.java`, `Progress.java`, `OluGame.java` unchanged.

## Remaining limitations (not silently considered done)

- This is a headless/static verification. Android/Gradle APK compilation and runtime scene rendering on an Android phone/tablet are **not** demonstrated here.
- No claim of a real-world 40-minute chapter playtime without a complete playthrough.
- Future callbacks of these flags across Chapters 2–6 must be audited and integrated in those chapter passes.
- A separate, full Prologue audit is still scheduled (the Prologue-to-Chapter-1 transition contract was preserved).

## Rebuild contract and QA commands

This draft patch MUST be applied after the v4.6.6 story generators if story JSON is regenerated:

```bash
python3 tools/apply_story_overhaul_v464.py
python3 tools/apply_story_completion_v465.py
python3 tools/apply_story_finale_v466.py
python3 tools/apply_story_chapter1_v467.py
python3 tools/gen_chapter1_assets_v467.py
python3 tools/gen_chapter1_audio_v467.py
bash tools/test_chapter1_v467.sh
```

Each generator has a self-contained entrypoint; do not use this command list as a substitute for a full Gradle build. Work remains in a **draft folder** with no ZIP distributed and no GitHub changes.
