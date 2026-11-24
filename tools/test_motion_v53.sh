#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
javac --release 11 -encoding UTF-8 -d "$TMP"  core/src/main/java/com/arlandsofia/olu/logic/MotionPersonalityV53.java  tools/tests/MotionV53Test.java
java -cp "$TMP" MotionV53Test
python3 tools/verify_motion_assets_v53.py
