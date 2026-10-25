# SI-07 opt-in client delivery — 2026-10-03

UL-058/UL-063: maintained v2 bootstrap/transport and static runner/bytecount.
This packet contains host execution and ELF linking/inspection only.
**Native SUSTAIN-01–06 remains NOT RUN.** Aether owns matched hooks, grants,
cohort selection/retirement, cleanup and authorized shutdown. No sibling changes,
service activation or SDK publication.

[Review before code](review.md), [pre-change source identities](before.json),
[explicit profile and pins](profile.json), [final results](final/results.json).
Reproduce with `python3 -B experiments/command-runner/check-sustained.py` and the
provisioned strict SDK. Python3.10+ source support; actual interpreter/platform/tools,
compiler flags, environment and owned cleanup receipts appear in results.

Both85-case host bootstrap/transport suites pass UBSan. Role2592 and result37716
controls, all65535epochs in the peer sweep and legacy decoder controls pass.
Three semantic mutations fail the expected bootstrap oracle: narrowing the parent
or child before validation, and child legacy-wire fallback. Mixed decoder/transport
links reject exact undefined v2 symbols. Static ELFs have no interpreter/dynamic
segment or unresolved externals. Formatting passes.21 command host cases and
parser/result/mapped regressions pass; local quality gate retained separately.

Delivered [v2 runner](final/v2-parent.elf):24280bytes,
SHA2565eff7f66d1649679e50dfdb6f9de94df761f508b3b28b25deac929423d27622b.
Delivered [v2 bytecount](final/v2-child.elf):13632bytes,
SHA256985ed35dee60ccc29bd0b625f30289bbab22c877dd694e8fd2dd0aa48b3db5df.
Frozen sources, objects, exact commands, output streams and receipts are included.
Original code BSD-2-Clause; pinned linked musl retains its own terms.

Legacy parent bytes match the previously native-tested ELF
4474b386ab1b49374f0c891a5878996f06eac79f334992245c7d52280fbfeb7d.
Legacy child bytes match a fresh exact pre-change-source build
1df22451fc4c1495749ae62ebe8bd47278eb1629032dbb037b96702a3fa7e205.
These are build identities, not new native executions. No changed payload ran native.

All attempts are retained: missing macOS auxv header fixed with a declaration-only
host shim; baseline child object order corrected; passing run; stricter SDK receipt
check rejected the alternative SDK copy; original native-c-xhkdw6jv receipt/stage
match required pins; two final passing instrumented runs. First parser regression
invocation omitted required --sdk (usage2); corrected invocation passes. Initial
packet-copy collision was local bookkeeping and did not alter any test result.

Next: Aether implements matched AERIO002/NIO2/0x7b hooks under proposed
AENSI001/ABI22 (or explicitly negotiates a new profile), qualifies five real cycles
including epoch3,65535completion/65536pre-effect retirement, stale/foreign/partial
controls, exact6\n stdout and0/0/17 terminals, complete reclaim and authorized halt.
Then userland independently consumes the frozen delivery. The runner stays finite
per connection; the owner provisions fresh coherent cohorts. Sys-init acceptance,
independent technical/reader review and broader UL-063 migration remain pending.
