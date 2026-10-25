#!/bin/sh
set -eu

script_dir=$(CDPATH='' cd "$(dirname "$0")" && pwd -P)
repo_root=$(CDPATH='' cd "$script_dir/.." && pwd -P)
script_path=$repo_root/mk/verify-metadata.sh
temporary_output=

cleanup_temporary_output() {
    if test -n "$temporary_output"; then
        rm -f "$temporary_output"
    fi
}

trap cleanup_temporary_output EXIT HUP INT TERM

emit_result() {
    printf 'result=%s label=%s target=%s\n' "$1" "$2" "$3"
}

diagnose() {
    printf '%s\n' "$*" >&2
}

fail_result() {
    label=$1
    target=$2
    shift 2
    diagnose "$*"
    emit_result fail "$label" "$target"
    return 1
}

is_sha256() {
    value=$1
    case $value in
        *[!0123456789abcdef]*|'') return 1 ;;
    esac
    test "${#value}" -eq 64
}

is_prefixed_sha256() {
    case $1 in
        sha256:*) is_sha256 "${1#sha256:}" ;;
        *) return 1 ;;
    esac
}

is_decimal_bytes() {
    case $1 in
        *[!0-9]*|'') return 1 ;;
    esac
    case $1 in
        0|[1-9]*) return 0 ;;
        *) return 1 ;;
    esac
}

byte_count() {
    count=$(wc -c < "$1") || return 1
    count=$(printf '%s' "$count" | tr -d '[:space:]')
    is_decimal_bytes "$count" || return 1
    printf '%s\n' "$count"
}

sha256_file() {
    file=$1
    if command -v sha256sum >/dev/null 2>&1; then
        output=$(sha256sum "$file") || return 1
        digest=${output%%[!0123456789abcdef]*}
    elif command -v shasum >/dev/null 2>&1; then
        output=$(shasum -a 256 "$file") || return 1
        digest=${output%%[!0123456789abcdef]*}
    elif command -v sha256 >/dev/null 2>&1; then
        if output=$(sha256 -q "$file" 2>/dev/null); then
            digest=$output
        else
            output=$(sha256 "$file") || return 1
            digest=${output##* }
        fi
    elif command -v openssl >/dev/null 2>&1; then
        output=$(openssl dgst -sha256 "$file") || return 1
        digest=${output##* }
    else
        return 127
    fi
    is_sha256 "$digest" || return 1
    printf '%s\n' "$digest"
}

# Diagnostics only: record paths are reported by the outer operation result.
invalid_record() {
    diagnose "$1"
    return 1
}

parse_source_record() {
    record=$1

    record_type=
    source_uri=
    source_hash_alg=
    source_hash=
    source_size=
    patch_hash=
    verification_result=
    result_label=

    seen_record_type=false
    seen_source_uri=false
    seen_source_kind=false
    seen_source_hash_alg=false
    seen_source_hash=false
    seen_source_size=false
    seen_patch_hash=false
    seen_verification_result=false
    seen_result_label=false

    while IFS= read -r line || test -n "$line"; do
        case $line in
            *=*)
                key=${line%%=*}
                value=${line#*=}
                ;;
            *) invalid_record 'malformed metadata line' || return 1 ;;
        esac
        test -n "$key" || { invalid_record 'malformed metadata line' || return 1; }
        test -n "$value" || { invalid_record "empty value for key: $key" || return 1; }

        case $key in
            record_type)
                test "$seen_record_type" = false || { invalid_record 'duplicate key: record_type' || return 1; }
                seen_record_type=true
                record_type=$value
                ;;
            source_uri)
                test "$seen_source_uri" = false || { invalid_record 'duplicate key: source_uri' || return 1; }
                seen_source_uri=true
                source_uri=$value
                ;;
            source_kind)
                test "$seen_source_kind" = false || { invalid_record 'duplicate key: source_kind' || return 1; }
                seen_source_kind=true
                # Required descriptive metadata, not fetch or trust authority.
                ;;
            source_hash_alg)
                test "$seen_source_hash_alg" = false || { invalid_record 'duplicate key: source_hash_alg' || return 1; }
                seen_source_hash_alg=true
                source_hash_alg=$value
                ;;
            source_hash)
                test "$seen_source_hash" = false || { invalid_record 'duplicate key: source_hash' || return 1; }
                seen_source_hash=true
                source_hash=$value
                ;;
            source_size)
                test "$seen_source_size" = false || { invalid_record 'duplicate key: source_size' || return 1; }
                seen_source_size=true
                source_size=$value
                ;;
            patch_hash)
                test "$seen_patch_hash" = false || { invalid_record 'duplicate key: patch_hash' || return 1; }
                seen_patch_hash=true
                patch_hash=$value
                ;;
            verification_result)
                test "$seen_verification_result" = false || { invalid_record 'duplicate key: verification_result' || return 1; }
                seen_verification_result=true
                verification_result=$value
                ;;
            result_label)
                test "$seen_result_label" = false || { invalid_record 'duplicate key: result_label' || return 1; }
                seen_result_label=true
                result_label=$value
                ;;
            *) invalid_record "unknown key: $key" || return 1 ;;
        esac
    done < "$record"

    for required in \
        record_type source_uri source_kind source_hash_alg source_hash source_size \
        verification_result result_label
    do
        case $required in
            record_type) seen=$seen_record_type ;;
            source_uri) seen=$seen_source_uri ;;
            source_kind) seen=$seen_source_kind ;;
            source_hash_alg) seen=$seen_source_hash_alg ;;
            source_hash) seen=$seen_source_hash ;;
            source_size) seen=$seen_source_size ;;
            verification_result) seen=$seen_verification_result ;;
            result_label) seen=$seen_result_label ;;
        esac
        test "$seen" = true || { invalid_record "missing required key: $required" || return 1; }
    done

    test "$record_type" = source || { invalid_record 'record_type must be source' || return 1; }
    test "$source_hash_alg" = sha256 || { invalid_record 'source_hash_alg must be sha256' || return 1; }
    is_sha256 "$source_hash" || { invalid_record 'source_hash must be 64 lowercase hexadecimal characters' || return 1; }
    is_decimal_bytes "$source_size" || { invalid_record 'source_size must be decimal bytes' || return 1; }
    if test "$seen_patch_hash" = true; then
        is_sha256 "$patch_hash" || { invalid_record 'patch_hash must be 64 lowercase hexadecimal characters' || return 1; }
    fi
    test "$verification_result" = defer || { invalid_record 'verification_result must be defer' || return 1; }
    test "$result_label" = source-authenticity-not-proven || {
        invalid_record 'result_label must be source-authenticity-not-proven' || return 1
    }
}

