# Inherited stdin and stderr — 2026-09-15

The parent now receives bounded read-only stdin and write-only stderr descriptions
alongside stdout. Full reference/binding/rights/capacity validation precedes descriptor
installation. Existing live snapshots reserve actual parent holdings before copies.
Exec retains stdin only for the writer, stderr for all three stages and stdout only
for the last stage. Parent independently closes all three holdings before dispatch.
Replacement descriptions report those retained holdings rather than create authority.

The writer uses actual musl read to consume pipe data newline from the10-byte input
source, checks EOF, closes stdin, and sends those read bytes into the pipeline.
The final worker still writes exact stdout to its separate32-byte capture. Each
stage writes its role byte to stderr and closes it. The owner checks all three
unique diagnostic bytes independently of stdout, input consumption/EOF and pipe
counters. All standard-stream holdings must be gone on successful completion.

A relay forges a zero-length read using the original stdin reference after exec;
it must receive canonical EACCES. Reference knowledge cannot restore revoked access.
Deliberately retaining that input holding makes the client's probe reject126 and
the owner reject2726 before reclaim. Another control acknowledges diagnostic writes
without capturing them; independent stderr accounting must reject owner2743 despite
normal worker exits. A zero-length forged read avoids consuming legitimate input
when the deliberately broken authority control succeeds.

## Qualification

Commands:

- `python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json`
- `zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`

All41 native cases pass on final sources; target case total is106.472 seconds.
Retained relay input rejects child126 then owner2726; lost diagnostic capture
rejects owner2743 despite normal exits, both before reclaim. Positive requires
exact input/EOF, independent captures and fifteen normal reclaims across three
generations. Host run returns0 with104 checks. No failed attempts occurred;
intentional rejection evidence remains. Sources, exact commands, tools/SDK identity,
timestamps, native envelopes/ISOs and serial hashes are retained. Kernel mapping
remains8007680 bytes.

## Compatibility and limits

280 frozen runtime inputs; seven private capacity files change, including the
shared local description-validation header. All54 earlier top-level ELF/raw images
are byte-identical. Positive owner16096 bytes, retained-input owner16176 and dropped
stderr owner16032 remain within16384. No kernel/shared pipe core or adapter/SDK/
dependency/quota/sibling/released pin change. Requests remain16 bytes; stdout and
stderr captures are32 bytes each, input is10 bytes and state is generation-local.

The existing owner remains authoritative for all holdings; no global table or
second FD ledger is introduced. Both stdin/stderr before/after plans are checked
before their holdings change. Client descriptor allocation now handles occupied
FD0–2 using temporary CLOEXEC aliases that are closed before each fork snapshot.
All I/O uses existing guarded, bounded synchronous transport. Native copy, exec
publication/readiness and terminal observation rules remain unchanged.

This is inherited standard-stream evidence for a bounded private pipeline, not
actual dash or console/TTY input. Child-driven builtin/exec scheduling, concurrent
blocking wait/data scheduling, signal interruption, unchanged pipeline/early-reader
scripts and SIGPIPE/status composition remain integration work. Full matching
suites and independent SDK/userland intake remain required. Persistence/OpenZFS,
packages, recovery and sys-init assembly remain R1 work. No full-dash/release claim.

Preimplementation review and outcome are in NATIVE-SHELL-STARTUP. Review/source
archives retain guidance and test support. collect.py verifies every generated
file against its archive before deleting only owned duplicates; cleanup.json
records verification. Prior packets remain untouched. SHA256SUMS excludes only
itself. Final checks bind Rust1.98 edition2024, Clang-format21.1.8, offline pins,
simplicity snapshot, workflow, whitespace and frozen runtime sources.
