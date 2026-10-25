#!/bin/sh
# Internal read-only observation for already validated old/proposed records.
set -eu
LC_ALL=C
export LC_ALL
test "$#" -eq 4 || exit 64
ROOT=$1; name=$2; old=$3; proposed=$4
export ROOT
here=$(CDPATH='' cd "$(dirname "$0")" && pwd -P)
sh "$here/check-root.sh" state
for record in "$old" "$proposed"; do
    awk -v mode=record -v expected="$name" -f "$here/state-schema.awk" "$record"
done
scratch=$(mktemp -d "${TMPDIR:-/tmp}/pkg-update-observe.XXXXXX")
trap 'rm -rf "$scratch"' 0
trap 'exit 1' HUP INT TERM
awk -F '\t' '$1=="file" {print $4}' "$old" "$proposed" > "$scratch/paths.unsorted"
sort -u "$scratch/paths.unsorted" > "$scratch/paths"
while IFS= read -r path; do
    parent=$ROOT/stage/$name
    remaining=$path
    safe=yes
    # Inspect every parent before reading a leaf; never follow a staged symlink.
    test -d "$ROOT/stage" && ! test -L "$ROOT/stage" || safe=no
    while :; do
        if test -L "$parent" || { test -e "$parent" && ! test -d "$parent"; }; then safe=no; fi
        case $remaining in
            */*) parent=$parent/${remaining%%/*}; remaining=${remaining#*/} ;;
            *) break ;;
        esac
    done
    file=$parent/$remaining
    if test "$safe" = no || test -L "$file"; then
        printf 'observed\t%s\tunsupported\n' "$path"
    elif test ! -e "$file"; then
        printf 'observed\t%s\tabsent\n' "$path"
    elif test ! -f "$file" || ! test -r "$file"; then
        printf 'observed\t%s\tunsupported\n' "$path"
    elif digest=$(sh "$here/verify-metadata.sh" hash-file "$file") && mode=$(sh "$here/file-mode.sh" "$file"); then
        printf 'observed\t%s\t%s\t%s\n' "$path" "$digest" "$mode"
    else
        printf 'observed\t%s\tunsupported\n' "$path"
    fi
done < "$scratch/paths"
