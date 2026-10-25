# M3 third slice: statically granted cross-core endpoints

Each pinned worker owns a three-slot endpoint table inside its local Core. Boot
installs request, reply, and readiness grants. Handles identify local slots;
CPU identity comes from interrupt routing, never a user argument. The immutable
slot binding selects a queue and send or receive right. Handles from the peer's
namespace, unpopulated slots, and wrong rights fail before queue access. These
bootstrap slots are never reused or transferred; stopping a worker disables its
whole table. Dynamic derivation, remote revocation, and restart are later work.

The register-only int 0x80 ABI uses RAX=1 send or 2 receive, RDI=handle,
RSI=payload; RAX returns 0 success, 1 invalid handle/operation, 2 denied,
4 full, or 5 empty. RDX returns a received word or zero. Three four-word SPSC
queues have fixed producer/consumer CPU bindings. Payloads convey data only.
No caller-supplied destination, sender identity, pointer, or transferred handle
is interpreted as authority. Full sends and empty receives change nothing.

The readiness endpoint makes backpressure testing deterministic without kernel
scheduling policy: the AP fills four reply slots and verifies a fifth send fails,
then sends readiness. BSP waits for readiness before consuming those four words.
The workers then exchange 100 ordered requests and computed results. Both check
invalid handles, peer-namespace handles, and missing rights. Nonblocking retry
loops remain subject to the existing local timer watchdog.

A fixture-only completion operation (RAX=0, RSI=120/130 for BSP/AP) validates local
successful send/receive counts and observed denials before returning to the
register-preservation loop. It grants no resource access. After communication,
the AP faults on supervisor MMIO and BSP must continue advancing. Acceptance
requires both completed IPC phases, the expected fault, and post-fault progress.
A corrupted expected result must fail the emulator test.

This slice reuses the kernel-probe request/reply queues after they drain and adds
one readiness queue. The [mapping slice](M3-MAPPINGS.md) places them on dedicated
supervisor RW/NX pages and removes old aliases and inherited direct mappings.
This does not establish isolation between compromised kernel instances.