parse_snapshot_record() {
    record=$1

    record_type=
    snapshot_hash=
    index_hash=
    signed_object=
    signature_status=
    tool_status=

    seen_record_type=false
    # These descriptive fields are required/nonempty/unique, but this research
    # verifier does not enforce identity, time freshness or metadata-selected keys.
    # The explicit caller arguments below select signature inputs.
    seen_snapshot_id=false
    seen_snapshot_hash=false
    seen_generated_at=false
    seen_valid_until=false
    seen_previous_snapshot_id=false
    seen_index_hash=false
    seen_signed_object=false
    seen_signer_id=false
    seen_key_id=false
    seen_signature_path=false
    seen_signature_status=false
    seen_expires_at=false
    seen_tool_status=false

    while IFS= read -r line || test -n "$line"; do
        case $line in
            *=*) key=${line%%=*}; value=${line#*=} ;;
            *) invalid_record 'malformed metadata line' || return 1 ;;
        esac
        test -n "$key" || { invalid_record 'malformed metadata line' || return 1; }
        test -n "$value" || { invalid_record "empty value for key: $key" || return 1; }

        case $key in
            record_type) seen_name=seen_record_type ;;
            snapshot_id) seen_name=seen_snapshot_id ;;
            snapshot_hash) seen_name=seen_snapshot_hash ;;
            generated_at) seen_name=seen_generated_at ;;
            valid_until) seen_name=seen_valid_until ;;
            previous_snapshot_id) seen_name=seen_previous_snapshot_id ;;
            index_hash) seen_name=seen_index_hash ;;
            signed_object) seen_name=seen_signed_object ;;
            signer_id) seen_name=seen_signer_id ;;
            key_id) seen_name=seen_key_id ;;
            signature_path) seen_name=seen_signature_path ;;
            signature_status) seen_name=seen_signature_status ;;
            expires_at) seen_name=seen_expires_at ;;
            tool_status) seen_name=seen_tool_status ;;
            *) invalid_record "unknown key: $key" || return 1 ;;
        esac

        case $seen_name in
            seen_record_type) seen=$seen_record_type ;;
            seen_snapshot_id) seen=$seen_snapshot_id ;;
            seen_snapshot_hash) seen=$seen_snapshot_hash ;;
            seen_generated_at) seen=$seen_generated_at ;;
            seen_valid_until) seen=$seen_valid_until ;;
            seen_previous_snapshot_id) seen=$seen_previous_snapshot_id ;;
            seen_index_hash) seen=$seen_index_hash ;;
            seen_signed_object) seen=$seen_signed_object ;;
            seen_signer_id) seen=$seen_signer_id ;;
            seen_key_id) seen=$seen_key_id ;;
            seen_signature_path) seen=$seen_signature_path ;;
            seen_signature_status) seen=$seen_signature_status ;;
            seen_expires_at) seen=$seen_expires_at ;;
            seen_tool_status) seen=$seen_tool_status ;;
        esac
        test "$seen" = false || { invalid_record "duplicate key: $key" || return 1; }

        case $key in
            record_type) record_type=$value; seen_record_type=true ;;
            snapshot_id) seen_snapshot_id=true ;;
            snapshot_hash) snapshot_hash=$value; seen_snapshot_hash=true ;;
            generated_at) seen_generated_at=true ;;
            valid_until) seen_valid_until=true ;;
            previous_snapshot_id) seen_previous_snapshot_id=true ;;
            index_hash) index_hash=$value; seen_index_hash=true ;;
            signed_object) signed_object=$value; seen_signed_object=true ;;
            signer_id) seen_signer_id=true ;;
            key_id) seen_key_id=true ;;
            signature_path) seen_signature_path=true ;;
            signature_status) signature_status=$value; seen_signature_status=true ;;
            expires_at) seen_expires_at=true ;;
            tool_status) tool_status=$value; seen_tool_status=true ;;
        esac
    done < "$record"

    for required in record_type snapshot_id snapshot_hash generated_at valid_until \
        previous_snapshot_id index_hash signed_object signer_id key_id signature_path \
        signature_status expires_at tool_status
    do
        case $required in
            record_type) seen=$seen_record_type ;;
            snapshot_id) seen=$seen_snapshot_id ;;
            snapshot_hash) seen=$seen_snapshot_hash ;;
            generated_at) seen=$seen_generated_at ;;
            valid_until) seen=$seen_valid_until ;;
            previous_snapshot_id) seen=$seen_previous_snapshot_id ;;
            index_hash) seen=$seen_index_hash ;;
            signed_object) seen=$seen_signed_object ;;
            signer_id) seen=$seen_signer_id ;;
            key_id) seen=$seen_key_id ;;
            signature_path) seen=$seen_signature_path ;;
            signature_status) seen=$seen_signature_status ;;
            expires_at) seen=$seen_expires_at ;;
            tool_status) seen=$seen_tool_status ;;
        esac
        test "$seen" = true || { invalid_record "missing required key: $required" || return 1; }
    done

    test "$record_type" = snapshot || { invalid_record 'record_type must be snapshot' || return 1; }
    is_prefixed_sha256 "$snapshot_hash" || { invalid_record 'snapshot_hash must be sha256:<64 lowercase hexadecimal characters>' || return 1; }
    is_prefixed_sha256 "$index_hash" || { invalid_record 'index_hash must be sha256:<64 lowercase hexadecimal characters>' || return 1; }
    test "$signed_object" = snapshot || { invalid_record 'signed_object must be snapshot' || return 1; }
    test "$signature_status" = defer || { invalid_record 'signature_status must be defer' || return 1; }
    test "$tool_status" = tool-unavailable || { invalid_record 'tool_status must be tool-unavailable' || return 1; }
}

