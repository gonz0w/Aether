# Bounded descriptor and transport mask guards

Before implementation: mask via the authoritative native context for complete
startup, fcntl, dup2 and startup I/O operations. Keep stack-local nested prior
masks, preserve errno/results and refuse all mutation when acquisition fails.
Restore failure terminates this fixture with exit 125; it cannot resume with an
unknown mask. No handler delivery or signal terminal encoding is enabled.

Reuse small explicit wrapper/body boundaries around current operations. Masking
only channel traps is insufficient because aliases and request/reply ownership
span traps. No new service, lock, kernel state or ABI is needed; existing poisoned
unknown replies and complete EIO close policy remain. Remove no existing fixture.
Scope is the single-context bounded shell facade; indefinite I/O requires a later
cancellation contract. Add native mask observations during every partial transfer,
nested descriptor calls, acquisition failure and fatal restore rejection, plus a
broken-block control. Run complete command and host suites; kernel and non-shell
profiles are unchanged. Actual queued-handler injection remains gated on delivery.

Implementation uses existing C indentation (four spaces in startup facade/probe,
two in legacy transport), with no whole-file formatting migration. Compiler is
pinned Clang 21.1.8, freestanding C11 with existing strict warnings. No new source
file, FFI or dependency was introduced. Stack mask pointers are synchronous,
eight-byte owned locals; the existing raw trap has a compiler memory clobber.
No global guard depth or longjmp cleanup token is retained.

The first launch used the consumer's differently shaped lock and failed before
build creation (KeyError: tools); native-attempt-1.log preserves that failure.
The retained native harness lock is used by the qualified run.

Reproduce from repository root using the matching strict SDK and retained lock:

```sh
python3 scripts/launch_smoke.py --command-runner --libc-build /absolute/strict-sdk --tools-lock /absolute/native-tools.lock.json
python3 scripts/regression.py
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

The run used Aether-userland/build/native-c-5olokhku as a read-only SDK and
zig-out/init-capacity-2026-09-06/tools.lock.json. Artifact/tool digests and commands
are recorded by the harness; the immutable SDK archive is retained in
../init-composed-capacity-2026-09-07/sdk-inputs.tar.gz. No sibling file is written.
M4's first QEMU launch was denied its temporary Unix socket by the sandbox; the
same suite passed with the required local-socket permission. Its failed output
directory is retained in target-artifacts.tar.gz alongside the qualified runs.

This is the implemented bounded mask boundary, not asynchronous signal delivery.
Actual queued-handler/longjmp injection, combined close errors under delivery,
raw action/query compatibility and signal terminal encoding remain open. Other
native mask/pthread profiles share unchanged kernel code; the shell facade is
compiled only for SHELL_STARTUP. Full command and M4 compatibility runs are selected;
no new pthread profile qualification is claimed.

Results: all 244 command-runner cases, seven M4 cases and 98 Python host tests
pass. The positive guard probe completes two generations/four reclaims; negative
controls retain exactly terminal 88 or 125 and owner 1501/reclaimed0. Workflow,
Python syntax and simplicity/pin checks pass. Sources stayed frozen during target
runs; no failed native semantic attempt occurred. The pre-build lock mistake and
sandbox socket denial are retained as described above.
