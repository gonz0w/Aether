# UL-067 current revision regression review

- Scope: full 213-case existing producer command regression on the already captured
  close-policy snapshot. No new runtime behavior, test oracle or sibling edits.
- Reason: two common runtime sources changed (cat-roles.rs, toybox-cat-probe.c).
  The owner change replaces the unknown/injected traffic guard with an uncertain
  state guard, affecting older error scenarios as well as new opt-in close cases.
  Prior local213 evidence cannot establish current owner compatibility.
- Rules: Foundations O/I/E, approved CP/TD/TC/TE/evidence requirements. Exact
  tool/SDK/intake identities verified before use, source rechecked after execution.
- Driver change: optional explicit execution receipt selects the current captured
  Rust wrapper pin; original finalizer discovery default retained. Missing/mismatched
  receipt or wrapper cannot pass. No subprocess ownership or timeout changes.
- Lifecycle: existing owned 1800-second outer command, captured guest watchdog and
  producer command bounds. Private build outputs; no prefix install/network/cleanup
  of historical artifacts. Require all213 cases and complete outer process cleanup.
- Reuse: captured SDK/LLVM/Rust tools and existing recipes; no claim to rebuild
  libc/CRT here. Actual-applet27 evidence retains its own scope. Full command suite
  includes conformance fixtures, not 213 executions of upstream cat_main.
- Technical reviewer: Codex inspected the two runtime diffs, wrapper selection and
  existing pass/count/source/cleanup checks. Independent technical/reader review
  pending. Current results will be retained with raw logs and source identities;
  incomplete or failed outcomes must not be marked accepted.
- Documentation: CAT matrix, backlog/STATE, coverage and dated evidence updated on
  completion. UL-007 native shell still awaits producer identity/signal/FD support;
  UL-067 complete matrix/review and release source trust remain separate gates.

Final result: PASS, all213 cases on the current close snapshot, unchanged input
inventory and complete outer cleanup. No failed attempt. This resolves current
CAT-08 command regression only; actual-applet matrix and independent review remain.
