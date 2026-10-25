# 0028 — Preserve control ownership across reconnects

Accepted for the trusted model, 2026-09-06, under BG-050. Define the next
external boundary in [Control boundary v0](../specs/CONTROL-BOUNDARY-V0.md).
The encoding and transport requirements are a local proposal, not a shared ABI.

Review found that constructing a second Control on the same Model resets the
receipt cache and sequence high-water mark. After an earlier activation has
stopped, replaying its sequence through this new facade could launch again.
Replacing a failed facade also discards the ambiguous-dispatch guard.

One Model therefore permits exactly one successful Control construction for its
lifetime. Claim it after facade initialization and before dispatch can occur.
Reject subsequent construction with InvalidRequest('control already claimed'),
without touching either model state or the existing receipts. Disconnect,
failure, revision changes and loss of the facade reference do not release the
claim. The trusted owner must retain the original facade for reconnects; losing
it leaves dispatch unavailable for that model. Recovery is deliberately absent.

Use one boolean marker on the model, with no global registry, destructor or
retained object cycle. A registry adds lifetime and cleanup machinery; silently
returning the old facade from a constructor obscures ownership. A separate
session for every connection defeats replay retention. This is a sequential
trusted-code guard: direct model access, attribute editing, cloning and concurrent
construction remain outside the contract. It is not caller authentication.

Tests must reject a second facade after completed start/stop, after receipt
eviction and disconnect, and after injected post-dispatch failure. The original
facade must keep its cached/retired/failed outcomes without additional launches.
Retain a failing pre-fix run, then run the model and full development checks.
No native code, dependencies, shared pins, CLI or output formats change.

The authority proposal requires transport-established caller scope and reuse of
the manager-owned session. Actual authentication, restart identity, revocation,
bounded framing and response delivery remain BG-050 acceptance work. This local
guard does not close C10 or demonstrate a producer/consumer transport witness.

Result: [retained evidence](../evidence/control-session-2026-09-06/README.md)
includes three pre-fix failures, 52 passing model tests/three lifecycle controls,
and passing full development checks (48 host, 37 harness, offline standards and
215 retained native outcomes audited). An intermediate test-only comparison bug
was corrected and its failed log retained. No native behavior changed or ran anew.
