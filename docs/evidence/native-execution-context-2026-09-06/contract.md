
## Execution-state separation contract — 2026-09-06

Before implementation: separate the native saved interrupt frame, aligned FX state,
FS base and clear-TID pointer from domain-owned mappings, backing, grants, streams,
lifecycle records and accounting. Embed one execution context per existing domain
for this prerequisite; no new syscall, thread count, scheduler choice or wait API.
OpenZFS requires multiple shared-address-space contexts, and the current single
frame/FS pair cannot represent them. Do not emulate pthreads with independent
address spaces or successful no-op locks.

Aether owns context switch and cleanup mechanisms. Userland will own libc thread
construction/adaptation; sys-init owns domain lifecycle policy, pkg-mgr artifacts.
Future threads must share only their domain's existing authority and backing;
separate thread exit/join from domain stop/reclaim. Future memory protection must
pin all live contexts' TLS/TID/stack storage and stop must quiesce every context
before reuse. Those are next-step requirements, not implemented APIs here.

The context keeps the existing 176-byte normalized frame and 16-byte aligned
512-byte FXSAVE/FXRSTOR storage. No pointer escapes owner-local storage; retain
current interrupt exclusion and assembly clobbers. On completed reclaim, scrub
the entire execution context after clear-TID and mapping cleanup, not just FS.
A zero context is not runnable; load must initialize FP/frame state before admission.
No heap, FFI, dependency, ambient authority or new public tool/profile.

Check layout/alignment, independent contexts and complete reset on host. Run both
native memory profiles, large executable replacement, an actual native libc
TLS/FP startup image and default boot. Preserve source snapshots, all attempts,
markers and scoped claims. General threads/waits, per-thread resource pins,
optimized-mode/stack evidence and consumer adoption remain open.
