#!/bin/sh
# Opt-in: provide the pinned archive locally. No downloads occur in this test.
set -eu
repo=$(CDPATH='' cd "$(dirname "$0")/.." && pwd -P)
cd "$repo"
test "$#" -eq 1 || { printf 'usage: sh tests/zlib-integration.sh /absolute/zlib-1.3.2.tar.gz\n' >&2; exit 64; }
archive=$1
case ${KEEP_ROOT:-no} in yes|no) ;; *) exit 64 ;; esac
root=$(mktemp -d "$repo/.pkg-mgr-live-zlib-replacement.XXXXXX")
cleanup() {
    if test "${KEEP_ROOT:-no}" = yes; then printf 'retained_root=%s\n' "$root"
    else rm -rf "$root"
    fi
}
trap cleanup 0
trap 'exit 1' HUP INT TERM
make -s -f mk/pkg.mk ROOT="$root" PKGNAME=zlib init-root
# Even a same-size source mutation must stop before extraction.
cp "$archive" "$root/tampered.tar.gz"
printf X | dd of="$root/tampered.tar.gz" bs=1 seek=0 conv=notrunc 2>/dev/null
if make -s -f mk/pkg.mk ROOT="$root" PKGNAME=zlib SOURCE_ARCHIVE="$root/tampered.tar.gz" package > "$root/tamper.log" 2>&1; then exit 1; fi
grep 'source-hash-mismatch' "$root/tamper.log" > /dev/null
test ! -e "$root/work/zlib/zlib-1.3.2"
make -s -j4 -f mk/pkg.mk ROOT="$root" PKGNAME=zlib SOURCE_ARCHIVE="$archive" register > "$root/zlib.log" 2>&1 || { tail -n 30 "$root/zlib.log"; exit 1; }
# Corrupt dependency evidence must prevent compiling against any host fallback.
cp "$root/stage/zlib/usr/local/lib/libz.a" "$root/good-libz.a"
printf X | dd of="$root/stage/zlib/usr/local/lib/libz.a" bs=1 seek=0 conv=notrunc 2>/dev/null
if make -s -f mk/pkg.mk ROOT="$root" PKGNAME=zpipe package > "$root/dependency-failure.log" 2>&1; then exit 1; fi
test ! -e "$root/work/zpipe/zpipe"
cp "$root/good-libz.a" "$root/stage/zlib/usr/local/lib/libz.a"
make -s -j4 -f mk/pkg.mk ROOT="$root" PKGNAME=zpipe PKGVERSION=0.1 LOCAL_SOURCE=fixtures/sources/zpipe-0.1/zpipe.c SOURCE_METADATA=fixtures/sources/zpipe-0.1/source.kv register > "$root/zpipe.log" 2>&1 || { tail -n 30 "$root/zpipe.log"; exit 1; }
printf 'zpipe\n' > "$root/state/world"
sh mk/state.sh verify "$root"
sh mk/state.sh list "$root"
test "$(sh mk/state.sh deps "$root" zpipe)" = zlib
test "$(sh mk/state.sh rdeps "$root" zlib)" = zpipe
test "$(sh mk/state.sh orphans "$root" | wc -l | tr -d ' ')" = 1
sh tests/zpipe-roundtrip.sh "$root/stage/zpipe/usr/local/bin/zpipe"
"$root/stage/zpipe/usr/local/bin/zpipe" c < "$archive" > "$root/archive.z"
"$root/stage/zpipe/usr/local/bin/zpipe" d < "$root/archive.z" > "$root/archive.decoded"
cmp "$archive" "$root/archive.decoded"
test -f "$root/stage/zlib/usr/local/lib/libz.a"
test -z "$(find "$root/stage/zlib" -type l -print)"
# Exact archive linkage is a recipe requirement, not a -lz system fallback.
if command -v otool > /dev/null 2>&1; then
    otool -L "$root/stage/zpipe/usr/local/bin/zpipe" > "$root/linked-libraries"
    if grep 'libz[.]' "$root/linked-libraries"; then exit 1; fi
fi
printf 'Static zlib upstream tests, staged registration, and dependent utility passed\n'

