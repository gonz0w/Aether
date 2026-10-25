#!/bin/sh
# SPDX-License-Identifier: BSD-2-Clause
# Validate inert SDK identity only; no package publication or native admission.
set -eu
LC_ALL=C
export LC_ALL
fail() { printf 'sdk-profile-error: %s\n' "$1" >&2; exit 1; }
is_hash() { case $1 in ''|*[!0-9a-f]*) return 1 ;; esac; test "${#1}" -eq 64; }
test "$#" -eq 4 || exit 64
target=$1; expected=$2; build=$3; native=$4
is_hash "$expected" || exit 64
repo=$(CDPATH='' cd "$(dirname "$0")/.." && pwd -P)
for file in "$target" "$build" "$native"; do
    if ! { test -f "$file" && test -r "$file" && ! test -L "$file"; }; then fail 'expected readable regular file'; fi
    links=$(find "$file" -type f -links +1 -print) || fail 'cannot inspect input'
    test -z "$links" || fail 'hard-linked input'
done
size=$(wc -c < "$target") || fail 'cannot size profile'
size=$(printf '%s' "$size" | tr -d '[:space:]')
case $size in ''|*[!0-9]*) fail 'invalid profile size' ;; esac
test "$size" -le 4096 || fail 'profile exceeds 4096 bytes'
scratch=$(mktemp -d "${TMPDIR:-/tmp}/pkg-sdk-profile.XXXXXX")
trap 'rm -rf "$scratch"' 0
trap 'exit 1' HUP INT TERM
awk '
BEGIN {
    split("format role build_os build_arch compiler_target build_receipt_sha256 native_profile_sha256 modes", keys, " ")
}
{
    if (NR > 8 || $0 !~ /^[ -~]*$/) {bad=1; next}
    prefix=keys[NR] "="
    if (index($0,prefix)!=1) {bad=1; next}
    value=substr($0,length(prefix)+1)
    if (NR==1 && value!="cross-sdk-target-v1") bad=1
    if (NR==2 && value!="build-inputs-only") bad=1
    if (NR>=3 && NR<=5 && (length(value)>128 || value!~/^[A-Za-z0-9][A-Za-z0-9._+-]*$/)) bad=1
    if ((NR==6 || NR==7) && (length(value)!=64 || value~/[^0-9a-f]/)) bad=1
    if (NR==8 && value!="recorded-0000-0777") bad=1
    rows[NR]=prefix value
}
END {
    if (bad || NR!=8) exit 1
    for (i=1;i<=8;i++) print rows[i]
}' "$target" > "$scratch/canonical" || fail 'invalid profile grammar'
cmp -s "$target" "$scratch/canonical" || fail 'noncanonical profile bytes'
hash() { sh "$repo/mk/verify-metadata.sh" hash-file "$1"; }
actual=$(hash "$target") || fail 'cannot hash profile'
test "$actual" = "$expected" || fail 'profile pin mismatch'
build_expected=$(sed -n '6s/^build_receipt_sha256=//p' "$scratch/canonical")
native_expected=$(sed -n '7s/^native_profile_sha256=//p' "$scratch/canonical")
actual=$(hash "$build") || fail 'cannot hash build receipt'
test "$actual" = "$build_expected" || fail 'build receipt mismatch'
actual=$(hash "$native") || fail 'cannot hash native receipt'
test "$actual" = "$native_expected" || fail 'native receipt mismatch'
