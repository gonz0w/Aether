# Private ABI29 shell client candidate — UL-007/081/082

2026-10-21. Implemented linked client candidate with explicit CRT/libc/component
selection and host kernel parser/initial backing fit. Matching sys-init
dispatcher, filesystem translation, runtime resource review and native tests remain.
This does not select a new SDK pin, admit a boot image or change Aether's ABI.

Select the separately sealed [v2 boot-parent correction](../evidence/session-abi29-boot-parent-2026-10-21/README.md).
The original object and v1 linked candidates reject the actual generation0 boot
owner and remain historical inputs, not usable startup candidates for this profile.

Aether's current AENFS003/ABI29 mechanism has engine0, processes1–5 and owner6.
The candidate selects shell1 and copied children2–4; slot5 remains unused. This
keeps three child records instead of expanding concurrency. Native generation
and grant checks remain authoritative. Existing epoch1–15, shell generation1–3,
finite SESSION lifetime, pipe generation1–9, descriptor16, binding/transfer,
argv/environment, memory and cleanup bounds remain unchanged. Decoding a number
does not reserve a lifetime or permit reuse/reset after exhaustion.

## Startup boundary

Compile runtime and application with `SESSION_FS_ABI29`, `SESSION_SERIAL` and
`SESSION_CHANNEL_WAIT`. This candidate deliberately requires channel waiting;
it supplies no polling fallback. `aether_fs29_session_start_v1` prevents a silent
old/new runtime/application pairing. The maintained sealed builder/component
validator now explicitly selects ABI29 across all four compiles and verifies all45
parent/eight helper link inputs. Older sealed builders remain unchanged. This is
an experimental input, not a promoted SDK or an accepted native shell.

On the already delegated private process channel, the owner sends exactly32
bytes before the existing64-byte installed-FD table and binding records. Integers
are little-endian u32. This **proposed client greeting** requires a new matched
dispatcher; it is not Aether's filesystem AF07 greeting or a kernel operation.

| Offset | Value |
| --- | --- |
| 0 | Eight literal bytes `AEFSH001` |
| 8 | 29 |
| 12 | 7 domains |
| 16 | Actual process slot: shell1 or child2–4 |
| 20 | Actual nonzero epoch1–15 |
| 24 | Actual native parent PID |
| 28 | Shell generation1–3 |

Require memory auxv0xa000 to equal `0x40000000 | epoch<<8 | (slot+1)` and
native PID to equal `epoch*7+slot+1`. A shell's epoch must equal its shell
generation; supplied and observed PPID must both equal7, the existing generation0
boot owner6. Shell generations do not advance that owner; synthetic restarted
owner14/21/28 is rejected even if frame and observation agree. A copied child's supplied/native PPID must equal
`shell_generation*7+2`. Native observations must agree before client identity
is installed. Errors publish no decoded output. Endpoints still come from the
actual auxv/copy return, with existing channel/native checks; no numeric ID is
converted into authority. Copy rebind/TLS repair remains the existing pinned
implementation and requires new native qualification in this composition.

Parent-only pipe/wait/exec paths and application entry now use actual slot1.
Wait replies accept only positive seven-domain PIDs for child2–4/epochs1–15;
specific PID matching, errors, reserved bytes, status publication and protocol
poisoning retain their existing behavior. Actual child membership, terminal
status and reply reservation remain dispatcher responsibilities. A syntactically
valid PID alone is insufficient evidence that a child exists or was collected.

## Matching work still required

Sys-init must supply its separately reviewed slot1 parent/2–4 child dispatcher,
startup/directory/descriptor/copy/exec/wait/endpoint adaptation and exact native
holder/lifetime oracles. Preserve old ABI24 and AF06 artifacts. The current
filesystem activation owner now has a separate AF07 candidate with Aether-reported
native witnesses. Its own consumer review and shell dispatcher integration remain
separate from this client; the old AF06 artifact is not relabeled.

Userland now supplies [full CRT/libc/application/helper link inputs](../evidence/session-abi29-link-2026-10-21/README.md).
Static initial backing is73/128 parent and24/128 helper pages including the main
stack; peak runtime stack/heap fit remains untested. AF07-backed file-descriptor/
path translation and an executed shell workload remain required. Existing startup
directory0x76030000+generation and
private FD/exec messages require actual matched owner implementation; they are
not native filesystem handles. `SESSION_SCRATCH`, if separately compiled, is
the old RAM fixture and cannot satisfy persistent-file acceptance. No new POSIX
credentials, TTY semantics or filesystem-loaded executable are implemented here.

For persistent execution, bind authorized lookup/read and immutable selected
bytes through Aether loader admission, enforce loader/stack/mapping limits and
preserve failed-exec identity/FD state. The required witness is a real external
command with exact streams/status and parent state, known child settlement,
clean filesystem disconnect/export, native reclaim/halt and fresh-boot readback.
Denied/stale/failed/unknown outcomes must never admit or replay effects.
Pkg-mgr owns actual persistent package bytes/records; Zsh/TTY remain open.

[Original host/object evidence](../evidence/session-abi29-candidate-2026-10-21/README.md)
and [complete link evidence](../evidence/session-abi29-link-2026-10-21/README.md)
separate arithmetic/framing, linking and initial fit from unrun native enforcement.
