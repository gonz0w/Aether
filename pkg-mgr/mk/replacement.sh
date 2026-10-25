#!/bin/sh
# One private-root replacement, retaining old payload. Single writer required.
set -eu
LC_ALL=C
export LC_ALL
here=$(CDPATH='' cd "$(dirname "$0")" && pwd -P)
fail() { printf 'replacement-error: %s\n' "$*" >&2; exit 1; }
# cmp distinguishes ordinary differences (1) from tool/read errors (>1).
same_record() {
    if cmp -s "$1" "$2"; then return 0
    else comparison_status=$?
    fi
    test "$comparison_status" -eq 1 || fail 'cannot compare package records'
    return 1
}
hash() { sh "$here/verify-metadata.sh" hash-file "$1"; }
id() { case $1 in ''|[!A-Za-z0-9]*|*[!A-Za-z0-9._+-]*) return 1;; esac; }
sha() { test "${#1}" -eq 64 && case $1 in *[!0-9a-f]*) false;; *) true;; esac; }
test "$#" -ge 3 || fail 'prepare ROOT BUNDLE BUNDLE-PIN TARGET OLD-RECORD-PIN | finish ROOT INTENT-PIN'
command=$1; ROOT=$2; export ROOT; shift 2
case $command in
    prepare) test "$#" -eq 4 && sha "$2" && id "$3" && sha "$4" || exit 64;;
    finish) test "$#" -eq 1 && sha "$1" || exit 64;;
    *) exit 64;;
esac
sh "$here/check-root.sh" replacement
scratch=$(mktemp -d "${TMPDIR:-/tmp}/pkg-mgr-replace.XXXXXX")
trap 'rm -rf "$scratch"' 0
trap 'exit 1' HUP INT TERM
# Verify all entries before copying a caller-controlled tree.
safe_tree() {
    if ! { test -d "$1" && ! test -L "$1"; }; then fail 'expected real directory'; fi
    bad=$(find "$1" \( ! -type d ! -type f \) -print -o \( -type f -links +1 \) -print)
    test -z "$bad" || fail 'unsupported tree entry'
}
regular() {
    if ! test -f "$1" || test -L "$1"; then fail 'expected regular file'; fi
}
others() {
    sh "$here/verify-metadata.sh" manifest "$ROOT/state" "$scratch/state-manifest" >/dev/null
    NAME=$name awk -F '\t' '$3!="world" && $3!="packages/" ENVIRON["NAME"] ".tsv"' "$scratch/state-manifest"
}
intent() {
    printf 'format=retained-replacement-v1\npackage=%s\ntarget=%s\n' "$(cat "$txn/package")" "$(cat "$txn/target")"
    for file in old-record new-record world others.tsv; do
        intent_digest=$(hash "$txn/$file") || return "$?"
        printf '%s=%s\n' "$file" "$intent_digest"
    done
    intent_digest=$(hash "$txn/bundle/artifact.kv") || return "$?"
    printf 'bundle=%s\n' "$intent_digest"
}
# Reconstruct a complete root in disposable workspace for existing validators.
shadow() {
    dest=$1; record=$2; payload=$3
    mkdir -m 700 "$dest"
    cp "$ROOT/.pkg-mgr-root" "$dest/.pkg-mgr-root"
    cp -Rp "$ROOT/state" "$dest/state"
    cp "$record" "$dest/state/packages/$name.tsv"
    mkdir "$dest/stage"
    for stage in "$ROOT/stage"/*; do
        test -e "$stage" || continue
        test "${stage##*/}" != "$name" || continue
        cp -Rp "$stage" "$dest/stage/"
    done
    cp -Rp "$payload" "$dest/stage/$name"
    sh "$here/state.sh" verify "$dest" >/dev/null
}
if test "$command" = prepare; then
    bundle=$1; bundle_pin=$2; target=$3; old_pin=$4
    case $bundle in /*) ;; *) fail 'absolute bundle path required';; esac
    sh "$here/check-root.sh" state
    # Preflight validates package identity, authority, payload, dependencies and target.
    sh "$here/binary.sh" preflight "$ROOT" "$bundle" "$bundle_pin" "$target" > "$scratch/preflight"
    name=$(awk -F '\t' 'NR==2 {print $2}' "$bundle/package.tsv")
    id "$name" || fail 'invalid package'
    test "$(hash "$ROOT/state/packages/$name.tsv")" = "$old_pin" || fail 'stale old-record pin'
    if same_record "$ROOT/state/packages/$name.tsv" "$bundle/package.tsv"; then
        printf 'unchanged\t%s\n' "$name"; exit
    fi
    safe_tree "$ROOT/state"; safe_tree "$ROOT/stage"; safe_tree "$bundle"
    # Build the new stage using the existing import contract in a temporary root.
    candidate=$scratch/candidate
    shadow "$candidate" "$ROOT/state/packages/$name.tsv" "$ROOT/stage/$name"
    rm -rf "$candidate/stage/$name"
    rm "$candidate/state/packages/$name.tsv"
    NAME=$name awk '$0!=ENVIRON["NAME"]' "$candidate/state/world" > "$scratch/world"
    cp "$scratch/world" "$candidate/state/world"
    sh "$here/binary.sh" import "$candidate" "$bundle" "$bundle_pin" "$target" >/dev/null
    txn=$scratch/transaction
    mkdir -m 700 "$txn"
    printf '%s\n' "$name" > "$txn/package"
    printf '%s\n' "$target" > "$txn/target"
    cp "$ROOT/state/packages/$name.tsv" "$txn/old-record"
    cp "$candidate/state/packages/$name.tsv" "$txn/new-record"
    cp "$ROOT/state/world" "$txn/world"
    others > "$txn/others.tsv"
    cp -Rp "$bundle" "$txn/bundle"
    mv "$candidate/stage/$name" "$txn/next"
    intent > "$txn/intent.kv"
    pin=$(hash "$txn/intent.kv")
    # Adjacent staging makes pending publication a same-filesystem rename.
    staging=$(mktemp -d "$ROOT/.replacement-preparing.XXXXXX")
    cp -Rp "$txn/." "$staging/"
    if ! { test ! -e "$ROOT/.replacement" && ! test -L "$ROOT/.replacement"; }; then fail 'replacement already pending'; fi
    mv "$staging" "$ROOT/.replacement"
    printf 'prepared\t%s\t%s\n' "$name" "$pin"
    exit
fi
pin=$1
completed=no
txn=$ROOT/.replacement
if test ! -e "$txn" && ! test -L "$txn"; then
    if ! { test -d "$ROOT/replacements" && ! test -L "$ROOT/replacements"; }; then fail 'invalid retained directory'; fi
    txn=$ROOT/replacements/$pin
    completed=yes
fi
safe_tree "$txn"
for file in package target old-record new-record world others.tsv intent.kv; do regular "$txn/$file"; done
name=$(cat "$txn/package"); target=$(cat "$txn/target")
if ! { id "$name" && id "$target"; }; then fail 'invalid intent identity'; fi
test "$(hash "$txn/intent.kv")" = "$pin" || fail 'intent pin mismatch'
intent > "$scratch/intent"
cmp -s "$scratch/intent" "$txn/intent.kv" || fail 'intent content mismatch'
for entry in "$txn"/* "$txn"/.[!.]* "$txn"/..?*; do
    test -e "$entry" || continue
    case ${entry##*/} in package|target|old-record|new-record|world|others.tsv|intent.kv|bundle|next|previous|record-publishing) ;; *) fail 'unknown transaction entry';; esac
