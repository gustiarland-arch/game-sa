# Arland & Sofia — Story Overhaul / private draft tracker

**Working baseline:** Full source v4.6.6. **Working draft:** v4.7.3 narrative passes (C01–C06 + Epilogue integrated). **Distribution:** none yet — don't send ZIP or push to GitHub until every chapter is ready and verified.

| Story section | Status | Audit location / required next step |
|---|---|---|
| Prologue — The Book of Us | Not fully audited | Verify route opening choices, gifts, first portal, 3 shards, transition into Chapter 1 |
| Chapter 1 — The Beginning of Us | Implemented, headless QA passed | `docs/STORY_CHAPTER1_OVERHAUL_V467_AUDIT.md` |
| Chapter 2 — A Little Date | Implemented, headless QA passed | `docs/STORY_CHAPTER2_OVERHAUL_V468_AUDIT.md`: true three-way dating/schedule, additional native quests, photo lantern, C01 callbacks, 486 route walkthroughs |
| Chapter 3 — The Little Things | **Implemented, headless QA passed** | `docs/STORY_CHAPTER3_OVERHAUL_V469_AUDIT.md`: playable scrapbook/frame, neighbor, half-letter, 3-stage gallery, 864 tested branches and complete-route softlock fix |
| Chapter 4 — The Empty Seat | **Implemented, headless QA passed** | `docs/STORY_CHAPTER4_OVERHAUL_V470_AUDIT.md`: 324 tested routes, dedicated Rain Garden map, five lanterns, non-instant healing, legacy save escape, C02–C03 consequences |
| Chapter 5 — Across the Stars | **Implemented, headless QA passed** | `docs/STORY_CHAPTER5_OVERHAUL_V471_AUDIT.md`: 3 new maps, 15 quest stages, 5 fragments + 4-stage bridge puzzle, 108 branch walkthroughs, 27,674 full-story logic checks, save-resume support |
| Chapter 6 — Our Tomorrow | **Implemented, headless QA passed** | `docs/STORY_CHAPTER6_OVERHAUL_V472_AUDIT.md`: three playable futures, four memory panels, 576 choice combinations, one canon ending |
| Epilogue — To Be Continued | **Implemented, headless QA passed** | `docs/STORY_EPILOGUE_OVERHAUL_V473_AUDIT.md`: required memory walk, 29 scenes, 7 quest stages, new dual-letter map, both-route-gated playable bonus, 36 checked paths |

## Permanent rules for all upcoming chapter passes

- Apply each pass to the previous draft, not to the old v4.6.6 ZIP and not to GitHub.
- Never silently claim Android runtime compatibility solely from headless Java tests.
- If replacing story nodes, keep or migrate scene and quest identifiers used in existing saves; do not delete user saves automatically.
- Every chapter should have substantive dual-route writing, scene-to-quest consequences, reachable interactions, audiovisual cues, responsive choices, no dead-end paths, reproducible content rebuilds, and verified endings.
- Run previous chapter checks after each new change, not just the new tests.
- Package **one full ZIP** only after the full story (including Prologue and Epilogue) has passed its own audits and no missing content remains.
