# Runner startup carrier qualification — 2026-09-06

Final pass: 39 command cases, 9 inherited-launch cases, 6 connection cases,
kernel host checks, 73 Python tests, three release-pin checks and workflow gate.
Pinned C/Rust formatting checks pass. The opt-in broker is 7448 bytes (8192 limit).

Three/six-string native witnesses retain empty and 31-byte arguments after copying
and source-buffer mutation, then complete the original exit-29 command workload
with six reclaims. Six malformed carriers reject at broker 994 before worker
terminal records. A changed but valid argument must produce parent 110 then broker
970. These exact outcomes are required; unrelated failure or timeout is not a pass.

The [initial attempt](../native-runner-startup-initial-2026-09-06/README.md) failed
its last control: parent correctly detected the changed argument but exited before
the next binding frame finished sending, producing transport failure 990. The
final witness drains that frame without publishing bindings before exit. All
selected suites reran on frozen final bytes. Initial failed source/logs remain
separately archived; later suites were not run on the failed attempt.

[Contract and review](../../NATIVE-COMMAND-IO.md#runner-startup-carrier-v1).
The UL-059 proposal is retained with its digest under docs/reviews. This implements
an opt-in user-space data carrier, not native argv expansion or a public CLI.
The independent probe does not yet forward the carrier's arguments to the child.
Legacy exit 29, authority, ABI and quotas remain unchanged. Public result mapping,
help grants, userland parser/adoption and package/service acceptance remain open.

`results.json` binds suite reports and final source archive. Profile directories
retain raw serial/build/static-analysis logs, native payloads, startup records,
client/kernel ELFs, raw broker images and maps under 2 MiB. ISOs are rebuildable
and omitted; complete original output paths remain recorded. Each startup record
has a size/digest and explicit build environment entry in the suite report. Source,
tests, contracts, proposal snapshot and approved standards snapshot are archived;
external SDK/tools remain separately bound by suite receipts/digests.

`*-attempt.json` records commands, UTC start/end and exit status captured around
runs. `format-attempts.json` records pinned format checks. This is producer/QEMU
evidence, not independent consumer/hardware acceptance or full standards compliance.
