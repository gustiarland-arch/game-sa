# v4.6.6 — Story Overhaul 3.2 · Release status

**Source ZIP complete; Android APK still unverified.**

- 457 scenes; 103 main quest steps; 23 maps; 139 Memory Book entries.
- 12 new scenes, three new source-editable memory icons and one original OGG cue.
- Six route-exclusive late-story decisions remembered by six distinct epilogue codas.
- Playable one-time gallery return postcredits for both protagonists; final main ending unchanged.
- Old-save epilogue fallback (no forced deletion or migration), same save format and route isolation.
- Source generator patch idempotent, audio cue registered in SoundscapePlan.
- Verification: `bash tools/test_story_finale_v466.sh` plus previous v4.6.5 logic/story QA. See docs/V466_STORY_FINALE_COMPLETE.md.
- Android Gradle APK build, device renderer, GPU performance, real-time story pacing and manual Android playthrough **not verified**.
