# UL-067 three-stream prerequisite

Before code, 2026-09-07. Select private AECAT001 role carrier128 bytes: header
magic8/count3/generation/zero16; three32-byte records role1..3/ref/fd0..2/rights
1,2,2/cap32,32,256/zero12. Refs0x76000000+(index<<16)+generation. Validate the
entire carrier before publishing any binding. Same bounded read/write/close frames
as existing transport, separate private backend input/stdout/stderr. No runner
stderr substitution, ambient authority, new kernel ABI or quota increase.

A direct conformance client plus backend (slots0/1, two generations/four reclaims)
qualifies the bootstrap/copy prerequisite only: no command child admission/receipt
or Toybox is claimed. Copy empty or exact32-byte binary fixture, force7-byte reads
and3-byte writes, and independently test a diagnostic sentinel. Preserve input,
verify exact output/opposite sink and positions, close all aliases/backend handles,
require request EOF at terminal, stale denial and kernel cleanup. Invalid third
rights/FD/ref and count publish nothing/status110. Skip/corrupt-copy/omitted close
and early-publication controls must reject exact owner checks.

Use existing synchronous bounded transport/FFI with stack frames, no new unsafe
block, allocation or dependency. New source BSD-2-Clause. Userland owns Toybox,
umask/locale/stdio/termination adaptation. Initial0077 process-local mask remains
a proposed userland state decision, not a new bootstrap field or successful stub.
Exact cat admission/startup/finalization and CAT acceptance remain open. Keep UL-059
handoff bytes/pins immutable, no sibling edits. Update NATIVE-CAT, workflow, STATE;
full command, connections/inherited, host/Zig/pins and C/Rust formatting on frozen
sources, retaining all attempts and explicit timing limitations.
