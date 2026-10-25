# Independent scratch session acceptance — 2026-09-29

**SCRATCH-SESSION-01–06 accepted for private AENMX007/ABI21 scripted execution.**
All149 capacity cases and five legacy command cases pass, plus127 Python tests and
configured Rust/Zig/offline-pin checks. Twelve independent trace comparisons and100
checker rejection controls pass. No consumer native, host or checker attempt failed
or required a rerun. Producer's retained failures remain part of its own history.

Three unchanged dash parents truncate the seeded file, write A/B through shared
aliases, survive closure of the first alias, receive owner-backed EACCES/child2,
reopen and read exactAB/EOF, then complete argv, pipeline, FD closure, stable PID
and parent stderr checks. Each parent emits exact52-byte stdout and19-byte stderr.
Totals:21 copies,15 helper replacements,18 admissions and24 terminal/reclaims.
The namespaces are freshly seeded only after retirement; this is not persistence.

The12 cases cover normal composition, lostB, corrupted read, wrong denied error,
false EOF, skipped owner request, premature alias close, wrong environment, leaked
FD, retired stderr, stale description and pipeline byte corruption. Denial must
be tied to the actual owner lookup and child2 with no replacement admission.
Client-synthesized EACCES rejects with confirmed parent stop143. Early-close and
retired-stderr cases require actual wrapper141; guessed script63/70 are rejected.
Both corrupt-output cases complete cleanup but fail the ordinary byte oracle.

The independent checker requires exact full terminal/admission multisets, child
phase ordering, parent completion, observations after cleanup, separate streams
and the exact supervisor result/reclaim count/final marker.100 counterexamples
exercise wrong/late admission, duplicate/early observations, duplicate/missing
terminals, stderr corruption, wrong supervisor, ordinary byte-oracle rejection
and the two guessed exit codes. Raw completed native traces are retained in cases/.
Owner-local file-state assertions and authority review are scoped in source-review.md;
serial logs alone do not expose all private storage fields.

## Inputs, source reconciliation and resources

Producer seal SHA256:
`7d72d2a0b3c6cf3b1458a17e22341d5f630f648561c56373d39739f27c623958`.
Verified all sealed files before extracting805 indexed source/support members.
The303-source capacity receipt and legacy receipt each differ from final export
only in scripts/scratch_smoke.py, which tightens the host diagnostic oracle.
Native sources are unchanged. Exact old/delivered hashes and Finder metadata
are recorded separately; original receipts were not rewritten.

4311 SDK files, compiler/tool pins, original consumer inputs and unchanged process
helper were verified before and after suites. No live sibling implementation was
built. All26 locally rebuilt raw and ELF owner images match the delivered bindings.
Maximum code18808/24576 bytes; contributor-inspected stack3896/4088 with192-byte
minimum margin. These are reused, hash-bound inspection estimates, not a formal
stack proof, kernel measurement or independent human reader review.

Owned native deadlines3600 seconds, review ceilings1800 seconds,512MiB streams;
host300 seconds. Guest watchdogs and resource limits were unchanged. Every outer
process owner reports complete cleanup. Exact commands, environment, toolchain,
source hashes, timings and process outputs are retained. Elapsed seconds:
capacity534.76, legacy17.20, host12.86.

These timings are qualification observations, not performance benchmarks. Replay
requires a fresh packet/work root, sealed export and pinned external tools/SDK,
then run.py prepare/capacity/host/legacy and finish.py. Never overwrite evidence.
Archive identities and retention paths are recorded in compaction.json.

## Scope and next action

[Current acceptance](../../../experiments/dash-native/SCRATCH-ACCEPTANCE.md) updates
the original request's historical NOT RUN state without changing pinned bytes.
No runtime, kernel ABI, resource limit, sibling implementation or released pin
changed here. Prior broad358-connection/431-runner suites were not rerun.

UL-007 stays active. Next prepare the real serial-session composition. SI-07 still
needs complete versioned bootstrap/transport and rebuilt runner/bytecount; decoder
checks alone do not supply them. Public SDK integration, independent reviews,
general filesystem/TTY/POSIX support and full M3/R1 remain open.

Both new suite archives were read back and verified before redundant output/cache
removal. Net reclaimed1,089,712,128 allocated bytes (about1039MiB).
Earlier builds, pinned inputs and sealed evidence remain retained.

Final quality, Python syntax, whitespace, source/SDK/tool/input preservation and
four prior packet seals pass. See final-checks.json. Independent reader review
remains pending; no release or broader runtime acceptance is claimed.
