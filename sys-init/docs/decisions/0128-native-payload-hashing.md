# 0128 — Streaming native payload hashing

BG-056 host slice, 2026-09-07. Replace whole-file digest reads with 64 KiB chunks,
a 64 MiB per-file ceiling, ordinary-file/component checks, nonblocking/no-follow
open and descriptor identity/metadata checks. Propagate the supplied checkout root
through audit hashing. Current largest listed artifact is 3,653,632 bytes.

Test digest compatibility, bounded read requests, oversized and special files,
replacement/growth and descriptor cleanup. Run focused and full checks. Preserve
catalog, retained evidence, release pins and native behavior. E-01–08 host scope.
Semantic JSON/serial/envelope reads still reopen inputs and are separate work;
this slice does not claim all reads are bounded, atomic snapshots or I/O deadlines.
Receipt validation, end consistency and independent review remain open.

Validation: 41 native-harness tests and all ten gates pass in run-wl7174yz.
Native audit stdout, catalog bytes and 24 native inputs stay unchanged. Four
manual commands pass. Evidence:
../evidence/native-payload-hashing-2026-09-07/README.md.
