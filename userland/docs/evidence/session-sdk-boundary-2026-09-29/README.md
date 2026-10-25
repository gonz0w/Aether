# Session SDK boundary audit — UL-081 / UL-007

UL-081's current integration-boundary assessment is complete. The
[owner delivery handoff](../../SESSION-SDK-BOUNDARY.md) selects an explicitly pinned
opt-in application runtime closure. Shared runtime implementation and independent
reader review remain pending; full UL-007/M3/R1 remains open.

The accepted serial parent relinks byte-for-byte to ELF SHA256
`7adbe1cff61892bf647c3c28558f364dad9dda2ea664d2bd2a8b5961cc44596c`.
The exact archived private object inputs,895-source export,4311 SDK files, compilers
and unchanged owned process helper were verified before consumption and afterward.
Only selected regular archive members were restored under a new private build root.
No sibling/runtime or installed SDK bytes changed; no new native run was performed.

| Static experiment | Observed result |
| --- | --- |
| Exact component closure | Link0, identical whole accepted ELF |
| Missing startup/session facade | Link1, __wrap_main unresolved |
| Missing memory adapter | Link0, different ELF; __mmap/mmap/mprotect/munmap resolve from musl members |
| Missing six fork/wait/rebind objects | Link1, copy_rebind unresolved |
| Duplicate facade | Link1, duplicate strong symbols |

Thirty actual symbol providers are recorded for baseline and memory omission in
providers.json. Public sigprocmask comes from the facade, while sigaction and
internal __block_all_sigs/__block_app_sigs/__restore_sigs come from the native musl
archive. The accepted native shared-mask evidence remains prior qualification;
this static observation is not a new signal-runtime test. All successful link
layouts are checked for their exact _DYNAMIC sentinel, with baseline comparison
against the accepted ELF, no INTERP/DYNAMIC header and no relocations.

The omitted-memory ELF is not natively qualified. Its successful link exposes why
component receipt/provider checks must reject missing adaptation before build or
admission. Packaging the fixed session wrapper into a library alone cannot create
a supported shared runtime or grant authority. Current application main/namespace
policy and per-process runtime state need an explicitly owned integration boundary.

Five link experiments and provider/symbol/header inspections pass. All commands use
absolute pinned tools, explicit environment/cwd,30-second deadlines,16MiB streams,
owned private output roots and complete process cleanup. Exact argv, input digests,
map files, raw outputs and receipts are retained. Both small audit build roots remain
recorded for reproducibility; no large native suite/cache was generated.

## Retained correction

The first audit reproduced the accepted ELF, then incorrectly demanded zero nm
undefined entries. Its existing linker sentinel _DYNAMIC made that assertion fail.
The original accepted ELF has the identical entry; the fresh corrected run requires
that exact sentinel plus absence of dynamic/interpreter headers and relocations.
No arbitrary missing import is allowed and no different baseline is accepted.
Original driver, pins, incomplete report, maps and receipts are in initial-attempt/.
See attempts.md. No native retry or new runtime success is claimed.

## Blocked next step

[SSDK-01–06](../../SESSION-SDK-BOUNDARY.md) specify the independent build/authority/
state/regression/review gates for a future owner-agreed runtime delivery.
[Reader review packet](../../quality/SESSION-RUNTIME-REVIEW.md) binds current inputs
and requires actual reviewer identity/findings; older SDK transport approval cannot
approve this boundary. Aether's current private serial delivery remains the exact
reference, with no standalone supported runtime bundle supplied in its handoff.
SI-07 separately needs complete versioned bootstrap/transport and rebuilt runner/
bytecount. These missing deliveries/reviews block dependent native integration.
No package/service policy, shared standard, source trust or release approval follows.

Final preservation/syntax, quality and whitespace checks pass. All895 source and
4311 SDK hashes, selected object/tool/archive pins and the serial, scratch and serial
preparation seals remain unchanged. final-checks.json records the exact scope and
pending owner/reviewer gates. SHA256SUMS seals this packet, including the retained
initial audit attempt; successful static checks do not promote runtime acceptance.
