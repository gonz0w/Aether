# UL-007 scratch redirection and recovery session

2026-09-29. Consumer handoff after EXEC-SESSION-01–06. Native execution **NOT RUN**.
Run the entire pinned [script](scratch-session/composed.sh) through actual dash main
and repeat in three parents. Prior isolated scratch/leak/denial acceptance remains
valid but does not qualify this composition or persistent storage.

## Namespace and descriptor contract

Use WITNESS=value, LC_ALL=C and PATH=/nonexistent with the unchanged helper.
Only /inputs/helper has image replacement authority. The owner supplies bounded,
volatile /scratch/data with read/write/truncate rights and a protected /inputs/denied
object without write authority. Seed each new parent namespace with exact
initial-data.bin and protected.bin bytes. Explicitly retire and clean the preceding
namespace before preparing the next; this is fresh-domain isolation, not persistence.
No real prefix, implicit user identity grant or pathname-only authorization.

Opening data with `>` must truncate it. fd3 and duplicated fd4 share one writable
open-file description and offset. Write A on fd3, close fd3, then write B on fd4:
closing one alias must not invalidate the other. Final alias close retires the writer.
The deliberate subshell write to /inputs/denied must reach the owner, return EACCES
with no handle or mutation, and produce actual child2. Its stderr is closed only
for this command to avoid upstream human diagnostics in bounded observation output.
A child2 without an authenticated denial is insufficient. Parent stderr stays open.

Reopening data for helper stdin creates a reader at offset0 and must produce exactly
AB then real EOF. Parent stdout supplies the newline; do not accept A, B, BA, stale
suffixes or synthetic helper output. The protected object must remain byte-identical
throughout denial and subsequent work. No request may gain image authority from
either file path. Retire reader/description references after helper termination.

The same live parent then verifies argv/environment, runs a fresh ten-byte pipeline,
checks fd3–63 closed, checks its PID and emits its final stderr diagnostic. Require
all healthy stage statuses0, real EOF and complete cleanup. The exact output files
and manifest supply byte counts within the existing128/32-byte observation bounds.
This does not qualify failed-command human diagnostics, append, durable writes,
a mounted/general filesystem or interruption recovery.

## Acceptance

| ID | Required native observation | Status |
| --- | --- | --- |
| SCRATCH-SESSION-01 | Truncate stale data, shared-offset A/B writes and alias-close lifetime; reopened reader yields exactAB and EOF | NOT RUN |
| SCRATCH-SESSION-02 | Owner-backed EACCES, child2, no handle/rights gain and unchanged protected object | NOT RUN |
| SCRATCH-SESSION-03 | Reader child collected/reclaimed before healthy argv and fresh pipeline; all stages0 | NOT RUN |
| SCRATCH-SESSION-04 | fd3–63 closed, same PID, parent stderr usable, exact separate streams and parent0 | NOT RUN |
| SCRATCH-SESSION-05 | Semantic negatives reject at precise authority/data/lifetime boundaries with confirmed cleanup | NOT RUN |
| SCRATCH-SESSION-06 | Three fresh parent namespaces with exact phase identities and full worker/channel/file reclamation | NOT RUN |

Per parent: seven copies (denied-write subshell, scratch-reader helper, argv helper,
builtin pipeline writer, two copy helpers, closure helper), five helper replacements,
eight terminals/reclaims. Across three:21 copies,15 replacements,24 reclaims; expect
18 image admissions if the owner records parents plus successful replacements.
The existing slot strategy would use five slot2 lifetimes per parent and one each
in slots3/4, reaching slot2 generation15. This is planning inference, not an imposed
map or proof. Reconcile exact IDs, channels and file-description lifetimes first.

Scratch writers/readers are retired before pipes become live, but temporal separation
does not authorize treating scratch references as pipe references. The owner must
provide type/rights/generation validation and bounded FD/description allocation.
Do not enlarge the15-lifetime, three-child/two-pipe,24KiB owner or4088-byte usable
stack limits. Existing owner stack margin is small; linked inspection is required.
Do not borrow prior3768-byte stack results for a changed scratch owner.

## Required negative controls

- Lose B, split the aliases' offset, skip truncation or corrupt reader bytes:
  normal lifecycle alone cannot pass the exactAB/file-state oracle.
- Close the underlying writer at the first alias close: reject the later write;
  freeze the actual native error and shell/cleanup result, not a generic crash.
- Grant the protected write, return a wrong errno, or synthesize child2 without an
  owner request: reject authority evidence even if script output looks correct.
  Record protected bytes and absence/presence of handles; no silent rollback claim.
- Retain writer/reader references or replay a stale description after close/reuse:
  reject before they can mutate a replacement file or satisfy later I/O. Prove
  stop/terminal/close/reclaim where needed; timeout never establishes cleanup.
- Skip or break the reopened-reader request: the owner/file/stream oracle rejects
  without accepting inventedAB or a fabricated EOF.
- Wrong WITNESS: helper91/parent66 after the denied/AB prefix; no healthy pipeline.
- Leak unflagged fd3 to the closure helper: helper95/parent68 after healthy work;
  no final diagnostic/success. Ordinary descriptor closure must remain checked.
- Corrupt healthy pipeline bytes: exact-output checker rejects even with parent0.
- Retire/misroute parent stderr: reject missing diagnostic and require the actual
  exit/close cleanup outcome. Prior failed-exec control observed wrapper141 rather
  than script57; do not assume this script's70 will be the native final result.

Freeze every producer mutation, exact native errors, allowed prefixes, image
admissions and cleanup identities before independent replay. Keep the positive
script and seeds unchanged. POSIX FD numbers, mode bits and names are not grants.

## Delivery and limits

Supply sealed complete source/support export, all invoked drivers and frozen inputs,
matched host/affected native regressions, exact tool/SDK/ABI pins, linked code/stack
review, file-state/authority oracles, separate streams and all failed attempts.
Reuse existing owned replay bounds: sequential3600-second native deadlines,
1800-second review ceiling,512MiB streams and unchanged guest watchdogs.

Host preparation may relocate /inputs/ and /scratch/ only under private build roots;
it does not execute original target paths or prove native authority/reclamation.
Current session integration must explicitly add the owner-backed scratch boundary;
local pathname/error stubs cannot satisfy it. No sibling implementation edits are
authorized here. SI-07 complete bootstrap/transport and rebuilt runner/bytecount,
real serial composition, shared SDK, reader reviews and full M3/R1 remain open.
