# Private native two-vector bridge

Pre-implementation contract, 2026-09-07. UL-067 prerequisite, not real Toybox
cat or musl stdio-loop acceptance. Userland owns the future libc adaptation;
Aether supplies this opt-in producer witness without sibling edits or new ABI.

Gather at most two valid borrowed vectors into a 16-byte stack buffer, preserving
order. Validate FD1/2, signed vector count, null metadata/data and aggregate
SSIZE_MAX bounds before any transfer. Pointers must designate readable objects;
this private synchronous single-thread helper cannot probe arbitrary pointers.
Zero length still goes through existing binding/rights validation. Existing
transport owns generation-scoped bindings and shared poison. Return confirmed
short counts or exact negative errors; turn nonempty zero progress into EIO.
Never replay an unknown transfer or send diagnostics after shared poison. Close
locally retires all three bindings; the owner reclaims after observed termination.
No allocation, global syscall hook, extra grant, concurrency or kernel change.

Forbidden: reordered/corrupted bytes, silent truncation, invalid input effects,
retry on EIO/EINTR, traffic after uncertain completion, stale alias reuse, skipped
cleanup, or treating this as actual fwrite/fflush/finalization coverage.

Select native copy, empty, short, write EIO/EINTR, malformed/cut write reply and
deliberate prefix/validation mutants. Existing Rust owner independently checks
bytes, positions, closes, two generations and four reclaims. Client controls
validate rejected arguments without channel calls and shared poison without
subsequent channel calls. Mutants must fail for named terminal/owner reasons.
Run host/pins/workflow, prior startup and full command regressions on final bytes.
Record all failed attempts before changes; freeze runtime sources during runs.
Foundation O-02–05, I-01/03/05/06, E-01–08 and local Development evidence/FFI rules
apply. Pins, budgets, UL-059 artifact and upstream SDK remain unchanged.

## Coverage boundaries

The native client reads eleven bytes at a time and splits each write at three
bytes. The short owner limits reads to seven and writes to three, exercising
vector-boundary advancement. All seven positive/error scenarios run through real
native channels; uncertain write replies can commit eleven bytes before the client
loses confirmation. The owner checks that prefix independently. Diagnostic
suppression is checked with actual channel-call counters, not a mock callback.

The bridge is not yet installed into musl. The current native cases do not cover
successful zero-length requests, gathering beyond sixteen bytes, a zero-progress
backend, arbitrary pointers, re-entry/concurrency or public stdio buffer state.
Those must be selected for the actual musl-loop integration rather than inferred
from these eleven-byte copies. Existing transport error validation is reused.
New original C/header and recipe use BSD-2-Clause; retained Toybox/musl objects
keep their recorded upstream terms. No new upstream source is imported.

## Results

First attempt passes all nine native cases: seven normal/error scenarios each
finish two generations with exact client0/1, backend17 and supervisor100/reclaimed4.
Corrupt-prefix rejects owner1505 after client0; missing-null-validation rejects
client117 then owner1501. Neither negative relies on a generic panic or timeout.
All four actual Toybox startup regressions, all211 command-runner cases and98 host
tests pass. Zig tests, all three pins, workflow31groups and Clang-format21.1.8
checks pass. No failed attempt occurred. Existing sources are byte-identical to
the preceding startup receipt; only the vector header/probe are new runtime files.

The default probe is24,952bytes, six load pages and4-byte PT_TLS. It uses no dynamic
memory grant. This is mapped-image evidence, not peak-memory or performance data.
No kernel, SDK, installed libc, release pin, UL-059 bundle or sibling changed.
Broader connections/inherited launch suites were not rerun: no shared runtime,
loader, profile or harness implementation changed; full command and startup
regressions cover the reused native envelope/transport path.

Reproduce the nine cases with `python3 docs/evidence/native-vector-2026-09-07/run-native.py`.
Run the prior startup recipe from its unchanged evidence path; run full commands
using `scripts/launch_smoke.py --command-runner --libc-build` with the exact SDK
and `--tools-lock` recorded in command-regression-timing.json. Run
`zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`.

`native-results.json`, `startup-results.json`, `command-results.json` and their
logs retain expectations, commands, hashes, whole-run UTC times and results.
`qualification.json` binds matching sources, SDK and the verified UL-059 bundle.
`final-artifacts.tar.gz` retains sources/, run-native.py and native/startup/command
outputs. ISO, installed boot duplicates and kernel.elf are omitted from that
archive; raw receipt artifact hashes remain. `archive-check.json` verifies every
archived source and the recipe. Per-command timestamps for the native recipe and
host/format command timestamps remain unavailable; whole native-run boundaries
are recorded, not retroactively invented. Independent review and extended testing
remain open as documented in DEVELOPMENT. This is bounded producer evidence.
