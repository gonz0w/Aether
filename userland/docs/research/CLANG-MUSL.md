# Initial Clang/musl feasibility review

Reviewed 2026-09-05. Preliminary research, not a pinned source audit, completed
libc port, security assessment or benchmark. Follow-on UL-002 is now complete as
[bounded pinned-source research](MUSL-1.2.6-AUDIT.md); the initial observations below
are retained as the starting checkpoint.

## Findings

Clang supports explicit cross-target compilation, but the caller must supply the
target headers, libraries and tool configuration. Unknown target components may
be treated as unknown rather than establishing a new OS ABI. Therefore our
freestanding probe triple is an object-generation setting, not a production
Aether target definition. [Clang cross-compilation](https://clang.llvm.org/docs/CrossCompilation.html)

Clang is one part of a toolchain. The proposed LLVM SDK includes LLD, object tools
and compiler-rt builtins; sanitizers and later C++ runtime support have additional
requirements. Their availability on Aether cannot be inferred from a host compiler.
Hardening flags require matching loader/runtime behavior: e.g. stack protection
requires initialized guards and failure handling; address randomization requires
loader support. [Clang toolchain](https://clang.llvm.org/docs/Toolchain.html)

Musl targets Linux or Linux syscall ABI emulation. Its compact design and static
linking support are relevant to recovery, but do not establish comparative
security or universal speed advantages. A static executable still needs OS
facilities. [Musl introduction](https://www.musl-libc.org/intro.html)

The inspected startup source reads environment/auxiliary-vector data and invokes
TLS and stack-protector initialization before main. Its secure-startup branch
also checks standard descriptors. Aether lifecycle v1 supplies none of that
process-startup contract. Single-threaded hello-world therefore needs more than
an output syscall and return instruction.
[Musl startup source](https://git.musl-libc.org/cgit/musl/plain/src/env/__libc_start_main.c)

The inspected thread implementation includes Linux-oriented clone, futex and
thread state machinery. It is evidence that a native port extends beyond ordinary
read/write wrappers, not a complete inventory of required calls.
[Musl pthread source](https://git.musl-libc.org/cgit/musl/tree/src/thread/pthread_create.c)

Musl documents different stdio I/O patterns, dynamic-linking behavior and thread
and locale behavior from glibc. Evaluate actual package assumptions, rather than
treating glibc-linked binaries as interchangeable.
[Functional differences](https://wiki.musl-libc.org/functional-differences-from-glibc.html)

## Candidate approaches — design inferences

| Approach | Advantage to test | Cost/risk to test |
| --- | --- | --- |
| Musl with Linux-facing adapter | Preserve more upstream code and familiar package assumptions | Correct Linux semantics, syscall coverage and capability translation; no broad binary-compatibility promise |
| Musl adapted to native services | Explicit native IPC/grants and smaller intended API surface | Long-lived libc patches, TLS/signals/thread changes and divergence from upstream tests |

Do not decide on source-code size alone. For each approach list changed files,
required semantics, trusted components, unsupported behavior, upstream update
procedure and tests. Prototype the smallest comparable startup/I/O/exit workload.
Do not return success from unsupported calls to make configure tests pass.

## First experiments

1. **Compile-only (done):** integer-only C produces an ELF x86-64 relocatable
   object with installed Apple Clang. See [probe](../../experiments/c-object/README.md).
2. **Host SDK (UL-004b):** locate/provision a pinned LLVM toolchain and isolated
   sysroot; produce and inspect a freestanding ELF executable. Verify no host SDK,
   unexpected interpreter, unresolved helpers or inappropriate CPU instructions.
3. **Pinned musl audit (UL-002):** obtain an identified release with verified
   source identity, inspect configure and startup/TLS/memory/process/signal/thread
   code. Capture an API matrix from source plus linked-symbol/disassembly evidence.
   Linker undefined symbols alone cannot reveal inline syscalls.
4. **Reference run (optional within UL-002):** Clang/musl on an explicitly named
   Linux environment can establish build/test baselines. It cannot prove Aether
   compatibility. Separate build-machine tools from target test executables.
5. **Aether C experiment (UL-006):** after UL-003 contracts exist, validate startup,
   TLS isolation where applicable, zeroed data, allocator failure, short I/O,
   denied access and observed exit before porting a shell.

An eventual release manifest must bind source/patch hashes, compiler/linker versions,
flags, target ABI, sysroot inputs and test environment. Sources below are moving
documentation, not dependency pins. Static library updates require tracking and
rebuilding consumers. Compare performance using fixed workloads and reported
binary size, memory and latency; no measurements are available yet.

## Source audit limitations

LLVM pages identify a development documentation version (24.0.0git), not the
installed compiler or a selected release. Musl source URLs refer to moving HEAD;
UL-002 must replace these leads with a pinned source inspection. Web fetches for
arch/x86_64/syscall_arch.h and src/process/fork.c failed; neither is represented
as inspected. No package vulnerability review or source archive was completed.
Local evidence is recorded in [source manifest](SOURCES.json); sibling files may
change after review, so hashes identify only the captured working-file snapshot.
