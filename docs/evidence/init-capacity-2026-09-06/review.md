# Scoped self-review

Independent reviewer and sys-init acceptance remain outstanding.

- Distinct magic and ABI select only capacity; init factory/observation roles and
  worker/supervisor slots remain v1-compatible apart from explicit ABI validation.
- All untrusted u32 lengths are bounded before sum/slice. Old magic keeps 4096.
- Existing loader zeroes code backing, maps actual page count RX, maps a distinct
  NX stack and removes writable code aliases in every kernel view before entry.
  V2 checks both page permissions/aliases and tail zero, with a dirty-tail mutant.
- V2 fixtures place their entry at 0x401000 with a first-page relative jump. The
  entire real init workload therefore executes through page two; exact-boundary
  first-page cases and second-page protection faults are separately identified.
- Existing all-domain owner-death sweep covers all backing including both code
  pages; no recovery or normal-completion supervisor reclaim is invented.
- The initial NX oracle failed on hex/decimal formatting despite correct hardware
  fault and cleanup. It is retained; corrected exact fault assertions are required.
- Baseline native ABI 6 regression and distinct v2 completion markers remain;
  sys-init must independently pin and rerun 151 plus new guard cases.
