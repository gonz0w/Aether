# 0148 — EHT-01 replay and platform handoff

BG-054, 2026-09-07. Foundations E-01–08 apply. Review the sealed 0147
campaign against its plan and execute the exact first seed through the real CLI.
Require the same plan, corpus and implementation identities, exactly 54 actual
IDs in the recorded order, no skips and replay mode. Replay must not be counted
as a second eight-seed campaign. Preserve source, runtime, pins and prior evidence.
Run the full local checks and retain the new attempt separately.

The existing Podman VM was stopped. A temporary start reported success, but the
subsequent image inspection failed with connection refused and a new machine
listing reported Running=false. No test container ran, image identity was not
reverified, and no Linux qualification is claimed. Docker also had no socket.
Do not recreate the VM, download images or claim other-platform acceptance.
Provisioning a functioning Linux/BSD/illumos environment and an actual independent
reviewer remain external inputs; local replay verification can proceed.

## Result

Decision 0148 verifies real exact-seed replay: 54 cases pass with no skips and
the complete worker record matches the retained campaign. All ten gates pass in
`out/checks/run-9ufsvvpd`; native inputs/output and release pins remain unchanged.
Linux refresh is blocked: the existing Podman VM reported startup success but
stopped before its API/image could be reached. No Linux tests ran. Local EHT-01
work is at its handoff: a functioning additional host and independent reviewer
are required for broader qualification. No scheduler or post-R1 work is added.
Evidence: `docs/evidence/extended-host-replay-2026-09-07/`.
