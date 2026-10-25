# Suspend-frame preparation

Prospective scope: define the next bounded SIGCHLD/suspend contract in the existing
native shell reference, and prepare its two-mask signal-frame codec. No syscall,
scheduler hook, remote signal route or consumer acceptance is introduced here.

Requirement: handler execution uses the temporary suspend mask plus action/self
blocking; its return payload restores the original mask and resumes with EINTR.
Forbidden: restore the temporary mask, execute under the original blocked mask,
retain unmaskable bits, alter memory on invalid mappings, or claim wakeup authority
from frame preparation. Existing ordinary entry behavior must remain unchanged.

Affected owner is Aether's private signal codec; userland consumes the future libc
suspend call. Selected checks: distinct-mask entry/return and EINTR, invalid mapping
no-write, semantic mutants swapping the masks, full host checks, Zig format and
x86_64 object compilation. Existing entry code remains byte-for-byte unchanged;
no runtime caller uses the new helper, so native wakeup qualification is deferred
until integration. Preserve released pins and sibling files. Record sources/tools,
all attempts and final checks; no new build flag, dependency or allocation.

SE-01–05: reuse checked entry serialization; an added narrow helper avoids changing
all ordinary callers. Reusing one mask is incorrect for sigsuspend. The helper
adds one bounded Entry copy on the stack, no retained state or service boundary;
it removes a need for a future second user-frame write/patch after validation.
Actual scheduler and lifecycle complexity belongs in the next implementation.
Pointers/backing slices retain the original codec's caller-owned lifetime and
serialization requirements; candidate output is publishable only on success.

## Results

PASS: 11 codec tests in Debug and ReleaseSafe, including 16 original/temporary
mask combinations and invalid-stack no-write. Each deliberate mask substitution
fails with TestExpectedEqual in the named suspend test. The production source is
never mutated by these controls. ReleaseSafe x86_64 freestanding object generation
and the full host suite (101 Python tests plus Zig/pins) pass. No unexpected attempt
failed. Source snapshots contain 264 files; only native_signal.zig changed relative
to the prior sealed runtime. The ordinary entry and return function text is verified
unchanged. No native caller uses the added helper; QEMU wakeup tests were not run
because routing and scheduling are not yet implemented. This is not a native
background-wait result, consumer approval, or release-readiness claim.

The helper copies one fixed Entry value and delegates all fallible mapping/frame
checks before backing writes. Only candidate mask assignment remains afterward.
Candidate output must not be published on error. Actual scheduler state/resource
cost and pending-bit commit ordering remain obligations for the integration step.

Reproduction: checks.json contains exact host, Debug/ReleaseSafe, target compile
and semantic-control commands; check.py captures their outputs and verifies frozen
inputs. Generated mutant copies and target object are retained in this packet.
Existing `zig build test` includes both new tests via native_execution's codec test.
