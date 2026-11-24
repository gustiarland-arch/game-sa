#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT
javac --release 11 -encoding UTF-8 -d "$T" $(find tools/stubs/logic -name '*.java' | sort)
javac --release 11 -encoding UTF-8 -cp "$T" -d "$T" $(find core/src/main/java/com/arlandsofia/olu/logic -name '*.java' ! -name 'RomanceSaveV45.java' | sort)
javac --release 11 -encoding UTF-8 -cp "$T" -d "$T" \
  $(find tools/stubs/ui -name '*.java' | sort) \
  core/src/main/java/com/arlandsofia/olu/ui/UiButton.java \
  core/src/main/java/com/arlandsofia/olu/game/DialogueHistoryOverlay.java \
  tools/tests/DialogueHistoryOverlaySmoke.java
java -cp "$T" DialogueHistoryOverlaySmoke
