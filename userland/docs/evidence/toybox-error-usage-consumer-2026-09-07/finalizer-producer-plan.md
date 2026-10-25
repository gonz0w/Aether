# Actual Toybox callback output and finalization failures

Pre-code contract, 2026-09-07. Qualify actual xexit callback-pop/call/free and real
musl buffered output with the existing private normal _xexit cleanup seam. A
finalizer-only mode reads the fixed32 binary input bytes and EOF, then callbacks
write ordered16-byte halves using fwrite into the existing4096-byte stdout buffer.
No channel call may occur during callbacks. This mode does not call cat_main;
normal applet and usage regressions remain separate required evidence.

Actual xexit flushes while all scoped aliases remain live. Its fflush-error
short-circuit legitimately skips ferror; observe and validate both paths. Known
flush EIO/EINTR permits only exact upstream stderr diagnostics, no output retry.
Unknown write completion forbids later traffic. Preserve nonzero64 through flush
or close failure; promote0 to1. All aliases are locally consumed and independent
owners supervise remote cleanup. Re-entry into the private cleanup hook must
reject120 before any channel effect. This does not implement recursive xexit or
signal-safe finalization. Deliberate corrupt output, omitted flush, premature
flush, skipped close and false success must fail exact semantic oracles.

Add only opt-in cat-owner accounting/diagnostics/status for the32-byte buffered
input. Preserve existing owner modes, ABI, grants, quotas, SDK and standards pins.
Rust1.98.0 edition2024 and clang-format21.1.8 conventions apply. Callback buffers
have static lifetime; Toybox exclusively pops/frees nodes, callbacks retain no
nodes. FFI uses the existing x86_64 function/data pointer convention. No new
concurrency, unsafe kernel code, dependency or policy ownership. Read-only upstream
sources and Foundations O/I/E, local DEVELOPMENT/STANDARDS and Experience ASCII
preservation apply. No sibling modification or consumer sign-off.

Select normal/short, flush EIO/EINTR/malformed/cut, close input/output/diagnostic,
nonzero64 plus flush/close failure, private-hook re-entry and five mutants. Rerun
actual cat/error/usage suites, full213 command cases, host/Zig/pins/workflow and
format. Freeze sources during qualification, retain every failed attempt before
edits. Update NATIVE-CAT, workflow and STATE; recursive/signal exit and independent
CAT acceptance remain open after this slice.
