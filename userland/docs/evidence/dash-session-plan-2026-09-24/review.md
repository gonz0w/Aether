# UL-007 session proposal review

Scope: prepare a bounded composed-session consumer workload and explicit owner
handoff. No runtime implementation, SDK pin, twelve-script input or sibling edit.
Applicable clauses: Foundations O-01–04/I-01/I-03/E-01–08; Testing TD-01–03,
TC-01–03, TE-01–03; Coding CS-01–03; Distribution PX-01–04. Internal plain ASCII
fixture output preserves existing Experience stream rules and native markers.

Risks: combining separately passing paths may retain endpoint aliases or exhaust
domain slots; a final pipeline status can hide an upstream failure. The proposal
requires independent owner status/EOF/identity/accounting checks. Shell $$ alone
cannot prove parent identity. Native counts and rejection numbers are pending
owner agreement; existing per-fixture counts are not copied as new expectations.
No native authority is provided by helper path strings or environment values.

Validation selected before execution: pinned host dash syntax and ShellCheck sh
mode,30 seconds each,16 MiB per stream through the existing owned process helper;
manifest byte checks and local quality gate. Host execution and native runtime
remain NOT RUN: syntax/static checks cannot validate command semantics. No new
compiler, SDK build, install or dependency. All outputs use a fresh build root;
small validation receipts are retained without creating native build suites.

Technical review: Codex inspected explicit statuses, fixed printf formats, quoted
expansions, final fd closure, exact streams and ownership boundaries. Independent
technical/reader and affected-owner review remain pending. No sign-off invented.
Existing helper remains under its original BSD-2-Clause terms; new script is
BSD-2-Clause. The maintained coverage entry stays draft.

Simplicity: the simpler alternative is the existing separate scripts; insufficient
to expose state retained between pipeline and substitution in one process. A small
plain script and owner-oracle table are chosen; no new runner or service protocol.
No old path is removed because existing profiles supply regression evidence.

Follow-ons: owner delivery and consumer runtime qualification for SESSION-01–06,
then early-reader/recovery/filesystem/serial composition. UL-007/M3 and UL-081 stay
open. This packet completes proposal preparation only.
