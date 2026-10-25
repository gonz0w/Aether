# Complete ABI29 client link and initial fit — 2026-10-21

UL-007/081/082 now has a separately sealed offline parent/helper client candidate.
The existing builder explicitly selects AENFS003/ABI29 across all four runtime/
application compiles and verifies every actual linked input:45 parent components
(including32 pinned dash objects), eight helper components. Old sealed bundles
and default ABI23/24 semantics remain unchanged; no SDK promotion or native run.

Actual pinned Clang/LLD builds produce:

| Image | Bytes | Initial pages /128 | SHA256 |
| --- | --- | --- | --- |
| Parent | 252800 | 73 | b65cb3c896ce54689346fa2361a87ac4cce4889391e3078e56b78b0a13a93e50 |
| Helper | 23384 | 24 | 5727299d1a937c6fea20a781a076b54506bd2bbd49a3cd0a58faf82572ddb4d2 |

Python3.10.21 and3.14.7 rebuild identical new ELFs. ABI23 and ABI24 parent/helper
whole ELF regressions reproduce their accepted hashes. Both interpreters pass
six host admission test methods, including per-component/compile/variant failure
subcases. Four actual mixed legacy/new application/runtime links fail with the
expected unresolved startup symbol. Five mutated real sealed recipes reject
before creating an output directory: missing memory, missing application profile,
wrong helper inventory, unlisted object and legacy relabel. An actual link omitting
the memory adapter succeeds with different bytes via the stock archive, proving
why required-component rejection is necessary; that ELF is unqualified and removed.

The exact frozen Aether ELF parser/loader sources accept both images in host
Zig0.16.0 tests; all19 tests pass, including changed ELF type and excess backing
rejection. TLS/NX, no dynamic segment, no relocations and no unexpected global
imports are checked. The unchanged libc has zero LOCAL HIDDEN UND `_DYNAMIC`,
a static-link sentinel also present in accepted legacy ELFs. Initial page use
includes the16-page main stack, leaving55/104 pages before runtime allocations.
This is not peak stack/heap, runtime fit, native admission or Zsh/TTY qualification.

The first inspection incorrectly rejected that sentinel after all links passed;
its failure and bytes remain preserved. Continuing inspection initially found an
already-created empty output directory; its failed receipt is retained. Corrected
inspection used a fresh directory without repeating the passed compiler builds.
The final delivery's README-only clarification has a new seal; an actual standalone
rebuild of that seal reproduces the same current/minimum-qualified image bytes.
No guest, retry, sibling mutation, old seal rewrite or limit increase occurred.

`summary.json` records delivery/qualification identities; `attempts/` and
`retention.json` retain compact source/tool/argv/environment/stdout/stderr/exit/
cleanup evidence and all failed attempts after verified generated-output disposal.
[Review](review.md) and [client contract](../../proposals/SESSION-FS-ABI29.md)
name remaining gates. CRT/libc/dash are explicitly prebuilt pinned inputs with
preserved notices, not a new upstream source-rebuild claim. Independent technical
and reader review are pending.

Aether reports actual AF07 sys-init activation/readback/five hostile-peer witnesses
passing (receipt a63ba3ef2f25789e8ae887b59d22c31fb91a8c9a8a34cc1cf64672f21c48b7d2).
That producer result is separate from this host link work and sys-init's own
consumer acceptance. Next: AF07-backed FD/path/immutable executable translation,
matching shell1/children2–4 dispatcher and native shell/error/cleanup/fresh-boot
witness. Persistent packages, Zsh/TTY, M3/R1 and wider finite SESSION support remain
open. The delivered helper path/modes are bounded workload inputs, not a working
filesystem-loaded command.

Final quality/pin/inventory, minimum/current Python syntax, Zig formatting and
whitespace checks pass. The standalone574-member bundle seal is
`6265a3eb21f110f4888572987f4bc4420c9b2f6c932810567ecc369512a47c3b`;
the580-member outer delivery seal is
`66d8ec0f8353563a270d2f7ae2fbb9e288be2287ff08ff566e16dc4a3491a468`.
Three new work roots were compacted/read back before removing68187879 logical
bytes;364865 archive bytes remain. Physical disk reclamation was not measured.
For a fresh reproduction with the pinned archive/tools present, run
`python3 -B docs/evidence/session-abi29-link-2026-10-21/qualify.py` from repository
root. It creates an owned build root, runs host checks and never starts a guest.
The two continuation/finalization scripts are dated attempt records, not general
entry points.
