# Native conflict-guard layout findings

2026-09-06; decision 0088, BG-058. Build research only.

The bounded 80-link study found no complete variant inside the existing 4096-byte
image bound. Revision 7 with all three functions always inlined is best: conflict
4256 bytes, resources 4528 bytes, maximum across all five cases 4528 bytes. These
are mapped extents, not executable images accepted above the limit. Compared with
0087's separate minima, conflict saves 208 bytes and resources saves 96 bytes;
these new minima now belong to the same source variant.

## Method and complete results

Retained revisions 5 and 7 from decision 0087 were copied into private build trees.
Only inline attributes for Pending::begin, Pending::conflict_synthetic and
Held::offer_synthetic vary. Names encode revision and always/never in that order.
All eight combinations per revision use the unchanged Rust 1.98.0, opt-level=s,
static target, prefix mapping and strict linker script. No instruction or
assertion was removed by source editing. Compiler optimization still determines
which paths survive in each case. Sources and tool hashes were checked before
and after. Live consumer sources remain identical to the accepted 0086 snapshot.

| Variant | Conflict | Resources | Skip close | Forget reader | Replace primary |
| --- | ---: | ---: | ---: | ---: | ---: |
| r5-aaa | 4480 | 4544 | 4496 | 3736 | 4512 |
| r5-aan | 4704 | 4672 | 4704 | 4736 | 4768 |
| r5-ana | 4784 | 4800 | 4768 | 4816 | 4832 |
| r5-ann | 4800 | 4816 | 4784 | 4864 | 4864 |
| r5-naa | 4768 | 4912 | 4784 | 4928 | 4800 |
| r5-nan | 4816 | 4800 | 4816 | 4848 | 4880 |
| r5-nna | 4800 | 4848 | 4784 | 4864 | 4832 |
| r5-nnn | 4816 | 4864 | 4800 | 4912 | 4880 |
| r7-aaa | 4256 | 4528 | 4272 | 3784 | 4320 |
| r7-aan | 4480 | 4752 | 4480 | 4784 | 4544 |
| r7-ana | 4640 | 4880 | 4624 | 4896 | 4688 |
| r7-ann | 4656 | 4896 | 4640 | 4944 | 4720 |
| r7-naa | 4640 | 4944 | 4656 | 5024 | 4656 |
| r7-nan | 4640 | 4864 | 4640 | 4912 | 4704 |
| r7-nna | 4672 | 4896 | 4640 | 4912 | 4704 |
| r7-nnn | 4688 | 4912 | 4656 | 4960 | 4752 |

78 links fail the size assertion. Only two forget-reader controls link (3736 and
3784 bytes); those builds can terminate earlier at an assertion and do not prove
that the complete guard fits. Neither was executed. No new native success,
omission outcome, lifetime, construction-denial or reoffer qualification is
claimed. This exhausts the specified inline matrix, not every possible layout.

[Study, source snapshots, commands, maps and results](../evidence/conflict-guard-layout-2026-09-06/README.md)
retain all 80 attempts. Earlier source reasoning and proposed native oracles remain
in [decision 0087](../decisions/0087-native-conflict-guard.md).

## Why the existing 8 KiB profile cannot substitute

Captured Aether sources describe AENPG001 / ABI 8 as a separate three-worker
program/file-service experiment. Its 80-byte envelope includes three ELF lengths
and 48 entropy bytes, while AENIN001 uses two workers, a 56-byte header and
32 entropy bytes. The parser permits 8192 bytes only for the program/connections
profiles and still caps the init envelope at 4096. See retained
[native_launch.zig](../evidence/conflict-guard-layout-2026-09-06/research-inputs/Aether/kernel/native_launch.zig)
and [NATIVE-PROGRAM.md](../evidence/conflict-guard-layout-2026-09-06/research-inputs/Aether/docs/NATIVE-PROGRAM.md).

More decisively, native_c.zig sets init_profile for the init/console profiles,
not the program profile. Its syscall dispatcher admits 0x25000–0x25005 only when
init_profile is true. ABI 8 places executable grant 0xc003 in R9 instead of the
init grant 0xe001, moves the supervisor from slot 2 to 3, and expects five reclaims
and a PROGRAM PASS marker instead of three reclaims and INIT PASS. Our adapter
checks the ABI-6 tuple and uses 0xe001 for clock, observation and wait operations.
See retained [native_c.zig](../evidence/conflict-guard-layout-2026-09-06/research-inputs/Aether/kernel/arch/x86_64/native_c.zig)
(profile selection, dispatcher and startSupervised) and
[adapter.rs](../evidence/conflict-guard-layout-2026-09-06/research-inputs/sys-init/prototypes/native-supervisor/adapter.rs).
The existing page-mapping loop is not an init-compatible profile contract.

These are hashed mutable-checkout research snapshots, not a new accepted producer
pin or witness. No source or release in a sibling repository was changed.

## Disposition and follow-ons

Keep the current 151-case runtime checkpoint. Stop this inline search and seek a
producer decision on the [init image capacity request](NATIVE-INIT-IMAGE-CAPACITY-REQUEST.md).
BG-058 tracks that dependency, consumer adoption and fresh execution of all
existing and proposed cases. If a larger separate fixture is declined, a deeper
layout redesign needs a new bounded plan and all original guard obligations.
Denied construction, closed reoffer, physical diagnostic capacity, PH-05/06
sealing and BG-057 PH-07 retirement remain open. The current evidence establishes
a fixture/profile compatibility blocker; it does not establish a missing kernel
lifecycle operation or production memory budget.
