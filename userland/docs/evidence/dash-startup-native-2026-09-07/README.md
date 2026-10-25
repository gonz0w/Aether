# UL-007 independent native startup qualification — 2026-09-07

PASS: all222 captured command-runner cases, including nine startup cases, execute
locally against the matched producer/SDK/adapter pair. The unchanged userland
startup probe returns0 in both normal generations. This is independent consumer
reproduction of the bounded prerequisite, not native dash or full UL-007 acceptance.

| Startup case | Observed terminal/oracle |
| --- | --- |
| Normal | Probe0 in generations1/2; owner100, four reclaims |
| Bad PID | Probe10; expected owner rejection1501 |
| No-op disposition | Probe20; expected owner rejection1501 |
| No-op mask | Probe21; expected owner rejection1501 |
| Missing CLOEXEC | Probe30; expected owner rejection1501 |
| Rights / FD / stale generation / missing role | Admission110 in generations1/2; owner100, four reclaims |

The wrapper additionally exercises real alias reads after FD0 closure, denied
writes through the input alias, flags, descriptor exhaustion, last-alias remote
close, identity generation and state reset. The owner checks exact stream content,
terminal kind/status and closes. Mutants deliberately cause profile rejection;
their rejection records are not successful four-reclaim lifecycle witnesses.

Run `python3 -B experiments/dash-native/run-native.py`. Final work:
`build/dash-startup-native-02k2tw4o`. The captured original producer script is
unchanged. Host `zig build test` passes, including98 Python tests and62 Zig tests.
Both outer commands exit0 with complete cleanup. Native child records preserve
producer schema; per-case wall-clock/owned receipts are not invented.

[Results](results.json) record exact argv/environment, Python/tool hashes,503 source
pins,4311 regular SDK file hashes and wrapper/driver identities. All source pins
and SDK regular hashes still match after execution. [Native results](native-results.json)
retain222 outcomes and artifacts; raw serial/QEMU logs are in cases/. Full build/
inspection logs, ELFs, envelopes and ISOs remain in the private output path named
by the receipt. [Startup cases](startup-cases.json) selects the nine results without
relabeling the full command suite as shell tests. [Review](review.md) records scope.

Two setup failures remain: attempt1 rejected the known musl-audit archive root
before execution; attempt2 selected an old system Python and failed five host
identity tests before native execution. Attempt3 selects explicit Python and
passes. No failed native case occurred in this consumer run. The producer's earlier
missing-TLS failure remains in its separately captured packet.

The native facade supplies DFL/IGN disposition and stored masks only, with explicit
unsupported-handler rejection. It does not supply signal delivery, internal musl
signal-mask adoption, UID/GID, fork/vfork/exec/wait or exec-time CLOEXEC enforcement.
Actual dash work remains with the producer; consume its next matched delivery
against real shell workloads. Independent review and release/package gates remain
open. No sibling source, shared pin or real-prefix installation changed.
