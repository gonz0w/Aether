# Toybox native SDK closure audit (UL-067)

2026-09-06. Source and SDK integrity review; no new native build or execution.
[Audit evidence](../evidence/toybox-native-sdk-2026-09-06/summary.json) verifies all
231 installed SDK files against the command-runner's native-stdio-files pin, the
SDK receipt,18 musl1.2.6 source files against the original archive, and the exact
native syscall-header transformation. The SDK is build/native-c-xhkdw6jv. Matching
bytes establish identity, not complete call-graph, source trust or native readiness.

This refines the [bounded cat proposal](../TOYBOX-NATIVE-CAT.md). Its CAT-01–08
remain NOT RUN. Local implementation contracts stay with userland/Aether; shared
requirements and future changes stay in Aether-standards. No pins changed.

## Startup and output paths

| Retained path | Actual selected SDK behavior | Consequence for the candidate |
| --- | --- | --- |
| read/write/close | Native syscall_arch routes internal operations0/1/3 to __aether_io;32/33 also route but command facade rejects unsupported duplication | Existing bounded scalar command transport is relevant. It publishes two roles only and rejects unbound stderr; no general descriptor service follows |
| umask | src/stat/umask.c calls SYS_umask; operation95 is outside that hook and reaches native operation0x1005f | Reviewed native-C contract returns ENOSYS for unsupported operations. There is no truthful process mask implementation in this command path; Toybox ignores the failure, so reaching main cannot count as valid initialization |
| setlocale/newlocale | LC_ALL=C resolves built-in C maps; C.UTF-8 resolves static __c_dot_utf8 and matching UTF8_LOCALE | The nominal exact environment can select built-ins without locale allocation or locale-file access. This narrows required startup behavior but is not a native witness |
| uselocale | Updates the current musl thread's locale pointer; null queries it | Requires valid musl thread/TLS initialization. It is local libc state, not an IPC service or native identity grant |
| xmalloc(4096) | Separate from locale selection; still reaches musl allocator | Native-memory adapter/grant and strict malloc metadata protection need exact composition; built-in locales do not remove the stdout buffer allocation |
| setvbuf | Uses caller-provided storage; sets F_SVB without allocating | Normal Toybox startup supplies the buffer. That flag suppresses __stdout_write's TIOCGWINSZ probe; early help/error paths need separate reachability review |
| fprintf/perror/stderr and buffered stdout | __stdio_write invokes SYS_writev, internal operation20 | It bypasses the scalar hook and reaches unsupported0x10014. Providing FD2 alone cannot make Toybox diagnostics work; a reviewed stdio vector bridge is also needed |
| fflush | Calls the FILE write callback for pending output; input synchronization may seek | On selected direct-read stdin there is no fread buffer to synchronize. Do not generalize this to buffered stdin or add a successful seek stub |
| _exit → _Exit | Uses native exit_group/exit operations; neither supplies the command adapter's close protocol | Toybox termination will not run bytecount's finish. Explicit finalization must happen while authorized endpoints are still available |

The scalar native header is verified as the original archive transformed to
interrupt0x81 plus the five-operation hook. Merely finding no Linux `syscall`
instruction would not prove every translated operation is implemented.

## Locale failure evidence, correctly scoped

The previous [locale experiment](TOYBOX-NATIVE-AUDIT.md)
forced setlocale/newlocale failure returns. Those tests show Toybox's control flow
on denied returns, not that normal C.UTF-8 setup allocates or can exhaust memory.
Musl newlocale compares the constructed locale with built-in objects before its
allocation path; the selected LC_ALL=C environment matches that fast path.

Non-built-in names can consult MUSL_LOCPATH and allocate locale maps. The proposed
startup admits only LC_ALL=C and must not acquire ambient locale path authority.
The fallback en_US.UTF-8 path remains a distinct allocation/path review if it can
be reached under an adopted fault policy. The trace's READ_OTHER is specifically
non-UTF-8, not a proof of a particular named locale or Unicode behavior. No wc
classification acceptance follows from cat's exact byte copies.

## Reuse the existing stdio work only after reviewing its boundary

[UL-044 buffered files](../../experiments/native-files/STDIO.md) already identified
the vector-hook gap and supplies narrow replacement callbacks plus a two-vector
adapter. Its native evidence concerns fixture file descriptors and excludes
standard streams/TTY. Its adapter calls a different descriptor layer and contains
fixture counters and injected seek failures. Do not include it unchanged in the
command adapter or claim its tests qualify child stderr.

Recommended next vector work: specify a private stdio-write bridge over the
command's admitted roles. Validate vector count/size, preserve ordering and short
positive counts, and stop without replay after unknown transfer. Retain real
failure semantics; no public writev API or ambient standard streams are implied.
Run split-vector, boundary, partial-commit, malformed/unknown-reply and diagnostic
role tests before native qualification. Do not widen syscall_arch globally just
to make a link succeed.

## Recommended termination seam

Prefer a candidate-local adaptation at Toybox's _xexit terminal branch, after the
existing rebound check and immediately before _exit. In the reviewed selected
main/lib/cat sources, xexit is the only direct caller of _xexit; it runs callbacks
and fflush/ferror before that branch. Preserve the rebound behavior and review
indirect/signal paths explicitly before patching. This is a proposed source seam,
not an implemented patch or a guarantee for every Toybox configuration.

A small userland finalizer at that seam should consume owned input/output once,
preserve a prior command error, promote otherwise-successful cleanup failure,
deliver any bounded final diagnostic while stderr remains live, and consume
stderr last. Protect against re-entry without repeating remote effects. Record
unknown cleanup separately from confirmed release. Failed bootstrap and abnormal
termination retain their own owner-supervised paths; do not pretend they reached
the normal seam. The finalizer must not invoke xexit recursively.

Do not override global musl _Exit or assume atexit runs: that would affect runtime
and abort paths outside this applet, and _exit bypasses normal exit processing.
Do not rely on musl __stdio_exit to close native bindings; stdio exit flushing is
not the command broker's consuming-close protocol. An owner still has to verify
resource reclaim independently of the candidate's exit status.

## Next local work and remaining gates

The [host finalizer](../../experiments/toybox-reference/FINALIZER.md) now passes
2,560 scenarios, six invalid-input controls and three semantic mutants. It checks
status/order/re-entry and uncertain cleanup without native wiring or proof of
upstream flushing. The [private vector candidate](../../experiments/toybox-reference/VECTOR.md) now
passes host tests and records libc integration plus unimplemented process-mask
state. Next exercise the actual pinned musl write loop with that bridge; no
native role or mask is supplied by a stub. Child diagnostic roles
and cat admission remain owner work.

A native implementation still needs explicit producer selection and role/lifetime
acceptance, composed memory/TLS/startup evidence, byte-identified patches, all
CAT-01–08 cases and independent review. New larger kernel-memory profiles do not
change this pinned SDK or imply adoption. UL-067 remains active; no sibling work,
package build, runtime test, release or security claim is made by this audit.
