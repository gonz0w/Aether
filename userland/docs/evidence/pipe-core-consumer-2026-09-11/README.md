# UL-007 pipe core consumer checks — 2026-09-11

The frozen Aether pipe core passes local host qualification: 12 producer Rust
cases, one independent public-method test with 32 chunk schedules, and five
semantic mutants rejected at their selected assertions. All completed command
receipts record cleanup. The unchanged core also compiles for
`x86_64-unknown-none`; this is object generation, not linking or execution.

The consumer schedules fill the 256-byte FIFO, observe a pending write, drain
space and retry, then terminate the writer and compare the remaining bytes with
a separate queue. They check EOF before wait collection, stale child denial and
retirement blocked by a pending reply. Authentication and terminal observation
are synthetic inputs; these checks cannot qualify the dispatcher that supplies
them. The producer manifest is
`73d0fb9aa58c422764c336807ee8a87b0e32f0732fa9c11cbc0d77813fbac51e`.
All 257 archived source hashes were verified before selecting the unchanged core.

[Plan/review](review.md), [results](results.json), [inputs](inputs.json),
[commands](commands.json), [artifact hashes](artifacts.json) and raw streams are
retained. The exact driver is [run.py](run.py); private build artifacts remain at
the path in results. Producer bytes and mutant inputs remain in the previously
sealed [producer packet](../dash-redirect-consumer-2026-09-11/producer-history/pipe-owner-core-2026-09-11/README.md).

Attempt 1 failed the consumer formatting check before product tests. Its input
snapshot and receipts remain in [attempt-1](attempt-1/failure.txt). The corrected
formatting was qualified in a fresh build root; no product behavior was changed.

Self-review checked public-method oracles, pin validation, bounded subprocess
cleanup and host/native claim separation. Independent technical/security/reader
review remains pending. The local quality gate passed; see quality.log.

Next: consume Aether's authenticated native dispatcher/private adapter delivery,
then run the unchanged dash substitution workload with native EOF, backpressure,
reply containment, descriptor ownership and signal controls. The existing
[pipe intake requirements](../dash-redirect-consumer-2026-09-11/pipe-next.md) remain
applicable. No native pipe support, dash substitution, pipeline, M3 completion or
release readiness is claimed. The previous 254-case native redirection evidence
is unchanged and was not rerun for this host-only selection.
