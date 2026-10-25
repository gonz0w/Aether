# UL-058 NB-02 native reply controls

Before code: add --reply-controls using the separately reviewed producer pin.
Test-only link wrappers consume a complete actual read/close reply, then discard
its final return or corrupt its metadata. Read destination stays unchanged;
uncertain close consumes locally once. Real musl errno plus channel-call counters
must prove no further file, launch or collection exchange. Successful witness
child 84, parent53, broker970/reclaimed0; no success marker or remote recovery claim.

One private adapter mutation removes the transfer poison guard. A test wrapper
catches the first forbidden channel call before issuing it and exits94, then
parent53/broker970 must reject. This tests detection of an attempted replay without
letting the deliberately broken client create ambiguous extra service traffic.
Run all nine ordinary cases plus four NB-01 and four NB-02 cases (17) on the new
producer, nine default old-pin regressions and 21 host checks. Verify five original
ELFs unchanged. All new ELFs inspected and require real musl read/write/close.

Existing Clang/LLD C17, Rust/Zig/QEMU/SDK pins and process ownership bounds apply.
Thirty-second guest watchdog, 180-second build/owned wrapper, 15-minute suite.
No ordinary adapter/owner code, protocol or default pin change. Preserve every
attempt, exact sources, injection ordinals, receipt bytes/digests, markers and
cleanup. Current task technical review; independent review and NB-03/04 pending.

Actual technical review: current task reviewed accumulation over synchronous
32-byte reply buffers, injection ordinals 1/3, record metadata corruption, errno
and sentinel checks, consuming closes and guard mutation. Before/after adapter
hashes are unchanged; nine old client ELFs identical. Exact native exits verify
all four controls, with 17 new-producer and 9 original regressions plus 21 host cases
passing. Formatting/Python grammar pass. No failed runtime attempt. Existing
receipt scope wording was generalized from five clients to source-rebuilt clients
to reflect optional witness sets. Independent technical/reader review pending.
