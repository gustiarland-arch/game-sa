#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT
javac --release 11 -encoding UTF-8 -d "$T" \
  core/src/main/java/com/arlandsofia/olu/logic/TouchInputModel.java tools/tests/TouchInputModelTest.java
java -cp "$T" TouchInputModelTest
# Compile real graphics-facing control wrapper against narrow API stubs (NOT an Android build).
javac --release 11 -encoding UTF-8 -cp "$T" -d "$T" \
  $(find tools/stubs/ui -name '*.java' | sort) \
  tools/stubs/logic/com/badlogic/gdx/graphics/Texture.java \
  core/src/main/java/com/arlandsofia/olu/logic/{Json,Settings}.java \
  core/src/main/java/com/arlandsofia/olu/ui/UiButton.java \
  core/src/main/java/com/arlandsofia/olu/game/TouchControls.java
printf 'TOUCH CONTROL WRAPPER: Java type-check terhadap stub UI lulus\n'
bash tools/test_settings_ui_v24.sh
