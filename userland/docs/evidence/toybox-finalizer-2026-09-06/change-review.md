# UL-067 host finalizer plan

Implement a standalone C17 callback candidate, no Toybox/libc/native wiring. Entry
requires upstream callbacks/flush already complete and three validated owned roles.
Logical roles are not FD assignments. Consume input/output once, optionally request
one bounded cleanup diagnostic while stderr lives, then consume stderr. Preserve
nonzero command status and promote cleanup/re-entry failure from zero to1. Unknown
or malformed callback results stop all transport callbacks; remaining local roles
are abandoned/consumed without claiming remote close. Never replay effects.

Use synchronous callbacks and a zeroed single-use state; reject invalid parameters
before callbacks. Re-entry must return failure and force an otherwise-successful
outer result to failure; completed replay returns stored result without effects.
No concurrency/thread safety or remote recovery is claimed. Test a Cartesian
outcome/status/re-entry matrix against an independently constructed event oracle,
invalid inputs, repeated calls and semantic mutants. Clang21.1.8 C17 strict warnings,
UBSan, pinned format and owned bounded command evidence; no network/native runtime.

Shared O/I/E, CE/CC/TD/TE apply. Plain API/state only, no new CLI/target text. New
original code BSD-2-Clause. Record all attempts, source/tool/plan hashes, exact
oracles and limits; local quality gate and documentation coverage required.
Independent and owner review remain pending; native CAT-06 is still NOT RUN.
