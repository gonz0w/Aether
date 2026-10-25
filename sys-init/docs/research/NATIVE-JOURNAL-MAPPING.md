# Native journal mapping review

Decision 0164, BG-057/BG-058, 2026-09-07. Source review of the current 185-case
native checkpoint and the 287-test model checkpoint. This is a mapping and witness
plan, not new target execution. Exact inputs are retained in
[the review package](../evidence/native-journal-mapping-2026-09-07/README.md).

## Boundary mapping

| Required boundary | Existing source and coverage | Missing integration |
| --- | --- | --- |
| Issued launch identity | [binding.rs](../../prototypes/native-supervisor/binding.rs): ISSUED, Driver::reserve and full Token equality; two fixed synthetic issuance tokens | These constants are not native EventJournal issuance. Preserve that limitation until a native journal actually owns issuance. |
| Received/applied launch | Driver::receive_channel/apply_channel and receive_launch/apply_launch retain resources, phases, exact error and target matching | Compose these operations with History capture; several history fixtures install Binding fields directly. Do not treat those assignments as a received/applied launch witness. |
| Native terminal origin | Sampling::receive retains raw O1/S/O2; terminal_view compares retained Fact with sealed Sample and requires the live owner, token and worker | Borrow the original history association into any future native cut; Python Source construction is not native provenance. |
| Applied observation cut | [cut_coordinator.py](../../prototypes/runtime_model/cut_coordinator.py), [cleaned_adapter.py](../../prototypes/runtime_model/cleaned_adapter.py) and its parent adapters apply the real Python model/journal | There is no native coordinator or native twenty-credit journal here. A Rust fixture must name its bounded lifecycle subset and independently compare traces; it cannot claim to execute Model.batch. |
| Pending release | Driver.pending and History preserve the terminal position; [cut_retirement.py](../../prototypes/runtime_model/cut_retirement.py) qualifies receipt-bound synthetic release | Native release needs the exact Applied Terminal cut member and confirmation before clearing only that position. Existing capture/launch clearing has different semantics. |
| Cleanup | [adapter.rs](../../prototypes/native-supervisor/adapter.rs): close, close_writer, release and reclaim return separate results; Binding owns optional reader/writer/worker | No per-attempt issued/applied reclaim journal record or wait disposition is connected to History. Keep each started/returned/applied operation and failure without discarding handles. |
| Empty inventory | Adapter::clean counts all workers/endpoints plus one wait; dispose_bound performs fixture cleanup and clears reader/worker afterward | Global clean cannot prove one member is empty while another remains live. dispose_bound is not a Cleaned receipt or journal acknowledgment. |
| Retirement | Model composition retains Applied receipts, exact release and tombstones | Native tombstones and their partial-failure ownership remain unimplemented. No history clearing or reused issuance follows from successful disposal. |

The native Context still labels the logical fixture `aether-init-abi6`, while the
large envelope is independently validated as ABI 15 by Adapter::new and the pinned
builder/consumer. Keep both identities explicit. Do not relabel a historical
producer string as the currently loaded kernel identity. Future native issuance
must bind the actual producer/envelope evidence separately from symbolic tokens.

## First consuming witness: complete launch-to-history path

Use one lifetime attempt in slot zero, the existing actual channel and `exit`
worker path, and the current pinned large-image producer/worker. In a new native
probe, call Driver::reserve, acquire and launch; do not initialize an Applied
Binding manually or call sample_setup. Assert exactly one acquisition and launch,
Applied phases, retained reader and worker, transferred writer, full target match,
used issuance and generation one. Any received-but-unapplied or failed launch must
be ineligible for sampling.

Move that Driver into History without reconstructing its records. Establish the
existing fixture's terminal condition, capture the real O1/S/O2 triple into its
original primary slot and verify normal result 18 with its actual kind/readiness.
Terminal polling is a fixture scheduling aid, not the retained cut source. Assert
the exact token, owner, worker, Sample, Fact and pending index. Repeated replay must
not read or launch again. Use explicit existing fixture disposal afterward, retain
all history/issuance bytes and assert adapter cleanup; do not call this retirement.

Positive outcome: the existing successful finish contract 100/3. Add distinct
semantic controls for sampling before launch application, losing the reader or
writer-transfer bookkeeping, and changing owner/token/worker association. Choose
unused assertion IDs when implementing; retain compile/size failures separately
from designated semantic failures. A control must fail its own postcondition, not
merely an earlier unrelated assertion. Use existing failure-path coverage where
it exercises the same call path; add targeted coverage where composition differs.

Keep the strict 8192-byte image limit and existing 185 outcomes. Measure the new
images; 7592 bytes was the prior suite maximum, not free capacity promised for a
new probe. Rebuild and consume the pinned artifacts, preserve old image identities
where unchanged, and run all local gates. The existing producer source-closure
limitation prevents a new catalog acceptance claim; it does not prohibit retaining
a separately labelled consuming witness. Do not expand its historical exception.

## Follow-on implementation gates

1. BG-058: implement and consume the launch-to-history witness above. This closes
   the direct-state-installation gap for its one-attempt path, not native issuance.
2. BG-057: specify and implement a fixed native observation/application owner with
   real reserved effect records, source references and independent expected phase
   traces. Preserve six cut records/two attempts and the twenty-credit obligation
   bound if claiming the full model contract. A smaller subset must be labelled
   and must reject unsupported cuts before mutation; no dummy application receipt.
3. BG-057/BG-058: connect exact reclaim occurrence, per-attempt reader/writer/worker/
   wait disposition, pending release and tombstones. Exercise a mixed cut so another
   live attempt cannot be hidden by an aggregate clean flag. Lost returns close and
   retain ownership; EBADF after the fact is not a substitute for received success.
4. BG-060/BG-033: history reuse and recovery remain separate. No reset or replacement
   owner is introduced by these experiments.

No missing kernel operation was established by this source review. The immediate
work is local composition and consumer evidence. The unavailable native journal
and per-attempt cleanup records are sys-init implementation work, not evidence of
a kernel blocker. All standards remain pinned; PS/Distribution candidate formats,
POSIX wait/session behavior, SMP and physical targets are outside this review.
