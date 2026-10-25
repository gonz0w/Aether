#!/bin/sh
# REQ-TMB-005 source metadata verification seam.

set -eu

repo_root=$(CDPATH='' cd "$(dirname "$0")/.." && pwd)
verifier=$repo_root/mk/verify-metadata.sh
canonical_record=$repo_root/fixtures/metadata-boundary/source.kv
canonical_target=$repo_root/fixtures/sources/hello-local/hello.txt
tmp_root=$(mktemp -d "${TMPDIR:-/tmp}/pkg-mgr-source.XXXXXX")
trap 'rm -rf "$tmp_root"' EXIT HUP INT TERM

fail() {
    printf '%s\n' "FAIL: $*" >&2
    exit 1
}

assert_eq() {
    actual=$1
    expected=$2
    label=$3
    test "$actual" = "$expected" || fail "$label: expected '$expected', got '$actual'"
}

assert_one_line() {
    file=$1
    label=$2
    lines=$(awk 'END { print NR + 0 }' "$file")
    test "$lines" -eq 1 || fail "$label: expected exactly one stdout line, got $lines"
}

assert_no_downstream_artifacts() {
    root=$1
    label=$2
    for path in work stage manifests build-record.kv; do
        test ! -e "$root/$path" || fail "$label: unexpected downstream artifact $root/$path"
    done
}

run_expect() {
    label=$1
    expected_status=$2
    expected_stdout=$3
    expected_stderr=$4
    shift 4
    stdout=$tmp_root/stdout
    stderr=$tmp_root/stderr
    : > "$stdout"
    : > "$stderr"
    if "$@" >"$stdout" 2>"$stderr"; then
        status=0
    else
        status=$?
    fi
    if test "$expected_status" = zero; then
        test "$status" -eq 0 || fail "$label: expected success, got status $status ($(sed -n '1p' "$stderr"))"
    else
        test "$status" -ne 0 || fail "$label: expected nonzero status"
    fi
    assert_one_line "$stdout" "$label"
    assert_eq "$(sed -n '1p' "$stdout")" "$expected_stdout" "$label stdout"
    if test "$expected_stderr" = empty; then
        test ! -s "$stderr" || fail "$label: expected empty stderr"
    else
        test -s "$stderr" || fail "$label: expected stderr diagnostic"
        grep -F "$expected_stderr" "$stderr" >/dev/null || fail "$label: stderr lacks '$expected_stderr'"
    fi
}

write_record() {
    output=$1
    hash=${2-735aef1485e4d223e2f1cffb03395a8e1e7b865b14d31310da1dc8e7a3220610}
    size=${3-105}
    algorithm=${4-sha256}
    printf '%s\n' \
        'record_type=source' \
        'source_uri=file:fixtures/sources/hello-local/hello.txt' \
        'source_kind=local-file' \
        "source_hash_alg=$algorithm" \
        "source_hash=$hash" \
        "source_size=$size" \
        'verification_result=defer' \
        'result_label=source-authenticity-not-proven' > "$output"
}

run_invalid_record() {
    label=$1
    record=$2
    diagnostic=$3
    run_expect "$label" nonzero \
        "result=fail label=source-metadata-invalid target=$record" "$diagnostic" \
        sh "$verifier" verify-source "$record" "$canonical_target"
    assert_no_downstream_artifacts "$tmp_root" "$label"
}

# Canonical direct and make adapters emit the same one-line result and no success diagnostic.
cd "$repo_root"
run_expect 'direct canonical source' zero \
    'result=pass label=source-bytes-match target=fixtures/sources/hello-local/hello.txt' empty \
    sh mk/verify-metadata.sh verify-source fixtures/metadata-boundary/source.kv fixtures/sources/hello-local/hello.txt
run_expect 'make canonical source' zero \
    'result=pass label=source-bytes-match target=fixtures/sources/hello-local/hello.txt' empty \
    make -s -f mk/pkg.mk verify-source-metadata \
        SOURCE_METADATA=fixtures/metadata-boundary/source.kv \
        SOURCE_TARGET=fixtures/sources/hello-local/hello.txt

# Missing inputs fail with stable labels.
missing_record=$tmp_root/missing.kv
run_expect 'missing record' nonzero \
    "result=fail label=source-metadata-invalid target=$missing_record" 'metadata record is not a readable file' \
    sh "$verifier" verify-source "$missing_record" "$canonical_target"
missing_target=$tmp_root/missing-target
run_expect 'missing target' nonzero \
    "result=fail label=missing-target target=$missing_target" 'target is not a readable file' \
    sh "$verifier" verify-source "$canonical_record" "$missing_target"

# Strict schema failures share source-metadata-invalid and are never normalized.
record=$tmp_root/missing-key.kv
awk '$0 !~ /^source_size=/' "$canonical_record" > "$record"
run_invalid_record 'missing required key' "$record" 'missing required key: source_size'

record=$tmp_root/duplicate-key.kv
cp "$canonical_record" "$record"
printf '%s\n' 'source_size=105' >> "$record"
run_invalid_record 'duplicate key' "$record" 'duplicate key: source_size'

record=$tmp_root/unknown-key.kv
cp "$canonical_record" "$record"
printf '%s\n' 'unexpected=value' >> "$record"
run_invalid_record 'unknown key' "$record" 'unknown key: unexpected'

