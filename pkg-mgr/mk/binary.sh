#!/bin/sh
# Local regular-file binary transport. No remote trust policy or live-prefix writes.
set -eu
LC_ALL=C
export LC_ALL
repo=$(CDPATH='' cd "$(dirname "$0")/.." && pwd -P)
verifier=$repo/mk/verify-metadata.sh
state_tool=$repo/mk/state.sh
fail() { printf 'binary-error: %s\n' "$*" >&2; exit 1; }
id() { case $1 in ''|[!A-Za-z0-9]*|*[!A-Za-z0-9._+-]*) return 1 ;; esac; }
is_hash() { case $1 in ''|*[!0-9a-f]*) return 1 ;; esac; test "${#1}" -eq 64; }
regular() { if ! { test -f "$1" && test -r "$1" && ! test -L "$1"; }; then fail 'expected readable regular file'; fi; }
# cmp distinguishes ordinary differences (1) from tool/read errors (>1).
same_record() {
    if cmp -s "$1" "$2"; then return 0
    else comparison_status=$?
    fi
    test "$comparison_status" -eq 1 || fail 'cannot compare package records'
    return 1
}
hash() { sh "$verifier" hash-file "$1"; }
field() {
    KEY=$2 awk 'BEGIN{k=ENVIRON["KEY"]} index($0,k "=")==1 {n++; v=substr($0,length(k)+2)} END {if(n!=1 || v=="") exit 1; print v}' "$1"
}
test "$#" -ge 3 || fail 'usage: binary.sh export ROOT NAME | import/recover/preflight ROOT BUNDLE DESCRIPTOR-SHA256 EXPECTED-COMPILER-TARGET'
command=$1; ROOT=$2; export ROOT; shift 2
sdk=no
expected_profile=
case $command in
    sdk-export)
        test "$#" -eq 2 && test "$1" = aether-musl-sdk && is_hash "$2" || exit 64
        sdk=yes; command='export'; expected_profile=$2; name=$1 ;;
    sdk-import|sdk-recover)
        test "$#" -eq 3 && is_hash "$2" && is_hash "$3" || exit 64
        sdk=yes; command=${command#sdk-}; expected_profile=$3 ;;
    export) test "$#" -eq 1 && id "$1" || exit 64; name=$1 ;;
    import|recover|preflight) test "$#" -eq 3 && is_hash "$2" && id "$3" || exit 64 ;;
    *) exit 64 ;;
esac
sh "$repo/mk/check-root.sh" state
# Validate existing authority and payload before attempting any mutation.
if test "$command" = preflight; then
    # Authority must be valid, but payload drift is reportable rather than fatal.
    sh "$state_tool" list "$ROOT" > /dev/null
    scratch=$(mktemp -d "${TMPDIR:-/tmp}/pkg-mgr-preflight.XXXXXX")
else
    sh "$state_tool" verify "$ROOT" > /dev/null
    scratch=$(mktemp -d "$ROOT/.binary-work.XXXXXX")
fi
new_stage=
cleanup() {
    # Roll back only a stage newly published by this invocation, and never one
    # whose record has committed. A crash can leave an unregistered stage.
    if test -n "$new_stage" && ! test -e "$ROOT/state/packages/$name.tsv"; then rm -rf "$new_stage"; fi
    rm -rf "$scratch"
}
trap cleanup 0
trap 'exit 1' HUP INT TERM
if test "$sdk" = yes; then trap 'exit 1' PIPE; fi

