# AF09 home broker in-place construction — UL-007/081/082

## Selected scope — 2026-10-24

The maintainer requested continued service/client integration until blocked.
Following [FILE/C receipts](FS-FILE-WRITES.md), this record owns explicit two-grant
in-place construction before native owner integration. Owner: userland filesystem
implementing agent. Candidate `codex/fs-home-in-place`; target
`codex/consolidate-system`; reviewed base `a558410da0a3a4339ee18e5c40a0b1aefe88a476`.
Apply PROJECT/METHOD/DEVELOPMENT, quality PROCESS, pinned Foundations O/I/E,
CE/CD/CR/CA/TD/SE and the existing [initialization contract](FS-BROKER-INIT.md).

Finite outcome: safely construct Client, shared descriptions and ProcessFiles in
the caller's final exclusive MaybeUninit slot, consume both AF09 greetings once,
then use the unchanged home write/FILE receipt APIs. No full broker temporary,
new fields, table/worker/channel, heap, authority, quota, dependency or native ABI.
Preserve old by-value and single-greeting in-place constructors and old machine
profiles. No CWD merge, libc/routed writer, native owner/entry, persistent home
layout/provisioning, complete fit, VM, durability or release claim.

## Contract before code

Select `fs_home_in_place` only with `fs_in_place` and `fs_home_wire`; remote/FILE
consumers also require the existing process-write/path/file16/replacement/wire
prerequisites. Old unselected AF09/in-place guards remain. Add explicit
`Client::connect_home_in_place` and `ProcessFiles::connect_home_in_place` rather
than silently changing the old constructor to accept two grants.

Return a borrow only after every nested field and both exact greetings validate.
Keep root rights3/home15, token sequence3 and existing nonreused epoch rules.
Epoch0 rejects before receive. First/second receive or malformed/status/token/kind/
reserved-field failure attempts both raw closes once and drops the channel once,
preserving the original ConnectFailure. No usable enclosing reference is published
on returned failure, no duplicate greeting/drop or replay. Failure leaves the
slot uninitialized for caller purposes; a successful caller must settle/disconnect
and eventually drop it once. Channel callbacks remain bounded, nonreentrant and
non-panicking; unwind recovery is not added.

Reuse existing fieldwise raw initialization through small private helpers where
both constructors need the same writes; reuse one home-greeting validator for
by-value and in-place paths. No zero-as-Option, complete struct write/copy, private
layout cast, reference to uninitialized Self or second ledger. Each projection
derives from the exclusive aligned parent slot; initialize non-owning fields
before the sole owning channel, publish only after nested success, and drop only
the fully initialized innermost client on returned greeting error. An internal
Client reference is permitted only after all its fields are valid; no caller
borrow escapes before both grants validate. Preserve exact
array element types, bounds, padding rules and ownership safety comments.

Simpler alternative: reuse by-value construction. Earlier concrete owner work
measured its complete broker temporary beyond the stack budget. Reuse the same
fieldwise initialization and one two-grant validator for both paths, removing
initialization duplication without another layout, ledger, stack pivot or allocator.
No old compatibility path can be removed while sealed/native consumers still use it.

## Verification and documentation impact

Before production, write and run tests expecting missing new API/profile support;
record actual compiler red without a runtime-red claim. Use poisoned nonzero backing
and adjacent canaries; check all four admission records, all16 FD entries in each
view and all13 shared descriptions through the new/old public capacity regressions;
assert successful identity/empty aliases, actual home
write/readback/shared position and typed FILE receipt; first/second greeting loss
and malformed sweeps, epoch0, both signed raw closes and exactly one channel drop;
old constructor refusal before input; successful disconnect/drop without duplicate
close and safe failed-slot reuse after both greeting failure stages with a fresh channel.
Check both directions of home/in-place/cfg mismatch on host and target. No Miri/sanitizer claim. The scripted poisoned in-place test supplies13 file
lookups to exercise every description and all16 aliases without claiming more
than the actual AF09 owner fixture's12 free handles.

Named compiling controls must omit second-greeting validation, corrupt home rights,
change next token, lose failure close/drop or initialize an admission record wrongly;
require exact semantic markers. Inspect concrete native constructor assembly/stack
reports and actual size/alignment, with strict host/no_std/Rustfmt/Clippy and old
in-place/default regressions. Individual frames are not complete-owner fit. The
existing FILE/process/client suite remains required for affected public helpers.
Use pinned tools, owned process helper, one300-second cumulative check budget,
all-attempt compact records, final input verification and owned-output deletion.

From `userland/` run
`PYTHONOPTIMIZE=1 python3 -B experiments/filesystem-service/check-home-in-place.py`.
Register its workflow before execution; update experiment README,
Experience/coverage and parent/root continuation. Separate peer contract/unsafe/
source/evidence/reader review precedes normal-hooks local integration. After this
finite constructor slice, continue to matched native owner and actual offline
whole fit; prepare concrete guest artifacts before requesting any fresh disposition.
Consumed VM approvals remain consumed. Owner decisions still gate any change to
scope authority, resource limits, persistent layout or native execution.

