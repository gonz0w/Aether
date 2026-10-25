# SDK process integration review — 2026-09-10

The [implementation selection](../../NATIVE-SHELL-STARTUP.md#sdk-process-integration-selection--2026-09-10)
chooses an isolated native staging hook inside musl `_Fork`, retaining upstream
`fork` orchestration and child repair. This is the next producer experiment;
no SDK installation, runtime implementation or affected-owner approval occurred.

Inspected native musl 1.2.6 sources and six compiled process objects. `_Fork`
disassembly contains the native0x10039 trap between signal blocking/abort-lock
acquisition and child repair/mask restoration. Its scalar return does not capture
the fresh grants returned by the private copy operation. The current fixture
repairs TID itself and clears child FD10 CLOEXEC before readiness; neither sequence
can be transplanted unchanged into the public call. Preserve inherited flags at
fork and keep cached-TID/robust-list/thread bookkeeping with libc.

The separate vfork object invokes native0x1003a directly, bypassing `_Fork`.
Waitpid uses the cancellation-aware wait4 path; wait4 can request rusage. Execve
has no transactional replacement implementation in the inspected kernel. These
findings define explicit later work, not successful stubs or runtime acceptance.
The next public fork candidate can proceed without OpenZFS; independent SDK/dash
intake and source-built dash fork/vfork configuration remain userland-owned.

Host checks pass, including 98 Python tests, Zig tests and offline standards/workflow
checks. The four-file simplicity snapshot and its manifest digest verify. Six object
disassemblies, exact commands/timings, input hashes and archive readback are retained.
The source archive includes upstream musl COPYRIGHT without relicensing its files.
The collector identifies the inspected libc archive and disassembler by digest.
This is selected source/object inspection, not an SDK rebuild or provenance closure.

No new QEMU run was selected for this documentation-only review. The preceding
[132 connections/five launch packet](../signal-incomplete-2026-09-10/README.md)
remains the latest runtime evidence. No runtime code, sibling files or released
pins changed. Existing dirty work is preserved. Missing implementation, consumer
review and full dash/R1 acceptance are explicit gaps, not waived requirements.

Reproduce the local review with the captured SDK path available:

```sh
python3 docs/evidence/sdk-process-review-2026-09-10/review.py
```

The script records evidence for the current inputs; it does not install or patch
the SDK. inputs.json binds this review to 33 files; checks.json records each command.
After review, manifest.json seals the packet. Re-execution changes evidence bytes
and requires a new reviewed receipt rather than treating the old seal as valid.
