# 0105 — Native runner manuals and complete builder capture

Accepted local documentation/capture fix, 2026-09-06; BG-056 follow-up to 0104.
Add canonical source manuals for all four native runners, preserving actual
options, effectful examples, profile/dependency gates, report shapes, timeouts,
error statuses and expected semantic markers. Do not imply that CLI probes or
manual rendering constitute native execution.

Source review found a regression from decision 0098: native-io-stop.py copies
the standalone supervisor builder but not its new bounded_tools.py import. Move
its existing copy loop into a small capture_client function and include that
helper. The existing source-hash loop then fingerprints it with the other copied
inputs. No target source, compiler flag, profile, expected marker or pin changes.

Validate the production copy function by executing the copied builder's help
with no checkout PYTHONPATH; removing the helper must fail. Build io-stop using
that isolated copy and require exact retained decision-0098 raw/envelope hashes.
This host capture fix needs no fresh guest run because native inputs/artifacts
are identical; no new target-behavior acceptance is claimed. Native smoke and
full-profile witnesses remain the existing retained evidence.

Twelve CLI probes, four manual lint/78/60-column/HTML renderings and the required
aggregate gates qualify the local slice. All eighteen inventoried commands now
have manuals; API/config detail, independent/HTML review and target installation
remain open. The scoped OS STYLE notices retain decision 0099's disposition.
Evidence: docs/evidence/native-runner-manuals-2026-09-06/README.md.
