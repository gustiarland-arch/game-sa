#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
D="$(mktemp -d)"
trap 'rm -rf "$D"' EXIT
javac --release 11 -encoding UTF-8 -d "$D"     core/src/main/java/com/arlandsofia/olu/logic/LivingWorldV46.java     tools/tests/LivingWorldV46Test.java
java -cp "$D" LivingWorldV46Test
