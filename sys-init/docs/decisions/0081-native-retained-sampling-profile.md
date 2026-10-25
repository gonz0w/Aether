# 0081 — Qualify the retained-sampling native profile

Accepted bounded experiment, 2026-09-06; BG-058. Decision 0080 supplies the build research.

## Acceptance plan and compatibility

Adopt `retained-sampling-v1` for the experimental `tests/native-init.py` harness:
Rust 1.98.0, edition 2024, x86_64-unknown-none, optimization s, panic abort,
static relocation, unchanged init.ld and 1–4096 byte raw image. Normalize the
native source directory to `sys-init/prototypes/native-supervisor` using rustc
path remapping. The former implicit opt-level=2 default is replaced only in this
harness; other builders remain unchanged. Historical receipts keep their exact
commands and bytes. The report adds a build_profile identifier; schema, existing
fields, CLI arguments/exits, smoke markers and all prior case oracles stay intact.

Consume the exact assembled decision 0080 candidate. Sample::new/push remain out
of line and Sample::state always inline. Fixed caller-owned three-receipt storage
is exclusively borrowed with Driver by Sampling; no allocation, new syscall,
dependency, unsafe block or wider authority is introduced. Each received raw
triple is retained before qualification. Native operation/errno remains distinct
from local validation failure; both close the driver and retain its pending target.
Invariant unwrap failures in these new paths use the existing 1042 fixture result;
no emergency handler or existing assertion result is replaced. The phase guard
assertion moves within the held fixture but still runs without a pending reservation.

Execute all 125 preceding oracles and two new bound partial-prefix cases on the
same pinned producer/worker, in a new private QEMU work root, SMP disabled. The
new cases invalidate the original worker after one/two successful reads by known
fixture cleanup and replacement. Exact S/O2 native -9, original prefix, pending
index, old diagnostic worker, absent fact and closed driver must remain; expected
completion is 100/reclaimed=3. No timeout, missing tool, missing test, overflow or
failed omission control can pass. Compare prior oracles and frozen input hashes.
Run relevant harness tests, pure host validator controls and all nine development
gates. Retain commands, compiler identity, failure logs, raw images and acceptance
records before claiming native acceptance.

Foundations O-01/O-03/O-04, I-01/I-03–06 and E-01–08 apply. Existing Distribution
fixture and Experience developer-output scopes remain; no shared ABI/pin or
presentation adoption changes. This local compatibility decision is within the
maintainer-authorized experiment, not independent reviewer sign-off.

## Remaining scope

Fixture-seeded admission does not qualify full reserve/acquire/launch-to-sampling
composition. Malformed native injection, NT-05–07, session/history retirement,
journal integration and BG-033 recovery remain under BG-058/BG-057. The borrowed
session does not enforce a future journal consumer's retention protocol. Image
size is not a speed benchmark or a production budget. Only 48 bytes of measured
headroom were available in the study; the actual consuming build must fit again.

## Review finding before completion

The study's AST extraction substituted receipt_channel for no-cfg policy. Its
120 named links are valid, but did not cover that default configuration. Corrected
the mutable research explanation, preserved original retained evidence, and kept
policy/skip-deadline in this full native acceptance run. Compare those against the
prior native witness; they have no corresponding build-study image.

Evidence retention also found four dynamically constructed service-bad-* cases
absent from the study AST extraction. Together with the two no-cfg cases, these
six native cases have no study-image comparison; all remain in the 127-case run.
The first retention script stopped on this missing baseline before sealing or
registering a witness; its partial private output is retained for diagnosis.

## Results and review

Decision 0081 passes all 127 native cases under retained-sampling-v1, including
all 125 prior oracles and two bound stale-prefix cases. The exact size-study
candidate now composes Driver with fixed raw-receipt storage through an exclusive
Sampling borrow. S/O2 native -9 preserves successful prefixes, original diagnostic
target, closed admission and pending state; positive probes finish 100/3.
All 183 frozen inputs unchanged; largest image 4048 bytes (48 bytes headroom).
All 121 comparable native images match the study bytes; six cases omitted by the study
have fresh native coverage and no claimed study baseline.

This qualifies bounded retained sampling with fixture-seeded admission. It does
not qualify full launch composition, malformed native injection, NT-05–07,
journal/history retirement or recovery. Next: NT-04 labelled malformed-reply
injection through the bound session with retained resources and exact local causes;
then NT-05 interruption and NT-06/07 pending-history bounds. BG-057 owns consumer
retirement and BG-033 retains unknown-owner recovery.

0 of 125 prior client images are byte-identical; every changed
client has a fresh target result. No previous oracle was relaxed. All 38 harness
tests and nine named host Rust validator tests with two exact omission controls
pass. Initial mistyped worker pin was rejected before work-root creation; the
failed diagnostic and corrected invocation are retained. No candidate VM run
failed. Evidence: `docs/evidence/native-retained-sampling-2026-09-06/`.

Documentation impact: profile/default compatibility, terminal contract status,
consumer usage, native coverage/catalog, standards adoption, quality inventory,
research coverage correction and owning planning records. Reviewed touched code
for fixed bounds, ownership, denial before reads, native/local error identity and
retention; no new unsafe primitive or external interface. Independent review and
production/platform conformance are not claimed.

Validation: all nine development gates pass in `out/checks/run-x0t_os6o`.
The offline catalog now audits 1779 historical outcomes across 42 bundles; this
is separate from the fresh 127-case native run. Ten current consumer inputs and
the unchanged worker/builder match the executed/build snapshots. Full results,
host validator artifacts and adoption records are retained with this evidence.
