#!/usr/bin/env bash
# UI smoke berbasis stub tombol saja: TIDAK menguji build/render LibGDX atau APK.
set -euo pipefail
cd "$(dirname "$0")/.."
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT
mkdir -p "$T/logic" "$T/ui"
javac --release 11 -d "$T/logic" $(find tools/stubs/logic -name '*.java' | sort)
javac --release 11 -encoding UTF-8 -cp "$T/logic" -d "$T/logic" \
  $(find core/src/main/java/com/arlandsofia/olu/logic -name '*.java' ! -path '*/logic/romance/*' | sort) \
  core/src/main/java/com/arlandsofia/olu/game/Animal.java
javac --release 11 -encoding UTF-8 -cp "$T/ui:$T/logic" -d "$T/ui" \
  $(find tools/stubs/ui -name '*.java' | sort) \
  core/src/main/java/com/arlandsofia/olu/ui/UiButton.java \
  core/src/main/java/com/arlandsofia/olu/game/ShopOverlay.java \
  core/src/main/java/com/arlandsofia/olu/game/RomanceOverlay.java \
  tools/tests/RomanceOverlaySmoke.java
java -cp "$T/ui:$T/logic" RomanceOverlaySmoke