snapshot_digest() {
    record=$1
    temporary=$(mktemp "${TMPDIR:-/tmp}/pkg-mgr-snapshot-content.XXXXXX") || return 1
    if ! sed '/^snapshot_hash=/d' "$record" > "$temporary"; then
        rm -f "$temporary"
        return 1
    fi
    if digest=$(sha256_file "$temporary"); then
        rm -f "$temporary"
        printf '%s\n' "$digest"
        return 0
    else
        status=$?
        rm -f "$temporary"
        return "$status"
    fi
}

validate_index() {
    index=$1
    rows=$(mktemp "${TMPDIR:-/tmp}/pkg-mgr-index-rows.XXXXXX") || return 1
    sorted=$(mktemp "${TMPDIR:-/tmp}/pkg-mgr-index-sorted.XXXXXX") || {
        rm -f "$rows"
        return 1
    }
    expected_header=$(printf 'namespace\tpackage_name\tversion\trecipe_path\trecipe_revision\tsource_hash\tsource_size\tmanifest_hash')
    actual_header=$(sed -n '1p' "$index")
    if test "$actual_header" != "$expected_header"; then
        diagnose 'index header does not match the Phase 2 eight-field schema'
        rm -f "$rows" "$sorted"
        return 1
    fi
    if ! awk -F '\t' '
        NR == 1 { next }
        {
            if (NF != 8) {
                print "index row must have exactly eight nonempty columns" > "/dev/stderr"
                exit 1
            }
            for (i = 1; i <= 8; i++) {
                if ($i == "") {
                    print "index row must have exactly eight nonempty columns" > "/dev/stderr"
                    exit 1
                }
            }
            source_hash = $6
            sub(/^sha256:/, "", source_hash)
            if ($6 !~ /^sha256:/ || length(source_hash) != 64 || source_hash ~ /[^0123456789abcdef]/) {
                print "index source_hash must be sha256 with 64 lowercase hexadecimal characters" > "/dev/stderr"
                exit 1
            }
            if ($7 !~ /^[0-9]+$/ || ($7 != "0" && $7 ~ /^0/)) {
                print "index source_size must be decimal bytes" > "/dev/stderr"
                exit 1
            }
            manifest_hash = $8
            sub(/^sha256:/, "", manifest_hash)
            if ($8 !~ /^sha256:/ || length(manifest_hash) != 64 || manifest_hash ~ /[^0123456789abcdef]/) {
                print "index manifest_hash must be sha256 with 64 lowercase hexadecimal characters" > "/dev/stderr"
                exit 1
            }
            print
            count++
        }
        END {
            if (count == 0) {
                print "index must contain at least one package row" > "/dev/stderr"
                exit 1
            }
        }
    ' "$index" > "$rows"; then
        rm -f "$rows" "$sorted"
        return 1
    fi
    tab=$(printf '\t')
    if ! LC_ALL=C sort -t "$tab" -k1,1 -k2,2 -k3,3 -k4,4 -k5,5 "$rows" > "$sorted"; then
        diagnose 'could not sort index rows'
        rm -f "$rows" "$sorted"
        return 1
    fi
    if ! cmp -s "$rows" "$sorted"; then
        diagnose 'index rows are not C-locale sorted'
        rm -f "$rows" "$sorted"
        return 1
    fi
    rm -f "$rows" "$sorted"
}

