# Native byte-stream profile v1

AENFD001 uses the supervised envelope layout: `<8sII` magic, C ELF length,
supervisor length; 32 developer bootstrap bytes; C ELF; raw supervisor. It selects
the new I/O profile only. AENSUP01, AENATC01, lifecycle v1 and SMP remain unchanged.
The boot-derived supervisor receives ABI 2 in RDI and factory 0xa001 in RSI.
This is a BSP-local experiment with existing page/generation bounds.

Aether supplies three caller-bound streams, not POSIX descriptor bookkeeping.
The [userland facade](../userland/docs/NATIVE-DESCRIPTORS.md) owns that
mapping and the [sys-init client](../sys-init/docs/NATIVE-IO.md) owns the fixture.
Names and guessed stream IDs do not grant access to another instance.

All calls use interrupt 0x81. RAX is operation, RDI native stream or holder handle,
RSI buffer/argument and RDX byte count when applicable. Signed negative errno-like
results use the existing x86-64 musl experiment convention.

| Operation | Required authority, effect and errors |
| --- | --- |
| 0x21000 | Worker input stream 0. Validate caller-writable range; transfer at most four bytes; 0 for zero length or drained/sealed input; -11 if empty/unsealed; -9 for wrong direction/closed stream; -14 for invalid range |
| 0x21001 | Worker output stream 1/2. Validate caller-readable range; transfer at most sixteen bytes to its distinct 256-byte retained buffer; -11 if capacity exhausted; -13 with withheld grant; direction/closed/range errors as above |
| 0x21002 | Worker caller-local stream close. Disable future native operations on that stream; input close also refuses producer submissions. Invalid/closed stream rejects before mutation |
| 0x20008 | Supervisor instance handle. RSI 0–255 submits one input byte; 256 seals producer; invalid argument -22, queue full -11, closed reader/sealed producer -32. Seal is idempotent while the reader remains open |
| 0x20009 | Supervisor instance handle. RSI high 32 bits select stdout 1/stderr 2, low bits select retained byte offset; return byte 0–255, 256 after closed output is exhausted, -11 while open with no such byte, -22 for invalid stream |

Workers invoking supervisor producer/consumer operations receive -13. Foreign/stale
instance handles reject with -9. Stream IDs outside 0–2 reject with -13; a guessed
stream value is never a transferable capability. Request length is at most 256;
pointer validation precedes consumption. Zero-length valid-stream calls return 0.
Legacy native write is rejected with ENOSYS in this profile to prevent bypassing
stream closure. All unsupported operations retain failure behavior.

Terminal exit, fault or explicit stop closes every stream; retained output remains
observable by the supervisor until reclaim. Reclaim invalidates its instance handle,
detaches mappings, flushes translations and zero-checks backing. Fresh launch
resets queues, references and closure state. Completion requires two reclaimed
workers and no admitted worker, emitting only `AETHER NATIVE IO PASS`.

`zig build test` includes byte-queue wrap/backpressure/sealed-drain tests. Build with
`-Dsmp=false -Dnative-c-image=ABSOLUTE_IO_ENVELOPE`, then run
`python3 scripts/io_smoke.py OUTPUT_ISO`. Full positive/negative reproduction is
owned by Aether-userland experiments/native-c/test_io.py. Evidence is under
docs/evidence/native-io-2026-09-05/.

This is not a TTY, POSIX pipe, console service, general descriptor table or a
blocking scheduler API. Kernel serial diagnostics keep their existing ownership
and emergency behavior. Entropy/identity, resource quotas and supervisor-death
limits remain those of the bounded native profile.
