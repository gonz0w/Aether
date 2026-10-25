# Filesystem policy change review — UL-082

Requirement before code: own a private Rust filesystem policy layer for the
existing-file write handoff. Start from the source-bound readonly fixture's
session/handle authority and keep all sibling framing/fixtures untouched. Add
trusted UTC, explicit WRITE attenuation, coherent size for all matching aliases,
and permanent context retirement after committed/uncertain/malformed completion.
One nonempty provider call per context until sustained transaction qualification;
zero length performs no clock/provider call. No public wire/API/native readiness.

Success: foreign peer/session/stale/reused handle/rights escalation deny before
backend; clean write refreshes every alias, preassignment error preserves reads,
postassignment error or lost/malformed completion revokes all handles and drops
backend exactly once, never replaying. Tests independently count calls/UTC/drop
and actual shared byte storage, deny bounds/holes/overflow/invalid time, exhaust
slots/serials and verify denied writes cannot reach provider.

Applicable Foundations O/I/E, Distribution NC/FS/OB, approved TD/TC/TE and CR/CP,
SE-01–05. Original work BSD-2-Clause; copied readonly source notices retained.
No OpenZFS CDDL implementation is transplanted. Rust1.98.0, explicit2021 edition,
no_std/no allocator/no unsafe implementation, panic=abort production compile;
host tests unwind only in test harness. rustfmt + default Clippy with warnings
as errors, owned60s compiles/30s tests, private build output and compact records.
Pin actual source/tool digests before consumption, actual minimum/current Python
syntax/controls and quality pins before completion. No install/network/sibling edit.

Review: exact source provenance checked against native pair source_freeze_base.
Native one-shot mutation/ordered witness is not a sustained service contract;
this slice intentionally enforces a single provider call. Missing live bridge,
full metadata, directory mutations, authenticated endpoint integration, IPC reply
loss handling, native resource fit, sustained service, sys-init/pkg assembly and
independent review stay open. Runtime UL-003/007/012/015/082 and M3/R1 not closed.

Simplicity questions: reuse the small serialized readonly authority design rather
than a new RPC framework/cache/async service. Cached independent sizes become
incorrect with writes, so update every existing identity alias on success. One
backend owner and bounded arrays need no additional file registry/locks/allocator.
No accepted path is removed; existing producer fixtures remain regression inputs.

Actual technical review by Codex: all authority/range/time checks precede provider
mutation; empty writes have no provider/clock effect. Completion handling separates
known unassigned errors from committed/lost/malformed progress, preserves committed
error details and drops the sole backend exactly once. Matching object+generation
aliases update together, and conflicting later metadata poisons the context. No
unsafe FFI/Send/Sync claims are made by this safe policy library. Default Clippy
on source/tests and rustfmt pass without suppressions. Thirteen actual host tests
and eight compiling semantic omissions pass. First11-test pass and later expanded
passes remain separate; no failed attempt is reclassified. Independent reader and
live owner/native consumer reviews remain pending. This slice is implemented;
UL-082 as a whole remains active. Next bridge/transport is local work, not blocked.

Experience scope: internal qualification recipes retain the dated recipe exception,
now explicitly recorded in docs/EXPERIENCE.md. Plain ASCII results/standard test
harness output, stderr failures, no new boot/client presentation or public CLI.
Published Experience integrity/contrast checker runs in the local quality gate.
