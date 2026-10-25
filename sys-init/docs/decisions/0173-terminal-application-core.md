# 0173 — Fixed Terminal application and reclaim capture

BG-057/BG-058, 2026-09-07. Implement the next pure Rust application primitive
before binding native terminal samples. This is a fixed started-dependency pair,
not Model.batch, general terminal-reason handling or native source acceptance.
Both Launched observations must already be applied. Accept one Terminal member
(attempt 0 or 1, phase 2) per cut; the selected phase must still be 1. Preserve the
peer's phase and all launch receipts. A parent must qualify the sealed original
Sample, exact terminal fact, original worker, launch occurrence and owner before
using this primitive. Synthetic indices here confer no native authority.

Generalize private reservation validation by a compile-time phase while preserving
the phase-1 entry point and all bounds. Terminal has a separate reserve/apply API;
phase-1 application cannot apply a reserved Terminal cut. Record Unknown/closed
before changing the selected phase to 2 and capturing its exact reclaim occurrence.
Reclaim uses symbolic kind 8, with the existing activation cause 7 and operation 1:
[1,2,3,journal,0,4+attempt,1,8,7,1]. This extends only local fixture symbolism; it
allocates no native ABI. Compare the actual phase vector and entire effect pool
against independently derived expectations before Applied publication.

An exact Terminal replay returns its original receipt without issuing another
reclaim. Credits remain held until explicit acknowledged-effect retirement;
retirement still preserves the exact original occurrence. No native reclaim call,
Cleaned phase, retry, history eviction, durable storage or general multi-member
terminal cut is implemented here. Keep 1976-byte storage and 1992-byte Application.

Host tests cover both terminal orders, exact reclaim tokens, peer/history
preservation, duplicates, early/unlaunched/foreign/cancelled/wrong-phase admission,
preflight revalidation, full-denial atomicity and post-mutation Unknown retention.
Controls omit the transition/capture, corrupt capture or reopen Unknown. Compile
the same core for x86_64-unknown-none. Rebuild all 208 ABI-15 and 151 ABI-6 clients;
byte-identical clients may reuse their recorded consuming results, but any changed
image requires fresh consuming execution. The new Terminal methods remain uncalled
by native probes and must not be described as native Terminal application.
Run all local gates and retain failed attempts and exact source/build comparisons.

Foundations O-02–04, I-04–06 and E-01–08 apply. Existing release pins, candidate
status, shared standards, kernel artifacts, smoke markers and image/stack bounds
remain unchanged. BG-058 owns the next native sample binding and consuming witness;
BG-060 sustained history reuse and BG-033 recovery remain separate.

## Validation and handoff

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

Technical review: the compile-time phase parameter shares admission mechanics without allowing phase-1 application to consume a reserved phase-2 cut. Terminal preflight checks the exact owner/key and current phases before mutation. Actual state/capture are compared with expectations before publication; incomplete output cannot reopen the owner. Historical count remains cached, and retirement does not erase the source cut. No native syscall or raw fact is accepted by this primitive. Documentation impact: storage contract, native coverage limits, quality inventory, standards disposition and BG-057/058 next steps.
