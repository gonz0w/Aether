# Bounded executable launch v1

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
