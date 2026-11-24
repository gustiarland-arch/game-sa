#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 tools/test_v51_environment.py
bash tools/test_logic.sh
bash tools/test_v30_ui_compile.sh
bash tools/test_v463_cinematic_ui.sh
bash tools/test_tablet_v44.sh
bash tools/test_living_world_v46.sh
printf 'V5.1 HEADLESS QA COMPLETE; Android APK/device testing not verified.\n'
