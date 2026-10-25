# UL-077 — controlled writable generators

PLAN.md defines stage ownership, source/authority bounds and acceptance. The build
now compiles target generators locally, executes them through top-level lifecycle
owners, and completes make locally. This avoids killing a nested cleanup owner when
make times out. Four exit-97 guards prevent unexpected generator execution by make.
Input hashes precede generator consumption and must match after execution; generated
outputs/guards must match after final make. Original upstream recipes are unchanged.

Model tests cover both mount modes, malformed/exclusive mount arguments and the
existing lifecycle cases on Python 3.14.7/3.10.21. The real writable-mount control
writes its allowed child and fails a parent write, then removes the container.
The parent tree is read-only; only the existing obj/src child is writable during
actual generation. No arbitrary bind options, remote service mutation or image pulls.

The initial Python 3.14.7 build passed; initial-build.py records its exact source.
Before final qualification, explicit generator input/output/guard hashes and stability
checks were added. The full Python 3.10.21 build then passed; build-executed.py binds
that executed source. All four guards reject with exactly 97. No failed build or
missing generator is counted as acceptance. Existing Clang unused-linker-argument
warnings remain unsuppressed in compile logs; no warning-free claim is made.

After execution, one metadata string was corrected in current build.py: the inherited
"host sandbox" label is replaced with an explicit no-host-sandbox claim. verify.py
requires that exact replacement to be the only difference from build-executed.py.
No execution path changed after the qualified build; source identities and this
reuse boundary are recorded. The old evidence bytes remain untouched and the old
sandbox label must not be treated as proof of host confinement.

The fresh ELF is byte-identical to the original reference. The import audit passes
with the same 99 symbols. Generated tables match after replacing only exact build
root paths; differing raw hashes are retained rather than normalized in evidence.
All twelve guest cases on the final fresh build pass, matching original script,
stdout and expected-exit identities. This is Linux emulation, not Aether execution.

A separate verifier confirms all eight generator containers, one mount-control
container and twelve guest containers absent by both name and ID: 42 complete
queries. verification.json binds these results, exact ELF/source identities and
comparison rules. Local receipts retain cleanup and status for each build stage.
Raw reports/scripts/notices/generated tables are retained selectively in runs/;
full compiled artifacts and source trees remain in named private build roots with
recorded hashes. This packet is not a self-contained redistributable SDK.

Commands from repository root:

```
python3 -B experiments/dash-reference/test-container-process.py
build/python-qualification/Python-3.10.21/python.exe -B experiments/dash-reference/test-container-process.py
python3 -B build/dash-generator-review/boundary.py
python3 -B experiments/dash-reference/build.py
build/python-qualification/Python-3.10.21/python.exe -B experiments/dash-reference/build.py
python3 -B experiments/dash-reference/audit-imports.py build/dash-reference-g6vh8in6
build/python-qualification/Python-3.10.21/python.exe -B experiments/dash-reference/test.py build/dash-reference-g6vh8in6
python3 -B build/dash-generator-review/verify.py
python3 -B docs/quality/check.py
```

UL-077 build/test integration now has live evidence. Independent technical review,
live remote service-loss/creation-ambiguity and broader UL-061–063 migration remain
open. Owner SIGKILL, hostile daemon/competing mutation and total wall-clock bounds
are not covered. No shared release pins, sibling implementation or native acceptance
changed. New source identities supersede affected dated census rows without rewriting
historical snapshots.

The initial staged whitespace check flagged raw traces and generated upstream
files. whitespace-review.json retains the result; exact evidence paths alone receive
.gitattributes exemptions. Original source whitespace checking remains enabled.
