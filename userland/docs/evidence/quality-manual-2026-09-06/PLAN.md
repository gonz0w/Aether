# UL-071: quality command documentation and contract evidence

Requirement: UL-061 / ADP-02 documentation gap. Reader: a contributor using the
existing quality 0.1.0 checker in this experimental checkout. Scope: its actual
CLI and local documentation workflow, not a target-installed command.

Apply DW-01–06, DS-01–05, DM-01–04, DP-01–05, TD-01–03, TC-01/02,
TE-01–05, CP-02/03 and EV-01–05 from the unchanged approved snapshot.
Existing Experience streams/exits remain authoritative; do not alter checker
behavior to make a manual easier to write. BSD-2-Clause for original documentation.

Before completion, record exact checker, manual, renderer and Python identities.
Use mdoc as the single manual source. Provide options, examples, expected outcomes,
files/environment, failure/recovery and scope. Add a command inventory entry bound
to the source digest; keep draft until actual independent reviews and relevant
packaged lookup are available. No fictional installed alias or native support.

Test plan (host only, local development/documentation stage):

| ID | Independent oracle |
| --- | --- |
| QD-01 | --help exits 0 on stdout, lists all options; stderr empty |
| QD-02 | --version exits 0, exactly quality 0.1.0 on stdout; stderr empty |
| QD-03 | Unknown option and extra operand each exit 64 with usage on stderr and no stdout |
| QD-04 | Default gate exits 0 with explicit integrity success and runtime NOT RUN |
| QD-05 | --release exits 1 with incomplete release entry; it cannot authorize publication |
| QD-06 | Private wrong-pin fixture exits 1 before copied validator execution; help/version still work without verified inputs |
| QD-07 | Repeated --release and argparse's accepted --rel prefix retain actual release-preflight outcome |
| QD-08 | mandoc lint exits 0 with no diagnostics; ASCII 78/50-column and HTML rendering succeed; inspect ordinary/narrow wrapping and HTML content |
| QD-09 | All three local standards checks plus inventory control pass; missing source/manual links reject local review validation |

Use existing owned-process helper for commands (explicit argv/env/cwd, no shell
interpolation, 120 seconds per gate, 30 seconds per render/CLI, 16 MiB log limit).
Put all temporary fixtures/render output in build/quality-manual. Do not mutate
real pins. No network, install, sibling writes or native tests. Capture every
attempt and cleanup. Select actual installed Python and mandoc; their host success
does not qualify Python 3.10 or 3.12, nor Aether manual lookup.

Current-task technical and rendering inspection is distinct from independent
reader/technical review, which remains pending. Runtime source is unchanged;
missing target/tool/minimum-version evidence stays in UL-061/062/063. New discovery
of a checker defect requires a separate behavior change with meaningful controls.
