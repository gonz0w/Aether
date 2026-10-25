
## Large static-image contract — 2026-09-06

Before implementation: native-image-large requires native-memory-large and only
accepts AENATC01/AENSUP01. These explicit producer fixtures permit at most 8 MiB
of ELF input and 2048 image+stack pages; all default/profile limits remain intact.
The ELF stays static ET_EXEC, mapped PHDR, bounded 4-KiB TLS, R/RX/RW and NX stack.
Reject interpreter/unsupported headers, W+X, overflow, overlap, invalid entry,
quota excess, stack overlap, anonymous-arena intrusion and table exhaustion before
mapping any user page. The existing launch-layout validator supplies native
geometry checks. Other bundle ABIs remain at their own original limits.

Grow only the retained supervised image copy to 8 MiB in this opt-in build;
retain 1-MiB secondary/tertiary buffers and 64-MiB kernel-alias cap. Kernel owner
holds immutable bytes through worker generations; they grant no new authority.
Copy validated image bytes in page-sized chunks, with each destination chunk
bounded by one known backing page; no borrowed pointer escapes the copy call.
Source and destination are distinct immutable input/private backing allocations.
No FFI, dependency, global allocator or dynamic linking. Supervision policy and
production consumer adoption remain with sys-init/userland, packages with pkg-mgr.

Use a real rebuilt musl fixture with 2-MiB initialized data and 4-MiB BSS, verify
every byte/TLS and post-load anonymous allocation, then stop/reclaim and replace.
Reject the same image under the old loader, plus mutated PIE, W+X, BSS-over-quota,
stack and arena overlap. Keep hardware memory regressions, host parser boundaries,
Zig/new-C format, workflow and default boot. Freeze sources and preserve all attempts.
No OpenZFS/native thread/assembled-release result follows from large image loading.
