# 0068 — Selected native busy rejection preserves issued ownership

Accepted experiment plan, 2026-09-06, BG-058/BG-057 NB-05.

Qualify only received 0x24000/16 creation and 0x23001/16 launch rejection in the
binding driver. The frozen SI-04 `native_c.zig` channelOperation/launchOperation
reject occupied resources before creation/admission. Other errors remain closed
and unresolved under the existing conservative path; no broader errno adoption.

Retain the original token and exact error, permanently consume that issuance, and
release only its provisional native slot claim. A creation rejection has empty
inventory and clears the completed creation position. A launch rejection retains
both acquired endpoints. Keep the owner open so a different issued service can
later reserve the released slot. Never reuse the rejected token or count rejection
as successful launch, cleanup or native target-generation advancement.

These are explicit trusted interference fixtures. Construct the driver in an
empty Adapter domain, then acquire temporary fixture-owned resources outside the
driver: two channel pairs for creation busy, or one worker/reader occupying slot
zero for launch busy. The fixture inventories and disposes every such resource.
It does not import an unknown prior owner, demonstrate concurrent operation or
broaden the production initial-inventory contract. Its interference would be
forbidden through the ordinary single-owner driver; only test setup bypasses it.

Creation positive: busy call leaves empty retained attempt; after fixture pair
disposal, duplicate token is denied, and the second issued service reserves the
same native slot and launches. Launch positive: busy call preserves both endpoints;
after fixture worker and rejected-pair disposal, duplicate token stays denied and
the second service launches in the released slot. Complete fixture accounting at
three reclaimed workers and 100. Disposal is not journal cleanup or retirement.

Controls: clear the consumed entry on creation rejection -> exact 1018/reclaimed=0;
forget the writer on launch rejection -> exact 1019/reclaimed=0. Require designated
native profile panic/context; unrelated build errors or timeout do not qualify.
Run all 63 prior cases plus four new cases with SI-04, Rust 1.98.0/2024, BSP-only,
unchanged 4 KiB clients, retained frozen input/build/serial evidence, then all checks.

Review O-04, I-03–06 and E-01–08: exact origin, absence versus retention of resources,
slot claim versus historical record, and operation consumption versus owner closure.
No new unsafe operation, dependency, shared ABI or output protocol. NB-06 expected
target/result qualification is next; other errors, exhaustion/lost replies and
ND-02–05 remain open. Full binding/journal/recovery conformance is not claimed.

## Implementation review

`Binding.reserved` distinguishes a live slot claim from a retained historical
attempt. Only the two selected busy returns clear that claim; creation also
clears the completed creation position. The exact error and consumed entry stay.
Launch retains writer/reader and its error guard prevents re-invocation. Unknown
or other returns still close admission; local binding failure remains separate.
There is no automatic cleanup event, table reset or old-token retry API.

Three compile-only source versions exceeded 4 KiB for the launch probe before
sharing fixture worker setup and terminal/close/reclaim helpers. Original checks
and the fixed limit remain intact. Sources/logs and diagnostic map are retained;
final local probes fit. This is a code-size accommodation for tests, not a
production performance claim. Existing typed close/reclaim primitives are reused.
No new unsafe code, allocation, dependency or independent reviewer sign-off.

Source basis: the [frozen producer implementation](../evidence/native-binding-failure-2026-09-06/witness/frozen-inputs/Aether/kernel/arch/x86_64/native_c.zig),
`channelOperation` and `launchOperation`, and the
[consumer Adapter](../../prototypes/native-supervisor/adapter.rs). Busy launch
precedes generation increment and channel transfer; busy creation returns before
Channel.create. The driver still lacks an expected-target generation registry,
so the passing native behavior must not be described as NB-06 implementation.

NB-06 planning constraint: the launch-busy fixture's independently admitted worker
consumes a native slot generation outside Driver. A future expected-target registry
must explicitly account for that trusted fixture history or redesign the probe;
it cannot assume the later successful driver launch is native generation one.
Do not weaken expected-target matching to preserve this interference sequence.
Service generation remains distinct from the producer slot generation.

## Validation — 2026-09-06

All 67 native cases pass with all 178 frozen inputs unchanged. Forty-four of 63
preceding raw clients match; nineteen changed clients pass their previous semantic
oracles and are individually listed in witness/comparison.json. New sizes: 3,880
bytes (creation busy), 3,896 (token control), 4,000 (launch busy), 4,000 (writer
control), all within 4 KiB. Exact controls 1018/0 and 1019/0 pass. No native
execution failed; compile-only size failures remain retained.

All eight gates pass in `out/checks/run-fyeusv9p`: 228 model tests, 23 negative
controls, 48 host tests and 37 harness tests. The native catalog verifies 893
historical outcomes across 33 bundles and 12,513 listed files. Both targeted
native-input harness tests, new document references and `git diff --check` pass.
Seven current consumer source entries match the executed snapshot.

Evidence: `docs/evidence/native-binding-busy-2026-09-06/`. Only validation notes
and retained evidence copies follow the checks; runtime sources, tests, catalog
and quality inventory remain unchanged. NB-06 expected target/result qualification
is next, with the fixture-generation constraint above; other NB/ND gates stay open.
