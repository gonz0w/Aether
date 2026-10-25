# Integration readiness review — 2026-09-05

The four projects have a bounded executable integration path: package transport,
native musl startup, and sys-init-controlled launch/readiness/fault/replacement.
They are ready for the next targeted integration experiment. They are not yet a
usable installed OS or a native package-manager environment.

## Findings, in action order

1. **The supervised package handoff is outside the normal regression gate.**
   `tests/check.sh` covers fifteen fixtures, including boot v1/v2, but omits
   `tests/aether-supervised.py`. The latter passes independently today: one valid
   synthetic transport and seven rejection cases. Changes to the six-artifact
   handoff can therefore escape the normal gate. Add it to that gate next,
   preserving its distinction from a QEMU/native acceptance test. Its contract
   also still mentions twelve shell tests; that is historical, not the current
   suite count. No runtime incompatibility was observed by this review.

2. **The native memory extension is the most concrete next shared contract.**
   Userland UL-028 has delivered a central draft and a scoped implementation
   plan. UL-003 owner acceptance remains open, followed by UL-015 adapter and
   UL-006 kernel/consumer work. The current pool is 128 pages per instance;
   workloads must account for startup occupancy instead of transplanting the
   MiB-scale Linux reference tests. Agree on arena, authority, quotas, errors,
   atomic failure and lifetime rules before adding native operations. The draft
   stays in Aether-standards; exact ABI and mechanisms stay with Aether.

3. **Output/supervision evidence does not provide an interactive environment.**
   The native service uses a bounded launch-bound output grant and fixture sink.
   General descriptors, input/TTY, process/signal semantics, VFS/storage and an
   agreed base selection remain open. Sys-init's host adapter separately records
   a parent-death containment gap and outstanding helper/exclusive-wait ownership.
   These prevent promoting successful fixture launch into general init readiness.
   Keep service-owned I/O/FD work separate from allocator acceptance.

4. **Release readiness is a separate gate from integration progress.**
   Aether's current M4 state records seven target regression cases and passing
   host/kernel checks, but still requires an independent committed-checkout
   witness, license/third-party decisions and a monitored security contact.
   Userland retains UL-016 authenticity work. Package hashes and private-root
   recovery do not establish release authenticity or durable installation.

## Current evidence and ownership

| Project | Established scope | Remaining gate |
| --- | --- | --- |
| pkg-mgr | Host source/binary workflow, private-root records, pinned replacement and receipt-loss recovery; saved boot/supervised transport witness | Normal supervised-transport coverage, authenticated distribution, target filesystem/install contract; no activation/deletion authority |
| Aether | Recorded SMP fault/replacement/display regressions; bounded native C and single-BSP supervised profile | Native allocation and runtime primitives; public-release prerequisites |
| sys-init | Bounded native lifecycle and supervised C client; current recorded host accounting/model/harness evidence | General ownership, parent-death containment, cross-host/native lifecycle expansion and service-owned I/O |
| Aether-userland | Native startup/context witness, supervised service variant, 18 bounded Linux memory/I/O reference cases, central memory proposal | Owner agreement and native allocator implementation; process/FD/TTY/VFS dependencies and final base selection |
| Aether-standards | Canonical Experience, Foundations and proposed Distribution releases | Native-memory draft is unreleased and unaccepted; no automatic consumer upgrade |

The Linux reference, host model, native fixture and release gates are distinct.
The package manager's POSIX shell/make core cannot run natively merely because a
bounded static-C service runs under Aether.

## Checks performed for this review

- Ran all three offline checkers in each of pkg-mgr, Aether, sys-init and
  Aether-userland: all twelve invocations passed.
- Compared every vendored release file against its canonical sibling copy:
  15 Experience, 26 Foundations and 18 Distribution files per consumer match
  (counts include manifest files; checker payload counts differ).
- Ran `python3 tests/aether-supervised.py`: valid transport plus seven rejection
  cases pass. It does not boot the synthetic input.
- Read current owner STATE/contracts and saved supervision/M4 results. No QEMU,
  kernel build, full package suite, sys-init host suite or Linux-emulated workload
  was rerun for this review.
- Five current files match their hashes in the saved package supervision source
  inventory: Aether `native_c.zig`, userland `native-c/build.py`, sys-init
  `build-native-supervisor.py`, and pkg-mgr's supervised transport/test. This is
  a spot check, not complete source-to-image reproduction.

No sibling implementation, shared release, pin or ABI was changed. This report
is a local review record, not a new shared standard or owner acceptance.

## Source documents

- [Package supervised handoff](SUPERVISED-HANDOFF.md) and [saved results](evidence/native-supervision-2026-09-05/results.json).
- [Aether current state](../../.planning/STATE.md) and [supervision results](../../docs/evidence/native-supervision-2026-09-05/results.json).
- [Sys-init current state](../../sys-init/.planning/STATE.md) and [native supervision contract](../../sys-init/docs/NATIVE-SUPERVISION.md).
- [Userland current state](../../userland/.planning/STATE.md) and [native-memory implementation plan](../../userland/docs/NATIVE-MEMORY-PLAN.md).
- [Central contract catalog](../../../Aether-standards/docs/CATALOG.md) and [native-memory draft](../../../Aether-standards/docs/NATIVE-C-MEMORY.md).
