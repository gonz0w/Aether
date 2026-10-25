# Native binding acceptance review — 2026-09-06

BG-058/BG-057, decision 0074. This is a scoped source/evidence review, not an
independent sign-off or full ND-01 acceptance. The
[reviewed source snapshot](../evidence/native-synthetic-missing-return-2026-09-06/reviewed-files.json)
retains the basis before appending the latest checkpoint notes. Current runtime
sources match decision 0074's frozen target witness.

The [binding contract](../specs/NATIVE-DRIVER-BINDING-V0.md) and
[receipt contract](../specs/NATIVE-RECEIPT-OWNERSHIP-V0.md) specify broader acceptance
than the two-token native fixture currently supplies. Keep those requirements
visible when proceeding to terminal evidence. Separate fixture passes do not
compose into a production lifecycle driver.

| Requirement | Demonstrated scope | Remaining requirement and owner |
| --- | --- | --- |
| NB-01 | Decision 0066 binds two issued services at equal service generation to distinct actual workers; later witnesses retain this oracle | Dynamic issuance and real issuer validation remain BG-057/ND-03 |
| NB-02 | Ten-field token corruption, foreign trusted owner and invalid slot deny before acquisition | Producer/profile are fixed context, not a transported identity; malformed scalar parsing and runtime reconfiguration are outside this typed fixture. BG-058 must qualify any expanded input boundary |
| NB-03 | Consumed occurrence, pending creation/receipt and reserved-slot denial; two bounded records | No same-service second issued token, third configured attempt or 20-entry cut implementation. BG-058/BG-057 must test capacity when expanding issuance |
| NB-04 | Decision 0067 retains an actual pair through injected local binding failure; writer-loss control | Arbitrary malformed producer pair and complete next-channel-generation validation remain BG-058 |
| NB-05 | Decision 0068 qualifies received creation/launch busy returns and retains ownership/consumption; current receipt phases preserve those paths | Other native and local errors and lifecycle translation remain ND-04/BG-058 |
| NB-06 | Decision 0069 retains actual worker before checking expected native slot/generation; mismatch closes | Injected wrong expectation is not malformed raw-reply transport qualification. Broader return validation remains BG-058 |
| NB-07 | Full-token/worker launched predicate rejects equal-generation cross-service substitution; decision 0073 denies qualification before application | No event queue tied to this binding, retired binding reuse or pending-event replacement integration. ND-03/BG-057 retains these obligations |
| NB-08 | Decision 0070 tests actual native slot generation exhaustion; consumed tokens survive fixture disposal | Epoch/cut/operation limits, larger tables/history and replenishment require BG-057/BG-058 follow-ons before broader scope |
| NB-09 | Decisions 0072–73 retain real received channel/launch returns before application. Decision 0074 tests synthetic Started-with-no-return closure | No kernel reply is actually lost. Unknown native effects and replacement-owner reconciliation remain BG-033/ND-04 |

IR-01–06 now have bounded actual-return witnesses; IR-07 has the explicitly
synthetic schedule specified by the contract. The native start counters record
local start transitions in IR-07, not proof that a factory/launch syscall occurred.
The launch pair can be disposed only because the fixture knows no launch was
invoked; the driver does not gain that recovery authority from absence.

## Next work and gates

Proceed to the ND-02 terminal-kind contract already identified by the
[integration review](NATIVE-DRIVER-INTEGRATION-REVIEW.md). The current
[Adapter](../../prototypes/native-supervisor/adapter.rs) observation flattens
terminal detail and lacks the exact kind. The
[reconciliation review](UNKNOWN-EFFECT-RECONCILIATION.md) identifies a separate
status read as a research lead in the selected profile. Recheck exact frozen
producer status/observation semantics, retained target binding and interruption
behavior before coding. Specify equal numeric results with distinct kinds, stale
target denial and conflicting pending evidence. Do not guess stopped/faulted
classification from an integer or accept a mutable sibling pass as evidence.

This contract work is locally unblocked and supplies no new kernel backlog
request. It does not waive the NB gaps above or authorize production routing.
ND-03 must define whole-cut acceptance/retirement and repeat-call behavior before
binding events to the journal. ND-04 must cover selected error/unknown ownership
composition, and ND-05 must supply a composed policy witness. BG-033 retains real
unknown-effect reconciliation; no timeout, stale handle or fixture cleanup resolves
it. Existing BG-056 quality and BG-054 extended testing/release gaps remain.

Standards scope remains Foundations O/I/E under unchanged offline pins. No shared
rule, language, transport or POSIX/BSD/illumos/Linux mapping is selected here.
Documentation adoption and a target fixture pass do not establish full conformance.
