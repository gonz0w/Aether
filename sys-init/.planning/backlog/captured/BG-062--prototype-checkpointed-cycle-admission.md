---
id: BG-062
title: Prototype checkpointed cycle admission
status: captured
created: 2026-09-07
source_type: research-follow-on
area: native
---

## Release disposition

Shelved for a later release by the maintainer on 2026-09-07. Do not begin this
model under v1; [v1 scope](../../../docs/V1-SCOPE.md) takes precedence.

## Problem and scope

Implement the pure, process-local two-cycle model proposed by decision 0178 and
[BG-060 research](../../../docs/research/SUSTAINED-HISTORY-RETENTION.md).
This tests checkpoint ordering and stale authority without a native reset API.

## Acceptance

- Two independently expected complete pair traces; six active cuts, twenty active
  effect credits, two completion archives; third admission Full without mutation.
- Reserve archive capacity before effects. Preserve exact source/return identity,
  uncertainty and checkpoints through every tested interruption boundary.
- Reject stale owner/cycle/member/occurrence on every mutation path; checked
  counters never wrap. Historical inspection confers no execution authority.
- Test archive exhaustion, partial cleanup, missing returns and outstanding
  reservation/resource/retirement cases. Run targeted omission controls and all
  repository gates; retain sources, commands and failed attempts.
- Declare archive field/count bounds. Separate synthetic model memory from native
  byte/stack costs; record native feasibility work before marking model complete.

Dependencies: decision 0178 research, BG-057/BG-058 native integration; BG-033
retains replacement-owner recovery. No native behavior or production retention
policy is part of this story. Follow-on native integration requires a fresh target
witness within the existing profile or an explicitly coordinated new profile.
