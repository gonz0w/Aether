# UL-066 bounded provider review

Prepared 2026-09-07. Recommendation for further userland evaluation; pending
maintainer acceptance. No package installation, native qualification, source-trust
approval or complete POSIX claim. This packet consolidates existing tests; no
runtime was rerun for its preparation. UL-069 emulator/recovery approvals retain
their original scopes and do not imply approval of later UL-066 helpers.

## Recommended disposition

| Requirement | Provisional candidate | Evidence and reason | Remaining boundary |
| --- | --- | --- | --- |
| BP-24 awk | mawk1.3.4-20260302 | Static musl build,50 upstream groups,FPE suite and11 package consumers; One True Awk/gawk remain alternatives | Native file/process/pipe behavior, regex/resource bounds, source/release review |
| BP-26 tr | GNU coreutils9.11 |17 common fixtures,134 upstream cases plus failure control; BusyBox retains four common-fixture differences | C-locale byte scope; true ISO-8859-1 unavailable with this musl profile; UTF-8 needs separate cases |
| BP-25 stty | GNU coreutils9.11 | Row/column,invalid input,full option pairs and independent PTY recovery; static cfsetispeed caller-error witness | Native TTY/session authority, natural upstream main-script cleanup, later-stage fault coverage |
| Comparison provider | BusyBox1.38.0 |13/17 common matches,5 focused and5 legacy upstream scripts; failure controls reject | Repeat/print-class/invalid-class/reversed-range differences remain; no substitution as general tr |

This retains existing evaluation order, not a final distribution manifest. GNU
tr/stty and shared gnulib are GPL-3.0-or-later with per-file notices; mawk is GPLv2;
BusyBox's distribution LICENSE is GPLv2-only with retained source/test notices.
Recipes do not relicense payloads. None is ranked a security or performance winner.
Linked archive size and language labels are not measured attack surface or runtime
cost. Dependency/maintenance/security-fix review remains UL-016 and UL-011.

## Evidence and exact limits

- [Mawk](../evidence/mawk-musl-2026-09-06/summary.json): historical image-QEMU run;
  not rerun with the corrected emulator. The50 count is groups, not assertions.
- [Corrected-emulator consumers](../evidence/qemu-consumer-regression-2026-09-07/README.md):
  GNU17/17,BusyBox13/17,GNU upstream134 plus exit99 control,BusyBox focused5.
  Option pairs exit0 and restore exactly; all9029 traced calls remain.
- [Recovery](../evidence/qemu-recovery-2026-09-07/README.md): main script exits0
  but natural restoration stays false; explicit recovery passes after normal exit,
  nonzero exit and timeout. Omitted-recovery control detects changed state.
- [Legacy](../evidence/busybox-legacy-2026-09-07/README.md) and
  [range disposition](../evidence/tr-ranges-2026-09-07/README.md): five script exits0
  and five controls reject. The supplementary ROT13 expectation was wrong;
  eight comparisons establish literal bracket behavior in both providers.
  Historical INCOMPLETE remains intact; it is not a new provider defect.
- [Static speed](../evidence/stty-speed-2026-09-07/README.md): original-equivalent
  baseline plus failure/pass-through fixtures pass three PTY cases. Failure is
  during argument validation. Upstream LD_PRELOAD script itself remains NOT RUN.
- [Locale](../evidence/candidate-locale-2026-09-07/README.md): ten observations show
  ISO-named and invented musl locales report UTF-8. Installing host locale data
  cannot qualify candidate ISO behavior. Name acceptance is not encoding support.

A failed stty operation does not guarantee unchanged state: the direct partial
cmspar+parenb witness retains CMSPAR while rejecting PARENB. BP-25 now requires
failure reporting, independent state observation and explicit restoration.
No new atomic-rollback implementation contract is imposed. The main script's
natural cleanup still fails its original oracle; successful recovery is separate.

## Review scope and engineering record

Requirement: consolidate UL-066/BP-24–26 recommendations and exercised limits.
Quality DW/DP/TD/TE and Foundations evidence/ownership rules apply. No new shared
standard, native authority, package/service API, tool pin or production source.
Changed surfaces: this packet, base-program matrix, contributor README, coverage,
BACKLOG and STATE. Artifact roles and runtime budgets remain in linked plans.

[Evidence inventory](../evidence/provider-review-2026-09-07/inventory.json) hashes
selected retained summaries and current source/plan snapshots. Current later-helper
bytes match their retained evidence; historical summaries are references, not
fresh runtime. Archive hashes for all five provider research inputs are verified.
Any changed candidate, SDK, emulator, helper or requirement invalidates relevant
reuse. No source authenticator or security-fix freshness is inferred from hashes.

This documentation change uses source/evidence identity checks and the quality
gate. It does not need repeated runtime tests because no execution behavior changes.
Technical reviewer and separate reader walkthrough: pending for this packet and
new legacy/range/speed/locale helpers. Earlier user approvals apply only to their
recorded SDK/emulator/consumer/recovery slices. No new approval is inferred.

## Acceptance and follow-ons

Review whether the recommendations match actual package needs, each result's
layer and limitations, licensing/dependency assumptions and every retained failed
attempt. In particular inspect the later helper oracles and the two corrected
supplementary assumptions before accepting the bounded reference comparison.

UL-066 stays active pending this disposition. Any acceptance must preserve:
UL-016 source authentication/update ownership; UL-011 final utility selection;
UL-007/008 native process/TTY support; UL-012 packaging; UL-013 explicit locale/
POSIX subset and UTF-8 cases; UL-061–063 remaining inventory/source/reader review.
Do not require an ISO profile merely to clear an inapplicable upstream branch.
If it becomes a product requirement, select a compatible candidate/libc explicitly.
