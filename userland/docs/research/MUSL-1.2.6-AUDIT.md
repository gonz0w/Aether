# musl 1.2.6: bounded source audit

2026-09-05; UL-002 complete as source research. No musl build or target execution.
Scope: x86-64 static startup, representative memory/I/O, process, signal and
thread paths. This is not an exhaustive syscall closure or security audit.

## Source identity

Selected upstream release **1.2.6**, announced 2026-03-20. The announcement
includes the iconv CVE-2025-26519 fix; this is a reason to avoid basing the new
experiment on unpatched 1.2.5, not a claim that 1.2.6 has no vulnerabilities.
[Upstream announcement](https://www.openwall.com/lists/musl/2026/03/20/1)

Archive SHA-256:
`d585fd3b613c66151fc3249e8ed44f77020cb5e6c1e635a616d3f9f82460512a`.
Official endpoints timed out. Downloaded Debian's upstream orig archive and
matched this independent published Buildroot pin before extraction.
[Debian archive](https://deb.debian.org/debian/pool/main/m/musl/musl_1.2.6.orig.tar.gz),
[Buildroot hash record](https://lists.buildroot.org/pipermail/buildroot/2026-April/800267.html)

Buildroot reports checking the upstream signature; **we did not independently
verify that signature or its key**. This is sufficient identification for this
read-only audit, not release eligibility. Archive and inspected-file hashes are
in [audit evidence](musl-1.2.6-evidence.json). No source scripts were executed.
Extracted inputs are disposable under build/musl-audit/musl-1.2.6.

## Source-derived requirements

Paths below are relative to that exact archive. They name inspected source, not
assumed Linux behavior. The source manifest allows checking the same bytes later.

| Area and source | Observed behavior | Consequence for Aether |
| --- | --- | --- |
| crt/crt1.c; arch/x86_64/crt_arch.h | Entry reads argc/argv from stack and aligns the C call stack | Need a real executable startup layout; lifecycle fixture registers do not substitute |
| src/env/__libc_start_main.c | Reads env and auxv, initializes TLS and stack guard, invokes constructors, calls main then exit | Define bounded argv/env/auxv and cleanup; startup can need more than main's own calls |
| src/env/__init_tls.c | Reads ELF program headers/PT_TLS, copies TLS image; may mmap larger TLS; sets thread pointer and calls set_tid_address | TLS and a valid thread identity are early requirements, even before pthread applications |
| src/thread/x86_64/__set_thread_area.s | Direct syscall 158, ARCH_SET_FS | Need FS-base mechanism or a reviewed replacement; wrappers alone miss it |
| src/env/__stack_chk_fail.c; src/malloc/mallocng/glue.h | Consume AT_RANDOM for canary/allocator secret; have address-derived fallback paths | Supply real entropy for any hardened profile; fallback existence is not a security guarantee |
| arch/x86_64/syscall_arch.h; src/internal/syscall_ret.c | Inline syscall instruction and Linux register layout; negative errors become errno | Existing int 0x80 capability ABI is different; define translation, pointer validation and error mapping |
| src/malloc/mallocng/malloc.c, glue.h | Metadata allocation tries brk and falls back to mappings; guard/protection behavior matters | Test actual allocator branches, quotas and failures; brk denial needs explicit compatible behavior |
| src/stdio/__stdio_write.c, __stdout_write.c | writev loop handles partial output; stdout probes TIOCGWINSZ with ioctl | printf is not merely write; correct terminal detection and short I/O matter |
| src/process/_Fork.c, fork.c | Masks signals, duplicates process, repairs child thread identity and libc state/locks | Launch cannot replace fork without preserving continuation, memory and inheritance semantics |
| src/process/execve.c, waitpid.c; src/internal/syscall.h | Exec uses execve; waitpid reaches wait4 cancellation wrapper on this architecture | Need image replacement, status encoding, child ownership, cancellation/interruption boundaries |
| src/signal/sigaction.c; src/signal/x86_64/restore.s | rt_sigaction/rt_sigprocmask plus direct rt_sigreturn assembly | Native signal delivery needs a matched frame/restorer design, not just a notification endpoint |
| src/thread/pthread_create.c; x86_64/clone.s, syscall_cp.s | Shared-state clone flags, TLS/stack setup, direct assembly syscall/cancellation regions | Multithreading is a separate gate; patching only syscall_arch.h is insufficient |
| src/exit/_Exit.c | exit_group followed by exit fallback | Termination must stop execution and preserve observable status, not return success |

The audit includes configure's runtime selection: it probes GCC libraries before
compiler-rt alternatives when LIBCC is unspecified. For our LLVM-first experiment,
set and inspect the actual compiler runtime explicitly. Likewise set CC, AR and
RANLIB; --target does not itself invent an Aether OS port.

## Comparison and recommendation

**Recommend testing a source-rebuilt musl with a narrow native transport adapter
that initially preserves musl's Linux-shaped internal arguments and errors.**
The user subsequently selected this experiment in
[decision 002](../decisions/002-native-musl-experiment.md); it is not an accepted system ABI. It combines
the useful parts of the two earlier options without promising Linux binaries run.

| Option | Patch/implementation surface | Authority and maintenance tradeoff |
| --- | --- | --- |
| Unmodified musl with Linux syscall entry | Kernel entry/return and Linux-facing service adapter; startup/ELF contract still required | Lowest musl delta, but exposes a machine-level ABI and requires validating every supported operation and signal frame; larger compatibility commitment |
| Native transport with retained internal conventions | syscall_arch.h plus TLS, clone, cancellation and signal-return assembly paths; startup adapter as needed | Explicit native transport, fewer semantic rewrites than a wholly native libc; still must implement correct supported Linux-shaped operations |
| Deep native musl port | Above plus process, signal, thread, allocator and other OS-sensitive internals | Can discard unwanted Linux assumptions but carries broad recurring upstream merge/test burden |

These are qualitative costs, not measured patch counts. No patch has been written.
All options need capability-scoped path/FD/process/memory operations and validated
cross-address-space buffers. A user-space adapter is not a security boundary
unless a capability-enforcing service validates it; applications can bypass libc.
An adapter must not use its own broad authority on behalf of an unprivileged caller.

Start with one static single-threaded C process, explicit initial descriptors and
startup/I/O/exit. Add allocation as a second slice, then process and TTY semantics.
Retain real TLS initialization. Reject unsupported pthread/process operations;
do not claim a complete libc merely because the selected program links.

## Follow-ons required before implementation

- **UL-003:** the [C runtime consumer proposal](../C-RUNTIME-PROFILE.md) needs
  Aether review and implementation owners; no numeric ABI is allocated here.
- **UL-014:** build a pinned Clang/musl reference and inspect linked objects,
  disassembly and executed syscall traces for startup/write/exit and allocation.
  Source inspection is not proof of the exact executable call set.
- **UL-015:** prototype the native transport approach only after the entry/buffer
  contract is agreed; enumerate all direct assembly entry points and prove denied
  operations cannot be bypassed. Compare patch delta with unmodified reference.
- **UL-016:** independently establish source signature/key policy and review
  post-release fixes before any distributable package is approved.

No sibling runtime changes, full security audit, benchmarking, or upstream
maintainer endorsement are claimed. Source findings supersede the moving-HEAD
leads in CLANG-MUSL.md for the paths inspected here.
