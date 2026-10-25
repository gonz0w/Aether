#!/bin/sh
# REQ-TMB-006 snapshot/index binding and optional signature verification seam.

set -eu

repo_root=$(CDPATH='' cd "$(dirname "$0")/.." && pwd)
verifier=$repo_root/mk/verify-metadata.sh
canonical_snapshot=$repo_root/fixtures/metadata-boundary/snapshot.kv
canonical_index=$repo_root/fixtures/metadata-boundary/index.tsv
tmp_root=$(mktemp -d "${TMPDIR:-/tmp}/pkg-mgr-snapshot.XXXXXX")
trap 'rm -rf "$tmp_root"' EXIT HUP INT TERM

fail() {
    printf '%s\n' "FAIL: $*" >&2
    exit 1
}

assert_eq() {
    test "$1" = "$2" || fail "$3: expected '$2', got '$1'"
}

hash_file() {
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$1" | awk '{ print $1 }'
    elif command -v shasum >/dev/null 2>&1; then
        shasum -a 256 "$1" | awk '{ print $1 }'
    elif command -v sha256 >/dev/null 2>&1; then
        sha256 -q "$1" 2>/dev/null || sha256 "$1" | awk '{ print $NF }'
    elif command -v openssl >/dev/null 2>&1; then
        openssl dgst -sha256 "$1" | awk '{ print $NF }'
    else
        fail 'no SHA-256 tool available to run snapshot tests'
    fi
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
    if "$@" >"$stdout" 2>"$stderr"; then status=0; else status=$?; fi
    if test "$expected_status" = zero; then
        test "$status" -eq 0 || fail "$label: expected success, got $status"
    else
        test "$status" -ne 0 || fail "$label: expected nonzero status"
    fi
    lines=$(awk 'END { print NR + 0 }' "$stdout")
    test "$lines" -eq 1 || fail "$label: expected one stdout line, got $lines"
    assert_eq "$(sed -n '1p' "$stdout")" "$expected_stdout" "$label stdout"
    if test "$expected_stderr" = empty; then
        test ! -s "$stderr" || fail "$label: expected empty stderr"
    else
        grep -F "$expected_stderr" "$stderr" >/dev/null || fail "$label: stderr lacks '$expected_stderr'"
    fi
}

replace_key() {
    key=$1
    value=$2
    input=$3
    output=$4
    awk -v key="$key" -v value="$value" '
        index($0, key "=") == 1 { print key "=" value; next }
        { print }
    ' "$input" > "$output"
}

refresh_snapshot_hash() {
    snapshot=$1
    without_hash=$tmp_root/snapshot-without-hash
    refreshed=$tmp_root/snapshot-refreshed
    sed '/^snapshot_hash=/d' "$snapshot" > "$without_hash"
    digest=$(hash_file "$without_hash")
    replace_key snapshot_hash "sha256:$digest" "$snapshot" "$refreshed"
    cp "$refreshed" "$snapshot"
}

run_unavailable() {
    label=$1
    snapshot=$2
    index=$3
    signature=$4
    public_key=$5
    run_expect "$label" zero \
        "result=tool-unavailable label=minisign-unavailable target=$snapshot" 'optional minisign command is unavailable' \
        env MINISIGN=pkg-mgr-minisign-unavailable sh "$verifier" verify-snapshot \
            "$snapshot" "$index" "$signature" "$public_key"
}

run_failure() {
    label=$1
    expected_label=$2
    target=$3
    diagnostic=$4
    snapshot=$5
    index=$6
    signature=${7-$tmp_root/missing-signature}
    public_key=${8-$tmp_root/missing-public-key}
    minisign_command=${9-pkg-mgr-minisign-unavailable}
    run_expect "$label" nonzero "result=fail label=$expected_label target=$target" "$diagnostic" \
        env MINISIGN="$minisign_command" sh "$verifier" verify-snapshot \
            "$snapshot" "$index" "$signature" "$public_key"
}

cd "$repo_root"

readable_signature_fixture=$tmp_root/readable-test-signature
readable_public_key_fixture=$tmp_root/readable-test-public-key
printf '%s\n' 'inert signature presence fixture; not cryptographic evidence' > "$readable_signature_fixture"
printf '%s\n' 'inert public-key presence fixture; not cryptographic evidence' > "$readable_public_key_fixture"

