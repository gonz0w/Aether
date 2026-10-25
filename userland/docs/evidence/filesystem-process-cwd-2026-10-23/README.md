# Retained process CWD candidate —2026-10-23

[Pre-code requirement, security/ownership/resource/simplicity review](../../proposals/FS-CWD.md).
A separate fs_cwd producer retains actual service directory handles in the existing
four process records. Relative reads use that process's directory; absolute reads
use the delegated root. Fork shares a retained handle, subsequent directory changes
are local, successful exec preserves CWD, and final native-settled view cleanup
closes the last reference. Known preparation errors preserve old CWD; unknown
lookup or failed close retires every view without replay or false settlement.
No PWD string/cache, getcwd success, new grant, service, channel, worker or allocator.

Run from userland:

```
python3 -B experiments/filesystem-service/check-process-descriptors.py --in-place --replace --file16 --paths --cwd
python3 -B experiments/filesystem-service/check-process-descriptors.py --replace --paths --cwd
python3 -B experiments/filesystem-service/check-process-descriptors.py --in-place --replace --file16 --paths
python3 -B experiments/filesystem-service/check-fd-protocol.py --paths --dup2
python3 -B experiments/filesystem-service/check-fd-protocol.py
```

[Results](results.json) retain all nine principal attempts, final per-child command/
output/tool hashes, exact source/tool/dependency identities and the short failure.
Intermediate passing attempts retain rollups/hashes; two meaningful final cases
were added after them, so the final changed producer selections were checked again.
The selected FILE consumer predates only those cfg-disabled test-fixture additions;
its production sources are unchanged, so its passing result is reused with that
explicit scope. No broad full suite or native guest was repeated.

Final producer results:27 tests/29 compiling semantic controls for16 aliases with
in-place initialization;50 tests/25 controls for13 aliases with unsafe code denied;
old16-alias non-CWD regression15 tests/21 controls. These totals include the12 new
CWD cases, old copy/FD/exec/in-place cases and their applicable controls. Exact root
and CWD lookup tokens/rights, all four records, independent child changes, exec,
settlement/reuse, stale/foreign keys, malformed paths, missing/wrong kinds, Full
before effects and once-only failure retirement pass. Four distinct retained
handles leave11 source file bindings in the same16-slot pool; no extra capacity is
created. All old FILE-description/FD and borrowed-copy controls remain enforced.

Both13/16 CWD dependencies reject existing FILE protocols on host and target for
the explicit CWD-contract guard, before effects. Default component FILE consumer
10 tests/eight controls and selected path/dup2 consumer15/ten controls pass, with
actual C/Rust/C, C17/UBSan and no_std libraries. Strict pinned Rustfmt/Clippy,
warnings, host and x86_64-unknown-none libraries pass. --cwd without --paths rejects
with exit2 before build-tree creation. In-place nonzero backing tests verify the
new Option fields are initialized explicitly, not treated as zero representations.

Actual zero-state Channel ProcessFiles layouts:16 aliases1464→1560 bytes and13
aliases1440→1536, both alignment8. The96-byte delta is four Option<Handle> fields;
both target type checks retain the <=96-byte/alignment guard. This is a type probe,
not complete owner code/resident/stack fit. Existing8192-byte resident and guarded
stack,49152-byte code,16 bindings/13 descriptions/four views and every native time,
worker/channel/authority limit remain unchanged. No new native inputs are selected;
old seals/SDK/released standards pins and the prior native witness stay frozen.

One control-harness attempt remains failed. Closing inherited CWD early produced
expected Rust exit101, but tests reached unwrap errors rather than the required
explicit assertion; the semantic gate correctly rejected that run. Assert the
absence of a premature close immediately after a child's directory change; the
final control now fails its ownership assertion. Production code was unchanged
by this correction. A separate wrong-working-directory recording edit stopped
before changing any file; it is recorded as a precheck failure, not a VM attempt.

Canonical directory selection is intentionally not public POSIX chdir: '/' and
'.' are supported, but parent/symlink/rename/getcwd semantics and matched public
protocol/owner integration remain. No fake getcwd('/'), native CWD, writable home,
Zsh or ISO readiness follows. No new unsafe block or dependency; existing in-place
raw field writes explicitly initialize the added non-owning fields. Technical
review by implementation agent only; minimum Python3.10 execution and independent
review remain open (current3.14.7 passes). Root STATE owns next integration.
Generated build trees are removed after compact readback; active dependencies stay.
