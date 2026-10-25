# Experimental host release plan

> Scope update, 2026-09-06: Aether is the only release target. This document
> preserves the earlier host-preview work; its macOS release/setup gates are
> superseded by [Aether release acceptance](AETHER-RELEASE.md). Host results remain
> development evidence and are not native package-manager acceptance.

Status: active preparation, not a publication approval. Candidate name:
`pkg-mgr 0.1.0 experimental host preview`. The maintainer authorized this work.
The first qualification target is the current macOS arm64 host with GNU Make;
record the exact OS/tool versions in candidate evidence. Linux/BSD are future
qualification targets, not inferred support. The release source must include
all files needed without sibling checkouts after separately documented setup.

## Promised scope

Build pinned local recipes, stage into initialized private roots, register and
inspect records/world, verify ordinary file contents/modes, export/import local
binary directory bundles, compare replacements and perform retained private-root
replacement/recovery. Ship the existing CLI and matching offline documentation.
Use hello-local for the compiler-free tutorial and bytecount for the real compiler
workflow; include zlib/zpipe only after their source/license/build closure is qualified.

No native package-manager execution, real-prefix installation, remove/prune, daemon,
concurrent writers, hostile filesystem-race resistance, remote repository eligibility,
power-loss durability, service activation or broad POSIX support is promised.
Native transport experiments remain separately labeled development tools and evidence.

## Ordered acceptance work

| ID | Work and independent acceptance | Current state |
| --- | --- | --- |
| HR-01 | Freeze scope/platform and enumerate CLI, formats, shipped sources, docs and dependencies | 187-file public candidate allowlist implemented; independent content review pending |
| HR-02 | Review shell findings and parser/path/transaction boundaries; resolve actual defects, narrow reviewed exceptions only | All 38 active shell files pass configured lint; three scoped exceptions documented; snapshot hash status and preflight producer/sort failure propagation fixed; record comparison errors and replacement intent and binary descriptor and final preflight hash and binary metadata-reader failures now fail closed; broader boundary review remains |
| HR-03 | Whole-suite watchdog and semantic controls proving timeout, child cleanup and nonzero propagation | Implemented; six process controls plus completion controls and full-suite witness pass |
| HR-04 | Bounded malformed-input corpus/fuzz runs and repeated transaction/recovery cases, with seeds, deadlines and retained failures | Partial-copy/rename controls, 71 source-record corpus cases, eight hash-tool faults, twelve preflight producer/sort faults six record-comparison errors and ten replacement intent hash failures and nine binary descriptor hash failures and four final preflight hash failures and thirteen binary reader failures added; three transaction-fixture runs pass on the refreshed candidate; broader fuzz/soak and actual full-storage qualification pending |
| HR-05 | Accurate manual/options/format coverage, onboarding and recovery examples; lint/render plus independent reader walkthrough | CLI/state/binary manuals and initial public-package render/example/lookup witness pass; independent walkthrough and each changed candidate need qualification |
| HR-06 | Clean source artifact and pinned setup; independent clean-checkout offline build and supported-host workflows | Explicit public inventory and initial extracted-candidate checks pass; qualification is archive-specific; original Apple installers unavailable; newly captured builder/setup and independent clean-candidate witness required |
| HR-07 | First/third-party license inventory, provenance, actual monitored security contact and triage owner | Component/notice review and exact public allowlist recorded; monitored contact and independent review pending |
| HR-08 | Bind candidate hashes, tests, defects, scope, recovery docs and real reviews; explicit publication decision | Blocked on preceding gates |

The pkg-mgr maintainer owns triage and acceptance; no reviewer identity or contact is
invented. Technical, independent build and reader reviews require actual people/results.
Shared draft content approval does not supply these witnesses. Required missing tools
and evidence are blocked coverage. No release tag, upload or signing occurs implicitly.

Run `sh tests/check.sh` for the development suite; record the retained run evidence.
Select additional checks through [the development process](DEVELOPMENT.md). Each
candidate change invalidates affected evidence. Fix failures before collecting a fresh
run; preserve prior attempts. No elapsed-time estimate substitutes for passing gates.

Current work and next actions stay in [STATE](../.planning/STATE.md) and
[ROADMAP](../.planning/ROADMAP.md). This document owns release scope/acceptance only.

[Development source snapshots](SOURCE-SNAPSHOT.md) provide an explicit local input
manifest and relocated validation path. Their included history is not a selected
public release inventory.

[Content/notice review](RELEASE-CONTENTS.md) and [installed-host preflight](HOST-SETUP.md)
separate development snapshot closure from public-content and tool-setup qualification.

[Public candidate assembly](PUBLIC-SOURCE.md) uses an explicit allowlist and records
its documentation edition. Each candidate is identified by its own archive hash;
later documentation/checkpoint changes are not covered by an earlier archive run.
