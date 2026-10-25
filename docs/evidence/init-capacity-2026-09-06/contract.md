
## SI-05 init capacity v2 contract — 2026-09-06

Before implementation: allocate opt-in AENIN002 / ABI 15, preserving AENIN001 /
ABI 6 and all old bytes/limits. This is the same 56-byte envelope: magic[8],
u32 first ELF length, second ELF length, supervisor length, reserved zero,
32 fixture entropy bytes, followed by the two ELFs and supervisor with exact
length. ELF lengths are 1..1048576; supervisor length is 1..8192 (v1 stays
1..4096). Check bounds before sums/slicing; reject truncation, extra bytes,
reserved fields and u32 maximum lengths before admission. This x86_64-only
parser has bounded sums after validation; no untrusted arithmetic may wrap.

Workers remain slots 0/1, supervisor slot 2; no third executable. Entry RIP
0x400000, RSP 0x800ff8, RDI=15, RSI=0xa001 factory, RDX=0xc001 first image,
RCX=0xc002 second image, R8=0xd001 channels, R9=0xe001 init observation.
Clock/observe/register/status/cancel/release, channel transfer, generations,
retained observations and owner-death semantics are unchanged. Code spans one
or two immutable user RX pages; separate one-page RW/NX stack at 0x800000.
Unused code tail is zero. Every kernel alias of code remains read-only/NX.
No memory/thread grant, recovery owner or authority inferred from ABI/size.

V2 normal oracle is AETHER NATIVE INIT LARGE PASS; fail-closed oracle is
AETHER NATIVE INIT LARGE CLOSED, only after existing all-domain cleanup checks.
Normal fixture completion remains result=100/reclaimed=3; shutdown clears both
code pages, stack, workers, channels and pending observation. Normal completion
halts with the supervisor still mapped, as in v1; it is not owner reclamation.

Qualify actual second-page entry, sequential reuse, deadline and cleanup controls,
lengths 4095/4096/8191/8192, zero/8193/huge lengths, reserved/truncated/extra
payloads, old-v1 oversize rejection, second-page write fault and stack NX fault.
Check code permissions/aliases and tail zero before publishing supervisor entry.
Run old init and affected launch/profile, native memory/thread and M4 regressions
on frozen sources plus host/standards/format. Preserve every attempt and return
an immutable source/tool/artifact/raw evidence bundle for independent sys-init
pinning and its 151 existing plus proposed guard cases. Producer qualification
is not consumer acceptance. No sibling/pin/shared standard changes.

After this one unblock, resume concurrent-child work per maintainer instruction;
UP-02 remains queued and does not take precedence in this turn.
