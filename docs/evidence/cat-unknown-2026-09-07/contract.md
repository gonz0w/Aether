# Unknown reply and local retirement contract

Before code, 2026-09-07. CAT conformance owner commits the first read, write,
diagnostic write or input close, then corrupts a reserved reply byte or sends
only16 reply bytes and closes its response endpoint. Actual channel truncation,
not a local simulated lost-result flag, must poison the adapter. No later channel
trap or owner request is permitted. Local close consumes all bindings despite
poison; repeated closes return EBADF without transport. Status1 (usage64) survives.
Read: positions11/0/0; write:11/11/0; diagnostic:0/0/16; close:32/32/0.
Owner distinguishes remaining aliases (all live except consumed input close),
verifies backend bytes and closes verifier-owned handles only after terminal EOF;
then reclaims client/backend across two generations/four native reclaims.
Never infer remote close acknowledgment from local retirement. Test corrupt/cut
for all four operations; force-zero, omitted-local-close and clear-poison mutants
must reject at1501/1501/1532. No generic timeout/panic acceptance.

Keep kernel/ABI/quotas/pins/UL-059 bundle and sibling files unchanged. Shared
transport adds opt-in test counters only; no unsafe/FFI boundary or dependency.
Fixed borrowed synchronous frames remain. Userland owns Toybox policy and actual
termination; this does not accept CAT-05/06 or upstream callbacks/flush. No new
presentation text. Foundations O/I/E and DEVELOPMENT apply. Full command,
connections/inherited, host/Zig/pins/workflow, Rust2024/Clang21 scoped formatting;
retain all failures and freeze runtime sources during qualification. transport.h
keeps existing legacy formatting for narrowly scoped counter instrumentation.
Update NATIVE-CAT/workflow/STATE with exact evidence and remaining work.

Attempt2 follow-up requirement: the existing pad-launch-eof negative control must
observe the actual parent terminal after its invented padded request admits a child.
Parent EOF may precede terminal observation. In that control only, yield/re-poll
within the existing bound; preserve exact104/970 rejection and all production paths.
No new resource or unsafe boundary. Full source-frozen rerun remains required.
