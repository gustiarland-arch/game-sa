#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
javac --release 11 -encoding UTF-8 -d "$TMP" $(find tools/stubs/logic -name '*.java' | sort)
javac --release 11 -encoding UTF-8 -cp "$TMP" -d "$TMP" \
  $(find core/src/main/java/com/arlandsofia/olu/logic -name '*.java' ! -path '*/logic/romance/*' | sort) \
  core/src/main/java/com/arlandsofia/olu/game/Animal.java \
  tools/tests/V466StoryFinaleTest.java
java -cp "$TMP" V466StoryFinaleTest android/assets
python3 tools/test_story_assets_v465.py
python3 tools/test_story_assets_v466.py
