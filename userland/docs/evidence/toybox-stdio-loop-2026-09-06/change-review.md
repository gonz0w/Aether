# UL-067 actual musl stdio-loop plan

Compile the pinned Linux musl1.2.6 __stdio_write source twice: renamed unmodified
control and renamed candidate with only syscall(SYS_writev, replaced by a private
bridge. Preserve original archive/SDK. Use actual musl FILE layout and vector.c;
no fake stdio algorithm, native wiring or public writev replacement. A real Linux
pipe validates the unmodified control. An independent byte backend checks candidate
buffer/external-vector order, short writes, zero progress, known EIO, lost ACK and
malformed reply. Unknown cases may commit bytes but never replay or allow a later
shared-state diagnostic. Verify returned newly-written byte count and F_ERR/buffer
state. Mutants must compile and fail runtime assertions. Keep all inputs, patches,
logs and attempts, explicit static Linux ELF/tool/image identity and cleanup.

C17 strict warnings for original code, declared upstream diagnostic exceptions,
pinned format, Python CLI/grammar and quality gate. Existing pinned LLVM/musl SDK
and QEMU Linux image only, no fetch/VM start; unprivileged read-only networkless
container,512MiB/32PID,60s owned process bounds and exact named cleanup. This runs
Linux reference, not native sanitizer/conformance. Host vector UBSan evidence is
reused for unchanged vector.c; Linux sanitizer runtime is not provisioned.
O/I/E, CE/CC/TD/TE apply; original code BSD-2-Clause, musl notices unchanged.
