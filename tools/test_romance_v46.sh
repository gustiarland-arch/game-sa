#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
OUT=$(mktemp -d)
trap 'rm -rf "$OUT"' EXIT
javac --release 11 -encoding UTF-8 -d "$OUT" \
 core/src/main/java/com/arlandsofia/olu/logic/romance/RomanceEngineV45.java \
 core/src/main/java/com/arlandsofia/olu/logic/romance/RomanceSlotKeysV45.java \
 core/src/main/java/com/arlandsofia/olu/logic/romance/RomanceSavePolicyV45.java \
 tools/tests/RomanceV46IntegrationTest.java
java -cp "$OUT" RomanceV46IntegrationTest
