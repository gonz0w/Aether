# Proposed local-output delivery candidate (UL-059)

This host-only C helper exercises delivery/cleanup of the six inert
[proposed text fixtures](../../docs/RUNNER-LOCAL-OUTCOMES.md). It is not called by
runner.c, packaged, installed, or mapped to native descriptors. Logical sink0/1
selects a callback route for stdout/stderr; it does not confer native authority.
The caller must supply already-selected text and already-owned sinks, with their
actual authority and binding validation performed elsewhere.

Run from the repository root, offline with the provisioned pinned Clang toolchain:

```sh
python3 -B experiments/command-runner/check-local-output.py
python3 -B docs/quality/check.py
```

The checker provides `--help`, `--version`, and `--plain` (ASCII is the default).
Exit0 means its test oracles passed, exit1 an operational/test failure, exit64
invalid usage, and exit130 interruption. The printed build path locates private
logs, exact commands, source snapshots and summary.json. Each subprocess has a
30-second deadline, 16 MiB file limit and recorded group cleanup. The candidate
runs with strict C17 and UBSan on the recorded macOS host, not under Aether.
No ASan or native sanitizer result is claimed.

## State and callback contract

`local-output.h` defines one single-use, zero-initialized state and synchronous
write/close callbacks. All objects must be live and disjoint; callbacks must return
normally without re-entry or concurrent mutation. No allocation or pointer-validity
check is supplied. Invalid initial input returns1 without callbacks; the caller
retains responsibility for its still-owned sinks. Reusing the state returns1
without changing recorded facts or issuing any callback.

The caller chooses one of help/version/usage/unavailable/denied/capacity and supplies
1–512 immutable text bytes. The latter three require the corresponding complete
admission error -2/-13/-16 as input; this consistency check does not establish that
an owner actually rejected a launch. Original action, intended exit and admission
error remain separate from delivery and cleanup. This low-level helper does not select parser actions, decode admission records
or select text; the host frontend below now supplies that integration. Fixture integrity is
checked against the retained proposal manifest before host execution.

Known write success advances only the confirmed count, at most the remaining
length. Known zero or negative errno ends writing, then attempts both sink closes
once in role order. There is no errno retry, including EINTR; this callback seam is
not a POSIX write implementation. Positive progress bounds writes by message length
(at most512), plus at most two closes. The text bound is a local experiment limit,
not evidence of any native sink capacity.

Unknown, oversized, contradictory or malformed callback results prohibit further
calls on the shared connection. Confirmed byte progress is preserved; unknown
additional effects are not declared absent. A known close error permits the other
close, while an unknown close leaves it unattempted. Delivery failure and individual
close states/errors remain distinct. Callback-reported close success is not native
reclaim evidence. The original intended0/2/64 is returned only after complete
confirmed delivery and both successful close reports; all other outcomes return1.

## Evidence and remaining work

[Host evidence](../../docs/evidence/runner-local-delivery-2026-09-06/summary.json)
contains 6,130 scenarios and four semantic mutations. It checks all six fixtures,
every positive chunk size, every failure prefix with eight failure classes, close
failures/unknown results and combinations, invalid plans, exact stream contents,
original outcomes and re-entry. Mutants detect prefix replay, ignored close failure,
post-unknown calls and wrong-stream output. Independent and affected-owner reviews
remain pending; these tests do not complete native RL-01–12 acceptance.

The host frontend below now connects parser actions and admission rejections.
Native use still needs the owner's reviewed sink-role/lifecycle extension and a new
explicitly pinned bundle.

## Host frontend integration

Run `python3 -B experiments/command-runner/check-local-output.py --suite frontend`.
Default delivery mode remains unchanged. The frontend builds private text arrays
from the verified proposal fixtures; no generated payload is installed. Its public
experiment declarations are in `local-frontend.h`; it is not linked into runner.c.

AF_LOCAL means local delivery was attempted: inspect delivery.exit_status and
recorded delivery/close facts, including operational exit1. AF_ADMITTED hands off
a validated receipt to a future collection path, not a completed command. AF_FAILED
leaves caller-owned resources unresolved; it does not silently close or invent
successful diagnostics. All state is zero-initialized/single-use; re-entry returns
failure without altering earlier facts or issuing callbacks. Callers dispatch on
the returned action, not stale state from an earlier invocation. Callback input is
borrowed const storage only during its synchronous call. Required callbacks are
validated before processing even when the selected branch will not invoke them.

Admission returns known1 plus an actual length and at most32 bytes; any other
certainty, invalid length, padding or generation is rejected by the real decoder.
Only three complete rejection errors map to the proposed local diagnostics; other
validated errors are retained and remain operational failures. Missing or ambiguous
admission is never inferred to mean no admitted child. The test callbacks confer
no native authority and cannot establish native no-admission/cleanup guarantees.

The [frontend receipt](../../docs/evidence/runner-local-frontend-2026-09-06/summary.json)
records280 scenarios/three mutations. Native role binding, runtime fixture packaging,
collection handoff, remote recovery and affected-owner/independent acceptance remain
separate work. Next: consolidate the owner handoff with the completed consumer
checks and exact remaining native requirements.
