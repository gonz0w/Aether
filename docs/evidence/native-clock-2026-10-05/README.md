# BSP q35 elapsed-clock and absolute-park qualification

[Before-code contract](contract.md) and [native reference](../../NATIVE-CLOCKS.md)
record requirements, forbidden outcomes, authority/resources/unsafe obligations and
test selection. Eleven selected fresh native cases and214 unchanged maintained
target regressions pass. The actual q35 HPET source progresses without delivered
interrupts; real200/400ms absolute parks expire without early completion. Raw child
tests verify wake, original-deadline requeue, mapping pins and confirmed completion
before memory reuse. User MMIO access faults; disabled/foreign/malformed requests,
missing HPET, virtual-time substitution and early-completion controls reject.

Five source and45 execution model cases run in Debug and ReleaseSafe. Full host
tests/pins, workflow41 references/22 tools/72 groups, scoped Zig/C formatting,
Experience, simplicity hashes and source freezing are checked by [checks.py](checks.py).
Its raw result binds native binaries, QEMU commands, actual SDK/tool/header/runtime
hashes, declared scope and source inputs. This is producer evidence, not independent
reader/consumer acceptance, physical clock accuracy, certified effective resolution,
hard realtime, UTC, POSIX timed-condition integration or full engine startup.

Original pre-change sources and all attempts remain. Attempt1 passed four cases
then failed a duplicate positive/false build argument; the recipe now emits one
clock option. Attempt2 passed the narrower nine-case suite. Attempt3 exposed an
incorrect new pin-denial expectation (-16 rather than existing -13); only the probe
was corrected. Attempt4 passes11 cases, including the added child tests. The first
host run passes149 Zig cases but fails the Python option inventory; classification
of the positive flag and both guarded negative flags is completed only after the
frozen214 target regressions. No runtime source changes accompany that correction.
The extra-waits driver's inherited `fresh_targets=190` aggregate is incorrect:
four validated six-case receipts and24 recorded QEMU invocations prove24. The raw
receipt remains unchanged; final checks record the correction, not a new target run.

Kernel source/device state belongs only to BSP. Default SDK/image, siblings,
quotas, legacy virtual time and released pins remain fixed. Required actual musl
conditions/sleep/interruption, truthful UTC, expanded worker costs and engine
providers/resources remain open under STATE/SI-01/R1-03.

Run from the repository root into a fresh owned output root; never overwrite this
sealed packet:

```sh
python3 docs/evidence/native-clock-2026-10-05/setup.py
python3 docs/evidence/native-clock-2026-10-05/native.py 1
python3 docs/evidence/native-clock-2026-10-05/regressions.py
python3 docs/evidence/native-clock-2026-10-05/extra-waits.py
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

The selected final attempt is4; reproducing the qualification and final checks
requires preserved failed/narrower attempts as well as fresh selected results.
Private recipes are evidence tools, not a new maintained SDK/build entry point.
Targets use pc-q35-11.1/TCG, qemu64/max, one vCPU, disposable UEFI state, no NIC,
30s guest limits/3s teardown; image builds180s, retained start/end UTC timestamps.
No per-line host timestamp or wall-clock calibration measurement is claimed.
Original source files are BSD-2-Clause; the retained SDK keeps its musl notice.

[archive.py](archive.py) collects only the16 explicitly registered fresh suite
roots, preserves every owned artifact, reads every archive member back and verifies
identity before removing those duplicate roots and matching temporary logs.
The recursive manifest covers nested pre-change sources too. Source pins and all
earlier sealed evidence remain unchanged.
