# 0149 — EHT-01 Linux container qualification

BG-054, 2026-09-07. User explicitly requested Podman restart and continuation.
Foundations E-01–08 apply. Keep startup and execution within one live session:
separate sessions lost VM connectivity; a combined start/inspect verified the
cached image's original ID and digest. This observation suggests session lifetime,
not a diagnosed guest failure. Do not rewrite the failed 0148 attempt.

Run the exact EHT-01 plan and three implementation files plus 16 corpus inputs
from a private read-only snapshot in the cached Linux arm64 image. No pulls or
network, read-only root, private 128 MiB tmpfs, 512 MiB memory, two CPUs, 128 PIDs,
no capabilities or privilege escalation. Eight workers retain existing 60-second/
4 MiB budgets and 600-second campaign bound; outer container wait is 620 seconds
with named container cleanup. Require 432 actual cases, zero skips, same IDs/order,
plan/source/implementation hashes as macOS. Retain raw logs and image identity.

This qualifies the EHT corpus on this Linux container only, not all development
gates on Linux, PID 1, native Aether, BSD/illumos, hardware or production. Run all
ten local development gates after documentation/inventory updates. No runtime,
release pin, sibling repository, hosted scheduling or independent sign-off changes.

## Validation

Decision 0149 restarts Podman and completes EHT-01 on the cached Linux arm64
image: eight seeds, 432 executions, zero skips. Complete ordered worker records
and plan/corpus/implementation hashes match macOS. Startup and execution within
one live command session restored connectivity; prior failed attempts remain.
All ten local macOS gates pass in `out/checks/run-4_m7xion`; native inputs/output
and release pins remain unchanged. Next: current full Linux gate qualification;
BSD/illumos environments, independent review and hosted scheduling remain open.
Evidence: `docs/evidence/extended-host-linux-2026-09-07/`.
