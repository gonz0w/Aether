# Interleaved pipeline construction — 2026-09-15

The private live parent now creates First, forks the writer, closes its First
writer, creates Second, forks the relay, closes First reader/Second writer, forks
the reader and finally closes Second reader. Unlike the earlier fixture, the first
child is copied before Second exists, and later copies receive reduced live tables.
Public fcntl aliases and musl fork/close/waitpid remain exercised. Replacement
workers still perform actual libc pipe I/O with exact ten-byte data and EOF.

An opt-in fork hook prefixes its existing snapshot/freeze with a canonical 32-byte
opcode83/length64 frame. The owner handles bounded create/close operations until
that prefix, then validates the complete live snapshot against actual holdings
before copying. Existing atomic stage_fork accepts absent Second generation for
the first child. Creating Second later does not add endpoints to that child.
No second authority ledger or shared-core change is introduced. At most four
operation frames plus the prefix are permitted per construction stage. Each reply
completes before intake advances; applied operations are not retransmitted.

The owner checks role-specific reduced snapshots during exec and uses the existing
atomic CLOEXEC commit. All three children retain native identity, private copied
state and fresh replacement descriptors. The parent closes its remaining reader
before dispatch, then collects all three terminal statuses once.

## Qualification

`python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json`
passes31 native cases on278 frozen inputs. Target case total is83.118 seconds.
The new positive requires nine replacements, exact data/EOF per pipe and fifteen
normal reclaims across three generations. The negative acknowledges First-writer
close without applying it; the next live snapshot disagrees with owner holdings,
rejecting owner2731 before the second copy and with zero reclaims. All29 earlier
cases retain their outcomes. No failed attempts occurred; intentional rejection
logs remain in the preserved artifacts.

`zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`
returns0 with104 host checks. Final checks cover Rust1.98 edition2024,
Clang-format21.1.8, workflow/standards/experience, simplicity manifest/four members,
whitespace and unchanged frozen runtime sources. Exact compilation commands,
pinned tools/SDK identity, timestamps and envelope/ISO/serial hashes are retained.

## Compatibility and limits

All40 prior top-level ELF/raw images are byte-identical (compatibility.json).
Both new owners are13344 bytes within16384; kernel mapping remains8007680 bytes.
Four private client/staging/harness files changed (source-changes.json). Kernel,
shared pipe/descriptor core and adapter, SDK, dependencies, quotas, siblings and
released pins are unchanged. Buffers remain live during synchronous masked fork
snapshot operations; no new unsafe boundary is introduced.

This moves parent construction closer to dash's evalpipe order. It does not execute
dash or reproduce child concurrency: children still await owner-selected exec/data
phases. Standard descriptors start absent. Actual dash wait-any/nonblocking
collection, scoped standard streams, child-driven builtin/exec scheduling and
unchanged pipeline/early-reader scripts remain integration work. SIGPIPE/status
composition, additional interruption schedules, matching full connections/runner
and independent SDK/userland acceptance remain open. Persistent storage/OpenZFS,
packages, recovery and sys-init assembly remain R1 work. No full-shell/release claim.

The preimplementation review and outcome are in NATIVE-SHELL-STARTUP. Source and
review archives preserve runtime inputs and local guidance/test support. collect.py
checks every generated file against its archive before deleting only this run's
private output root; cleanup.json records verification. Prior sealed packets are
untouched. SHA256SUMS covers all packet files except itself.
