# Bounded home delegation — UL-007/081/082

## Selected library scope — 2026-10-24

This record owns the first writable-home provisioning slice selected through root
[STATE](../../../.planning/STATE.md#system-work-index). The maintainer requested
continued work under the standards/process; the existing
[writable-home decision](FS-ROOT-PATHS.md#results-and-next-authority-boundary)
already permits home mutation while requiring explicit installer/admin authority
for system changes. The completed [AF08 qualification](FS-CWD.md) remains closed.

Owner: implementing agent for the userland filesystem service. Base:
`3066d17bc374754bed53736679a36b8415547b78` on `codex/consolidate-system`; candidate branch
`codex/fs-home-delegation`, integration target that unchanged consolidation branch.
No integration of the earlier consolidation into main, push or publication.

Finite outcome: an opt-in, host-tested owner-library operation derives a writable
home handle from an existing authorized directory handle while giving the recipient
a read-only system root. This is trusted provisioning preparation, not a callable
client operation or a new native profile. Existing tables and teardown own both
handles. No new service, channel, worker, heap, writable static or resource quota.

Non-goals: creating a home, choosing the installed home location or initial CWD,
modifying service/FILE wire formats, client/libc/process integration, login/admin
policy, symlinks, disk executable admission, native startup/readiness, guest
execution, persistent Zsh/packages/TTY/ISO or release acceptance. A test directory
named `home` is synthetic input, not a distribution layout decision.

## Contract recorded before implementation

Select `fs_home` only with `fs_directory_contexts` and its existing prerequisites.
Add `Owner::attach_home(source_peer, source_session, home_handle, peer)`, returning
`HomeAttachment { session, root, home }`. The source peer/session/handle must pass
the existing live owner/epoch/session checks. Require a Directory distinct from
the owner's system root, with LOOKUP|READ|WRITE|MUTATE_DIR (15). Reject insufficient
rights, a file, root identity, stale/foreign handles and zero recipient peer before
publication. The caller obtains `peer` from authenticated transport provisioning;
no client opcode, path, raw Node, HOME/UID/mode or package record can invoke this
administrative operation or supply authority. Names are not grant sources.

The new recipient has exactly one connection and two independent handles: system
root with LOOKUP|READ (3), home with rights15. Do not copy METADATA16 or any source
rights beyond15. The home object identity comes from the validated source handle;
no provider lookup, mutation, clock read or namespace interpretation is needed.
The root3 grant comes from the trusted Owner's existing administrative authority,
not from the home handle or its name; only the home grant is derived from source.
Existing `attach` and all unselected profiles keep their behavior.

Reserve a free connection, two distinct free handle slots and three serial values
before publishing any state. Full tables, permanent serial exhaustion and overflow
leave connections, handles and counters unchanged. No recycling/reset. Publication
is synchronous under exclusive `&mut Owner`; no callback, fallible operation or
reentry occurs after serial reservation. This adds no Owner fields or capacities.

Home lookups attenuate existing rights. A read-only lookup through system root
must never recover the privileged home handle. `parent_directory` continues to
return only read rights; leaving home cannot carry mutation into its parent.
The existing provider contract still owns correct object/parent identity and
namespace containment. This library result is not a native transport or malicious
storage-provider isolation claim. Symlink/cross-directory rename support is absent.

Closing the source handle/session does not revoke the separately delegated
recipient handles; close and revocation are distinct. Recipient disconnect removes
both handles through the existing session cleanup. Subsequent old handles/session
are stale, slot reuse issues new serials, and owner retirement/shutdown invalidates
all attachments without replay. No new recovery or revocation mechanism is added.

## Review, standards and verification plan

Apply root [DEVELOPMENT](../../../docs/DEVELOPMENT.md), userland
[quality process](../quality/PROCESS.md) and its [review outline](../quality/change-review.md).
Pinned Foundations O-01–05/I-01–08/E-01–08 and locally adopted CE/CD/CR/CA/TD/SE
apply. Proposed Distribution FS/DS/PD clauses inform future composition only;
this local API allocates no shared ABI or released standard. Original work stays
BSD-2-Clause, with existing Rust1.98 tools and no dependency additions.

Security review: untrusted requests must remain unable to call provisioning or
convert root reads into home/system mutation. Protected state is the existing
connection/handle/serial ledger. Tests must distinguish wrong peer, wrong session,
stale generation, deficient source rights, root substitution, metadata escalation,
exhaustion/partial publication and teardown. Existing trusted Owner and Backend
remain in the TCB. No unsafe/FFI/assembly boundary is introduced. Preserve existing
Rust source style with pinned rustfmt edition2021 (compiler edition2021 for these
existing fixtures); new files use that scoped fixture convention rather than
mixing a format migration with authority work.

Simpler alternative: give the shell the existing mutable root attachment. It
violates the settled system-write restriction. Deriving one explicit home handle
uses the existing authoritative ledger and attenuation checks; it avoids another
client/SPA/service or path-prefix authority filter. No obsolete path can be removed
yet because existing consumers use the frozen profiles. The necessary cost is one
small optional owner operation and tests; native routing remains a separate step.

Before implementation, write behavior tests against the proposed API and record
their actual red result. Then exercise the actual owner with a synthetic backend:
home write/create succeeds, system and read-only home aliases reject before
provider effects; metadata16 is absent; `..` gives read-only parent; source closure
preserves recipient; wrong/stale authority, every missing source right, file/root,
connection/handle/serial exhaustion, shutdown and disconnect/reuse reject correctly.
Include compiling semantic controls for source-right omission, root-writability,
home-root substitution and partial/exhausted publication as feasible. Retain the
existing affected owner regressions and build selected/default no_std target
libraries. Compare Owner layouts; whole-executable fit remains untested.

Command from `userland/` (registered before execution):
`python3 -B experiments/filesystem-service/check-home.py`.
Use the existing pinned owned-process helper, bounded child deadlines and private
`build/` output; retain compact commands/tool/source hashes/results and short
failures, then remove generated outputs. Strict rustfmt/Clippy/unsafe denial apply.
Run userland quality and root workflow/pin/inventory checks, scoped links/diff,
and separate peer-agent review before integration. No broad native handoff occurs;
the full host/native composed checkpoint belongs to later consumer integration.

## Results and review

The contract and tests preceded implementation. The missing API produced an
actual compiler red before `attach_home` was added; no semantic test-first runtime
claim is made. [Compact evidence](../evidence/filesystem-home-2026-10-24/README.md)
retains all four attempts, including the metadata harness failure and a rejected
generic-overflow control. Final attempt04 passes14 selected tests (13 home plus1
existing runtime),1 unselected AF08 and13 legacy owner regressions; five compiling
controls reject lost source checks, writable system root, wrong home object,
serial-exhaustion publication and single-slot alias publication.

Strict pinned rustfmt/Clippy/Owner unsafe denial, selected/AF08/legacy host and
no_std libraries, and host/target prerequisite rejection pass. Owner with a
zero-sized provider remains1080 bytes/alignment8; target size/alignment equality
passes. No whole-executable resource claim follows. Frozen sources/tools/libraries
match after execution, children join and generated outputs are removed. Current
Python is tested; minimum Python3.10 remains untested in this scope.

Root workflow41 references/37 tools/182 groups, Foundations/Experience/Distribution
pins, four simplicity files and all eight method files pass. Userland quality
passes its pins, snapshots and documentation inventory. These checks establish
their stated inputs/structure, not runtime or release compliance. Separate review
is recorded below; local integration identity follows after execution.

Final checker CLI/syntax controls pass on SHA256
`794b2bbccdc54d1a95b63259b0cfa316f91639612fdf459fbcffc71f18ccf80a`.
Its only change after attempt04 is help ordering; the
[CLI receipt](../evidence/filesystem-home-2026-10-24/cli-controls.json) records
unchanged behavioral inputs/logic and the scoped evidence reuse. No unchanged
behavioral suite is repeated solely for the help presentation change.

### Separate peer review

Peer agent `home_review`, separate from the implementation and checker authors,
reviewed the complete candidate against the recorded base. No unresolved findings.
The [review receipt](../evidence/filesystem-home-2026-10-24/peer-review-checks.json)
binds the reviewed source/checker/document hashes, final workflow and userland
quality passes,25 scoped local links/anchors, whitespace and owned-output cleanup.
The reviewer read all40 final child receipts and five semantic controls, confirmed
input identities, and reconstructed the exact help-only checker delta supporting
behavioral evidence reuse. This is peer-agent source/evidence review, not human,
specialist or independently executed native acceptance.

Reviewed owner/policy/tests SHA256 respectively:
`e77903971bd74e9886ba516719d626d551384ca048ca31b3525f001518ce7897`,
`d1ece8b077cd51515ec3241d27b7a20c004cccdcc31497d18cd4b56fea05f069`,
`afb6241932481857d777346fc90bc49a5e5070c3d8428ad48f876a9ce2fef090`.
The integrating agent rechecked final behavior inputs, unchanged target base and
configured hooks. No new guest or broad suite is needed for this reconciliation.

## Status and continuation

Status: complete for the library scope, focused checks and separate peer review;
the implementation is locally integrated as recorded below. Documentation impact
is this record, root selection, experiment
README, userland Experience/coverage and root workflow command routing. No released
pin, frozen candidate or native input is refreshed; AF08 approval is not reused.

The separate [service/client binding record](FS-HOME-WIRE.md) now owns consumption
of these two grants and its continuation. Do not silently widen old AF08 or
AEFP0003 read-only clients. Creating the real home, native whole-owner fit and fresh
qualification need their own finite scope and execution disposition. Full
UL-007/081/082 and persistent Zsh/packages/TTY/ISO acceptance remain open.

### Observed integration

The normal commit with configured `.githooks` produced
`37e95c99d9aee269109c0033da810f2328f95cd3`, tree
`fc969c07d13786353a03f80a22b7d2ce2bbd38db`, matching the reviewed staged candidate.
Before that commit, the reviewer separately confirmed the review-record additions:
FS-HOME SHA256 `112ba14a48b3c43556f5348dcda83ba985897a10e106e2137a8723cb0f6120e2`
and evidence README `e9275972c07f3d60e23693538b9a544ca8f0673f9b0bac6f19f4efaea80ad224`.
With a clean tree and unchanged target base, the integrating agent fast-forwarded
`codex/fs-home-delegation` into `codex/consolidate-system`. The resulting commit
and tree exactly match those identities. Main remains
`78c13fc5f5329bb590c2ab4772f2e1e2372dc067`; no push or guest occurred.
This final observation and STATE routing are documentation-only reconciliation;
they do not change tested runtime/checker bytes or expand the completed scope.
