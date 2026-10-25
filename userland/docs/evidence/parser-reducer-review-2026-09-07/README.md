# UL-062 reduction outcome classification — 2026-09-07

Reducer classification now treats fixture exit 91, incomplete cleanup, unexpected
diagnostics, missing PASS, invalid JSON and mismatched retained bytes/metadata as
incomplete reduction, not as a non-reproducing candidate. Only exit 0 with the
exact PASS marker and no failure files is a negative; only exit 90 with the exact
named ORACLE line and matching retain files is a positive. Eleven in-process
controls pass, including two that show the previous logic returning false for
exit 91 and mismatched bytes. Full --ubsan-only sweep/reduction passes on Python
3.14.7 and 3.10.21. C fixtures, production parser and process.py are unchanged.

The first driver run failed because the unittest file was listed before it
existed; that attempt is retained. ASan was not rerun. Independent review is
pending. This does not close UL-062.

See [PLAN.md](PLAN.md). Commands remain in
[EXTENDED.md](../../../experiments/command-runner/EXTENDED.md).

| Attempt | Result |
| --- | --- |
| parser-extended-kny6g3yj | Missing test-parser-reduction.py during source hash; incomplete |
| parser-extended-3zflg97i | Python 3.14.7: pass |
| parser-extended-7wj7156x | Python 3.10.21: pass |