# Mandatory parsing and both hashes succeed before the absent optional tool is labeled.
run_expect 'direct unavailable signer' zero \
    'result=tool-unavailable label=minisign-unavailable target=fixtures/metadata-boundary/snapshot.kv' \
    'optional minisign command is unavailable' \
    env MINISIGN=pkg-mgr-minisign-unavailable sh mk/verify-metadata.sh verify-snapshot \
        fixtures/metadata-boundary/snapshot.kv fixtures/metadata-boundary/index.tsv \
        fixtures/metadata-boundary/snapshot.minisig fixtures/metadata-boundary/minisign.pub
run_expect 'make unavailable signer' zero \
    'result=tool-unavailable label=minisign-unavailable target=fixtures/metadata-boundary/snapshot.kv' \
    'optional minisign command is unavailable' \
    make -s -f mk/pkg.mk verify-snapshot-metadata MINISIGN=pkg-mgr-minisign-unavailable

# Hash-tool faults must stop before signer invocation and preserve input bytes.
hash_tools=$tmp_root/hash-tools
hash_temp=$tmp_root/hash-temp
mkdir "$hash_tools" "$hash_temp"
cp "$canonical_snapshot" "$tmp_root/snapshot-before"
cp "$canonical_index" "$tmp_root/index-before"
self_pin=$(sed -n 's/^snapshot_hash=sha256://p' "$canonical_snapshot")
index_pin=$(sed -n 's/^index_hash=sha256://p' "$canonical_snapshot")
cat > "$hash_tools/sha256sum" <<'HASH_TOOL'
#!/bin/sh
case $1 in
    *pkg-mgr-snapshot-content.*) stage=self; pin=$SELF_PIN ;;
    *) stage=index; pin=$INDEX_PIN ;;
esac
if test "$stage" = "$HASH_FAIL_STAGE"; then
    case $HASH_FAULT in
        fail) exit 73 ;;
        empty) exit 0 ;;
        malformed) printf 'invalid-digest\n'; exit 0 ;;
        plausible-failed) printf '%s\n' "$pin"; exit 73 ;;
    esac
fi
printf '%s\n' "$pin"
HASH_TOOL
cat > "$hash_tools/pkg-test-signer" <<'SIGNER_TOOL'
#!/bin/sh
: > "$SIGNER_MARKER"
exit 1
SIGNER_TOOL
chmod +x "$hash_tools/sha256sum" "$hash_tools/pkg-test-signer"
for hash_stage in self index; do
    case $hash_stage in
        self) hash_label="snapshot-hash-unavailable"; hash_target=$canonical_snapshot
              hash_diagnostic='could not calculate snapshot self-hash' ;;
        index) hash_label="index-hash-unavailable"; hash_target=$canonical_index
               hash_diagnostic='could not calculate index SHA-256' ;;
    esac
    for fault in fail empty malformed plausible-failed; do
        run_expect "hash $hash_stage $fault" nonzero \
            "result=fail label=$hash_label target=$hash_target" "$hash_diagnostic" \
            env PATH="$hash_tools:$PATH" TMPDIR="$hash_temp" SELF_PIN="$self_pin" INDEX_PIN="$index_pin" \
                HASH_FAIL_STAGE="$hash_stage" HASH_FAULT="$fault" MINISIGN=pkg-test-signer \
                SIGNER_MARKER="$tmp_root/signer-called" sh "$verifier" verify-snapshot \
                "$canonical_snapshot" "$canonical_index" "$readable_signature_fixture" "$readable_public_key_fixture"
        test ! -e "$tmp_root/signer-called" || fail 'hash failure reached signer'
        test -z "$(find "$hash_temp" -type f -print)" || fail 'hash failure leaked temporary file'
        cmp "$canonical_snapshot" "$tmp_root/snapshot-before"
        cmp "$canonical_index" "$tmp_root/index-before"
    done
done
# Prove the signer marker works after both controlled digests pass.
run_expect 'hash control reaches signer' nonzero \
    "result=fail label=bad-signature target=$canonical_snapshot" 'minisign rejected the snapshot signature' \
    env PATH="$hash_tools:$PATH" SELF_PIN="$self_pin" INDEX_PIN="$index_pin" HASH_FAIL_STAGE=none \
        HASH_FAULT=fail MINISIGN=pkg-test-signer SIGNER_MARKER="$tmp_root/signer-called" \
        sh "$verifier" verify-snapshot "$canonical_snapshot" "$canonical_index" \
        "$readable_signature_fixture" "$readable_public_key_fixture"
