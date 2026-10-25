#!/bin/sh
# Private staged-package state: plain records, no installation or deletion.
set -eu
LC_ALL=C
export LC_ALL
script_dir=$(CDPATH='' cd "$(dirname "$0")" && pwd -P)
verifier=$script_dir/verify-metadata.sh
schema=$script_dir/state-schema.awk
fail() { printf 'state-error: %s\n' "$*" >&2; exit 1; }
valid_id() { case $1 in ''|[!A-Za-z0-9]*|*[!A-Za-z0-9._+-]*) return 1 ;; esac; }

# find passes paths as arguments so tabs/newlines cannot impersonate rows.
if test "${1-}" = _scan; then
    stage=$2; failure=$3; shift 3
    for entry do
        test "$entry" != "$stage" || continue
        relative=${entry#"$stage"/}
        case $relative in
            ''|*[!A-Za-z0-9._+\ /-]*|/*|*/|*//*|.|..|./*|../*|*/./*|*/../*|*/.|*/..)
                printf 'unsupported-path\n' > "$failure"; exit 1 ;;
        esac
        if test -L "$entry"; then type=symlink
        elif test -d "$entry"; then type=directory
        elif test -f "$entry"; then type='file'
        else type=special
        fi
        printf '%s\t%s\n' "$type" "$relative"
    done
    exit
fi

test "$#" -ge 2 || fail 'usage: state.sh <init|register|check-register|list|owners|files|deps|rdeps|verify|orphans> ROOT [arguments]'
command=$1; ROOT=$2; export ROOT; shift 2
case $command in
    init|list|owners|verify|orphans) test "$#" -eq 0 || exit 64 ;;
    files|deps|rdeps) test "$#" -eq 1 && valid_id "$1" || exit 64 ;;
    register|check-register) test "$#" -eq 3 || fail 'register ROOT MANIFEST BUILD-RECORD DEPENDENCIES (absolute file paths)' ;;
    *) exit 64 ;;
esac
sh "$script_dir/check-root.sh" state
state=$ROOT/state
scratch=$(mktemp -d "${TMPDIR:-/tmp}/pkg-mgr-state.XXXXXX")
pending=
trap 'rm -rf "$scratch"; if test -n "$pending"; then rm -rf "$pending"; fi' 0
trap 'exit 1' HUP INT TERM
hash() { sh "$verifier" hash-file "$1" || fail 'cannot hash regular file'; }
regular() { if ! { test -f "$1" && test -r "$1" && ! test -L "$1"; }; then fail 'expected readable regular input'; fi; }

if test "$command" = init; then
    if ! { test ! -e "$state" && ! test -L "$state"; }; then fail 'state already exists'; fi
    pending=$(mktemp -d "$ROOT/.state-init.XXXXXX")
    mkdir "$pending/packages"
    : > "$pending/world"
    mv "$pending" "$state"
    pending=
    printf 'state-initialized\n'
    exit
fi

if ! { test -d "$state" && ! test -L "$state"; }; then fail 'initialize state first'; fi
if ! { test -d "$state/packages" && ! test -L "$state/packages"; }; then fail 'invalid packages directory'; fi
regular "$state/world"
bad=$(find "$state" \( ! -type d ! -type f \) -print -o \( -type f -links +1 \) -print) || fail 'cannot inspect authority files'
test -z "$bad" || fail 'unsupported authority link/type'
for entry in "$state"/* "$state"/.[!.]* "$state"/..?*; do
    test -e "$entry" || continue
    case $entry in "$state/world"|"$state/packages") ;; *) fail 'unknown state entry' ;; esac
done

# Validate records independently of stage contents, then derive one temporary view.
validate_record() {
    record=$1; expected=$2
    regular "$record"
    awk -v mode=record -v expected="$expected" -f "$schema" "$record"
    awk -F '\t' '$1=="file" {print $2 "\t" $3 "\t" $4}' "$record" > "$scratch/manifest"
    manifest_digest=$(awk -F '\t' '$1=="evidence" && $2=="manifest_hash" {print substr($3,8)}' "$record")
    test "$(hash "$scratch/manifest")" = "$manifest_digest" || fail 'record manifest fingerprint mismatch'
    awk -F '\t' '$1=="evidence" {print $2 "=" $3}' "$record" > "$scratch/build"
    build_digest=$(awk -F '\t' '$1=="build-record" {print $2}' "$record")
    test "$(hash "$scratch/build")" = "$build_digest" || fail 'record build fingerprint mismatch'
}
append_record() {
    awk -F '\t' 'BEGIN {OFS="\t"} $1=="package" {p=$2; print} $1=="dependency" {print "dependency",p,$2} $1=="file" {print "file",p,$2,$3,$4,(NF==5 ? $5 : "untracked")}' "$1" >> "$scratch/database"
}
: > "$scratch/database"
for record in "$state/packages"/* "$state/packages"/.[!.]* "$state/packages"/..?*; do
    test -e "$record" || continue
    name=${record##*/}; name=${name%.tsv}
    if ! { valid_id "$name" && test "$record" = "$state/packages/$name.tsv"; }; then fail 'invalid package record filename'; fi
    validate_record "$record" "$name"
    append_record "$record"
done
awk -v mode=names -f "$schema" "$state/world" > "$scratch/roots"
awk '{print "root\t" $0}' "$scratch/roots" >> "$scratch/database"
awk -v mode=check -f "$script_dir/state-views.awk" "$scratch/database"

