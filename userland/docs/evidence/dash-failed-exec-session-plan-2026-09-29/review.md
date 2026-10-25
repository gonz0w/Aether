# UL-007 failed-exec session preparation

Prepare the next consumer-owned workload after RECOVERY-01–06. No runtime, sibling,
helper, previous script or accepted evidence changes. Read current owner source:
session-client currently rejects every path except /inputs/helper locally with
EACCES. It therefore cannot supply the required owner-backed ENOENT/EACCES split;
a pathname-only special case returning ENOENT would not satisfy this handoff.
The native owner must validate lookup and non-executable object denial, then prove
failed-child collection/reclaim before reuse. Native implementation remains pending.

Foundations O/I/E, Testing TD/TC/TE, Coding CP/CS and Distribution PX apply.
Experience output/stream rules remain unchanged. This is a bounded fixture, not a
public diagnostic redesign. Close stderr only on each deliberately failed external
command to avoid coupling acceptance to dash's human diagnostic spelling and the
32-byte observation limit. Require the parent's later stderr diagnostic separately.
Do not claim command-error diagnostic delivery; that remains separate coverage.
No /dev/null, scratch filesystem or real-prefix installation is introduced.

Simpler alternative: reuse the old isolated failed-exec script. It cannot prove
healthy commands/pipeline work afterward in the same shell or across three parents.
Reuse its missing/denied path semantics and the unchanged argv/copy/closed helper;
add only the continuation needed. No existing runtime can be removed now.

Pin exact new script/expected streams/helper/plan/manifest before checks. Use owned
30-second commands with clean environment and16MiB streams. Syntax and ShellCheck
on the original; build the unchanged helper with pinned Clang21.1.8 C17 and host
SDK, then execute a transparently path-relocated host reference under private build/.
Only /inputs/ path tokens change for the host; original target script is not run.
A mode0644 ordinary file supplies host EACCES, an absent sibling supplies ENOENT.
Pin compiler, Python, shell, ShellCheck, host SDK metadata, source and derived bytes.
All outputs/attempts stay retained; no real-prefix files or sibling changes.

Host controls: wrong missing result, wrong denied result, skipped denied command,
wrong WITNESS, fd3 leaked into final helper, and corrupted healthy data. Positive
must exit0 with exact separate streams. First five controls must fail with specified
shell exits; byte corruption must finish but fail exact stdout. These test script
predicates and host process behavior, never native authority or cleanup.

Technical reviewer: this Codex task. Native owner reconciliation, slot/lifetime
and resource fit, negative native identities/cleanup, linked images and independent
consumer replay remain pending. UL-007/M3/R1 stay open. Update handoff/current state
and coverage, run quality/syntax/whitespace checks and preserve earlier seals.
