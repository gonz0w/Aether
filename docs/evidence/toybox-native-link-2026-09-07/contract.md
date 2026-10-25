# Real Toybox native SDK build audit

Before build, 2026-09-07. Compile unmodified Toybox0.8.14 standalone cat source
against the exact native-c-5olokhku SDK used by the qualified cat conformance
fixtures. Pin archive827e4cdfd69f5da973e00e2a59b30b3c9857fb7fae74c362fd0b4f96be7929b0,
reference-generated headers/config separately, SDK inventory, tools and adapter.
Compile all upstream lib C units/main/cat using retained upstream warning/section
flags; link with existing native memory/raw-I/O adapter and section GC. Preserve
Toybox license and original notices; no source patch or successful syscall stub.

This is object/link/ELF/call-path evidence only. Do not boot the unadapted artifact:
no AECAT001 role bootstrap, process mask, private stdio bridge or terminal seam is
supplied. Require static x86_64 ELF, no dynamic interpreter/unresolved symbols,
NX stack and no W+X segments; report loaded page/segment/TLS sizes without claiming
native loader acceptance, memory budget sufficiency or full syscall closure.
Disassemble named startup/stdio/exit paths and identify concrete missing adaptation.
Generated headers are separately captured inputs, not a fresh generator reproduction.
Retain actual config including upstream resolved fork setting, not just miniconfig.

No kernel/user runtime/build defaults/pins/UL-059 bundle/sibling modification.
Userland owns production mask/stdio/termination; this artifact cannot satisfy CAT
or release acceptance. Foundations O/I/E and DEVELOPMENT provenance/failed-attempt
retention apply. Record every command/status and frozen hashes, retain archive,
headers/objects/maps/logs and report. Run zig build test/workflow and diff check for
doc adoption. QEMU regression unnecessary because runtime sources do not change.
Update NATIVE-CAT/THIRD-PARTY/STATE with actual build and remaining native work.
