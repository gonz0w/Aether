# 0111 — SIGTERM during active aggregate capture

BG-056 host harness change, 2026-09-06. SIGTERM currently uses default process
termination, bypassing aggregate cleanup. During a main-thread run_check capture,
install a temporary SIGTERM handler that raises KeyboardInterrupt. The existing
interrupted result, SIGINT grace, forced fallback and aggregate exit 130 then
apply. Restore the prior handler in finally. Secondary SIGTERM during cleanup is
ignored; unrelated signal dispositions remain unchanged. Background-thread calls
retain their prior signal behavior and do not install process-global handlers.

The handler is installed only after the gate process has been created and while
capture owns it. Startup/Popen windows, between-gate/hash/report work, SIGKILL,
repeated SIGINT, detached/unresponsive/deeply nested owners and pipe-pressure
limits are not claimed fixed. No native code, pinned release, sibling repository,
CLI flags or result schema change. Ordinary SIGTERM previously could terminate
without a report; in this scoped active phase it becomes interruption, exit 130.

Use a real SIGTERM to an owned aggregate process after a nested worker readiness
handshake; require interrupted result, nested child reap and restoration of the
old SIGTERM disposition. Test normal and failed capture restoration plus existing
cleanup/runner controls. Retain the expected pre-fix failure and perform fixture
cleanup. Run all repository gates and update the aggregate manual/adoption record.
Evidence: docs/evidence/aggregate-termination-2026-09-06/README.md.

Validation: three new signal/restoration/thread tests, fourteen prior focused
tests and all ten gates pass in out/checks/run-pe9urad8. Default SIGTERM changes
from -15/no result to the probe's 130/interrupted result with nested cleanup.
The fixture's initial import typo and custom-handler iterations are retained.
Manual lint passes; all 24 native inputs and the inner helper remain unchanged.
