# Native two-pipe dispatch — 2026-09-15

Three independently admitted native workers now write, relay and read exact
`pipe data\n` across two real owner-held pipe objects. The two remaining capacity
workers keep their original readiness/identity roles and exit on release. Across
three generations, both pipes transfer ten bytes, report EOF once, retire only
after terminal/holder/frame cleanup, and the owner reclaims fifteen workers.
This is native transport/ownership evidence, not the unchanged dash pipeline:
these workers are initially admitted, not forked or replaced through exec.

## Review and implementation

The [preimplementation review](../../NATIVE-SHELL-STARTUP.md#native-two-pipe-dispatch-witness--2026-09-15)
records O-02–04, I-01/03–06, E-01–06 and SE-01–05, authority, bounds, cleanup and
selected tests. The owner binds each participant to its exact native channel and
handle generation. It observes readiness before enabling requests, stages only
role-specific holders and closes its own endpoints. Numeric references never
substitute for participant authority.

The dispatcher holds one 32-byte request and one optional completed reply/cursor
per pipe worker. A partial request cannot cause effects; Pending keeps the frame;
a completed reply prevents reapplication until its remaining bytes are delivered.
Workers send at most seven bytes and receive at most five per call. The owner
sends replies in at most seven-byte fragments, polling peers between iterations.
FIFO/holder/generation rules reuse the same two PipelinePipe objects across all
three lifetimes. Normal terminal observation requires no unfinished request or
reply before holder cleanup and retirement.

Fixed frame arrays suffice for this current fixture. No new transport framework,
mutable authority registry, kernel operation, resource limit, dependency, sibling
or released-pin change. The existing private native-call wrapper validates user
buffers in the kernel and keeps stack buffers live across calls. Existing five-
worker capacity behavior remains compiled separately under the same harness.

## Qualification

All eight native cases pass on final frozen inputs:

- The original five capacity cases still pass, including stop/reuse and native
  profile/entropy rejection controls.
- The two-pipe positive passes fifteen normal exits/reclaims with exact data and
  EOF over three generations. Both pipe objects retire; no pending frame is dropped.
- Deliberately routing Second through First rejects owner2723 with zero reclaims.
- Deliberately repeating a write while its reply is partially delivered rejects
  owner2726 with zero reclaims. The worker detects duplicated data before any
  lifetime can be accepted.

The original capacity worker.elf and owner.raw are byte-identical to the previous
sealed packet. Only scripts/pipeline_capacity.py and its worker/owner sources
changed among previous runtime inputs; pipes.rs is new. Kernel and existing
connection/pipe-core sources are unchanged. The new dispatch owner is 7,712 bytes;
wrong-route/reapply variants are 7,760/7,840 bytes, all within the existing16 KiB
limit. This is linked code size, not total TCB or peak memory.

All 104 host checks and required Zig/pin checks pass. Format/workflow/standards
checks and the four simplicity snapshot hashes pass. The earlier ordinary kernel
and legacy pipe evidence still names its own input set; no new full connections
or command-runner run is claimed here. Actual native dispatch is exercised by the
eight-case capacity suite, not inferred from compilation.

## Retained first attempt

The positive and wrong-route cases passed first try. The initial replay mutant
reapplied both reads and writes; their effects sometimes canceled during the
first lifetime, and it rejected owner2726 only after five reclaims in lifetime2.
The expected zero-reclaim oracle therefore failed. That run and exact sources
remain preserved. The final control repeats only a write during partial reply
and rejects in lifetime1 with zero reclaims. This changes the deliberate mutant,
not the passing dispatcher, and retains the original strict oracle. host-first.log
records the host pass before that change; host.log records the final pass.

## Replay and preservation

```sh
python3 scripts/pipeline_capacity.py --libc-build <pinned-sdk> --tools-lock <pinned-tools.json>
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
python3 scripts/check_workflow.py
python3 docs/check-standards.py
```

Attempt results record commands, tool/SDK digests, sources, timestamps and per-case
image/serial hashes. Source archives preserve both attempts. Artifact archives
include the native serial traces, images and deliberate controls. Each archive
member and original is verified before removing exact duplicate generated roots;
cleanup.json records those removals. Review inputs capture current documentation
and host support. SHA256SUMS seals this packet. Replay into fresh output roots,
never overwrite these receipts or previous sealed evidence.

## Remaining work

Connect actual native fork/exec and descriptor snapshots to the multi-pipe owner;
initial admission is not that handoff. Exercise ordinary EPIPE/error delivery and
interrupted requests/replies with confirmed stop before cleanup. This fixture
rejects unexpected errors instead of providing a general error-delivery service.
Then qualify the unchanged dash pipeline/early-reader scripts, matching full
connections/runner and independent SDK/userland acceptance. Filesystem/OpenZFS,
package execution, recovery and sys-init R1 assembly remain open.
