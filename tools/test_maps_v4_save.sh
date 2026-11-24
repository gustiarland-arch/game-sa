#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
T=$(mktemp -d);trap 'rm -rf "$T"' EXIT
javac --release 11 -d "$T" $(find tools/stubs/logic -name '*.java' | sort)
javac --release 11 -cp "$T" -encoding UTF-8 -d "$T" $(find core/src/main/java/com/arlandsofia/olu/logic -name '*.java' ! -name 'RomanceSaveV45.java' | sort) tools/tests/MapLayoutV4Test.java
java -cp "$T" com.arlandsofia.olu.logic.MapLayoutV4Test
