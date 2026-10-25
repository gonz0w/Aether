# Actual dash serial composition

Requirement: real dash consumes host-sent commands through a separately owned UART
backend, forks/execs /next, whose inherited stdin consumes a later host byte, then
waits and exits72. Two shell sessions share one backend/UART grant lifetime. The
backend resets its logical stream handles only after all three closes. After both
sessions, reclaim it and launch its image once more to prove the slot generation
cannot inherit the open UART grant: six reclaims in the unchanged ABI18 profile.

Forbidden: ambient UART in shell/child, EAGAIN as EOF, offset movement on retry,
reacquiring UART by slot reuse, closing the backend while a session uses it,
changing released pins/SDK/siblings, or claiming full R1 from this fixture.
Private reset is a zero 32-byte request, accepted only with all handles closed;
no general service restart/session protocol is adopted. Job control is disabled.

Use existing dispatcher frame retention, and retry pre-fork reads synchronously
where no child exists. No new kernel API, dependency or queue. Preserve finite
watchdogs, frame/span/right validation and no-replay of uncertain replies. UART
inline assembly has synchronous valid stack-buffer spans, no escaping pointers,
no unwind, and uses the existing BSP synchronous grant operations. Rust owns
console routing; C is the conformance/libc boundary, not init/package policy.

SE01–05: synchronous pending reads after fork cannot serve the other caller; use
existing bounded polling. A single backend is simpler than reacquisition and
matches exclusive authority. No general multiplexer, TTY line discipline, job
control or restart framework. One reset operation is necessary for two sessions;
only after explicit logical close, with one authorized channel owner. Existing
frame storage and image/profile bounds are retained; stack high-water remains
unmeasured. No obsolete consumer path is removed in this scoped integration.

Tests: complete connections suite and launch regressions; console ABI18 positive
and wrong-input regressions; host, pin, format and experience checks. New serial
cases require actual command/input exchanges, exact terminal/reclaim inventories,
and a wrong child-input rejection; freeze sources and preserve all failed attempts.
Update shell/console references, workflow for any helper entry point, STATE and
ROADMAP. Shared Foundation O/I/E, scoped TD/TE, SE and existing raw fixture-output
experience exception apply. Interactive/TTY and independent adoption remain open.
