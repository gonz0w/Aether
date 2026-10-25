# Consumer helper path and arguments — 2026-09-24

The preimplementation contract and security/resource review are in
../../NATIVE-SHELL-STARTUP.md, Consumer helper arguments at exec. Qualification passed in one native attempt. The new opt-in request accepts only /inputs/helper with the two-element
vector [/inputs/helper, copy] and empty environment. It transmits argc2 and copy;
argv0 is fixed by the pregranted image selection. The owner validates the canonical
vector and supplies it at native replacement admission. Native PID/PPID retain
fixture identity independently of argv. No arbitrary argv/environment transport,
filesystem lookup or path-derived authority is claimed.

Positive probes reject unsupported path, argv0, argument, count and environment
before denied/retried exec, then require unchanged descriptor flags, inherited
fd0/1/2, full streams,8 waits and15 reclaims. A corrupt wire argument must reject2746
before helper replacement admission. Existing profiles remain regression witnesses.
The replacement body remains a fixture: actual consumer helper and dash orchestration
are still pending, as are independent acceptance and full serial-shell assembly.

Commands:

```sh
python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json
zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global
```

## Qualification

All85 native cases pass in239.843 recorded case seconds;
105 Python host tests plus Zig/Rust checks pass. The new positive completes across
three generations; the corrupt wire argument rejects2746 with zero reclaims and
no slot3/4 replacement admissions. There were no failed native attempts.

All281 runtime inputs remained frozen. Six sources changed, all in the private
capacity clients/owner and harness. Of105 previous ELF/raw images,75 are identical
and30 legacy exec-request owner images changed. The representative old remap owner
is still17496 bytes and differs only at four pointers to equal zero-filled constants;
legacy-layout-review.json verifies their spans and legacy-audit.diff records the
exact disassembly difference. All affected legacy profiles pass target regressions.
The two new owner images are identical17512 bytes, within the existing24-KiB limit.
Three new client ELFs cover source, forged wire and replacement.

Reviewed positive linked call depth remains3968 of4088 usable owner stack bytes,
leaving120; the changed argument admission and request validation are shallower.
The audited ELF's extracted text equals the qualified raw. This is a scoped binary
review, not a general stack proof. The native worker stack is separate from the
Rust owner's one-page stack. No resource budget, kernel, shared pipe core, SDK,
sibling, dependency, released pin or public contract changed.

finalize.py verifies source snapshots, archives every generated file and checks its
hash against both the archive and live file before deleting the owned duplicate
suite directory. Source/consumer snapshots, reports, logs, compatibility and stack
reviews remain sealed by SHA256SUMS. No earlier evidence is removed.
