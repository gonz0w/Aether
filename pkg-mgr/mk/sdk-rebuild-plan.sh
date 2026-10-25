#!/bin/sh
# SPDX-License-Identifier: BSD-2-Clause
# Read-only, caller-quiesced private-root SDK requalification report.
set -eu
LC_ALL=C
export LC_ALL
fail() { printf 'sdk-plan-error: %s\n' "$1" >&2; exit 1; }
is_hash() { case $1 in ''|*[!0-9a-f]*) return 1 ;; esac; test "${#1}" -eq 64; }
test "$#" -eq 5 || exit 64
installed=$1; candidate=$2; installed_pin=$3; candidate_pin=$4; profile_pin=$5
for pin in "$installed_pin" "$candidate_pin" "$profile_pin"; do is_hash "$pin" || exit 64; done
repo=$(CDPATH='' cd "$(dirname "$0")/.." && pwd -P)
# Normalize tool failures to 1, including a provider that emits plausible bytes.
status=0
trap 'exit 1' HUP INT TERM PIPE
trap 'status=$?; if test "$status" -ne 0; then exit 1; fi' 0
for root in "$installed" "$candidate"; do
    ROOT=$root sh "$repo/mk/check-root.sh" state || fail 'invalid private root'
done
installed=$(CDPATH='' cd "$installed" && pwd -P)
candidate=$(CDPATH='' cd "$candidate" && pwd -P)
case "$candidate/" in "$installed/"*) fail 'roots must be separate' ;; esac
case "$installed/" in "$candidate/"*) fail 'roots must be separate' ;; esac
scratch_parent=$(CDPATH='' cd "${TMPDIR:-/tmp}" && pwd -P) || fail 'invalid scratch parent'
for root in "$installed" "$candidate"; do
    case "$scratch_parent/" in "$root/"*) fail 'scratch must be outside roots' ;; esac
done
scratch=$(mktemp -d "$scratch_parent/pkg-sdk-plan.XXXXXX") || fail 'cannot create scratch'
trap 'status=$?; rm -rf "$scratch" || exit 1; if test "$status" -ne 0; then exit 1; fi' 0
chmod 700 "$scratch"
TMPDIR=$scratch; export TMPDIR
hash() { sh "$repo/mk/verify-metadata.sh" hash-file "$1"; }
bounded() {
    if ! { test -f "$1" && test -r "$1" && ! test -L "$1"; }; then fail 'expected regular input'; fi
    bytes=$(wc -c < "$1") || fail 'cannot size input'
    bytes=$(printf '%s' "$bytes" | tr -d '[:space:]')
    case $bytes in ''|*[!0-9]*) fail 'invalid input size' ;; esac
    test "$bytes" -le "$2" || fail 'metadata limit exceeded'
}
# Bound inputs before delegating to the existing unbounded state parser.
snapshot() {
    selected=$1; output=$2
    if ! { test -d "$selected/state" && ! test -L "$selected/state" &&
        test -d "$selected/state/packages" && ! test -L "$selected/state/packages"; }; then fail 'invalid state directories'; fi
    bounded "$selected/state/world" 1048576
    digest=$(hash "$selected/state/world") || fail 'cannot hash world'
    printf 'world\t%s\n' "$digest" > "$output"
    count=0; total=0
    : > "$output.records"
    for record in "$selected/state/packages"/* "$selected/state/packages"/.[!.]* "$selected/state/packages"/..?*; do
        test -e "$record" || test -L "$record" || continue
        name=${record##*/}; name=${name%.tsv}
        case $name in ''|[!A-Za-z0-9]*|*[!A-Za-z0-9._+-]*) fail 'invalid record name' ;; esac
        test "$record" = "$selected/state/packages/$name.tsv" || fail 'invalid record filename'
        count=$((count+1)); test "$count" -le 1024 || fail 'package limit exceeded'
        bounded "$record" 1048576
        total=$((total+bytes)); test "$total" -le 16777216 || fail 'aggregate record limit exceeded'
        header=$(head -n 1 "$record") || fail 'cannot read record header'
        test "$header" = "$(printf 'format\tpkg-state-v2')" || fail 'v2 records required'
        digest=$(hash "$record") || fail 'cannot hash record'
        printf 'record\t%s\t%s\n' "$name" "$digest" >> "$output.records"
    done
    sort "$output.records" >> "$output"
    # All record bytes are now bounded. Reject excess edges before graph processing.
    : > "$output.edges"
    while IFS="$(printf '\t')" read -r _ name _; do
        awk -F '\t' -v name="$name" '$1=="dependency" {print name "\t" $2}' \
            "$selected/state/packages/$name.tsv" >> "$output.edges"
        edges=$(wc -l < "$output.edges")
        test "$edges" -le 16384 || fail 'edge limit exceeded'
    done < "$output.records"
}
verify() { sh "$repo/mk/state.sh" verify "$1" > "$scratch/verify" 2> "$scratch/verify-error" || fail 'state verification failed'; }
snapshot "$installed" "$scratch/installed"
snapshot "$candidate" "$scratch/candidate"
candidate_count=$(wc -l < "$scratch/candidate.records") || fail 'cannot count candidate records'
test "$candidate_count" -eq 1 || fail 'candidate must contain only SDK'
for selected in installed candidate; do
    selected_pin=$installed_pin
    test "$selected" != candidate || selected_pin=$candidate_pin
    actual=$(awk -F '\t' '$1=="record" && $2=="aether-musl-sdk" {print $3}' "$scratch/$selected")
    test "$actual" = "$selected_pin" || fail 'SDK record pin mismatch'
    sdk_edges=$(awk -F '\t' '$1=="aether-musl-sdk" {print}' "$scratch/$selected.edges") || fail 'cannot inspect SDK edges'
    test -z "$sdk_edges" || fail 'SDK dependencies unsupported'