verify_snapshot() {
    test "$#" -eq 4 || {
        fail_result usage-error verify-snapshot 'usage: verify-snapshot <snapshot.kv> <index.tsv> <signature> <public-key>'
        return
    }
    snapshot=$1
    index=$2
    signature=$3
    public_key=$4

    test -f "$snapshot" && test -r "$snapshot" || {
        fail_result snapshot-metadata-invalid "$snapshot" 'snapshot metadata is not a readable file'
        return
    }
    if ! parse_snapshot_record "$snapshot"; then
        emit_result fail snapshot-metadata-invalid "$snapshot"
        return 1
    fi
    test -f "$index" && test -r "$index" || {
        fail_result index-metadata-invalid "$index" 'index is not a readable file'
        return
    }
    if ! actual_snapshot_hash=$(snapshot_digest "$snapshot"); then
        fail_result snapshot-hash-unavailable "$snapshot" 'could not calculate snapshot self-hash'
        return
    fi
    if test "sha256:$actual_snapshot_hash" != "$snapshot_hash"; then
        fail_result snapshot-hash-mismatch "$snapshot" 'snapshot self-hash mismatch'
        return
    fi

    if ! validate_index "$index"; then
        emit_result fail index-metadata-invalid "$index"
        return 1
    fi
    if ! actual_index_hash=$(sha256_file "$index"); then
        fail_result index-hash-unavailable "$index" 'could not calculate index SHA-256'
        return
    fi
    if test "sha256:$actual_index_hash" != "$index_hash"; then
        fail_result mix-and-match "$index" 'index SHA-256 does not match snapshot'
        return
    fi

    minisign_command=${MINISIGN-minisign}
    case $minisign_command in
        ''|-*|*[!ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._+-]*)
            fail_result signer-command-invalid "$snapshot" 'MINISIGN must be one command name without arguments'
            return
            ;;
    esac
    if ! command -v "$minisign_command" >/dev/null 2>&1; then
        diagnose 'optional minisign command is unavailable; required snapshot/index checks passed'
        emit_result tool-unavailable minisign-unavailable "$snapshot"
        return 0
    fi
    test -f "$signature" && test -r "$signature" || {
        fail_result missing-signature "$signature" 'signature is not a readable file'
        return
    }
    test -f "$public_key" && test -r "$public_key" || {
        fail_result missing-public-key "$public_key" 'public key is not a readable file'
        return
    }
    if ! "$minisign_command" -V -q -p "$public_key" -m "$snapshot" -x "$signature" >/dev/null 2>&1; then
        fail_result bad-signature "$snapshot" 'minisign rejected the snapshot signature'
        return
    fi

    diagnose 'configured fixture key signed the exact snapshot bytes; authenticity and governance remain unproven'
    emit_result warn signature-not-sufficient "$snapshot"
}

verify_source() {
    test "$#" -eq 2 || {
        fail_result usage-error verify-source 'usage: verify-source <record.kv> <target-file>'
        return
    }
    record=$1
    target=$2

    test -f "$record" && test -r "$record" || {
        fail_result source-metadata-invalid "$record" 'metadata record is not a readable file'
        return
    }
    if ! parse_source_record "$record"; then
        emit_result fail source-metadata-invalid "$record"
        return 1
    fi
    test -f "$target" && test -r "$target" || {
        fail_result missing-target "$target" 'target is not a readable file'
        return
    }

    if ! actual_size=$(byte_count "$target"); then
        fail_result source-size-unavailable "$target" 'could not determine target byte size'
        return
    fi
    if test "$actual_size" != "$source_size"; then
        fail_result source-size-mismatch "$target" "size mismatch: expected $source_size bytes, got $actual_size"
        return
    fi

    if ! actual_hash=$(sha256_file "$target"); then
        fail_result source-hash-tool-unavailable "$target" 'no working SHA-256 tool is available'
        return
    fi
    if test "$actual_hash" != "$source_hash"; then
        fail_result source-hash-mismatch "$target" "SHA-256 mismatch: expected $source_hash, got $actual_hash"
        return
    fi

    emit_result pass source-bytes-match "$target"
}

make_adjacent_temporary() {
    destination=$1
    destination_dir=$(dirname "$destination")
    destination_base=$(basename "$destination")
    test -d "$destination_dir" && test -w "$destination_dir" || return 1
    mktemp "$destination_dir/.$destination_base.tmp.XXXXXX"
}