target_record() {
    printf 'format=host-binary-target-v1\nhost_os=%s\nhost_arch=%s\ncompiler_target=%s\n' "$1" "$2" "$3"
    printf 'modes=recorded-0000-0777\n'
}
descriptor() {
    record_digest=$(hash "$1/package.tsv") || return "$?"
    target_digest=$(hash "$1/target.kv") || return "$?"
    modes_digest=$(hash "$1/modes.tsv") || return "$?"
    dependencies_digest=$(hash "$1/dependencies.tsv") || return "$?"
    transport_format=local-binary-directory-v2
    if test "$sdk" = yes; then transport_format=local-sdk-directory-v1; fi
    printf 'format=%s\nrecord_sha256=%s\ntarget_sha256=%s\nmodes_sha256=%s\ndependencies_sha256=%s\n' \
        "$transport_format" "$record_digest" "$target_digest" "$modes_digest" "$dependencies_digest"
    printf 'authenticity=not-proven\nservice_activation=unsupported\n'
}
# Reconstruct the existing evidence formats; state.sh checks their binding and
# dependency/ownership rules in a private candidate root before any publication.
extract_record() {
    awk -F '\t' '$1=="file" {print $2 "\t" $3 "\t" $4}' "$1" > "$scratch/manifest.tsv"
    awk -F '\t' '$1=="evidence" {print $2 "=" $3}' "$1" > "$scratch/build.kv"
    awk -F '\t' '$1=="dependency" {print $2}' "$1" > "$scratch/deps"
}

# This profile is explicit build-input transport, never inferred from host data.
sdk_identity() {
    test "$name" = aether-musl-sdk || fail 'unsupported SDK package name'
    awk -F '\t' '$1=="dependency" {bad=1} END {exit bad}' "$record" || fail 'SDK dependencies unsupported'
    sdk_metadata=$stage/usr/local/share/pkg-mgr/$name
    for sdk_file in sdk-target.kv sdk-build-receipt sdk-native-profile; do
        SDK_PATH="usr/local/share/pkg-mgr/$name/$sdk_file" awk -F '\t' '
            $1=="file" && $4==ENVIRON["SDK_PATH"] {found=1} END {exit !found}
        ' "$record" || fail 'SDK identity is not manifest-bound'
    done
    sh "$repo/mk/sdk-profile.sh" "$sdk_metadata/sdk-target.kv" "$expected_profile" \
        "$sdk_metadata/sdk-build-receipt" "$sdk_metadata/sdk-native-profile" || fail 'invalid SDK profile'
}

if test "$command" = export; then
    record=$ROOT/state/packages/$name.tsv
    regular "$record"
    stage=$ROOT/stage/$name
    if test "$sdk" = yes; then
        sdk_identity
    else
        host=$stage/usr/local/share/pkg-mgr/$name/host.kv
        regular "$host"
        # Only the current host recipes, with a manifest-bound observation, are supported.
        sh "$state_tool" files "$ROOT" "$name" > "$scratch/file-view"
        HOST_PATH="usr/local/share/pkg-mgr/$name/host.kv" awk -F '\t' '$1==ENVIRON["HOST_PATH"]{found=1} END{exit !found}' "$scratch/file-view"
        os=$(field "$host" host_os); arch=$(field "$host" host_arch); triple=$(field "$host" compiler_target)
        if ! { id "$os" && id "$arch" && id "$triple"; }; then fail 'invalid host identity'; fi
        runtime=$(field "$host" target_runtime)
        test "$runtime" = host-only || fail 'unsupported runtime'
    fi
    bundle=$scratch/bundle
    mkdir "$bundle" "$bundle/files"
    cp "$record" "$bundle/package.tsv"
    if test "$sdk" = yes; then
        cp "$sdk_metadata/sdk-target.kv" "$bundle/target.kv"
    else
        target_record "$os" "$arch" "$triple" > "$bundle/target.kv"
    fi
    extract_record "$record"
    : > "$bundle/modes.tsv"
    tab=$(printf '\t')
    while IFS="$tab" read -r digest _size path; do
        cp "$stage/$path" "$bundle/files/$digest"
        chmod 0644 "$bundle/files/$digest"
        mode=$(sh "$repo/mk/file-mode.sh" "$stage/$path")
        printf '%s\t%s\n' "$mode" "$path" >> "$bundle/modes.tsv"
        test "$(hash "$bundle/files/$digest")" = "$digest" || fail 'payload changed during export'
    done < "$scratch/manifest.tsv"
    : > "$bundle/dependencies.tsv"
    while IFS= read -r dependency; do
        digest=$(hash "$ROOT/state/packages/$dependency.tsv")
        observed_dependency=$(field "$host" "dependency_${dependency}_record_sha256")
        test "$observed_dependency" = "$digest" || fail 'dependency differs from build observation'
        printf '%s\t%s\n' "$dependency" "$digest" >> "$bundle/dependencies.tsv"
    done < "$scratch/deps"
    descriptor "$bundle" > "$bundle/artifact.kv"
    # Calculate the receipt pin while the bundle is still private.
    bundle_digest=$(hash "$bundle/artifact.kv")
    if test -e "$ROOT/binaries" || test -L "$ROOT/binaries"; then
        if ! { test -d "$ROOT/binaries" && ! test -L "$ROOT/binaries"; }; then fail 'invalid binary output directory'; fi
    else mkdir "$ROOT/binaries"
    fi
    destination=$ROOT/binaries/$name
    if ! { test ! -e "$destination" && ! test -L "$destination"; }; then fail 'binary already exists'; fi
    mv "$bundle" "$destination"
    if test "$sdk" = yes; then
        printf 'sdk-exported\t%s\t%s\n' "$name" "$bundle_digest" || exit 1
    else
        printf 'exported\t%s\t%s\n' "$name" "$bundle_digest"
    fi
    exit
