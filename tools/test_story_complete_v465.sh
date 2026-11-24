#!/usr/bin/env bash
# Pure Java + data-asset checks; no Android SDK needed.
set -euo pipefail
cd "$(dirname "$0")/.."
OUT=$(mktemp -d)
trap 'rm -rf "$OUT"' EXIT
javac --release 11 -encoding UTF-8 -d "$OUT" $(find tools/stubs/logic -name '*.java' | sort)
javac --release 11 -encoding UTF-8 -cp "$OUT" -d "$OUT" \
  $(find core/src/main/java/com/arlandsofia/olu/logic -name '*.java' ! -path '*/logic/romance/*'|sort) \
  core/src/main/java/com/arlandsofia/olu/game/Animal.java \
  tools/tests/V464StoryBranchTest.java \
  tools/tests/V465StoryCompletionTest.java \
  tools/tests/V465StoryNavigationTest.java
java -cp "$OUT" V464StoryBranchTest android/assets
java -cp "$OUT" V465StoryCompletionTest android/assets
java -cp "$OUT" V465StoryNavigationTest android/assets
python3 -I tools/test_story_assets_v465.py
