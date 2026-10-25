# Serialized file inheritance v1 — UL-007/081/082

This additive local library API addresses the file-view ordering mismatch in
sys-init Decision0201/BG-069. It does not assign a staging opcode, change the
kernel, implement native fork or establish affected-owner agreement. The existing
`inherited_child` API still requires its documented native frozen-parent window.
The new API is an explicit alternative for an owner that serializes admission.

## Local contract

`ProcessFiles::copy_inherit_serialized_v1(parent, target, observed_parent, copy)`
holds one exclusive mutable borrow of the existing file ledger from preflight
through a synchronous callback and local binding publication. It adds no fields
to ProcessFiles, second ledger, heap allocation, source handle or native grant.
Safe Rust callbacks cannot access that ledger, including other process views.

Before calling `copy`, the library checks the actual current parent key, shell1,
canonical target child2–4, actual-parent label, empty child record and next epoch.
Preflight failure returns BeforeCopy without invoking the callback. The target
is the dispatcher-reserved expected instance; canonical syntax does not prove
native admission or authority. The callback must return authenticated native
observations, never synthesize a successful child from those expected labels.

| Callback observation | Local result and obligations |
| --- | --- |
| Refused(error) | Confirmed no native child. Preserve parent bindings, offsets, flags and generation; return the exact error. Dispatcher still owns known staged-holder rollback and token-matched thaw, including the actual parent/owner error distinction. |
| Copied(identity, parent_pid), matching target/parent | Revalidate and copy exact bindings/flags into the child using the existing shared-description algorithm before releasing the borrow. Shared offsets and final-close lifetime remain shared; per-process flags separate. No backend lookup/copy or descriptor remapping. |
| Unknown(error) | Return exact unknown observation and retire admission once via the existing source abort path. Preserve process record occupancy and do not publish a child. No retry, native thaw, rollback, termination or reclaim is performed. |
| Copied with unexpected identity/parent or failed local publication | Return Unbound with the actual observation and local error. Retire admission; exact native child/reservation/endpoint settlement remains caller-owned. No claim that retirement terminates a native process. |
| Callback unwinds | A stack guard retires admission during unwinding, retaining process occupancy. Native panic-abort still requires owner fail-stop/watchdog/recovery; no unwinding or bounded duration is promised on target. |

## Ordering argument and remaining owner boundary

There is one ProcessFiles and one source. Before the callback, preflight is pure.
During the callback, the mutable borrow excludes all safe ProcessFiles access;
no binding, offset, flag, generation or view in that ledger can change through
its API. On a matching confirmed copy, the local clone executes before the borrow
ends. Therefore the clone sees the same local file-view state as at callback entry,
even if the native parent resumes inside the callback. Later parent FD requests
must be queued until this method returns. Subsequent reads/seeks intentionally
change the shared descriptions' offsets in both views, as required by fork.

This is a local safe-Rust ownership argument, not synchronization of remote native
processes or arbitrary aliases to an underlying Channel. The dispatcher must own
the sole file ledger/source and prevent any out-of-band mutation of that source.
It must also exclude parent/child stream admission and source-view bypass until
all required file and stream views are installed; the library cannot prove that
separate owner policy. It must snapshot/validate the tagged128 map and pipe history
while the parent is parked, authenticate the exact nonzero freeze token, reserve
channels/holders, perform bounded native copy and preserve native obligations on
known refusal/unknown outcomes. It must not reread mutable parent memory to change
child initialization after copy. A signal mask alone does not enforce this rule.

The new API removes the need for a native frozen-parent interval specifically
around this local file-view clone when the owner meets that serialized contract.
It does not relax the old API or select this alternative on sys-init's behalf.
BG-069 still needs matching versioned wire and affected-owner agreement, exact
source/stream exclusion and child-only TLS/auxv/copied-context/generation/history
transition. BG-070 must compose the transaction, full shell link, resource fit and
native positive/refusal/unknown/continued-parent/readiness/wait/cleanup witnesses.
There is still no implementation of __aether_fork_stage here. Immutable exec and
public dup2 compatibility remain separate gates.

## Qualification

Run from the repository root using provisioned pinned tools:

```sh
python3 -B experiments/filesystem-service/check-process-descriptors.py
build/python-qualification/Python-3.10.21/python.exe -B experiments/filesystem-service/check-process-descriptors.py
python3 -B docs/quality/check.py
```

The process profile has26 tests:18 retained and eight new actual-library host
cases, with ten compiling semantic omissions (eight retained/two new). New cases
exercise queued parent close/open after confirmed copy, independent flags/shared
offsets/last close, full13-descriptor table across three children, bad/busy/stale
preflight, exact known refusals and unconsumed generation, unknown/no replay,
unexpected confirmed observations and callback panic. An actual rustc compile-fail
case attempts callback reentry into the mutably borrowed ledger and must fail with
a borrow diagnostic. The new tests use the existing actual AF07 handler/Owner
with synthetic storage; native-copy observations and parent queue are simulated.
This does not execute a native copy or prove real stream-dispatch serialization.

Strict Rust2021/rustfmt/default Clippy/unsafe denial and generic target
x86_64-unknown-none rlib are separate build checks, not a monomorphized owner
runtime, whole resource measurement or native acceptance. Prior sealed process,
libc and other evidence stays immutable. See the dated qualification record.
