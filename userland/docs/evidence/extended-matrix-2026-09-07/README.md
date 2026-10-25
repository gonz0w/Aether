# UL-062 extended matrix and native compensation — 2026-09-07

A checked family/stage inventory now lists every PX* ID plus NB-01–04 with
family, layer, stage, oracle, status and evidence hashes. PXE-04 and PXA-04
stay blocked. Compensation names the existing native denial/reclaim witnesses
and must say it does not cover host heap OOB or pinned ASan; waiver is false.
Four mutants (PXE-04 pass, overclaim, missing file, wrong hash) are rejected.
Unexercised TC-02 families have explicit exclusions. No native suite was rerun
and no sanitizer waiver is granted.

Python 3.14.7 and 3.10.21 checks pass. The first driver run accepted a PXE-04
pass mutant and is retained. Independent review is pending. This does not close
UL-062.

Command: `python3 -B experiments/command-runner/check-extended-matrix.py`.

| Attempt | Result |
| --- | --- |
| extended-matrix-r1tozv64 | PXE-04 pass mutant accepted; incomplete |
| extended-matrix-12hn7cxb | Python 3.14.7 after ASan-id guard: pass |
| extended-matrix-ptvt3775 | Python 3.10.21: pass |
| extended-matrix-2oxcc3pu | Python 3.14.7 after EXTENDED PXM rows: pass |
