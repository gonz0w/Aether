# Bounded owner-local lifetime admission — 2026-10-04

The [before-code contract](contract.md) and
[private reference](../../NATIVE-THREAD-REUSE.md) extend only an explicit opt-in
profile to512 lifetime child admissions. Live slots remain two, existing memory
bounds remain unchanged, creation is still parent-only and ordinary profiles
retain the four-admission limit. Retirement never replenishes either budget.
Successful creation produces monotonically increasing IDs scoped by the domain
thread grant. No global table, implicit grant, SDK/pin/sibling change is introduced.

Fresh final five-case matrix passes:512 cycles in each isolated domain; the same
positive extension with release-artifact=true; default-four exhaustion; actual
same-ID enforcement mutant failing254; and three fresh supervised admissions.
Cycles check zeroed reusable backing, foreign-grant denial without TID mutation,
nonrepeating IDs, stale ID denial while another child exists, running retirement
-16, pinned memory denial, exact clear-TID completion, stopped observation,
retirement and budget restoration after unmap. Final exhausted creation returns
-28 without changing caller storage or publishing a child. Old memory/TLS/output/
exact64-yield oracles remain. This is a bare-child fixture, not production musl TCB
or full-engine qualification. Child stack/cookie pages are4KiB each.

Attempt1 incorrectly retained an entropy build flag without a device; kernel
correctly rejected the absent device. Its inventory entry also failed the reference
status schema. Both failures, recipe/probe/workflow bytes and raw logs remain.
Attempt2 corrects these fixture setup problems and passes four cases. Fresh
attempt3 adds release-designated positive acceptance and records actual QEMU
commands. It passes all five without changing runtime bytes. First scoped guard checks
expected the reuse guard before the existing missing-image memory guard; that
failed checker is retained. Corrected checks supply the explicit native image
and single-core mode, then exercise the intended earlier configuration errors.

Full137 Python host cases plus Zig/Rust/pins/workflow pass. Required older pair
and actual pthread lifecycle suites run in default/large memory modes, together
with hardware/native entropy, block and seven two-core regressions. Exact counts
and outcome receipts are retained by checks.json in the archive. Missing independent
reader/SDK adoption remains coverage; this packet cannot claim release readiness.

Reproduce from pinned offline inputs: `python3 docs/evidence/native-thread-reuse-2026-10-04/setup.py`
then `python3 docs/evidence/native-thread-reuse-2026-10-04/native.py`. The intake
verifies preceding seals and all1979+5037 archive members, stages owned SDK/source
copies, and retains upstream terms. Legacy regressions receive a private byte-
identical evidence.json filename and adjacent pinned musl source archive; original
SDK remains unchanged. Clang/LLD21.1.8, Rust1.98.0, Zig0.16.0 and QEMU11.1.1/
qemu64/q35/TCG flags/tools/sources/time/artifacts are recorded. Builds180seconds,
VM30seconds, owned teardown3seconds; forced teardown fails. Every owned archive
member is read back before deleting only verified duplicate output roots.

The host's selected queue policy still needs82 simultaneous workers and more
backing than this fixture supplies.512 is an experiment lifetime ceiling justified
by281 observed creates, not a production workload guarantee or simultaneous capacity.
Next audit worker-origin creation and owner-local backing/geometry before extending
those independently. Identity/configuration, feature closure and actual complete
engine startup/fini/restart precede granted filesystem/package composition.
