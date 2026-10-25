# 001: Clang-first C toolchain and musl evaluation

Date: 2026-09-05. Status: accepted direction; libc/runtime design remains open.

The user prefers Clang over GCC and agreed to investigate musl through a bounded
experiment. Prefer Clang, LLD, LLVM object tools and compiler-rt builtins for C
target work. Establish explicit target headers/libraries/startup files; do not
inherit host SDKs or GCC runtimes accidentally. Versions must be pinned when the
actual SDK experiment is built, rather than choosing a version from moving docs.

Musl is the first libc to evaluate. Selection is conditional on the source audit,
runtime contract, port maintenance burden and target tests (UL-002/003/006).
No blanket security or performance superiority is accepted. Start with static
executables to reduce initial loader dependencies; maintain a rebuild inventory
for embedded library fixes. This does not decide permanent static-only linking.

Consequences: existing portable C packages are preferred over rewrites. Clang is
a host tool initially, not a prerequisite installed on the boot image. Freestanding
compilation can proceed before libc. LLVM selection does not change Aether's Zig
kernel or commit sys-init to a language. GCC compatibility exceptions require a
specific package/build reason, not a general ban or mandatory second toolchain.
