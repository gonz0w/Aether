# Bounded pipeline participant ownership — 2026-09-15

The shared pipe core now supports its existing parent/one-child shape and a
parent/three-child shape for the next pipeline experiment. Pipe remains the
two-participant type with the existing API/wire behavior; PipelinePipe selects
four participants. The FIFO, endpoint retention, exec, terminal cleanup and
retirement logic have one implementation. No native profile selects PipelinePipe
yet, so this packet does not prove native multi-stage pipeline execution.

## Requirement and capacity review

The [preimplementation review](../../NATIVE-SHELL-STARTUP.md#pipeline-participant-ownership-and-capacity-review--2026-09-15)
records requirements, forbidden outcomes, owner boundaries, standard clauses and
selected tests. The unchanged pipeline script needs a shell, printf child, two
helper children and the existing backend: five workers plus supervisor, two pipes
and seven bindings. The current fixture supplies three workers plus supervisor,
six request/reply channels and five bindings. Native execution threads are not
extra independent process slots. A future profile must review five workers, ten
channels, memory and PID/handle encoding without silently widening old profiles.

Participant slots 1–3 identify owner-local authenticated connections, not kernel
worker slots, descriptor bindings or pipe object IDs. Legacy Caller::Child maps
to participant1. Application request bytes cannot select caller authority.
Two simultaneous objects still need distinct identities and authenticated routing;
that work is not supplied by this core and the existing equal-generation handle
format does not distinguish them.

O-02–04, I-01/05/06, E-01–06 and SE-01–05 apply. Parameterizing the existing owner
is simpler than duplicating the FIFO/recovery code or maintaining an aggregate
holder ledger beside another authority ledger. Only the existing two-party and
currently required four-party shapes are accepted. Capacity256, frame payload16,
pipe/peer generation bounds and old method signatures remain. Each object owns
its mutable state. No kernel, dependency, unsafe boundary, service, public SDK,
sibling, released pin or resource-limit change.

## Core qualification

core.log records all 34 Rust tests passing: the 29 existing tests plus five
multi-participant cases. They cover:

- EOF waits for ready and staged writers; a known failed copy drops only its reservation.
- EPIPE waits for the last reader; exec can drop endpoints but cannot add rights.
- Peer generation/reuse is independent; stale, reserved and out-of-range identities reject without mutation.
- Confirmed staged termination releases only the matching peer; old readiness and terminal records cannot affect another peer.
- Retirement waits for every holder and every pending frame slot, then zeroes storage before reuse.

Three deliberately broken copies in controls/ all fail the intended new tests:
ignoring holders after the first two slots, accepting stale peer generations, and
ignoring pending slots after the first two. controls.json records commands,
statuses and digests; failures are expected semantic rejections, not compiler or
infrastructure failures. model-artifacts.tar.gz preserves the passing test binary
and all three failing control binaries; originals were removed only after archive
and file verification. No unexpected implementation failures occurred in this step.

The ordinary host gate now requires 34 tests and explicitly instantiates the
four-participant constructor/request path for no_std. target_core.rs and
target-compile.json also instantiate all new transitions for x86_64-unknown-none;
target-core.o is compilation evidence only. host-first.log retains the initial
host pass before strengthening that target wrapper; host-test-before.py and
host-test-final.py preserve both support inputs. host.log records the final host
run: all 104 host tests pass. checks.json records formatting, workflow, standards and four simplicity
snapshot hashes.

## Native regression and replay

The focused selector runs all 21 existing dash-pipe cases from the regular harness;
focus-1.log records their pass on unchanged inputs. It does not add a native
four-participant workload. The full suite passes all 358 existing cases in
1099.04 seconds, below the 1800-second review ceiling, on 268 unchanged inputs.
connections.json and connections-results.json record the run; connections-traces.json
also verifies the existing consumer substitution and its two rejection controls.
Compatibility digests compare 693 previous ELF/raw images: 658 are byte-identical,
and the 35 changed pipe owners pass with a maximum size of 15,440 bytes, within
four pages. All client images are unchanged. These are native compatibility
regressions, not native four-participant pipeline qualification.

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/launch_smoke.py --connections --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
python3 scripts/check_workflow.py
python3 docs/check-standards.py
```

The direct core run used rustc +1.98.0 --edition=2024 --test on
user/native-connections/pipe.rs, then ran the binary with --nocapture.
The existing Python host gate records its compiler/run/target commands on failure;
no new public script entry point was introduced. AT-CONNECTIONS documents the
scoped host extension and native limitation.

attempt-1-sources.tar.gz and final-sources.json preserve the frozen runtime/support
inputs. Separate final review/support inputs are in review-inputs.tar.gz. Native
reports record SDK/tool identities; replay requires those external pinned
prerequisites. The focused/full reports, artifacts and cleanup receipts are
preserved. Full and focused archives were checked against every original file
before removing 4,485,065,201 redundant generated bytes. Cleanup receipts name
only those two generated roots. The four model binaries were likewise verified
before removal; their archive remains. The first review-input packaging attempt referenced a nonexistent build.zig.zon;
review-packaging-attempt-1.json records that tooling failure. The corrected review
archive uses the actual build.zig. Runtime qualification was unaffected.
Prior sealed evidence remains unchanged.

## Remaining work

Define two-pipe object identities and authenticated routing, then the seven-binding
fork/exec adapter and an opt-in native capacity profile. Qualify simultaneous
children, both pipe lifetimes, native early-reader EPIPE and the unchanged pipeline
and early-reader scripts. Matching runner and independent SDK/userland acceptance
remain separate. Persistent filesystem/OpenZFS, package execution, recovery gaps
and sys-init R1 assembly remain open.
