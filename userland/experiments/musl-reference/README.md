# Clang/musl static reference build

Host build/link/inspection experiment for UL-004b and UL-014. These are **Linux
reference ELF files**, not Aether programs. Runtime checks in probe.c are not
executed by build.py; the separate [Linux run now passes](RUNTIME.md).

## Reproduce

Requires Python with tarfile's data extraction filter, GNU make, and the local
LLVM executables identified in [tools.lock.json](tools.lock.json). Clang/LLVM and
LLD are 21.1.8; GNU make is 3.81. Pins include executable SHA-256 values. Missing
or changed tools stop the run. Shared host libraries and host utilities are not
fully pinned; this is not a hermetic SDK or source-provenance claim.

Place the musl 1.2.6 source archive at build/musl-audit/musl-1.2.6.tar.gz relative
to the repository root. The script checks its recorded SHA-256 before extracting
a fresh copy. It does not download anything or reuse a previously built libc.
See [source identity](../../docs/research/MUSL-1.2.6-AUDIT.md).

From the project root:

```sh
python3 experiments/musl-reference/build.py
```

Each run uses a new build/musl-reference-* directory, printed at startup. It
contains commands.json, configure/build/staging logs, headers, disassembly, maps,
syscall-site JSON and evidence.json. All installs use an explicit private DESTDIR.
No real system prefix or sibling checkout is changed.

## Checks and deliberate limits

- Clang's default configuration is disabled: the installed host configuration
  otherwise injects a macOS SDK. An allowlisted subprocess environment excludes
  CPATH, SDKROOT, LIBRARY_PATH and other ambient compiler settings.
- An empty sysroot is used for the initial C link. A missing header and missing
  libc must fail for their expected reasons, not silently use host files.
- Musl is configured static-only with no wrapper and built with explicit Clang,
  LLD, llvm-ar and llvm-ranlib. Its configure script is trusted, pinned source code.
- LIBCC is deliberately whitespace to suppress automatic runtime discovery. No
  compiler builtins are linked in this bounded experiment. A 128-bit division
  fixture must fail with missing __udivti3. The separate UL-017 [compiler-rt build and witness](RUNTIME.md) now supplies
  and validates the target builtins; this original build still omits them.
- Startup and allocator probes use only staged musl headers, explicit startup
  objects and libc.a. Probe compilation enables strong stack protection.
- Inspection requires ELF64 x86-64 ET_EXEC, no interpreter/dynamic segment,
  no unresolved external symbols or relocations, no writable executable LOAD
  segment, an NX stack, and TLS segments in the musl programs.
- LLD retains a local hidden zero-valued undefined _DYNAMIC marker from musl's
  weak declaration. The checker permits that exact marker, not unresolved imports.

The SDK fixture's entry is a compile/link witness, not an executable startup
protocol. The musl probes are actual Linux programs designed to check args/env,
BSS/data, TLS, EBADF behavior and output; one also allocates/touches/frees 128 KiB.
They do not force allocator exhaustion, short writes or preemption. Those remain
separate runtime tests. A successful link says nothing about those assertions.

When a Linux x86-64 reference environment is established, run each with argument
`check` and environment `AETHER_PROBE=reference`, require exit 0 and the exact
PASS output, and capture syscall traces. A wrong argument/environment must fail.
Do not run these directly on macOS or treat QEMU system emulation as Linux user
emulation. The build itself does not start a runtime; the separate runner reuses the
prepared local tool image described in RUNTIME.md.

## Recorded result

See [latest evidence](evidence.json) for measured artifact sizes, hashes and static
syscall-site counts. Counts include instruction sites in linked code; they are
not distinct syscall numbers or observed calls. Full logs remain in its output
directory. The final validation was invoked with a poisoned parent CPATH containing
host-only.h and a macOS SDKROOT; the isolated header check still failed as intended.

Two setup failures were corrected before the recorded passing run: linker flags
were accidentally passed to a warnings-as-errors compile-only step, and the first
symbol check rejected the harmless local _DYNAMIC marker. Final checks distinguish
those cases without disabling compile warnings or permitting external imports.
