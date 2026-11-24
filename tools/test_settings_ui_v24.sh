#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT
javac --release 11 -encoding UTF-8 -d "$T" \
  $(find tools/stubs/ui -name '*.java' | sort) \
  tools/stubs/logic/com/badlogic/gdx/graphics/Texture.java \
  core/src/main/java/com/arlandsofia/olu/logic/{Json,Settings,AdaptiveLayoutV43,AdaptiveLayoutV44,CameraFramingV52}.java \
  core/src/main/java/com/arlandsofia/olu/ui/{UiButton,SettingsPanel}.java \
  tools/tests/SettingsPanelSmoke.java
java -cp "$T" SettingsPanelSmoke
