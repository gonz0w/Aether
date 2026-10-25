# First static C runtime: consumer proposal


> Current scope, 2026-09-05: the [bounded native experiment](../experiments/native-c/README.md) now demonstrates startup, private TLS/FP context, partial output and cleanup. The [kernel-owned contract](../../aether/docs/NATIVE-C.md) defines its exact ABI and narrower limits. Requirements and earlier gap snapshots below remain proposals for broader support; they do not negate that witness. Shared requirements are owned by [Aether-standards](../../../Aether-standards/docs/CATALOG.md), consumed through the [Distribution adoption](DISTRIBUTION.md). Native allocation, service-owned I/O and general POSIX integration remain open.

2026-09-05; UL-003 active draft. Not an accepted Aether ABI or assignment to sibling
projects. Based on the [musl audit](research/MUSL-1.2.6-AUDIT.md).
The [concrete handoff](NATIVE-C-HANDOFF.md) and tested
[host launch model](../experiments/launch-profile/README.md) now refine this proposal.

## Smallest useful experiment

Run one statically linked x86-64 musl executable that checks argc/argv/environment,
initialized/zeroed data and a TLS variable; writes a known byte sequence to an
explicit output descriptor and exits with a checked status. No dynamic loader,
fork, pthread application, filesystem traversal or terminal job-control claim.
Then add allocation/free and bounded input to exercise mapping and I/O failure.

| Contract | Proposed requirement | Acceptance/negative case | Coordination |
| --- | --- | --- | --- |
| Executable | Static ELF64 with bounded PT_LOAD/PT_TLS, validated offsets/alignment, zeroed BSS, RX/RW separation, NX stack | Truncated/overflowing/overlapping invalid segments rejected without partial launch; unsupported interpreter rejected | Aether loader owner |
| Startup | C-compatible initial stack containing argc, argv, env, terminated auxv; mapped program headers and correct page size | Missing/invalid startup pointers fail launch; program checks sentinel arguments/data | Aether + userland |
| Auxv | Specify AT_PHDR/PHENT/PHNUM, AT_PAGESZ, credential/secure state, entropy and any optional CPU hints consumed; AT_NULL termination | Loader builds trusted values; no fabricated UID=0 privilege or fake security entropy | Aether + identity owner |
| Context | Set/restore FS base and required x86-64 FP/SIMD state; define stack alignment/red-zone policy | Preemption between distinct contexts preserves TLS and register sentinels; unsupported context not advertised | Aether |
| Memory | Bounded private mappings with zero-fill, protection and quota; initial TLS allocation contract | Denied/out-of-range mapping fails; quota exhaustion leaves no leaked grants/backing | Aether + adapter owner |
| Transport | Native calls or Linux entry decision; bounded request buffers, ownership/lifetime, result/error format | Forged handles, invalid pointers/lengths and stale references rejected without authority escalation | Aether + adapter owner |
| Descriptors | Explicit read/write rights and initial FD mapping; short transfers/EOF/errors | Wrong-direction access denied; short write completed correctly; no other service data exposed | Unassigned FD/console owner |
| Exit | Terminal status survives termination until designated observer consumes it | Exited code never resumes; wrong observer cannot consume status; failure cleans up launch resources | Aether + sys-init |

Define exact limits, error values and addresses with the owning implementation;
this document intentionally reserves no syscall numbers or production target triple.
If stdout is initially a byte stream rather than a terminal, ioctl must report
that honestly. No full termios support is required for the first write witness.

For initial unprivileged tests, credential auxv values can describe equal real and
effective identities truthfully. This does not solve administrative startup:
musl's secure-startup branch needs descriptor checks and a /dev/null equivalent,
or an explicitly reviewed native adaptation. Track that under UL-010.

## Gating decisions

1. Native adapter versus unmodified Linux instruction entry (UL-002 recommendation,
   UL-015 experiment; Aether agreement required).
2. Who owns POSIX process/FD/memory service state and its grants (UL-003).
3. Exact link-time and runtime call set for the chosen binary (UL-014).
4. Entropy and CPU context support (UL-003); disabling hardening to conceal missing
   support is not acceptance of a secure profile.

Existing lifecycle v1 is a reference for retained outcomes and scoped authority;
its fixed worker/code/stack profile cannot launch this program as specified.

## Reference evidence and next contract slice

The [Linux reference now executes](../experiments/musl-reference/RUNTIME.md).
Use its startup/TLS/data/I/O/exit probe as the first native consumer workload,
followed by its allocator variant. Trace-derived minimum operations are:

| Linux-side convention | Native service requirement to specify |
| --- | --- |
| arch_prctl ARCH_SET_FS | Set the caller's thread pointer with valid user address semantics; preserve it on context switch |
| set_tid_address | Define caller identity and lifetime/clear-address semantics; a dummy positive result is not thread support |
| write | Caller-scoped FD lookup, bounded readable input, partial/error return and correct EBADF |
| exit_group | Stop the process, preserve status for authorized observer and complete resource teardown |
| mmap/brk/munmap (allocator slice) | Owned mappings, quotas, zeroing/protection, fixed mapping restrictions and truthful failure behavior |

These are semantic requirements, not a request to assign Linux syscall numbers
to Aether. Initial argv/env/auxv, loaded program headers, entropy and TLS storage
are provided by launch rather than visible as ordinary calls in the trace.
The trace does not cover secure-startup FD repair, large TLS, allocator fallback
or failure, signal handling, threads or TTY control. UL-019 covers additional
reference branches before widening support.

Aether's latest state also records live cross-core display and an OpenZFS-led
future storage direction. Neither supplies the missing C-runtime contracts;
the first probe can use a delegated byte stream without committing to a disk
filesystem or changing the kernel's current M4 priorities.
