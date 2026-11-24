#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
javac --release 11 -encoding UTF-8 -d "$TMP" $(find tools/stubs/logic -name '*.java' | sort)
javac --release 11 -encoding UTF-8 -cp "$TMP" -d "$TMP" \
  $(find core/src/main/java/com/arlandsofia/olu/logic -name '*.java' ! -path '*/logic/romance/*' | sort) \
  core/src/main/java/com/arlandsofia/olu/game/Animal.java \
  tools/tests/V468ChapterTwoTest.java tools/tests/V468ChapterTwoNavigationTest.java tools/tests/V467ChapterOneTest.java tools/tests/V464StoryBranchTest.java
java -cp "$TMP" V468ChapterTwoTest android/assets
java -cp "$TMP" V468ChapterTwoNavigationTest android/assets
java -cp "$TMP" V467ChapterOneTest android/assets
java -cp "$TMP" V464StoryBranchTest android/assets
python3 tools/test_chapter2_assets_v468.py
