# Guarded handler entry on known errors

Before implementation: arm the existing pending handler at the return boundary of
an invalid-descriptor fcntl (EBADF) and a denied write through the read-only alias
(EACCES). The handler performs its existing descriptor/diagnostic operations and
deliberately leaves errno=ERANGE. The interrupted wrapper must report its original
error, then normal copy and exact-byte cleanup must succeed across two generations.
A fixture-only skipped fcntl errno restoration must reject client97/owner1501.

Reuse the existing hook/owner and guard. No kernel behavior, extra authority,
allocation or protocol. This is a bounded known-error prerequisite; ambiguous
remote replies/poisoning and nonlocal exits during errors remain separate work.
The negative restoration branch is compile-selected only in the fixture. This is
simpler than injecting remote failures before local error preservation is proven.

Select full command and host/pin suites with strict existing C warnings and scoped
whitespace checks. Freeze inputs and preserve attempts/pins. No sibling changes.
No fresh M4 is claimed for this fixture-only change; earlier evidence stays scoped.

Initial attempt: the new post-handler descriptor oracle incorrectly expected
CLOEXEC, although earlier startup setup explicitly clears it. The positive failed
client97/owner1501. Retain its native artifacts, original client source and initial
passing host log. Correct only that expectation to zero and rerun both selected
suites on frozen corrected bytes. The first run does not establish which other
conditions inside its combined check passed; final qualification supplies that.

Second attempt: both positives passed, but the negative unexpectedly booted.
The negative preprocessor branch had matched startup_begin's earlier errno-restore
sequence instead of fcntl's. Retain the second outputs/client and the adapter used
in both initial attempts. Move the branch to startup_fcntl's actual wrapper and
restore startup_begin unchanged. Rerun both suites on final frozen bytes; a negative
that does not fail is not accepted evidence.

Reproduce from the repository root:

```sh
python3 scripts/launch_smoke.py --command-runner --libc-build /absolute/strict-sdk --tools-lock /absolute/native-tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

This run uses read-only Aether-userland/build/native-c-5olokhku and retained
zig-out/init-capacity-2026-09-06/tools.lock.json. Receipts retain commands, tool
and source hashes, artifacts and serial logs. collect.py verifies the previous
nonlocal packet, simplicity snapshot and archived members, including both earlier
failed attempts. The saved adapter applies to attempts1/2; their saved clients
record the descriptor-oracle correction.

Final results: all 273 command-runner cases and host/pin checks (98 Python tests)
pass on frozen corrected sources. Both positives complete two generations/four
reclaims; skipped fcntl errno restoration rejects client97/owner1501/reclaimed0.
Both earlier failed attempts remain retained with source and artifact evidence.
Scoped whitespace checks pass. Ambiguous-error handler injection and nonlocal
error exits are not qualified by these known-error cases.
