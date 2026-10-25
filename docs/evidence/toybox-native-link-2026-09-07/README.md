# Real Toybox cat linked with the native SDK — 2026-09-07

Unmodified Toybox0.8.14 standalone cat now compiles and links against the exact
native-c-5olokhku libc/tools used by the preceding conformance suite. The audit
compiled17 upstream translation units (main, cat and lib sources), linked the
existing native memory/raw-I/O adapter and inspected the resulting ELF. No source
patch, successful syscall stub, role bootstrap or global libc override was added.

Result:80,128-byte static x86_64 ELF,21 distinct load pages, no dynamic interpreter,
no unresolved externals, NX stack and no W+X load segment. It has no PT_TLS segment;
that is a structural observation, not runtime TLS validation. Page counts exclude
stacks, anonymous allocations and other native grants. Native loader acceptance
and resource sufficiency were not tested. The ELF is named toybox-cat-unadapted.elf
and **was not executed**.

## Concrete integration gaps

| Selected linked path | Static observation | Required next adaptation |
| --- | --- | --- |
| toy_singleinit → umask | Native interrupt operation0x1005f | Truthful process-local mask state and observed save/restore; no ENOSYS treated as valid initialization |
| __stdio_write | Native interrupt operation0x10014 | Reviewed private vector bridge over admitted roles, preserving partial counts, errors and no replay |
| xexit → _xexit | Callbacks, fflush_unlocked/ferror_unlocked then _exit | Candidate-local terminal seam after flush/rebound behavior; no global musl exit replacement |
| Scalar I/O/startup | Existing raw adapter; no AECAT001 bootstrap | Bind the real applet through qualified admission/roles and reject extra arguments before Toybox |

[Selected disassembly](boundary-disassembly.txt) and [boundary checks](boundary-check.json)
provide evidence for these paths, not an exhaustive call graph or syscall closure.
The first post-build check assumed the symbol name fflush; the selected code calls
fflush_unlocked. That [checker failure](audit-attempt-1.txt) is retained; correcting
the check changed no sources or artifacts. Compilation/linking passed first try.

The retained generated configuration selects only the cat applet but resolves
CONFIG_TOYBOX_FORK=y, despite the consumer's miniconfig requesting otherwise.
The audit preserves the actual resolved headers/config, without forcing NOFORK,
skipping normal initialization or asserting that fork is supported natively.
Generated headers are captured inputs from the reference build, not independently
regenerated evidence. They and the SDK stage are separately hashed snapshots.

## Reproduction and provenance

Run `python3 docs/evidence/toybox-native-link-2026-09-07/build-audit.py` after the
pinned local tools are available. It verifies retained inputs/tools/SDK and creates
a private zig-out directory. It compiles/links/inspects only, never boots the ELF.
Commands, flags, UTC boundaries, tool/object/ELF digests and program headers are in
[results.json](results.json). The upstream archive digest is
827e4cdfd69f5da973e00e2a59b30b3c9857fb7fae74c362fd0b4f96be7929b0.
The source archive, generated headers, resolved config, SDK snapshot, adapter and
review inputs are retained under inputs; build-artifacts.tar.gz preserves extracted
source, objects, map, complete disassembly and logs. Toybox's [license](LICENSE.Toybox)
and source notices remain intact. Source authenticity/security review remains open;
byte identity is not provenance authentication or distribution approval.

Host/pin/workflow checks accompany the documentation update. Runtime sources,
kernel/build defaults, standards pins, prior UL-059 bundle and siblings remain
unchanged. No QEMU run is claimed or needed for this non-runtime build audit.
Actual native mask/vector/terminal integration, CAT acceptance, consumer review
and assembled R1 remain open. Next: qualify truthful native mask initialization
against real toy_singleinit, then private stdio and terminal adaptation.

Final local checks:98 host tests plus Zig tests, all offline pins, workflow and
whitespace checks pass. Every prior runtime source hash and UL-059 bundle artifact
matches its receipt. Archived ELF,17 objects and17 upstream translation units
match recorded hashes; resolved config matches the reference build receipt.
