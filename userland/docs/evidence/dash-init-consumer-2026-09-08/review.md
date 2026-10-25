# UL-007 generated-init consumer review and execution plan

Selected 2026-09-08 before execution. Reproduce the completed Aether
shell-dash-init-2026-09-08 packet, manifest SHA256
51058b97d7da8f37a2af56e42da8ca5a857cc100b605828a513c38d874a3cd24.
This is independent execution of the producer's unchanged fixture and oracles,
not independently authored full-shell acceptance. No sibling edits or pin updates.

Applicable: Foundations O-01–05, I-03/05/06, E-01–08; adopted TD-01–03,
TC-01–04, TE-01–04, CP Python subprocess rules, DW/DS/DP documentation;
Distribution NC/PX/ID/EV distinctions. Preserve upstream dash terms and objects.

Use the previous verified startup scaffold and SDK receipt in
build/dash-startup-native-02k2tw4o/results.json. Verify every incoming packet
file, source archive member, producer runtime source and reused SDK/tool hash
before running; preserve a separate local snapshot beneath build/. Match the
producer libc digest. Do not consume moving parent-identity implementation.

Run the unchanged command suite with the pinned tools and existing owned-process
helper: 291 cases, 1800-second suite deadline, existing per-guest deadlines,
512 MiB outer stream bound, private TMPDIR and controlled PATH. Record exact
arguments/environment, raw output and complete outer-process cleanup. Native
accepted cases retain their own reclaim oracles; semantic mutants must reject
at the specified context, not merely time out. Recheck source/SDK integrity.
Run python3 -B docs/quality/check.py after documenting results.

The four selected dash cases are real signal setup, skipped signal setup,
generated init and skipped init. Positive generated init must expose PPID -38,
empty PWD, unsupported geteuid and the exact getcwd diagnostic. It must also
initialize IFS/OPTIND/CHLD, copy normally and reclaim four tasks over two
generations. Skipped init must reject client103/owner1501. These expected gaps
must never be labeled successful shell startup. Private SIGCHLD production is
not a general child-notification service. Actual main/parser/exec/wait/pipes
and consumer-authorized identity/CWD contracts remain UL-007 dependencies.

Technical review by Codex: inspected captured initializer/signal assertions and
producer recipe input paths. Native runtime source is reproduced unchanged;
this is not a complete source audit. Independent technical/reader review remains
pending. No sign-off, M3 acceptance, native sanitizer or fresh M4 claim.

Simplicity: the simpler alternative is reusing the existing reproduction pattern
and owned-process helper; selected. A new integration framework or runtime facade
is unnecessary. None removed now: historical evidence and active consumers must
remain intact. Local driver changes are intake/count/integrity checks only.

Documentation scope: STATE/BACKLOG/ROADMAP and NATIVE-DASH-GAPS point to this
receipt; update existing coverage evidence without changing published surfaces.
Preserve all attempts and raw receipts. Final results and unresolved gates follow
in README.md; this plan does not predeclare a pass.

## Execution disposition

One attempt passed all 291 original cases. Exact four-case serial checks are in
dash-cases.json; the receipt and logs preserve positive four-reclaim outcomes and
negative zero-reclaim limits. All 545 source files and 4311 SDK files retain
identity. No oracle or runtime implementation change was needed. The quality gate
passes. Technical review by Codex additionally checked owner diagnostic selection,
exact terminal order, upstream object equality and compiler/tool identity. This
scoped reproduction review does not close the broader source/reader review gaps.

The executed one-off run.py is retained verbatim as evidence using the earlier
reproduction pattern. It is not a newly supported public harness or a declaration
of full CP/source-migration conformance. Any promoted reusable driver must undergo
UL-063 readability/minimum-version review; this run records Python 3.14.7 only.
