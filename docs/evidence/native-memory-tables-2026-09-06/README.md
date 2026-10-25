# Native memory table reservation — 2026-09-06

[Contract and result](../../NATIVE-MEMORY.md#page-table-reservation-result--2026-09-06).
This change makes table-slot selection a complete precommit transaction and routes
native map/protect/unmap through it. Current quota/arena and all ABI bytes remain
unchanged. Multi-leaf geometry is host-planner coverage; the current native arena
fits one leaf. This is a prerequisite, not a larger-memory or OpenZFS runtime.

## Inputs and checks

contract.md retains the requirement recorded before implementation. before.tar.gz
contains the two edited kernel files as found at turn start, including inherited
working-tree changes. attempt-1-sources.tar.gz is the first implementation; the only
later runtime-source-file difference is whitespace in one host-test array literal.
Final sources.tar.gz and results.json under final/ bind the frozen kernel, user,
build and tool-script inputs used by the final verification. No sources changed
during either target suite. The repository was not a clean checkout.

Final timestamped top-level commands and expected exits are in final/results.json:

- `zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`
  passes kernel tests, including three new table-reservation tests, 85 Python
  cases and standards/workflow checks.
- `zig fmt --check kernel/native_memory.zig kernel/arch/x86_64/native_c.zig` passes
  with Zig 0.16.0.
- `python3 scripts/memory_smoke.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock /Users/cam/DEV/Aether-userland/experiments/musl-reference/tools.lock.json`
  passes eleven cases. The strict native-libc/tool pins, envelopes, source hashes,
  build commands, ISOs and serial logs are in the retained suite directories.
- `zig build smoke` with the recorded private output/cache arguments passes the
  default two-core acceptance and framebuffer check.

Host cases cover a request crossing two 2-MiB boundaries, existing/vacant/new
slot selection, exact boundary endpoints, late exhaustion despite sufficient
nominal slot count, missing existing tables, malformed indices and arithmetic,
and all 32 available table slots. The native suite covers allocation, NONE/read-only/
unmapped faults with peer completion, denied authority, deliberately skipped
protection/zeroing, metadata-denial/retry, supervised reuse and stop with live
allocations. Its deliberate wrong stop-kind expectation rejects at result 304.
Timeouts and unrelated panics do not satisfy these oracles.

## Attempts and retention

Initial host tests pass (host-1.json/log). format-1.json records a rejected check:
one new test literal required spaces. No semantic change was made to fix it.
The initial target memory suite also passes all eleven cases, but the default
boot command fails before guest execution: QEMU cannot bind its local QMP socket
inside the sandbox. boot/qemu.log retains `Operation not permitted`.

The final verification repeats host, format, all eleven memory cases and default
boot with local socket permission; every command exits 0. target-attempts.tar.gz
contains both complete memory-suite directories and both boot output directories,
including the failed startup and successful framebuffer capture. No failed output
was overwritten. qualify.py and qualify-final.py are one-off retained wrappers,
not new supported developer entry points or dependency installers. They use the
existing runners and exact local inputs. Removing this experiment does not affect
consumer pins or install host services.

Top-level command UTC intervals are recorded; inherited memory-suite internals
retain exact build commands/artifact identities but lack per-subcommand UTC
intervals. No retroactive full evidence-standard claim is made. No independent
reader review, optimized-mode/stack-high-water, enlarged-arena target witness,
companion acceptance or assembled release is established here. SHA256SUMS covers
all files except itself.
