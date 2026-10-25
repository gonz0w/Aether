# Reconciliation source review evidence — 2026-09-06

Decision 0042 reviews fifteen selected producer, standards and consumer files.
`reviewed/` holds exact bytes; `reviewed-files.json` records their hashes and sizes.
Each source was re-read immediately after copying. `source-recheck.json` records
a later comparison: only Aether's command contract and planning state changed.
`late-reviewed/`, its manifest and two diffs preserve those updated documents
separately. They add completed command-result qualification and explicitly leave
unknown recovery open. Original snapshots were not rewritten. Selected files are
research inputs, not a complete producer build or native qualification pin.

Findings: confirmed ABI-6 returns have useful exact semantics; terminal and wait
observations do not identify a journal occurrence. Successful reclaim returns
follow local cleanup/zeroing checks, while EBADF and target-reclaimed wait status
are not general replayable receipts. Selected init and command profiles do not
provide lost-result/replacement-owner reconciliation. BG-058 captures qualification
of confirmed results before any native adapter change; unknown remains unresolved.

Validation command from `/Users/cam/DEV/sys-init`:

```
python3 scripts/check-all.py
```

`validation/` retains successful `out/checks/run-d623l27p`: all offline standards,
experience, distribution, quality and historical native evidence gates, unchanged
165 model tests / fifteen mutation controls, 48 host tests and 37 harness tests.
No runtime source or test was changed. Native execution was not rerun and no new
test coverage or recovery is claimed. No failed validation run occurred.

`source/` preserves all model report inputs and changed review/adoption/planning
records. Model hashes and all reviewed-source hashes were verified. Late producer
document copies, their disposition, the research-index link and final validation
notes were retained after full checks; executable inputs and quality inventory
were unchanged. These additional documents were inspected and their manifest
hashes verified separately. SHA256SUMS.json covers all retained files except
itself. Existing evidence, release bytes, runtime pins and sibling files were not
modified. A source checksum establishes identity, not authority or conformance.
