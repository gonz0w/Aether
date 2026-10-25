# Private native entropy grant

## Selected OpenZFS binding scope — 2026-10-05

Requirement before code: remove selected libzpool's ambient random-device opens
and non-progressing read loop. Bind its actual random_init/fini/get-bytes functions
to existing auxv0xa002 draw/close operations. Keep the calibrated elapsed port in
the same derivative. This is Aether's private engine port; userland owns maintained
SDK policy and Rust owns future filesystem integration. No public getentropy API,
device namespace, grant/ABI/quota increase or sibling/pin changes.

Initialization obtains the explicit grant and verifies an actual eight-byte draw,
then clears that temporary stack buffer through volatile stores. Draws use bounded
chunks with exact counts. Zero/short/negative/unexpected completions, absent/stale/
closed authority, range overflow and exhaustion must terminate125; never return
successful random bytes after an error. Zero-length requests have no draw effect
while initialized. Invalid later chunks may leave an already completed prefix;
the owner terminates and cannot consume it. This is not a transactional fill or
entropy-quality/reseed certification. No bytes/selectors are logged.

The state is one grant owned by this isolated engine domain, published before
worker creation and closed only after every engine caller quiesces. Concurrent
draws share the kernel-enforced4096-byte lifetime quota; init/fini must not race
with them. Fini closes permanently and clears the local reference, with repeated
fini a no-op. Reinit cannot reopen a closed bootstrap grant; fresh domains receive
new generation grants. Buffer spans stay live/writable through each synchronous
copied draw, and the x86_64 native trap ABI remains unchanged. Keep CDDL notices.

Simplicity questions: opening scoped device descriptors would require an unrelated
FD/device service binding; direct existing capability operations satisfy this
current engine need. The small checked adapter is sufficient and removes both
ambient opens and the EOF retry loop, without a provider framework or new service.
Preserve exported path labels for upstream source compatibility; they confer no
authority or native path support.

Tests selected: actual82/two-worker musl/elapsed composition plus shared entropy
draws, exact quota drain/rejection, permanent close, replacement and stop; native
absent/future/closed and omitted-quota controls; controlled actual C chunk/error/
overflow/zero-length/lifecycle cases; byte-identical baseline/original objects and
selected engine link with no test probes; unchanged elapsed regressions; full host,
pins/workflow, format and simplicity hashes. Freeze sources for qualified runs.
Dispose generated builds on success/failure with compact commands/hashes/logs,
never new archives. Document outcomes in STATE/ROADMAP and this reference.

[Compact result](evidence/openzfs-entropy-2026-10-05.json) records14 final native
cases, ten fresh elapsed-only regressions and175 host tests. Actual82/two-worker
draws, exact shared quota drain, permanent close and stop/replacement pass; missing,
future and closed grants terminate125, and the skipped-quota mutation rejects395.
Twenty-one controlled actual-C scenarios cover chunks, no-progress/errors,
overflow, zero length, init/fini and closed reinit. Native commands retain explicit
QEMU backend metadata. All6458 input hashes and105 frozen sources remain unchanged;
workflow/pins, Experience, simplicity and format pass. No failed target/test attempt
was waived; an intermediate14-case pass is retained separately.

Baseline/original objects rebuild byte-identically. Exactly two selected objects
change, with elapsed transforms retained and no test observer in the full engine.
The selected ELF links against the existing guarded SDK and is not entered. Final
port/regression runs dispose530/479 generated files (about181/139MB logical), with
compact results/short logs and no archives. These caller tests do not establish
production entropy demand or full engine heap/ARC/helper/startup. Required scoped
providers/resources, longer waits and UTC remain before filesystem/R1 acceptance.

The explicit `-Dnative-entropy=true` memory/thread fixture grants each loaded worker
auxv0xa002. AENATC01/AENSUP01 only; no SMP, copy/exec/launch composition. The kernel
binds a selector to its authoritative domain slot/generation. Threads share the
domain grant,4096-byte lifetime quota and permanent close. No move/reopen or ambient
entropy syscall exists. Disabled route returns-38; public SDK/getentropy remains
unchanged. This is an experimental producer contract, not companion adoption.

Private int0x81 draw0x2b000: RDI grant, RSI writable output, RDX1–256, R10/R8/R9 zero.
Success returns exact count. Close0x2b001: RDI grant, remaining fields zero; returns0
and permanently closes. Rejection order: unbound/foreign/stale-13, closed-9,
fields/count-22, full writable span/overflow-14, byte quota-28. Failed preflight
preserves quota and caller bytes. No user pointer becomes a DMA descriptor.

The BSP keeps IF clear through validation, synchronous transport, copied result
and stack-copy clearing. User unmap, teardown and replacement cannot overlap it.
Hardware timeout/malformed completion panics with reserved backing; no partial
success, fallback bytes or recovery/reuse claim. Termination invalidates the grant;
fresh explicit-profile admissions receive a new generation selector. Polling
latency under concurrent services, entropy health/reseed, physical hardware/IOMMU,
restart policy and independent consumer review remain open.

Current selected caller reproduction, after pinned offline setup:

```sh
python3 scripts/service_libc_clock_smoke.py --openzfs-entropy --libc-build .deps/native-current/sdk --tools-lock .deps/native-current/sdk/tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

The runner verifies current input hashes, composes actual upstream callers with
musl and existing grants, and retains compact results. QEMU uses an explicit
host `/dev/urandom` backend for its legacy virtio-rng device, with exact command
metadata in each case. No generated source/binary/image archive is retained.
Historical setup/archive recipes are retired under the maintainer's retention
decision; their original results remain historical evidence, not current replay
instructions. Changed kernel/transport behavior still requires the hardware entropy
and affected M4 regressions; this port changes neither.
Each build180seconds, VM30seconds, teardown3seconds; forced teardown fails.
New negative quota control is excluded from release-designated artifacts.
No API names, entropy quality certification or public release follows from these
bounded tests. See STATE for qualified evidence and remaining work.
