# libzpool runtime integration reassessment

Review-only follow-up to the paired musl condition-waiter qualification. No runtime
sources, sibling repositories, dependency installations or release pins changed.
The authoritative requirement matrix and next witness contract are in
[OPENZFS-FEASIBILITY](../../OPENZFS-FEASIBILITY.md#runtime-reassessment-after-paired-condition-waits--2026-09-06).

`inputs.json` records exact original archive, three reviewed engine source hashes,
retained Linux executable identity and the derived default stack demand. All three
engine files compared byte-for-byte with the original retained source archive:
`lib/libzpool/kernel.c`, `lib/libzpool/taskq.c`, `include/sys/zfs_context.h`.
Upstream source/notices remain in the original archive; no relicensing or patching.

Reviewed paths establish unconditional system-taskq startup, 64+4 worker requests,
TS_RUN detached defaults, 256-KiB default stacks, rwlocks, timed conditions and
thread-specific data. Requested stacks total 17 MiB before other allocations;
this is not RSS, peak usage, minimum engine capacity or a native budget.

`dynamic-symbols.log` was freshly generated with:

```sh
/opt/homebrew/Cellar/llvm@21/21.1.8/bin/llvm-readelf --dyn-syms --wide \
  zig-out/openzfs-x86-2026-09-06/work/owned-probe
```

It identifies imports of a Linux PIE; it does not turn archive imports or Linux
host facilities into proposed native syscalls. Prior engine execution and the
latest native threading/memory results are retained evidence, not rerun here.
The current native adapter/source contracts were inspected against these needs.

Next is a bounded actual musl reader/writer-lock witness using existing grants,
not larger global arrays or no-op locks. Timed conditions, key destructors,
detached reclamation, measured service budgets, platform/vdev port and filesystem
composition remain separate explicit requirements. Independent owner acceptance
and full R1 qualification remain open.

Validation passes: original-source comparison, fresh ELF dynamic-symbol
inspection, Zig/98 Python host tests (including all three offline pins), workflow
inventory and diff checks. No new QEMU run was needed for this review-only change.
