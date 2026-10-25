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