manifest_rows() {
    stage=$1
    rows=$2
    failure=$3
    shift 3
    tab=$(printf '\t')
    newline='
'

    for file do
        relative=${file#"$stage"/}
        case $relative in
            ''|"$file"|*"$tab"*|*"$newline"*)
                diagnose 'staged path contains a tab or newline and cannot be represented'
                printf '%s\n' manifest-path-invalid > "$failure"
                return 1
                ;;
        esac
        if ! digest=$(sha256_file "$file"); then
            diagnose "could not hash staged file: $relative"
            printf '%s\n' manifest-hash-unavailable > "$failure"
            return 1
        fi
        if ! size=$(byte_count "$file"); then
            diagnose "could not determine staged file size: $relative"
            printf '%s\n' manifest-size-unavailable > "$failure"
            return 1
        fi
        if ! printf '%s\t%s\t%s\n' "$digest" "$size" "$relative" >> "$rows"; then
            diagnose 'could not write temporary manifest row'
            printf '%s\n' manifest-write-failed > "$failure"
            return 1
        fi
    done
}

generate_manifest() {
    test "$#" -eq 2 || {
        fail_result usage-error manifest 'usage: manifest <stage-dir> <output.tsv>'
        return
    }
    stage=${1%/}
    output=$2
    test -n "$stage" || stage=/

    if ! test -d "$stage" || ! test -r "$stage" || test -L "$stage"; then
        fail_result manifest-input-invalid "$stage" 'stage directory is not readable'
        return
    fi
    if ! temporary_output=$(make_adjacent_temporary "$output"); then
        fail_result manifest-output-invalid "$output" 'manifest destination directory is not writable'
        return
    fi
    rows=$temporary_output.rows
    sorted=$temporary_output.sorted
    failure=$temporary_output.failure
    : > "$rows"
    rm -f "$failure"

    if ! find "$stage" -type f -exec sh "$script_path" _manifest-rows "$stage" "$rows" "$failure" {} + && ! test -s "$failure"; then
        diagnose 'could not traverse stage directory'
        printf '%s\n' manifest-traversal-failed > "$failure"
    fi
    if test -s "$failure"; then
        label=$(sed -n '1p' "$failure")
        rm -f "$rows" "$sorted" "$failure" "$temporary_output"
        temporary_output=
        emit_result fail "$label" "$stage"
        return 1
    fi
    tab=$(printf '\t')
    if ! LC_ALL=C sort -t "$tab" -k3,3 "$rows" > "$sorted"; then
        rm -f "$rows" "$sorted" "$failure" "$temporary_output"
        temporary_output=
        fail_result manifest-sort-failed "$stage" 'could not C-sort temporary manifest'
        return
    fi
    if ! awk -F '\t' '
        NF != 3 || length($1) != 64 || $1 ~ /[^0123456789abcdef]/ ||
        $2 !~ /^[0-9]+$/ || $3 == "" { exit 1 }
    ' "$sorted"; then
        rm -f "$rows" "$sorted" "$failure" "$temporary_output"
        temporary_output=
        fail_result manifest-validation-failed "$stage" 'generated manifest row failed validation'
        return
    fi
    if ! mv "$sorted" "$temporary_output" || ! mv "$temporary_output" "$output"; then
        rm -f "$rows" "$sorted" "$failure" "$temporary_output"
        temporary_output=
        fail_result manifest-output-invalid "$output" 'could not atomically publish manifest'
        return
    fi
    rm -f "$rows" "$failure"
    temporary_output=
    emit_result pass package-manifest-created "$output"
}

