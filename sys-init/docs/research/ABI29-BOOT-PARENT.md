# ABI29 boot-parent compatibility — 2026-10-21 / BG-067

Update2026-10-21: [Decision0194](../decisions/0194-abi29-dispatch-core.md) consumes
separately sealed corrected v2 linked input and prepares matching startup/child-
wait core with actual Rust/C decoder interoperability. Boot parent7 is accepted;
the original incompatibility below is historical. No native shell or AF07 FD/path/
exec acceptance follows; full dispatcher/transport integration remains pending.


The new29-member userland client candidate closes the old six-domain arithmetic
assumption for its proposed shell1/children2–4 identities. Its proposed startup
contract still cannot pair with the current boot supervisor. Do not implement the
wrong parent identity or adjust a role/PID label to pass validation.

Aether's current native_c.zig initializes every State generation to0. Boot maps
and admits owner slot6 without advancing that generation; the seven-domain
getpid/getppid expressions yield `0*7+6+1 = 7` for the supervisor. This review does not claim a new native getppid measurement.
The first slot1 process has generation1, PID9 and memory label0x40000102.

The sealed candidate fs-identity.h requires a shell's actual PPID to equal the
supplied parent field and permits parent14/21/28 only. A host program executing
that exact decoder with strict C17/UBSan confirms:

| Frame parent | Native-observation input PPID | Decoder result |
| --- | --- | --- |
| 7 | 7 | Reject; output unchanged |
| 14 | 7 | Reject; output unchanged |
| 14 | 14 | Accept synthetic identity |

The last row proves that the fixture/header executes successfully; it does not
justify fabricating a native observation. The first two establish the current
boot-parent mismatch in the host parser. Source arithmetic, host decoder behavior
and native authority remain separate evidence layers. Exact sealed header, C
control, source/tool hashes, commands and outputs are retained in the
[consumer packet](../evidence/filesystem-af07-consumer-2026-10-21/README.md).

## Required input (local handoff, unsent)

Userland must supply a separately sealed corrected startup/client input for the
actual generation0 boot owner, with exact native PID/PPID/memory and parent-only
validation preserved. Coordinate the intended owner lifetime domain explicitly;
shell generation is not the boot supervisor generation. Do not edit the old seal,
weaken observation equality, reset lifetimes or promote numeric IDs to authority.
If Aether intends another parent model, its owner must supply that changed
contract and native witness rather than sys-init guessing an implementation.

The initial29-member object candidate also lacks a complete ABI29 CRT/libc/
application/helper component receipt, linked ELF/stack fit, AF07 FD/path/exec and
persistent loader/runner/package inputs. Its components.py admits ABI23/24 only.
After corrected identity and usable matched client inputs, sys-init can implement
the slot1/children2–4 dispatcher/startup/descriptor/copy/exec/wait adaptation and
qualify it with fresh Aether command/settlement witnesses. No partial RAM-only
shell or speculative dispatcher framework is introduced to conceal these gates.
Old serial/AF06/AF07 deliveries and released standards pins remain unchanged.
