# UL-059 native mapped uncertainty

Link-only parent wrappers watch actual native exchanges. After a complete real
reply has arrived in bounded fragments, they validate its original success,
receipt and metadata. Pending collection replies are untouched. The selected
successful reply is then either reported as losing its final received fragment,
or has its padding/receipt corrupted locally. The real adapter and mapped runner
handle the injected result; no fake child terminal is constructed.

Five controls check lost/padded admission and lost/padded/foreign-receipt terminal
collection. Wrapper main requires the real runner's return1, one injection, no
incomplete fragment state and the appropriate input-close count. Guarded exchange,
channel, read, close and policy calls after injection fail immediately at109.
A successful witness then exits101(admission) or102(collection), deliberately
separate from the verified runner return. Unexpected wrapper state exits110 and
must fail the oracle. The sixth control privately changes the mapped header to
retry lost collection; the exchange guard exits109 before replay reaches adapter
or channel, demonstrating that the no-replay witness detects a broken consumer.

All six require broker970/reclaimed0 and no success marker in generation1.
Collection cases require actual normal child0 before parent102 (retry109).
Admission does not assume child scheduling: any child terminal that occurs must
be normal0, but child completion is not required. Original successful admission
receipt is verified before injection under the pinned owner that publishes it
only after admission. This distinguishes caller uncertainty from the test's known
remote effect. No completed cleanup, continued service or recovery is claimed.

The full run and counts are recorded in summary.json. Prior42 client ELFs are
byte-identical; six new client variants and their exact wrapper/mutation inputs
are retained. Production adapter, parser, result decoder and mapped header are
unchanged; only opt-in test wiring is added. The original producer pin remains
separate and default. All attempts and original serial/process records are retained.
Large images/private checkouts stay under the listed build roots.

Mapped25/four mutations, result28159/four, parser1293/two and21 command host
regressions pass. New C uses strict C17 diagnostics and Clang-format21.1.8; Python
3.10 grammar runs on3.14.7. The quality/three-standards gate is recorded separately.
Pinned Clang/SDK/producer/host tools, exact flags/carriers/ELFs and owned commands
are in receipts. Native180s commands, guest30s/no-NIC isolation and512MiB per-file
limits remain; host30s/16MiB and quality60s. No new dependency or standard pin.
UBSan remains explicit; ASan, independent review and release gates remain open.

Current-task technical review by Codex checked interception phase, contiguous
fragment bounds, validation before fault injection, exact one-time guards, known
receipt/terminal checks and distinct runner/witness/owner outcomes. Independent
technical/reader and affected-owner reviews are pending. Foundations O/I/E and
approved CE/CC/CP, TD/TC/TE apply. Evidence reuse requires unchanged affecting
sources/tools/contracts. Native pending-budget and malformed startup carrier
witnesses remain open; RL local outcomes require the prepared owner extension.
General unknown/stop/resource recovery and package/sys-init acceptance are separate.
