# Corrected private ABI29 boot client — v2

This separately sealed correction targets the existing AENFS003/ABI29 boot
profile: supervisor6 stays generation0/PID7; shell1 has PID9/16/23 in its three
generations and always observes PPID7. Copied children2–4 retain their shell's
native parent identity. AEFSH001 layout/startup symbol and all bounds stay fixed.
The old v1 linked candidate rejects the genuine boot parent and is not usable for
this startup. Its immutable bytes remain retained for evidence; do not select it.

The decoder requires the real observed PPID and frame parent to match, and requires
exact boot parent7 for a shell. Synthetic restarted owner14/21/28 is rejected even
if the supplied observation agrees. Native memory/PID/child-parent checks remain
strict; numeric names/labels never grant authority. This is a host-tested and
linked correction, not a new kernel model, native shell witness or SDK promotion.

The pinned complete recipe rebuilds runtime/application, memory, public musl
fork/wait/rebind and the serial helper. CRT/libc/dash remain explicitly prebuilt
pinned dependencies with original notices. All45 parent/eight helper link inputs
are checked, along with explicit ABI29/serial/wait selection on all four client
compiles. Choose the externally reviewed SHA256SUMS digest before calling
support/rebuild.py's rebuild(bundle,new_output,expected_seal), Python3.10+.
Every tool/input is checked and each owned compiler/link process has60s/16MiB
bounds. Output must be a new private directory outside this bundle. No network,
installation, guest launch or native authority is provided by this builder.

Initial host kernel parser/backing fit is separate from peak stack/heap/runtime
acceptance. The zero LOCAL HIDDEN UND _DYNAMIC symbol is the inherited static
libc sentinel, not a global import or dynamic loader. Native execution, matching
sys-init dispatcher, AF07-backed FD/path/immutable executable translation,
cleanup/fresh-boot persistence, packages, Zsh/TTY and independent reviews remain
open. The existing /inputs/helper serial workload is not a filesystem loader.
