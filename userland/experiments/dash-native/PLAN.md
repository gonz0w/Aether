# UL-007 native-SDK link preflight

2026-09-07. Verify the durable dash0.5.13.5 reference object inventory and relink
those unchanged objects with the captured native SDK/CRT and existing native memory/
startup-I/O adapter. Inspect ELF segments, undefined imports and process syscall
bodies. This is a link compatibility experiment, not a source rebuild/native port
or runtime test. Linux-configured generated files and process calls remain explicit.
Do not boot the artifact under an unrelated utility oracle or replace missing
process/signal/FD semantics with successful stubs.

Use pinned Clang/LLD/tools, explicit target/no-default-config/nostdlib flags, private
build output and owned180-second commands. Validate SDK and source inputs before
consuming them. Retain build failures, hashes, flags and inspection output. Review
current owner contracts; record exact next producer requirements for real dash.
Foundations O/I/E and CP/TD/TE apply. Preserve upstream COPYING and first-party
BSD-2-Clause. Run quality; no new shared contract or sibling implementation edit.

## Startup contract probe

Add a silent, exit-status-only internal probe for positive/stable PID, checked
SIGUSR1 disposition and mask round trips, inherited descriptors 0–2 and atomic
F_DUPFD_CLOEXEC allocation at >=10. Restore signal state and close owned duplicate
on every applicable path. This is a prerequisite subset, not signal delivery,
identity authority, exec inheritance, fork/wait or native shell acceptance.

Compile the same probe on the host and with the pinned native SDK. Exercise host
success and injected bad PID, failed signal query, successful no-op disposition,
successful no-op mask and missing CLOEXEC. These controls must reject by stage;
no injection code enters the native artifact. Native execution stays NOT RUN
until a matching owner-reviewed producer profile exists. Use owned commands and
strict C17 diagnostics, pinned clang-format check, retain sources and every result.

## Delivered startup pair native reproduction

Consume only verified intake dash-startup-intake-lzvm3lp3. Verify captured source
and SDK archives and source member hashes, safely extract the confined SDK (one
internal relative Makefile symlink), and recheck unchanged consumer bytes. Use
pinned native/host tools and the previously verified private Rust wrapper. Run
captured zig host tests and unchanged full222 command suite, including nine startup
cases, with owned outer cleanup (300/1800 seconds) and existing guest watchdogs.
No producer source/oracle edit or native acceptance from producer-only results.
Retain raw output, failures, exact source/tool/SDK hashes; qualify only DFL/IGN/mask
state, descriptor/alias behavior and checked startup. Full dash work stays separate.


Serial candidate checkpoint (2026-09-11): see the [bounded consumer qualification](../../docs/evidence/dash-serial-consumer-2026-09-11/README.md).
The explicit jobs fork/exec and input fallback configurations are selected only in
that private profile, with original-object controls. They are not installed SDK
choices or libc vfork semantics. UL-081 must resolve the supported integration
boundary before broader adoption; independent source and reader review remain open.
