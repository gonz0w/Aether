# Client descriptor preparation — 2026-09-10

The client now checks its private descriptor state before sending the 96-byte plan
or invoking native freeze. The 16-slot scan requires boolean presence, canonical
absent entries, in-range bindings and only FD_CLOEXEC flags. A bounded local count
array must agree with duplicate counts. The three admitted streams must remain live
with exact parent lifetime references, roles and rights. Transport must be initialized,
unpoisoned and have distinct nonzero endpoints. Binding bounds are checked before
array indexing. Owner and kernel authority checks are unchanged.

All 83 connections and five launch cases pass, plus 98 Python host tests and
Zig/pin/workflow checks. Nine invalid preparations cover presence, flags, binding
range, dirty absent entry, duplicate count, dead binding, widened rights, stale
reference and poisoned transport. Each returns source78 without plan bytes. The
owner observes termination and empty output, checks the vacant child identity and
both remaining channel slots, then closes the known idle backend handles and
observes backend17. Three generations produce six reclaims with no slot2 admission.
This preserves the existing copy-enabled completion count and exercises all three
admitted generations of spare-channel reuse without relaxing a kernel check.

Ignoring a duplicate-count validation failure exposes plan bytes and rejects
owner2010 before reclaim. The serialized table alone looks normal in that control,
which demonstrates why owner-only validation is insufficient for private counts.
A deliberately leaked reservation produces source78 then owner2011 when the spare
capacity check fails. Both controls require zero reclaims. No failed attempt occurred;
connections-suite-jopggm3w passes on frozen runtime sources.

The [pre-code selection](../../NATIVE-SHELL-STARTUP.md#client-descriptor-preparation-selection--2026-09-10)
records ownership, forbidden outcomes, test selection and simplicity tradeoffs.
One small validator and stack count array avoid a new wire schema or FD service.
Client consistency does not constitute authority: owner-side exact snapshot checks
still precede reservation and kernel access checks remain. No kernel, backend, shared
adapter, command-source, pool, dependency or unsafe-boundary change is introduced.

All previous inheritance cases pass with validation enabled. The backend image
matches the preceding slice byte-for-byte; 22 older raw connection payloads match
outside 48 fresh entropy bytes. Maximum owner size remains 5,880 within 8,192. Prior
full 431-command/M4 runtime evidence remains historical. No sibling sources or
released standards pins changed.

The scope remains three live streams in a one-context fixture without custom signal
delivery. Signal-masked preparation/restoration, arbitrary open/closed descriptor
sets, installed SDK fork/exec/wait and independent consumer acceptance remain open.
This does not claim validation atomicity against handlers, full dash or R1 readiness.

Timings retain exact commands, UTC timestamps and exit status. Reports bind source,
tool and SDK identities. The collector verifies the preceding packet, frozen inputs,
pinned simplicity snapshot and archive readback. Native artifacts retain musl
notices. Formatting, compatibility and final checks have separate receipts;
manifest.json seals this packet.

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --connections \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/launch_smoke.py \
  --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku \
  --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
```

Archive readback verified 225 source files and 1,548 native target artifacts.
All final suites met their documented review budgets.
