# Separate16-slot FILE ledger —2026-10-23

[Maintainer approval](approval.json), [pre-code/security/simplicity contract](../../proposals/FS-FILE-REPLACE.md).
The opt-in fs_file16/fs_replace candidate admits remote aliases0–15, retaining13
shared descriptions,16 AF07 client bindings and four process views. No new fields,
source handles, grants, heap or kernel changes. Initialization uses separate alias
and description array lengths; unsafe writes remain inside each actual array.
Source/target labels never grant console access. Default3–15 and old wire bytes
remain unchanged; the old FILE handler rejects this selected dependency at compile
time on host and target, including its canonical-path variant. No VM ran.

From userland:

- `python3 -B experiments/filesystem-service/check-process-descriptors.py --in-place --replace --file16`
- Add `--paths` for the combined candidate;15 tests/21 compiling semantic controls
  pass in each selection, plus strict Rustfmt/Clippy/host/freestanding libraries
  and compiler rejection of borrowed callback reentry/legacy FILE wire.
- Omit `--file16` for the old profiles:41/42 tests and19 controls each pass.
- `python3 -B experiments/filesystem-service/check-fd-protocol.py`, and add
  `--paths`:10/11 old protocol cases/eight controls each, C/Rust/C interoperation
  and strict C/Rust/UBSan/target checks pass.

The real ProcessFiles/Remote/AF07 service over synthetic host storage verifies:
13 distinct opens;14th description rejected before lookup despite free alias
slots; three further aliases; full16-table exact replacement; low/high mask bits;
shared/independent offsets; per-view flags/exec/settlement; all-four-view inherited
victim lifetime; stale identity/generation; serialized known/unknown copy; failed
close/read/invalid completion zeroing and once-only retirement without replay.
Controls include a falsely expanded description pool and lost low mask bits.
The four in-place tests exercise poisoned storage/canaries and failed construction.

[Compact results](results.json) bind sources/tools/recipes, dependency closure,
controls, outcomes and cleanup. [Concrete layout](layout.json): selected
ProcessFiles<Measure>1464 versus1440 bytes (+24); single-view Descriptors1136
versus1128 (+8); alignment8. Four alias arrays add24 bytes, while the standalone
single-view type rounds its six additional bytes up for alignment. Target const
assertions match host geometry. This is a zero-sized test Channel layout, not the actual
owner resident/code/stack or a native execution measurement.

Four failed attempts remain failed: [1](attempt1.json) and [2](attempt2.json) had
passing15 tests but an incorrect13-case oracle; a relative-path edit failed before
applying and accidentally repeated it once. [3](attempt3.json) found the selected
suite omitted new-shell rejection while a child remained live; add the actual
Busy assertion. [4](attempt4.json) rejected a premature-close mutant by unwrap
rather than the required assertion; observe close count immediately. Production
ledger code did not change for these harness corrections. No warnings or semantic
control gates were suppressed. All11 owned test/source/binary trees are disposed;
only compact results and short failure extracts remain. Current Python3.14.7 ran;
minimum3.10 runner and independent review remain missing coverage.

This completes the separately selected ledger/build slice only. The new selector
range is fenced off from old FILE/startup contracts. Matching explicit versioned
FILE/C map/fork/exec/startup consumers, public mixed stream/FILE dup2 semantics,
complete owner fit within49152 code/8192 data/guarded stack and later separately
authorized native qualification remain open. No new ABI, wire fallback, writable
home grant, persistent executable loading, package/Zsh/TTY/ISO readiness or
independent acceptance follows. Root STATE owns integration and next action.