fi

bundle=$1; expected_digest=$2; expected_target=$3
case $bundle in /*) ;; *) fail 'bundle path must be absolute' ;; esac
if ! { test -d "$bundle" && ! test -L "$bundle"; }; then fail 'invalid bundle directory'; fi
# Reject unsupported entries before reading content. No generic archive extractor.
bad=$(find "$bundle" \( ! -type d ! -type f \) -print -o \( -type f -links +1 \) -print)
test -z "$bad" || fail 'bundle contains links or special files'
for entry in "$bundle"/* "$bundle"/.[!.]* "$bundle"/..?*; do
    test -e "$entry" || continue
    case ${entry##*/} in artifact.kv|package.tsv|target.kv|modes.tsv|dependencies.tsv|files) ;; *) fail 'unknown bundle entry' ;; esac
done
for file in artifact.kv package.tsv target.kv modes.tsv dependencies.tsv; do regular "$bundle/$file"; done
if ! { test -d "$bundle/files" && ! test -L "$bundle/files"; }; then fail 'missing blob directory'; fi
test "$(hash "$bundle/artifact.kv")" = "$expected_digest" || fail 'descriptor pin mismatch'
descriptor "$bundle" > "$scratch/descriptor"
cmp -s "$scratch/descriptor" "$bundle/artifact.kv" || fail 'descriptor/content mismatch'
if test "$sdk" = yes; then
    observed_profile=$(hash "$bundle/target.kv") || fail 'cannot hash SDK profile'
    test "$observed_profile" = "$expected_profile" || fail 'SDK profile pin mismatch'
else
    os=$(uname -s); arch=$(uname -m)
    target_record "$os" "$arch" "$expected_target" > "$scratch/target"
    cmp -s "$scratch/target" "$bundle/target.kv" || fail 'incompatible host/target'
fi
name=$(awk -F '\t' 'NR==2 {print $2}' "$bundle/package.tsv")
id "$name" || fail 'invalid package name'
awk -v mode=record -v expected="$name" -f "$repo/mk/state-schema.awk" "$bundle/package.tsv"
record_format=$(sed -n '1p' "$bundle/package.tsv")
test "$record_format" = "$(printf 'format\tpkg-state-v2')" || fail 'binary import requires permission-tracked v2 records'
extract_record "$bundle/package.tsv"
if test "$sdk" = yes; then
    test "$name" = aether-musl-sdk || fail 'unsupported SDK package name'
    test ! -s "$scratch/deps" && test ! -s "$bundle/dependencies.tsv" || fail 'SDK dependencies unsupported'
