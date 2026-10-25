# Pthread key/destructor lifecycle

This bounded Aether fixture uses actual pinned musl key/TSD implementations.
`contract.md` records the preimplementation requirements and test selection.
Production adaptation remains owned by userland; no sibling files are changed.

Two children observe null initial values despite the parent's value, set distinct
records and retain them across scheduling. At exit, callbacks must run on the
owning native thread and observe that musl cleared the key before invocation.
One callback rearms once and must run twice; another always rearms and must stop
at PTHREAD_DESTRUCTOR_ITERATIONS. Exact counts are checked after real join and
native retirement, before record reuse.

While both children are gated, the parent deletes a key carrying values in all
three threads. No destructor may run. It creates a new valid key before reads,
and all threads observe null under that key. No deleted-key access is tested or
permitted. Parent values remain isolated; joins restore thread lists and quota.
Two batches use the unchanged four-admission budget, and supervision exercises
fresh-generation completion. A skipped callback must fail exact terminal status
263 for both domains; a timeout/generic panic is insufficient.

Three upstream sources (`pthread_key_create.c`, `pthread_setspecific.c`,
`pthread_getspecific.c`) are rebuilt unchanged only for the new key variants,
using the established syscall-header/admission adaptations. This introduces
musl's actual TSD storage into those child mappings; it does not raise native
budgets or add a kernel key service. Existing profiles retain their source closure.

Reproduce with `python3 scripts/thread_smoke.py --pthread-lifecycle` and `--large`,
passing `--libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku` and
`--tools-lock /Users/cam/DEV/Aether-userland/experiments/musl-reference/tools.lock.json`.
Suite receipts retain exact commands, source snapshots, tools, artifacts, terminal
outcomes and timestamps. No kernel/build bytes or release pins change, so older
memory/raw-thread/M4 results remain retained coverage, not new executions here.

Detached/cancelled lifetimes, arbitrary destructor behavior, key-capacity limits
and independent production acceptance remain open. Next: explicit clock and
deadline contracts and an actual timed-condition witness, before detached cleanup
and measured libzpool service budgets. This is not full filesystem/R1 readiness.

Final qualification passes both full 31-case profiles (62 target cases),
including exact status-263 callback rejection. All 98 Python tests, Zig host,
Clang-format, workflow and diff checks pass. The three upstream key sources
compare unchanged in both key variants on both profiles. Both frozen target
attempts passed; no failed qualification attempt occurred.
