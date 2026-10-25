# Compile-only C object probe

Purpose: establish whether the installed host Clang can generate x86-64 ELF code
before a libc, loader or target toolchain is available. Run from the project root:

```sh
mkdir -p build/c-object
clang --version
clang --target=x86_64-unknown-none-elf -ffreestanding \
  -fno-stack-protector -mno-red-zone -mgeneral-regs-only \
  -O2 -Wall -Wextra -Werror \
  -c experiments/c-object/probe.c -o build/c-object/probe.o
file build/c-object/probe.o
```

Observed on 2026-09-05: Apple clang 21.0.0 (clang-2100.3.20.102), host target
arm64-apple-darwin27.0.0. Compile exit 0. File inspection reported:

```text
ELF 64-bit LSB relocatable, x86-64, version 1 (SYSV), not stripped
```

An independent ELF-header check verified ELF64, little-endian, ET_REL and
EM_X86_64. Source and object hashes are in [evidence](evidence.json).

The probe has no headers, calls, libc, entry point or linker step. It is not an
Aether executable or musl build. Its target triple is provisional and its SYSV
ELF label is not POSIX conformance. General-register-only code avoids depending
on the kernel's currently unsupported FP/SIMD context. Stack protection is disabled
only for this libc-free probe; this is not a proposed production hardening profile.

Initial inventory: /usr/bin/clang was found. ld.lld, llvm-readelf and llvm-objcopy
were not found on PATH; standard /opt/homebrew/opt/llvm/bin paths for Clang/LLD/
readelf were absent. This does not prove no LLVM tools exist elsewhere. UL-004b
continues tool discovery before provisioning. No software was installed.
