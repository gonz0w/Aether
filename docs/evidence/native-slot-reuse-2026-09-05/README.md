# SI-04 sequential slot reuse verification

The kernel metadata correction already captured in
[native-program](../native-program-2026-09-05/README.md) fixes sys-init's retained
sequential reuse failure. The exact forward probe passes; a private copy changing
only `[0, 1, 0]` to `[1, 0, 1]` passes too. Both require supervisor result 100,
three reclaims and `AETHER NATIVE INIT PASS`. All nine unchanged sys-init adapter
cases pass, including the overlapping-worker ordering and designated deadline,
readiness, owner-death and zeroing controls. No panic or watchdog is accepted in
either sequential probe.

The corrected, already-published producer summary SHA-256 is:

```text
3a399587b34010302d25838d9f8e1cc73e2b93bec1ac673321326494bde1f155
```

Reproduce the adapter run with explicit offline inputs and a new private output:

```sh
python3 /absolute/sys-init/tests/native-init.py \
  --producer /absolute/Aether/docs/evidence/native-program-2026-09-05 \
  --summary-pin 3a399587b34010302d25838d9f8e1cc73e2b93bec1ac673321326494bde1f155 \
  --deps /absolute/Aether/.deps --work /new/private/adapter-run
```

For the exact minimal probe use the retained
`forward/sys-init/tests/native-init.py` here with the same arguments; the reverse
copy is under `reverse/sys-init/`. These runners resolve their adjacent retained
client sources. Commands, source inventories, raw supervisors, envelopes and serial
logs are retained. All frozen inputs were verified unchanged before retention.
The producer archive and its input/artifact pins remain in the linked existing
bundle; no historical evidence or companion pin was rewritten.

Aether's permanent init suite now includes both ordering regressions. Its nine
cases pass, as do host tests, 44 Python tests and all three offline standards
checks. `init/` retains that final run; `regression-sources.tar.gz` and the summary
pin its source snapshot. The kernel files match the consumed producer exactly;
only the local regression fixture/runner changed. The first local regression
attempt failed assertion 743 because it used an incorrect reclaim opcode; that
test-authoring mistake was corrected before the final acceptance run.

These eleven companion-source outcomes were run by Aether. Sys-init still owns
its consuming refresh, evidence catalog and service/dependent lifecycle policy.
This closes the kernel-side SI-04 gate, not broader lifecycle integration,
descriptor inheritance, shell execution or persistent package installation.
