#!/usr/bin/env bash
# Reproducible headless test: DOES NOT verify full LibGDX/Android compile.
set -euo pipefail
cd "$(dirname "$0")/.."
# build_content regenerates a mural prop while producing JSON. Protect the
# current v3.2+ art-pass runtime PNG so tests do not silently change artwork.
S=$(mktemp -d "${PWD}/.testlogic-stubs.XXXXXXXX"); G=$(mktemp -d "${PWD}/.testlogic-classes.XXXXXXXX")
MURAL=android/assets/props/mural_new.png
cp "$MURAL" "$S/mural_original.png"
trap 'cp "$S/mural_original.png" "$MURAL"; rm -rf "$S" "$G"' EXIT
if [[ -f tools/build/anchors.json && -f tools/build/maps_base.json ]]; then
    # Full generation is possible only when tools/build_maps.py has produced anchors.
    python3 -I tools/build_content.py
    python3 -I tools/maps_v4_upgrade.py
    python3 -I tools/maps_v41_remaining.py --metadata-only
    python3 -I tools/world_redesign_v43.py --metadata-only
    python3 -I tools/world_redesign_v44.py --metadata-only
    python3 -I tools/apply_v463_cinematic.py
    python3 -I tools/apply_story_overhaul_v464.py
    python3 -I tools/apply_story_completion_v465.py
    python3 -I tools/apply_story_finale_v466.py
    python3 -I tools/apply_story_chapter1_v467.py
    python3 -I tools/apply_story_chapter2_v468.py
    python3 -I tools/apply_story_chapter3_v469.py
    python3 -I tools/apply_story_chapter4_v470.py
    python3 -I tools/apply_story_chapter4_rain_garden_v470.py
    python3 -I tools/apply_story_chapter5_v471.py
    python3 -I tools/apply_story_chapter6_v472.py
    python3 -I tools/apply_story_epilogue_v473.py
    python3 -I tools/apply_story_prologue_v474.py
    python3 -I tools/repair_c02_gallery_access_v480.py
    python3 -I tools/apply_story_cinematics_v480.py
else
    # Source ZIPs may omit generated maps_base/anchors. The complete shipped JSON
    # remains authoritative and MUST NOT be replaced with incomplete legacy data.
    echo "INFO: build anchors absent; checking preserved shipped story and map JSON."
fi
python3 -I tools/world_repaint_v42.py --verify-only  # v4.2 active art retained during headless test
python3 -I tools/clean_landmark_alpha_v42.py --verify  # 33 optimized sprite mattes retained
python3 -I tools/check_layout.py android/assets
javac --release 11 -d "$S" $(find tools/stubs/logic -name '*.java' | sort)
javac --release 11 -cp "$S" -encoding UTF-8 -d "$G" \
  $(find core/src/main/java/com/arlandsofia/olu/logic -name '*.java' ! -path '*/logic/romance/*' | sort) \
  core/src/main/java/com/arlandsofia/olu/game/Animal.java \
  core/src/test/java/com/arlandsofia/olu/LogicSelfTest.java
java -cp "$G:$S" com.arlandsofia.olu.LogicSelfTest android/assets
