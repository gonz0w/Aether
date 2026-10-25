# 0158 — Confirmed disposition and retirement model

BG-059 NC-06/07 subset, 2026-09-07. Add a pure Retirement owner around the
CutCoordinator and a trusted synthetic resource adapter. Before retiring either
member of a Cleaned cut, require the exact retained Applied receipt, earlier
Applied Launched/Terminal, and matching source-bound disposition: applied reclaim,
no reader/writer/worker/wait ownership and no unresolved obligation. Inspect both
members before marking either. Refuse foreign/old/uncaptured receipts and closure.

This initial retirement entry accepts cuts whose members are all Cleaned. Mixed
phase cuts remain valid coordinator inputs but their partial retirement needs a
follow-on. Resource inspection is a declared read-only trusted adapter operation,
not a caller-supplied boolean or native authority witness. Retain the exact applied
receipt and per-member started/retired disposition before each callback; a failure
closes the core without reapplication or rollback, retaining partial progress.
Exact repeated retirement returns without another callback. Never clear source
history, cut records, issuance or generations. No replacement/reset API is added.

Test two-member success/replay; premature/foreign/unapplied receipt; each nonempty
resource and missing reclaim/unresolved obligation; stale disposition identity;
second-member denial before any mark; failures before/after partial marking;
reentry and unchanged history. Three source controls must fail named assertions
for premature retirement, ignoring inventory and resetting retained source history.
Model/runner hashes, documentation and quality inventory must include this file.
Run all ten local gates. Native source bytes and standards pins stay unchanged.

This models tombstones, not actual journal/native cleanup, sampling pending release,
sustained reuse or recovery. BG-057 retains integration; BG-059 retains mixed-cut
retirement and NC-06 pending disposition, BG-060 reuse and BG-033 recovery.
Foundations O/I/E and Distribution durability exclusions remain as in 0156/0157.
Python allocation and trusted-adapter assumptions are not native memory guarantees.

Review refinements: permit only one Retirement attachment to a live core. Retain
returned diagnostic values in a one-element tuple so a returned None differs from
an exception without a return. Eight test methods cover this slice, with three
embedded source omission controls. Mixed-phase cut retirement and NC-06 sampling
pending disposition remain explicit follow-ons; this does not close BG-059.

## Validation and handoff

Decision 0158 adds pure resource-disposition and retirement qualification. A single
Retirement owner requires the exact Applied Cleaned receipt, prior lifecycle phases,
source-bound empty inventory, applied reclaim and no unresolved obligation. Both
members pass preflight before either is marked. Exact replay makes no new marks.
Partial callback failure closes the owner and preserves started/retired progress,
both observations, receipts and any returned diagnostic without resetting history.

All 246 model tests pass, including eight retirement tests with three embedded
source omission controls. The controls detect premature retirement, ignored live
inventory and history reset. A reserved-but-unapplied Cleaned cut explicitly denies.
All ten local gates pass in `run-ngufsiwl` with unchanged checked inputs. All twelve
native consumer sources, three release locks and catalog bytes remain unchanged;
the 185-case native witness remains the runtime checkpoint. This is synthetic
model evidence, not native cleanup, resource authority or a new target run.

Next BG-059: NC-06 terminal-application pending disposition and mixed-phase cut
retirement, still retaining exact receipts/history. BG-057 owns actual journal/
lifecycle/native integration; BG-060 sustained reuse and BG-033 recovery remain
open. No sampling reset, replacement, sustained reuse or recovery API is added.

Review: attachment and callback reentry are guarded; all receipt/source comparisons
use exact retained identities. Inspection is a declared read-only synthetic adapter
operation and is not a native enforcement boundary. Four ownership booleans plus
reclaim/unresolved state have exact type checks. Started is retained before each
mark; failure cannot erase earlier completion or retry uncertain work. Application
receipts stay Applied even when subsequent retirement bookkeeping fails. History
and issuance are retained by leaving the core/source records intact. Python
allocation and trusted adapter assumptions remain explicit. No independent reviewer
sign-off is claimed. Documentation impact: model count/reference, contract limits,
runner source hashes, command inventory, quality coverage and planning handoff.
Evidence: `docs/evidence/cut-retirement-model-2026-09-07/`.
