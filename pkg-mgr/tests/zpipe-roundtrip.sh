#!/bin/sh
set -eu
binary=$1
scratch=$(mktemp -d "${TMPDIR:-/tmp}/pkg-mgr-roundtrip.XXXXXX")
trap 'rm -rf "$scratch"' 0
trap 'exit 1' HUP INT TERM
"$binary" --version
: > "$scratch/empty"
printf 'a small real package dependency\n' > "$scratch/text"
dd if=/dev/zero of="$scratch/binary" bs=16384 count=5 2>/dev/null
printf '\000\001\177\200\377' >> "$scratch/binary"
for input in empty text binary; do
    "$binary" c < "$scratch/$input" > "$scratch/compressed"
    "$binary" d < "$scratch/compressed" > "$scratch/decoded"
    cmp "$scratch/$input" "$scratch/decoded"
done
if "$binary" d < "$scratch/text" > /dev/null 2>&1; then exit 1; fi
if "$binary" d < "$scratch/empty" > /dev/null 2>&1; then exit 1; fi
dd if="$scratch/compressed" of="$scratch/truncated" bs=1 count=4 2>/dev/null
if "$binary" d < "$scratch/truncated" > /dev/null 2>&1; then exit 1; fi
printf extra >> "$scratch/compressed"
if "$binary" d < "$scratch/compressed" > /dev/null 2>&1; then exit 1; fi
printf 'zpipe empty/text/binary round trips and malformed-stream checks passed\n'