test -f "$tmp_root/signer-called" || fail 'signer control did not reach marker'
printf '%s\n' 'Eight hash-tool faults stop before signing; signer reachability control passed'

# Missing explicit evidence fails before signer detection.
missing=$tmp_root/missing
run_failure 'missing snapshot' snapshot-metadata-invalid "$missing" 'snapshot metadata is not a readable file' \
    "$missing" "$canonical_index"
run_failure 'missing index' index-metadata-invalid "$missing" 'index is not a readable file' \
    "$canonical_snapshot" "$missing"
run_failure 'missing signature' missing-signature "$missing" 'signature is not a readable file' \
    "$canonical_snapshot" "$canonical_index" "$missing" "$readable_public_key_fixture" true
run_failure 'missing public key' missing-public-key "$missing" 'public key is not a readable file' \
    "$canonical_snapshot" "$canonical_index" "$readable_signature_fixture" "$missing" true

# Snapshot records are strict inert data.
snapshot=$tmp_root/missing-key.kv
awk '$0 !~ /^key_id=/' "$canonical_snapshot" > "$snapshot"
run_failure 'missing snapshot key' snapshot-metadata-invalid "$snapshot" 'missing required key: key_id' "$snapshot" "$canonical_index"

snapshot=$tmp_root/duplicate-key.kv
cp "$canonical_snapshot" "$snapshot"
printf '%s\n' 'key_id=duplicate' >> "$snapshot"
run_failure 'duplicate snapshot key' snapshot-metadata-invalid "$snapshot" 'duplicate key: key_id' "$snapshot" "$canonical_index"

snapshot=$tmp_root/unknown-key.kv
cp "$canonical_snapshot" "$snapshot"
printf '%s\n' 'unknown=value' >> "$snapshot"
run_failure 'unknown snapshot key' snapshot-metadata-invalid "$snapshot" 'unknown key: unknown' "$snapshot" "$canonical_index"

snapshot=$tmp_root/empty-value.kv
replace_key signer_id '' "$canonical_snapshot" "$snapshot"
run_failure 'empty snapshot value' snapshot-metadata-invalid "$snapshot" 'empty value for key: signer_id' "$snapshot" "$canonical_index"

snapshot=$tmp_root/malformed.kv
cp "$canonical_snapshot" "$snapshot"
printf '%s\n' malformed >> "$snapshot"
run_failure 'malformed snapshot line' snapshot-metadata-invalid "$snapshot" 'malformed metadata line' "$snapshot" "$canonical_index"

snapshot=$tmp_root/unsupported-index-hash.kv
replace_key index_hash 'sha512:abcd' "$canonical_snapshot" "$snapshot"
run_failure 'unsupported index hash' snapshot-metadata-invalid "$snapshot" 'index_hash must be sha256' "$snapshot" "$canonical_index"

snapshot=$tmp_root/bad-self-hash-syntax.kv
replace_key snapshot_hash 'sha256:ABCD' "$canonical_snapshot" "$snapshot"
run_failure 'unsupported snapshot hash' snapshot-metadata-invalid "$snapshot" 'snapshot_hash must be sha256' "$snapshot" "$canonical_index"

snapshot=$tmp_root/self-hash-mismatch.kv
replace_key signer_id changed-without-rehash "$canonical_snapshot" "$snapshot"
run_failure 'snapshot self hash mismatch' snapshot-hash-mismatch "$snapshot" 'snapshot self-hash mismatch' "$snapshot" "$canonical_index"

# The exact Phase 2 index schema and C ordering are mandatory before index binding.
index=$tmp_root/wrong-header.tsv
sed '1s/namespace/origin/' "$canonical_index" > "$index"
run_failure 'wrong index header' index-metadata-invalid "$index" 'index header does not match' "$canonical_snapshot" "$index"

index=$tmp_root/wrong-columns.tsv
awk 'NR == 1 { print; next } { sub(/\t[^\t]*$/, ""); print }' "$canonical_index" > "$index"
run_failure 'wrong index columns' index-metadata-invalid "$index" 'index row must have exactly eight nonempty columns' "$canonical_snapshot" "$index"

index=$tmp_root/bad-source-hash.tsv
awk 'BEGIN { FS=OFS="\t" } NR == 1 { print; next } { $6="sha256:ABCD"; print }' "$canonical_index" > "$index"
run_failure 'bad index source hash' index-metadata-invalid "$index" 'index source_hash must be sha256' "$canonical_snapshot" "$index"

