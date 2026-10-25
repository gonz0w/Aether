# UL-007 composed SESSION independent consumer qualification

Status: **private scripted SESSION-01–06 accepted**. All910 native cases pass:
121 capacity,358 connections and431 command-runner. Host115 Python and configured
Zig/Rust checks pass. Eight independent SESSION comparisons,14 prior lifecycle
comparisons and25 checker rejection controls pass. See `acceptance.json` and the
[current matrix](../../../experiments/dash-native/SESSION-ACCEPTANCE.md).

| Stage | Cases | Elapsed seconds | Result |
| --- | --- | --- | --- |
| Host | 115 Python plus configured Zig/Rust/pin checks | 15.30 | Pass |
| Native capacity | 121 | 407.74 | Pass |
| Native connections | 358 | 1140.31 | Pass |
| Native command-runner | 431 | 1441.82 | Pass |

Every native suite meets its predeclared1800-second review ceiling; all owned
process cleanup completed. All host/native suites passed first execution. Timings
are bounded experiment evidence on macOS27 arm64 with QEMU x86-64, not performance
benchmarks or physical-hardware/POSIX conformance.

The complete unchanged script runs in each of three actual dash parent lifetimes:
27 native copies,21 helper exec replacements,24 image admissions and30 zero-status
terminal records/reclaims. Each parent produces the exact65-byte stdout and19-byte
stderr independently specified by the consumer. Exact identity groups precede each
owner-only, hex-framed observation. All six complete linked owner ELFs and raw code
match the final audited producer binaries; reviewed maximum3688/4088 stack bytes
is scoped linked-path evidence, not formal whole-system safety.

The initial independent collector selected older session-* boundary cases as well
as the intended eight composed cases. It failed on an absent composed observation.
`session-check.py` and `session-check.log` retain that attempt; the final selector
names exactly the predeclared eight cases in `session-check-final.py`. Expected
streams, identities and cleanup predicates are unchanged. No native rerun was used
to accommodate the collector fix. The real bad-byte output is rejected by the
ordinary oracle;24 additional mutated traces reject wrong admission identity,
duplicate observation and observation before cleanup.

Inputs are the sealed Aether session-native-2026-09-25 delivery, restored directly
from its661-file final export,293 runtime-source hashes and4311 reused SDK regular
files. The full producer seal was verified before processing. `producer-packet/`
is a selected local copy (top-level sealed files and the replay source archive),
not a mirror of all producer archives. Original failures and other artifacts remain
at the producer's sealed packet; copied inventories bind them.

See `review.md` for the pre-run scope/oracles/budgets, `source-review.md` for scoped
technical assessment, `preparation.json` for exact paths/pins, and mode-specific
owned-process receipts for commands, environment, time and teardown. New local
Python tools are tested on Python3.14.7; no minimum-series qualification is claimed.
They inspect pinned, bounded experimental evidence, not an exposed runtime API.

The delivered composed.sh, helper, expected output files, manifest and SESSION.md
proposal remain byte-identical. The separate current acceptance record supersedes
the proposal's historical NOT RUN status without rewriting those pinned inputs.

The private AENMX007/ABI21 `sh -c` workload is distinct from real serial composition,
full UL-007/M3/R1, public SDK support, independent reader review, TTY/job control,
persistent filesystem and packaged sys-init assembly. Those gates remain open.

## Retention and closeout

All910 native serial logs and available QEMU/exchange logs are copied under
`cases/`, checked against their receipts. `local-owners/` retains the six matched
raw/linked owners. Whole kernel ELF byte equality across build roots is not claimed.
Five legacy Finder metadata entries are recorded separately; every nonmetadata
runtime source matches all three producer reports. No source pin was regenerated
to conceal metadata differences.

Cleanup requires completed acceptance and three exact qualified receipts before
touching outputs. A deliberate missing-acceptance control proves refusal before
any compaction receipt or deletion. Actual cleanup runs only after a separately
checked preflight, archives and reads back every file/hash/size/mode, then verifies
unchanged originals before deleting duplicate suites and their private cache.
`compaction.json` records the final result; SDK, source snapshots, all failures and
prior evidence remain retained. No real-prefix install or sibling change occurred.

Technical assessment is Codex's scoped consumer review. Independent human/reader
review and wider SDK/owner sign-offs remain pending. Documentation adoption and
these passing fixtures do not close full UL-007/M3/R1. The next required workloads
compose early-reader recovery, failed exec, scratch redirection and real serial input.

Closeout: all three suites, 17,143 files, were archived and readback-verified.
Duplicate suites and their private cache removal reclaimed 6.69 GiB
(7,181,160,448 allocated bytes net of archives). Post-cleanup
source/SDK/input pins, prior seal and archive hashes all pass.
