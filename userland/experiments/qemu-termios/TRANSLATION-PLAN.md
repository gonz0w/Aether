# UL-069 CMSPAR translation slice

Verify the QEMU 10.0.11 archive and all retained build inputs before consumption.
Prepare a guarded CMSPAR row in linux-user/syscall.c's cflag_tbl; no other source
changes. Preserve GPL/LGPL notices in extracted upstream fragments. This is a
local dependency patch proposal, not an Aether ABI or native TTY change.

Compile the actual upstream bitmask translation functions and cflag table's
non-baud rows with pinned Clang 21.1.8 in a host-only test. Use pinned target
constants and deliberately different synthetic host CMSPAR bits to detect false
identity mapping. Enumerate all character sizes and eight independent control
flags in both directions. Baseline and wrong-host-bit mutants must reject;
patched, missing-host-CMSPAR and missing-target-CMSPAR variants must pass with
explicit omission in the unsupported variants. No unsupported success is claimed.

This tests selected translation code, not a built emulator, ioctl/PTY behavior,
termios recovery, full baud handling or GNU/BusyBox acceptance. Offline container
build of the unpatched/patched emulator and full PTY regression remain next UL-069
work. Host controls cannot close those gates or source authentication under UL-016.

Quality change review: Foundations E-01–07, approved CP/C/CD and TD/TE apply.
Private build outputs, owned process helper, fixed environment, per-command 30s
limit and 3-minute suite budget. Generated upstream fragments retain original
style/notices; new orchestration is BSD-2-Clause. No upstream/generated formatting
migration. Record compiler, input/patch/driver/generated-source hashes, every argv,
expected/actual exits and cleanup. Run local quality gate. Independent review of
this new UL-069 slice remains pending; SDK approval does not cover it.
