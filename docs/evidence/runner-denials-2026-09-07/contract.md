# Combined roles and denied launches

2026-09-07 before code. Aether-local experimental profile AERIO001: 160 bytes,
32-byte header (magic8,count4,generation,zero16), four 32-byte records with the
AEOUT001 layout. Ordered roles/FDs1..4: runner stdout/write/cap512, stderr/write/
cap256, child-input/read/cap6, child-output/read-write/cap64. Close consumes each.
Runner references retain 0x75000000+(role<<16)+generation. Child-source refs retain
0x71000000+((role-3)<<16)+generation for existing 384-byte launch validation.
Validate all records before publishing any binding. AEOUT001 bytes/profiles stay.
Backend adds one 64-byte child-output record/handle0xf203; existing handles and
private-channel ownership remain. No native quota/kernel/standards pin changes.

Reuse existing validate/admit: absent name returns ENOENT; widened stdin rights
return EACCES; hold one actual channel pair, call admit with valid arguments and
require its actual EBUSY without a native admission. Release the held pair and
probe two available pairs plus third-pair EBUSY, then restore all endpoints.
Exactly one launch request, zero successful admission/collection, exact errno,
untouched input/child output/stdout, exact proposed stderr text, explicit four
closes and normal status2 precede backend cleanup/four native reclaims in two gens.
All errors are independently observed; no fabricated exit2 or diagnostic proof.

Controls: missing/repeated request, wrong diagnostic/reply errno, leaked held
reservation and invalid fourth-role rights. Reject at exact oracle, never watchdog.
Use existing text proposals with verified hashes. No sibling modification, CLI
parsing or consumer adoption. No new unsafe block; larger frames stay bounded
stack slices passed synchronously to existing traps. Rustfmt1.98.0 edition2024,
Clang-format21 for new-header scope; legacy transport style preserved. Run full
command, inherited-launch/connections, Zig/host/offline/format checks; freeze and
retain all attempts, update reference/inventory/STATE. Successful child execution,
denial diagnostic failures, exhaustive carrier cuts and owner review remain open.

Attempt2 resource review: channel slots have a monotonic three-generation budget.
Probe availability only after the second positive denial (reservation generations
1/2, probe3); the leak mutant probes immediately to reject before native reclaim.
Successful second reservation witnesses first cleanup. Do not claim generations
reset, unlimited reuse or relax the kernel limit. Retain both failed attempts.
