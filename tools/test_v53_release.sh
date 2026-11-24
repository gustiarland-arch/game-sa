#!/usr/bin/env bash
# Real headless/static checks. Does NOT compile an Android APK.
set -euo pipefail
cd "$(dirname "$0")/.."
bash tools/test_motion_v53.sh
bash tools/test_character_logic_v37.sh
bash tools/test_v52_navigation.sh
bash tools/test_v30_ui_compile.sh
bash tools/test_visual_v462.sh
bash tools/test_logic.sh
printf 'V5.3 release headless QA complete. Android build/device tests pending.\n'
