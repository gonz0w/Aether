# SDK-08 closure selection — UL-005, 2026-09-07

Consumer pins for the imported-SDK io_probe ELF are verified against the libc
receipt and live adapter sources. Historical native-memory kernel contract is
absent; live Aether NATIVE-C.md has drifted and is not selected. Intended native
cases remain NOT RUN. Three mutants (native pass, wrong ELF hash, equating live
and historical contracts) are rejected. No sibling copy, ELF execution or pin
change.

| Attempt | Result |
| --- | --- |
| sdk08-closure-qzl8js6b | pass |

SDK-08 execution waits on an isolated, reviewed producer snapshot.
