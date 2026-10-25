# M2 acceptance: bounded native C runtime

2026-09-05, UL-033. M2 and UL-006 are complete **for the original minimal native
C gate**, using the opt-in native-memory v1 plus descriptor fixture. This is
userland consumer acceptance of tested kernel-owned interfaces, not ratification
of every shared proposal, production release readiness or POSIX conformance.
No new cross-project reviewer sign-off is invented. UL-003/015 retain broader
ABI/service ownership and adapter work; M3–M5 remain incomplete.

## Gate and exact evidence

The original milestone requires a static musl test reaching main, validating
arguments/TLS/BSS, exercising memory and I/O, exiting with observed status, and
passing denial/exhaustion/malformed-image checks. A fresh combined artifact now
covers these requirements in one twelve-case suite:

| Gate | Consumer witness |
| --- | --- |
| Static C startup | Pinned native musl source rebuild; inspected static ELF, no unresolved externals or Linux syscall instructions in the linked fixture |
| Arguments/environment/data/BSS | main checks argc=2, argv[1]=check, AETHER_PROBE=reference, initialized data=23 and zero BSS |
| TLS | Existing I/O fixture checks private initialized TLS; prior native context experiments retain their broader FP/TLS scope |
| Memory | Real malloc/realloc/calloc, quota failure preserving old bytes, zeroing, subrange protection, restore, release/reallocation and accounting |
| I/O | Existing descriptor fixture checks read/write, duplication, byte order, direction, EOF, bounded transfers and invalid-pointer non-consumption |
| Exit/cleanup | Exact successful terminal records for generations 1 and 2, expected output and supervisor result=100/reclaimed=2 |
| Authority/protection denial | Missing grant exits 61; skipped protection exits 73 at the protected-buffer output oracle |
| Metadata failure/retry | A retry-only variant requires an initial EACCES and successful retry; absence of injection exits 81 |
| Malformed images | Wrong machine and writable-executable LOAD reject as invalid supervised ELF; invalid service length rejects the envelope before worker admission |
| Existing controls | Bad duplicate retention, withheld output and skipped terminal zeroing retain their expected rejection; memory-disabled profile rejects the memory consumer |

[Retained report](evidence/m2-acceptance-2026-09-05/summary.json) binds the exact
build, adapter/probe sources, kernel snapshot, sys-init producer, commands, images
and serial logs. Malformed inputs derive from the emitted AENFD001 envelope;
records preserve both original producer hash and mutated envelope hash. A specific
panic with no worker-admission/terminal record is required, not a generic timeout.
All twelve cases pass their expected outcomes. Kernel/sys-init working trees are
unchanged; builds ran in a fresh private snapshot. The preceding UL-032 run
separately recorded four memory-disabled descriptor regressions; those are not
presented as fresh runs in this report.

The reference and kernel-owned suites remain supporting evidence with their own
source snapshots and limitations. This acceptance does not merge their run counts
or claim every negative was exercised through the current userland consumer.

## Limits carried forward

Single core/thread, two successive fixed supervised generations, explicit bootstrap
memory grants, eight descriptors/three fixture streams, 128 total backing pages,
small initial TLS, no shared/file/executable mappings and no public brk/remap.
Developer identity/host bootstrap entropy are not login or a native entropy service.
Full extended CPU state, large pre-main TLS, production signal/process semantics,
SMP allocation, filesystem and terminal services remain out of scope. Source
integrity is not source authenticity or release eligibility. The original C gate
can close without pretending these broader goals are implemented.

## Next useful shell step

UL-034 completed a [pinned dash reference build](../experiments/dash-reference/README.md)
and twelve bounded script outcomes. UL-035 completed the musl process/FD audit
and nine-case witness; UL-036 now targets unchecked descriptor fallback errors. This is package feasibility work in userland; it neither ports
dash to Aether nor selects it permanently as the recovery shell.

The first useful M3 workload should execute an external helper from a script in
a bounded namespace, then demonstrate redirection, a finite pipeline and wait/
reap with no leaked children or descriptors. Required native dependencies include
executable/path access, cwd, descriptor inheritance/CLOEXEC, process creation or
a justified shell adaptation, exec/wait and pipe lifetime. A prompt or builtin-only
shell cannot close M3. TTY/job-control work follows separately under UL-008/009.

Use the [compatibility inventory](compatibility/README.md) to select exact missing
interfaces and the [package candidates](research/PACKAGES.md) for provider review.
Shared interface requirements belong in Aether-standards; implementation assignment
still needs the relevant owners. No kernel modification follows merely from this
next package experiment.
