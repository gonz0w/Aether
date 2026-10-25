# 0145 — Aggregate startup and output pipes

BG-056 host slice, 2026-09-07; Foundations evidence rules and the internal
Experience stdout/stderr exception apply. Catch output-root/private-run-directory
creation errors before gates, emit bounded escaped stderr and exit 1 (130 for
KeyboardInterrupt), with no invented report path or terminal summary.

Flush terminal summary output before returning. On output OSError, return failure
and retain the already-published check result; delivery failure does not undo
completed checks. Redirect the failed stream's descriptor to os.devnull where
available to avoid a second buffered failure at interpreter exit. Stderr diagnostics
are best effort if stderr is unavailable. Progress output failure stops further
gates, records gate-progress:<name>, preserves completed checks and publishes fail.
No global signal policy change, child execution change or report schema change.

Use real closed pipes with explicit handshakes and private stub gates; test startup
file conflicts/interrupts and absent diagnostics. Run focused/full checks. Existing
native bytes, historical evidence and release pins remain fixed. Repeated/fatal
signals, descriptor-redirection failure, blocked I/O and crash durability remain
limits; output-root symlink policy is unchanged. No runtime feature is introduced.

Validation: four focused tests, including real closed pipes with handshake and
bounded child cleanup, and all ten gates pass in run-axrwya5u. Four manual
lint/render commands pass; all attempts passed. Native identities/pins unchanged.
Evidence: ../evidence/aggregate-startup-pipes-2026-09-07/.
