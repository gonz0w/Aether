# Descriptor redirection before repeated fork

Requirement: actual dash redirects a builtin to its inherited stderr, restores
stdout, then forks and execs external commands repeatedly in the same parent.
Use `echo redirected >&2; /next`, then `echo restored; /next`, then `/next`, and
finally the existing status/exit line. Three collected children and six reclaims
remain the bound. This tests descriptor redirection, not filesystem redirection.

Inspection found that the local FD facade uses present=0 to close an entry and
can retain its old binding/flags. The fork adapter incorrectly requires those
inactive fields to be zero and serializes them as active-format wire metadata.
Validate present strictly as0/1, ignore inactive metadata for live reference
accounting, and emit zero bytes for absent entries. Continue validating every live
binding, flag, count and reference before any fork traffic. The wire contract and
owner's exact descriptor-table check stay unchanged. Closed descriptors must not
be resurrected, authority must not widen, and saved aliases must not leak to exec.
No shared facade refactor or permissive receiver change is needed.

Simpler alternative: canonicalize the already-zeroed fork snapshot, chosen because
closed local entries carry no authority. Requiring a global table representation
change would affect unrelated consumers unnecessarily. Reusing existing fcntl,
dup2, fork and backend routes avoids a new redirection service. Remove the
unnecessary coupling between inactive local metadata and the wire representation.
Pipes require distinct endpoint lifetimes/EOF/backpressure and remain the next
contract, not an excuse to add successful stubs now. SE-01–SE-05 apply in this
existing change record; the kernel and all quotas remain untouched.

Aether owns this private adapter/fixture; SDK/userland acceptance and sys-init
policy stay separate. No siblings, upstream objects, released pins or published
ABI change. Existing ASCII witnesses and Experience exception apply. No new
unsafe code, allocation, pointers or dependency; serialization stays inside the
existing fork mask, with the same96-byte bounded publication.

Tests: full connections suite plus launch and console ABI18 regressions; host,
C/Rust format, workflow and offline standards checks. The raw-closed-entry mutant
must reject at the unchanged owner table check2150, zero child admissions/reclaims.
Require exact stream byte totals, redirected/restored markers and all terminal
identities. Retain failed attempts and freeze sources. Update STATE, shell
reference and workflow inventory. Existing C format uses pinned Clang21.1.8 style;
Rust uses1.98 edition2024. No broad formatting migration.

Follow-up before the second implementation: the copied local table also reaches
exec-stage.h. Its zeroed wire table needs the same absent-entry canonicalization.
A separate raw-exec-entry mutant must reject2120 with zero reclaims, preserving
the exact live-entry and owner validation. The first frozen run confirms this
missing boundary; its failed result is retained. Shared facade remains unchanged.
