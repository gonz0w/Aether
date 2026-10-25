# Native init ABI-6 consuming witness — 2026-09-05

[Decision 0017](../../decisions/0017-native-init-consumer.md) and
[consumer scope/reproduction](../../NATIVE-INIT.md). All seven cases in
[results.json](results.json) pass on the frozen Aether native-init producer:
policy, incorrect deadline policy, late-admission policy, supervisor exit,
supervisor UD2, ignored kernel deadline, and skipped cleanup zeroing.

The independent sys-init supervisor consumes retained producer strict-musl ELF
workers. No companion working tree, kernel ABI, shared pin or older sys-init
fixture was edited. The summary, source archive, producer suite report, original
envelope and both ELF bodies are retained under producer/. Their hashes and
correspondence were verified before use. Boot dependencies were explicitly supplied
and checked by the frozen offline verifier. All 165 captured producer/client/boot
input files remained unchanged after the seven-case run. Source archive digest:
c4bd3c37ff763014a5e9c73f17923339436a4d010dad2d1e8dbef14517af7aeb.

The positive policy observes retained revisions, expired and future interrupt-
time deadlines, cancellation and occupied-slot denial, completion after target
reclaim, terminal-owner buffered-readiness rejection, independent helper liveness
and explicit stop, and fresh channel/worker isolation. It completes three reclaims
and the exact INIT PASS marker. Its raw code is 3,536 bytes. Wrong deadline and
late-admission controls reject at results 821/822 with zero reclaims. Ignored
kernel deadline rejects at 821, not a generic timeout. Supervisor exit/UD2 begin
with live=1 terminal=1 queued=2 wait=1 and reach INIT CLOSED only after the producer
cleanup checks. Omitted zeroing hits the cleanup-specific panic without CLOSED.
These are verified shutdown outcomes, not supervisor restart or recovery.

Two earlier failed attempts are retained in attempts/: the first rejected GOT
entries under the older strict linker map; a separate ABI-6 map now permits
statically resolved read-only GOT entries while forbidding writable data/BSS. The
second rejected the kernel deadline mutation at a generic polling-bound assertion;
the final policy checks immediate expired completion directly, so the mutation
must hit the designated deadline assertion. Neither failed attempt is acceptance.

[Full macOS validation](validation/results.json) passes 48 host tests, 34 model
cases/three mutations, 25 harness tests, three offline standards checks and the
historical ABI-2 evidence audit. Two new input tests use explicitly inert data to
reject changed summary/archive/report/envelope, reserved fields and ELF mismatch;
they are identity/bounds tests, not ELF-loader execution. The new seven ABI-6
cases are separate from the old audit's 22 recorded cases. No fresh Linux or older
native regression run is claimed; producer regressions remain its own witness.

Commands, tool version logs, snapshots, envelopes, serial/QEMU logs and image
hashes are retained. Large ISO outputs and extracted kernel/dependencies remain
at the private work path in the report. SHA256SUMS.json fingerprints this bundle.
Existing musl and first-party notices are retained. Producer/source hashes identify
trusted local inputs, not publisher authenticity or complete host-library closure.
Development entropy, interrupt-clock, polling, single-core, fixed-resource and
helper-transfer limitations remain explicit. General elapsed time, arbitrary
revocation, supervisor replacement and SMP recovery are still unsupported.
