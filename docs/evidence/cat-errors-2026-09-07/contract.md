# Complete-error replies and cleanup contract

Before code, 2026-09-07. Extend the direct AECAT001 conformance client only.
Read/write EIO after one successful 11-byte transfer must yield status1, preserve
exact input/output prefixes, stop further data requests and still consume all
three aliases. Diagnostic EIO after16 committed bytes retains usage64, no input,
empty stdout and exact diagnostic prefix. Complete zero-padded close EIO confirms
consumption in this opt-in protocol, permits cleanup of remaining roles, promotes
zero status to1 and retains usage64. Exercise each close role and usage close.
Malformed/lost replies, EINTR, Toybox callbacks/flush and actual SDK adaptation
remain separate; these cases do not accept CAT-05/06 for userland.

Owner injects precisely one EIO at the named request before forwarding it (close
consumes owner alias first). Require the injection actually occurs, no later data
requests, exact positions/readback, all closes, terminal EOF, backend stale denial,
four reclaims in two generations. Mutants force success, skip close or retry failed
write; require exact owner1501/1503/1530 respectively. No generic panic acceptance.
No new diagnostic text, kernel ABI, quota, dependency, unsafe boundary or authority.
Borrowed synchronous frames and fixed per-owner state remain. A complete close
EIO confirms only alias consumption, not backend destruction/native reclamation.

Affected: CAT_ROLES adapter/owner/client and shared transport header; existing
RUNNER_STREAMS semantics and other profiles remain. Userland owns final Toybox,
mask, stdio and termination policy. Foundations O/I/E and local DEVELOPMENT
require frozen sources, all-attempt retention and source/artifact identities.
Select full command-runner, connections, inherited-launch and zig build test;
scoped Rust2024/C Clang21 formatting, workflow/pin checks. Retain old pins/UL-059
bundle; no sibling edits. Update NATIVE-CAT, workflow and STATE with scoped evidence.

Formatting scope: cat-client.c uses the approved Clang21 config; cat-roles.rs uses
Rust2024. The shared transport.h retains its existing compact style for this
conditional/comment-only change; whole-header migration is separate.
