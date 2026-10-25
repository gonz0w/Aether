# Private ABI29 shell client candidate — UL-007/081/082

2026-10-21. Implemented source/object candidate, pending matching sys-init
dispatcher, complete component/CRT/link intake, resource review and native tests.
This does not select a new SDK pin, admit a boot image or change Aether's ABI.

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
old/new runtime/application pairing. The existing sealed builder/component
validator still rejects ABI29: these objects are not a promoted SDK bundle.

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
generation; PPID must equal the supplied supervisor PID14,21 or28 (owner6,
generation1–3). A copied child's supplied/native PPID must equal
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
filesystem activation owner still expects AF06 and cannot consume AF07 by merely
changing a label. Its AF07 readiness/shutdown update is separate from this client.

Userland still needs full CRT/libc/application/helper component selection and
ELF/resource-fit evidence, AF07-backed file-descriptor/path translation and one
selected shell workload. Existing startup directory0x76030000+generation and
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

[Host/object evidence](../evidence/session-abi29-candidate-2026-10-21/README.md)
separates tested arithmetic/framing from unrun transport and native enforcement.
