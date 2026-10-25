# Joined owner routing / code-fit checkpoint

BG-070 /2026-10-22. [Pre-code review](../../../sys-init/docs/decisions/0210-unified-owner-routing.md),
[contract](../../../sys-init/prototypes/native-filesystem-session/FORK.md),
[commands](../../../sys-init/prototypes/native-filesystem-session/README.md).
Implementation-agent review; no independent/native/ISO acceptance. All limits,
released/sealed pins and default compiler/link flags stay unchanged. No guest ran.

The new actual owner route joins FILE64/fork304/stream32 from the same Peer under
one admission before prefix read. FILE uses the unchanged real Connection/body/
delivery handler; fork retains the actual decoded sequence/capture; streams require
an explicit actual-owner callback. No successful default handler or guessed exec
wire. Zero-byte EAGAIN alone skips an idle peer without waiting; partial messages
remain closed and bounded. Workspace clears on return/host unwind. No framing
cache, extra queue/channel/worker/ledger/allocation or new unsafe operation.

| Selection | Result |
| --- | --- |
| Existing producer |35 tests/15 semantic omissions, borrow denial and strict host/native builds pass; exact source/library/tool hashes consumed/rechecked |
| Current owner components |46 tests:34 previous plus nine mixed-route and five legacy FILE cases; strict host/native builds, test Clippy and Rust2024 formatting pass |
| Mixed protocol schedules |464 truncated prefixes (FILE128 including padded name, fork304, stream32); actual FILE open/read/shared offsets/CLOEXEC then capture/copy; pipe factory/state and stale history rejected before copy; unknown/malformed/sequence/identity/generation; raw wait/count/budget/partial reply/once-only closes/unwind clearing |
| Multi-peer idle |Idle authenticated parent consumes no byte/wait/source effect; active admitted copied child on its own generation/channel then completes real FILE operation under the same owner |
| Semantic controls |Three publication omissions remain; new prefix-before-gate, wait-idle-peer and lose-fork-capture variants compile and fail their exact named assertions |
| Safe borrow controls |Actual rustc rejects escaping Peer's scoped mutable channel borrow and reentering owner during route callback |
| Initial joined core |18432 code before idle handling; first45 tests pass; not a full owner |
| Final joined core |18768 code against16384, largest observed fixed subtraction776; exit2 after host success, not native admission or peak-stack proof |
| Safe ICF |18768; no improvement |
| No jump tables / with safe ICF |18664 /18664; still fails |
| Machine outlining / with no jump tables |18544 /18424;25 outlined symbols each, largest fixed subtraction still776; helper calls are not free peak-stack space, and neither image executes |

No alternate flag is adopted: even the smallest probe remains2040 bytes over the
fixed ceiling, before complete native entry/control-loop/lifetime/exec/wait/shutdown.
The prior17440 independent roots omitted this actual same-channel join; this is
broader measured scope rather than a demonstrated runtime size regression. These
roots still do not prove every coherent complete owner must exceed budget.

Source/native/storage observations are injected on host. The actual linked shell
is not executed, its ABI30 mapped entry is not supplied by this core, the required
stream callback has no native owner caller in the measurement, and full native
copy/refusal/terminal/endpoint/resource settlement remain open. No Zsh/TTY/package/
runner/persistent ISO readiness follows. Keep implementation work local under the
existing ownership boundaries; don't reinterpret another folder as a blocker.

attempt-6.json is the final source/checker/component receipt; earlier attempts retain
their own scopes and input hashes. Link-only flag comparisons reuse unchanged46
host tests by exact source identity; their argv/artifact hashes are in the two
probe reports. No target execution is inferred. All builds/host tools use bounded
owned process groups; no missing/timeout/compile failure can satisfy a semantic
omission. The final edge-case test batch initially fails47/48 because its new test expects
an error response after source loss. The actual handler correctly sends only the
prior open response, closes before an incomplete read reply and retains both raw
cleanup results. attempt-5.json and its short failure log preserve that incorrect
test expectation. Correct only the oracle/name; all48 tests then pass. A consumed
fork sequence also rejects after a settled refusal. No native guest failure ran.
Final structural review found the new measurement still used the historical
`ENTRY(minimum_rpc)` after replacing that root. LLD warns but Rust's linker-message
lint is outside `-Dwarnings`; the earlier ELF entry is0. Preserve that warning and
the explicitly non-native older receipts. Select `minimum_route` in the owned
measurement script and require its one defined symbol/nonzero exact ELF entry.
Fresh full affected checks/link pass that guard, with code still18768/16384.
Older flag probes describe code size only and never native/entry acceptance;
their zero entry is not silently replaced or promoted. No kernel/loader relaxation.
One atomic documentation patch found a line-wrap mismatch and made no edits;
the corrected patch used the actual current anchor.

The old unsafe constructor functions are byte-identical to the reviewed0207
source; only textual site positions shift after adding the safe Routed type.
The active boundary inventory updates after this exact chunk comparison, with no
historical/published pin rewrite. Partial-client stalling still can fail-stop this
bounded POC owner; isolated per-client availability and complete native deadlines
are not claimed. Source/peer closure is not native child stop/reclaim or media export.

Retention keeps compact results, commands, hashes and small summaries. Generated
objects/rlibs/images, scratch sources and tool logs are removed after capture;
current SDK and sealed service/session inputs are retained. There is no new
build/test/source archive or copied SDK. Root STATE records the next integration gate.

Nine current sys-init stages pass before the final two test additions; runtime
bytes are unchanged. current-checks.json retains stage commands, tool identity,
scoped hashes and the complete original manifest digest/count without copying
historical artifacts. The final affected48-test build/control batch and current
workflow/quality/static checks pass after that test-only correction. Final
source identities and1428 touched Markdown destinations verify. cleanup.json
records947 owned generated files/151781376 allocated bytes removed; this is
allocated-file disposal, not a measured net-free-disk change. No SDK/sealed input
or unrelated output is removed. Full broad/native suites are not repeated.
