# UL-062 host static, resource, concurrency and transport-stress plan

Before behavior work: add host extended fixtures and a new driver only. Keep
runner-parse.c, native-io.c, parser-extended.c, sibling repositories and release
pins unchanged. Prior parser sweep/replay evidence stays bound to those sources.
This does not finish UL-062 or qualify ASan.

Applicable requirements: Foundations E-01–08, I-03; Testing TD-01–05, TC-01–03,
TE-01–05; Coding CE-02–09, CC-01–04, CP-01–03; Documentation DW/DS/DP; Experience
for the new contributor CLI. Original work is BSD-2-Clause. Reuse pinned Clang
21.1.8, clang-tidy 21.1.8, Apple SDK, Python standard library and process.py.
No dependencies are fetched. This slice's executed C fixtures use UBSan only;
ASan remains the known host timeout and is not an automatic fallback.

PXS-01: clang --analyze and clang-tidy (pinned checks
clang-analyzer-core.NullDereference, core.uninitialized.Assign, core.DivideZero,
unix.Malloc) on runner-parse.c, parser-extended.c and parser-reduce-oracle.c
produce no warning/error diagnostics.
PXS-02: an isolated null-dereference canary must emit the analyzer null-deref
diagnostic on both tools. Exit 0 with a warning is not success for the canary;
silence is not success for clean sources.
PXB-01: after bounded parser decodes, getrusage ru_maxrss is recorded and must
stay under 32 MiB and above 0. Darwin reports bytes. This is an observational
budget, not kernel rlimit enforcement (setrlimit RLIMIT_AS/DATA are unsupported
here).
PXB-02: mmap-and-dirty 128 MiB must report ru_maxrss at least 64 MiB. mmap
without dirtying must not satisfy that grow oracle.
PXC-01: eight forked children each decode a valid carrier and reject a reserved
byte; all exit 0; parent wait status is the oracle. Parser statics are not shared
across children.
PXC-02: an infinite-loop child must hit a 5-second owned-process timeout with
complete process-group cleanup. Timeout is harness health, not product success.
PXT-01: after ordinary parent bootstrap, 256 native_exchange 32-byte rounds
succeed with exact 3072 channel_raw calls (5 writes of limit 7, 7 reads of
limit 5 each). Connection remains usable.
PXT-02: invalid exchange size poisons without further channel_raw; a forbidden
follow-on call is rejected. No native execution.

Commands: python3 -B experiments/command-runner/check-extended-host.py from the
repository root. Repeat with Python 3.10.21. Format new C, quality gate,
Experience help/version/usage 0/0/64. Each child: 30-second wait except PXC-02
at 5 seconds; 16 MiB output caps; complete cleanup. Hang control must not pass
the 30-second default. No VM or network. Suite budget 3 minutes.

Technical self-review covers analyzer diagnostic matching, RSS unit, fork/_exit
and wait status, channel call counts, poison/no-replay and process ownership.
Independent review remains pending. Retain failed and successful attempts.
Update EXTENDED, coverage, PROCESS, BACKLOG and STATE with actual evidence and
remaining ASan, broader stress, native compensation review and weekly-cadence
gaps.
