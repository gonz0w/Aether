# UL-007 continuation after failed exec

2026-09-29. Next consumer-owned composition after accepted RECOVERY-01–06.
Status: native execution **NOT RUN**. Run the entire pinned
[script](failed-exec-session/composed.sh) through actual dash main, then repeat in
three parent generations. The existing standalone DASH-failed-exec acceptance is
a prerequisite; it does not establish this persistent-session composition.

## Workload and authority

Use WITNESS=value, LC_ALL=C and PATH=/nonexistent. The owner must distinguish an
absent /inputs/missing from a present owner-backed /inputs/not-executable object
without replacement authority. Only /inputs/helper has executable lookup authority.
Keep the existing helper bytes unchanged. Missing returns ENOENT/child127; denied
returns EACCES/child126. Observe and reclaim each failed child before the next
external command. Failed exec must preserve no replacement image and grant no
new authority. Owner-backed lookup/denial and cleanup must be directly witnessed.

The current session client locally returns EACCES for every non-helper pathname.
That is an explicit integration dependency. Do not replace it with a pathname
special case that merely synthesizes ENOENT; the owner must make and record the
authority decision. Supply concrete producer request/reply/negative semantics
before integration. No numeric ABI or owner failure code is assigned here.

Each failed command deliberately closes its own fd2 with `2>&-`. This avoids
human-diagnostic spelling and overflow of the existing32-byte stderr observation.
Do not suppress diagnostics elsewhere or silently truncate streams. Parent stderr
must remain writable and deliver the final exact diagnostic. This fixture does
not qualify the failed commands' human diagnostic delivery. No /dev/null lookup
or scratch filesystem is needed.

After statuses127/126, the same parent runs argv/environment verification, a fresh
three-stage ten-byte pipeline and the fd3–63 closure helper. Its PID must remain
unchanged; final exit0 and exact pinned stdout/stderr are required. Require all
healthy pipeline stage statuses zero and true EOF, not just the last stage status.

## Acceptance and expected logical work

| ID | Required native witness | Status |
| --- | --- | --- |
| EXEC-SESSION-01 | Owner-backed missing and non-executable decisions produce child127 then126, without image replacement or widened authority | NOT RUN |
| EXEC-SESSION-02 | Each failed child is collected/reclaimed before subsequent command; stale identities cannot satisfy later waits | NOT RUN |
| EXEC-SESSION-03 | Same parent runs healthy argv and ten-byte pipeline, all stages0 with real EOF | NOT RUN |
| EXEC-SESSION-04 | fd3–63 closed; failed-child stderr closure leaves parent stderr usable; unchanged PID, exact streams, parent0 | NOT RUN |
| EXEC-SESSION-05 | Semantic negative controls reject with confirmed cleanup; timeout/crash is never a passing denial | NOT RUN |
| EXEC-SESSION-06 | Three complete parents with exact phase identities, admissions, terminal results and worker/channel reclamation | NOT RUN |

Per parent: seven copies (two failed exec children, argv helper, builtin writer,
two copy helpers, closure helper), four successful helper replacements, eight
terminals/reclaims. Across three:21 copies,12 successful replacements,24 terminals/
reclaims. If admission records count parents and successful replacement images,
expect15 admissions. Failed exec attempts must not count as successful admissions.
Exact stream byte counts are in manifest.json. All observations fit existing
128-byte stdout/32-byte stderr bounds; never enlarge the ABI to fit this script.

The owner's existing slot reuse strategy would use five slot2 lifetimes per parent,
reaching15 across three; slot3/4 each use three. This is a resource-planning
inference, not a mandated map or proof of fit. The current private profile permits
15 lifetimes. Owner reconciliation must prove the last allowed lifetime completes
without a sixteenth slot2 launch, wrap, hidden helper, widened limit or leaked
reservation. Keep24KiB owner code and4088-byte usable stack bounds unchanged.

## Negative controls to freeze before native replay

- Missing reported as denied: first child126 and parent51; no second lookup,
  healthy command, pipeline or success output.
- Denied reported as missing: first child127, second127 and parent52; no later work.
- Skip or falsely succeed a failed-exec request: the owner must reject missing
  authenticated request/terminal evidence; never accept fabricated status/output.
- Retain the first failed child or replay its collected identity: reject reuse or
  stale wait before it can satisfy a later child; freeze exact native error,
  stopped/terminal/close/reclaim oracle. A timeout does not establish cleanup.
- Wrong WITNESS after both failures: helper91, parent53, stdout only
  `exec errors ok` newline; no healthy pipeline.
- Corrupt healthy bytes with otherwise normal lifecycle: ordinary exact-output
  checker rejects despite exit0 and completed cleanup.
- Leak unflagged fd3 into the closure helper: helper95, parent55, stdout only the
  exec/argv/pipeline prefix; no final diagnostic or success marker.
- Close or misroute parent stderr after child failure: the final diagnostic must
  fail its stream/status contract; native mutation/error/cleanup identity must be
  recorded rather than guessed from a missing line.

Mutants are separate cases; preserve the positive script unchanged. Freeze actual
slot/generation map, denied-request facts, admitted image counts, permitted output
prefixes and exact cleanup before running. Native observations must be privileged
and bound to real instances; names, POSIX IDs and status text confer no authority.

## Delivery

Supply sealed source/support export including every invoked test driver and its
frozen inputs, current affected regressions/host checks, exact compiler/tool/SDK
pins, target ABI, linked owner resource review, native logs, observation oracle and
all failed attempts. The preceding recovery export omitted the legacy harness;
include that dependency explicitly this time. Userland will replay independently
through the existing owned runner with sequential3600-second native deadlines,
1800-second review ceilings,512MiB streams and unchanged guest watchdogs.

Host syntax/reference checks are only preparation. Their /inputs/ relocation is
explicit and does not execute original target paths or prove native authority,
resource fit or epoch cleanup. See the linked evidence checkpoint below when
available. No sibling implementation changes are authorized by this local handoff.
Scratch and real serial session composition, SI-07, shared SDK, independent reviews
and full M3/R1 remain open.
