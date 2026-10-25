# UL-059 native collected-result mapping

The opt-in parent uses the tested admission/collection decoder, keeps receipt
and raw terminal facts separate from cleanup, and calls terminal policy only
after a validated collected reply. It sends one launch, retries collection only
after a validated pending reply, and aborts unknown/malformed/error/budget outcomes
without replay. Close3 occurs once after admission; output EOF and close4 occur
after collection. A failed close does not overwrite raw terminal facts. These
aborts are bounded experiment behavior, not accepted public precondition exits
or an unattended recovery service.

The pinned producer enables runner_startup plus mapped_results only for the new
cases. Ten positives cover normal0/1/2/64/125/126/127/134/255 and actual invalid-
instruction fault134/kind2 mapped to parent1. Link-only child wrappers terminate
after unchanged bytecount produces actual output but before closing aliases.
The producer independently verifies backend bytes/positions, collected results
and alias cleanup: two generations, six reclaims per positive. Raw child terminal
records remain distinct from parent exit. Parent imports musl read/close but no
write, so it adds no stdout bytes. The default finite parent29 remains intact.

Three exact controls pass:
- Ignored fault kind: child kind2/detail134, incorrect parent134, broker970.
- Forced zero: child normal64, incorrect parent0, broker970.
- Local cleanup report: actual close4 succeeds, wrapper returns EIO; the policy
  wrapper checks child0/kind1/receipt and cleanup=false remain intact. Parent1 and
  broker970 reject the mismatch. A missing/raw-corrupt hook observation would
  instead exit91 and fail this oracle. This is not a failed remote close witness.

All47 combined native cases and nine original-pin cases pass. The28 prior client
ELF hashes are identical;14 new clients pass static ELF/TLS/NX/no-WX/no-interpreter/
no-Linux-syscall checks. Native normal detail is eight-bit bounded; wide detail
and stopped-kind policy remain host-only. Native mapped-path malformed/unknown
reply controls are still a follow-on; earlier adapter and pure decoder witnesses
are not a claim of complete end-to-end coverage for that path.

The initial compile-only build passed but unnecessarily linked bytecount into
mapped parents. This was corrected before boot testing, with exact initial source
hashes/snapshots retained. The final native run passed first attempt. Result28159
assertions/four mutations, parser1293/two mutations and21 host command cases pass.
Strict mapped C17 and new-wrapper diagnostics, format, Python3.10 grammar (actual
3.14.7) and the quality/three-standards gate pass. No new runtime dependency,
producer source, standards pin, pkg-mgr state or sys-init policy changed.

`native/` and `legacy/` retain raw command/serial/cleanup records and owner artifacts;
client directories retain inspected ELFs/maps and build receipts. Large boot images
and isolated checkouts remain under the listed build roots. `initial-build/` and
`build-attempt-1-sources/` retain the earlier compile; host and quality directories
retain their actual logs. Sources, diffs, carrier bytes, compiler/SDK/runtime and
process environment identities are pinned in receipts; current documents are
snapshotted separately. Native commands retain180s owned deadlines, guest30s/no-NIC
isolation and512MiB per-output-file limits; host30s/16MiB, quality60s. Those are not
global memory/disk or performance claims. ASan remains incomplete as recorded in
prior evidence; selected host sanitizer is UBSan.

Current-task technical review by Codex checked decoder outcome dispatch, receipt
lifetime, raw facts through cleanup, pending-only bounded polling, no output write
and independent owner rejection. Separate technical/reader and full affected-owner
reviews remain pending. Foundations O/I/E, Experience exit policy and approved
CE/CC/CP, TD/TC/TE and documentation process apply. Affecting input changes invalidate
reuse. Next UL-059: concrete zero-admission/local-output lifecycle handoff and
mapped uncertainty controls. No installed CLI, recovery, shell/TTY, package or
sys-init acceptance follows from these scoped witnesses.
