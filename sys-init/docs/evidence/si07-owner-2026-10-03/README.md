# Sys-init ABI22 sustained command owner — 2026-10-03

Four fresh native consumer cases pass using the existing sys-init paired owners.
The positive completes five useful bytecount cycles, exact output/readback and
ordered command/runner/backend terminals, 3045 total ticks, 3004 idle ticks,
15 reclaims and authorized halt. This closes the first consuming integration
slice of BG-067; it does not complete a production init or all SUSTAIN-01–06.

## Cases and bounds

| Image | Native oracle | Code bytes | Inspected stack bound |
| --- | --- | ---: | ---: |
| positive-2 | Five cycles; exact 0/0/17 terminals; stale query/close denied; UART closed before authorized halt | 10192 | 2696 |
| cohort-consumer | Backend identity mismatch; actual stop/terminal/cleanup, rejection before command admission | 10208 | 2696 |
| cohort-late-consumer | Mismatch after all three workers exist; stop/observe/cleanup clients before backend, before child-reference publication | 10240 | 2696 |
| exhausted-consumer | Private epoch 65536 rejects before any worker admission | 739 | 304 |

Bounds remain 16384 bytes code and 4096 bytes stack (4088 usable). Stack analysis
walks the linked control flow including fatal paths. All RIP-relative indirect
calls resolve to immutable memcpy/memset cells. The two register calls at
0x40123f/0x401250 use RBX loaded at 0x401238 from the memset cell; no intervening
RBX write exists and memset preserves that callee-saved register. This holds in
all three nontrivial linked images. No indirect jumps appear. The analyzer charges
both builtins at indirect calls conservatively. This is an inspection aid with
manual bindings, not formal verification, kernel-stack analysis or a benchmark.

Mismatch cases intentionally end at SI07 fixture failure after the explicit
cleanup assertions; they do not claim clean authorized shutdown. The late case's
oracle requires exactly one command-ready prompt, no ordinary worker-terminal
records, and the rejection-after-reclaim marker. Exhaustion's constant selected
epoch tests rejection, not 65535 executed cycles. No generic fault recovery follows.

## Implementation and review

success.rs keeps persistent backend/runner/command owners across five cycles.
The opt-in ABI22 path uses AERIO002/NIO2 and receipt family 0x7b, with private
epoch 1..65535 checked before admission. Full-width native cohort identity is
checked before each protocol publication; it is never truncated to the epoch.
Mismatch stops only actually owned workers, observes real terminal143/kind3 and
uses the existing explicit ownership cleanup. The normal path preserves protocol
reference retirement, backend EOF, actual terminals, reclaim and stale denial.
Snapshot-before-input followed by compare/park uses the producer event contract.
UART and final halt require their distinct kernel-enforced grants. Fixture startup
also checks denied grants, unsupported final action and busy halt.

The small sustained_owner.rs adapts the frozen producer's wait/input fixture
operations and adds sys-init paired-owner rejection cleanup. No new unsafe block,
dependency, syscall, shared ABI or release pin is introduced. Existing Native
adapter error/ownership rules remain authoritative; ambiguous errors fail closed.
No automatic effect replay or successful shutdown is reported after unknown cleanup.

Simplicity review: the simpler alternative is the producer's direct fixture owner;
it does not exercise sys-init's ownership/cleanup implementation. We reuse the
existing paired owners and a small opt-in helper instead of another lifecycle
framework. No obsolete compatibility path is removed now: five old ABI9 command
variants (positive, empty, fault, stop and stop-control) rebuild byte-identically.
ABI17 script sources are untouched. Extra test selection covers early and late
ownership, exhaustion, grant denial, stale handles and compatibility without a
new platform campaign. Existing host ownership/error tests remain required.

## Inputs and retained attempts

The preceding si07-intake packet pins the producer and v2 userland input set.
The new image replaces only the supervisor portion of its three-image envelope;
runner, bytecount and backend bytes are reused, not claimed source-rebuilt here.
consumer-sources.tar.gz retains the complete staged source used for this build;
consumer-sources.json and dependencies.json bind source and local boot dependencies.
All restored inputs were checked against the sealed producer execution/source or
available-artifact hashes before use. Mutable sibling reads supplied matching
bytes only during setup; no sibling file was modified. Original source archives
omitted assembly, embedded data and root build inputs; restoration is recorded.
The copied boot inputs were checked against sealed artifact metadata before the
successful build. This is ABI22 experiment evidence, not Distribution m4 conformance.

The first Rust build failed on missing embedded data and helper lifetime parameters;
its exact source/log is retained. The stack script initially assumed a memcmp
symbol that this linked image does not contain; stack.log retains that failure.
Three subsequent kernel build failures exposed missing assembly/toolchain/license
inputs and are retained as kernel-attempt1/2/3.log. An artifact-path lookup during
setup failed because a sibling generated path was absent; identical live source
bytes were then verified against the sealed artifact hash. None of these setup
failures booted a guest. Rust's library environment stays confined to Rust calls
through the retained shim; Zig and QEMU do not inherit it.

Final source comments and the opt-in late-control branch were followed by rebuilds
of all four raw and ELF images: all eight are byte-identical to those executed
and inspected. final-source-compatibility.json binds this correspondence. Commands,
serial/QEMU logs, exact raw/envelope/ELF artifacts and private ISO hashes are retained.
The ISO and firmware remain private under out; dependencies are pinned separately.
Drivers are dated evidence recipes with local paths, not a newly supported CLI.

## Remaining product work and standards

This is a five-cycle developer console fixture: r requests a fixed bytecount
cycle and h requests halt only after the fifth cycle. It is not authenticated
operator input, a general shell, indefinite uptime, or shutdown at every boundary.
Next BG-067 work is a small request loop permitting halt at each quiescent boundary,
then focused idle/input/partial-reply and cleanup-failure controls. Preserve the
policy that outstanding effects settle rather than being replayed. Independent
userland replay and full SI-07 disposition remain distinct; broader v1 service
configuration and assembled product/release review remain open. No external
blocker is established for that local follow-on.

Applicable shared requirements: O-01–05 ownership/authority; I-01/03–06 bounds,
identity, explicit unsupported behavior and effect handling; E-01–08 pinned inputs,
private staging, exact target evidence and retained failures. Distribution ID-01
limits the console claim; PF-01–03 limits measurements. Existing Experience internal
fixture-output exception covers the preserved SI07 markers and ASCII-only output;
no operator renderer conformance or new exception is claimed. All released pins
and historical packets stay fixed. Quality inventory and current planning link
this packet. No independent review or release authorization is claimed.

All ten development gates pass in run-vnswqsuh with checked sources unchanged;
validation.json and validation/ retain the result. git diff --check passes.
sha256.json seals this packet and excludes only itself.

Final source comparison against the frozen final-sources.json differs only in
success.rs plus the explicitly added sys-init modules. The producer's finalized
sustained.rs differs from its earlier positive-run source map; we retain the final
archive version unchanged. The consumed local helper is sustained_owner.rs, whose
final raw/ELF identities and fresh native results are recorded above.
