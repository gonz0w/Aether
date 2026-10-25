#!/bin/sh
# REQ-TMB-007 deterministic manifests/build records and REQ-TMB-008 advisory SPDX checks.

set -eu

repo_root=$(CDPATH='' cd "$(dirname "$0")/.." && pwd -P)
verifier=$repo_root/mk/verify-metadata.sh
canonical_build=$repo_root/fixtures/metadata-boundary/build-input.kv
canonical_source=$repo_root/fixtures/metadata-boundary/source.kv
canonical_sbom=$repo_root/fixtures/metadata-boundary/advisory.spdx
canonical_material=$repo_root/fixtures/sources/hello-local/hello.txt
tmp_root=$(mktemp -d "$repo_root/.pkg-mgr-records.XXXXXX")
tmp_rel=${tmp_root#"$repo_root/"}
trap 'rm -rf "$tmp_root"' EXIT HUP INT TERM

fail() {
    printf '%s\n' "FAIL: $*" >&2
    exit 1
}

hash_file() {
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$1" | awk '{print $1}'
    elif command -v shasum >/dev/null 2>&1; then
        shasum -a 256 "$1" | awk '{print $1}'
    elif command -v sha256 >/dev/null 2>&1; then
        sha256 -q "$1" 2>/dev/null || sha256 "$1" | awk '{print $NF}'
    elif command -v openssl >/dev/null 2>&1; then
        openssl dgst -sha256 "$1" | awk '{print $NF}'
    else
        fail 'no SHA-256 tool is available to verify test evidence'
    fi
}

assert_eq() {
    actual=$1
    expected=$2
    label=$3
    test "$actual" = "$expected" || fail "$label: expected '$expected', got '$actual'"
}

assert_one_line() {
    lines=$(awk 'END { print NR + 0 }' "$1")
    test "$lines" -eq 1 || fail "$2: expected exactly one stdout line, got $lines"
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
        test "$status" -eq 0 || fail "$label: expected success, got $status ($(sed -n '1p' "$stderr"))"
    else
        test "$status" -ne 0 || fail "$label: expected nonzero status"
    fi
    assert_one_line "$stdout" "$label"
    assert_eq "$(sed -n '1p' "$stdout")" "$expected_stdout" "$label stdout"
    if test "$expected_stderr" = empty; then
        test ! -s "$stderr" || fail "$label: expected empty stderr"
    else
        test -s "$stderr" || fail "$label: expected stderr"
        grep -F "$expected_stderr" "$stderr" >/dev/null || fail "$label: stderr lacks '$expected_stderr'"
    fi
}

replace_field() {
    input=$1
    output=$2
    key=$3
    value=$4
    awk -v key="$key" -v value="$value" '
        index($0, key "=") == 1 { print key "=" value; next }
        { print }
    ' "$input" > "$output"
}

remove_field() {
    awk -v key="$3" 'index($0, key "=") != 1' "$1" > "$2"
}

run_build_failure() {
    label=$1
    input=$2
    diagnostic=$3
    output=$tmp_root/build-failure.kv
    rm -f "$output"
    run_expect "$label" nonzero \
        "result=fail label=material-reference-invalid target=$input" "$diagnostic" \
        sh "$verifier" build-record "$input" "$output"
    test ! -e "$output" || fail "$label: partial build record was published"
}

run_sbom_failure() {
    label=$1
    input=$2
    diagnostic=$3
    run_expect "$label" nonzero \
        "result=fail label=sbom-record-invalid target=$input" "$diagnostic" \
        sh "$verifier" check-sbom "$input"
}

cd "$repo_root"

# Stable, C-sorted package manifests preserve spaces and bind exact bytes.
stage=$tmp_root/stage
mkdir -p "$stage/z directory" "$stage/a"
printf '%s\n' alpha > "$stage/z directory/file with spaces.txt"
printf '%s\n' beta > "$stage/a/first.txt"
manifest_one=$tmp_root/manifest-one.tsv
manifest_two=$tmp_root/manifest-two.tsv
run_expect 'first manifest' zero \
    "result=pass label=package-manifest-created target=$manifest_one" empty \
    sh "$verifier" manifest "$stage" "$manifest_one"
run_expect 'second manifest' zero \
    "result=pass label=package-manifest-created target=$manifest_two" empty \
    sh "$verifier" manifest "$stage" "$manifest_two"
cmp -s "$manifest_one" "$manifest_two" || fail 'identical stages produced different manifests'
tab=$(printf '\t')
LC_ALL=C sort -t "$tab" -k3,3 "$manifest_one" > "$tmp_root/sorted.tsv"
cmp -s "$manifest_one" "$tmp_root/sorted.tsv" || fail 'manifest is not C-sorted by path'
awk -F '\t' '
    NF != 3 || length($1) != 64 || $1 ~ /[^0123456789abcdef]/ || $2 !~ /^[0-9]+$/ || $3 == "" { exit 1 }
    $3 == "z directory/file with spaces.txt" { spaces++ }
    END { exit !(NR == 2 && spaces == 1) }
' "$manifest_one" || fail 'manifest row shape or space path is invalid'
expected_hash=$(hash_file "$stage/a/first.txt")
expected_size=$(wc -c < "$stage/a/first.txt" | tr -d '[:space:]')
grep -F "$expected_hash$tab$expected_size${tab}a/first.txt" "$manifest_one" >/dev/null || fail 'manifest lacks actual hash/size row'

empty_stage=$tmp_root/empty-stage
mkdir "$empty_stage"
empty_manifest=$tmp_root/empty.tsv
run_expect 'empty manifest' zero \
    "result=pass label=package-manifest-created target=$empty_manifest" empty \
    sh "$verifier" manifest "$empty_stage" "$empty_manifest"
test ! -s "$empty_manifest" || fail 'empty stage manifest is not empty'

make_manifest=$tmp_root/make-manifest.tsv
run_expect 'make manifest adapter' zero \
    "result=pass label=package-manifest-created target=$make_manifest" empty \
    make -s -f mk/pkg.mk hashed-manifest STAGEDIR="$stage" HASHED_MANIFEST="$make_manifest"
cmp -s "$manifest_one" "$make_manifest" || fail 'make manifest differs from direct manifest'

printf '%s\n' changed > "$stage/a/first.txt"
changed_manifest=$tmp_root/changed.tsv
run_expect 'changed manifest' zero \
    "result=pass label=package-manifest-created target=$changed_manifest" empty \
    sh "$verifier" manifest "$stage" "$changed_manifest"
cmp -s "$manifest_one" "$changed_manifest" && fail 'content drift did not change manifest'

missing_stage=$tmp_root/missing-stage
missing_output=$tmp_root/missing-output.tsv
run_expect 'missing stage' nonzero \
    "result=fail label=manifest-input-invalid target=$missing_stage" 'stage directory is not readable' \
    sh "$verifier" manifest "$missing_stage" "$missing_output"
test ! -e "$missing_output" || fail 'missing stage published a manifest'

bad_stage=$tmp_root/bad-stage
mkdir "$bad_stage"
tab_name=$(printf 'tab\tname')
newline_name='newline
name'
printf x > "$bad_stage/$tab_name"
bad_output=$tmp_root/bad-output.tsv
run_expect 'tab filename' nonzero \
    "result=fail label=manifest-path-invalid target=$bad_stage" 'tab or newline' \
    sh "$verifier" manifest "$bad_stage" "$bad_output"
test ! -e "$bad_output" || fail 'tab filename published a manifest'
rm -f "$bad_stage/$tab_name"
printf x > "$bad_stage/$newline_name"
run_expect 'newline filename' nonzero \
    "result=fail label=manifest-path-invalid target=$bad_stage" 'tab or newline' \
    sh "$verifier" manifest "$bad_stage" "$bad_output"
test ! -e "$bad_output" || fail 'newline filename published a manifest'

fake_bin=$tmp_root/fake-bin
mkdir "$fake_bin"
printf '%s\n' '#!/bin/sh' 'exit 9' > "$fake_bin/sha256sum"
chmod +x "$fake_bin/sha256sum"
hash_failure_output=$tmp_root/hash-failure.tsv
run_expect 'forced hash failure' nonzero \
    "result=fail label=manifest-hash-unavailable target=$stage" 'could not hash staged file' \
    env PATH="$fake_bin:$PATH" sh "$verifier" manifest "$stage" "$hash_failure_output"
test ! -e "$hash_failure_output" || fail 'hash failure published a manifest'

# Use a repository-relative generated manifest as canonical build evidence.
canonical_manifest=$tmp_root/package-manifest.tsv
canonical_manifest_rel=$tmp_rel/package-manifest.tsv
sh "$verifier" manifest "$stage" "$canonical_manifest" >/dev/null
build_input=$tmp_root/build-input.kv
replace_field "$canonical_build" "$build_input" manifest_ref "$canonical_manifest_rel"
build_one=$tmp_root/build-one.kv
build_two=$tmp_root/build-two.kv
run_expect 'first build record' zero \
    "result=warn label=reproducible-build-success-not-proven target=$build_one" empty \
    sh "$verifier" build-record "$build_input" "$build_one"
run_expect 'second build record' zero \
    "result=warn label=reproducible-build-success-not-proven target=$build_two" empty \
    sh "$verifier" build-record "$build_input" "$build_two"
cmp -s "$build_one" "$build_two" || fail 'identical build inputs produced different records'
outside_cwd_build=$tmp_root/outside-cwd-build.kv
run_expect 'build record outside repository cwd' zero \
    "result=warn label=reproducible-build-success-not-proven target=$outside_cwd_build" empty \
    sh -c "cd / && exec sh \"\$1\" build-record \"\$2\" \"\$3\"" sh "$verifier" "$build_input" "$outside_cwd_build"
cmp -s "$build_one" "$outside_cwd_build" || fail 'caller cwd changed deterministic build record'
manifest_hash=$(hash_file "$canonical_manifest")
grep -qx "manifest_hash=sha256:$manifest_hash" "$build_one" || fail 'build record lacks actual manifest hash'
for line in \
    'source_hash_alg=sha256' \
    'source_hash=735aef1485e4d223e2f1cffb03395a8e1e7b865b14d31310da1dc8e7a3220610' \
    'materials_ref=fixtures/metadata-boundary/source.kv' \
    'material_path=fixtures/sources/hello-local/hello.txt' \
    'sbom_ref=fixtures/metadata-boundary/advisory.spdx' \
    'builder_label=local-fixture' \
    'provenance_confidence=advisory' \
    'result_label=reproducible-build-success-not-proven'
do
    grep -qx "$line" "$build_one" || fail "build record lacks $line"
done
if grep -E '(^|_)(host|time|timestamp|random|uuid)=' "$build_one" >/dev/null || grep -F "$tmp_root" "$build_one" >/dev/null; then
    fail 'build record contains ambient host/time/random/absolute temporary data'
fi

make_build=$tmp_root/make-build.kv
run_expect 'make build-record adapter' zero \
    "result=warn label=reproducible-build-success-not-proven target=$make_build" empty \
    make -s -f mk/pkg.mk build-record BUILD_RECORD_INPUT="$build_input" BUILD_RECORD="$make_build"
cmp -s "$build_one" "$make_build" || fail 'make build record differs from direct build record'

printf '%s\n' additional >> "$stage/a/first.txt"
sh "$verifier" manifest "$stage" "$canonical_manifest" >/dev/null
build_changed=$tmp_root/build-changed.kv
sh "$verifier" build-record "$build_input" "$build_changed" >/dev/null
cmp -s "$build_one" "$build_changed" && fail 'manifest drift did not change build record'

# Canonical digest representation is never prefixed, case-folded, trimmed, or repaired.
good_hash=735aef1485e4d223e2f1cffb03395a8e1e7b865b14d31310da1dc8e7a3220610
upper_hash=735AEF1485E4D223E2F1CFFB03395A8E1E7B865B14D31310DA1DC8E7A3220610
long_hash=${good_hash}0
case_number=0
for bad_hash in "sha256:$good_hash" "$upper_hash" short "$long_hash" \
    735aef1485e4d223e2f1cffb03395a8e1e7b865b14d31310da1dc8e7a322061z \
    " $good_hash" "$good_hash "
do
    case_number=$((case_number + 1))
    invalid=$tmp_root/bad-hash-$case_number.kv
    replace_field "$build_input" "$invalid" source_hash "$bad_hash"
    run_build_failure "bad build digest $case_number" "$invalid" 'source_hash must be raw 64-character lowercase hexadecimal'
done
for bad_alg in SHA256 sha512
do
    invalid=$tmp_root/bad-alg-$bad_alg.kv
    replace_field "$build_input" "$invalid" source_hash_alg "$bad_alg"
    run_build_failure "bad build algorithm $bad_alg" "$invalid" 'source_hash_alg must be sha256'
done

source_copy=$tmp_root/source.kv
source_copy_rel=$tmp_rel/source.kv
replace_field "$canonical_source" "$source_copy" source_hash_alg sha512
invalid=$tmp_root/source-alg-mismatch.kv
replace_field "$build_input" "$invalid" materials_ref "$source_copy_rel"
run_build_failure 'source/build algorithm mismatch' "$invalid" 'source metadata record is invalid'
replace_field "$canonical_source" "$source_copy" source_hash 035aef1485e4d223e2f1cffb03395a8e1e7b865b14d31310da1dc8e7a3220610
run_build_failure 'source/build digest mismatch' "$invalid" 'source_hash does not match build input'
replace_field "$canonical_source" "$source_copy" source_size 106
run_build_failure 'source material size mismatch' "$invalid" 'material size does not match source metadata'

material_copy=$tmp_root/material.txt
material_copy_rel=$tmp_rel/material.txt
cp "$canonical_material" "$material_copy"
printf X | dd of="$material_copy" bs=1 seek=0 conv=notrunc 2>/dev/null
replace_field "$canonical_source" "$source_copy" source_uri "file:$material_copy_rel"
invalid=$tmp_root/local-byte-mismatch.kv
replace_field "$build_input" "$invalid" materials_ref "$source_copy_rel"
replace_field "$invalid" "$invalid.next" material_path "$material_copy_rel"
mv "$invalid.next" "$invalid"
run_build_failure 'local byte digest mismatch' "$invalid" 'material SHA-256 does not match source metadata'

# Every local reference is rooted, regular, non-symlinked, and byte-consistent.
for unsafe in /absolute ../escape a//b a/./b a/../b
do
    invalid=$tmp_root/unsafe-$(printf '%s' "$unsafe" | tr '/.' '__').kv
    replace_field "$build_input" "$invalid" manifest_ref "$unsafe"
    run_build_failure "unsafe manifest ref $unsafe" "$invalid" 'unsafe repository-relative path'
done
invalid=$tmp_root/missing-manifest.kv
replace_field "$build_input" "$invalid" manifest_ref "$tmp_rel/missing-manifest.tsv"
run_build_failure 'missing manifest' "$invalid" 'manifest_ref is not a readable regular file'
invalid=$tmp_root/missing-sbom.kv
replace_field "$build_input" "$invalid" sbom_ref "$tmp_rel/missing.spdx"
run_build_failure 'missing SBOM' "$invalid" 'sbom_ref is not a readable regular file'
ln -s /etc "$tmp_root/outside-parent"
invalid=$tmp_root/escaping-parent.kv
replace_field "$build_input" "$invalid" manifest_ref "$tmp_rel/outside-parent/hosts"
run_build_failure 'symlinked escaping parent' "$invalid" 'manifest_ref parent escapes repository root'
invalid=$tmp_root/missing-material.kv
replace_field "$build_input" "$invalid" material_path "$tmp_rel/missing.txt"
run_build_failure 'missing material' "$invalid" 'material_path is not a readable regular file'

symlink_path=$tmp_root/material-link
ln -s "$canonical_material" "$symlink_path"
invalid=$tmp_root/symlink-material.kv
replace_field "$build_input" "$invalid" material_path "$tmp_rel/material-link"
run_build_failure 'symlink material' "$invalid" 'material_path must not be a final symlink'

replace_field "$canonical_source" "$source_copy" source_uri 'https://example.invalid/source'
invalid=$tmp_root/unsupported-source-uri.kv
replace_field "$build_input" "$invalid" materials_ref "$source_copy_rel"
run_build_failure 'unsupported source URI' "$invalid" 'source_uri must be canonical local file reference'
replace_field "$canonical_source" "$source_copy" source_uri 'file:fixtures/sources/hello-local/other.txt'
run_build_failure 'URI path disagreement' "$invalid" 'material reference does not match source_uri'

missing_input=$tmp_root/missing-input.kv
missing_build=$tmp_root/missing-build.kv
run_expect 'missing build input' nonzero \
    "result=fail label=build-record-invalid target=$missing_input" 'build input is not a readable file' \
    sh "$verifier" build-record "$missing_input" "$missing_build"
test ! -e "$missing_build" || fail 'missing build input published output'
malformed=$tmp_root/malformed-build.kv
remove_field "$build_input" "$malformed" builder_label
run_expect 'malformed build input' nonzero \
    "result=fail label=build-record-invalid target=$malformed" 'missing required key: builder_label' \
    sh "$verifier" build-record "$malformed" "$missing_build"
test ! -e "$missing_build" || fail 'malformed build input published output'

# The checked-in bounded SPDX 2.3 sample is advisory even when structurally valid.
run_expect 'canonical SPDX advisory' zero \
    "result=warn label=sbom-completeness-not-proven target=$canonical_sbom" empty \
    sh "$verifier" check-sbom "$canonical_sbom"
run_expect 'make SPDX advisory' zero \
    'result=warn label=sbom-completeness-not-proven target=fixtures/metadata-boundary/advisory.spdx' empty \
    make -s -f mk/pkg.mk check-sbom SBOM_RECORD=fixtures/metadata-boundary/advisory.spdx

sbom_case=$tmp_root/missing-spdx-version.spdx
awk '$0 !~ /^SPDXVersion:/' "$canonical_sbom" > "$sbom_case"
run_sbom_failure 'missing SPDX field' "$sbom_case" 'missing required field: SPDXVersion'
sbom_case=$tmp_root/duplicate-package-name.spdx
cp "$canonical_sbom" "$sbom_case"
printf '%s\n' 'PackageName: duplicate' >> "$sbom_case"
run_sbom_failure 'duplicate SPDX field' "$sbom_case" 'duplicate field: PackageName'
sbom_case=$tmp_root/bad-created.spdx
sed 's/^Created:.*/Created: 2026-08-30/' "$canonical_sbom" > "$sbom_case"
run_sbom_failure 'malformed SPDX field' "$sbom_case" 'Created must use UTC syntax'
sbom_case=$tmp_root/bad-relationship.spdx
sed 's/^Relationship:.*/Relationship: SPDXRef-DOCUMENT DESCRIBES SPDXRef-Other/' "$canonical_sbom" > "$sbom_case"
run_sbom_failure 'wrong SPDX relationship' "$sbom_case" 'Relationship must describe the package SPDXID'

printf '%s\n' \
    'REQ-TMB-007 deterministic package and build records passed' \
    'REQ-TMB-008 advisory SPDX verification passed'
