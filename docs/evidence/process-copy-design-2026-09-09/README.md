# Bounded process-copy design selection

The local design in [NATIVE-SHELL-STARTUP](../../NATIVE-SHELL-STARTUP.md#bounded-process-copy-design--2026-09-09)
selects eager private copying with explicit self-freeze and supervisor-authorized
publication/cancellation. It records ownership, copied/reset state, fresh grants,
rollback, resource limits and native acceptance obligations. No operation numbers,
runtime implementation, consumer acceptance or released pin changes are claimed.

The review found implementation hazards in existing mechanisms: inaccessible and
vacant anonymous pages cannot be copied through byte(); addPage initializes image
ownership; State embeds physical page-table pointers and unrelated capabilities;
getppid currently names the direct launcher; native-runner-local chooses a different
reclaim count. These are limitations for the proposed fork path, not evidence that
the existing bounded contracts are broken.

The first native implementation is the copy primitive and isolation/rollback
witness. Libc grant/identity rebinding, transactional exec/CLOEXEC, parent wait and
unchanged DASH-argv follow. No shared production process-service owner is assigned.
This records the contributor's local review, not independent implementation review.

Validation: `zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`,
plus explicit simplicity snapshot hash verification. Host results are retained in
host.log. No fresh QEMU run was selected for this documentation-only change;
the prior helper packet remains the target baseline. sources.json and sources.tar.gz
retain the inspected inputs and final local guidance; manifest.json binds the packet.

All98 Python host tests and Zig/pin/workflow checks passed. The simplicity
manifest and four inputs match their adopted hashes. All205 runtime/build inputs
remain unchanged from the helper packet;230 inspected source files passed archive
readback. No sibling repository was modified.