scan_stage() {
    stage=$ROOT/stage/$1
    test -d "$ROOT/stage" && ! test -L "$ROOT/stage" || return 1
    test -d "$stage" && ! test -L "$stage" || return 1
    : > "$scratch/scan-failure"
    find "$stage" -exec sh "$script_dir/state.sh" _scan "$stage" "$scratch/scan-failure" {} + > "$scratch/observed" || return 1
    test ! -s "$scratch/scan-failure" || return 1
    # Hard links are excluded even when their content currently matches.
    links=$(find "$stage" -type f -links +1 -print) || return 1
    test -z "$links" || return 1
}

if test "$command" = register || test "$command" = check-register; then
    supplied_manifest=$1; supplied_build=$2; dependencies=$3
    for input do
        case $input in /*) ;; *) fail 'registration inputs must be absolute paths' ;; esac
        regular "$input"
    done
    awk -v mode=build -f "$schema" "$supplied_build"
    name=$(sed -n 's/^package_name=//p' "$supplied_build")
    version=$(sed -n 's/^version=//p' "$supplied_build")
    scan_stage "$name" || fail 'missing or unsupported stage'
    awk -F '\t' '$1!="file" && $1!="directory" {exit 1}' "$scratch/observed" || fail 'unsupported staged type'
    sh "$verifier" manifest "$stage" "$scratch/actual.manifest" > /dev/null
    cmp -s "$supplied_manifest" "$scratch/actual.manifest" || fail 'stage does not match supplied manifest'
    awk -v mode=names -f "$schema" "$dependencies" > "$scratch/deps.unsorted"
    sort "$scratch/deps.unsorted" > "$scratch/deps"
    candidate=$scratch/candidate
    {
        printf 'format\tpkg-state-v2\npackage\t%s\t%s\nbuild-record\t%s\n' "$name" "$version" "$(hash "$supplied_build")"
        awk '{eq=index($0,"="); print "evidence\t" substr($0,1,eq-1) "\t" substr($0,eq+1)}' "$supplied_build"
        awk '{print "dependency\t" $0}' "$scratch/deps"
        tab=$(printf '\t')
        while IFS="$tab" read -r digest size path; do
            permissions=$(sh "$script_dir/file-mode.sh" "$stage/$path") || fail 'cannot record file permissions'
            printf 'file\t%s\t%s\t%s\t%s\n' "$digest" "$size" "$path" "$permissions"
        done < "$supplied_manifest"
    } > "$candidate"
    validate_record "$candidate" "$name"
    destination=$state/packages/$name.tsv
    if test -e "$destination"; then
        cmp -s "$candidate" "$destination" || fail 'package already registered with different evidence; update is not implemented'
        printf 'already-registered\t%s\n' "$name"
        exit
    fi
    append_record "$candidate"
    awk -v mode=check -f "$script_dir/state-views.awk" "$scratch/database"
    if test "$command" = check-register; then
        printf 'registration-checked\t%s\n' "$name"
        exit
    fi
    pending=$(mktemp "$state/packages/.pending.XXXXXX")
    cp "$candidate" "$pending"
    mv "$pending" "$destination"
    pending=
    printf 'registered\t%s\n' "$name"
    exit
fi

if test "$command" = verify; then
    : > "$scratch/report"
    for record in "$state/packages"/*.tsv; do
        test -f "$record" || continue
        name=${record##*/}; name=${name%.tsv}
        if ! scan_stage "$name"; then
            printf 'unsupported-or-missing-stage\t%s\n' "$name" >> "$scratch/report"
            continue
        fi
        if ! awk -F '\t' '$1!="file" && $1!="directory" {exit 1}' "$scratch/observed"; then
            printf 'unsupported-type\t%s\n' "$name" >> "$scratch/report"
            continue
        fi
        awk -F '\t' '$1=="file" {print $2 "\t" $3 "\t" $4 "\t" (NF==5 ? $5 : "untracked")}' "$record" > "$scratch/expected"
        tab=$(printf '\t')
        while IFS="$tab" read -r digest size relative permissions; do
            target=$stage/$relative
            if test ! -e "$target"; then result=missing
            elif test ! -f "$target"; then result='type-mismatch'
            elif test ! -r "$target"; then result=unreadable
            elif ! actual_size=$(wc -c < "$target"); then result=unreadable
            elif test "$(printf '%s' "$actual_size" | tr -d '[:space:]')" != "$size"; then result='size-mismatch'
            elif ! actual=$(sh "$verifier" hash-file "$target"); then result=unreadable
            elif test "$actual" != "$digest"; then result=content-mismatch
            elif test "$permissions" = untracked; then result=mode-untracked
            elif ! actual_mode=$(sh "$script_dir/file-mode.sh" "$target"); then result=unsupported-mode
            elif test "$actual_mode" != "$permissions"; then result=mode-mismatch
            else continue
            fi
            printf '%s\t%s\t%s\n' "$result" "$name" "$relative" >> "$scratch/report"
        done < "$scratch/expected"
        awk -F '\t' -v name="$name" 'FILENAME==ARGV[1] {known[$3]=1; next} $1=="file" && !($2 in known) {print "unowned\t" name "\t" $2}' "$scratch/expected" "$scratch/observed" >> "$scratch/report"
    done
    if test -s "$scratch/report"; then sort "$scratch/report"; exit 1; fi
    printf 'verified\tstaged-regular-files\n'
    exit
fi

query=${1-}
awk -v mode="$command" -v query="$query" -f "$script_dir/state-views.awk" "$scratch/database" > "$scratch/view"
sort "$scratch/view" > "$scratch/sorted"
if test "$command" = orphans; then printf 'report\torphan-plan-v1\tnon-deleting\n'; fi
cat "$scratch/sorted"
