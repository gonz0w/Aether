# Host finalizer candidate (UL-067)

The standalone [finalizer](finalizer.c) implements the shutdown-state proposal
from the [native SDK audit](../../docs/research/TOYBOX-NATIVE-SDK.md). It is not
linked into Toybox, musl or a native image. CAT-06 remains native NOT RUN.
Original source is BSD-2-Clause; no upstream code or shared pin changed.

Call tf_finish with a private zeroed state, command status0–255, flushed=1 and
valid close/diagnostic callbacks. The caller already owns all three roles. Logical
roles0/1/2 mean input/output/diagnostic; they are not native FD or grant assignments.
The caller must actually complete upstream callbacks and flush before entry; the
flag checks a precondition and cannot prove that flushing occurred. Invalid entry
consumes the state but performs no callbacks or ownership transfer; the caller
retains cleanup responsibility. Borrowed objects must remain valid and disjoint.

The function consumes input then output locally before calling their close
callbacks. Known failures preserve a prior nonzero status or promote0 to1. A known
input/output close failure requests one cleanup diagnostic, then closes the
diagnostic role. Its callback owns bounded delivery; this code does not format
text, retry partial writes or promise successful diagnostic output. Failure while
closing the diagnostic role cannot recursively request another diagnostic.

Unknown or malformed callback results stop all further callbacks on the shared
connection. Remaining local roles become consumed/abandoned, not remotely closed.
The caller must retain that uncertainty for owner-supervised cleanup. A known
close failure also does not claim release. No descriptor state here substitutes
for native reclaim, grants, remote recovery or cross-generation observation.

Recursive entry returns failure, marks re-entry and forces an otherwise-successful
outer result to1, without repeating effects. Completed repeated entry returns the
stored outcome unchanged. Callbacks may reenter through this API but must not
otherwise mutate the state or ops. This is synchronous single-thread code, not a
thread/signal-safe primitive. It allocates nothing and makes at most four callbacks;
callback duration and transport bounds remain the callback provider's obligation.

## Reproduction and evidence

From repository root with pinned Clang21.1.8:

```sh
python3 -B experiments/toybox-reference/check-finalizer.py
```

The driver uses private build output, strict C17 warnings, UBSan with no recovery,
pinned formatting and owned60-second process bounds. It copies source/plan before
execution and records compiler identity, flags, logs and hashes. Python3.12+;
help/version use stdout0, invalid usage stderr64. No native SDK, VM or network is
used for this host suite.

[Retained evidence](../../docs/evidence/toybox-finalizer-2026-09-06/summary.json)
contains 2,560 Cartesian scenarios: each close and diagnostic callback returns
success/error/unknown/malformed, with prior status0/64 and re-entry at every
possible callback position. A separate expected event transcript checks ordering,
local consumption, diagnostic liveness and abandonment; completed replay cannot
change state. Six invalid-input controls check null state, out-of-range status,
missing flush acknowledgement and missing callbacks. Three semantic mutants lose
prior status, continue after unknown close or reverse close order; all must fail
assertions, not merely fail to compile. UBSan is host evidence only.

No native termination hook, upstream callback/flush execution, real partial
diagnostic delivery or lifecycle reclaim is exercised. Same-task technical review
is recorded; independent review remains pending. Next: specify the private stdio
write bridge over admitted command roles, with vector bounds and no replay after
unknown transfer. Native integration still requires owner-produced child roles,
truthful umask state, selected admission, real shutdown witnesses and all CAT cases.
