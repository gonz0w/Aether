# 0124 — Active standards capture termination

BG-056 host slice, 2026-09-07. During main-thread reference capture, map SIGTERM
to Python interruption so existing owned-group kill/reap and temporary-directory
unwinding run. Install only after Popen returns; ignore secondary SIGTERM during
capture cleanup and restore the previous handler afterward. Background-thread
calls retain their existing signal policy. Catch CLI KeyboardInterrupt as exit
130 with a plain stderr diagnostic, covering ordinary SIGINT as well.

Test real SIGTERM after a child readiness marker, child reaping and staged-tree
removal; handler restoration and background-thread calls. Run focused and full
checks. Preserve released pins/native bytes and successful output. E-01–08 and
existing internal diagnostic scope apply; no new dependency or shared ABI.

Startup/Popen, staging, postchecks, output replay and temporary cleanup after
handler restoration are not a broad termination guarantee. Repeated signals,
SIGKILL, escaped descendants and blocked I/O remain outside scope. Independent
review remains pending. No claim of atomic cleanup or full containment.

Validation: twenty-four focused tests pass (20 standard tests and four lock tests).
All ten gates pass in out/checks/run-81w8wpg7. Three real standard stdout streams,
lock bytes and 24 native inputs stay unchanged. Twelve manual commands pass.
Evidence: ../evidence/standards-termination-2026-09-07/README.md.
