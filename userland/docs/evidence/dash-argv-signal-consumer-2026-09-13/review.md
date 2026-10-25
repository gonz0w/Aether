# UL-007 unchanged argv/signal consumer qualification

Pre-execution scope, 2026-09-13: reproduce the seven final producer argv/signal
profiles from SHA256SUMS a95c142b4f21038bf102794f33ae12830c1d7a6dfa58e3785620668cc4c2db0c.
Aether owns its private adapter; this checkout validates exact consumer inputs and
native outcomes without changing sibling sources or installing SDK content.

Reuse the prior pinned scaffold, SDK, tools and owned process runner. Overlay only
verified final producer sources; verify every archived member and expected harness
source hash. Keep output in a fresh build directory. Select the producer's existing
seven-case AST filter with only SDK/tool paths adapted. No target behavior edits.
Native suite budget 600 seconds, guest watchdog 30 seconds, outer stream bound
512 MiB; require complete process cleanup and all seven exact case identities.

Check argv.sh and signal-table.sh plus helper and manifest identity against local
consumer bytes. Positive cases require child0/parent0/backend17 twice and six
reclaims; argument/environment corruption require child91/owner2130; skipped helper
requires child0/owner2310; omitted signal post child0/owner2175; bypassed PID guard
parent signal10/owner2176. Each denial reclaims zero. Independently compare complete
serial terminal sequences and supervisor markers after receipt completion. Output
byte validation is an owner assertion backed by actual backend readback, not a
separate host capture of shell stdout. Preserve this distinction.

Foundations O/I/E, Distribution PX and adopted TD/TC/TE/CP clauses apply. Native
identity remains authenticated connection authority; positive PID is not authority.
Single-child pipe/readiness/terminal/reply ownership and bounded synchronous self
USR1 support are fixture limits, not general POSIX signals/pipelines. Preserve
upstream licenses and all immutable history. No new dependency or UI behavior.

Run local quality gate and Python syntax checks. Do not count the producer's 287
cases as local execution or reuse old runtime regression as proof of changed pipe
paths. Full local regression and broader pipe/exec controls remain a subsequent
qualification scope; this selection establishes only these two unchanged scripts.
Update workload documentation, STATE/BACKLOG/ROADMAP and draft coverage. Technical
self-review and independent reader/security review remain separate; independent
reviews are pending. No M3, installed SDK, assembly or release completion.

Simplicity: reuse the frozen harness and existing focused selector; no dispatcher
simulator, new runner framework or duplicate package machinery. Nothing can be
removed before the matched public SDK and wider workload gate are available.
