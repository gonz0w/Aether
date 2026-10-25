# UL-062 pinned ASan host diagnosis plan

Before behavior work: add a host diagnosis driver only. Keep runner-parse.c,
native-io.c, process.py, sibling repositories and release pins unchanged. Do not
switch the Clang 21.1.8 pin to Apple clang. This inventories missing ASan, not a
sanitizer pass.

Applicable requirements: Foundations E-01–08; Testing TD-01–05, TC-02, TE-01–04;
Coding CC-03; Documentation DW/DS/DP; Experience for the new contributor CLI.
BSD-2-Clause original work. Reuse pinned Homebrew Clang 21.1.8, Apple SDK and
process.py. No fetched dependencies.

PXA-01: empty main built with pinned Clang -fsanitize=address does not complete
in 5 seconds. A live /usr/bin/sample of that process must contain AsanInitInternal
and LockSlow. Empty stderr before kill is required; a generic timeout without that
stack is incomplete diagnosis.
PXA-02: the same empty main with pinned -fsanitize=undefined exits 0 within 5
seconds under process.py ownership and cleanup.
PXA-03: Apple clang -fsanitize=address empty main exits 0. Record compiler
identity and dylib. This is a comparison control, not a pin and not product
qualification. Do not use it to compile parser sources in this slice.
PXA-04: pinned ASan heap-buffer canary times out without AddressSanitizer
diagnostics. PXE-04 stays blocked on this toolchain/OS pair.

macOS 27 dyld/malloc re-enters ASan init while InitializeShadowMemory walks
mappings; that is host incompatibility, not a parser hang. Compensating coverage
remains host UBSan plus existing native denial/reclaim witnesses. No native
sanitizer port and no waiver of memory-safety claims.

Command: python3 -B experiments/command-runner/check-asan-host.py from the
repository root. Repeat with Python 3.10.21. Help/version/usage 0/0/64. Format
any new C. Quality gate. Sample uses a 1-second window; hang bound 5 seconds;
suite budget 60 seconds. No VM or network.

Independent review pending. Retain failed and successful attempts. Update
EXTENDED, PROCESS, coverage, BACKLOG and STATE. UL-062 stays active.
