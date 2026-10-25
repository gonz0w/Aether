# Session dispatch prerequisites — 2026-09-25

This packet qualifies reusable host cores and authentic child identity in existing
native fixtures. It does **not** execute the composed SESSION workload or deliver
a userland handoff. The separately developed scratch dispatcher is not a runtime
input to any suite in this packet.

## Changes and scope

The session-only pipe core selects nine object and fifteen participant lifetimes;
old aliases retain three-use limits. Routing and holder transactions share the same
implementation. Three retained child records distinguish admission, terminal,
reserved wait reply, delivery and reclamation using exact slot/generation/handle/PID.
The bounded exec parser preserves actual argv/env values, including wrong WITNESS.
Existing capacity wait/readiness paths now use admitted native handles and rebound
memory capabilities instead of subtracting the parent's PID or generation.

Nine new Rust core tests bring the existing wrapper to69. They cover stale routes,
zeroing, exhaustion, partial delivery, reuse barriers and malformed vectors. Two
generation-blind mutants compile and fail the intended stale-identity assertion.
These host tests do not establish native higher-generation copied-child execution.

## Executed evidence

- `host-final-run.json` / `host-final.log`: required `zig build test`,110 Python
  tests,69 Rust tests in the pipe wrapper and configured Zig/Rust/pin checks pass.
- `capacity-results.json`:113 cases pass.
- `connections-results.json`:358 cases pass.
- `runner-results.json`:431 cases pass.
- `host-inputs.*` pins308 source/support files; each final native attempt pins289
  runtime/build inputs. Tools and SDK identities match across suites. Sources stay
  frozen through qualification; scratch draft files are outside these inventories.
- `stack-builds.json` binds the three linked legacy owners to qualified raw bytes.
  Inspected critical paths use3888,3968 and3984 of4088 usable stack bytes. This is
  scoped linked-code inspection, not formal whole-program stack verification.
- `artifact-comparison.json` records52 unchanged and102 changed top-level binaries
  compared with the prior profile packet; this is not a kernel-binary inventory.

`finalize.py` verifies the suite counts, frozen inputs, archive members, cleanup,
mutant failures, raw/linked stack bindings, workflow, format and simplicity pin.
`verification.json` and `SHA256SUMS` are produced only after those checks pass.
The review snapshot records the local references as they stood at this boundary;
later implementation may advance them without changing this sealed packet.

## Retained unsuccessful attempts

The preaudit capacity attempt was interrupted for linked stack review, before a
qualified full run. Its −2 result,76-second duration, source snapshot, incomplete
report, build outputs and native transcripts are retained. It is not a passing
suite. Initial host-only intermediate snapshots/results remain separate from the
final frozen host/native qualification.

The first capacity, connections and runner archive attempts rejected changing `.DS_Store`
metadata. Their inventories, archives, logs and complete mismatch audits remain.
All other member hashes matched; retries verify archives against every original
before removing only the owned duplicate output directory. The interrupted
preaudit output is similarly retained in a verified archive before cleanup.
No previous sealed evidence, sibling repository or released standard pin changes.

## Next required work

Integrate the request-driven persistent parent, real argv/env exec, live descriptor
snapshots, repeated jobs, confirmed-stop cleanup and separate stream observations.
Run the entire unchanged pinned composed.sh and semantic controls, with fresh
matching producer regressions and linked stack review. Only then request independent
userland replay. Existing serial-shell evidence is separate; SESSION-01–06 remains
NOT RUN at this packet boundary.
