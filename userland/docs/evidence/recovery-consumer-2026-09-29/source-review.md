# Scoped consumer source review

Reviewed sealed source-review.patch and the corresponding restored source. The
only kernel behavior change is final completion for the private pipeline-session
profile: zero observations still requires30 reclaims; exactly three observations
require the recorded cumulative count between3 and30 to equal actual reclaims.
Worker admitted flags, channel ownership and zeroed channel storage still gate
final success. No changed authority, operation number, allocation or concurrency
mechanism was found in this diff. This scope justifies the producer-selected full
capacity suite plus the unchanged non-pipeline command branch, rather than claiming
prior358-connection/431-runner observations cover these new bytes.

sessionObservation accepts only the supervisor and exact0xa001 grant. It checks
ordinal,176-byte frame, pointer overflow/access and record padding before reading
streams into public output. All workers and channel owners/pending bytes must be
absent; reclaim delta must equal copies+parent. Counters change only after valid
publication. User/helper text cannot invoke this privileged observation path.

Recovery fork boundaries require no retained prior child handles. Existing pipe
state determines retirement; allowing the already-created healthy pipes at fork3
does not clear their state. The retained-reader predicate checks real pending
parent wait and pump write with a live read binding after the one helper terminates.
Only then does it stop the parent. Existing orphan cleanup observes terminals,
closes/reclaims and waits for pipe retirement. It never treats a watchdog timeout
as cleanup. The wrong-EPIPE case changes the exact native response to EIO and checks
that the mutation ran; pump98 and parent42 are denial evidence. Stale wait checks
ECHILD and untouched status after prior collection, before the next fork.

Native source remains owner-owned; no implementation changed here. Consumer
checker independently reconstructs slot/generation identities, exact status and
admission sets, phase order, separate streams and final reclaimed totals. Five
local owner hashes will be bound to the sealed linked stack assessment before
acceptance. This is contributor review plus executable evidence, not a separate
human reader review, formal whole-program proof or broad source-audit completion.

Export gap: recovery replay-inputs omits docs/evidence/init-command-handoff-2026-09-08
run.py and its frozen inputs even though it requests their five regressions. The
consumer separately pins the historical driver and21 files against the historical
manifest; the frozen input manifest must equal final legacy import_manifest.
The supplement is explicit, byte-verified and retained, never treated as original
recovery-export membership. No source replacement or tool substitution is allowed.
