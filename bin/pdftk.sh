#!/usr/bin/env sh

# PDFTK_JAVA_OPTS (optional): options for the JVM, e.g. PDFTK_JAVA_OPTS="-Xmx1g"
# shellcheck disable=SC2086
java $PDFTK_JAVA_OPTS -jar lib/pdftk-all.jar "$@"
