#!/bin/sh
set -eu
repo=$(pwd -P)
source=$WRKDIR/zlib-1.3.2
# Upstream Makefile paths are unquoted. Refuse unsupported paths before extraction.
case "$ROOT$PREFIX" in *[!A-Za-z0-9_./+-]*) printf 'zlib currently requires paths without spaces or shell metacharacters\n' >&2; exit 1 ;; esac
case ${CC:-cc} in *[!A-Za-z0-9_./+-]*|'') printf 'CC must name one compiler executable\n' >&2; exit 1 ;; esac
case $1 in
    extract)
        # Only the already hash-verified release is supported, not arbitrary tarballs.
        tar -tzf "$DISTFILE" > "$WRKDIR/archive.paths"
        awk '$0 !~ /^zlib-1[.]3[.]2\// || $0 ~ /(^|\/)\.\.(\/|$)/ {exit 1}' "$WRKDIR/archive.paths"
        tar -tvzf "$DISTFILE" > "$WRKDIR/archive.types"
        awk 'substr($0,1,1)!="-" && substr($0,1,1)!="d" {exit 1}' "$WRKDIR/archive.types"
        tar -xzf "$DISTFILE" -C "$WRKDIR"
        ;;
    patch) : ;;
    configure) (cd "$source"; CC="$CC" CFLAGS=-O2 sh ./configure --static --prefix="$PREFIX") ;;
    build) make -C "$source" ;;
    test) make -C "$source" test ;;
    stage-install)
        make -C "$source" DESTDIR="$DESTDIR" install
        mkdir -p "$DESTDIR$PREFIX/share/licenses/zlib"
        cp "$source/LICENSE" "$DESTDIR$PREFIX/share/licenses/zlib/LICENSE"
        sh "$repo/mk/package-evidence.sh" host
        ;;
    *) exit 64 ;;
esac
