# Two actual musl condition waiters

The bounded conformance adapter now exercises two simultaneous pthread condition
waiters using existing native wake-count and requeue operations. This is Aether's
fixture, not production userland acceptance. The preimplementation scope and
forbidden outcomes are in `contract.md`.

The first batch signals one eligible waiter and then the other; the second uses
broadcast and requires observed native requeue. Parent-held mutex notification
forces reacquisition blocking. Each batch joins both threads and verifies empty
condition/mutex/thread-list state, distinct native IDs and restored memory quota.
Two batches consume the unchanged four-admission budget. A supervised case checks
replacement-generation completion. A wake substituted for requeue must fail with
both domain terminal statuses 239; timeout/generic panic does not satisfy it.

Only the paired-condition adapter accepts the exact private requeue subset used
by pinned musl: wake zero, move one, destination pointer, no sixth argument.
Shared requeue, other counts and reserved arguments reject with ENOSYS. Native
capability and pointer validation remain the enforcement boundary. Private wake
uses the caller's bounded count. Other lifecycle modes retain their old adapter.
The raw interrupt wrapper borrows no user pointer after return; the kernel owns
validation and wait lifetime. Source uses the existing Clang 21.1.8 reviewed style.

Attempt 1 passed the new workload but failed harness classification: the new
unsupervised case was incorrectly required to report a replacement generation.
The case now uses the existing exact two-domain success oracle. That failed
attempt, source snapshot and raw logs are retained; it is a harness defect, not a
product failure or an accepted run. Final attempts include rejected-input probes.

Reproduction uses the existing `--pthread-lifecycle` and `--large` commands with
`--libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku` and
`--tools-lock /Users/cam/DEV/Aether-userland/experiments/musl-reference/tools.lock.json`.
Each suite records exact commands, tools, source/ELF/envelope/ISO identities,
semantic outcomes and timestamps. `kernel-identity.json` verifies every kernel
source and build.zig matches the prior memory-audit qualification. Its 52 target
memory/pair/M4 cases remain retained coverage, not new executions here.

No timer/cancellation/shared-condition semantics, production libc, filesystem
completion, independent owner acceptance or release readiness is claimed. Next
is evaluating the remaining libzpool runtime requirements against this bounded
threading subset, with consumer ownership retained by userland.

Final qualification: both complete 25-case lifecycle suites pass (50 target
cases total); all 98 Python tests and Zig host checks pass. Clang-format, workflow
and diff checks pass. The intentional bypass reports exact status 239 in both
profiles; earlier successful controls and the failed first attempt are retained.
Sources stayed frozen during each final suite.
