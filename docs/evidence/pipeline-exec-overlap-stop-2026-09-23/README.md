# Interrupted exec with surviving pipe I/O — 2026-09-23

This private overlap profile stops the final reader after native publication and
exactly seven bytes of its filtered descriptor table. The retained replacement
state checks the bound handle's terminal detail143/kind3 and readiness0 before
clearing its frames, tables and request state. Only then does the dispatcher remove
that participant's pipe holders and standard-stream grants and mark it dead.
Stop acceptance alone does not authorize cleanup. No cancelled channel enters the
I/O decoder; backing remains subject to the existing later terminal/reclaim checks.

The copied writer and relay survive. The relay drains the first pipe's exact ten
bytes to EOF; each second-pipe write must fail with EPIPE because its only reader
is gone. Writes to that pipe are held until reader cleanup, making the witness
repeatable. The final ledger requires ten first-pipe reads/writes, no second-pipe
data, one first-pipe EOF and at least one second-pipe EPIPE. Both surviving children
exit0. The parent uses public musl wait entry points to collect all scoped children
once; the stopped reader maps to SIGTERM15, explicitly distinct from exit143.
The original unrelated-PID, WNOHANG and repeated/exhausted collection probes remain.

Standard-stream completion requires empty stdout, consumed stdin and stderr bytes
from only the writer and relay, with all holders closed. This uses the existing
ledger with one terminal-confirmed reader cleanup method, not a separate ledger.
The new client variants assert these scoped failure outcomes; old clients and
profiles remain compiled without the new flags.

## Negative controls and limits

- Omit native stop: the child remains live, retained state cannot be cleared, and
  after32 held cancellation polls the owner must reject2770 with zero reclaims.
- Omit partial-frame clearing: exact terminal is observed, but the retained state
  fails2772 before holder cleanup/reclaim.

Timeout, unrelated panic and generic nonzero exit do not satisfy these controls.
The positive completes three generations,12 admissions and15 reclaims. The earlier
seven-byte exec-denial/first-writer-progress witness remains part of this profile.
This tests an injected post-publication stop while I/O is active, not arbitrary
peer faults, lost replies, pre-publication cancellation during overlap, interrupted
parent waits, SIGPIPE delivery or independent full-dash acceptance.

## Resource and compatibility review

The final positive ELF's extracted text exactly matches the tested raw owner.
Its reviewed start/poll/commit/descriptor-prepare/memory-leaf chain consumes3952
bytes of4088 usable, leaving136 bytes. Cancellation's out-of-line observation is
shallower. Disassembly, raw/ELF and commands are retained. This is scoped evidence,
not a general stack proof; compiler, buffer, participant or caller changes require
renewed review. The one-page stack,24-KiB owner ceiling, participants, channels and
kernel backing budget are unchanged. New owner sizes are18072,17976 and17576 bytes.
All83 previous ELF/raw images remain byte-identical. No kernel, shared pipe core,
SDK, sibling, dependency, immutable release or consumer-pin changes.

## Reproduce

```sh
python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

The source freeze covers281 runtime inputs. Preimplementation requirements,
forbidden outcomes, security and simplicity review are in NATIVE-SHELL-STARTUP.
finalize.py verifies the frozen sources, archives exact generated outputs, verifies
archive/live bytes and removes only the verified duplicate suite directory.
SHA256SUMS seals this packet. Earlier failed and successful evidence stays immutable.

Before exposing this path to general shell consumers, qualify broader cancellation
boundaries and interrupted wait replies. Actual dash main/eval, unchanged consumer
workloads, matching full suites and independent SDK acceptance remain outstanding.
OpenZFS persistence, packages and sys-init assembly remain separate R1 requirements.

## Attempt1 triage

The existing68 cases passed. The new positive completed all runtime checks and
result100/reclaimed15, but the harness asserted a nonexistent forced-stop log line.
The kernel intentionally emits no normal terminal marker on this stop path.
This is a harness-oracle error; the two new negative cases were not run. The exact
runtime terminal/readiness, parent wait status, surviving-child exits and reclaim
checks remain authoritative. Attempt2 removes only the impossible log assertion
and reruns all71 cases. No runtime source change was made between attempts.
Both source sets, host logs and complete generated outputs are retained.

Final attempt2 passes all71 native cases in201.119 recorded case seconds. Host checks pass105 Python tests plus Zig/Rust checks. New positive and exact2770/2772 omission controls pass. All83 prior images remain identical. Attempt1's harness failure and unrun cases are preserved and distinguished above; no runtime failure or timeout is counted as success.
