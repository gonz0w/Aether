# Exec replacement with continuing pipe I/O — 2026-09-23

The private capacity dispatcher retains one active replacement while polling parent
waits and servicing the copied writer or already-ready replacements. The next
replacement receives the state only after the previous child reaches Done. Until
then its channel belongs exclusively to exec/report handling. Pending children's
bytes never enter the pipe request decoder. Handle, generation and channel bindings,
CLOEXEC filtering, native publication and readiness checks remain unchanged.

The positive witness holds the relay's denied-exec reply after exactly seven bytes,
checks that no pipe write has yet occurred, and releases it only after the copied
writer makes its first successful pipe write. It then completes both replacements,
all streams, eight parent wait probes and fifteen reclaims over three generations.
The deliberate starvation variant suppresses I/O during that hold and must return
exact2760 with zero reclaims after32 held rounds. A timeout or arbitrary panic cannot
satisfy this oracle. The public shell, SDK and kernel ABI are unchanged.

## Failure and correction

Attempt1 completed the existing66 cases, then the new overlap positive faulted:
vector14, RIP40341f, error6, followed by native supervisor terminated. The starvation
case was not run. This is a product failure, not an expected negative or timeout.
Two retained replacement states plus dispatcher locals exceeded the one-page stack.
The exact linked start/poll/commit frames consume at least4136 bytes before deeper
calls versus4088 usable. The disassembly identifies the fault in commit's stack-local store.
The failed raw binary, disassembly, frozen inputs, serial log and complete generated
suite outputs are retained in the attempt1 packet.

One active replacement is sufficient for exec/I/O overlap. Reusing that state after
Done removes unnecessary simultaneous state without increasing stack, backing,
participant, channel or code limits. Each child keeps its own authenticated route;
only completion transfers its channel to I/O. Non-overlap variants keep their prior
sequential driver, including existing confirmed-stop cancellation controls.

The final ELF's extracted text matches the qualified positive raw bytes exactly.
The reviewed start/poll/commit/descriptor-prepare/memcpy-or-memset chain uses3920
bytes including return addresses, leaving168 usable bytes. This is a scoped linked
binary audit, not a general compiler-independent stack bound or whole-system proof.
Future caller, compiler, buffer or participant changes require renewed stack review.
The complete raw, ELF and disassembly plus command receipts are retained.

## Reproduction and scope

```sh
python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

Both native attempts bind281 runtime inputs. The prior81 ELF/raw images remain
byte-identical; two new private owner variants are16936 and17000 bytes. The overall
largest owner remains17016 within the existing24576-byte ceiling. No shared pipe
core, client, sibling, dependency, released pin or kernel source changes.

The preimplementation review and correction are recorded in NATIVE-SHELL-STARTUP.
finalize.py verifies source snapshots, archives all attempt outputs and verifies
archived/live bytes before removing only those generated duplicate directories.
SHA256SUMS seals all packet files; earlier evidence remains immutable.

This establishes the bounded happy-path overlap and its starvation control. It does
not qualify interrupted/lost-reply recovery while I/O is active, unchanged full-dash
workloads, actual dash main/eval integration, matching full connections/runner
suites or independent SDK/consumer acceptance. Those remain prerequisites before
broadening the private route into a shell contract. OpenZFS persistence, packages
and sys-init assembly remain separate R1 work.

Final attempt2 passes all68 native cases in192.000 recorded case seconds. The host suite passes105 Python tests plus Zig/Rust checks. Both the positive overlap and exact2760 starvation control pass. All prior81 images remain identical. Attempt1's product failure is preserved; no timeout is counted as acceptance.
