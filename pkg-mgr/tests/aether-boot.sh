#!/bin/sh
set -eu
scratch=$(mktemp -d "${TMPDIR:-/tmp}/pkg-mgr-boot-test.XXXXXX")
trap 'rm -rf "$scratch"' 0
trap 'exit 1' HUP INT TERM
root=$scratch/'private root'
(umask 077; mkdir "$root")
make -s -f mk/pkg.mk ROOT="$root" init-root
# Header-shaped bytes exercise only the transport guard, never a boot claim.
printf '\177ELF\002\001\001\000\000\000\000\000\000\000\000\000\002\000\076\000' > "$scratch/kernel"
dd if=/dev/zero bs=44 count=1 >> "$scratch/kernel" 2>/dev/null
printf fixture > "$scratch/user"
hash() { sh mk/verify-metadata.sh hash-file "$1"; }
kernel_hash=$(hash "$scratch/kernel"); user_hash=$(hash "$scratch/user")
reject() { if "$@" > "$scratch/out" 2> "$scratch/err"; then printf 'unexpected handoff success\n' >&2; exit 1; fi; }
reject sh mk/aether-boot.sh stage "$root" "$scratch/kernel" "$scratch/user" "$user_hash" "$user_hash"
test ! -e "$root/aether-boot"
printf X > "$scratch/bad-kernel"
reject sh mk/aether-boot.sh stage "$root" "$scratch/bad-kernel" "$scratch/user" "$(hash "$scratch/bad-kernel")" "$user_hash"
dd if=/dev/zero of="$scratch/oversized" bs=4097 count=1 2>/dev/null
reject sh mk/aether-boot.sh stage "$root" "$scratch/kernel" "$scratch/oversized" "$kernel_hash" "$(hash "$scratch/oversized")"
# Failed final publication leaves no bundle or pending directory.
mkdir "$scratch/bin"
cat > "$scratch/bin/mv" <<'WRAPPER'
#!/bin/sh
for destination do :; done
case $destination in */aether-boot) exit 1 ;; esac
exec "$REAL_MV" "$@"
WRAPPER
chmod +x "$scratch/bin/mv"
reject env PATH="$scratch/bin:$PATH" REAL_MV="$(command -v mv)" sh mk/aether-boot.sh stage "$root" "$scratch/kernel" "$scratch/user" "$kernel_hash" "$user_hash"
test ! -e "$root/aether-boot"
test -z "$(find "$root" -name '.aether-boot.*' -print)"
sh mk/aether-boot.sh stage "$root" "$scratch/kernel" "$scratch/user" "$kernel_hash" "$user_hash"
sh mk/aether-boot.sh verify "$root"
cp "$root/aether-boot/receipt.kv" "$scratch/receipt"
reject sh mk/aether-boot.sh stage "$root" "$scratch/kernel" "$scratch/user" "$kernel_hash" "$user_hash"
cmp "$scratch/receipt" "$root/aether-boot/receipt.kv"
printf X | dd of="$root/aether-boot/boot/protection.bin" bs=1 seek=0 conv=notrunc 2>/dev/null
reject sh mk/aether-boot.sh verify "$root"
cp "$scratch/user" "$root/aether-boot/boot/protection.bin"
printf unknown > "$root/aether-boot/extra"
reject sh mk/aether-boot.sh verify "$root"
rm "$root/aether-boot/extra"
ln -s "$scratch/user" "$root/aether-boot/boot/link"
reject sh mk/aether-boot.sh verify "$root"
rm "$root/aether-boot/boot/link"
printf 'service_activation=enabled\n' >> "$root/aether-boot/receipt.kv"
reject sh mk/aether-boot.sh verify "$root"
cp "$scratch/receipt" "$root/aether-boot/receipt.kv"
sh mk/aether-boot.sh verify "$root"
printf 'Aether boot transport guards passed; synthetic inputs were not booted\n'
