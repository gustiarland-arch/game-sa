#!/usr/bin/env bash
# Source and headless regression tests for v4.6.6. This is NOT an Android APK test.
set -euo pipefail
cd "$(dirname "$0")/.."
bash tools/test_logic.sh
bash tools/test_story_complete_v465.sh
bash tools/test_story_finale_v466.sh
bash tools/test_soundscape_plan.sh
bash tools/test_v463_cinematic_ui.sh
bash tools/test_romance_v46.sh
bash tools/test_living_v46.sh
bash tools/test_tablet_v44.sh
bash tools/test_controls_v28.sh
bash tools/test_visual_v462.sh
bash tools/test_romance_ui.sh
python3 tools/test_maps_v4_navigation.py
python3 tools/test_audio_v24.py
python3 tools/test_cinema_v25.py
python3 tools/test_story_v26.py
printf '%s\n' 'ALL SOURCE/HEADLESS QA PASSED; ANDROID APK/DEVICE NOT VERIFIED.'