parse_build_record() {
    record=$1

    record_type=
    repo_origin=
    namespace=
    package_name=
    version=
    recipe_path=
    recipe_revision=
    source_hash_alg=
    source_hash=
    manifest_ref=
    materials_ref=
    material_path=
    sbom_ref=
    builder_label=
    phase_label=
    command_label=
    provenance_confidence=
    verification_result=
    result_label=
    seen_record_type=false seen_repo_origin=false seen_namespace=false seen_package_name=false
    seen_version=false seen_recipe_path=false seen_recipe_revision=false seen_source_hash_alg=false
    seen_source_hash=false seen_manifest_ref=false seen_materials_ref=false seen_material_path=false
    seen_sbom_ref=false seen_builder_label=false seen_phase_label=false seen_command_label=false
    seen_provenance_confidence=false seen_verification_result=false seen_result_label=false

    while IFS= read -r line || test -n "$line"; do
        case $line in
            *=*) key=${line%%=*}; value=${line#*=} ;;
            *) invalid_record 'malformed build metadata line' || return 1 ;;
        esac
        test -n "$key" || { invalid_record 'malformed build metadata line' || return 1; }
        test -n "$value" || { invalid_record "empty value for key: $key" || return 1; }
        case $key in
            record_type) seen=$seen_record_type ;;
            repo_origin) seen=$seen_repo_origin ;;
            namespace) seen=$seen_namespace ;;
            package_name) seen=$seen_package_name ;;
            version) seen=$seen_version ;;
            recipe_path) seen=$seen_recipe_path ;;
            recipe_revision) seen=$seen_recipe_revision ;;
            source_hash_alg) seen=$seen_source_hash_alg ;;
            source_hash) seen=$seen_source_hash ;;
            manifest_ref) seen=$seen_manifest_ref ;;
            materials_ref) seen=$seen_materials_ref ;;
            material_path) seen=$seen_material_path ;;
            sbom_ref) seen=$seen_sbom_ref ;;
            builder_label) seen=$seen_builder_label ;;
            phase_label) seen=$seen_phase_label ;;
            command_label) seen=$seen_command_label ;;
            provenance_confidence) seen=$seen_provenance_confidence ;;
            verification_result) seen=$seen_verification_result ;;
            result_label) seen=$seen_result_label ;;
            *) invalid_record "unknown key: $key" || return 1 ;;
        esac
        test "$seen" = false || { invalid_record "duplicate key: $key" || return 1; }
        case $key in
            record_type) record_type=$value; seen_record_type=true ;;
            repo_origin) repo_origin=$value; seen_repo_origin=true ;;
            namespace) namespace=$value; seen_namespace=true ;;
            package_name) package_name=$value; seen_package_name=true ;;
            version) version=$value; seen_version=true ;;
            recipe_path) recipe_path=$value; seen_recipe_path=true ;;
            recipe_revision) recipe_revision=$value; seen_recipe_revision=true ;;
            source_hash_alg) source_hash_alg=$value; seen_source_hash_alg=true ;;
            source_hash) source_hash=$value; seen_source_hash=true ;;
            manifest_ref) manifest_ref=$value; seen_manifest_ref=true ;;
            materials_ref) materials_ref=$value; seen_materials_ref=true ;;
            material_path) material_path=$value; seen_material_path=true ;;
            sbom_ref) sbom_ref=$value; seen_sbom_ref=true ;;
            builder_label) builder_label=$value; seen_builder_label=true ;;
            phase_label) phase_label=$value; seen_phase_label=true ;;
            command_label) command_label=$value; seen_command_label=true ;;
            provenance_confidence) provenance_confidence=$value; seen_provenance_confidence=true ;;
            verification_result) verification_result=$value; seen_verification_result=true ;;
            result_label) result_label=$value; seen_result_label=true ;;
        esac
    done < "$record"

    for required in record_type repo_origin namespace package_name version recipe_path recipe_revision \
        source_hash_alg source_hash manifest_ref materials_ref material_path sbom_ref builder_label \
        phase_label command_label provenance_confidence verification_result result_label
    do
        case $required in
            record_type) seen=$seen_record_type ;; repo_origin) seen=$seen_repo_origin ;;
            namespace) seen=$seen_namespace ;; package_name) seen=$seen_package_name ;;
            version) seen=$seen_version ;; recipe_path) seen=$seen_recipe_path ;;
            recipe_revision) seen=$seen_recipe_revision ;; source_hash_alg) seen=$seen_source_hash_alg ;;
            source_hash) seen=$seen_source_hash ;; manifest_ref) seen=$seen_manifest_ref ;;
            materials_ref) seen=$seen_materials_ref ;; material_path) seen=$seen_material_path ;;
            sbom_ref) seen=$seen_sbom_ref ;; builder_label) seen=$seen_builder_label ;;
            phase_label) seen=$seen_phase_label ;; command_label) seen=$seen_command_label ;;
            provenance_confidence) seen=$seen_provenance_confidence ;;
            verification_result) seen=$seen_verification_result ;; result_label) seen=$seen_result_label ;;
        esac
        test "$seen" = true || { invalid_record "missing required key: $required" || return 1; }
    done
}

validate_build_values() {
    test "$record_type" = build || { diagnose 'record_type must be build'; return 1; }
    test "$source_hash_alg" = sha256 || { diagnose 'source_hash_alg must be sha256'; return 1; }
    is_sha256 "$source_hash" || { diagnose 'source_hash must be raw 64-character lowercase hexadecimal'; return 1; }
    test "$provenance_confidence" = advisory || { diagnose 'provenance_confidence must be advisory'; return 1; }
    test "$verification_result" = warn || { diagnose 'verification_result must be warn'; return 1; }
    test "$result_label" = reproducible-build-success-not-proven || {
        diagnose 'result_label must be reproducible-build-success-not-proven'
        return 1
    }
}

