# SI-07 companion handoff review — 2026-10-03

Before-work requirement: verify userland's matched consumer replay and sys-init's
ABI22 paired-owner/request-loop/error delivery against the unchanged kernel and
producer seal. Record satisfied scoped gates and remaining work here. No sibling
writes/messages, released-pin changes, new kernel ABI, supervision policy copied
into Aether, or full SI-07/R1 acceptance is permitted.

Inputs: six dated companion evidence packets, their manifests/source archives,
exact native receipts, selected paired-owner sources and tool/artifact bindings.
At discovery the request-loop final seal was not yet visible. Verify any seal
available at intake, plus retained archives and matching packet members; freeze
exact local bytes without inventing a publisher seal.

Selection: all supplied manifest members; source archive namespace/hash checks;
current kernel/source equality; independent native trace comparison, malformed
trace controls, retained ownership-error observations, fresh offline Rust owner
rebuild identity, host/pin/workflow checks and local links. Native receipts remain
companion executions; no new QEMU replay is claimed unless actually performed.

Security/ownership: halt is delegated developer-console authority, not an
authenticated public operator command. Quiescent input precedes worker acquisition;
outstanding command settlement precedes next input. Unknown ownership must remain
retained after reply/cleanup failure; neither successful recovery nor replay may be
inferred. Sys-init owns that policy; Aether owns enforcing lifetimes and grants.
No new unsafe boundary, dependency, resource growth or authority is introduced.

Simplicity: verify and record the existing owner handoff rather than creating a
second init loop. No runtime compatibility path or service is added; removing stale
missing-input blockers is the immediate simplification. Keep broader wait-transition,
child-bootstrap/malformed/foreign schedules, useful shell-session composition and
SDK/reader disposition explicitly separate from bounded acceptance.

## Disposition

All six snapshots verify. The matched userland consumer seal is checked in full;
its retained839-member archive and the loop consumer’s573-member archive pass full
hash/size/mode/namespace readback. All six packets have verified supplied manifests at intake; the loop consumer
seal arrived after initial discovery. Additional copied metadata is covered by
the local snapshot seal, not silently included in the publisher’s declared seal. The343-member
sys-init source archive validates exactly, including35 current kernel files and
unchanged build.zig. Fresh raw/ELF normal owner rebuilds equal native-tested pins.
The normal owner remains10152 code bytes and the producer’s scoped2696/4088 stack
estimate; the review does not create independent all-path stack assurance.

Twenty retained companion traces compare successfully; fourteen deliberate local
trace corruptions reject. Nine producer cases and seven request-loop cases have
independent userland replay. Four sys-init error cases demonstrate complete
fragment assembly or retained Unknown/no replay on loss/cleanup failure. Those
fatal cases do not prove cleanup recovery or ordinary shutdown. Exact output
remains bound to inspected owner assertions, rather than a direct UART data stream.
No new native run or full acceptance is inferred from this documentation intake.

The missing-input and fixed-five-cycle blockers are closed for bounded development.
Next: native child-bootstrap mismatch and remaining malformed/stale/foreign
schedules, broader wait transitions and useful shell integration with sys-init’s
actual owner. Reader/SDK disposition and full SI-07/R1 remain open. Independent
review is not a blanket blocker to authorized implementation. Original evidence,
released pins and all sibling files remain unchanged.

Retained local failed attempts: initial startup-artifact lookup used the wrong
index shape, before any compiler invocation; initial trace reader used producer
attempt suffixes rather than consumer-normalized directories. Corrected readers
and a fresh rebuild succeed without changing supplied bytes. Both initial drivers
and failure records remain. Temporary extracted source copies are verified against
the retained source archive before removal; rebuilt artifacts/logs remain.

Reproduction: from the repository root run `python3 docs/evidence/si07-handoff-review-2026-10-03/check-traces.py` for retained comparisons; intake.py and rebuild.py reject reused output roots and require a fresh dated attempt. Local required checks are `zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global` and `python3 scripts/check_workflow.py`. Checks and the final local seal cover exact snapshot bytes without claiming sibling publisher seals where none exist.
