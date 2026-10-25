#!/bin/sh
# Transport the five-artifact M4 profile; legacy aether-boot.sh is unchanged.
set -eu
LC_ALL=C
export LC_ALL
script_dir=$(CDPATH='' cd "$(dirname "$0")" && pwd -P)
verifier=$script_dir/verify-metadata.sh
fail() { printf 'aether-handoff-v2-error: %s\n' "$*" >&2; exit 1; }
test "$#" -ge 2 || fail 'usage: aether-boot-v2.sh stage ROOT KERNEL PROTECTION DISPLAY LIFECYCLE SMP KPIN PPIN DPIN LPIN SPIN SOURCE_PIN | verify ROOT RECEIPT_SHA256'
command=$1; ROOT=$2; export ROOT; shift 2
case $command in stage) test "$#" -eq 11 || exit 64 ;; verify) test "$#" -eq 1 || exit 64 ;; *) exit 64 ;; esac
sh "$script_dir/check-root.sh" state
bundle=$ROOT/aether-boot-v2
scratch=$(mktemp -d "${TMPDIR:-/tmp}/pkg-mgr-aether.XXXXXX")
pending=
trap 'rm -rf "$scratch"; if test -n "$pending"; then rm -rf "$pending"; fi' 0
trap 'exit 1' HUP INT TERM
hash() { sh "$verifier" hash-file "$1"; }
is_hash() { case $1 in ''|*[!0-9a-f]*) return 1 ;; esac; test "${#1}" -eq 64; }
regular() { if ! { test -f "$1" && ! test -L "$1" && test -r "$1"; }; then fail 'expected readable regular file'; fi; }
flat() {
    regular "$1"
    size=$(wc -c < "$1")
    if ! { test "$size" -gt 0 && test "$size" -le 4096; }; then fail 'flat fixture must occupy 1..4096 bytes'; fi
}
headers() {
    regular "$1"
    bytes=$(od -An -tx1 -N20 "$1" | tr -d '[:space:]')
    case $bytes in 7f454c46020101??????????????????02003e00) ;; *) fail 'expected ELF64 little-endian x86_64 executable header' ;; esac
    test "$(wc -c < "$1")" -ge 64 || fail 'truncated ELF header'
    flat "$2"; flat "$3"; flat "$5"
    regular "$4"
    total=$(wc -c < "$4")
    if ! { test "$total" -ge 33 && test "$total" -le 4128; }; then fail 'invalid lifecycle length'; fi
    header=$(od -An -tx1 -N24 "$4" | tr -d '[:space:]')
    test "$header" = 41454c494645303101000000010000000000400000000000 || fail 'invalid lifecycle ABI, role or entry'
    reserved=$(od -An -tx1 -j28 -N4 "$4" | tr -d '[:space:]')
    test "$reserved" = 00000000 || fail 'nonzero lifecycle reserved field'
    length_bytes=$(od -An -tu1 -j24 -N4 "$4")
    # od emits only decimal byte values; word splitting is intentional here.
    # Exactly four decimal bytes from od; deliberate splitting cannot expand paths.
    # shellcheck disable=SC2086
    set -- $length_bytes
    length=$(($1 + 256 * $2 + 65536 * $3 + 16777216 * $4))
    if ! { test "$length" -ge 1 && test "$length" -le 4096 && test "$total" -eq "$((32 + length))"; }; then fail 'lifecycle length mismatch'; fi
}
receipt() {
    directory=$1; source_pin=$2
    printf '%s\n' 'format=aether-boot-handoff-v2' 'profile=aether-m4-five-v1' \
        'target_arch=x86_64' 'target_abi=unversioned-aether-fixture' \
        "build_source_sha256=$source_pin"
    for name in aether protection.bin display.bin lifecycle.bin smp-supervisor.bin; do
        printf '%s_sha256=%s\n' "$name" "$(hash "$directory/boot/$name")"
        size=$(wc -c < "$directory/boot/$name" | tr -d '[:space:]')
        printf '%s_size=%s\n' "$name" "$size"
    done
    printf '%s\n' 'source_authenticity=not-proven' 'service_activation=unsupported'
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
        case $entry in "$directory/boot"|"$directory/boot/aether"|"$directory/boot/protection.bin"|"$directory/boot/display.bin"|"$directory/boot/lifecycle.bin"|"$directory/boot/smp-supervisor.bin"|"$directory/manifest.tsv"|"$directory/receipt.kv") ;; *) fail 'unknown bundle entry' ;; esac
    done
    regular "$directory/receipt.kv"; regular "$directory/manifest.tsv"
    headers "$directory/boot/aether" "$directory/boot/protection.bin" "$directory/boot/display.bin" "$directory/boot/lifecycle.bin" "$directory/boot/smp-supervisor.bin"
    source_pin=$(sed -n 's/^build_source_sha256=//p' "$directory/receipt.kv")
    is_hash "$source_pin" || fail 'invalid source identity'
    receipt "$directory" "$source_pin" > "$scratch/receipt"
    cmp -s "$scratch/receipt" "$directory/receipt.kv" || fail 'receipt or payload mismatch'
    sh "$verifier" manifest "$directory/boot" "$scratch/manifest" > /dev/null
    cmp -s "$scratch/manifest" "$directory/manifest.tsv" || fail 'manifest mismatch'
}
if test "$command" = verify; then
    is_hash "$1" || fail 'expected receipt pin'
    regular "$bundle/receipt.kv"
    test "$(hash "$bundle/receipt.kv")" = "$1" || fail 'receipt pin mismatch'
    verify_bundle "$bundle"
    printf 'aether-handoff-v2-verified\n'
    exit
