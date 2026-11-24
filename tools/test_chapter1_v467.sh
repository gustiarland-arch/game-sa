#!/usr/bin/env bash
# Chapter 1 regression gate — JDK 11 only, no Android SDK required.
set -euo pipefail
cd "$(dirname "$0")/.."
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
javac --release 11 -encoding UTF-8 -d "$TMP" $(find tools/stubs/logic -name '*.java' | sort)
javac --release 11 -encoding UTF-8 -cp "$TMP" -d "$TMP" \
  $(find core/src/main/java/com/arlandsofia/olu/logic -name '*.java' ! -path '*/logic/romance/*' | sort) \
  core/src/main/java/com/arlandsofia/olu/game/Animal.java \
  tools/tests/V467ChapterOneTest.java tools/tests/V467ChapterOneNavigationTest.java
java -cp "$TMP" V467ChapterOneTest android/assets
java -cp "$TMP" V467ChapterOneNavigationTest android/assets
python3 tools/test_chapter1_assets_v467.py
