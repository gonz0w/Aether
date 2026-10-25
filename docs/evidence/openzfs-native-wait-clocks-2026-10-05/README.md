# Checked OpenZFS wait-clock callers

2026-10-05,R1-03. [Before-change contract](contract.md) and
[source review](source-review.md) delimit the private C port and evidence.
The full engine remains unexecuted and unavailable for startup.

The two CV wait callers now compare absolute deadlines before subtraction and
use checked realtime with overflow-safe deadline addition. Expired/zero/negative
inputs retain -1; mutex owner clearing/restoration and wait-result handling remain.
The tpool idle-time block checks its actual realtime read, fields and linger addition
before use. Only two actual source/object positions change; checked inline header,
selected queues, SDK, kernel, ABI, quotas, pins and companions remain fixed.

The previous checked engine baseline relinks byte-identically. Two fresh original
objects reproduce exact bytes before replacement. Final ELF4,384,544 bytes/1312
initial pages/4-byte TLS keeps1/1/1/1 selections, no observer dependencies or static
relocations and the same two unresolved discovery hooks under strict whole-object
linking. Both current loader geometry and W+X/TLS denial models pass.

All53 final host cases pass: error/expiry/sign/fraction, tick/relative/absolute
conversion, carry/overflow/maxima, timeout/error/success and mutex-owner restoration.
Three actual old-source controls accept poisoned failed reads instead of125.
Host tests compile literal adapted functions and the tpool clock block, with explicit
signed64 musl tick/time semantics. Clock/wait models are test-only and never linked
into the engine. They do not qualify actual waiting, worker scheduling or UTC.

Six fresh native cases pass with the unchanged SDK: three real unavailable-clock125
cases and three no-clock expiry/zero cases that retain actual memory/TLS/64-yield/
24-byte-output/terminal witnesses. A test-only fixed lbolt isolates the CV caller;
it is not a native monotonic provider. No modeled native timed wait is counted as
working blocking/progress. Full137 host/pin/workflow/scoped checks pass. All failed
and narrower attempts remain; all selected/archive bytes read back before only
verified owned duplicates and temporary redirected logs are removed.

Next provide real calibrated monotonic/required UTC and actual musl/native timed
wait/delay semantics, then scoped resources/CPU/identity/config/entropy/volume,
production helper admission, native heap/ARC/TLS and remaining feature closure
before engine startup/fini/restart and Rust filesystem/packages/R1. The inherited
poll-based delay still ignores unsupported outcomes and remains unavailable for
engine execution; this scoped correction does not claim all timing paths are safe.
Independent SDK/reader/consumer and wider SESSION acceptance remain separate.

Private evidence recipes, requiring a fresh absent owned output/attempt tree:

```sh
python3 docs/evidence/openzfs-native-wait-clocks-2026-10-05/setup.py
python3 docs/evidence/openzfs-native-wait-clocks-2026-10-05/build.py 2
python3 docs/evidence/openzfs-native-wait-clocks-2026-10-05/components.py
python3 docs/evidence/openzfs-native-wait-clocks-2026-10-05/host.py 3
python3 docs/evidence/openzfs-native-wait-clocks-2026-10-05/native.py 2
python3 docs/evidence/openzfs-native-wait-clocks-2026-10-05/geometry.py
python3 docs/evidence/openzfs-native-wait-clocks-2026-10-05/inspect.py
```

These are retained experimental recipes, not supported developer entry points.
Original one-shot checks.py/archive.py require all retained attempt records; use
fresh receipts for reproduction and never overwrite this sealed packet. Subprocesses
are bounded180 seconds; QEMU30 seconds with3-second teardown. Upstream-derived
source/test slices retain CDDL notices/style; new original tooling/probes are
BSD-2-Clause. No dependency, public interface or normative shared standard is added.
