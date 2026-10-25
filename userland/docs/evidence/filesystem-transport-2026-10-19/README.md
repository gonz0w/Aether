# UL-082 bounded service transport — 2026-10-19

The [implementation](../../../experiments/filesystem-service/service.rs) adds a
private versioned connection loop with lookup/read/write/stat/close/disconnect,
complete-frame readiness, one nonempty provider call, alias visibility, partial
input rejection and context retirement after any lost reply. The native entry
uses the pinned synchronous channel traps with retained bootstrap bindings;
the kernel must still authenticate their holders. No request carries authority
to attach, choose peers/objects/UTC, or widen provisioned rights.

See [exact protocol/owner handoff](../../proposals/FS-SERVICE-TRANSPORT.md) and
[change review](review.md). Eleven host transport/policy tests and four actual
Rust-entry/typed-C-fixture tests pass; seven compiling semantic omissions fail
assertions as intended. Every short chunk size1..16 and partial EOF0..63, transfer
stall/oversized count, stale/version/rights errors, alias EOF, one-write/error
budget, reply loss/committed/unknown results and context-before-endpoint cleanup
are exercised. Rustfmt/default Clippy, no_std native panic-abort object generation,
ELF/symbol checks and C size/alignment/offset/packed rejection pass. Native service
launch, endpoint enforcement and original-engine persistence are **NOT RUN** for
this composition. The C fixture is injected, not original OpenZFS.

Producer receipts captured in inputs.json report successful native Rust write/
fresh recovery and eight finite C writes. They supersede historical timeout/
callback selection notes, not independent consumer acceptance here. The current
actual builder guard still rejects writable+IPC; its isolated AST-extracted guard
is exercised without importing or executing sibling builders. Current intake
only accepts the old probe seal. The new native object is a concrete review input,
not a launchable executable, accepted SDK or completed operational service.

All attempts stay retained. Preparation failures: first checker expected11 tests
while10 existed (all10 passed); first retirement omission failed compiler warnings
instead of behavior; first host entry link mixed abort-library with unwind-test
strategy. The corrected host test library uses unwind as required by the host test
harness; native code remains panic-abort. An unmatched patch was rejected without
mutation. Early attempts retain hashes/commands/logs; full original source snapshots
were not captured for every early attempt, a provenance limit. Final runs snapshot
every compiled local source and checker. No native failure/retry occurred.

Results/attempts, sealed candidate and verified compact retention are recorded in
summary.json and retention.json after final checks. Compiler/resource/native Rust
libraries are pinned; dynamically loaded host libraries/system SDK headers are not
a complete hermetic host dependency closure. No physical disk saving, performance,
native stack/peak memory, POSIX, durability or independent human review claim.

Postflight owner drift: current builder began separate C transaction-lifetime work during this turn. The full-file identity check rejected that drift; captured postflight sources show the selected service exclusion guard unchanged and re-exercised. Old probe intake/current STATE remain exact. See postflight.json; no silent repin, new lifetime acceptance, Rust call-bound lift or native retry.
