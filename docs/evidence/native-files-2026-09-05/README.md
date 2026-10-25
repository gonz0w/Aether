# Read-only Rust file-service witness

2026-09-05: three file-service cases pass: positive file requests, corrupted-data
rejection and partial-frame rejection. Five launch, four channel, eleven memory,
twelve frozen userland consumer cases, kernel host tests, 44 Python tests, three
standards checks and default two-core/framebuffer acceptance also pass.

[Owner contract and commands](../../NATIVE-FILES.md). Source, tool, image and
serial hashes are retained with command logs and linker maps. Sources/serial
identities were rechecked during retention; larger artifacts remain at the private
paths named in the reports. The Rust file service is a kernel conformance fixture,
not userland's libc file facade or a persistent filesystem. Companion regressions
use their prior profile and do not imply adoption of the new service protocol.
No sibling source or pinned release changed.
