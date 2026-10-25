# Actual ABI29 boot-parent correction — 2026-10-21

UL-007/081/082 fixes a real startup bug found by the sys-init/Aether consumer
reviews. Boot owner6 stays generation0/PID7; our old decoder allowed only14/21/28
and rejected the genuine first shell PID9/PPID7. No kernel change is required.

The decoder now requires **exact boot parent7** for all three shell generations,
in addition to equality with the real PPID observation, memory grant, PID, role
and shell generation. Synthetic restarted owner14/21/28 is rejected even when
frame and observation agree. Copied child2/PID10 still requires shell parent9;
boot parent7 is rejected for that child. No native observation is fabricated.
AEFSH001 layout/startup symbol and all finite bounds remain unchanged.

The regression executes the actual old decoder with literal PID9/PPID7/memory
0x40000102 and returns42 (rejected); the corrected decoder returns0. Strict C17
host UBSan tests cover three genuine shells,135 copied-child identity combinations,
forged/mismatched/restarted owners, malformed frames and unchanged failed output.
All eleven compiling semantic omissions are detected, including restored old
owner logic and removed boot-parent equality. These are host observations, not
new native PID measurements or process authority witnesses.

Python3.14.7 and3.10.21 rebuild identical corrected complete parent/helper ELFs:

| Image | Bytes | Initial backing /128 | SHA256 |
| --- | --- | --- | --- |
| Parent | 252784 | 73 | 6357c4e7a63db73263d0191d9db364e39e2e7a6935e4f490df9ef2e9d62d0d39 |
| Helper | 23400 | 24 | 2dfcab81ae65f70c494cc42d338dcf18be4b57f8a822f3f36902d513d1456ae4 |

Eight actual before/after legacy ABI23/24 runtime/application object pairs match.
Prior whole-ELF legacy evidence retains its original scope; those full legacy
links were not repeated. Frozen Aether kernel parser/layout and all19 host Zig
tests pass for the new ELFs, including wrong ELF type and excess backing. Initial
pages include the16-page main stack; peak stack/heap/runtime fit remains untested.
Pinned prebuilt CRT/libc/dash, full45/8 link inventories, tools and notices are
unchanged. Only the bundle's identity header and explanatory README change.

`summary.json` names the separately sealed **v2 linked delivery**. Old v1, its
source/object predecessor and all immutable receipts remain retained, but their
supervisor-parent check is incompatible with this boot profile. Select v2 for the
next matching consumer. No new SDK/released pin, native campaign, sibling mutation,
message, generation reset, quota change or independent sign-off occurs here.

[Review](review.md), raw commands/logs/source/tool/header pins and cleanup are
retained in the attempt archives and retention record. A fresh current-interpreter
qualification is `python3 -B docs/evidence/session-abi29-boot-parent-2026-10-21/qualify.py`;
run minimum.py on its returned owned work root with the provisioned actual minimum
interpreter. Each compiler/link/test has its own bounded owned process; no outer
watchdog is placed around another independently owned compiler session.

This correction clears the identified local boot-parent input defect. Matching
sys-init shell dispatcher and native startup/command/error/cleanup witnesses,
AF07-backed FD/path/immutable executable translation, persistent packages,
Zsh/TTY, independent reviews and full M3/R1 remain open.

Final header-pinned host UBSan, ELF import/sentinel/relocation inspection,
minimum/current syntax, quality/pins/inventory and whitespace checks pass.
The v2 outer seal is
`e559c2ef5a0675c6c243aa3cc517bf5c34fd78ae5ef90a8ca3f3e99b04999081`;
the standalone bundle seal is
`70f87686d4d7ef7f23f6f53fd6ca1632e524eeefd75345321e0806c4cbe43942`.
Both old and new delivery bytes reverify. Two exact new work roots were archived
and fully read back before removing56151055 logical bytes;525753 compact archive
bytes remain. Physical reclamation was not measured. No historical cleanup.