fi
kernel=$1; protection=$2; display=$3; lifecycle=$4; smp=$5
shift 5
kernel_pin=$1; protection_pin=$2; display_pin=$3; lifecycle_pin=$4; smp_pin=$5; source_pin=$6
for pin in "$kernel_pin" "$protection_pin" "$display_pin" "$lifecycle_pin" "$smp_pin" "$source_pin"; do
    is_hash "$pin" || fail 'expected explicit lowercase SHA-256 pins'
done
if ! { test ! -e "$bundle" && ! test -L "$bundle"; }; then fail 'bundle already exists; use a fresh private root'; fi
headers "$kernel" "$protection" "$display" "$lifecycle" "$smp"
test "$(hash "$kernel")" = "$kernel_pin" && test "$(hash "$protection")" = "$protection_pin" && \
    test "$(hash "$display")" = "$display_pin" && test "$(hash "$lifecycle")" = "$lifecycle_pin" && \
    test "$(hash "$smp")" = "$smp_pin" || fail 'input hash mismatch'
pending=$(mktemp -d "$ROOT/.aether-boot-v2.XXXXXX")
mkdir "$pending/boot"
cp "$kernel" "$pending/boot/aether"
cp "$protection" "$pending/boot/protection.bin"
cp "$display" "$pending/boot/display.bin"
cp "$lifecycle" "$pending/boot/lifecycle.bin"
cp "$smp" "$pending/boot/smp-supervisor.bin"
# Bind the copied payload to every explicit input pin before publication.
test "$(hash "$pending/boot/aether")" = "$kernel_pin" && \
    test "$(hash "$pending/boot/protection.bin")" = "$protection_pin" && \
    test "$(hash "$pending/boot/display.bin")" = "$display_pin" && \
    test "$(hash "$pending/boot/lifecycle.bin")" = "$lifecycle_pin" && \
    test "$(hash "$pending/boot/smp-supervisor.bin")" = "$smp_pin" || fail 'copied input hash mismatch'
receipt "$pending" "$source_pin" > "$pending/receipt.kv"
sh "$verifier" manifest "$pending/boot" "$pending/manifest.tsv" > /dev/null
verify_bundle "$pending"
mv "$pending" "$bundle"
pending=
printf 'aether-handoff-v2-staged\n'