# Import contains no build step and retains the exact registered record bytes.
fresh=$root/imported
mkdir -m 700 "$fresh"
make -s -f mk/pkg.mk ROOT="$fresh" init-root
sh mk/state.sh init "$fresh" >/dev/null
triple=$(sed -n 's/^compiler_target=//p' "$root/stage/zpipe/usr/local/share/pkg-mgr/zpipe/host.kv")
for name in zlib zpipe; do
    bin/pkg-mgr --root "$root" --format tsv export "$name"
    pin=$(sh mk/verify-metadata.sh hash-file "$root/binaries/$name/artifact.kv")
    bin/pkg-mgr --root "$fresh" --format tsv import "$root/binaries/$name" "$pin" "$triple"
    cmp "$root/state/packages/$name.tsv" "$fresh/state/packages/$name.tsv"
done
bin/pkg-mgr --root "$fresh" --plain verify
sh tests/zpipe-roundtrip.sh "$fresh/stage/zpipe/usr/local/bin/zpipe"
printf 'Real binary export/import and imported executable passed\n'

# Build the next utility against the exact same registered zlib package.
next_root=$root/next-build
mkdir -m 700 "$next_root"
make -s -f mk/pkg.mk ROOT="$next_root" init-root
sh mk/state.sh init "$next_root" >/dev/null
pin=$(sh mk/verify-metadata.sh hash-file "$root/binaries/zlib/artifact.kv")
bin/pkg-mgr --root "$next_root" --format tsv import "$root/binaries/zlib" "$pin" "$triple" >/dev/null
make -s -j4 -f mk/pkg.mk ROOT="$next_root" PKGNAME=zpipe register > "$root/zpipe-next.log" 2>&1 || { tail -n 30 "$root/zpipe-next.log"; exit 1; }
bin/pkg-mgr --root "$next_root" --format tsv export zpipe
bundle=$next_root/binaries/zpipe
pin=$(sh mk/verify-metadata.sh hash-file "$bundle/artifact.kv")
old_pin=$(sh mk/verify-metadata.sh hash-file "$fresh/state/packages/zpipe.tsv")
old=$fresh/stage/zpipe/usr/local/bin/zpipe
"$old" --version | grep '^zpipe 0.1;' >/dev/null
code=0
"$old" --help > "$root/old-help.out" 2> "$root/old-help.err" || code=$?
test "$code" -eq 64
printf 'zpipe\n' > "$fresh/state/world"
cp "$fresh/state/world" "$root/before-world"
cp "$fresh/state/packages/zlib.tsv" "$root/before-zlib"
bin/pkg-mgr --root "$fresh" --format tsv preflight "$bundle" "$pin" "$triple" > "$root/replacement-preflight.tsv"
bin/pkg-mgr --root "$fresh" --format tsv prepare "$bundle" "$pin" "$triple" "$old_pin" > "$root/replacement-prepared.tsv"
intent_pin=$(awk -F '\t' '$1=="prepared"{print $3}' "$root/replacement-prepared.tsv")
if bin/pkg-mgr --root "$fresh" list > "$root/pending-list" 2> "$root/pending-error"; then exit 1; fi
bin/pkg-mgr --root "$fresh" --format tsv finish "$intent_pin"
bin/pkg-mgr --root "$fresh" --format tsv finish "$intent_pin"
retained=$fresh/replacements/$intent_pin/previous/usr/local/bin/zpipe
active=$fresh/stage/zpipe/usr/local/bin/zpipe
"$active" --version | grep '^zpipe 0.2;' >/dev/null
"$active" --help > "$root/new-help.out"
grep 'compress a zlib stream' "$root/new-help.out" >/dev/null
"$retained" --version | grep '^zpipe 0.1;' >/dev/null
code=0
"$retained" --help >/dev/null 2>&1 || code=$?
test "$code" -eq 64
sh tests/zpipe-roundtrip.sh "$active"
sh tests/zpipe-roundtrip.sh "$retained"
# Cross-version stream compatibility, not just same-version round trips.
printf 'real retained replacement\n' > "$root/cross-input"
"$retained" c < "$root/cross-input" > "$root/old-stream"
"$active" d < "$root/old-stream" > "$root/new-decoded"
cmp "$root/cross-input" "$root/new-decoded"
"$active" c < "$root/cross-input" > "$root/new-stream"
"$retained" d < "$root/new-stream" > "$root/old-decoded"
cmp "$root/cross-input" "$root/old-decoded"
cmp "$root/before-world" "$fresh/state/world"
cmp "$root/before-zlib" "$fresh/state/packages/zlib.tsv"
cmp "$bundle/package.tsv" "$fresh/state/packages/zpipe.tsv"
bin/pkg-mgr --root "$fresh" --plain verify
printf 'Real zpipe 0.1 -> 0.2 replacement, retained executable and cross-version streams passed\n'
