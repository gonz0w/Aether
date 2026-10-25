# Program beside file service v1

AENPG001 / ABI 8 is a separate BSP producer profile for a requester, file-service
worker and independently executing program under one Rust broker. It retains four
channels and the existing per-worker memory/startup limits. Three worker slots
0–2 precede supervisor slot 3; old profiles retain slots 0–1 and supervisor slot 2.
Actual caller checks must use the profile's supervisor slot, never a magic task ID.

The envelope is: magic[8], three ELF lengths u32, supervisor length u32, two
reserved-zero u32, developer entropy[48], then ELF0/1/2 and supervisor bytes.
Header size is 80. Each ELF is 1–1048576 bytes; this profile permits 1–8192
supervisor code bytes, mapped immutable across at most two pages with no writable
statics. Its separate stack remains one page. Old envelope/code limits do not
change. Parse and preflight every image before admitting any user task. Entropy
supplies a separate 16-byte developer seed per worker slot, not a production
randomness API. Exact length/reserved fields are mandatory.

Supervisor entry is RDI=8, RSI=launch factory, RDX/RCX=first/second executable
grants, R8=channel factory, R9=third executable grant 0xc003. The third grant is
caller-bound like the first two; only the broker may launch it. Existing launch
operations accept slot 2 and that grant only in ABI 8. Each worker slot still
retires after three generations. User mappings, TLS/FP state, terminal observation,
stop/reclaim and channel cleanup remain local. Completion requires five reclaims,
no admitted workers and no owned/buffered channels, then `AETHER NATIVE PROGRAM PASS`.

The conformance broker extends NATIVE-COEXIST with a separately owned program
record and namespace name `program`. Operation 4 requests an empty-inheritance
program launch (ticket 0, version 1, NUL-terminated name, reserved zeros); operation
5 explicitly stops and collects its program ticket (zero name/inheritance).
Program tickets use a separate connection-local family from backend tickets;
neither is kernel authority. File operations keep their backend ticket scope.
This is not POSIX exec/wait or a production process-service selection.

The program starts with no channels, validates its own fresh TLS/BSS, writes a
bounded diagnostic byte and marks itself ready before yielding indefinitely.
The broker waits for readiness before acknowledging launch. The requester then
performs file I/O while that program remains live, explicitly stops/collects it,
and repeats with fresh program/backend generations. This deliberately tests
concurrent domain ownership and stop cleanup, not command completion or a shell.
No requested descriptor is inherited; broker-assigned file-service channels are
separate dependencies. Shared open-file state, fork/in-place exec, signals,
production timing, descriptor inheritance and SMP recovery remain outside scope.

## Reproduce and verify

```sh
python3 scripts/launch_smoke.py --program \
  --libc-build /absolute/strict-musl-sdk \
  --tools-lock /absolute/compiler-tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

The broker uses its own two-page linker map, size optimization and fat LTO; it is
5160 bytes in this capture. The third strict-musl ELF is independently compiled
from program.c. Its fresh BSS/TLS checks and denied factory/child-control/channel
calls are especially significant: native slot 2 must be an ordinary worker in
ABI 8, despite being the privileged supervisor slot in older profiles.

Six cases: positive simultaneous program/file activity across two generations;
wrong third executable (slot 2 exits 201, broker rejects at 933 before reclaim);
malformed third ELF machine; nonzero second reserved word; truncated envelope;
and omitted program stop (broker rejects the still-live record at 936 before
reclaim). Malformed inputs must reject before any worker terminal/admission
outcome. Positive completion requires both file-service exits 17, requester 29,
five reclaims and the PROGRAM PASS marker. Source, tool, input and output hashes
are retained; no timeout/unrelated panic substitutes for an expected rejection.

The program remains alive between its readiness acknowledgment and an explicit
stop after file operations. The broker rejects collecting the file backend while
that program is live, rejects backend tickets presented as program tickets and
consumes the program ticket after stop/reclaim. EOF cleanup stops an outstanding
program before cleaning the backend. Only this finite conformance workload is
claimed; graceful signals, POSIX process parenting and recovery remain separate.

## Reclaimed metadata correction

The first replacement test exposed stale image metadata: after program reclaim,
loading the file-service replacement walked that retired slot's old page records
and made already-zeroed backing read-only again. Reusing the program slot then
faulted in kernel memset. Reclaim now clears the retired page inventory/count
after root detachment, alias restoration, zero verification and admission removal.
This keeps later image loads from reinstating permissions for a dead image. The
successful second program generation exercises that precise ordering. This fix
applies to existing native profiles too, so their regressions remain required.

This profile makes room for one program beside its requester and file service.
It does not meet the proposed shell-plus-three-stage-pipeline capacity, supply
inherited descriptors or transfer the caller's file table. The next consuming
work must establish the userland owner of shared open-file/reference state and
its explicit inheritance/routing contract. Original standard and consumer pins
are unchanged; independent adoption of ABI 8 is a separate witness.
