# Native two-client connections evidence

2026-09-05. [Contract and reproduction](../../NATIVE-CONNECTIONS.md).
Six new AENMX001 / ABI 9 cases pass: two-client progress despite a partial request,
insufficient channel capacity, reserved-header rejection, malformed third ELF,
deliberate partial-frame rejection and corrupted file data. The positive runs two
generations with six reclaims. The corrupt-data log records client slot 2 exit 245
and supervisor 960/reclaimed 0; unrelated boot failures are not accepted controls.

Regressions pass: six program, six coexist, six process, nine init, four channel,
three read-only files, five writable files, seven lookup, five launch and eleven
memory cases. Twelve frozen legacy companion cases and the default two-core
framebuffer smoke pass. Host tests, 56 Python tests and all three offline standards
checks pass. Rust/Zig formatting and Python compilation pass.

`summary.json` pins suite reports, sources, tools and `producer-sources.tar.gz`.
Every captured suite source hash matched the working source before retention.
Small binary envelopes, ELF helpers, maps and logs are retained; large kernel/ISO
outputs remain at the private paths in reports. Explicit strict-musl/compiler
dependencies remain separate pinned inputs. No build discovers a mutable sibling
checkout or silently upgrades a standard.

The first draft lacked a TLS segment and was rejected by the strict ELF validator.
Adding explicit client TLS preserved that validator. An intermediate run predates
the final broker terminal check and is not acceptance evidence. Only the final
six-case run and source-matching regressions are captured here.

This is producer evidence, not independent userland or package adoption. The
legacy consumer retains its older ABI. No sibling sources or immutable pins
changed. Incremental client request handling does not promise nonblocking backend
or reply handling under arbitrary stalls. Shared descriptors, native shell,
inherited startup, persistent installation and ABI-6 policy composition remain
separate integration work.
