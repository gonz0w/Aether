# Terminal application core — 2026-09-07

Decision 0173 adds the fixed Rust Terminal application primitive. After both
Launched observations, one member can advance from phase 1 to phase 2 while the
peer and historical launch cuts stay unchanged. The transaction reserves the
whole pool, records Unknown before mutation, and captures exactly one complete
reclaim occurrence before publishing Applied. Its local token uses kind 8 for
reclaim, existing activation cause 7 and operation 1. Source facts, terminal kind,
readiness, native grants and actual reclaim remain outside this pure primitive.

Exact replay returns the retained cut and cannot issue another reclaim. Early,
foreign, cancelled, wrong-phase and mixed-member requests deny without mutation;
application revalidates policy. Unexpected pool entries or failed transition/
capture verification preserve actual phase/effects, retain Unknown and close.
Both terminal orders are exercised, including explicit acknowledged retirement
between cuts and preservation of the original launch records. Four omission
controls detect skipped transition, dropped/corrupted capture and reopened Unknown.
No Cleaned, retry, general multi-member Terminal cut or sustained reuse is added.
Storage remains 1976 bytes and Application 1992 bytes, without allocation or new
unsafe code. Phase-specific reservation shares the same bounded implementation.

All ten local gates pass in `run-w7c_s_i7`: 287 model tests, ten Rust groups with
22 core tests and 16 omission controls. The core also compiles for the native
no_std target. All 208 existing ABI-15 clients rebuild within their unchanged
8192-byte limit (maximum 8152). 190 images match decision 0172 byte-for-byte;
18 changed images were freshly consumed on Aether and preserve their exact prior
outcomes. All 151 ABI-6 images rebuild identically within 4096 bytes. The retained
comparison names every client and the restricted native runner executes exactly
the 18 changed images. This is not a new 208-case execution campaign. No failed
builds, tests or native attempts occurred in this step.

The new Terminal methods are not invoked by native clients. Representative
bound-reservation and dependent-launch assembly is retained and contains neither
Terminal entry point. Therefore this evidence demonstrates host core behavior and
compatibility of existing native paths, not native Terminal application. Full
sealed-Sample/fact/worker/occurrence qualification and consuming execution are the
next BG-058 gate; no caller-created terminal phase is accepted as native evidence.

Evidence: `docs/evidence/terminal-application-core-2026-09-07/`.
Producer/worker/release pins and the 50-bundle/3019-outcome catalog are unchanged.
BG-056 producer source closure is still pending; no existing exception is extended.
The core is process-local, with no durability, recovery or independent review claim.
Other-platform provisioning remains deferred and no sibling repository was edited.

Next BG-057/BG-058: bind this Terminal primitive to sealed original provider and
generated-dependent samples under the original owners, preserving partial returns
and errors before cleanup. A fresh target witness must cover that binding and its
reclaim capture. Actual reclaim/Cleaned application, BG-060 sustained retention and
BG-033 recovery remain later work. No kernel blocker is established.

build-comparison/ retains all 208 ABI-15 rebuilds, frozen source and representative assembly; legacy-build/ retains 151 ABI-6 rebuilds. witness/ retains only the 18 changed-image executions, their source, pinned producer/worker, raw images/envelopes and QEMU logs. Generated ISOs remain in private out. compatibility.json names the reused or fresh evidence for each image. validation/, rust/ and focused-rust/ retain local results. adoption/ freezes the handoff; sha256.json seals this bundle. The inherited producer archive still omits two recorded .DS_Store files; this is not complete producer closure or new catalog acceptance.
