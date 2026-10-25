# AEOUT001 remaining startup validation

2026-09-07, before code. Exercise all existing carrier field categories without
changing wire bytes, normal parser behavior, kernel, quotas, pins or siblings.
Add invalid magic/version, missing/excess role count, stale header generation,
header padding, duplicate FD, wrong capacity and record padding. Existing cases
already cover duplicate role, wrong rights and stale record reference. Each full
96-byte malformed carrier must publish neither binding, emit no request, terminate
normally with bootstrap status110, and permit owner backend cleanup plus two
native generations/four reclaims. Malformed startup is not runner CLI success.

A deliberately broken client ignores capacity validation; the independent owner
must reject its first request at1302, not infer rejection from a parent status.
Bounds/identities are checked before any binding publication. Short/truncated
carrier delivery and other extended byte-level cases remain separate coverage;
this is field-category coverage, not fuzzing or exhaustive startup verification.

Scope: Rust owner mutation fixtures, C parser control only, existing command
harness; document exact cases and inventory. No new unsafe/FFI boundary, runtime
allocation, dependency, language or ABI. Rustfmt1.98.0 edition2024 and pinned
Clang-format21. Full command plus inherited-launch/connections regressions,
Zig/host/offline checks, frozen inputs and retained all-attempt evidence. Denied
launches and role/child composition still require their own contract and proof.
