#!/bin/sh
# SPDX-License-Identifier: BSD-2-Clause
# Opt-in host compiler workflow; only private roots and pinned local source.
set -eu
repo=$(CDPATH='' cd "$(dirname "$0")/.." && pwd -P)
cd "$repo"
root=$(mktemp -d "$repo/.pkg-mgr-live-bytecount.XXXXXX")
trap 'printf "retained_root=%s\n" "$root"' 0
make -s -f mk/pkg.mk ROOT="$root" PKGNAME=bytecount init-root
cp recipes/bytecount/bytecount.c "$root/tampered.c"
printf X | dd of="$root/tampered.c" bs=1 seek=0 conv=notrunc 2>/dev/null
if make -s -f mk/pkg.mk ROOT="$root" PKGNAME=bytecount LOCAL_SOURCE="$root/tampered.c" register > "$root/tamper.log" 2>&1; then exit 1; fi
grep 'source-hash-mismatch' "$root/tamper.log" >/dev/null
test ! -e "$root/work/bytecount/bytecount.c"
make -s -j4 -f mk/pkg.mk ROOT="$root" PKGNAME=bytecount register > "$root/build.log" 2>&1 || { tail -30 "$root/build.log"; exit 1; }
printf 'bytecount\n' > "$root/state/world"
sh mk/state.sh verify "$root"
python3 tests/bytecount-output.py "$root/stage/bytecount/usr/local/bin/bytecount"
cp recipes/bytecount/origin.json "$root/source-origin.json"
bin/pkg-mgr --root "$root" --format tsv export bytecount
pin=$(sh mk/verify-metadata.sh hash-file "$root/binaries/bytecount/artifact.kv")
triple=$(sed -n 's/^compiler_target=//p' "$root/stage/bytecount/usr/local/share/pkg-mgr/bytecount/host.kv")
fresh=$root/imported
mkdir -m 700 "$fresh"
make -s -f mk/pkg.mk ROOT="$fresh" init-root
sh mk/state.sh init "$fresh" >/dev/null
bin/pkg-mgr --root "$fresh" --format tsv import "$root/binaries/bytecount" "$pin" "$triple"
sh mk/state.sh verify "$fresh"
cmp "$root/state/packages/bytecount.tsv" "$fresh/state/packages/bytecount.tsv"
cmp recipes/bytecount/LICENSE "$fresh/stage/bytecount/usr/local/share/licenses/bytecount/LICENSE"
python3 tests/bytecount-output.py "$fresh/stage/bytecount/usr/local/bin/bytecount"
printf 'PASS: bytecount source tamper rejection, parallel build, registration, binary import and imported execution\n'
