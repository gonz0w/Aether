# ADP-01-W04 negative-control exclusion

The preimplementation contract is `contract.md`; `before-build.zig` preserves
this change's baseline, including previously uncommitted native work. Final
implementation identities are in `sources.json`.

- `zig build test`: passes, including 98 Python tests and Zig host checks.
- `zig fmt --check build.zig`, `sh -n` and `shellcheck -s sh` on both installed
  Git hooks pass. Hook syntax/lint is scoped evidence, not execution portability.
- `negative-results.json`: all 39 actual `zig build --help` graph evaluations
  reject the exact named negative option with `-Drelease-artifact=true`.
  Nonzero exit alone is insufficient; each recorded named diagnostic was checked.
- Guarded `panic-test=false` and unguarded `panic-test=true` evaluations pass.
- Ordinary and guarded builds pass with prefixes `default` and `guarded` under
  `zig-out/adp01-build-guard-2026-09-06`, local Zig caches, and otherwise default
  options. `artifact-comparison.json` records every output hash.
- Whole-output equality initially failed because ISO bytes differ. Both comparison
  attempts are retained. The narrower kernel/four Rust payload comparison passes;
  it does not prove reproducible ISO construction.
- `python3 scripts/regression.py`: all seven M4 target cases pass. Raw target logs
  and the harness's source/tool/artifact identities are retained here.

This is an opt-in build guard, not an assembled release qualification. It changes
no ABI or runtime options. Negative experiments remain available outside guarded
builds. New option classification is covered by `tests/test_build_policy.py`.
Extended testing, independent review and release assembly remain outstanding.
