# Script startup capacity: scoped size review

Nine measurement-only builds evaluated small layout alternatives to the rejected
startup rollback candidate. Eight combinations (compiler-selected versus forced
separate startup, cleanup and provider-finish functions) all measure9,152 bytes.
Constant-specialized launch slots measure10,528 bytes. None fits8,192 bytes; none
was booted. This bounds the attempted alternatives, not every possible redesign.

The eight-build driver and exact commands, candidate binding variants, logs and
raw-image hashes are retained. The constant-slot case retains both changed source
files, command and result. All use the prior capacity attempt's frozen staged
sources and pinned compiler/environment; only recorded local candidate files vary.
`../dash-script-startup-capacity-2026-09-09/build/measurement-only.ld` is diagnostic,
with entry/no-writable-static assertions retained. No accepted compiler flag or
maintained runtime source changes. The original staging files were restored.

`boundary/native_launch.zig` and `program-linker.ld` are copied from the frozen
script intake. The other boundary files are read-only observations of current
Aether, not adopted build inputs. Current command documentation still limits this
profile to8,192-byte code and a separate4,096-byte stack. Current producer progress
qualifies file-description semantics; it does not provide this capacity handoff.

The local [handoff](../../DASH-STARTUP-CAPACITY-HANDOFF.md) states the missing input
and acceptance workload. No sibling repository was edited or request sent.
Existing maintained sources, released pins and previous evidence remain unchanged.
SE review: function sharing is the simpler alternative to a new manager; it saved
no bytes here. Specialization duplicates code and is rejected. Broad runtime
refactoring to satisfy a fixture budget is deferred; no checks or ownership facts
are discarded. O-01/04, I-01/03–06 and E-01–08 apply without a new exception.

## Validation

All ten gates pass in `run-3194elix` with unchanged checked sources. All five
maintained command source/patch files match the previous native stop checkpoint.
Three released lock hashes remain unchanged; `git diff --check` passes.
No new native execution or capacity acceptance is claimed.
