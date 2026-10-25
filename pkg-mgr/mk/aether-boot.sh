#!/bin/sh
# Transport an explicitly pinned boot pair; not a package or service loader ABI.
set -eu
LC_ALL=C
export LC_ALL
script_dir=$(CDPATH='' cd "$(dirname "$0")" && pwd -P)
verifier=$script_dir/verify-metadata.sh
fail() { printf 'aether-handoff-error: %s\n' "$*" >&2; exit 1; }
test "$#" -ge 2 || fail 'usage: aether-boot.sh stage ROOT KERNEL USER KERNEL_SHA256 USER_SHA256 | verify ROOT'
command=$1; ROOT=$2; export ROOT; shift 2
case $command in stage) test "$#" -eq 4 || exit 64 ;; verify) test "$#" -eq 0 || exit 64 ;; *) exit 64 ;; esac
sh "$script_dir/check-root.sh" state
bundle=$ROOT/aether-boot
scratch=$(mktemp -d "${TMPDIR:-/tmp}/pkg-mgr-aether.XXXXXX")
pending=
trap 'rm -rf "$scratch"; if test -n "$pending"; then rm -rf "$pending"; fi' 0
trap 'exit 1' HUP INT TERM
hash() { sh "$verifier" hash-file "$1"; }
is_hash() { case $1 in ''|*[!0-9a-f]*) return 1 ;; esac; test "${#1}" -eq 64; }
regular() { if ! { test -f "$1" && ! test -L "$1" && test -r "$1"; }; then fail 'expected readable regular file'; fi; }
headers() {
    regular "$1"; regular "$2"
    # A header guard only: the actual image builder and guest validate usability.
    bytes=$(od -An -tx1 -N20 "$1")
    bytes=$(printf '%s' "$bytes" | tr -d '[:space:]')
    case $bytes in 7f454c46020101??????????????????02003e00) ;; *) fail 'expected ELF64 little-endian x86_64 executable header' ;; esac
    kernel_size=$(wc -c < "$1")
    user_size=$(wc -c < "$2")
    test "$kernel_size" -ge 64 || fail 'truncated ELF header'
    if ! { test "$user_size" -gt 0 && test "$user_size" -le 4096; }; then fail 'user fixture must occupy 1..4096 bytes'; fi
}
receipt() {
    printf '%s\n' 'format=aether-boot-handoff-v1' 'target_arch=x86_64' \
        'target_abi=unversioned-aether-fixture' 'kernel_format=elf64-le-x86_64' \
        'user_format=flat-fixture-page' "kernel_sha256=$1" "user_sha256=$2" \
        'source_authenticity=not-proven' 'service_activation=unsupported'
}
verify_bundle() {
    directory=$1
    if ! { test -d "$directory" && ! test -L "$directory"; }; then fail 'missing regular bundle directory'; fi
    if ! { test -d "$directory/boot" && ! test -L "$directory/boot"; }; then fail 'invalid boot directory'; fi
    bad=$(find "$directory" \( ! -type d ! -type f \) -print -o \( -type f -links +1 \) -print)
    test -z "$bad" || fail 'bundle contains links or special files'
    for entry in "$directory"/* "$directory"/.[!.]* "$directory"/..?* \
        "$directory/boot"/* "$directory/boot"/.[!.]* "$directory/boot"/..?*; do
        test -e "$entry" || continue
        case $entry in "$directory/boot"|"$directory/boot/aether"|"$directory/boot/protection.bin"|"$directory/manifest.tsv"|"$directory/receipt.kv") ;; *) fail 'unknown bundle entry' ;; esac
    done
    regular "$directory/receipt.kv"; regular "$directory/manifest.tsv"
    headers "$directory/boot/aether" "$directory/boot/protection.bin"
    receipt "$(hash "$directory/boot/aether")" "$(hash "$directory/boot/protection.bin")" > "$scratch/receipt"
    cmp -s "$scratch/receipt" "$directory/receipt.kv" || fail 'receipt or payload mismatch'
    sh "$verifier" manifest "$directory/boot" "$scratch/manifest" > /dev/null
    cmp -s "$scratch/manifest" "$directory/manifest.tsv" || fail 'manifest mismatch'
}
if test "$command" = verify; then
    verify_bundle "$bundle"
    printf 'aether-handoff-verified\n'
    exit
fi
kernel=$1; user=$2; kernel_hash=$3; user_hash=$4
if ! { is_hash "$kernel_hash" && is_hash "$user_hash"; }; then fail 'expected explicit lowercase SHA-256 pins'; fi
if ! { test ! -e "$bundle" && ! test -L "$bundle"; }; then fail 'bundle already exists; use a fresh private root'; fi
headers "$kernel" "$user"
if ! { test "$(hash "$kernel")" = "$kernel_hash" && test "$(hash "$user")" = "$user_hash"; }; then fail 'input hash mismatch'; fi
pending=$(mktemp -d "$ROOT/.aether-boot.XXXXXX")
mkdir "$pending/boot"
cp "$kernel" "$pending/boot/aether"
cp "$user" "$pending/boot/protection.bin"
receipt "$kernel_hash" "$user_hash" > "$pending/receipt.kv"
sh "$verifier" manifest "$pending/boot" "$pending/manifest.tsv" > /dev/null
verify_bundle "$pending"
mv "$pending" "$bundle"
pending=
printf 'aether-handoff-staged\n'
