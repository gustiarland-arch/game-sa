#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
OUT="$(mktemp -d)";trap 'rm -rf "$OUT"' EXIT
javac --release 11 -encoding UTF-8 -d "$OUT" \
  core/src/main/java/com/arlandsofia/olu/logic/{AnimationMathV462,WorldClock,WorldAtmosphereV462}.java \
  tools/tests/VisualV462Test.java
java -cp "$OUT" VisualV462Test
python3 tools/test_visual_v462.py
