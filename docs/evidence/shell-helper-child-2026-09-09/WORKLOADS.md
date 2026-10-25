# UL-007 actual dash workload handoff

These twelve candidate native scripts reuse the existing Linux-reference tests.
The sole transformation removes `/usr/bin/qemu-x86_64` before `/inputs/helper`.
[Manifest](workloads.json) pins each original/transformed script, existing expected
stdout, exact exit and current helper source. All native cases remain NOT RUN.
No shell behavior or expected error is relaxed to fit current producer support.

## Admission and fixture contract requiring owner agreement

Before execution, select matching dash source/config/generated files, SDK/adapter,
helper ELF, kernel, startup envelope and explicit resource limits. Record hashes,
compiler flags, target ABI, runtime, timeout and independent terminal/reclaim oracle.
The helpers must execute as native child images with argv/environment, not through
an emulator. Give the shell WITNESS=value, LC_ALL=C and PATH=/nonexistent.

The logical `/inputs` fixture needs executable helper, a missing `missing` entry,
a present but non-executable `not-executable` entry and denied write to `denied`.
`/scratch` needs a fresh empty writable namespace per test. Names alone confer no
native authority. The owner must explicitly provide/review these mappings before
claiming the existing cases run natively; path strings do not authorize installation.
Do not mount/write real system prefixes or mutate an unrelated service namespace.

## Ordered acceptance

1. Run actual dash initialization with checked custom handler/mask semantics.
   Then argv, signal-table and syntax-error cases. The earlier startup probe is
   prerequisite evidence only; dash trap setters can hide unsupported operations.
2. Run wait, failed-exec, fd-closure and deliberate fd-leak-control. Require exact
   exit22 for the leaked-descriptor control, status7 collected by the wait script,
   and127/126 for missing/non-executable images as checked by the script. Parent
   status must survive child failures and all owned children must be reclaimed.
3. Run redirection, denied-redirection, pipeline, substitution and early-reader.
   Preserve shared offsets/FD restoration, last-endpoint EOF and checked EPIPE.
   The early-reader helper attempts up to16 MiB through a pipe until EPIPE; this is
   a bounded progress test, not a requirement to allocate a16 MiB pipe. Its4096-byte
   local buffer plus native stack usage needs an explicitly reviewed stack budget.

Use exact stdout and exit from workloads.json; do not demand Linux-specific stderr
wording. Capture stderr for diagnosis and agree native diagnostics before publication.
A matching success text alone cannot establish child status, signal delivery, denied
authority or cleanup. The owner-observed status/reclaim context must accompany it.
Syntax-error exit2 and fd-leak exit22 are expected negatives, not infrastructure
failures. A crash, timeout, unsupported operation or uncertain cleanup never passes.

This is the first existing-workload subset, not complete M3 acceptance. ENOEXEC
fallback, large here-documents, interruption/wait races, nested state and broader
failure cleanup still need exact owner-reviewed cases. Track these within UL-007;
TTY/jobs/Zsh remain UL-008/009. Source/license trust remains UL-016. Do not expand
optional utility/benchmark work while these dependencies are unresolved.