fi
# Modes/dependency rows must match record order exactly; no extra path or owner.
awk -F '\t' '$1=="file" {print $5 "\t" $4}' "$bundle/package.tsv" > "$scratch/record-modes"
cmp -s "$scratch/record-modes" "$bundle/modes.tsv" || fail 'mode table differs from package record'
awk -F '\t' 'FILENAME==ARGV[1] {names[++n]=$0; next} {i++; if(NF!=2 || $1!=names[i] || length($2)!=64 || $2~/[^0-9a-f]/) bad=1} END{exit (bad || i!=n)}' "$scratch/deps" "$bundle/dependencies.tsv" || fail 'invalid dependency table'
tab=$(printf '\t')
while IFS="$tab" read -r dependency digest; do
    regular "$ROOT/state/packages/$dependency.tsv"
    test "$(hash "$ROOT/state/packages/$dependency.tsv")" = "$digest" || fail 'dependency record mismatch'
done < "$bundle/dependencies.tsv"
for blob in "$bundle/files"/* "$bundle/files"/.[!.]* "$bundle/files"/..?*; do
    test -e "$blob" || continue
    digest=${blob##*/}
    is_hash "$digest" || fail 'invalid blob name'
    regular "$blob"
    DIGEST=$digest awk -F '\t' '$1==ENVIRON["DIGEST"]{found=1} END{exit !found}' "$scratch/manifest.tsv" || fail 'unreferenced blob'
done
candidate=$scratch/candidate
mkdir -m 700 "$candidate"
cp "$ROOT/.pkg-mgr-root" "$candidate/.pkg-mgr-root"
cp -R "$ROOT/state" "$candidate/state"
mkdir -p "$candidate/stage/$name"
while IFS="$tab" read -r digest _size path; do
    regular "$bundle/files/$digest"
    test "$(hash "$bundle/files/$digest")" = "$digest" || fail 'payload hash mismatch'
    destination=$candidate/stage/$name/$path
    mkdir -p "$(dirname "$destination")"
    cp "$bundle/files/$digest" "$destination"
done < "$scratch/manifest.tsv"
while IFS="$tab" read -r mode path; do chmod "$mode" "$candidate/stage/$name/$path"; done < "$bundle/modes.tsv"
if test "$sdk" = yes; then
    stage=$candidate/stage/$name; record=$bundle/package.tsv
    sdk_identity
    cmp -s "$sdk_metadata/sdk-target.kv" "$bundle/target.kv" || fail 'SDK target differs from bound profile'
else
    host=$candidate/stage/$name/usr/local/share/pkg-mgr/$name/host.kv
    regular "$host"
    os=$(field "$host" host_os); arch=$(field "$host" host_arch); triple=$(field "$host" compiler_target)
    target_record "$os" "$arch" "$triple" > "$scratch/bound-target"
    cmp -s "$scratch/bound-target" "$bundle/target.kv" || fail 'target differs from bound build observation'
    runtime=$(field "$host" target_runtime)
    test "$runtime" = host-only || fail 'unsupported runtime'
    while IFS="$tab" read -r dependency digest; do
        observed_dependency=$(field "$host" "dependency_${dependency}_record_sha256")
        test "$observed_dependency" = "$digest" || fail 'dependency differs from bound build observation'
    done < "$bundle/dependencies.tsv"
fi
if test "$command" = preflight; then
    regular "$ROOT/state/packages/$name.tsv"
    # Substitute only in the disposable candidate. Full state loading checks the
    # proposed graph/ownership, including dependents and the editable world.
    cp "$bundle/package.tsv" "$candidate/state/packages/$name.tsv"
