# I/O worker tool-bound evidence

Decision 0097 closes the older I/O worker builder duration/output finding.
Tools now have 180-second and 4 MiB bounds, owned process-group cleanup, retained
log prefixes and per-attempt running/pass/fail/timeout/output-limit/infra-error/
interrupted records. All four retained/readiness/authority/peer profiles rebuild
from verified offline SDK/tools to identical worker ELF and envelope bytes.
No new native execution is claimed or needed for identical artifacts.

Six real runner tests cover success/nonzero, missing tool, timeout and overflow
across both worker builders. All ten aggregate gates pass in
`out/checks/run-fcjtshwd`; native inputs and release pins are unchanged.
Other older supervisor/lifecycle builders, complete Python/C path review,
extended scheduling and independent technical/reader review remain open.

`results.json` records all four original commands and exact ELF/envelope
comparisons. Per-profile directories retain captured inputs, tools, logs and
tool-attempts.json. `build.py` records SDK reconstruction from already verified
retained input bytes; no mutable sibling SDK is used. `validation/` retains the
complete offline checks. Existing historical evidence is unchanged.
