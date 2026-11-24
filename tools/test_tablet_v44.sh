#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
javac --release 11 -d "$TMP" core/src/main/java/com/arlandsofia/olu/logic/AdaptiveLayoutV43.java core/src/main/java/com/arlandsofia/olu/logic/AdaptiveLayoutV44.java core/src/test/java/com/arlandsofia/olu/TabletLayoutV44Test.java
java -cp "$TMP" com.arlandsofia.olu.TabletLayoutV44Test