fi
# This checks hashes/sizes, canonical record bytes, dependencies and conflicts.
sh "$state_tool" register "$candidate" "$scratch/manifest.tsv" "$scratch/build.kv" "$scratch/deps" > /dev/null
cmp -s "$bundle/package.tsv" "$candidate/state/packages/$name.tsv" || fail 'record round-trip mismatch'
if test "$command" = preflight; then
    blocked=no
    if ! sh "$state_tool" verify "$ROOT" > "$scratch/drift"; then blocked=yes; fi
    sh "$state_tool" rdeps "$ROOT" "$name" > "$scratch/rdeps"
    if ! same_record "$ROOT/state/packages/$name.tsv" "$bundle/package.tsv" && test -s "$scratch/rdeps"; then
        blocked=yes
    else : > "$scratch/rdeps"
    fi
    awk -f "$repo/mk/update-diff.awk" "$ROOT/state/packages/$name.tsv" "$bundle/package.tsv" > "$scratch/changes.unsorted"
    sort "$scratch/changes.unsorted" > "$scratch/changes"
    sh "$repo/mk/update-observe.sh" "$ROOT" "$name" "$ROOT/state/packages/$name.tsv" "$bundle/package.tsv" > "$scratch/observed-update"
    awk -f "$repo/mk/update-three-way.awk" "$ROOT/state/packages/$name.tsv" "$bundle/package.tsv" "$scratch/observed-update" > "$scratch/three-way.unsorted"
    sort "$scratch/three-way.unsorted" > "$scratch/three-way"
    old_record_digest=$(hash "$ROOT/state/packages/$name.tsv")
    new_record_digest=$(hash "$bundle/package.tsv")
    printf 'report\tupdate-preflight-v1\tnon-mutating\n'
    printf 'package\t%s\nold-record\t%s\nnew-record\t%s\n' "$name" "$old_record_digest" "$new_record_digest"
    cat "$scratch/changes" "$scratch/three-way"
    if test "$blocked" = yes; then
        awk -F '\t' '$1!="verified" {print "blocker\tinstalled-drift\t" $0}' "$scratch/drift"
        awk '{print "blocker\treverse-dependent\t" $0}' "$scratch/rdeps"
        printf 'result\tblocked\n'
        exit 2
    fi
    printf 'result\tno-blockers-detected\n'
    exit
fi
if test "$command" = recover; then
    # Explicit adoption of an exact existing stage, never replacement or repair.
    # The pinned bundle supplies expected modes even before record publication.
    stage=$ROOT/stage/$name
    if ! { test -d "$ROOT/stage" && ! test -L "$ROOT/stage"; }; then fail 'unsafe stage directory'; fi
    if ! { test -d "$stage" && ! test -L "$stage"; }; then fail 'recovery requires an existing stage'; fi
    while IFS="$tab" read -r mode path; do
        matched=$(find "$stage/$path" -type f -perm "$mode" -print)
        test "$matched" = "$stage/$path" || fail "recovery mode/type mismatch: $path"
    done < "$bundle/modes.tsv"
    # Check the actual stage without creating a pending file in authority.
    # On failure this existing stage is deliberately not owned by cleanup().
    sh "$state_tool" check-register "$ROOT" "$scratch/manifest.tsv" "$scratch/build.kv" "$scratch/deps" > /dev/null
    if test ! -e "$ROOT/state/packages/$name.tsv"; then
        mv "$candidate/state/packages/$name.tsv" "$ROOT/state/packages/$name.tsv"
    fi
    if test "$sdk" = yes; then
        printf 'sdk-recovered\t%s\t%s\n' "$name" "$expected_digest" || exit 1
    else
        printf 'recovered\t%s\n' "$name"
    fi
    exit
fi
test ! -e "$ROOT/state/packages/$name.tsv" || fail 'package already registered'
if test -e "$ROOT/stage" || test -L "$ROOT/stage"; then
    if ! { test -d "$ROOT/stage" && ! test -L "$ROOT/stage"; }; then fail 'unsafe stage directory'; fi
else mkdir "$ROOT/stage"
fi
destination=$ROOT/stage/$name
if ! { test ! -e "$destination" && ! test -L "$destination"; }; then fail 'stage already occupied'; fi
mv "$candidate/stage/$name" "$destination"
new_stage=$destination
mv "$candidate/state/packages/$name.tsv" "$ROOT/state/packages/$name.tsv"
new_stage=
if test "$sdk" = yes; then
    printf 'sdk-imported\t%s\t%s\n' "$name" "$expected_digest" || exit 1
else
    printf 'imported\t%s\n' "$name"
fi
