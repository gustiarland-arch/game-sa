#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
DIR=$(mktemp -d)
trap 'rm -rf "$DIR"' EXIT
javac --release 11 -encoding UTF-8 -d "$DIR" \
  core/src/main/java/com/arlandsofia/olu/logic/{Json,Settings,WorldClock,SoundscapePlan}.java \
  tools/tests/SoundscapePlanTest.java
java -cp "$DIR" SoundscapePlanTest