index=$tmp_root/bad-source-size.tsv
awk 'BEGIN { FS=OFS="\t" } NR == 1 { print; next } { $7="0105"; print }' "$canonical_index" > "$index"
run_failure 'bad index source size' index-metadata-invalid "$index" 'index source_size must be decimal bytes' "$canonical_snapshot" "$index"

index=$tmp_root/bad-manifest-hash.tsv
awk 'BEGIN { FS=OFS="\t" } NR == 1 { print; next } { $8="sha512:abcd"; print }' "$canonical_index" > "$index"
run_failure 'bad index manifest hash' index-metadata-invalid "$index" 'index manifest_hash must be sha256' "$canonical_snapshot" "$index"

index=$tmp_root/unsorted.tsv
cp "$canonical_index" "$index"
printf '%s\t%s\t%s\t%s\t%s\tsha256:%s\t%s\tsha256:%s\n' \
    aaa hello-local 0.1 recipes/hello-local/package.mk fixture-v1 \
    735aef1485e4d223e2f1cffb03395a8e1e7b865b14d31310da1dc8e7a3220610 105 \
    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa >> "$index"
run_failure 'unsorted index' index-metadata-invalid "$index" 'index rows are not C-locale sorted' "$canonical_snapshot" "$index"

index=$tmp_root/changed-index.tsv
sed '2s/\t105\t/\t106\t/' "$canonical_index" > "$index"
run_failure 'changed valid index' mix-and-match "$index" 'index SHA-256 does not match snapshot' "$canonical_snapshot" "$index"

# A command override is one executable name, never an evaluated command string.
run_expect 'unsafe minisign override' nonzero \
    'result=fail label=signer-command-invalid target=fixtures/metadata-boundary/snapshot.kv' \
    'MINISIGN must be one command name' \
    env MINISIGN='minisign --version' sh mk/verify-metadata.sh verify-snapshot \
        fixtures/metadata-boundary/snapshot.kv fixtures/metadata-boundary/index.tsv \
        fixtures/metadata-boundary/snapshot.minisig fixtures/metadata-boundary/minisign.pub

# Live cryptographic assertions are additive and conditional.
if command -v minisign >/dev/null 2>&1; then
    public_key=$tmp_root/minisign.pub
    secret_key=$tmp_root/minisign.key
    signature=$tmp_root/snapshot.minisig
    minisign -G -W -p "$public_key" -s "$secret_key" >/dev/null 2>&1
    minisign -S -W -s "$secret_key" -m "$canonical_snapshot" -x "$signature" >/dev/null 2>&1

    run_expect 'valid configured fixture signature' zero \
        "result=warn label=signature-not-sufficient target=$canonical_snapshot" \
        'configured fixture key signed the exact snapshot bytes' \
        sh "$verifier" verify-snapshot "$canonical_snapshot" "$canonical_index" "$signature" "$public_key"

    snapshot=$tmp_root/live-self-hash-mismatch.kv
    replace_key signer_id live-mutated "$canonical_snapshot" "$snapshot"
    run_failure 'live mutation fails at self hash' snapshot-hash-mismatch "$snapshot" \
        'snapshot self-hash mismatch' "$snapshot" "$canonical_index" "$signature" "$public_key"

    refresh_snapshot_hash "$snapshot"
    run_expect 'rehash without resigning' nonzero \
        "result=fail label=bad-signature target=$snapshot" 'minisign rejected the snapshot signature' \
        sh "$verifier" verify-snapshot "$snapshot" "$canonical_index" "$signature" "$public_key"

    corrupt_signature=$tmp_root/corrupt.minisig
    printf '%s\n' 'untrusted comment: intentionally corrupt fixture' 'not-a-valid-minisign-signature' > "$corrupt_signature"
    run_expect 'corrupt detached signature' nonzero \
        "result=fail label=bad-signature target=$canonical_snapshot" 'minisign rejected the snapshot signature' \
        sh "$verifier" verify-snapshot "$canonical_snapshot" "$canonical_index" "$corrupt_signature" "$public_key"

    printf '%s\n' 'live minisign verification: passed'
else
    printf '%s\n' 'live minisign verification: skipped (minisign unavailable)'
fi

printf '%s\n' 'REQ-TMB-006 strict snapshot metadata verification passed'
