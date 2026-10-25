# UL-075 — dash import auditor process boundary

Scope: experiments/dash-reference/audit-imports.py host object inspection only.
Review found unbounded check_output, inherited cwd/environment, no owned descendant
cleanup and assertions guarding pins/empty input. Preserve the libc-imports.json
keys and symbol subtraction, silent success and existing positional build argument.
No dash rebuild, Linux guest/native run, sibling change or standards pin update.

Apply CP-01–03, Foundations E-01–08 and local UL-063 requirements. Reuse the
unchanged command-runner process helper with explicit build cwd, minimal environment,
30-second per-tool wait and 1 MiB per-file output bound. Retain separate streams and
cleanup receipts in a fresh private build directory. Reject incomplete execution,
nonzero status and empty object input; pin checks must also work under Python -O.
No hostile session-escape, owner-SIGKILL, filesystem race or total-suite bound claim.
The caller supplies a trusted private build tree; normalization is not confinement.

Validation: synthetic symbol subtraction, wrong pin before execution, empty input,
nonzero exit, timeout/descendant cleanup and output exhaustion. Retain all attempts.
Run controls on qualified 3.10.21 and current 3.14.7. Compare full symbols/object
hashes with retained original report using copies of the original objects. Run
local quality gate and whitespace checks. No native regression needed for host-only
inspection. Record script/helper/tool hashes, argv, platform and raw logs. Independent
review of this new change remains pending; previous maintainer approval does not
cover it. Track remaining dash build/test remote-container lifecycle separately.
