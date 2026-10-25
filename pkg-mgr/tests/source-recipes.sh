#!/bin/sh
# Rejection paths run without a compiler, network, or downloaded source archive.
set -eu
root=$(mktemp -d "${TMPDIR:-/tmp}/pkg-mgr-source-recipe.XXXXXX")
trap 'rm -rf "$root"' 0
trap 'exit 1' HUP INT TERM
make -s -f mk/pkg.mk ROOT="$root" init-root
printf 'not an upstream archive\n' > "$root/bad.tar.gz"
if make -s -f mk/pkg.mk ROOT="$root" PKGNAME=zlib SOURCE_ARCHIVE="$root/bad.tar.gz" package > "$root/bad.log" 2>&1; then exit 1; fi
test ! -e "$root/work/zlib/zlib-1.3.2"
# A negated command outside a condition does not trigger POSIX errexit.
# Distinguish an absent marker (1) from an unreadable log/tool failure (>1).
code=0
grep -q extract-start "$root/logs/zlib/phase.log" || code=$?
test "$code" -eq 1
if make -s -f mk/pkg.mk ROOT="$root" PKGNAME=zlib DISTNAME=../escape package > "$root/escape.log" 2>&1; then exit 1; fi
# No zlib record means no compiler invocation or fallback to the host library.
if make -s -f mk/pkg.mk ROOT="$root" PKGNAME=zpipe CC=compiler-must-not-run package > "$root/missing.log" 2>&1; then exit 1; fi
test ! -e "$root/work/zpipe/zpipe"
grep 'initialize state first' "$root/missing.log" > /dev/null
printf 'Pinned source and missing-dependency rejection paths passed\n'
