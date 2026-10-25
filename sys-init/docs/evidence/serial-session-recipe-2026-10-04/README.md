# Maintained offline serial-shell candidate recipe

2026-10-04, decision0185/BG-067. New maintained command and lock rebuild the
repaired ABI24 owner from current source and compose exact sealed009 inputs.
Released standards pins, ABI22 behavior and sibling repositories are unchanged.

Fresh immediate and 35-second delayed consuming witnesses pass exact 90 UART
bytes, eight admissions, ten terminal identities/reclaims and owner-authorized
halt. Rebuilt raw/ELF bytes match the qualified repaired owner; the scoped
3816/4088-byte stack inspection is reused only on exact parity. All six boot
components read back exactly, including unchanged client/spare/entropy prefix.
No kernel/client rebuild or full toolchain closure is claimed.

Focused tests cover archive membership/links/aliases/hash/budget, envelope bounds,
output ownership/traversal, changed/missing inputs, retained tool failure/timeout/
cancellation, CLI exits, unchanged producer oracle and semantic trace mutants,
and real early native exit/reaping. Earlier intermediate test failures are
summarized in development-failures.json (initial raw log was not saved): corrected
fixture trace path and avoided signalling an already exited native process. The pre-hardening immediate witness is retained.

See validation/ for full local checks and sources/ for the checked maintained
snapshot. Artifacts and notices are retained in artifacts.tar.gz with exact member
metadata. sha256.json seals the final packet and is checked by readback.py.
Independent assembled review, further mismatch/exhaustion/unknown-cleanup
qualification, finite capacities, fatal/repeated signals, detached tools,
filesystem races/deadlines and manual console freshness remain limits.

All ten local gates pass in validation/results.json, with sources unchanged. Nine
focused tests pass. Build-only succeeds without a smoke claim. Real missing-tool
and existing-output CLI controls exit2 before creating output; existing artifacts
are preserved. No release authorization or independent sign-off is inferred.
