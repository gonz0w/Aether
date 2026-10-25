# Bounded runtime extraction — UL-007

The maintainer explicitly assigned the bounded libc/POSIX runtime implementation
to Aether-userland on2026-09-29. Aether retains native ABI/grants/enforcement and
the fixture owner. Ownership no longer blocks local implementation. Independent
technical/reader review and broader SDK promotion remain pending.

Runtime/application extraction is implemented. runtime.c owns bootstrap, process/
FD/mask/channel state and finalization; application.c chooses dash arguments,
environment and helper path policy. The runtime no longer references __real_main.
The native owner still enforces actual image authority. Repeated startup is rejected
before further channel traffic, and copied children inherit startup state. Existing
transport/fork/memory mechanisms and notices remain source-pinned under vendor/.

## Executed evidence

- One initial extracted native serial composition; eleven fresh serial regressions;
  one additional native null/repeated-start probe:13 fresh008 native executions.
- Thirty-six fresh007 compatibility cases: eight scripted, seven recovery, nine
  failed-exec and twelve scratch. Existing007 source configurations were rebuilt
  with the extracted code; the advertised component bundle remains008 only.
- Each native execution has an independent consumer stream/identity/lifecycle
  comparison. The serial cases use actual prompt-driven input and retained exchange
  records. Deliberate byte/read/stream corruption also fails ordinary oracles.
- Seven pre-link missing/stale/duplicate/wrong-profile/path component controls pass.
  A missing memory adapter is rejected even if musl could satisfy its symbols.
- Eight malformed standalone-bundle/output controls reject before commands or new
  output effects: wrong seal, missing/altered source, unlisted include input,
  symlink file/directory, existing output and output inside the input bundle.
- A sealed self-contained008 candidate rebuilds runtime/application, native memory,
  patched public musl fork/wait/rebind and application helper sources. Exact prebuilt
  CRT/libc/dash dependencies and their original terms are included. Both resulting
  whole ELFs equal the freshly native-tested extracted parent/helper bytes.

This is49 fresh native executions and49 independent comparisons, across47 distinct
original workload cases plus one initial repeat and one bootstrap probe. Tests use
unchanged qualified kernel/owner bytes. No kernel, resource limit, shared pin,
package/service policy, real prefix or sibling source changed. No full POSIX,
new wire/bootstrap ABI, sustained SI-07, performance, sanitizer or whole-program
stack-safety claim follows. Kernel and owner code/limits are reused by exact digest;
new worker ELF acceptance/streams/cleanup are exercised directly.

[review.md](review.md), exact argv/environment/process-group cleanup receipts,
source/SDK/tool/archive pins, linker maps, symbols/headers/relocations and raw native
logs are retained. Compiler21/LLD21 and Python3.14.7 are pinned; other Python series
are not newly qualified for these experimental drivers. New application/header
source passes the pinned format check; borrowed source style is preserved.

## Candidate and remaining gates

Candidate manifest SHA256: `795feee16d1cfa3bcbc28cb10a996b6ef8f4de496120179d818fb46d3f288405`.
bundle-results.json and bundle-recipe.json bind the candidate location, tools,
rebuild inputs and output identities. The externally selected seal must be checked
before consuming it. components.py is developer build admission, never a native
capability boundary. The candidate has an application callback that can narrow
helper paths; it cannot delegate or grant native rights.

The bundle remains a bounded private008 candidate, not a supported SDK publication.
SSDK-01–06 need scoped owner/independent disposition; existing private tests do not
invent reviewer approval or cover general POSIX/TTY/storage. UL-007/063/M3 remain
open. SI-07 separately needs its versioned lifetime/bootstrap/transport composition.
The remaining promotion blocker is actual independent technical/reader review and
its findings, not missing runtime ownership. The runtime is now locally implemented
and available for concrete review rather than an unassigned future dependency.

## Retained attempts

Initial build-driver output lookup failed after successful object compilation and
component controls; corrected selection uses -o. Initial standalone helper equality
failed only on renamed STT_FILE metadata; the original basename restores equality.
A later source-review improvement rejects unlisted file/symlink namespaces before
imports or compilation; both candidate revisions and their receipts are retained.
See attempts.md, initial-attempt/, bundle-initial/ and bundle-v1/. No native suite
needed a retry. The final stronger builder produces the same native-tested ELFs.

Final quality, format, syntax, whitespace and six previous evidence-seal checks
pass. All native receipts show checked completion/reaping/owned process cleanup.
The source/dependency candidate is [session-runtime-candidate.tar.gz](session-runtime-candidate.tar.gz).
The complete private build tree was archived with an indexed readback of every
file/symlink before removing it; retention.json records exact paths/hashes.
Compaction reclaimed348041216 allocated bytes. The small failed initial
object-build root remains recorded; no historical evidence was pruned.
