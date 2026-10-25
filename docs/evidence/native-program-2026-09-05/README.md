# Program beside file service witness

2026-09-05. [Contract and reproduction](../../NATIVE-PROGRAM.md).
Six new cases pass: simultaneous program/file activity across two replacement
generations, wrong third executable, malformed third ELF machine, reserved header
word, truncated envelope and omitted program stop. The positive result requires
five reclaims; negative controls require their specific preflight or broker failure.

Regressions pass: six coexist, six process, five launch, seven lookup, four channel,
three read-only files, five writable files, seven init, eleven native-memory and
twelve frozen legacy companion cases. Default two-core smoke and framebuffer
verification pass. Host tests, 44 Python tests, three offline standards checks,
Rust/Zig formatting, Python compilation and CLI help/mode rejection pass.

`summary.json` pins the producer archive, individual source files, suite reports
and tool versions. All captured suite source hashes were checked against the
final working sources before retention. The archive contains kernel, fixtures,
scripts, boot/toolchain pins, tests, native contracts and offline standards.
Strict-musl/compiler dependencies remain separate pinned inputs. Small binaries,
maps, reports and logs are retained; large ISO/kernel outputs remain at the
private paths recorded in reports.

`attempts/reclaimed-metadata-fault` retains the initial failed replacement run,
not acceptance evidence. Reclaimed image metadata caused a later image load to
restore read-only aliases for retired backing. Clearing that inventory during
reclaim fixes the kernel fault; the second program generation exercises the
ordering that exposed it.

This is Aether producer evidence for AENPG001 / ABI 8. The frozen legacy consumer
regression does not establish independent adoption of ABI 8. No sibling sources
or immutable standard/consumer pins changed. This separate profile permits three
workers and two immutable broker code pages (5160 bytes in this capture); old
profiles retain their limits. Shared descriptor inheritance, normal command
completion, shell pipelines and persistent installation remain separate work.