## Status

Pre-code contract received separate peer-agent review (`home_review`), with no
design blocker. Incorporated full-ledger/canary, both-stage reuse, mismatch and
concrete-root measurement requirements. Test compiler red precedes production.
No native owner, output artifact or guest is selected yet.

Attempt01 is the pre-production compiler red: the current remote profile guard
refuses AF09 plus in-place before the missing new API tests can compile. An initial
invocation from the repository root used the component-relative path and exited2
before starting the checker; rerun from userland produced the retained attempt.
No semantic runtime-red or production execution is claimed.

Attempt02 compiles production but its generic poisoned Guard helper needs an
explicit Guard<T> annotation. Attempt03 runs three cases successfully; its malformed
matrix incorrectly calls directory size invalid (the protocol carries real sizes).
Use invalid kind3 instead. Attempt04 repeats that failure because the correction
command ran from the wrong directory and did not apply; retain it as a duplicate
failed run, not a new reproduction. Attempt05 passes four initial tests and strict
host/native/Clippy builds, then deliberately stops at unregistered remaining gates.
The full-capacity fifth case and exact-error assertions follow implementation.

Separate unsafe/source review finds no initialization/lifetime/drop defect under
the recorded callback contract. It catches a missing local FILE selection guard;
that guard now requires matching home/in-place/write selection even against old
consumers. Error messages distinguish unselected in-place. The existing home-token
mutation checker is adjusted from client.entry to self.entry after the shared
greeting extraction, preserving the same omission and marker. Final qualification
and measured reservations are recorded below; final separate review passes.

Attempt06 retains expanded-test compilation errors (status bit casts/API spelling).
Attempt07 passes all five cases, both old in-place profiles, guards and six compiling
controls, then fails at the missing supplemental objdump manifest key. Its existing
LLVM21.1.8 pin is now explicit before measurement/final verification. Attempt08
passes582 children and concrete1504/8 layout, maximum individual328-byte reservation.
Attempt09 adds retained stack adjustment/prologue excerpts, strict probe Clippy
and the transport source's declared Rust2024 edition;583 children pass. Probe/tests
retain the existing userland Rust1.98/2021 fixture exception; production language
requirements are unchanged. Attempt10 preserves an expanded sealed-profile
checker mismatch: a path/process broker used a plain client without those methods.
Rebuild the matching old-profile current client against the exact sealed service.

Final attempt11 passes597 bounded children: five constructor cases, six new
compiling controls, old AF07/AF08 in-place regressions and current/sealed profile/API
guards, concrete native object/layout/Clippy and FILE452 predecessor suite. All924
frozen entries verify and owned output is removed. The concrete broker is1504/8;
four emitted static reservations are40/24/120/328 bytes with retained prologues and
adjustments. This is not linked/summed/interrupt/whole-owner fit. Exact-source CLI
checks pass18 children. Current Python3.14.7 is tested, not minimum3.10.
Separate peer agent `home_review` reviewed the pre-code contract, revised unsafe/
source paths, controls, frozen identities and final evidence/reader instructions;
no unresolved production blocker remains. Its
[review receipt](../evidence/filesystem-home-in-place-2026-10-24/peer-review-checks.json)
records workflow/userland quality, scoped links/whitespace, reconstructed controls
and complete owned-output cleanup. This is ordinary peer review, not human,
specialist, native or release acceptance. Normal-hooks local integration is observed below.
After integration continue with a matched sys-init FILE receipt dispatcher and
then native owner composition/offline whole fit before any fresh guest disposition.

## Observed local integration — 2026-10-24

Status: complete for the bounded constructor slice, final-byte qualification,
separate review and local integration. Normal `.githooks` accepted
`9af901cdcbcd6b6f5fae644125f6ca1742a56185`
(`feat(fs): construct home brokers in final storage`). The unchanged target
`codex/consolidate-system` fast-forwarded from the recorded base. Tree
`6f85daec1e7c60ab1cf493214ec791188dd82695` matches the reviewed staged candidate;
checkout was clean. Main stays `78c13fc5f5329bb590c2ab4772f2e1e2372dc067`.
No source, pin, tool, native input or accepted quota changed after qualification.

This documentation-only closure reconciles root selection and parent continuation.
Its [narrow separate review](../evidence/filesystem-home-in-place-2026-10-24/integration-review.json)
precedes normal closure commit/target fast-forward. [Matched sys-init FILE observations](../../../sys-init/docs/decisions/0223-file-write-observations.md)
now own completed consumption and continuation through native owner/offline whole fit. No guest, push, libc
activation or native acceptance follows.
