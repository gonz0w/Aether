# Bounded executable launch v1

The ordinary one-app namespace extension is specified
[below](#ordinary-one-app-namespace-launch). The original v1 contract follows.

Kernel-owned experimental profile. This first slice supports two immutable,
boot-supplied ELF images, selected through caller-bound executable grants, with
copied arguments/environment and retained child outcomes. It does not implement
POSIX fork/exec/wait, filesystem paths, descriptor inheritance, pipes or a shell.
Userland owns those adapters and sys-init retains supervision policy. No companion
acceptance or shared-standard revision is implied.

## Bootstrap and invocation

Select the existing explicit native boot-module option with `-Dsmp=false`.
New envelope `AENEX001`: little-endian magic[8], image0 length u32, image1 length
u32, supervisor length u32, reserved zero u32, developer entropy[32], then both
ELFs and the raw supervisor. Each ELF is 1–1048576 bytes; supervisor 1–4096.
Lengths must match exactly. Both ELFs are parsed before user entry and checked
against the actual native address/stack/table limits. Malformed boot inputs reject
before any child admission. Existing envelopes and their ABIs are unchanged.

The supervisor starts with RDI=3, RSI=factory grant 0xa001, RDX=image grant 0xc001,
RCX=image grant 0xc002. Grants are bindings in that domain, not transferable values:
workers cannot acquire launch authority by guessing them. The old fixed-image
launch operation returns ENOSYS in this profile.

`int 0x81`, RAX=0x23000: RDI=factory, RSI=executable grant, RDX=slot (0 or 1),
R10=pointer to a 272-byte startup record; R8/R9 reserved zero. Signed RAX returns
fresh instance handle or negative errno. Other registers follow the existing
native trap clobber convention. Record fields: argc u64 (1–4), envc u64 (0–4),
then eight 32-byte strings: argv in slots 0–3, environment in slots 4–7. Active
strings must contain NUL; unused bytes/slots are ignored. Strings are copied into
the child stack, never referenced across domains. Environment entries are opaque;
they grant no authority. Empty strings are permitted, including argv[0].

Validation order: caller and factory/executable binding (EACCES), slot/reserved
fields (EINVAL), occupied slot (EBUSY), generation exhaustion (ENOSPC), complete
readable record (EFAULT), record counts/termination (EINVAL). Failed requests
leave the slot, generation and other workers unchanged. Preparation copies and
validates all input before commit; prevalidated fixed resources make commit
infallible. This is BSP interrupt-gate execution with interrupts disabled, not
an SMP or asynchronous cancellation transaction.

## Lifetime and limits

Normal child exit values are narrowed to their low eight bits before retention
and observation, so arbitrary register values cannot overflow detail+1. Fault
and controlled-stop details retain their existing meanings.

Reuse 0x20001 observe, 0x20002 reclaim, 0x20003 output, worker readiness/generation
and 0x20007 stop from native supervision v1. Only the owning supervisor controls
children. Observation is retained and repeatable; reclaim requires terminal state
and invalidates its handle. This is not parent wait/reap semantics. Each slot has
three generations without wrapping. Two slots, 128 backing pages each, 32 leaf
tables, fixed 16-page stack, initial TLS at most 4 KiB. Native-memory remains a
separate option. No descriptors or executable grants are implicitly inherited.
Workers retain the existing bounded legacy output transport for this fixture.

The conformance completion operation accepts 100 after three reclaims and no
admitted children, emitting `AETHER NATIVE LAUNCH PASS`. This marker describes the
bounded fixture only. Tests must select both different images, verify copied
arguments/environment and exact child results, check denied authority/malformed
requests without consuming generations, exercise replacement/stale handles and
reject incorrect image/result expectations. Kernel source changes also require
existing memory, consumer and default-SMP regressions.

## Reproduce

Use an explicit retained strict-musl build and its pinned compiler/linker lock:

```sh
python3 scripts/launch_smoke.py \
  --libc-build /absolute/Aether-userland/build/native-c-BUILD \
  --tools-lock /absolute/Aether-userland/experiments/musl-reference/tools.lock.json
zig build test
zig build smoke
```

The runner verifies libc receipt and compiler/linker digests, builds two C helpers
and a Rust conformance client, and writes fresh `zig-out/launch-suite-*` artifacts,
linker maps, command logs, source hashes, image hashes and serial outcomes. It uses
installed inputs without fetching or changing companion files. The client image
is a static link with resolved GOT bytes mapped inside its immutable code page;
it has no writable statics. This is a test adapter using the bounded legacy output
sink, not a replacement for userland's descriptor implementation.

Each build has a 180-second timeout; QEMU has a separate 30-second watchdog.
`--help` and `--version` return 0; invalid arguments return 64; operational failures
return 1 with incomplete evidence retained. Successful completion returns 0.
Integrity checks establish byte identity, not authenticity or publication clearance.

Five cases: positive selection/copy/lifetime; wrong-image substitution requiring
helper exit 92 then supervisor result 411 before reclaim; malformed second ELF;
nonzero envelope reserved field; syntactically valid ELF outside the loader's low
address range. Only the designated panic satisfies each negative. The layout
control preserves ELF file/address page congruence so it reaches the actual loader
boundary rather than failing earlier generic ELF validation.

Positive checks include empty authority, invalid image grant/slot/pointer,
cross-page inaccessible record, bad count/unterminated argument, occupied/live
reclaim denial, disabled legacy launch, copied strings despite parent mutation,
worker denial of guessed launch/reclaim authority, repeatable terminal records,
arbitrary exit-register narrowing, output from distinct images, stale handles,
and a different-image replacement which deliberately faults and is reclaimed.
Host checks cover record counts/termination, envelope bounds/reserved fields,
stack/arena exclusion and independent leaf-table exhaustion.

Next integration requires owner agreement on how a user-space process service
uses launch authority, child ownership/reaping, failed exec semantics and inherited
I/O. This profile does not assign those policies or make dash runnable. File lookup,
RAM-backed file service, pipes and durable installation remain later slices.

[Retained results](evidence/native-launch-2026-09-05/README.md): all five launch
cases, eleven existing memory cases, twelve frozen userland consumer cases, kernel
host tests, 44 Python tests, standards and default two-core/framebuffer checks pass.
Companion tests consume their existing profile; new launch-ABI adoption remains open.

## Ordinary one-app namespace launch

The [issue99](https://github.com/gonz0w/Aether/issues/99) extension implements the
owner-approved [contract](policy/execution.md#ordinary-app-namespace-and-clock-contract-2026-10-28)
in the ordinary combined ABI31 init/guarded-owner-stack closure. The larger
application and storage-lifetime profiles do not select it; other profiles return
ENOSYS. Sys-init supplies the trusted engine/process relationships and userland
consumes the startup record under [issue100](https://github.com/gonz0w/Aether/issues/100).
Kernel source alone does not establish whole-app fit or native acceptance.

`int 0x81`, RAX0x2300a: RDI factory0xa001; RSI retained image0xc001,0xc002 or0xc003;
RDX app slot1..5; R10 readable320-byte record; R8 process reader; R9 process writer.
All record words are little-endian:

| Offset | Bytes | Value |
| --- | --- | --- |
| 0 | 8 | `AENAP001` |
| 8 | 8 | 320 |
| 16 | 272 | Unchanged argc/envc/eight-string argument record |
| 288 | 8 | Exact current engine instance handle |
| 296 | 8 | Namespace response reader |
| 304 | 8 | Namespace request writer |
| 312 | 8 | Zero |

The engine must be admitted, nonterminal slot0 with its exact retained handle.
Namespace endpoints occupy distinct service channels10..11 and are currently
held by this supervisor. Their counterparts must be the actual engine-held
`channel_reply_cap` writer and `channel_cap` reader, with current directions and
generations. Process reader/writer occupy two distinct channels0..9, are open
and empty, and both counterpart ends remain held by this supervisor. All four
channels are distinct. Numeric labels alone do not prove ownership.

The namespace response must never have transferred a positive read and the request
must never have transferred a positive write in this channel generation. History
survives transfer, drain and close; only fresh-generation creation clears it.
Zero-byte calls, EAGAIN, EOF and errors do not set history. An engine greeting may
already be queued; transfer preserves every queued byte and its position. Epoch
is the complete actual engine request-reader capability, derived by the kernel.

New-operation error precedence: disabled profile(-38); caller/factory/image
authority(-13); destination role/range(-22); occupied(-16); lifetime exhausted
(-28); full record snapshot/pointer(-14); format/arguments(-22); live engine and
four-endpoint authority/history(-13); binding lifetime(-28); image/backing/leaf
preflight(-12). Recoverable failures precede reset, generation advance, transfer
or alias mutation. The fixed-pool commit runs under the BSP IF=0 interrupt gate;
no scheduling intervenes before all transfers, binding and startup publication.
Post-preflight invariant assertion failure is a kernel defect.

Auxv0xa003 points to64 checked stack bytes at0x0800e200 (data+512), immediately
after the256-byte argument bank and separate from entropy at data+128:

| Offset | Bytes | Value |
| --- | --- | --- |
| 0 | 8 | `AENAP001` |
| 8 | 8 | 64 |
| 16 | 8 | Read-only app-lifetime clock capability kind0x36 |
| 24 | 8 | Namespace response reader |
| 32 | 8 | Namespace request writer |
| 40 | 8 | Full engine request-reader capability (epoch) |
| 48 | 8 | `/home/` followed by two NUL bytes |
| 56 | 8 | Zero |

Auxv0xa000..0xa002 keep their meanings. Maximum argc4/envc4 uses45 words
(360 bytes) from SP0x0800c000. Limits stay1MiB ELF,128 image-plus-stack pages,
128 backing pages,4096TLS,64KiB mapped stack and initial SP48KiB. Engine, owner,
channel and backing-reservation limits stay fixed. Binding storage is32 scalar
bytes per local State; channel history adds two booleans. No sustained profile,
global capability/task table or ambient clock is selected.

Bound apps return ENOTSUP(-95) for self-freeze0x23003, copy0x23006, exec0x23007
and exec publication0x23009 before effects. Read-only receipt0x23008 remains
available; unbound operations retain prior behavior. Terminal/fault/forced stop,
reclaim, reset and init close clear the entire binding. Clock queries enforce
liveness and exact nonreused lifetime; see
[NATIVE-CLOCKS](NATIVE-CLOCKS.md#ordinary-app-read-only-monotonic-grant).

Focused host entries, selected through the lead's bounded runner:

```sh
zig test kernel/native_app.zig
PYTHONPATH=tests python3 -B -m unittest test_native_app -v
```

The pure Zig root is registered in hosted CI. Actual-body host qualification uses
the separately reviewed private local adapter; the direct Python entry is not a
new hosted CI gate. Its maintained capture-helper execution boundary remains a
separate gap and does not replace the qualified local runner.

The latter uses shared production admission and extracted actual launch, stack,
channel-progress, clock and lifecycle bodies in Debug/ReleaseSafe. Denials compare
full destination/engine/channel snapshots; compiling counterpart/history/revocation/
profile/dispatch omissions must fail behavioral assertions. The actual profile
selector is exercised with old/larger/lifetime denials. New-op dispatch clauses
execute with a fallback sentinel. MMU load, alias flush, device reads, scheduler
returns and notification/trace effects have explicit host substitutes; State uses
fixed host backing. Reset uses its scalar prefix and init close its detach loop.
Bound copy/exec tests execute actual pre-effect prefixes; existing full-body tests
retain unbound success/rollback coverage.
Actual results, offline builds and separate review belong in issue99; these host
checks do not execute a guest or establish hardware enforcement.