done
verify "$installed"
verify "$candidate"
metadata=$candidate/stage/aether-musl-sdk/usr/local/share/pkg-mgr/aether-musl-sdk
sh "$repo/mk/sdk-profile.sh" "$metadata/sdk-target.kv" "$profile_pin" \
    "$metadata/sdk-build-receipt" "$metadata/sdk-native-profile" > "$scratch/profile" 2> "$scratch/profile-error" || fail 'candidate profile invalid'
# state verify enforces exact stage/manifest coverage; explicitly require profile rows.
for leaf in sdk-target.kv sdk-build-receipt sdk-native-profile; do
    awk -F '\t' -v path="usr/local/share/pkg-mgr/aether-musl-sdk/$leaf" \
        '$1=="file" && $4==path {found=1} END {exit !found}' \
        "$candidate/state/packages/aether-musl-sdk.tsv" || fail 'profile is not manifest-bound'
done
awk -F '\t' '$2=="aether-musl-sdk" {print $1}' "$scratch/installed.edges" > "$scratch/direct"
while IFS= read -r name; do
    stage=$installed/stage/$name
    binding_path=usr/local/share/pkg-mgr/$name/sdk-binding.kv
    binding=$stage/$binding_path
    bounded "$binding" 4096
    tr -d '\012\040-\176' < "$binding" > "$scratch/invalid-bytes" || fail 'cannot inspect binding bytes'
    test ! -s "$scratch/invalid-bytes" || fail 'invalid binding grammar'
    awk -v mode=binding -f "$repo/mk/sdk-rebuild-plan.awk" "$binding" > "$scratch/binding" || fail 'invalid binding grammar'
    cmp -s "$binding" "$scratch/binding" || fail 'noncanonical binding bytes'
    actual=$(sed -n '3s/^sdk_record_sha256=//p' "$scratch/binding")
    test "$actual" = "$installed_pin" || fail 'stale SDK binding'
    receipt_path=$(sed -n '4s/^input_receipt_path=//p' "$scratch/binding")
    artifact_path=$(sed -n '6s/^artifact_path=//p' "$scratch/binding")
    test "$receipt_path" != "$artifact_path" && test "$receipt_path" != "$binding_path" &&
        test "$artifact_path" != "$binding_path" || fail 'binding paths must be distinct'
    bounded "$stage/$receipt_path" 1048576
    for path in "$binding_path" "$receipt_path" "$artifact_path"; do
        actual=$(hash "$stage/$path") || fail 'cannot hash bound file'
        recorded=$(awk -F '\t' -v path="$path" '$1=="file" && $4==path {print $2}' "$installed/state/packages/$name.tsv")
        test "$actual" = "$recorded" || fail 'binding file is not manifest-bound'
        case $path in
            "$receipt_path")
                expected=$(sed -n '5s/^input_receipt_sha256=//p' "$scratch/binding") ;;
            "$artifact_path") expected=$(sed -n '7s/^artifact_sha256=//p' "$scratch/binding") ;;
            *) expected=$actual ;;
        esac
        test "$actual" = "$expected" || fail 'bound file hash mismatch'
    done
done < "$scratch/direct"
# Bound again before invoking the state parser on potentially changed inputs.
snapshot "$installed" "$scratch/pre-final-installed"
snapshot "$candidate" "$scratch/pre-final-candidate"
# The second verification plus inventory comparison detects ordinary input drift.
verify "$installed"
verify "$candidate"
snapshot "$installed" "$scratch/installed-final"
snapshot "$candidate" "$scratch/candidate-final"
for selected in installed candidate; do
    cmp -s "$scratch/$selected" "$scratch/$selected-final" || fail 'input drift detected'
done
{
    printf 'format\tsdk-rebuild-plan-v1\nsdk-installed\t%s\nsdk-candidate\t%s\ncandidate-profile\t%s\n' \
        "$installed_pin" "$candidate_pin" "$profile_pin"
    cat "$scratch/installed"
} > "$scratch/report"
if test "$installed_pin" != "$candidate_pin"; then
    awk -v mode=closure -f "$repo/mk/sdk-rebuild-plan.awk" \
        "$scratch/installed.records" "$scratch/installed.edges" > "$scratch/selection" || fail 'cannot select dependents'
    sort "$scratch/selection" >> "$scratch/report"
fi
cat "$scratch/report" || fail 'cannot deliver report'
