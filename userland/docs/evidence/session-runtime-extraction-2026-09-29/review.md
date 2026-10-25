# UL-007 bounded runtime extraction review

Requirement: the maintainer explicitly assigned the bounded libc/POSIX runtime
implementation to Aether-userland in this chat on2026-09-29. Aether retains ABI,
capability/grant enforcement and fixture-owner responsibility. This clears the
ownership gate, not independent review, native acceptance or publication.

Scope: extract the accepted private AENMX008/ABI23 session client into a runtime
object and application startup/policy object. Retain exact borrowed transport,
startup, memory, fork-stage and libc rebind bytes with provenance. Preserve upstream
musl source/terms, strict memory patch, public/internal mask state, protocol frames,
per-process descriptor state, poison handling and cleanup. No sibling modification,
UL-058 behavior change, package/service machinery or real-prefix installation.

Foundations O-01–05, I state/error/compatibility and E-01–08; applicable approved
Coding/Testing clauses and SE-01–05 apply. Pin previous seals, producer/SDK/source
files, compiler/flags and selected archive inputs before consumption. Reuse the
unchanged owned command runner with absolute tools, explicit cwd/environment,
private build outputs, bounded streams/deadlines and receipts. Preserve attempts.

Application owns dash arguments/environment/helper lookup policy. Runtime owns
bootstrap, channels, FD/process/mask state, copy/exec/finalization. Keep fixed native
identity/binding limits visible: this is an experimental008 adapter, not general
POSIX or a new bootstrap version. Reject a repeated startup before channel effects.
Application policy can narrow accepted exec requests; native owner still enforces
actual image authority. No policy callback grants rights. A missing memory adapter
must fail the local component gate even though libc can supply linkable symbols.

Tests: compile/link native objects with pinned Clang21/LLD; inspect symbols/providers
and static layout; positive component closure and missing/stale/duplicate/wrong
profile controls. Rebuild parent/helper and replay actual serial composition using
unchanged qualified kernel/owner inputs, retaining exact outputs and cleanup if
performed. Changed artifacts require fresh native witnesses; old169-case acceptance
is a baseline only. A later full scripted/recovery/failed-exec/scratch regression
and independent review remain required before SSDK-01–06 completion. New original
C is C17, borrowed generated/upstream style preserved; apply pinned format gate to
new first-party source. Quality/syntax/whitespace checks before checkpoint.

Simpler alternative: archive the fixed wrapper unchanged. Insufficient because it
still chooses shell environment/arguments/path and allows omitted adaptation to
link. Use two direct translation units plus one explicit component manifest, not a
new framework or POSIX service. Complexity removed: startup/application coupling
from the runtime object; retain borrowed headers until scoped replacement review.
No active accepted path or immutable evidence is removed.

Risks: additional translation-unit boundary changes code layout and stack estimates;
copy callbacks, exit interposition and helper rebind must retain exact behavior.
No broad safety/performance claim. Author technical findings recorded here/evidence;
independent reviewer and reader walkthrough pending. UL-007/063 and SSDK promotion
remain incomplete until their actual gates pass.
