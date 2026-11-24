#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
bash tools/test_logic.sh
bash tools/test_v52_navigation.sh
python3 tools/test_v52_world_access.py
python3 tools/test_v50_content.py
python3 tools/test_v51_environment.py
bash tools/test_settings_ui_v24.sh
bash tools/test_v30_ui_compile.sh
bash tools/test_v463_cinematic_ui.sh
bash tools/test_tablet_v44.sh
bash tools/test_living_world_v46.sh
printf 'v5.2 HEADLESS/STATIC QA PASSED. Android APK build and device playtest NOT verified.\n'
