#!/bin/sh
# SPDX-License-Identifier: BSD-2-Clause
set -eu
repo=$(pwd -P)
case ${CC:-cc} in *[!A-Za-z0-9_./+-]*|'') printf 'CC must name one compiler executable\n' >&2; exit 1 ;; esac
case $1 in
    extract) cp "$DISTFILE" "$WRKDIR/bytecount.c" ;;
    patch|configure) : ;;
    build) "$CC" -std=c11 -O2 -Wall -Wextra -Werror "$WRKDIR/bytecount.c" -o "$WRKDIR/bytecount" ;;
    test) python3 "$repo/tests/bytecount-output.py" "$WRKDIR/bytecount" ;;
    stage-install)
        mkdir -p "$DESTDIR$PREFIX/bin" "$DESTDIR$PREFIX/share/licenses/bytecount"
        cp "$WRKDIR/bytecount" "$DESTDIR$PREFIX/bin/bytecount"
        cp "$repo/recipes/bytecount/LICENSE" "$DESTDIR$PREFIX/share/licenses/bytecount/LICENSE"
        sh "$repo/mk/package-evidence.sh" host
        ;;
    *) exit 64 ;;
esac
