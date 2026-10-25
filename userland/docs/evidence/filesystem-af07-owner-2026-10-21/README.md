# AF07 operational owner input — UL-082, 2026-10-21

Aether's current handoff clears the selected AF07 service positive/failure gates.
The old operational owner still selected AF06/rights15. The new separate
[Rust owner](../../../experiments/filesystem-service/launch-metadata-owner.rs)
selects the exact qualified AF07 entry and rights31 without changing that owner,
its executable, or either service's sealed bytes. [Exact next engine/consumer
handoff](../../proposals/FS-AF07-OPERATIONAL-OWNER.md), [review](review.md).

The owner preserves main/callback,136-byte launch state,72-byte result, inherited
native holders, trusted dataset/identity, sole live SPA/UTC and separate context/
endpoint/drain/export/lifetime obligations. Added fail-closed result checks reject
impossible clean progress and empty-request disconnect. Contradictory final phase
evidence cannot transfer endpoint ownership back after a service report.

Eight actual-owner host tests and nine compiling omissions pass; five old AF06
owner cases pass separately. Tests cover fixed provisioning/METADATA16, every
cleanup phase/unknown bit, malformed bootstrap/callback, startup ownership,
service errors/progress/close/readiness/disconnect and real exit retention.
Native x86-64 Rust and default Clippy/format/warnings, exact C/Rust ABI/packed
rejection, symbol-only matched/old-service and duplicate-owner controls pass.
The symbol-only C doubles are not executed or delivered as an engine. The artifact
is a relocatable object, not a linked executable or native operational witness.

First preparation attempt failed an unjustified Rustc-versus-Clippy byte-equality
expectation; both compilers passed, but emitted different code. Retain both hashes/
logs and ship the Rustc object explicitly. Native codegen-units is now explicitly1;
default Clippy remains a separate source check, with no byte-equivalence promise.
Actual minimum/current Python artifacts and final quality gates are recorded in
summary.json, as are any further attempts. No native failure/guest/retry occurred.

875 current producer input hashes match the passing provider receipt at intake;
that identity check is not an independent replay of its12 native oracles. Preserve
the older timeout and consumed disposition. Pin/source/command/environment/
cleanup evidence and verified compact disposal remain local; no copied engine/
SDK, sibling edits/messages, altered release pins or new guest limits.
Matching Aether AF07 engine link/intake/fit/qualification, then sys-init exact
replacement consumption, remain required. All old seals/executable stay selected.
