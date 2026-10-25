# UL-062 first parser workload plan

Scope: unchanged runner-parse.c on macOS arm64 with pinned Clang 21.1.8,
ASan+UBSan, original semantic controls and deterministic single-byte mutation.
TD-01–05, TC-01–03, TE-01–04, CC-01–04, CP-01–03 and E-01–08 apply.
Original work is BSD-2-Clause; existing LLVM and Apple SDK terms remain intact.
No new dependency, native interface, package/service change or release pin.

Before running: hash compiler against existing libc evidence, snapshot sources,
record resource runtime and host SDK identities. C17 strict diagnostics, O1,
frame pointers and address/undefined instrumentation; no recovery or suppression.
Each compile/run uses the existing owned process helper, explicit cwd/environment,
30-second timeout and 16 MiB per output file. Pure workload uses fixed-size stack
objects, no children, network, filesystem or input-driven allocation. ASan runtime
memory is not hard capped; peak RSS budgets and wider resource metrics remain open.

PXE-01: existing parser controls pass under both sanitizers.
PXE-02: three fixed valid records, every byte replaced with all 255 other values
(171360 cases), plus all 224 short lengths and one long length per seed (675).
Oracles: unchanged rejected output; accepted carrier round-trip byte equality;
selector non-publication or bounded owned child arguments and exact environment.
Each known valid seed must launch. Mutation index and seed identify failures.
PXE-03: reserved-byte rejection bypass must fail the round-trip oracle, exit 90.
PXE-04/05: isolated heap out-of-bounds and signed-overflow canaries must produce
specific sanitizer diagnostics and nonzero exits, with complete process cleanup.
A generic crash, timeout or compiler failure cannot satisfy those controls.

Commands: python3 -B experiments/command-runner/check-parser-extended.py; repeat
on local Python 3.10.21. Run pinned clang-format dry-run on new C, quality gate
and whitespace check. Record elapsed time, exact argv/env, source/tool/runtime
hashes, cases, binaries and process cleanup. Keep all failed and passed attempts.
The fixed workload has no random seed, coverage feedback or minimizer. Failure
coordinates reproduce a one-byte case; general fuzz minimization, transport stress,
static analysis, native compensation and independent technical review remain open.
This slice does not close UL-062 or claim extended-suite/release readiness.

## Explicit partial-mode amendment before qualification

The original combined instrumentation run timed out in the first control, both
inside and outside the sandbox. Both attempts remain retained with exact sources
and plan. This matches the earlier empty-main ASan limitation recorded by UL-058;
its root cause is not established. Add --ubsan-only as an explicit partial run,
never an automatic fallback. Default still requires ASan and cannot pass a timeout.
PXE-04 remains blocked; PXE-01/02/03/05 can be qualified with UBSan. Leak detection
is disabled and symbolization omitted to avoid external symbolizer processes;
no leak-check or full SDK provenance claim is made. The SDK path/settings and
sanitizer runtime hashes identify the selected host inputs, not all system files.
