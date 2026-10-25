# Inherited-stream publication recovery — 2026-09-10

The local owner now recovers the parent after a copied child rejects its binding
receipt or completion message, or is explicitly stopped before receiving its
receipt. Child holders are released only after confirmed terminal state. The
parent retains its descriptor table, FD 10 with CLOEXEC, and original input
position; reads a/b and final backend closure demonstrate usable retained state.
This implements the bounded [pre-code selection](../../NATIVE-SHELL-STARTUP.md#inherited-stream-publication-recovery-selection--2026-09-10).

All 32 connections and five launch cases pass, plus 98 Python host tests and
Zig/pin/workflow checks. Each positive repeats two generations and six reclaims.
No failed format, build or native attempt occurred in this slice. The previous
packet's failures remain retained there without modification.

| Case | Required result |
| --- | --- |
| copy-inherit-receipt | Nonzero receipt byte31 rejects child251 before acknowledgment/application traffic; parent73 and backend17 recover |
| copy-inherit-completion | Invalid completion opcode68 rejects child251 before application traffic; parent73 and backend17 recover |
| copy-inherit-stop | Withheld receipt, native stop and exact status143/kind3 query before holder release; parent73/backend17 recover |
| copy-inherit-receipt-skip | Skipped receipt validation exposes acknowledgment traffic and rejects owner1961, zero reclaims |
| copy-inherit-completion-skip | Skipped child gate exposes application traffic and rejects owner1963, zero reclaims |
| copy-inherit-parent-skip | Application request cannot satisfy the waiting-parent probe; owner1962, zero reclaims |
| copy-inherit-stop-skip | An active child cannot satisfy confirmed-stop status; owner1964, zero reclaims |

The first two positives require ordered child2=251, parent0=73, backend1=17
terminal lines in each generation. Forced stop produces no normal child terminal
line; the compiled owner must query143/kind3 and only parent0=73/backend1=17 appear.
Each recovery retains the three backend bindings until the parent's last local
aliases close. No backend I/O is performed for the failed child. Probe69/reply70
is an explicit local conformance probe of the waiting parent wrapper, followed by
failure68; it is not a new production readiness or public errno protocol.

Runtime changes are limited to inherit-client.c, inherit.rs and the connections
branch of launch_smoke.py. Kernel/build and all other runtime source hashes match
the previous packet. All 22 prior raw connection envelopes match outside the exact
fresh entropy interval [32,80). The three earlier inheritance cases also pass;
their client wrapper changed intentionally to recognize failure completion.
The largest owner is 5,464 bytes within its existing 8,192-byte bound. No worker,
channel or descriptor pool, dependency, public SDK hook or kernel operation was added.

The prior 431-command/M4 results remain historical. They were not rerun because
this change is confined to the inherited-stream conformance client and its cfg-gated
owner; shared command adapters, kernel and other profile builders remain unchanged.
Full connections, launch, harness/host checks, exact mutation outcomes and the
scoped source comparison are the selected fresh coverage. Sources were frozen
through the qualified runs. No sibling files or released standards pins changed.

Pre-copy rollback, arbitrary descriptor-table preparation, missing/partial records,
shared uncertain backend outcomes and signal-aware preparation remain unfinished.
This is not full protocol coverage, installed SDK fork/exec/wait, pipelines, full
dash or release readiness. Independent consumer adoption and extended coverage
remain separate gates. The current clients are single-context with custom signal
delivery disabled; a public application failure return is not specified here.

Per-suite timing files contain exact commands, UTC start/end and exit status.
Source/report hashes, tool/SDK identities, binary/serial artifacts, formatting,
snapshot verification and compatibility comparisons are retained. The collector
verifies the previous packet manifest, final runtime inputs and archive readback;
manifest.json binds this packet. The extracted musl private headers and COPYRIGHT
are preserved without changes to upstream terms.

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --connections \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

Archive readback verified 225 final source files and
676 target artifacts. All selected suite durations were within
the documented review budgets.
