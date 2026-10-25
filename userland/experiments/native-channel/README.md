# Independent native channel consumer (UL-038)

Six native QEMU cases pass with userland-authored C helpers and a small typed
channel adapter. This consumes the kernel-owned AENCH001 launch/channel v1 profile.
It does not implement POSIX pipe/read/write descriptors, fork, exec, wait, a TTY,
a process service, or dash execution. Shared PD requirements remain pending review.

## Ownership and source boundary

The adapter in channel.c calls the existing int 0x81 ABI, obtains one explicitly
transferred endpoint from auxv 0xa001, and translates raw negative errors to errno.
It does not allocate ABI values or add an FD table. A small __aether_io hook resolves
the retained strict-musl build's existing raw transport; it is not a console or
new libc descriptor implementation. Native memory is disabled in this profile;
small startup TLS is exercised, but allocation is not tested here.

The writer and reader are independently authored here and exchange the owner's
specified pattern using 11-byte writes and 7-byte reads, rather than the owner's
16-byte fixture requests. Each validates argc, argv[0], mode, empty environment,
TLS/BSS, endpoint presence, wrong-holder authority and wrong-direction rejection.
No successful syscall stub is introduced. Transfer loops are explicitly bounded
and yield on EAGAIN; this is not a blocking-pipe implementation.

The supervisor is Aether's existing `user/native-channel/supervisor.rs`
conformance client. Sys-init's inspected producer has no channel profile; this
run is **not sys-init adoption** or general supervision policy. The owner client
checks channel fullness/emptiness, buffer denial without consumption, stale grants,
failed-launch endpoint retention, busy-slot rollback, transfer revocation, terminal
outcomes, three reclaims and exhaustion/reuse. We reuse these checks without
changing the kernel or sys-init working trees.

## Reproduce

```sh
python3 experiments/native-channel/check.py \
  --aether /Users/cam/DEV/aether \
  --sdk build/native-c-xhkdw6jv
```

Use a strict native libc build with its matching receipt. The script verifies
LLVM/make executable pins and libc archive/patch receipt, records the complete
SDK inventory before use and rechecks it afterward. It copies Aether to a fresh
private build directory, rejects source changes during capture, and builds only
there. Boot dependencies are checked by the owner's pinned verifier; Zig, Rust
1.98.0 and QEMU versions are retained. The runner performs no fetch or installation.
Host tool/shared-library closure and source authentication remain separate limits.

Each ELF is linked explicitly with target startup/libc inputs, checked for
unresolved symbols and Linux syscall instructions, and inspected with readelf.
Native loader admission supplies the target-format/permission witness. All new
transports use the owner ABI. Envelopes bind two ELFs and one bounded raw supervisor;
host-generated entropy remains developer-only input.

Final run: `build/native-channel-userland-gvc24gmv`.
It reused the isolated kernel capture from `build/native-channel-userland-awq3_gnq`,
so the rerun did not silently follow concurrent companion changes. The first run
passed normal/fault and reached the stop success marker, then failed our extra
serial assertion: controlled stop has no producer terminal serial line in this
profile. The corrected runner relies on the owner supervisor's retained kind=3,
detail=143 check plus the cleanup/success outcome. The first run is incomplete,
not additional passing acceptance evidence.

[Durable evidence](../../docs/evidence/native-channel-userland-2026-09-05/summary.json)
retains source/SDK/tool identities, build commands, smoke parameters, boot manifest,
ELF/envelope/ISO hashes, link maps, raw supervisor source identities and serial logs.
The hashed native_smoke helper supplies exact QEMU invocation and 30-second
watchdog behavior; firmware variables are a private temporary copy. Builds have
180-second timeouts. Tests use BSP-only QEMU TCG, one core, no network and a private
256 MiB machine. No default-SMP, older native-memory or sys-init regression suite
was rerun: their implementations were not changed by this consumer experiment.

## Cases and exact scope

| Case | Required outcome |
| --- | --- |
| positive | Writer exits 17 after 96 bytes; reader validates order and EOF, exits 29; replacement writer sees EPIPE and exits 33; supervisor result 100 with three reclaims |
| writer-fault | Writer sends 96 bytes then UD2; owner observes kind 2/detail 134; reader drains then EOF; replacement/cleanup pass |
| writer-stop | Writer sends 16 bytes then readiness/yield; owner stops it and checks retained kind 3/detail 143; reader drains to EOF; replacement/cleanup pass |
| wrong-count | Owner config tells reader to expect 16 while writer sends 96; reader exits 103, writer may then observe EPIPE (retained run exits 208), supervisor result 511 before reclaim and exact profile-rejection panic |
| startup-copy | Test-only supervisor variant overwrites both source argv[0] records after successful launches; helpers still see original h; ordinary successful data/cleanup outcomes follow |
| wrong-pattern | Writer corrupts the final byte; reader exits 103; supervisor result 511 before reclaim and exact profile-rejection panic |

The startup mutation uses anchored transformations of a private supervisor copy,
with original/mutated source and binary hashes. `black_box` retains the overwritten
records for the test. This is explicit test instrumentation, not a silent change
to the producer or supervision policy. The corrupted writer is a separate ELF.
No unrelated panic, boot error or timeout can satisfy the two negative cases.

These cases demonstrate one transferred endpoint per child and the profile's
exit/fault/stop cleanup. They do not prove endpoint duplication, inherited FD
flags, syscall interruption, concurrent exec, arbitrary argv/env bounds, SMP,
parent/orphan policy, real device transport or authenticated sessions. Kernel
source describes additional properties; this six-case consumer suite makes no
claim to have independently exercised every owner test.

## Next step

UL-039 will inspect and consume the newer kernel-owned read-only file-service
experiment with an independent userland client. That has a separate AENFS001
profile and two-endpoint transfer; no such adoption is included here. Wider
PD/process/FD ownership and M3 native shell work remain open in UL-003/007/015.
