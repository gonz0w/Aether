# Checked native OpenZFS inline time callers

2026-10-05,R1-03. [Contract](contract.md) records the before-change scope;
[source review](source-review.md) explains compatibility, security and remaining
unsafe wait callers. Private port/build evidence; no engine entry executes.

All four actual libspl inline time helpers now check provider failure, negative
seconds, fractional units and applicable signed nanosecond overflow before use.
Wall helpers call checked CLOCK_REALTIME directly, preserving microsecond precision;
they bypass musl gettimeofday's ignored clock failure. Unsupported or malformed
time terminates125. No fabricated UTC, virtual ticks, retries or SDK changes.

The selected queue baseline relinks byte-identically. Of289 ordered object inputs,
272 OpenZFS/generated inputs freshly reproduce original bytes;17 zlib/libtirpc
inputs lack the OpenZFS include chain and remain fixed. Actual dependency scans
rebuild234 time-header consumers, proving the guarded header is selected and the
old header absent;37 objects change. Final1027 bounded build/inspection commands
produce4,384,584-byte ELF/1312 initial pages versus1309 before. Actual ELF retains
1/1 system/delay, one ARC eviction worker and one file worker, no observer symbols
or relocations; whole-object discovery still fails its exact two unresolved hooks.
Both current loader models and actual W+X/TLS mutations pass;4-byte ELF TLS remains.

Forty controlled host-provider cases pass, including failure with initialized
poison or no output, negative/fraction/range errors, zero and signed boundaries,
and sub-microsecond truncation. Four real original-header controls return valid-
looking data on provider failure and fail the required125 oracle. Four fresh native
helper cases terminate125 using the unchanged guarded SDK. These are helper tests,
not successful clocks, whole-engine runtime, thread peak, admission or recovery.
Full137 host/pin/workflow/scoped checks pass. All failures and narrower passing
attempts remain, including native wall-inode245 that exposed the second ignored
error. Archive readback precedes removal of only owned verified duplicate output.

No kernel, ABI, SDK, quota, normal image, workflow entry, sibling or released pin
change. Direct timed-wait callers remain unsafe and full engine entry unavailable;
checked deadline conversions, real calibrated monotonic/UTC and scoped resource/
CPU/identity/configuration/entropy/volume providers, production helper counts,
native heap/ARC/TLS and CPU-state closure precede startup/fini/restart and R1.
Independent owner/reader/consumer and wider SESSION acceptance remain separate.

Private recipes require fresh absent attempt directories and exact sealed inputs;
these are evidence recipes, not supported developer tooling. Reproduction order:

```sh
python3 docs/evidence/openzfs-native-time-callers-2026-10-05/setup.py
python3 docs/evidence/openzfs-native-time-callers-2026-10-05/inputs.py
python3 docs/evidence/openzfs-native-time-callers-2026-10-05/zlib-inputs.py
python3 docs/evidence/openzfs-native-time-callers-2026-10-05/tirpc-inputs.py
python3 docs/evidence/openzfs-native-time-callers-2026-10-05/build.py 5
python3 docs/evidence/openzfs-native-time-callers-2026-10-05/build.py 4
python3 docs/evidence/openzfs-native-time-callers-2026-10-05/host.py 4
python3 docs/evidence/openzfs-native-time-callers-2026-10-05/native.py 3
python3 docs/evidence/openzfs-native-time-callers-2026-10-05/geometry.py
python3 docs/evidence/openzfs-native-time-callers-2026-10-05/inspect.py
```

The extra build4 supplies the historical path expected by the retained helper
recipes; both headers must match build5 bytes. It is not required to compile an
engine for helper tests. For exact original custody/failed-attempt outcomes consult
the retained archive/recipes rather than overwriting packet receipts with a new
run. checks.py/archive.py are one-shot original sealing steps and require all
original attempt records. CDDL upstream and MIT musl notices remain; new original
recipes/probes are BSD-2-Clause. No normative shared standard is added here.
