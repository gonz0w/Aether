# Actual musl read/write-lock contention

Aether's bounded lifecycle fixture exercises upstream private, untimed rwlocks
using existing native waits/wakes. `contract.md` records preimplementation scope,
forbidden outcomes and test selection. Production adaptation remains userland's.

Two child readers hold the lock concurrently while the parent's try-write fails
without mutation. They unlock only after the writer enters its actual wait seam;
writer acquisition must then observe no active readers. In batch two the parent
holds a write lock while both readers register waits, rejects try-read, then
unlocks. Both readers enter; joins, empty lock/wait records, distinct IDs, TLS and
full mapping quota are checked. Supervision repeats completed generations.

The deliberately skipped parent writer lock makes the second-batch reader
exclusion check fail at exact status 251 in both domains. Generic panic/timeout
cannot satisfy that oracle. Seven pinned musl operation sources are rebuilt
unchanged; only the existing private syscall header and admission adaptation
apply. No new suppression, kernel primitive, child budget or dependency version.
The functions named timedrdlock/timedwrlock are called with null deadlines;
clock, timed-lock, process-shared, fairness or cancellation support is not claimed.

Reproduce the complete suite with `python3 scripts/thread_smoke.py
--pthread-lifecycle --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku
--tools-lock /Users/cam/DEV/Aether-userland/experiments/musl-reference/tools.lock.json`,
and repeat with `--large`. Raw suite receipts bind source snapshots, commands,
tools, executables/envelopes/ISOs, terminal outcomes and UTC timestamps.

No sibling files, release pins or kernel/build bytes change in this slice. Earlier
memory/raw-thread/M4 results remain retained coverage, not fresh executions here.
Independent consumer review and full libzpool/R1 integration remain open. Next is
pthread key/destructor isolation and cleanup, followed by explicit time/deadline
contracts before detached lifetimes and measured service budgets.

Final qualification passes both complete 28-case profiles (56 target cases),
including the exact status-251 bypass rejection, all 98 Python tests and Zig
host checks. Clang-format, workflow and diff checks pass. All seven rwlock
sources compare unchanged across 18 producers per profile. Both target attempts
passed with frozen sources; no failed qualification attempt occurred.
