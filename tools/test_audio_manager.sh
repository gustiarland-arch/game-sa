#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
DIR=$(mktemp -d)
trap 'rm -rf "$DIR"' EXIT
javac --release 11 -encoding UTF-8 -d "$DIR" \
  $(find tools/stubs/audio -name '*.java' | sort) \
  core/src/main/java/com/arlandsofia/olu/logic/{Json,Settings,WorldClock,SoundscapePlan}.java \
  core/src/main/java/com/arlandsofia/olu/AudioManager.java \
  tools/tests/AudioManagerSmokeTest.java
java -cp "$DIR" AudioManagerSmokeTest
