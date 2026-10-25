# 0079 — Capture and retain actual raw sample returns

Implemented standalone capture probes, 2026-09-06, BG-058 NT-04 slice.

Add raw observation/status capture through the existing unchanged trap and consume
those returns with the decision 0078 validator. Existing Adapter methods and error
contracts remain. Standalone fixtures retain actual Worker/Reader variables and
fixed Sample storage; no allocation, reset, journal or authority API is added.
Capture each actual raw return before validation, preserving signed RAX/RDX/R8.

Raw-terminal retains O1/S/O2 and checks the qualified kind-1/result-18 fact plus
sealed-state overwrite denial. Raw-first-stale, raw-status-stale and
raw-observe-stale reclaim/replace a fixture-owned terminal worker before O1, S or
O2 respectively. Actual stale lookup returns -9, preserving every received prefix
and operation identity with no fact. These deliberate fixture lifecycle
interleavings are not production concurrent mutation or lost-reply recovery.
All four positives finish 100/reclaimed=3. Raw-forget-prefix deliberately drops O1
when the actual S error arrives and must reach 1042/reclaimed=1. Retention assertions
use 1042; setup/cleanup use 1043. All 120 prior case oracles remain required.

## Composition limit and scope decision

The initial implementation added storage borrows to Driver. A second attempted
composition used a session exclusively borrowing Driver and Sample, preserving
the old Driver layout. Both exceeded the unchanged 4096-byte image limit in
sampling probes. A retained linker map measures one combined held probe at
0x1530 bytes. A third size attempt reduced panic-location overhead but still did
not fit. These snapshots/logs remain in preflight-builds; none is target acceptance.

Keep the previously qualified binding.rs byte-for-byte. Qualify actual raw capture
and error-prefix retention independently rather than weakening the old driver
oracles or raising the image bound. Full retained-driver composition is unfinished
and needs an explicit fixture-size strategy; adding storage to Driver is not
accepted by this checkpoint. The current Driver still uses its old decoded sampler
and does not retain raw partial receipts. Standalone success is not ND-02 completion.

Producer/worker pins, 4096-byte bound, old native methods and smoke protocols remain.
Host validator tests/omission controls and nine full development gates are required,
as is a fresh native witness. Shared releases, ABI, unsafe primitive, dependencies
and presentation do not change. Native malformed-return injection, NT-05–07, full
launch composition, journal retirement and recovery remain follow-ons. No independent
review sign-off or general POSIX/runtime conformance is claimed.

## Result and scoped review

Decision 0079 passes 125 native cases, including all 120 previous oracles.
Raw capture retains actual signed RAX/RDX/R8 for a coherent terminal sample and
actual stale errors at O1, S and O2. Successful prefixes remain intact; the native
prefix-omission control reaches 1042/reclaimed=1. Four positives finish 100/3.
All 183 frozen inputs unchanged; 65 of 120 prior images match byte-for-byte.

This is standalone raw capture and validation. Combined driver/receipt probes
exceeded 4 KiB in retained size attempts; binding.rs remains byte-identical to
its prior witness and still uses the decoded sampler. Next: a size-bounded driver
composition strategy before integrating raw history. Native malformed injections,
NT-05–07, full launch composition, journal retirement and recovery remain open.

The raw Adapter methods call the same unchanged trap with the same operation and
actual Worker arguments as existing decoded methods. They perform no validation,
resource accounting change or mutation. Sample retains the returned triple before
interpretation, and seals on live/terminal/error outcomes. The test deliberately
reclaims only its positively known worker before retaining a stale diagnostic
wrapper; the replacement's actual handle is checked against the expected generation.
Native negative RAX is distinguished from local validation causes. Original prefix
and negative auxiliary register values survive exactly; no missing receipt is
fabricated and no sampled error is interpreted as reclaim acknowledgment.

The full binding and terminal modules are unchanged from decision 0077. The attempted
session composition and initial Driver storage changes are retained only as failed
build snapshots, not accepted runtime code. No driver ownership or retention claim
is inferred from standalone success. The host validator still checks malformed
booleans/kinds/coherence and synthetic interruption with two semantic controls.
The new native omission control executes the same prefix-dropping mutation against
an actual S error, and fails before replacement teardown at the required assertion.

Four preflight attempts are retained; the final builds all 118 configurations.
The linker map was generated diagnostically without relaxing its bound. One first
runner invocation rejected a mistyped worker receipt pin before creating a work
root or executing target code; the corrected invocation uses the unchanged pin.
That rejection log/command is retained. No actual target execution failed.
Current native inputs, original worker build and all nine development gates are
checked separately. Tool versions, shared releases, unsafe primitives, ABI,
existing methods, output/exit contracts and dependencies remain unchanged.

Documentation impact: terminal contract, native coverage/adapter references,
standards adoption, quality inventory and planning. No independent reviewer
sign-off, full NT-04/ND-02 completion or new supported platform is claimed.
Evidence: `docs/evidence/native-raw-sampling-2026-09-06/`.

All nine development gates pass in `out/checks/run-onzug_wc`. Ten current
consumer files and unchanged worker/builder sources match the retained native
evidence in `docs/evidence/native-raw-sampling-2026-09-06/`.
