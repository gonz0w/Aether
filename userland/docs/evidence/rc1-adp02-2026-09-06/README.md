# RC1 / ADP-02 review evidence

2026-09-06, UL-070. For maintainers checking the unpublished standards review.
The authoritative findings and exceptions are in
[the local review](../../quality/RC1-ADP02.md). No runtime change is under test.

## Change review and test plan

- Purpose: account for RC1/ADP-02 applicability and route missing work to UL-061–063.
- Scope: documentation, profile-qualified clause inventory and preserved input/check
  evidence. No sibling modification, release-pin update or post-R1 implementation.
- Requirements: DW/DS/DP, TD-01–03, TC-01, TE-01–06, CA-01–03 and EV-01–05.
  The complete review register covers 116 new-profile clauses separately.
- Authority/lifetime: copy review inputs locally, verify the complete archive before
  executing copied reference checkers, run only in owned build/temporary roots.
  Existing ABI, capability, package/service authority and runtime markers unchanged.
- Tools: Python host standard library and existing owned-process helper; exact
  executable/environment identities are in each process receipt. No dependency
  provision, native compiler upgrade, runtime build or network fetch is requested.
- Selection: local quality gate (all three baseline checks plus snapshot/inventory
  control); release preflight must reject incomplete inventory; isolated RC1 offline
  reference checks; clause/link/input identity and changed-doc whitespace checks.
  No unrelated native tests: no native code, build flags or interfaces changed.
- Limits: quality checks 120 seconds each, candidate 240 seconds, owned process
  groups with cleanup verification, 16 MiB per output file; temporary output under
  build/rc1-review. Tool availability is reported, never inferred.
- Oracles: exact expected exit status and gate-specific output; incomplete release
  coverage is a release blocker, not a release pass. Candidate synthetic examples
  cannot certify userland. Missing strict render/tool checks stay unqualified.
- Documentation: RC1-ADP02, clause register, standards/process navigation, ID-05
  baseline map, coverage inventory and local BACKLOG/STATE.
- Reuse: prior component evidence is reviewed for scope only and not rerun/promoted;
  referenced result hashes are captured. The 97-file prior review snapshot matches
  the candidate exactly; current release and draft pins are preserved.
- Review: current Codex task technical assessment only. Independent technical and
  reader walkthroughs and affected-owner native acceptance remain pending; structured
  owner-review/adoption records contain no invented approvals.
- Retention: all execution attempts and final results retained here, source snapshots
  in inputs, full candidate archive plus ARTIFACT identity, checksums in SHA256SUMS.
  Changed authoritative files are bound in local-files.json; this packet does not
  hash itself recursively. No retention cleanup or release authorization is implied.

## Results

See [results.json](results.json) for actual checks and raw process receipts/logs.
The final completion decision is recorded in userland STATE and the local review;
UL-061–063 and native UL-059/067 remain open. Run the normal offline gate from the
repository root with `python3 -B docs/quality/check.py`. For candidate rechecking,
verify this packet's SHA256SUMS first, then use its copied checker and archive;
its integrity-only invocation is:

```sh
python3 -B docs/evidence/rc1-adp02-2026-09-06/inputs/tools/check-candidate.py
```

Add `--run` for isolated offline reference checks. These do not change consumer pins.
