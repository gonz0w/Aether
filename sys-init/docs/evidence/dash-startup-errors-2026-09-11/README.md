# Script startup allocation and unknown-outcome checks

2026-09-11: nine final native cases pass using the already verified ABI17 kernel,
script worker images and enforcing16 KiB code/4 KiB stack profile. All ten previous
startup/stop/launch-failure supervisor images rebuild byte-for-byte unchanged.

Six cases deny channel allocation by withholding the factory grant, at each of
the first and second allocation positions for file, stream and shell startup.
The actual kernel response is EACCES(-13). File failure reports1605/reclaimed0;
stream failure reclaims the file provider and reports1605/reclaimed1; shell failure
retires stream startup file handles, observes stream17/file17 and reports1605/
reclaimed2. Retained endpoint cleanup completes before provider retirement.
These are denied-grant allocation errors, not native quota/exhaustion witnesses.

Three additional cases reclassify a confirmed no-effect allocation or launch
error as Unknown inside the test binding, at the first channel, second channel
and shell launch. This deliberately injected response closes the owner's state.
The ordinary startup path rejects1604/reclaimed0 with no provider terminals.
Source review confirms the Known check precedes all cleanup. These cases execute
the composed fail-closed branch on Aether; they do not show that a real kernel
operation had an ambiguous outcome or qualify recovery after such an outcome.

The test-only cfg fields/hooks disappear from normal builds. No release behavior,
protocol, owner algorithm, unsafe boundary, dependency, shared pin or sibling
changes. Exact commands and artifacts are retained. Builds reuse the frozen local
ABI17 stage from ../dash-startup-abi17-2026-09-11 with only script_lifecycle.rs
replaced. That packet retains the base sources and tool/input identities.

## Retained failed attempt

The first native test expected EPERM(-1); actual missing-grant allocation returns
EACCES(-13), as the frozen channelOperation contract specifies. The test's errno
assertion rejected1606 before exercising rollback. Its source, build/native logs,
image and results are retained under attempt1. Correcting only that test expectation
produced the final nine passing cases. All ten compatibility builds also passed
in the first attempt. The failed attempt is not counted as successful rollback.

## Review, documentation impact and limits

The gap was composed startup coverage, not missing runtime machinery. Reuse the
existing bounded fixture and owner; no new manager or error recovery protocol.
SE-01–05: component-only tests are simpler but do not execute provider rollback
from the ordinary entry; test-only binding controls supply that missing witness.
No production complexity is added, and no correctness check is removed.
O-01/04, I-01/03–06 and E-01–08 apply without a new exception. Existing source
retains unknown outcomes and does not automatically retry or reclaim them.

The adapter reference, prototype guide, BG-067, current plan and quality inventory
record this scope. Launch EINVAL and both allocation positions now have composed
coverage; general kernel failure coverage and recovery after cleanup/protocol
failure are not claimed. Do not expand the matrix merely to fill deferred scope.
The next product boundary remains sustained wait/reuse/authorized shutdown and
selecting the useful session integration with its producer handoff.

## Validation

All ten local development gates pass in `run-c_fadkit` with unchanged checked
sources. Maintained binding matches the executed source. All released lock hashes
are unchanged and `git diff --check` passes. The nine native outcomes and ten
byte-identical compatibility builds are retained separately above.