record=$tmp_root/empty-value.kv
awk '{ if ($0 ~ /^source_uri=/) print "source_uri="; else print }' "$canonical_record" > "$record"
run_invalid_record 'empty value' "$record" 'empty value for key: source_uri'

record=$tmp_root/malformed-line.kv
cp "$canonical_record" "$record"
printf '%s\n' 'not-a-key-value-line' >> "$record"
run_invalid_record 'malformed line' "$record" 'malformed metadata line'

record=$tmp_root/bad-record-type.kv
sed 's/^record_type=.*/record_type=archive/' "$canonical_record" > "$record"
run_invalid_record 'wrong record type' "$record" 'record_type must be source'

record=$tmp_root/bad-verification-result.kv
sed 's/^verification_result=.*/verification_result=pass/' "$canonical_record" > "$record"
run_invalid_record 'wrong verification result' "$record" 'verification_result must be defer'

record=$tmp_root/bad-result-label.kv
sed 's/^result_label=.*/result_label=source-authenticity-proven/' "$canonical_record" > "$record"
run_invalid_record 'wrong no-go label' "$record" 'result_label must be source-authenticity-not-proven'

for algorithm_case in sha512 SHA256
do
    record=$tmp_root/unsupported-algorithm-$algorithm_case.kv
    write_record "$record" 735aef1485e4d223e2f1cffb03395a8e1e7b865b14d31310da1dc8e7a3220610 105 "$algorithm_case"
    run_invalid_record "unsupported algorithm $algorithm_case" "$record" 'source_hash_alg must be sha256'
done

good_hash=735aef1485e4d223e2f1cffb03395a8e1e7b865b14d31310da1dc8e7a3220610
upper_hash=735AEF1485E4D223E2F1CFFB03395A8E1E7B865B14D31310DA1DC8E7A3220610
long_hash=${good_hash}0
for hash_case in \
    "sha256:$good_hash" \
    "$upper_hash" \
    735aef14 \
    "$long_hash" \
    735aef1485e4d223e2f1cffb03395a8e1e7b865b14d31310da1dc8e7a322061z \
    " $good_hash" \
    "$good_hash " \
    "other:$good_hash"
do
    record=$tmp_root/bad-hash-$(printf '%s' "$hash_case" | wc -c | tr -d ' ')-$(date +%s).kv
    # Reusing this path is safe: each invocation consumes the completed record synchronously.
    write_record "$record" "$hash_case"
    run_invalid_record "malformed digest $hash_case" "$record" 'source_hash must be 64 lowercase hexadecimal characters'
done

record=$tmp_root/valid-patch-hash.kv
cp "$canonical_record" "$record"
printf '%s\n' "patch_hash=$good_hash" >> "$record"
run_expect 'optional patch hash' zero \
    "result=pass label=source-bytes-match target=$canonical_target" empty \
    sh "$verifier" verify-source "$record" "$canonical_target"

record=$tmp_root/invalid-patch-hash.kv
cp "$canonical_record" "$record"
printf '%s\n' 'patch_hash=short' >> "$record"
run_invalid_record 'malformed optional patch hash' "$record" 'patch_hash must be 64 lowercase hexadecimal characters'

record=$tmp_root/empty-size.kv
write_record "$record" "$good_hash" ''
run_invalid_record "malformed size ''" "$record" 'empty value for key: source_size'

for size_case in -1 +105 0105 105x ' 105' '105 '
do
    record=$tmp_root/bad-size-$(printf '%s' "$size_case" | wc -c | tr -d ' ').kv
    write_record "$record" "$good_hash" "$size_case"
    run_invalid_record "malformed size '$size_case'" "$record" 'source_size must be decimal bytes'
done

# Byte evidence failures occur only after the complete record has validated.
same_size_target=$tmp_root/changed.txt
cp "$canonical_target" "$same_size_target"
printf X | dd of="$same_size_target" bs=1 seek=0 conv=notrunc 2>/dev/null
run_expect 'digest mismatch' nonzero \
    "result=fail label=source-hash-mismatch target=$same_size_target" 'SHA-256 mismatch' \
    sh "$verifier" verify-source "$canonical_record" "$same_size_target"
assert_no_downstream_artifacts "$tmp_root" 'digest mismatch'

larger_target=$tmp_root/larger.txt
cp "$canonical_target" "$larger_target"
printf x >> "$larger_target"
run_expect 'size mismatch' nonzero \
    "result=fail label=source-size-mismatch target=$larger_target" 'size mismatch' \
    sh "$verifier" verify-source "$canonical_record" "$larger_target"
assert_no_downstream_artifacts "$tmp_root" 'size mismatch'

# Explicit target paths containing spaces remain valid and are not derived from source_uri.
space_dir=$tmp_root/'directory with spaces'
mkdir -p "$space_dir"
space_target=$space_dir/'hello source.txt'
cp "$canonical_target" "$space_target"
run_expect 'target path with spaces' zero \
    "result=pass label=source-bytes-match target=$space_target" empty \
    sh "$verifier" verify-source "$canonical_record" "$space_target"

python3 "$repo_root/tests/trust-metadata-corpus.py"
printf '%s\n' 'REQ-TMB-005 strict source metadata verification passed'
