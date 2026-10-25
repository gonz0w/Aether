# Native C supervision experiment v1

Implemented and tested 2026-09-05 under the explicitly authorized cross-project
scope. Single BSP only, selected by the AENSUP01 envelope in the optional fifth
native boot module. Lifecycle v1, the AENATC01 startup profile and default SMP
protocols are unchanged. This is a sys-init-owned policy client supervising real
musl C instances, not production init, POSIX processes or supervisor recovery.

## Bootstrap and authority

The exact envelope is little-endian `<8sII`: AENSUP01, C ELF byte length, raw
supervisor byte length; then 32 developer entropy bytes, the static C ELF, and
1–4096 supervisor bytes linked at 0x400000. ELF is at most 1 MiB and retains the
native C loader's mapping/page bounds. The supervisor has an immutable code page
and a separate 4 KiB stack. Only it is runnable initially. The kernel copies and
parses the ELF during bootstrap, retaining an immutable-by-convention kernel-only
image description. Replacements consume that description and the retained bytes.

Sys-init receives RDI=1 (profile version), RSI=0xa001 (its scoped factory grant).
Two local worker slots each permit at most three generations without wrapping.
The supplied policy launches both, allows one replacement of slot zero, and then
stops the peer. Slot number or guessed handle alone is never authority: the kernel
requires the invoking domain to hold the supervisor's bootstrap binding. Workers
have only caller-local runtime operations, readiness and their launch-bound FD1
output right. No grant can be transferred or derived in this narrow profile.

The native C startup mapping/auxv/TLS/FP rules remain in NATIVE-C.md. Replacement
reuses developer bootstrap entropy; no production randomness or login identity
claim is made. Instance generations are separate from the reused musl thread ID.
This owner and scheduler are BSP-local; the SMP fixture does not use them.

## Operations

Interrupt 0x81, RAX operation, RDI holder handle, RSI argument; signed RAX result.
Existing native C operations remain unchanged. Non-supervisor callers of control
operations receive -13 before lookup or mutation. Handle failure returns -9.

| Operation | Authority and effect |
| --- | --- |
| 0x20000 | Supervisor factory grant, slot 0/1. Reject occupied (-16), invalid slot (-22), exhausted generation (-28). Return fresh handle and admit a private C instance |
| 0x20001 | Supervisor instance handle. Return 0 if running, terminal detail+1 otherwise; RDX historical readiness observed, RCX yield count, R8 terminal kind (0 none, 1 exit, 2 fault, 3 stop) |
| 0x20002 | Supervisor instance handle; require terminal (-16 while live). Detach mappings, reload CR3, permit kernel cleanup aliases, zero and check backing, invalidate handle and release slot |
| 0x20003 | Supervisor instance handle, byte offset. Read an output byte; -11 if not yet present/outside retained output. No child or unknown holder can read peer data |
| 0x20004 | Worker-local first-party readiness notification; retained as historical evidence, not health or a claim that a terminal instance is currently ready |
| 0x20005 | Worker-local current generation query |
| 0x20006 | Supervisor conformance completion; accepts 100 only after three reclaims and no admitted workers; not a production completion API |
| 0x20007 | Supervisor instance handle; stop runnable worker, retain stop detail 143 and kind 3, clear registered TID; explicit reclaim still required |

FD1 writes use the existing validated partial-copy transport (16 bytes per transfer,
256-byte total bounded buffer). Sys-init is now the authorized user-space consumer
of those bytes. This is a retained per-instance byte transport, not a terminal,
general pipe or console renderer. Generation-bound handles become unusable after
reclaim. No automatic restart policy lives in the kernel. Authority/format failures
never authorize a launch. Trusted kernel/profile invariants fail with diagnostics.

## Evidence and reproduction

Build the service with Aether-userland's `experiments/native-c/build.py --supervised`.
Pass its emitted native-c.bin to sys-init:

```sh
python3 tests/native-supervision.py --aether /absolute/Aether --native /absolute/native-c.bin --work /tmp/new-supervision-run
```

The work directory must not exist. This copies Aether and pinned boot dependencies,
builds the independently owned Rust policy client and five isolated images, and
retains source/artifact hashes, commands and serial logs. Each subprocess has a
120-second watchdog; each emulator has a separate 30-second watchdog. The kernel
also bounds the experiment to 3000 PIT ticks; these are not calibrated service
budgets. Host requirements match the existing Rust 1.98.0 and pinned kernel tools.

The positive client verifies unauthorized factory use, busy/live-cleanup rejection,
ready/output evidence, an actual #UD terminal kind/detail, continued peer progress,
reclaim, stale-handle rejection, a fresh successful replacement, and explicit peer
stop/reclaim. Wrong-detail and fault-at-entry clients reject. Withheld output and
skipped zeroing reject with kernel diagnostics. Existing native C startup, kernel
host tests, default two-core smoke and framebuffer checks remain passing.

The withheld-output case exposed an interrupt-stack overflow: reparsing ELF on
launch needed more than the 16 KiB interrupt stack, corrupting TSS state. Parsing
now happens before user entry on the boot stack; runtime load takes a validated
image description and cannot call the parser. The negative suite was rerun without
tracing after this correction. General kernel stack guards remain future work.

Sys-init owns `docs/evidence/native-supervision-2026-09-05/`. Package transport
is separately documented by pkg-mgr in `docs/SUPERVISED-HANDOFF.md`. This experiment
does not establish package authenticity, rootfs installation, persistent service
selection, SMP supervision, arbitrary ELF services or recovery after sys-init death.
