# Combined carrier/forwarding/results — 2026-09-06

Pass: 55 command cases, 9 inherited-launch cases, 6 connection cases, kernel host
checks, 73 Python tests, three release-pin checks and workflow validation. Pinned
format checks pass. One attempt per suite, no failure or timeout. Combined broker
7544 bytes within 8192; kernel ABI and quotas remain unchanged.

Three combined cases forward two/four child arguments, retain empty/31-byte
payloads, verify argv termination and sole LC_ALL=C environment, and map normal
0/64 or actual #UD kind 2/detail 134 to 1. Caller request mutation after spawn
must not affect child startup. Exact two-generation child/parent/backend terminal
records and broker 100/reclaimed 6 are required. A changed fourth argument must
produce child 80, parent 1 and broker 970/reclaimed 0. Generic failure cannot pass.
All 51 previous cases remain included.

[Contract](../../NATIVE-COMMAND-IO.md#combined-startup-and-result-forwarding).
Forwarding offsets are explicit fixture inputs, not public CLI parsing. This
qualifies the producer combination; userland parser and independent adoption,
help/output grants and error/recovery evidence remain separate work. No sibling
implementation, pin, shared standard or release acceptance was changed.

`results.json` binds suite reports and final source archive. Profile directories
retain serial/build/static-analysis logs, native payloads, client/kernel ELFs,
broker images, startup artifacts and maps under 2 MiB. ISOs are rebuildable and
omitted; complete output paths remain recorded. Source, tests, contracts, UL-059
snapshot and approved standards review are archived. External SDK/tools remain
bound separately by suite receipts/digests. Startup inputs retain exact size/hash
and explicit embedding environment. Commands and UTC start/end/status are captured
in `*-attempt.json`, pinned format checks in `format-attempts.json`. This is
producer/QEMU evidence, not independent consumer or physical-hardware acceptance.
