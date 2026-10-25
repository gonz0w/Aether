# Native-memory resource review — 2026-09-05

This is static artifact accounting, not native memory execution. The shared
[implementation review](../../../../Aether-standards/docs/NATIVE-C-MEMORY-REVIEW-2026-09-05.md)
records candidate owner decisions and acceptance gates. No ABI or runtime changed.

Reproduce from pkg-mgr (the retained build path must still exist):

```sh
python3 docs/evidence/native-memory-review-2026-09-05/footprint.py \
  /Users/cam/DEV/Aether/kernel/arch/x86_64/native_c.zig \
  /Users/cam/DEV/Aether-userland/build/native-c-5olokhku/startup.elf
```

[startup.json](startup.json) and [control.json](control.json) bind exact ELF/kernel
hashes. Both count five image pages plus sixteen fixed startup/stack pages, leaving
107 nominal backing pages. The reader checks the known loader resource literals
and the bounded ELF tables used by these retained artifacts. It is a review
utility, not a general ELF validator or package runtime tool. A future allocator
ELF must be remeasured. Runtime TLS/allocator metadata and temporary realloc
allocations must be charged by the eventual implementation.

The strict native build and descriptor regression were inspected in userland's
[UL-030 evidence](../../../../Aether-userland/docs/evidence/strict-native-libc-2026-09-05/summary.json).
Those earlier native tests were not rerun. Their descriptor startup evidence does
not execute the proposed native allocation/protection operations.
