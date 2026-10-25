# Real TLS shell relink — UL-007/081/082

Aether's actual ELF parser rejected the earlier stage81 shell: dropping the old
runtime also dropped its initialized TLS object. The generic link check missed
this loader requirement. Preserve that candidate and its original build evidence;
this correction is a separate delivery.

## TLS lifetime and failure contract

The opt-in native fork module now defines a real C17 `_Thread_local volatile
uint32_t fork_tls = 0x73657373`. Live references retain an actual four-byte ELF
TLS symbol/template. Initial shell startup checks it before consuming the first
greeting and returns existing -EIO on failure (entry's existing direct143).
Native fork checks it before arming/parking (direct116 on failure); the actual
child checks it again after pinned copy_rebind and before greeting/context-ready
(existing child114 failure). No production reset masks a missing/bad TLS copy.

CRT TLS initialization, native private backing and pinned auxv/libc copy rebind
remain responsible for validity. The unchanged upstream __post_Fork repairs
TID/list state after child constructor success. Canary equality is an invariant
check, not proof of thread-pointer integrity, native copy correctness or authority.
A bad thread pointer may fault before the check returns. No TLS allocator,
threading support, new grant, owner policy or additional boot/context is added.
Default bindings do not select this opt-in module; their previous layout remains.

## Loader acceptance

The maintained checker pins an unmodified snapshot of Aether's current
kernel/native_elf.zig (`e3a2b1133af03dc3d835f0cc0f9a4bd0f8911d33e4c05edbfad05f8da696ee67`)
and Zig0.16.0. Host Zig tests execute that parser on the **actual relinked shell**
under unchanged default limits (1 MiB file,128 pages including16 main-stack pages).
They require a real four-byte initialized TLS template, reject the exact old
stage81 ELF without TLS, and reject malformed TLS flags/ranges/alignment plus a
writable executable load. The kernel source/loader is never patched or relaxed.
This is parser acceptance, separate from native loading/execution and whole fit.

[Qualification](../evidence/filesystem-fork-tls-2026-10-22/README.md) records1010
stage cases (1008 retained/two new real host-fork corruption paths), nine compiling
semantic omissions, frame5847, default libc78 and opt-in libc78 including bad-TLS
startup before any greeting/source effects. Strict C17/UBSan/format; real native
TLS accesses and full pinned dash/CRT/libc/fork/rebind static link are inspected.
Host rebind/hardware observations are injected; no native TLS/scheduling witness.

## Remaining acceptance

The producer relink resolves the missing-TLS parser defect only. Sys-init must
consume the corrected artifact and file-view API, enforce exact FILE/stream/
source/history preflight under its sole gate, and compose actual copy/refusal/
unknown/greeting/ready/parent and terminal/endpoint/holder/readiness/shutdown.
Whole code/stack/TLS/heap/backing/channel peak fit and fresh matched Aether native
continued-parent/child/wait/error/cleanup/readback witnesses remain required.
Immutable exec/public dup2/full shell/Zsh/TTY/packages/ISO and full UL-007/082/M3/R1
remain open, as do affected-owner and independent reader reviews. No sibling
changes/messages, guest, install, quota/default/release-pin change or monitoring.
