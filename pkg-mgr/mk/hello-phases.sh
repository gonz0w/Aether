#!/bin/sh
set -eu
case $1 in
    extract) cp "$DISTFILE" "$WRKDIR/hello.txt" ;;
    patch) : ;;
    configure) printf 'PREFIX=%s\n' "$PREFIX" > "$WRKDIR/config.mk" ;;
    build) mkdir -p "$WRKDIR/build"; cp "$WRKDIR/hello.txt" "$WRKDIR/build/hello.txt" ;;
    test) cmp "$WRKDIR/hello.txt" "$WRKDIR/build/hello.txt" ;;
    stage-install) mkdir -p "$DESTDIR$PREFIX/share/$PKGNAME"; cp "$WRKDIR/build/hello.txt" "$DESTDIR$PREFIX/share/$PKGNAME/hello.txt" ;;
    *) exit 64 ;;
esac
