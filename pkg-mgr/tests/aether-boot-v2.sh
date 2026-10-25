#!/bin/sh
set -eu
scratch=$(mktemp -d "${TMPDIR:-/tmp}/pkg-mgr-boot-v2-test.XXXXXX")
trap 'rm -rf "$scratch"' 0
trap 'exit 1' HUP INT TERM
root=$scratch/'private root'
(umask 077; mkdir "$root")
make -s -f mk/pkg.mk ROOT="$root" init-root
printf '\177ELF\002\001\001\000\000\000\000\000\000\000\000\000\002\000\076\000' > "$scratch/kernel"
dd if=/dev/zero bs=44 count=1 >> "$scratch/kernel" 2>/dev/null
printf protection > "$scratch/protection"
printf display > "$scratch/display"
printf supervisor > "$scratch/smp"
printf 'AELIFE01\001\000\000\000\001\000\000\000\000\000\100\000\000\000\000\000\001\000\000\000\000\000\000\000X' > "$scratch/lifecycle"
hash() { sh mk/verify-metadata.sh hash-file "$1"; }
k=$(hash "$scratch/kernel"); p=$(hash "$scratch/protection"); d=$(hash "$scratch/display"); l=$(hash "$scratch/lifecycle"); s=$(hash "$scratch/smp")
reject() { if "$@" > "$scratch/out" 2> "$scratch/err"; then printf 'unexpected v2 handoff success\n' >&2; exit 1; fi; }
stage() { sh mk/aether-boot-v2.sh stage "$root" "$scratch/kernel" "$scratch/protection" "$scratch/display" "$scratch/lifecycle" "$scratch/smp" "$k" "$p" "$d" "$l" "$s" "$k"; }
# Hash mismatch, missing input and lifecycle ABI mismatch fail before publication.
printf altered > "$scratch/display"
reject stage; test ! -e "$root/aether-boot-v2"
printf display > "$scratch/display"
mv "$scratch/smp" "$scratch/smp-save"
reject stage; test ! -e "$root/aether-boot-v2"
mv "$scratch/smp-save" "$scratch/smp"
cp "$scratch/lifecycle" "$scratch/life-save"
printf '\002' | dd of="$scratch/lifecycle" bs=1 seek=8 conv=notrunc 2>/dev/null
reject stage
cp "$scratch/life-save" "$scratch/lifecycle"
# Swapped typed roles with their original pins fail; arbitrary flat semantics need target checks.
reject sh mk/aether-boot-v2.sh stage "$root" "$scratch/kernel" "$scratch/display" "$scratch/protection" "$scratch/lifecycle" "$scratch/smp" "$k" "$p" "$d" "$l" "$s" "$k"
# Envelope reserved/length errors are format failures even with otherwise valid input paths.
for offset in 12 16 24 28; do
    printf '\377' | dd of="$scratch/lifecycle" bs=1 seek="$offset" conv=notrunc 2>/dev/null
    reject stage
    cp "$scratch/life-save" "$scratch/lifecycle"
done
mkdir "$scratch/bin"
cat > "$scratch/bin/mv" <<'WRAPPER'
#!/bin/sh
for destination do :; done
case $destination in */aether-boot-v2) exit 1 ;; esac
exec "$REAL_MV" "$@"
WRAPPER
chmod +x "$scratch/bin/mv"
reject env PATH="$scratch/bin:$PATH" REAL_MV="$(command -v mv)" sh mk/aether-boot-v2.sh stage "$root" "$scratch/kernel" "$scratch/protection" "$scratch/display" "$scratch/lifecycle" "$scratch/smp" "$k" "$p" "$d" "$l" "$s" "$k"
test ! -e "$root/aether-boot-v2"
test -z "$(find "$root" -name '.aether-boot-v2.*' -print)"
stage
receipt=$(hash "$root/aether-boot-v2/receipt.kv")
sh mk/aether-boot-v2.sh verify "$root" "$receipt"
reject stage
reject sh mk/aether-boot-v2.sh verify "$root" "$k"
cp "$root/aether-boot-v2/receipt.kv" "$scratch/receipt"
for artifact in aether protection.bin display.bin lifecycle.bin smp-supervisor.bin; do
    cp "$root/aether-boot-v2/boot/$artifact" "$scratch/original"
    printf altered > "$root/aether-boot-v2/boot/$artifact"
    reject sh mk/aether-boot-v2.sh verify "$root" "$receipt"
    cp "$scratch/original" "$root/aether-boot-v2/boot/$artifact"
done
printf extra > "$root/aether-boot-v2/boot/extra"
reject sh mk/aether-boot-v2.sh verify "$root" "$receipt"
rm "$root/aether-boot-v2/boot/extra"
ln -s "$scratch/display" "$root/aether-boot-v2/link"
reject sh mk/aether-boot-v2.sh verify "$root" "$receipt"
rm "$root/aether-boot-v2/link"
printf 'service_activation=enabled\n' >> "$root/aether-boot-v2/receipt.kv"
reject sh mk/aether-boot-v2.sh verify "$root" "$receipt"
cp "$scratch/receipt" "$root/aether-boot-v2/receipt.kv"
sh mk/aether-boot-v2.sh verify "$root" "$receipt"
printf 'V2 five-artifact guards passed; synthetic inputs were not booted\n'
