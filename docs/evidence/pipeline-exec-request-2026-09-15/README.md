# Child-requested pipeline exec — 2026-09-15

Copied children now initiate replacement through a private public-execve shim,
without waiting for the owner's token2. After reporting copy readiness and setting
live CLOEXEC flags, each requests /denied, requires EACCES, compares all16 descriptor
flags with the pre-request state, then requests /replacement. The shim supports
only the fixture's three exact bounded arguments and empty environment; this is
not general path lookup or a published SDK exec interface.

A canonical32-byte opcode84 request names image selector, role and generation.
The owner authenticates the channel's native child independently and checks every
field. Denial returns before snapshot/freeze or image changes. Accepted request
receives acknowledgment; only then does the child capture its live table and freeze.
The existing owner validates snapshot and native freeze before image admission,
CLOEXEC holding commit and publication. Acknowledgment alone is not completion.
Successful replacement never returns to old execve. Existing native denied-image
and receipt checks remain inside replacement qualification.

Children can queue requests while the parent continues construction. The owner
still services them in slot order, so this is child-driven request initiation,
not a general concurrent execution dispatcher or actual dash scheduling.

## Qualification

Commands:

- `python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json`
- `zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`

All43 native cases pass on final sources; target case total is112.620 seconds.
Wrong denial errno rejects child127 then owner2730 before reclaim. Positive requires
exact stdin/EOF, stdout, diagnostics and fifteen normal reclaims across3 generations.
Host run returns0 with104 checks. No failed attempts occurred; intentional rejection
evidence remains. Exact commands, tool/SDK identities, timestamps, native artifacts
and serial hashes are retained with source snapshots. Kernel mapping remains
8007680 bytes.

## Compatibility and limits

281 frozen runtime inputs; four private capacity files change, including the new
exec-request header.52/59 previous top-level ELF/raw images are byte-identical.
Seven live-source client ELFs change with token initialization; all prior owners
are identical. Changed clients require their full native regressions. Both new
owners are16360 bytes within16384; retain this limit in subsequent integration.
No kernel/shared adapter/pipe core/SDK/dependency/quota/sibling/released pin change.

Stack request/argument buffers remain live under the existing masked synchronous
snapshot contract. Granted image choice stays owner-controlled, and role/generation
metadata cannot authorize another native process. Unsupported argument/environment
shapes fail locally. No new unsafe boundary or service is introduced. Existing
owner-scheduled profiles remain explicit regression consumers.

Actual dash builtin execution, a general execution/data/wait event loop, signal
interruption, unchanged pipeline/early-reader scripts, SIGPIPE/status composition
and console/TTY integration remain open. Full matching suites and independent
SDK/userland intake are still required. Persistence/OpenZFS, packages, recovery and
sys-init assembly remain R1 work. No full-dash or assembled-release claim.

Preimplementation review/outcome are in NATIVE-SHELL-STARTUP. Runtime/review archives
retain inputs, guidance and test support. collect.py verifies every generated file
against an archive before deleting only this run's owned duplicates; cleanup.json
records verification. Prior packets are unchanged. SHA256SUMS excludes only itself.
Final checks bind Rust1.98 edition2024, Clang-format21.1.8, pins, simplicity snapshot,
workflow, whitespace and frozen runtime sources.
