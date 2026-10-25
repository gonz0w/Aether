# Source-rebuilt native musl probe

Separate from the unchanged Linux reference. `build.py` verifies the existing musl
1.2.6 archive and compiler/tool pins, extracts a fresh source tree, changes native
transport entry sites, builds a private static libc, and links a probe. No package
registry/network fetch or real-prefix installation is used.

```sh
python3 experiments/native-c/build.py
```

Requires the same pinned archive under build/musl-audit and toolchain as
[the reference build](../musl-reference/README.md). Output is a new build/native-c-*
directory with logs, commands, ELF, maps, evidence and native-c.bin. All linked
startup syscall-instruction sites must be absent: C wrappers and x86_64 assembly
entries use interrupt 0x81 with a separate 0x10000 operation namespace. Musl's
internal conventions remain; unsupported operations return real errors in Aether.
The compiler's Linux-musl target is a source/build convention, not a Linux runtime
claim. This bounded adaptation is not an audit of every possible libc code path.

Select the printed envelope with Aether's `-Dsmp=false -Dnative-c-image=...` option;
run its dedicated `python3 scripts/native_smoke.py .../aether.iso`. See the
[native contract](../../../Aether/docs/NATIVE-C.md) for exact bounds and rights.
The host-static-c-v0 model remains a broader proposal; this native experiment uses
a smaller mapping quota and a different stack address, documented by the consumer.

Two private instances test argc/argv/env, initialized/BSS values, TLS, XMM values
across 64 yields each, bad FD, inaccessible pointer, unsupported call, zero-length
write, partial-output completion and exit. The kernel retains statuses and checks
mapping removal/zeroing. It does not supply allocation, shell/process/TTY or a
native package runtime. The launch's fixed initial identities and host-generated
bootstrap random bytes are developer inputs, not authenticated login or a native
entropy-service claim.

```sh
python3 experiments/native-c/build.py --fault-first
```

This builds an explicitly faulty first instance. The kernel must observe its
invalid-instruction fault, let the other instance finish, and reject overall
acceptance. Do not treat a compiler failure or emulator timeout as that semantic
negative. Aether also has output-grant, FP-restore and zeroing negative controls.

Evidence lives in each fresh build directory and the kernel's retained native
integration report. Original Linux probes, UL-021 large-TLS work and existing
consumer pins remain unchanged. This completes a bounded native startup witness;
UL-006's allocator scope and the general UL-003/015 interfaces remain follow-ons.

## Supervised service variant

`python3 experiments/native-c/build.py --supervised` builds the same pinned musl transport with a service fixture. Both instances check TLS/FP, pointer/FD rejection and partial writes. They publish readiness after output; the first generation of slot zero faults deliberately, its replacement exits successfully, and the peer yields until explicitly stopped. The worker checks it cannot invoke the supervisor factory even with the correct numeric grant value. Feed the emitted native-c.bin to sys-init scripts/build-native-supervisor.py or tests/native-supervision.py. This adds a fixed service experiment, not a general POSIX program/session.

`--io` builds the [native descriptor facade and acceptance probe](../../docs/NATIVE-DESCRIPTORS.md), including the bad-dup control. Use test_io.py with the emitted SDK directory and explicit Aether/sys-init paths. Existing startup and supervised variants remain separate.


## Strict metadata protection (UL-030)

All newly built native libc variants remove mallocng's special tolerance for
mprotect ENOSYS. The exact anchored change is recorded with before/after source
hashes in native-libc-patches.json and build evidence, together with the archive
hash and linked UL-029 reference evidence. An unexpected source anchor or altered
reference patch rejects the build. The Linux reference tree is unchanged.

The strict condition returns allocation failure when metadata protection cannot
be established. Existing reference tests distinguish EACCES/ENOSYS and successful
retry; this change does not translate every failure into ENOMEM. No injection or
test wrapper is added to the native archive.

A fresh `--io` build and all four `test_io.py` outcomes pass against an isolated
current Aether snapshot: ordinary descriptor operation, bad-dup, no-output and
skip-zero controls. [Retained evidence](../../docs/evidence/strict-native-libc-2026-09-05/summary.json)
binds build/patch/archive, producer inputs, exact commands, results and serial
logs. Kernel and sys-init working trees were read, not modified.

The descriptor fixture does not allocate and therefore does not execute this
metadata-protection branch. This is native archive patch adoption plus target
regression evidence; runtime validation of that branch still requires the agreed
native memory operations. Default startup/supervised builds and default two-core
smoke were not rerun in this scoped check; their prior reports remain historical.


## Combined memory and descriptors

`python3 experiments/native-c/build.py --io --memory` adds the userland-owned
[native-memory v1 adapter and consumer](../../docs/NATIVE-MEMORY.md). Its nine
target outcomes and four fresh ordinary descriptor regressions pass. The exact
kernel memory ABI is adopted only for this opt-in bounded profile; no shared
release or pin changes. Allocation is now target-tested in this combined fixture;
earlier statements that allocation is unavailable describe prior checkpoints.

## Checked provider failures (UL-015 / UL-081)

New native builds check failed realtime gettimeofday fallback before conversion
or success, and failed physical/available-page sysinfo before reading its result.
Both patches require exact musl1.2.6 source hashes and anchors; before/after bytes
are recorded in native-libc-patches.json. Upstream/reference and old SDKs stay
unchanged. No native clock or capacity provider is implemented.

[Qualification](../../docs/evidence/sdk-error-guards-2026-10-04/README.md) binds
three native cases: fixed archive success and old-clock/old-pages exact rejection.
Private replacement-source controls cover successful fallback/conversion and
ENOSYS/EACCES/EINTR with preserved buffers/errors and checked call counts. Those
providers are injected; real native providers, other sysconf branches, broader
overflow and thread schedules remain open. The sealed candidate is separate from
existing SDK pins and requires independent owner consumption.

Aether has now [independently consumed this candidate](../../docs/evidence/sdk-guards-disposition-2026-10-04/README.md).
Its ordered ar comparison covers1349 occurrences including duplicate basenames;
the original extraction-based comparison covered distinct names only. Three new
owner VM cases independently qualify guarded errors and old-library denials. This
closes the scoped owner handoff, while default pins, real providers, broader SDK
correctness and reader/release acceptance remain separate.