repo_relative_file() {
    reference=$1
    kind=$2
    tab=$(printf '\t')
    newline='
'
    case $reference in
        ''|.|..|/*|*"$tab"*|*"$newline"*|*//*|./*|../*|*/./*|*/../*|*/.|*/..)
            diagnose "$kind uses an unsafe repository-relative path: $reference"
            return 1
            ;;
    esac
    parent_ref=$(dirname "$reference")
    base_ref=$(basename "$reference")
    if ! parent=$(CDPATH='' cd "$repo_root/$parent_ref" 2>/dev/null && pwd -P); then
        diagnose "$kind parent does not exist: $reference"
        return 1
    fi
    case $parent in
        "$repo_root"|"$repo_root"/*) ;;
        *) diagnose "$kind parent escapes repository root: $reference"; return 1 ;;
    esac
    resolved=$parent/$base_ref
    if test -L "$resolved"; then
        diagnose "$kind must not be a final symlink: $reference"
        return 1
    fi
    if ! test -f "$resolved" || ! test -r "$resolved"; then
        diagnose "$kind is not a readable regular file: $reference"
        return 1
    fi
    printf '%s\n' "$resolved"
}

generate_build_record() {
    test "$#" -eq 2 || {
        fail_result usage-error build-record 'usage: build-record <input.kv> <output.kv>'
        return
    }
    input=$1
    output=$2
    test -f "$input" && test -r "$input" || {
        fail_result build-record-invalid "$input" 'build input is not a readable file'
        return
    }
    if ! parse_build_record "$input"; then
        emit_result fail build-record-invalid "$input"
        return 1
    fi
    if ! validate_build_values; then
        emit_result fail material-reference-invalid "$input"
        return 1
    fi

    if ! source_record=$(repo_relative_file "$materials_ref" 'materials_ref'); then
        emit_result fail material-reference-invalid "$input"
        return 1
    fi
    if ! material_file=$(repo_relative_file "$material_path" 'material_path'); then
        emit_result fail material-reference-invalid "$input"
        return 1
    fi
    if ! manifest_file=$(repo_relative_file "$manifest_ref" 'manifest_ref'); then
        emit_result fail material-reference-invalid "$input"
        return 1
    fi
    if ! repo_relative_file "$sbom_ref" 'sbom_ref' >/dev/null; then
        emit_result fail material-reference-invalid "$input"
        return 1
    fi

    build_record_type=$record_type
    build_source_hash_alg=$source_hash_alg
    build_source_hash=$source_hash
    build_verification_result=$verification_result
    build_result_label=$result_label
    if ! parse_source_record "$source_record"; then
        diagnose 'source metadata record is invalid'
        emit_result fail material-reference-invalid "$input"
        return 1
    fi
    case $source_uri in
        file:*) source_uri_path=${source_uri#file:} ;;
        *)
            diagnose 'source_uri must be canonical local file reference'
            emit_result fail material-reference-invalid "$input"
            return 1
            ;;
    esac
    if test "$source_uri_path" != "$material_path"; then
        diagnose 'material reference does not match source_uri'
        emit_result fail material-reference-invalid "$input"
        return 1
    fi
    if test "$source_hash_alg" != "$build_source_hash_alg"; then
        diagnose 'source_hash_alg does not match build input'
        emit_result fail material-reference-invalid "$input"
        return 1
    fi
    if test "$source_hash" != "$build_source_hash"; then
        diagnose 'source_hash does not match build input'
        emit_result fail material-reference-invalid "$input"
        return 1
    fi
    if ! actual_size=$(byte_count "$material_file") || test "$actual_size" != "$source_size"; then
        diagnose 'material size does not match source metadata'
        emit_result fail material-reference-invalid "$input"
        return 1
    fi
    if ! actual_source_hash=$(sha256_file "$material_file") || test "$actual_source_hash" != "$source_hash"; then
        diagnose 'material SHA-256 does not match source metadata'
        emit_result fail material-reference-invalid "$input"
        return 1
    fi
    if ! actual_manifest_hash=$(sha256_file "$manifest_file"); then
        diagnose 'could not hash package manifest'
        emit_result fail material-reference-invalid "$input"
        return 1
    fi

    if ! temporary_output=$(make_adjacent_temporary "$output"); then
        fail_result build-record-output-invalid "$output" 'build-record destination directory is not writable'
        return
    fi
    if ! printf '%s\n' \
        "record_type=$build_record_type" \
        "repo_origin=$repo_origin" \
        "namespace=$namespace" \
        "package_name=$package_name" \
        "version=$version" \
        "recipe_path=$recipe_path" \
        "recipe_revision=$recipe_revision" \
        "source_hash_alg=$build_source_hash_alg" \
        "source_hash=$build_source_hash" \
        "manifest_hash=sha256:$actual_manifest_hash" \
        "materials_ref=$materials_ref" \
        "material_path=$material_path" \
        "sbom_ref=$sbom_ref" \
        "builder_label=$builder_label" \
        "phase_label=$phase_label" \
        "command_label=$command_label" \
        "provenance_confidence=$provenance_confidence" \
        "verification_result=$build_verification_result" \
        "result_label=$build_result_label" > "$temporary_output"; then
        fail_result build-record-output-invalid "$output" 'could not write temporary build record'
        return
    fi
    if ! mv "$temporary_output" "$output"; then
        fail_result build-record-output-invalid "$output" 'could not atomically publish build record'
        return
    fi
    temporary_output=
    emit_result warn reproducible-build-success-not-proven "$output"
}

validate_sbom() {
    awk '
        function bad(message) { print message > "/dev/stderr"; exit 1 }
        function remember(name, value) {
            if (seen[name]++) bad("duplicate field: " name)
            field[name] = value
        }
        /^[[:space:]]*$/ { next }
        {
            separator = index($0, ": ")
            if (!separator) bad("malformed SPDX tag-value line")
            name = substr($0, 1, separator - 1)
            value = substr($0, separator + 2)
            if (value == "") bad("empty SPDX field: " name)
            if (name == "SPDXID") {
                if (!seen["SPDXID.document"]) remember("SPDXID.document", value)
                else remember("SPDXID.package", value)
            } else if (name == "SPDXVersion" || name == "DataLicense" || name == "DocumentName" ||
                       name == "DocumentNamespace" || name == "Creator" || name == "Created" ||
                       name == "PackageName" || name == "PackageVersion" || name == "PackageDownloadLocation" ||
                       name == "FilesAnalyzed" || name == "PackageChecksum" ||
                       name == "PackageLicenseConcluded" || name == "PackageLicenseDeclared" ||
                       name == "PackageCopyrightText" || name == "Relationship") {
                remember(name, value)
            } else bad("unknown field: " name)
        }
        END {
            required[1]="SPDXVersion"; required[2]="DataLicense"; required[3]="SPDXID.document"
            required[4]="DocumentName"; required[5]="DocumentNamespace"; required[6]="Creator"
            required[7]="Created"; required[8]="PackageName"; required[9]="SPDXID.package"
            required[10]="PackageVersion"; required[11]="PackageDownloadLocation"; required[12]="FilesAnalyzed"
            required[13]="PackageChecksum"; required[14]="PackageLicenseConcluded"
            required[15]="PackageLicenseDeclared"; required[16]="PackageCopyrightText"; required[17]="Relationship"
            for (i=1; i<=17; i++) if (!seen[required[i]]) bad("missing required field: " required[i])
            if (field["SPDXVersion"] != "SPDX-2.3") bad("SPDXVersion must be SPDX-2.3")
            if (field["DataLicense"] != "CC0-1.0") bad("DataLicense must be CC0-1.0")
            if (field["SPDXID.document"] != "SPDXRef-DOCUMENT") bad("document SPDXID must be SPDXRef-DOCUMENT")
            if (field["SPDXID.package"] !~ /^SPDXRef-/ || field["SPDXID.package"] == field["SPDXID.document"])
                bad("package SPDXID must be distinct and start with SPDXRef-")
            namespace=field["DocumentNamespace"]
            if (namespace !~ /^[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz][ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+.-]*:/ ||
                namespace ~ /#/ || namespace ~ /[[:space:]]/)
                bad("DocumentNamespace must be an absolute URI without a fragment")
            if (field["Creator"] !~ /^(Person|Organization|Tool): /) bad("Creator must identify a Person, Organization, or Tool")
            created=field["Created"]
            if (length(created) != 20 || substr(created,5,1) != "-" || substr(created,8,1) != "-" ||
                substr(created,11,1) != "T" || substr(created,14,1) != ":" || substr(created,17,1) != ":" ||
                substr(created,20,1) != "Z" || created ~ /[^0-9TZ:-]/)
                bad("Created must use UTC syntax YYYY-MM-DDThh:mm:ssZ")
            if (field["PackageDownloadLocation"] != "NOASSERTION") bad("PackageDownloadLocation must be NOASSERTION")
            if (field["FilesAnalyzed"] != "false") bad("FilesAnalyzed must be false")
            checksum=field["PackageChecksum"]
            digest=checksum; sub(/^SHA256: /, "", digest)
            if (checksum !~ /^SHA256: / || length(digest) != 64 || digest ~ /[^0123456789abcdef]/)
                bad("PackageChecksum must be SHA256 with 64 lowercase hexadecimal characters")
            if (field["PackageLicenseConcluded"] != "NOASSERTION" || field["PackageLicenseDeclared"] != "NOASSERTION" ||
                field["PackageCopyrightText"] != "NOASSERTION") bad("license and copyright fields must be NOASSERTION")
            expected="SPDXRef-DOCUMENT DESCRIBES " field["SPDXID.package"]
            if (field["Relationship"] != expected) bad("Relationship must describe the package SPDXID")
        }
    ' "$1"
}

check_sbom() {
    test "$#" -eq 1 || {
        fail_result usage-error check-sbom 'usage: check-sbom <advisory.spdx>'
        return
    }
    sbom=$1
    test -f "$sbom" && test -r "$sbom" || {
        fail_result sbom-record-invalid "$sbom" 'SPDX advisory is not a readable file'
        return
    }
    if ! validate_sbom "$sbom"; then
        emit_result fail sbom-record-invalid "$sbom"
        return 1
    fi
    emit_result warn sbom-completeness-not-proven "$sbom"
}

case ${1-} in
    hash-file)
        test "$#" -eq 2 || exit 64
        test -f "$2" && ! test -L "$2" && test -r "$2" || {
            diagnose 'hash-file requires a readable regular file'
            exit 1
        }
        sha256_file "$2"
        ;;
    verify-source)
        shift
        verify_source "$@"
        ;;
    verify-snapshot)
        shift
        verify_snapshot "$@"
        ;;
    manifest)
        shift
        generate_manifest "$@"
        ;;
    build-record)
        shift
        generate_build_record "$@"
        ;;
    check-sbom)
        shift
        check_sbom "$@"
        ;;
    _manifest-rows)
        shift
        manifest_rows "$@"
        ;;
    *)
        fail_result usage-error "${1-verify-metadata}" 'usage: verify-metadata.sh hash-file FILE | verify-source ... | verify-snapshot ... | manifest ... | build-record ... | check-sbom ...'
        ;;
esac
