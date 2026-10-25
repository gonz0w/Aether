# UL-007/012 maintained lab boot check

Before-code plan: replace date-specific boot invocation with one maintained
ABI24-only host command consuming an externally selected kit SHA256SUMS.
No native code/grant/sibling policy change; default ABI23 remains separate.
Foundations O-01/03/04, I-02–06, E-01–08, CP-01–03, TD/TC/TE and offline
Experience OUTPUT/BOOT apply. BSD-2-Clause original tooling.

Success: verify exact regular-file kit inventory, complete hashes and receipt;
only pinned QEMU from receipt, fresh variables, new private build output.
Prompt-driven exact three commands,90 UART bytes, eight admissions, ten terminal
reclaims and halt via reused unchanged independent oracle. Delayed mode35seconds
first prompt/2 later; singleCPU TCG/qemu64/256MiB, no NIC, native90s, driver105s,
UART1MiB/stderr4MiB and outer16MiB files, explicit emulator/group reap.
Forbidden: kit executable hooks, links/traversal/duplicates/unknown inventory,
tampered tools/commands/receipt/firmware, overwritten output, input before prompt,
missing cleanup or pretending boot failure is semantic success.

Tests: actual Python3.10/current syntax/admission/CLI controls, corrupt kit and
trace rejection before native launch; fresh maintained immediate/delayed boot
of exact repaired sys-init kit; compare prior sealed logs and oracle logic.
Help/version stdout0, usage stderr64, missing2/operational1; success stdout path,
plain ASCII escaped errors. Retain all failures and outputs; quality plus all
three standards checkers. Document CLI/schema/failure recovery and coverage.

Simpler alternative: keep copying evidence scripts. Insufficient for reproducible
lab operation; extract the already-qualified driver/oracle into maintained files,
no generic emulator framework. No historical paths removed.
Technical review: implementation agent; reader/SSDK-06 deferred. No physical
hardware, release, general TTY/recovery or exhaustive timing claim.
