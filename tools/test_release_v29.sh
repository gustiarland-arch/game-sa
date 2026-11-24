#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT
javac --release 11 -encoding UTF-8 -d "$T" $(find tools/stubs/logic -name '*.java' | sort)
javac --release 11 -encoding UTF-8 -cp "$T" -d "$T" \
  $(find core/src/main/java/com/arlandsofia/olu/logic -name '*.java' ! -name 'RomanceSaveV45.java' | sort) tools/tests/ReleaseResilienceTest.java
java -cp "$T" ReleaseResilienceTest
javac --release 11 -encoding UTF-8 -d "$T" tools/JavaSyntaxCheck.java
find core/src/main/java android/src/main/java -name '*.java' -print0 | xargs -0 java -cp "$T" JavaSyntaxCheck
