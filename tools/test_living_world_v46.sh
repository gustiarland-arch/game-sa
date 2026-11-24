#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
OUT="$(mktemp -d)"
trap 'rm -rf "$OUT"' EXIT
javac -encoding UTF-8 -d "$OUT" \
  core/src/main/java/com/arlandsofia/olu/logic/LivingWorldV46.java \
  tools/tests/LivingWorldV46Test.java
java -cp "$OUT" LivingWorldV46Test
