#!/usr/bin/env bash
# v5.4 headless stair/elevation traversal regression for all 21 terraces.
set -euo pipefail
cd "$(dirname "$0")/.."
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT
javac --release 11 -d "$T" $(find tools/stubs/logic -name '*.java' | sort)
javac --release 11 -encoding UTF-8 -cp "$T" -d "$T" \
 $(find core/src/main/java/com/arlandsofia/olu/logic -name '*.java' ! -path '*/logic/romance/*' | sort) \
 core/src/test/java/com/arlandsofia/olu/V54StairTraversalTest.java
java -cp "$T" com.arlandsofia.olu.V54StairTraversalTest android/assets
