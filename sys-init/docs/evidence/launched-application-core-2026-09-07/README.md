# Fixed Rust Launched application — 2026-09-07

Decision 0169 implements a fixed Rust Launched application transaction with
exclusive policy/reservation ownership. Independent attempts and a single started-
dependency pair have explicit starting/started state. Whole-member preflight
precedes mutation; the provider's transition generates and retains its dependent
launch obligation with all ten occurrence-token fields and Reserved disposition.
Verified application publishes an owner-bound Applied receipt; replay does not
repeat policy mutation or effect capture. Foreign/cancelled/stale inputs deny.
Unknown is recorded and the owner closes before mutation; failed verification
retains actual state and captured effects, and blocks replay/cancel/new admission.
Read-only state/effect inspection grants no execution authority.

All seven new application tests and four omission controls pass, alongside the
five reservation tests and three reservation controls. All ten local gates pass
in `run-7zvhu56k`, including 287 unchanged model tests and ten Rust groups. The same
code compiles for x86_64-unknown-none. Storage stays 1976 bytes; Reservations stays
1984; Application is 1992, excluding native History/resources/stack. The profiles
generate at most one effect per cut but retain the twenty-entry pool. Even a zero-
effect Applied cut keeps twenty credits; further reservation remains Full until
explicit retirement exists. No acknowledgment, effect execution or reset API.

All 194 existing ABI-15 images and 151 ABI-6 rebuilds are byte-identical, with a
maximum ABI-15 image of 8056 bytes. The new methods are not called by the native
consumer: this is host Rust execution and target compilation, not a fresh Aether
application witness. The 194-case native checkpoint remains decision 0168. Full
native integration still requires an exclusive original-History owner, exact
source revalidation, actual worker binding and a fresh consuming witness. Tokens
use the fixed fixture's symbolic domain; native journal issuance is not claimed.
Release locks and the 50-bundle/3019-case catalog remain unchanged. BG-056 complete
producer source closure remains a separate catalog-acceptance gap.

The first image-comparison driver failed while mistaking `rustc --version` for a
build command; its frozen inputs, driver and traceback are retained. Filtering
actual output-producing compiler commands fixed the driver; the fresh full rebuild
then passed. No image failure or target-run result is inferred from that error.
Evidence: `docs/evidence/launched-application-core-2026-09-07/`.

Next BG-057/BG-058: bind this application owner to qualified native launch history,
verify complete generated effects and consume fresh target controls. The driver
return's Applied state and policy observation's Applied receipt remain distinct.
BG-058 keeps per-attempt cleanup/reclaim provenance; BG-060 sustained reuse and
BG-033 recovery stay open. No additional host-platform campaign or sibling change.

validation/ retains the complete local run; rust/ the final focused Rust source, compiler pins, host binaries, target compilation and controls. initial-rust/ preserves the earlier passing revision. Native/legacy comparison directories are build-only artifacts, not QEMU results. failed-build-driver/ retains the failed orchestration attempt. adoption/ freezes this handoff; sha256.json seals the package.
