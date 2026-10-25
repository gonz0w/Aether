# 0171 — Execute the retained generated launch

BG-057/BG-058, 2026-09-07. Extend the fixed Application's retained effect with
owner-bound invocation keys and explicit Reserved(1), Started(2), Returned(3),
Applied(4), Executed(5), Unknown(6) dispositions. These are private experiment tags,
not shared ABI values. Exact full token and owner equality precede every transition.
Only Reserved may start once; only Applied may acknowledge. Executed/Unknown never
retry and no disposition frees credits, evicts records or creates a new owner.
Unknown closes Application while retaining the token and native outcome inventory.

The native probe owns the same Application and original History throughout
reservation, policy application, generated launch, return validation and
acknowledgment. Use the actual retained token, including occurrence index zero;
never substitute ISSUED[1]. A separate owned generated-launch record retains its
key, channel phases, reader/writer/worker and exact error. Application's journal
key does not confer native authority: Adapter grants and slot/generation checks
remain at the enforcing native boundary. The first profile permits only attempt
one, slot one, generation one, launch/activation operation one.

Start the journal invocation before acquiring its channel. Retain channel return
and ownership before launching. A successful native launch return retains Worker,
transfers Writer and records Returned; validate complete target 0xb0000102 and
resource association before Applied, then acknowledge the exact occurrence.
Denied starts/early acknowledgment must not issue another call. Any failed native
step retains its actual error/handles and closes both owners; no rejected-effect
retry or cleanup receipt is invented. Cleanup is explicit fixture disposal, not
retirement, and the Application stays alive across the generated return and ack.

Positive 100/3: actual provider and generated dependent, plus one ordinary fixture
worker. Controls substitute token (1083), acknowledge early (1084), retain the
transferred writer (1085); an occupied slot exercises actual launch EBUSY (1086).
Failure-state retention uses a separate 1087 postcondition. Test host full-token,
foreign-key, stage-order, closure and no-retry behavior with omission controls;
then consume 203 fresh Aether cases. Keep strict image/stack limits, old semantics,
pinned offline producer/worker/releases, no new unsafe operation or sibling edits.
Preserve failures and exact commands. Foundations O/I/E and current scoped
Experience/Distribution adoption apply; no descriptors/readiness/retirement API.

## Preflight and fixture refinement

The first five images link within 8192 bytes. A source/key check was then added
at the actual native invocation boundary, before channel acquisition, independently
of the earlier start request. EffectKey measures 96 bytes; GeneratedLaunch is
compile-time bounded to 192 bytes; Application/storage sizes remain unchanged.
The application stays in the outer native frame through execution, acknowledgment
and fixture disposal, addressing decision 0170's short owner lifetime.

The first restricted run passes execution and three omission controls but the busy
case reaches 1087. A separately retained diagnostic reports operation 147456
(0x24000, channel creation), so it did not reach the intended launch error. Waiting
for the occupying worker's terminal return before closing its reader releases the
channel while retaining the unreclaimed worker slot. A fresh restricted run passes
all five cases, including the exact launch error operation 0x23001/errno 16 at 1086.
The failed run, diagnostic source/commands/logs and successful rerun remain distinct.

## Validation and handoff

Decision 0171 executes the exact generated dependent-launch obligation on Aether.
The original Application and History stay alive in the outer probe across policy
application, generated invocation, native return, acknowledgment and fixture disposal.
An owner-bound 96-byte EffectKey carries the complete retained occurrence identity;
the invocation boundary independently verifies original owner, exact token and
Started disposition before native I/O. It does not substitute ISSUED[1]. Native
grants and slot/generation checks remain separate from journal identity.

The generated record (compile-time bounded to 192 bytes) retains channel/launch
phases, reader/writer/worker and exact native error. Successful return transfers the
writer, retains the real worker and validates target 0xb0000102 before Applied.
The journal progresses Reserved -> Started -> Returned -> Applied -> Executed;
only Applied acknowledges, and repeated start/ack/perform calls deny without I/O.
The token and Executed disposition remain inspectable after fixture disposal.
Credits remain occupied; acknowledgment is not effect retirement or history reuse.

The positive finishes 100/3 using the actual provider and generated dependent plus
one ordinary fixture worker. Token substitution and early acknowledgment reject at
1083/0 and 1084/0. Retaining the transferred writer rejects at 1085/0 after verifying
Unknown closure and retained handles. An occupied, unreclaimed worker slot produces
the real launch error operation 0x23001/errno 16 at 1086/0, retaining reader, writer
and error without a worker or retry. Assertion 1087 detects broken failure retention.
The initial busy fixture instead reached channel creation; its failed run and a
diagnostic reporting operation 0x24000 are retained. Waiting for the occupant's
terminal return before closing its reader frees the channel while preserving the
busy slot. The five-case restricted rerun and full run then pass distinctly.

All 203 fresh Aether cases pass. All 198 prior images/outcomes and 151 ABI-6 rebuilds
remain byte-identical. The five new images are 7944/4968/7944/6744/8072 bytes; the
suite maximum is 8152/8192. All ten local gates pass in `run-hgsvbhzx`, including
287 model tests and ten Rust groups with fifteen core tests and nine omission
controls. The same core compiles for x86_64-unknown-none, preserving 1976-byte
storage and 1992-byte Application. No heap, new unsafe site, syscall or image/stack
limit relaxation is introduced. These remain bounded experiments, not a production
resource or readiness claim. Evidence: `docs/evidence/generated-launch-execution-2026-09-07/`.

Producer/worker/release pins remain unchanged. The catalog stays at 50 bundles and
3019 historical outcomes pending BG-056 complete producer source closure; no new
exception is introduced. Symbolic epoch/revision remain fixed fixture context.
Native Terminal/Cleaned application, general effect rejection policy, explicit
retirement, sustained reuse and recovery are not implemented by this step. No
additional OS provisioning or sibling edits were made.

Next BG-057/BG-058: retain the acknowledged generated-launch return as an original
per-attempt source before explicit effect-pool retirement, then qualify the
dependent Launched policy observation. The current twenty-credit hold deliberately
blocks another cut even after acknowledgment. Freeing it requires a retained exact
Executed occurrence and native resource/return association, not merely an empty
adapter or copied token. Keep the same owner across those transitions; do not
clear the effect pool or recreate Application as a workaround. BG-060 sustained
reuse and BG-033 recovery remain separate. No kernel blocker was established.

Technical review: the root owns Application and History until native finish, addressing the prior short-lived helper scope. The private effect key retains full token identity and the original external owner anchor. Started validation is repeated at the I/O boundary; stage guards prohibit repeat channel/launch invocation. Actual return fields are stored before validation; unknown/error paths retain inventory and close, with an independent postcondition before designated failure completion. Successful fixture disposal clears handles only after existing checked calls return; this is not a Cleaned receipt or retirement. The core tests cover every token field, foreign owners, stage order and closure. No independent reviewer sign-off is claimed. Documentation impact: execution contract, storage/application reference, native coverage, quality/boundary and CLI source inventories, BG-057/058 handoff.
