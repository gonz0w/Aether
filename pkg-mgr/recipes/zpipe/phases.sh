#!/bin/sh
set -eu
repo=$(pwd -P)
dependency=$ROOT/stage/zlib$PREFIX
case ${CC:-cc} in *[!A-Za-z0-9_./+-]*|'') printf 'CC must name one compiler executable\n' >&2; exit 1 ;; esac
case $1 in
    extract) cp "$DISTFILE" "$WRKDIR/zpipe.c" ;;
    patch) : ;;
    configure|build)
        # Require recorded, matching bytes before selecting headers or archive.
        sh mk/state.sh files "$ROOT" zlib > /dev/null
        sh mk/state.sh verify "$ROOT" > /dev/null
        test -f "$dependency/include/zlib.h"
        test -f "$dependency/lib/libz.a"
        if test "$1" = build; then
            "$CC" -O2 -Wall -Wextra -Werror -I"$dependency/include" "$WRKDIR/zpipe.c" "$dependency/lib/libz.a" -o "$WRKDIR/zpipe"
        fi
        ;;
    test) sh "$repo/tests/zpipe-roundtrip.sh" "$WRKDIR/zpipe" ;;
    stage-install)
        mkdir -p "$DESTDIR$PREFIX/bin"
        cp "$WRKDIR/zpipe" "$DESTDIR$PREFIX/bin/zpipe"
        sh "$repo/mk/package-evidence.sh" host
        ;;
    *) exit 64 ;;
esac
