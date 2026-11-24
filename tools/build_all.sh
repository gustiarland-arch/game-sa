#!/usr/bin/env bash
# Bangun ulang SEMUA aset & data dari sumber (butuh Python 3 + Pillow + numpy + fontTools).
# Jalankan dari folder project: bash tools/build_all.sh
set -euo pipefail
A=android/assets
python3 tools/extract_art.py art_source/CHARACTER_DESIGN_REFERENCE.png $A   # sprite & potret dari lembar desain
python3 tools/gen_npcs.py $A                                                  # sprite NPC (ganti palet)
python3 tools/gen_poses.py $A                                                 # lembar pose (duduk, lambai, hadiah, gandengan, ...)
python3 tools/gen_animals.py $A                                               # hewan ambient (kucing, anjing, bebek, burung, ayam, kelinci, tupai)
python3 tools/gen_art.py $A android/res                                       # ikon, UI, sprite quest, ikon aplikasi
python3 tools/gen_visual_fx.py $A                                            # vignette, ripple, splash, dust, petals, heart FX
python3 tools/gen_visual_v21.py $A                                            # 8-frame walks, scenery layers, 6 UI skins, dialogue/cinematic assets
python3 tools/gen_font.py $A/fonts                                            # font bitmap
python3 tools/gen_music2.py $A/audio/music   # 8 track klasik dari v1.2
python3 tools/gen_soundscape_v24.py $A/audio   # 25 BGM baru + 14 ambience loop + 25 SFX; tidak menghapus track klasik
python3 tools/gen_cinema_audio_v25.py                                           # 7 musik cutscene orisinal v2.5
python3 tools/gen_cinema_fx_v25.py                                              # 4 SFX + 6 ekspresi potret v2.5
python3 tools/build_maps.py                                                   # 22 peta + collision + props
python3 tools/polish_world_v23.py $A                                            # detail pixel art 22 peta, tanpa mengubah collision
python3 tools/build_content.py                                                # naskah -> story/quests/maps/memory_book
python3 tools/visual_overhaul_v32.py                                         # 22 area, 256 prop, 25 karakter, UI skin, portret (dari baseline art source)
python3 tools/gen_cinematic_stills_v32.py                                    # 12 frame sinematik dari peta asli
python3 tools/world_redesign_stage1.py                                      # art direction v3.3: 3 landmark maps, 29 props, 12 editable layers
python3 tools/world_redesign_stage2.py                                      # art direction v3.4: 5 romantic/fantasy areas, 30 props, 20 editable layers
python3 tools/world_redesign_stage3.py                                      # art direction v3.5: 5 fantasy forest areas, 36 props, 25 editable layers
python3 tools/world_redesign_stage4.py                                      # v3.6: nine remaining city/interior areas, 57 props, 36 editable layers
python3 tools/character_polish_v37.py                                       # 25 karakter, atlas v3.7
python3 tools/maps_v4_upgrade.py                                            # 9 map baru, collision+portal+quest v4.0
python3 tools/maps_v41_remaining.py                                         # v4.1 legacy backdrop and scenic props
python3 tools/world_repaint_v42.py                                           # v4.2 three editable visual layers for 13 areas
python3 tools/clean_landmark_alpha_v42.py                                    # remove white background leakage from 33 landmark sprites
python3 tools/world_redesign_v43.py                                        # four new benchmark environment passes; rebind props
python3 tools/world_redesign_v44.py                                        # four romantic fantasy maps with collision-safe prop art
python3 tools/gen_visual_v462.py                                           # v4.6.2 8-facing hero atlas + 7 pixel-art atmosphere FX
python3 tools/apply_v463_cinematic.py                                      # restore v4.6.3 cinematic camera shots after regenerated quests
python3 tools/gen_story_assets_v464.py                                      # original pixel-art Galeri Komunitas and memory icons
python3 tools/gen_gallery_audio_v464.py                                      # original gallery soundtrack
python3 tools/apply_story_overhaul_v464.py                                   # branch-aware story, quests and gallery map
python3 tools/gen_story_assets_v465.py                                       # one new editable memory icon
python3 tools/gen_story_audio_v465.py                                        # soft reconciliation instrumental
python3 tools/apply_story_completion_v465.py                                 # playable reconciliation and story payoff
python3 tools/gen_story_assets_v466.py                                       # letter/sketch/gallery memory icons
python3 tools/gen_story_audio_v466.py                                        # original emotional epilogue soundtrack
python3 tools/apply_story_finale_v466.py                                     # optional postgame gallery, route letters and coda
python3 tools/apply_story_chapter1_v467.py                                     # Chapter 1 complete two-perspective branching and personal quests
python3 tools/gen_chapter1_assets_v467.py                                      # C01 pixel assets
python3 tools/gen_chapter1_audio_v467.py                                       # C01 original music
python3 tools/apply_story_chapter2_v468.py                                     # C02 real date consent, extra day, visible consequences
python3 tools/gen_chapter2_assets_v468.py                                      # C02 pixel art
python3 tools/gen_chapter2_audio_v468.py                                       # C02 original soundtrack and original photo SFX
python3 tools/apply_story_chapter3_v469.py                                     # C03 original personal chapter + half letter + gallery promise
python3 tools/gen_chapter3_assets_v469.py                                      # C03 original pixel art and memories
python3 tools/gen_chapter3_audio_v469.py                                       # C03 two original scene cues + sound effect
python3 tools/apply_story_chapter4_v470.py                                   # C04 full conflict, five lanterns, earned reconciliation
python3 tools/apply_story_chapter4_rain_garden_v470.py                        # C04 original Rain Garden map + C04 scene and quest rewiring
python3 tools/gen_chapter4_map_v470.py                                      # C04 dedicated 1920x1280 pixel-art map
python3 tools/gen_chapter4_assets_v470.py                                   # C04 five new original pixel art items
python3 tools/gen_chapter4_audio_v470.py                                    # C04 three original scores + paper sound
python3 tools/apply_story_chapter5_v471.py                                   # C05 route-specific clocks, moonlit reflections, five bridge fragments, The Quiet reveal
python3 tools/gen_chapter5_maps_v471.py                                      # C05 three original playable map backgrounds
python3 tools/gen_chapter5_assets_v471.py                                    # C05 five editable pixel icons
python3 tools/gen_chapter5_audio_v471.py                                     # C05 three original cues and scene chime
python3 tools/patch_chapter5_audio_v471.py                                   # C05 offline music + world ambience registration
python3 tools/patch_chapter5_world_v471.py                                   # C05 all three areas have runtime world atmosphere and FX
python3 tools/apply_story_chapter6_v472.py                                   # C06 personal future choice + 3 playable illusions + 4 alignment puzzles, single canon ending
python3 tools/gen_chapter6_assets_v472.py                                    # C06 original Hall of Tomorrow 1920x1280 + 5 editable icons
python3 tools/gen_chapter6_audio_v472.py                                     # C06 2 original instrumental tracks + memory glint
python3 tools/patch_chapter6_audio_v472.py                                   # register audio IDs and hall footstep/ambience
python3 tools/patch_chapter6_world_v472.py                                   # classify hall as native FX-enabled 28th world area
python3 tools/apply_story_epilogue_v473.py                                    # playable memory walk and two-route secret coda
python3 tools/gen_epilogue_assets_v473.py                                    # editable letter archive map and five icons
python3 tools/gen_epilogue_audio_v473.py                                     # two original Epilogue scores and paper sfx
python3 tools/patch_epilogue_runtime_v473.py                                 # native soundtrack, map climate, global route gate
python3 tools/apply_story_prologue_v474.py                                   # Prologue playable 2 routes and long-term payoffs
python3 tools/gen_prologue_assets_v474.py                                   # four original illustrated story icons
python3 tools/gen_prologue_audio_v474.py                                    # two original cinematic instrumental cues
python3 tools/generate_maps_v4_report.py                                   # original 9 area coordinate references
python3 tools/repair_c02_gallery_access_v480.py                              # restore Sofia C02 gallery route; lock otherwise kept
python3 tools/remaster_story_world_v480.py                                    # seven original story-area environment detail layers
python3 tools/gen_cinematic_scores_v480.py                                    # five original 44.1-kHz stereo soundtrack cues
python3 tools/apply_story_cinematics_v480.py                                  # six native cinematic sequences and music registry

# Version-aware release QA. Historical v4.0-v4.4 frozen-data hash tests are
# intentionally excluded because new story.json/quests.json/maps.json and
# two original OGG cues make their equality assumptions obsolete.
python3 tools/check_layout.py $A
python3 tools/test_story_world_v480.py
bash tools/test_logic.sh
bash tools/test_story_complete_v465.sh
bash tools/test_story_finale_v466.sh
bash tools/test_chapter1_v467.sh
bash tools/test_chapter2_v468.sh
bash tools/test_chapter3_v469.sh
bash tools/test_chapter4_v470.sh
bash tools/test_chapter5_v471.sh
bash tools/test_chapter6_v472.sh
bash tools/test_epilogue_v473.sh
bash tools/test_prologue_v474.sh
bash tools/test_visual_v462.sh
bash tools/test_v463_cinematic_ui.sh
bash tools/test_romance_v46.sh
bash tools/test_living_v46.sh
bash tools/test_tablet_v44.sh
bash tools/test_controls_v28.sh
python3 tools/test_maps_v4_navigation.py
python3 tools/test_audio_v24.py
python3 tools/test_cinema_v25.py
python3 tools/test_story_v26.py
echo "SOURCE QA PASS. Android APK still needs SDK + Gradle + physical device verification."