done
if test -e "$txn/record-publishing"; then
    cmp -s "$txn/record-publishing" "$txn/new-record" || fail 'invalid pending record copy'
fi
safe_tree "$ROOT/state"; safe_tree "$ROOT/stage"
cmp -s "$ROOT/state/world" "$txn/world" || fail 'world changed since preparation'
others > "$scratch/others"
cmp -s "$scratch/others" "$txn/others.tsv" || fail 'unrelated state changed since preparation'
current=$ROOT/state/packages/$name.tsv
regular "$current"
if same_record "$current" "$txn/old-record"; then record_state=old
elif same_record "$current" "$txn/new-record"; then record_state=new
else fail 'unexpected current record'
fi
# Infer progress from validated locations, not a mutable phase counter.
if test -d "$txn/next"; then
    if ! { test "$record_state" = old && test "$completed" = no; }; then fail 'inconsistent next stage'; fi
    new_payload=$txn/next
    if test -d "$txn/previous"; then
        test ! -e "$ROOT/stage/$name" || fail 'ambiguous displaced stage'
        old_payload=$txn/previous
    else old_payload=$ROOT/stage/$name
    fi
else
    old_payload=$txn/previous
    new_payload=$ROOT/stage/$name
fi
safe_tree "$old_payload"; safe_tree "$new_payload"
shadow "$scratch/before" "$txn/old-record" "$old_payload"
shadow "$scratch/after" "$txn/new-record" "$new_payload"
cmp -s "$txn/new-record" "$txn/bundle/package.tsv" || fail 'proposed record differs from bundle'
bundle_pin=$(hash "$txn/bundle/artifact.kv")
sh "$here/binary.sh" preflight "$scratch/before" "$txn/bundle" "$bundle_pin" "$target" > "$scratch/preflight"
if test "$completed" = yes; then
    test "$record_state" = new || fail 'completed transaction does not match current record'
    printf 'completed\t%s\t%s\n' "$name" "$pin"; exit
fi
if test -e "$ROOT/replacements" || test -L "$ROOT/replacements"; then
    if ! { test -d "$ROOT/replacements" && ! test -L "$ROOT/replacements"; }; then fail 'invalid retained directory'; fi
else mkdir "$ROOT/replacements"
fi
if ! { test ! -e "$ROOT/replacements/$pin" && ! test -L "$ROOT/replacements/$pin"; }; then fail 'retained destination occupied'; fi
if test ! -d "$txn/previous"; then mv "$ROOT/stage/$name" "$txn/previous"; fi
if test -d "$txn/next"; then mv "$txn/next" "$ROOT/stage/$name"; fi
if test "$record_state" = old; then
    # Keep the pinned new record in the retained evidence too.
    cp "$txn/new-record" "$txn/record-publishing"
    mv "$txn/record-publishing" "$current"
fi
mv "$txn" "$ROOT/replacements/$pin"
printf 'completed\t%s\t%s\n' "$name" "$pin"
