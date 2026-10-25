# Dynamic musl service lifetime

Private producer qualification passes,2026-10-05. The
[packet](evidence/native-service-dynamic-2026-10-05/README.md) and
[before-code scope](evidence/native-service-dynamic-2026-10-05/contract.md) extend
[origin creation](NATIVE-SERVICE-ORIGIN.md) with two full rounds. One creator and
one cleanup worker count within82 service slots;80 detached peers are reused once,
with162 total admissions. Actual creation is in progress while cleanup still owns
old pending peers. Small companions use primary creation and one cleanup worker.
Atomic record ownership and direct TLS association avoid metadata races. Pending
peers park; only confirmed native stop/unmap/retire publishes a reusable FREE slot.

Seven final fresh cases and137 host/pin/workflow/scoped checks pass. Wrong-grant
clone360, early unmap352, missing overlap365 and omitted primary park356 reject
exactly. The ordinary case runs one dynamic service and small-peer replacement;
full-capacity stop/replacement uses one round. The fresh origin regression retains
full-service replacement and deep-stack/heap checks. All eleven attempts, including
repeated-service/four-round timeouts and diagnostics, remain sealed. Those stress
workloads, dynamic reuse after service stop and281 engine lifetime are unqualified.

Run the packet's `sdk-setup.py`, then `qualify.py 1` from the repository root with
a fresh owned output tree. No kernel/public ABI/SDK, quota, sibling or pin change.
Production reaper/helper cost, measured native latency and actual engine providers/
configuration/calibrated clocks/startup/peak and independent consumer/R1 acceptance
remain open. This private producer witness does not deliver companion SESSION.


Subsequent qualification,2026-10-05: [owner-local mapping pin validation](NATIVE-SERVICE-PINS.md)
closes selected repeated-service and four-round progress under the same watchdog,
retaining every pin. This supersedes those pending stress results at a newer
kernel revision; the original sealed packet remains unchanged and no broader
engine/production/consumer acceptance follows.
