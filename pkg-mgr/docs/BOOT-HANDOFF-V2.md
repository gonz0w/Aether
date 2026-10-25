# Five-artifact Aether boot handoff

Implemented for explicitly pinned private-root transport, 2026-09-05. The original
`mk/aether-boot.sh` remains unchanged for historical v1 kernel/protection pairs.
The new `mk/aether-boot-v2.sh` consumes the current matching M4 kernel and all four
modules. It does not install packages, activate services or establish authenticity.

Aether's `zig build` now exports `zig-out/bin/aether` and matching files under
`zig-out/boot/`: protection.bin, display.bin, lifecycle.bin, smp-supervisor.bin.
Build from one pinned source snapshot, hash its source inventory, then stage:

```sh
sh mk/aether-boot-v2.sh stage "$root" "$kernel" "$protection" "$display" "$lifecycle" "$smp" "$kernel_pin" "$protection_pin" "$display_pin" "$lifecycle_pin" "$smp_pin" "$source_pin"
receipt_pin=$(sh mk/verify-metadata.sh hash-file "$root/aether-boot-v2/receipt.kv")
sh mk/aether-boot-v2.sh verify "$root" "$receipt_pin"
```

Each pin is lowercase SHA-256. Initialize a fresh private root with the existing
`make -f mk/pkg.mk ROOT="$root" init-root` contract first. The source pin binds
producer-supplied provenance; it does not prove source-to-binary correspondence
by itself. Keep the receipt pin outside the bundle through an explicitly trusted
handoff. Verification binds both the exact receipt and payload inventory.

Format `aether-boot-handoff-v2`, profile `aether-m4-five-v1`, records target,
source inventory digest, each named artifact's hash/size and fixed
`source_authenticity=not-proven`, `service_activation=unsupported`. The bundle
contains receipt.kv, manifest.tsv and exactly five regular files under boot/.
Kernel header, flat-image bounds and lifecycle v1 envelope are checked; only
consuming target tests establish semantic compatibility of flat modules.

From the matching Aether checkout, consume the staged files explicitly:

```sh
python3 scripts/image.py "$bundle/boot/aether" "$output/aether.iso" "$bundle/boot/protection.bin" "$bundle/boot/display.bin" "$bundle/boot/lifecycle.bin" "$bundle/boot/smp-supervisor.bin"
python3 scripts/emulator.py smoke "$output/aether.iso" --cpus 2
```

The current isolated source snapshot passed `AETHER FAULT RECOVERY PASS` and
framebuffer validation. [Evidence](evidence/boot-v2-2026-09-05/results.json) binds
source inventory, receipt and all inputs. This closes the older module-set
transport mismatch for these exact bytes. It is not a general loader/service ABI.

Tests: `sh tests/aether-boot-v2.sh`; the ordinary `sh tests/check.sh` includes this
new test alongside unchanged v1 cases. Missing/changed/swapped inputs, malformed
lifecycle fields, bad receipt pin, extra files/links and publication failure are
rejected. Failed staging leaves no accepted bundle; existing bundles are retained.
Wrong usage exits 64, operational failure exits 1, documented success exits 0.
These new exits do not alter any legacy helper contract. Single-writer private-root
assumptions remain; hostile filesystem races and power-loss durability are unproven.
