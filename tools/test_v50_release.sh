#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 tools/test_v50_content.py
bash tools/test_logic.sh
bash tools/test_v30_ui_compile.sh
bash tools/test_v463_cinematic_ui.sh
bash tools/test_tablet_v44.sh
bash tools/test_living_world_v46.sh
printf 'V5.0: HEADLESS QA COMPLETE. Not a substitute for Android build/device playtest.\n'
