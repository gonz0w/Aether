# Atomic command bootstrap evidence — 2026-09-06

Pass: 20 command cases, 9 inherited-launch cases and 6 connection cases. Kernel
host checks, 67 Python tests, three release-pin checks and workflow validation
pass. There was one attempt per suite, with no unexpected failure or retry.

The three malformed-second-binding cases require child witness 95: both bindings
remain unpublished, public operations return EBADF, read storage stays unchanged
and channel-call count stays fixed. A deliberately broken early publisher requires
witness 97. All four then require parent 69 and broker 970/reclaimed 0. Expected
workload rejection is not a product failure, remote reclamation or recovery claim.

See [the contract](../../NATIVE-COMMAND-IO.md#atomic-bootstrap-test-plan).
`results.json` binds source hashes and the source archive to the complete suite
reports. Profile directories retain raw serial/build/static-analysis logs, native
payloads, kernel and client ELFs, maps and broker bytes (files under 2 MiB); ISO
images are rebuildable and omitted. Original complete output paths remain in the
summary. The source archive contains final source, tests, contracts and the active
approved standards snapshot; it does not contain the external SDK or tool binaries.
Suite reports bind their existing SDK receipt and tool digests. No sibling pin was
updated and this is not independent consumer or physical-hardware acceptance.

`*-attempt.json` records exact command, UTC start/end and exit status for each
suite, captured around execution. Logs retain all attempts. Sources were frozen
through all qualified runs. `format-attempts.json` and `format.log` record pinned
clang-format 21.1.8 checks: approved configuration for the new probe, existing LLVM
format for the two edited legacy C files. No new unsafe boundary or dependency was
added. Full standards compliance, extended fuzz/soak and reader reviews remain
separate work as recorded in DEVELOPMENT.
