#!/usr/bin/env bash
# v5.4 headless/static QA. Does NOT compile an Android APK or replace a device playtest.
set -euo pipefail
cd "$(dirname "$0")/.."
bash tools/test_v54_stairs.sh
bash tools/test_v54_weather.sh
python3 tools/scale_audit_v54.py
bash tools/test_v53_release.sh
python3 tools/test_v52_world_access.py
python3 tools/test_v51_environment.py
python3 tools/test_v50_content.py
printf 'V5.4 headless QA complete. Android build/device playtest reported separately.\n'
