# Guarded SDK independently consumed — 2026-10-04

**The SDK error-handling blocker is closed in its bounded native scope.**
OpenZFS still cannot execute safely without real providers and qualified engine
configuration/resources. This R1-03 intake preserves kernel/runtime, sibling
repositories, old SDKs, existing shell kits, quotas and released standards pins.
[Contract](contract.md) records the pre-implementation scope/security/simplicity;
[source review](source-review.md) records acceptance and remaining boundaries.

[Setup](setup.json) verifies userland's complete23-file producer seal and its
retained archive (7310 regular files,336 directories,one inert historical link),
the selected241-file SDK delivery/256-member archive, and all28 files/322 archive
members of the prior Aether startup packet. Every retained regular archive member
is read back under its exact archive hash. Historical link metadata is never
extracted or followed. Only verified candidate regular files and selected real
startup objects are copied into this owned experiment.

The candidate seal is
f6bc6d6da3b051e1e4617e60ae256cbd35d193b608631ac29f7c42dbe73b13dc;
libc SHA256 is2459a32ba53cfc1dd62160d4bb8ea8e1afbac3615f2784c7351ad04f91183719.
All staged files except libc match the old SDK, including headers and startup
objects. A reader that preserves duplicate basenames compares all1349 object
occurrences: only clock_gettime.lo/sysconf.lo differ. No libc-wide or provider
conformance is inferred from those unchanged bytes.

## Independent native evidence

[New probe](probe.c) compiles with the existing C11/freestanding/no-builtin flags,
Clang21.1.8 and -Wall/-Wextra/-Werror. Real native memory adapter/driver source is
copied unchanged except the probe hook; no provider stub is linked. Three fresh
QEMU11.1.1/q35/TCG/qemu64 cases exercise two isolated instances each:

| Case | Required observed result |
| --- | --- |
| Corrected candidate | Realtime rejects-1/ENOSYS with unchanged sentinel/outer canaries; physical and available pages reject-1/ENOSYS. Raw clock/gettimeofday/sysinfo and uname/getentropy/device open remain unsupported with exact errors; caller buffers remain unchanged. Public monotonic errno remains EINVAL. Both contexts then pass the existing24-byte output/64-yield/terminal acceptance. |
| Old clock | Same realtime check exits240 in both contexts, with the exact ordered native terminal/panic oracle. |
| Old pages | Separate negative image deliberately repeats the unsafe old sysconf branch; both exit241 at the exact check. No returned page count is accepted or used. |

[Native results](native-results.json) bind commands/times, libraries, ELF/envelope/
ISO/log bytes and full source/SDK/tool inventories; qualified inputs stay frozen.
Images have no external imports or relocations. musl's local hidden zero UND
_DYNAMIC sentinel is distinguished explicitly. These are denial semantics, not
actual clocks, resource accounting, entropy or native OpenZFS startup.

The sealed engine/startup/adapter objects relink against the corrected library.
The new ELF remains4,371,768 bytes; its bytes change with libc, not its geometry.
[Actual parser/layout checks](geometry-results.json) accept1309 pages/fixed stack,
4-byte TLS and739 remaining pages under existing large limits. Ordinary limits,
W+X and4097-byte TLS mutations reject. Entry is never invoked. Remaining arena
space is not measured peak heap/thread-stack admission.

Actual executable disassembly still includes extended-state implementations.
Upstream SIMD helpers check OSXSAVE before xgetbv and enabled YMM/ZMM state before
availability; native runtime keeps OSXSAVE disabled and preserves x87/SSE only.
The named source review narrows the next profile work but does not qualify all
dispatchers, tunables, algorithms, CPU models or interrupted crypto execution.

## Failures, checks and retention

Three setup failures remain: rejecting an inert historical absolute Makefile
symlink; comparing regular-file7310 with all7647 entries; and treating the SDK's
241 count as payload files rather than240 plus seal. Fourth setup verifies the
actual sets; a final fresh-root replay also passes without depending on failures. Native preflight1 rejects duplicate object basenames; preflight2
links but rejects the local hidden _DYNAMIC sentinel. Third native attempt and
geometry pass. Earlier failures never entered a VM and remain distinct from the
three deliberate native controls. The first local final-check adapter also fails before commands because it uses
the prior geometry receipt field name; the corrected adapter checks the actual
input_bytes_unchanged field. Exact recipes/sources/logs/receipts are retained.

Full133-Python host suite plus Zig/Rust/pins/workflow, simplicity snapshot digests,
new C/Zig formatting, Python syntax and local links pass. No kernel/ABI behavior
change requires unrelated target regressions; the affected optimized library and
its exact old-library controls run natively. This is local independent technical
intake, not a reader walkthrough, SDK promotion or assembled release acceptance.

Original probes/recipes use BSD-2-Clause; [musl notices](COPYRIGHT.musl) and
OpenZFS [license](LICENSE.OpenZFS)/[copyright](COPYRIGHT.OpenZFS) remain distinct.
Verified SDK source/archive/recipe/patch inputs and selected engine objects remain
in this archive; complete engine/dependency sources remain in the bound earlier
packets. No normal ISO engine payload or distribution clearance is added.

Private [setup](setup.py), [native](native.py), [geometry](geometry.py),
[check](checks.py) and [retention](archive.py) recipes are evidence, not maintained
entry points. Reproduce with fresh output constants, exact sealed inputs and
recorded tools; never overwrite evidence. New archive members are all read back
before only this turn's owned workspace is removed. Current error guards are
qualified; native profile/providers/resources and real startup/fini/restart remain
the next work before granted storage and Rust filesystem/package integration.
