# 0161 — Terminal-cut journal integration

BG-057, 2026-09-07. Extend the actual policy-model/journal adapter with bounded
Terminal observations after an earlier applied Launched cut. Reuse reserved batch
and complete effect-capture checks. Factor Launched event/transition hooks without
changing its existing behavior or omission oracles.

TerminalAdapter retains up to two Launched and two Terminal Source bindings under
the same owner/token/worker. Terminal content is the explicitly synthetic qualified
fact tuple (revision, result, kind, historical_ready), not native O1/S/O2 capture.
Validate scalar bounds and the existing normal 1..256, fault 135, stopped 144
mapping before application. Revalidate executed launch binding, live generation
and running/owned state. Preserve normal/fault/stop distinctions and exact detail;
verify terminal/cleanup-pending/owned state and the real reserved reclaim obligation.
Historical readiness remains retained metadata, never a new ready event.

Test normal zero/nonzero exit, normal-vs-fault 135 and normal-vs-stop 144 collisions,
malformed facts, early terminal, stale generation, repeated replay and dependent
launch obligation blocking Terminal reservation until settled. Controls collapse
kind by result or omit transition kind/detail verification and must fail named
assertions. Retain all earlier adapter/core controls. Run all local gates.

Fixed-time, running-to-terminal model scope only: native fact provenance, live stop/
unknown recovery, Cleaned admission and actual reclaim/endpoint/wait disposal remain
follow-ons. No native code, ABI, shared pin, dependency or sibling modification.

## Validation and handoff

Decision 0161 integrates Terminal cuts with the actual lifecycle model and effect
journal. It validates bounded synthetic facts and the executed launch binding,
then maps normal exit, fault and stop without collapsing equal numeric results.
Application must retain terminal ownership, pending cleanup and exactly one real
reserved reclaim obligation. Replay returns the retained receipt without another
transition. Missing reclaim or incorrect terminal kind closes the adapter while
retaining the resulting state and captured obligations.

All 271 model tests pass, including eight Terminal adapter tests and two source
omission controls. All ten local gates pass in `run-v1m4lwsw`, with unchanged
checked inputs. All twelve native consumer sources, three release locks and
catalog bytes match the preceding checkpoint. This tests actual policy-model and
journal code with synthetic native-origin facts; it does not demonstrate native
source capture or resource disposal. No independent reviewer sign-off is claimed.

Next BG-057: Cleaned admission after the actual reclaim obligation is applied and
remaining resources are verified empty. Native provenance remains BG-058; sustained
reuse remains BG-060 and recovery BG-033. The 185-case native checkpoint and BG-056
producer source-closure limitation remain unchanged.

Review: normal exit 135/fault 135 and normal exit 144/stop 144 remain distinct;
historical readiness never becomes a current ready event. State and effect-capture
verification remain separate, and the missing-reclaim oracle inspects the actual
post-mutation state. Shared Launched hooks preserve all existing transition and
capture controls. Documentation impact: model reference and test count, adapter
contract, source inventory, command digest/line references, quality coverage and
BG-057 handoff. Evidence: `docs/evidence/terminal-journal-adapter-2026-09-07/`.
