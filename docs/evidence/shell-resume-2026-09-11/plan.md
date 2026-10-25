# Return to the serial prompt

Requirement: keep actual dash alive after /next exits72, return a second prompt,
then accept a separately host-sent `echo $?;exit N` command. Require output72,
parent exit0 in session1 and7 in session2, final shared closes and six reclaims.
The child still consumes host a. One UART backend spans both sessions. No second
external-child admission, indefinite waiting or general TTY claim in this step.

Fix the private driver cleanup gate: a healthy initialized parent identified by
its captured PID may close published descriptors for any normal exit status;
poisoned/uninitialized transport must not initiate cleanup. Copied child error
paths retain the previous gate. No new SDK or kernel API. The owner remains a
conformance witness checking the two externally chosen statuses, not an init
policy. Existing serial one-line command modes remain unchanged regressions.

Forbid premature shell exit, stale/false wait result, skipped final closes, UART
leakage, false EOF and source drift. Positive host sequencing requires child72,
a new prompt, then a later command; no preloaded exit script. Controls keep the
old cleanup gate (parent0/owner2131,zero reclaims) and choose wrong exit8 in the
second session (parent8/owner2130,two reclaims). Full connections, launch and
console/profile regressions plus host/format/pin/workflow checks are selected.

SE01–05: reuse the existing dispatcher, private transport health and PID identity;
no new session engine, kernel queue, protocol or process table. Removing exit-code
policy from healthy parent cleanup addresses a current lifecycle bug. Captured
PID only distinguishes the original driver from its copied child; it grants no
authority. Fixed statuses remain solely in conformance oracles. No new unsafe/FFI,
dependency or resource quota. Finite watchdogs, one child per session and healthy
normal-exit scope remain; cancellation and fault recovery are separate.
Update shell reference, existing workflow, STATE and ROADMAP. Shared Foundation
O/I/E, scoped TD/TE and SE rules apply; preserve all attempts and immutable pins.
