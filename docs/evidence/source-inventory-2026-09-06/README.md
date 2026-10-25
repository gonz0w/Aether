# Complete source inventory and M4 reproduction — 2026-09-06

The corrected reproduction check compares the full post-build source inventory,
rejecting added as well as changed/removed/symlinked files. Seven new host cases
cover those failures, legitimate top-level build outputs and nested output-like
names that must remain source. Generated Python caches retain their prior exclusion.
Dependency bytes are checked separately by the reproduction runner.

Final fresh-cache reproduction passes: 80 host/Python tests plus kernel host and
standards/workflow checks, seven M4 target regressions and one-core boot/pixel
acceptance. Positive M4 framebuffer was visually inspected: AETHER/RUST DISPLAY,
RGB bands, AP result 5050 and display count 100 are visible. No display code changed.

The initial run passed host checks but QEMU could not bind its local QMP socket
under the sandbox (Operation not permitted). No guest boot completed; one-core
was not run. This is an infrastructure failure, not an expected negative/kernel
pass. A permitted local QMP rerun passed on unchanged source bytes. Both attempt
commands, exact UTC intervals, reports, logs and full source inventories/archives
are retained. Initial and final subdirectories keep their separate artifacts.

`summary.json` binds each reproduction report and source archive. Reports include
all source, verified boot-dependency and output hashes, tool versions/paths and
commands. Boot dependencies/tools are reused installed inputs, not included in
these archives. Artifact copies retain files under 2 MiB except ISO images; full
original output paths and hashes remain recorded. Rebuildable ISOs are omitted.
No independent clean commit/host, network confinement, native C companion suite,
physical-hardware acceptance or release readiness is claimed. The local working
tree is the source snapshot. `scripts/reproduce.py` remains the documented command.
