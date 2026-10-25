# Direct service pair — 2026-09-07

BG-065 component evidence: seven native executions, host tests/controls and
compatibility builds. Runtime builds use the existing offline producer/worker
pins; released standards and the unreleased simplicity snapshot are unchanged.
Final validation and adoption records are retained here before sealing.

Final validation passes all ten gates in run-9z093f7o, with checked inputs unchanged.
The Rust receipt also passes: twelve methods, thirteen named records, eight owner
and five pair tests with five exact private omission controls. host-final/ retains
source, commands and logs; rebuildable host executables are omitted. native/ retains
seven actual Aether cases and their copied inputs, raw/envelope/serial/QEMU artifacts,
commands and ISO hashes. Generated ISOs remain in private out/. No new native
failure occurred. compatibility/ retains all 590 prior-profile builds: 587 identical
images and three changed owner images matching their fresh executions.

The first aggregate passed all tests but rejected six evidence Python files added
during its source snapshot; validation-attempt-1/cause.json records the exact added
names and confirms no prior source bytes changed. It is not acceptance. Final
validation began after packaging. Adoption records capture the first SE-01–05
application and BG-066 handoff; the shared draft snapshot and released pins remain
unchanged. sha256.json seals the retained bundle, excluding only itself.
