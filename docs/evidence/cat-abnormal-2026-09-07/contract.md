# Abnormal terminal and owner cleanup

Before code, 2026-09-07. Conformance client executes intentional x86 UD2 after
validated startup, first committed copy write, or first diagnostic write. Require
native detail134/kind2, exact positions0/0/0,11/11/0,0/0/16 and no local finalization.
Owner-forced stop after first committed output write requires live reclaim EBUSY,
stop success and detail143/kind3; repeat stop retains identical terminal observation.
Do not send the outstanding reply after stop. Request EOF and all remote aliases
still live must be observed before verifier-owned backend closes/stale denial and
native reclaim. Two generations/four reclaims, then stale child poll/stop/collect
must reject EBADF. Input bytes stay unchanged and output prefixes are exact.

Normal _exit134 substituted for a fault must reject1501; wrong forced-stop kind
must reject1501; corrupted copied prefix must reject1505; skipped backend close
must reject1506. Preserve exact panic contexts, not generic panic acceptance.
Test-only UD2 has no pointer operands and never returns; volatile instruction plus
unreachable terminates only the isolated conformance client. No production unsafe
boundary, kernel/ABI/quota/dependency change. Existing private authority stays with
owner; userland/sys-init retain production termination/supervision policy.

Foundations O/I/E and DEVELOPMENT apply. No new presentation text, pin/bundle or
sibling change. Freeze sources and retain every failed attempt. Full command,
connections/inherited and host/Zig/pin/workflow/Clang21/Rust2024 checks; update
NATIVE-CAT/workflow/STATE with scoped evidence. Not Toybox callback/flush acceptance.
