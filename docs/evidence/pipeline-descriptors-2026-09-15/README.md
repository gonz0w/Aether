# Two-pipe descriptor transitions — 2026-09-15

The private adapter now prepares seven descriptor bindings and publishes local
fork/exec, copy readiness/failure and confirmed terminal changes atomically across
two pipe objects. It recomputes the descriptor plan and checks current holdings
and generations. Fork preserves CLOEXEC aliases; exec removes only the replacing
caller's last filtered alias. None generation requires no local endpoints and
permits another caller's active object or a pipe not yet created.

## Review and authority

The [preimplementation contract](../../NATIVE-SHELL-STARTUP.md#two-pipe-descriptor-transitions--2026-09-15)
records O-02–04, I-01/03–06, E-01–06 and SE-01–05, affected owners, forbidden
partial effects and test selection. The owner applies changes to a bounded copy
of the pair and publishes only after both succeed. This removes rollback logic
that would otherwise need to restore discarded FIFO bytes. No extra persistent
ledger, heap, service, unsafe code, kernel operation, resource limit, dependency,
sibling or released-pin change. Snapshot copying adds stack work; its native
integration budget remains to be measured in the eventual owner profile.

The enclosing owner still authenticates streams and snapshots, quiesces I/O,
validates native image admission and observes exact readiness/terminal evidence.
These local functions do not deliver frames, grant native authority or implement
a cross-service transaction. Userland owns SDK intake; sys-init owns supervision.

## Qualification

- 60 Rust executions pass: 47 distinct tests and 13 descriptor tests compiled
  through both module contexts. Five new semantic cases cover CLOEXEC across seven
  bindings, atomic failed exec with preserved bytes, partial staging/readiness/
  terminal rejection, malformed/count/authority rejection, and fork before second
  pipe creation with known failure, retry and exact terminal cleanup.
- A deliberately non-atomic implementation compiles, then fails both named exec
  preservation and fork-staging tests. Sources, binary and failing logs remain.
- All 104 host checks, required Zig/pin checks and x86_64-unknown-none no_std
  compilation pass. Target compilation is not execution of the new transitions.
- All 21 selected existing dash-pipe native cases pass on 269 frozen inputs.
  The selector and exact case list are retained. All 208 generated baseline
  ELF/raw images are byte-identical. The 485 omitted full-suite images are listed;
  full matching connections/runner coverage is not claimed.
- Formatting, workflow, standards and final snapshot checks pass.

The initial collection script assumed the focused run built every full-suite
image and failed on missing copy-inherit-close.raw before archiving or deleting
anything. collect-native-attempt-1.py and collection-attempt-1.json retain that
failure. The corrected collector compares the actual intersection and records
missing images explicitly. No runtime implementation failures occurred.

## Replay and preservation

```sh
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 -m unittest discover -s tests -p test_pipe_owner.py
rustfmt +1.98.0 --edition 2024 --check user/native-connections/pipeline.rs user/native-connections/pipe.rs user/native-connections/exec_fds.rs
python3 scripts/check_workflow.py
python3 docs/check-standards.py
```

qualify.py records direct Rust compilation and semantic controls. focused-selector.py
selects the 21 existing cases from launch_smoke.py with the pinned SDK and tool lock.
Replay commands in fresh output roots; do not overwrite this sealed evidence.
sources.json/tar.gz preserve all native runtime inputs; review-inputs also preserve
host support and documentation. checks.json and native-results.json record tools,
commands and results. Binary/native archives are verified against every original
before removing only exact duplicate generated outputs. SHA256SUMS seals the
packet; archive manifests verify members. Prior sealed evidence remains unchanged.

## Remaining work

Wire these private transitions into native descriptor dispatch, copy/admission,
pending requests and completed reply cleanup. Add the reviewed opt-in worker and
channel capacity; execute the unchanged pipeline and early-reader scripts.
Full matching connections/runner and independent SDK/userland acceptance remain
before the next handoff. Persistent filesystem/OpenZFS, package execution,
recovery gaps and sys-init R1 assembly remain open.
