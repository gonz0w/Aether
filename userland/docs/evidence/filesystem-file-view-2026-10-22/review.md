# UL-007/081/082 authoritative file view v1 review

Requirement: sys-init Decision0202/BG-071 needs exact read-only FILE presence and
cloexec for thirteen remote selectors before copy. Supply equivalent bounded
metadata from the sole ProcessFiles ledger, not a request-trusting validator.

Plan before code: additive file_view_v1 under exact current opaque Process key;
return (presence, cloexec) u16 masks with bit n denoting remote FD n, only3..15.
No persistent state, source callback, native call, flag normalization, exec probe,
new ledger, protocol, dependency or policy. Owner must compare BOTH masks exactly
under its exclusive admission gate before copy; unused bits, omitted/extra slots
and flags on absent slots therefore mismatch. Inspection does not authenticate
client bytes or validate streams/source history, nor authorize native operations.

Ownership/error review: active/exact key before private view read; stale/foreign
keys and retired source keep existing ProcessError identity. Thirteen bounded
iterations and four bytes of inert result, no heap; &self cannot alter parent or
retire source on mismatch. Owner retains exclusive &mut access from preflight
through copy and handshake. Snapshot ceases to be authoritative after mutation.
Old APIs/candidates and entry/defaults remain unchanged.

Validation plan: extend existing actual Rust AF07/Owner process fixture with
empty/full/holey/one-bit flag views, same shared offsets/different flags, stale/
foreign/replacement identities, known denial, unknown retirement and synchronous
copy/refusal outcomes. Verify no source requests or closes during inspection,
parent flags/offsets unchanged, capacity and all four views. Retain prior26tests,
10semantic omissions, borrow rejection and external host/target builds; add
compiling metadata omissions. Strict pinned Rust2021/rustfmt/default Clippy,
unsafe forbidden, generic no_std x86_64-unknown-none. Actual Python3.10/current,
quality gate and every attempt retained. No guest/native witness or full fit.

Standards: O-01–05/I-01–06/E-01–08, applicable approved CE/CD/CA/Rust/CP,
TD/TC/TE and documentation DW/DS/DM; Distribution NC/PX/SV/FS/EV scoped by local
applicability map. Pins/dependencies unchanged; BSD-2-Clause original work.
Simpler alternative: export two masks directly; chosen because it provides all
requested metadata without a new claim/error framework. Existing position API
cannot expose private flags. Removes need for a duplicate descriptor mirror or
destructive exec probe, adds no service machinery. Review by implementation
agent only; affected-owner and independent reader acceptance remain pending.
Full UL-007/082/M3/R1, whole fit/native transaction/exec/dup2 remain open.

Actual results:31tests/13controls on minimum/current, default8tests/11controls,
external host/target consumers and borrow-reentry denial pass. Initial pass before
private-helper cfg retained; final sources support both process/default profiles.
No source requests/close or offset/flag effects from export; no empty-success on
stale/unknown. Owner comparison remains disabled until matching consumption; no
owner/reader sign-off inferred. Existing stage81/full-link evidence reused only
for unchanged C sources; no C/runtime/full shell rerun justified by this Rust seam.
