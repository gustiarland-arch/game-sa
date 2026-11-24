# PRIVATE DRAFT — Epilog: To Be Continued (v4.7.3)

**Status:** checkpoint EPILOGUE source/quest/assets completed and headless regression checked. **No ZIP, no push to GitHub.** Android APK/device performance, cutscene visuals on GPU, external font rendering, and real-life total playtime **not yet verified**.

## Narrative contract

- After the Lantern Festival, the players return to **Plaza -> Kafe Senja -> Galeri Komunitas -> Tepi Danau**, each a **required physically accessible quest stage**, before the quiet lakeside Epilogue coda.
- The Empty Seat remains part of the story: Arland takes responsibility without using his projector as an excuse; Sofia's presentation courage is celebrated without minimizing her disappointment. The old hurt is not wiped away.
- Arland and Sofia get distinct route scenes, with 2 selections each at the Plaza, Café, and Gallery. 2×2×2 variations are persisted in save flags and Memory Book. Earlier choice consequences from chapters 2–6 are recalled conditionally at the lake. Neither route is forced to choose a 'correct' answer.
- Original C06 canon ending, Epilogue Festival, route-specific letters, v4.6.5 quiet lakeside scene and six v4.7.2 future callbacks are retained. Their shared quiet closure was **physically relocated** from a festival dialogue queue to the playable lakeside bench. Epilogue completion occurs **exactly once**.
- Post-credits: optional meaningful visits to Plaza, Café, lakeside and the pre-existing Gallery revisit remain available and cannot be farmed indefinitely.
- The optional **The Other Side of the Page** is a **playable bonus mini-chapter** (not merely a Memory Book panel): enter original pixel-art **Ruang Dua Surat** from the Gallery; read both hidden letters, then choose how to preserve them. This room unlocks only when **GlobalProgress.bothCompleted("C06")** is true. Its gate is not satisfied by a local save flag.
- Previous v4.6.6 scene/step IDs and the save schema are preserved. Existing saves at EPI_FREE remain in free roam; saves at EPI_FEST_LEPAS enter the full new memory walk. Interrupted two-letter bonus may resume because both its interaction markers and return portal remain reachable.

## Production source, assets and runtime

| Part | Implementation |
|---|---|
| Story/quest logic | `tools/apply_story_epilogue_v473.py`; **29 scenes**, **7 playable steps**, 16 new Memory Book entries (5 core, 3 postgame, 8 choice-exclusive) |
| World | New pixel-art 960x640 `ruang_dua_surat.png` with reciprocal door, wall collision, safe arrival, NPC-free narrative interactions; **29 world areas total** |
| Editable items | 5 original pixel-art icons `items/v473_{page,letter,chair,photo,sunset}.png`, source `tools/gen_epilogue_assets_v473.py` |
| Sound | `cinema_homecoming_v473.ogg`, `cinema_dual_letters_v473.ogg`, `v473_letter_fold.wav`; source `tools/gen_epilogue_audio_v473.py` |
| Runtime | `QuestEngine.setGlobalProgress` (read-only conditional) + GameScreen injection, SoundscapePlan and WorldAtmosphereV462 registrations, `tools/patch_epilogue_runtime_v473.py` |
| Reproducibility | Integrated into `tools/build_all.sh` and full-regen branch of `tools/test_logic.sh`. 2 repeated patch runs produced identical hashes for 8 main JSON/Java files; pixel art generator deterministic |

## Tests actually executed

- **36 full playable Epilogue/bonus routes**, **3,376 assertions**, with two protagonists, all 8 combinations of 3 main choices, legacy/no-flag route, two-letter bonus decisions, save/load, one canon ending, and one-time postgame.
- **43 map-physics/nav/door/both-route gate assertions**, including physical BFS reachability and no recursive portal bounce.
- **186 asset and data-reference assertions**, including OGG Vorbis decode metadata and all sprite, scene, step, music and letter item references.
- **28,695** full Prologue-to-Epilogue Java headless checks across both routes, existing romance/world/side quests, save migration, inventory, anti-farming and cutscene-action scheduling.
- Earlier chapter regressions: C01 1,787; C02 78,314; C03 160,568; C04 69,947; C05 21,234; C06 101,466 assertions — all completed after this Epilogue patch.
- Other checks passed: 231 character/world, 859 cinematic/layout, 51 romance, 12 living world, 390 tablet profiles, 750 touch inputs, 126 settings UI, 155 map navigation, 267 soundscape audio, 93 cinematic audio, 396 historical story actions.
- **All 1,980 original v4.6.6 source-package files exist** in this draft. **All 1,616 original PNG/JPEG/OGG/WAV assets are byte-for-byte identical** (ZIP CRC+size comparison); old legacy assets were not overwritten.
- Source regeneration and tests now account for **29 maps** (legacy tests formerly hard-coded map counts and Epilogue immediate-completion order were updated, not disabled).

## Known restrictions / next checkpoint

- **Prologue still requires its own dedicated chapter review**, as requested by the user. End-to-end playthroughs passing do not replace this narrative-depth audit.
- No complete Android SDK/Gradle APK build or device gameplay session verified; no claim of perfect graphics, bug-free phone runtime, or a tested six-hour route duration.
- Draft is intentionally **not packaged**; no GitHub writes. Next step: audit and polish the Prologue, then cross-chapter narrative coherence and actual Android build/playtest when a suitable runtime becomes available.
