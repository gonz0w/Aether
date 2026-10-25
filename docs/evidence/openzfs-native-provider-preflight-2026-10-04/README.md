# Granted providers, native selectors and checked OpenZFS time helpers

2026-10-04, R1-03. Private native experiments with the independently consumed
error-guarded SDK. No kernel/ABI/quota, normal image, release pin or sibling changes.
[Contract](contract.md) records requirements before implementation; [source review](source-review.md)
separates real enforcement, private port semantics and remaining prerequisites.

Five provider/selector cases pass: qemu64/max positive, exact frozen-clock253,
disabled-pair251 and false-AVX254 controls. Both positive contexts preserve the
existing memory/TLS/64-yield/output/terminal oracles. Missing/foreign/future/wrong-type
grants reject; a page allocation consumes one available page and unmap restores it.
Time advances during user work. max advertises hardware AVX while real upstream
selectors correctly deny it because the kernel does not enable OSXSAVE.

Eight private time-helper cases pass: qemu64/max positive; exact frozen253; denied
grant/disabled-pair and all three wall helpers terminate125. Positive cases use the
actual adapted inline gethrtime. No fake epoch, entropy, resource count or error
suppression. Initial time attempt1 fails compilation because _Exit needs stdlib.h;
it is retained with exact sources/commands/logs. Attempt2 corrects that include;
qualified inputs remain frozen. Provider attempt1 has no failed target cases.

This is virtual boot-local time and available granted pages, not calibrated public
time, physical RAM, resource reservations or full engine admission. SIMD selector
success does not qualify algorithms or preemption. Only helper consumers are rebuilt;
the full engine's previously linked objects and engine entry are untouched. See
source-review for the remaining local provider/profile/admission work. No new sibling
blocker, owner acceptance, production filesystem or R1 readiness is claimed.

Reproduction uses the exact current pinned compiler/runtime and historical build
command receipt; private evidence scripts are not supported developer entry points:

```sh
python3 docs/evidence/openzfs-native-provider-preflight-2026-10-04/setup.py
python3 docs/evidence/openzfs-native-provider-preflight-2026-10-04/verify-inputs.py
python3 docs/evidence/openzfs-native-provider-preflight-2026-10-04/native.py
python3 docs/evidence/openzfs-native-provider-preflight-2026-10-04/time-native.py
python3 docs/evidence/openzfs-native-provider-preflight-2026-10-04/checks.py
```

Use a fresh owned root; never overwrite retained attempts. The original setup.json
binds prior complete readback and input selection; verify-inputs.py emits a fresh
receipt against all sealed members. The SDK and original/generated headers are
selectively copied regular files; no sibling bytes or historical links are followed
by builds. New run receipts snapshot actual runtime/tools/header/SDK bytes, commands,
timestamps, ELF/ISO/serial hashes and controls. QEMU has an external30-second watchdog.
The max runner changes only the frozen helper's CPU literal and is retained.

Full host/pin/workflow, simplicity, original-source identity, scoped C formatting,
Python syntax and local links are required before sealing. Derived CDDL header keeps
upstream formatting; new original C follows the reviewed style. New artifacts include
all attempts and selected reused inputs; archive.py reads back every member before
removing only this experiment's owned duplicate output. Prior sealed packets stay
immutable. Notices for original upstream/musl remain; original wrappers/recipes are
BSD-2-Clause. Retention receipts distinguish experimental results from release gates.
