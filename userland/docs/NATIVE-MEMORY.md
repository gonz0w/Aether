# Userland adoption of native-memory v1

2026-09-05, UL-032. Userland adopts the exact bounded
[Aether-owned memory ABI](../../aether/docs/NATIVE-MEMORY.md) for an opt-in
libc/descriptor consumer. Shared design remains in Aether-standards; no released
standard or wire profile is revised by this adoption. The previous kernel-work
hold is lifted by the user's instruction and delivered implementation.

## Implementation

`experiments/native-c/native_memory.c` owns the libc mapping facade. It retrieves
the caller-local grant from auxv 0xa000 and uses the kernel-defined interrupt
0x81 operations 0x22000–0x22003. Inline assembly accounts for overwritten RDX,
RCX and R8 and zeros reserved input fields. No granted value is synthesized or
cached across instances; the kernel enforces caller/generation authority.

The adapter overrides public and internal mmap/mprotect/munmap symbols when
`--io --memory` is selected. It accepts only anonymous private mapping, zero hint,
fd -1 and zero offset; other classes return ENOSYS. Negative native results
become errno without converting EACCES/ENOSYS into fake ENOMEM. Protection keeps
musl's address rounding, with nonzero length and overflow checks before rounding.
Native brk and remap remain unsupported; the strict native mallocng build takes
its tested mapping/copy fallback. The descriptor facade remains in place; output
does not use the kernel conformance adapter's legacy-write bypass.

The kernel arena, 128-page total quota, NONE/R/RW restrictions, generation-bound
rights, conservative TLS/TID pinning and atomic range checks are unchanged.
Ordinary dangling C pointers are not capability handles. These are adapted native
semantics, not general POSIX mmap/munmap compatibility or authenticated sessions.

## Consumer and evidence

The combined probe executes memory checks before the existing I/O/readiness flow:
allocation and metadata initialization; growing realloc with byte preservation;
quota-failed realloc preserving the old buffer; zeroed calloc; direct zero-filled
mapping; subrange PROT_NONE denying descriptor output with EFAULT; access restoration;
unmap/reallocation and free-page accounting; unsupported shared-map rejection.
It sizes requests for the bounded target instead of copying MiB-scale reference
workloads. Admission records 24 pages used and 104 remaining for each generation;
post-malloc accounting permits retained allocator metadata.

Two successive supervised generations complete memory and descriptor checks,
then the sys-init-owned fixture observes successful terminal cleanup. The retry
variant requires an actual EACCES on the first malloc metadata protection, then
successful retry. Running that variant without injection must exit 81.

[Retained evidence](evidence/native-memory-userland-2026-09-05/summary.json) records
nine memory-enabled outcomes and four ordinary descriptor regressions:

| Case | Required result |
| --- | --- |
| Combined positive | Two generation exits 0, exact existing descriptor output, reclaimed=2 and existing I/O success marker |
| Bad dup / withheld output / skipped terminal zeroing | Existing descriptor controls reject |
| Missing memory grant | Consumer exits 61 before readiness; specific terminal record plus expected supervisor rejection |
| Skipped permission tightening | Consumer exits 73 at PROT_NONE descriptor-copy check; exact terminal record required |
| Metadata denial/retry | Retry-only variant succeeds twice under one-time protection-denial injection |
| Missing denial control | Retry-only variant exits 81; false success cannot satisfy the suite |
| Memory option disabled | Consumer exits 61 without usable memory query; existing profile is not silently enabled |
| Ordinary descriptor regressions | Fresh --io build retains four expected outcomes without the memory option |

No kernel/sys-init working-tree files were modified. Each suite uses a fresh
kernel snapshot, source hashes, explicit envelopes, private outputs and bounded
build/QEMU timeouts. Missing tools or unrelated crashes cannot substitute for the
specific new consumer terminal outcomes. Original Linux reference evidence remains
separate and unchanged.

## Reproduction

```sh
python3 experiments/native-c/build.py --io --memory
python3 experiments/native-c/test_io.py --aether /absolute/aether --sys-init /absolute/sys-init --sdk /absolute/emitted-build --work /absolute/new-private-run
```

`--memory` requires `--io`; it adds memory sources and a retry-only negative-control
artifact to the build receipt. `test_io.py` verifies artifact and memory-source
hashes, selects `-Dnative-memory=true` except for its disabled-profile control,
and retains exact commands, kernel/producer snapshots and serial logs. Repeat
with plain `--io` for the existing descriptor-only suite.

Remaining work: broader malformed/overflow and direct hardware-fault consumer
coverage, larger/pre-main TLS, general file/process/TTY behavior, source trust and
end-to-end packaging. The kernel already records its own nine-case memory suite;
those results remain kernel-owned evidence, not tests rerun by this consumer.
M2's complete gate review and broader UL-003/006/015 remain explicit follow-ons.


## M2 gate review

UL-033 adds combined argv/env/data/BSS and malformed-image checks. The
[twelve-case current-artifact suite](M2-ACCEPTANCE.md) closes the original M2
minimal C gate in its bounded scope. Earlier statements that gate review is
pending are superseded; broader POSIX/runtime limitations remain unchanged.
