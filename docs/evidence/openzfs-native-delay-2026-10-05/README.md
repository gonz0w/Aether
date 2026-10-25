# Checked OpenZFS delay caller

2026-10-05,R1-03. [Before-change contract](contract.md) and
[source review](source-review.md) describe this private port experiment. Full engine
entry remains unavailable; no actual elapsed delay or timed condition wait is claimed.

The actual selected libzpool delay checks negative/oversized signed64 ticks before
conversion into signed32 poll milliseconds. Zero is immediate. Positive durations
retain the inherited8ms/tick, accepting only poll(NULL,0,timeout)==0. Unsupported,
interrupted and unexpected outcomes terminate owner125 rather than silently return.
No retry policy, fake clock, SDK/kernel/ABI/quota change or new dependency is added.

One actual object145 changes among289 ordered engine inputs. Prior aggregates/ELF
and the freshly compiled original object reproduce exact bytes. Final selected ELF
4,384,800 bytes retains guarded inline/direct clocks, selected1/1/1/1 queues and no
host observers/static relocations. Whole-object discovery still denies exactly two
unavailable hooks. Current loader/W+X/TLS models must qualify the final bytes.

Twenty-seven host cases and two real old-source controls exercise bounds, zero,
conversion and poll outcomes with a controlled poll model. Six actual native cases
exercise unchanged musl poll's unsupported denial, zero immediate success and four
pre-provider bound denials. Existing isolated-context memory/TLS/64-yield/24-output/
terminal witnesses remain. Host poll models are never linked into the engine;
passing modeled timeouts do not establish elapsed waiting. Qualification and full
137 host/pin/workflow/scoped check receipts are retained with the archive.

Real calibrated monotonic/required UTC and native deadline parking, interruption
and mutex reacquisition still precede full engine startup/fini/restart. Scoped
resource/CPU/identity/config/entropy/volume providers, production helper counts,
actual native heap/ARC/TLS and feature closure remain R1-03 work. Independent SDK/
reader/consumer acceptance and broader SESSION integration are separate gates.

Private offline evidence recipes require a fresh absent owned tree:

```sh
python3 docs/evidence/openzfs-native-delay-2026-10-05/setup.py
python3 docs/evidence/openzfs-native-delay-2026-10-05/build.py 1
python3 docs/evidence/openzfs-native-delay-2026-10-05/components.py
python3 docs/evidence/openzfs-native-delay-2026-10-05/host.py 1
python3 docs/evidence/openzfs-native-delay-2026-10-05/native.py 1
python3 docs/evidence/openzfs-native-delay-2026-10-05/geometry.py
python3 docs/evidence/openzfs-native-delay-2026-10-05/inspect.py
```

These are frozen experimental recipes, not maintained developer entry points.
checks.py/archive.py require retained run.log receipts; never overwrite a sealed
packet. Subprocesses180s,QEMU30s/3s teardown. Archive readback precedes only owned
duplicate cleanup; shared caches/siblings/released evidence and pins stay fixed.
CDDL source/patch attribution and third-party notices remain; original probes and
tooling are BSD-2-Clause. No production fit, owner signoff or release is claimed.
