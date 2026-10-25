# Masked inheritance preparation — 2026-09-10

The inherited-stream client now holds the existing all-maskable-signals guard
across descriptor validation, plan publication, native freeze/copy, libc and endpoint
rebinding, and final completion. It queries the held mask at selected boundaries
and restores the exact saved mask before application I/O and returning errors.
Private saved state is copied into the child. Nested descriptor guards preserve
it; stopped clients do not resume. Existing fail-closed mask-leave behavior remains.

All 91 connections and five launch cases pass, plus 98 Python host tests and
Zig/pin/workflow checks. Four nonzero SIGUSR1/SIGUSR2-mask cases cover success,
validation rejection, pre-copy rollback and bad-receipt recovery. Four deliberately
broken controls omit entry or rejection restoration (source79/owner2010), parent
restoration (source79/owner1950), or child restoration (child79/owner1950). They
require the exact terminal ordering and zero reclaims. All prior inheritance
cases retain their lifecycle oracles. No failed attempt occurred.

The [pre-code selection](../../NATIVE-SHELL-STARTUP.md#masked-inheritance-preparation-selection--2026-09-10)
records ownership, forbidden outcomes, test selection and simplicity tradeoffs.
The change reuses the existing mask primitive without new kernel operations,
wire formats, services or dependencies. Only the C client and harness runtime
sources changed from the preceding preparation packet. Existing synchronous
mask pointers remain stack/private storage; no pointer escapes.

The kernel still rejects copying with custom signal actions or threads. These
are mask-state witnesses, not handler delivery or pending-signal acceptance.
The next work must specify that copy contract before implementing its kernel/SDK
prerequisites. Arbitrary descriptor sets, installed fork/exec/wait and independent
consumer acceptance remain open. Full dash and R1 are unfinished.

The backend image matches the preceding packet byte-for-byte. All 22 older raw
connection payloads match outside their 48 entropy bytes. Owner images remain
at most 5,880 bytes within the 8,192-byte limit. Kernel, Rust owner, shared adapters
and command sources are unchanged; prior 431-command/M4 execution remains
historical. No companion repository or released standards pin changed.

Timings retain exact commands, UTC timestamps and exit codes. The collector
verifies the previous packet, frozen source hashes, pinned simplicity snapshot
and archive readback. Native artifacts preserve musl notices. Formatting,
compatibility and final checks have separate receipts; manifest.json seals the
packet. Runtime changes are retained in runtime.patch.

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --connections \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

Archive readback verified 225 source files and 1,684 native target artifacts.
All final suites met their documented review budgets.
