# UL-062 extended family/stage and native-compensation inventory plan

Before behavior work: add a checked JSON inventory and host driver. No parser,
adapter, process helper, native suite rerun, sibling or pin change. This is
inventory and compensation review, not ASan qualification or a waiver.

Applicable requirements: Testing TC-01–03, TD-02/05, TE-01/03–04; Documentation
DW/DS/DP; Foundations E-01–08; Experience for the new contributor CLI.
BSD-2-Clause. Python 3.10+ standard library only.

PXM-01: experiments/command-runner/extended-matrix.json lists every PX* ID from
EXTENDED.md with family, layer, stage, oracle, status, evidence paths and
sha256. Status is pass, blocked or excluded. Blocked sanitizer items set
waiver false.
PXM-02: native compensation for missing host ASan names NB-01–04 evidence
files that exist and match recorded hashes. covers and does_not_cover are
required. does_not_cover must include host heap OOB / pinned ASan.
PXM-03: the driver rejects a mutated matrix that marks PXE-04 pass, omits
does_not_cover, points at a missing file, or has a wrong hash.
PXM-04: TC-02 families that this component does not exercise have explicit
exclusions. No family is silently omitted.

Command: python3 -B experiments/command-runner/check-extended-matrix.py
from the repository root. Repeat on Python 3.10.21. Help/version/usage 0/0/64.
Quality gate and git diff --check. No VM, network or native boot.

Independent review pending. Retain attempts. Update EXTENDED, PROCESS, coverage,
BACKLOG and STATE. UL-062 stays active.
