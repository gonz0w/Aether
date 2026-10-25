# Pipeline final stdout grant — 2026-09-15

The last libc replacement now forwards pipeline bytes through actual musl write
to an explicitly granted stdout destination. After its validated exec descriptor
table, only slot4 receives a16-byte reference/binding/write-right/capacity record.
The client checks every field before installing FD1. This is a new post-exec grant,
not inherited standard descriptors. The other workers receive no such grant.

A private owner capture authenticates the dispatcher participant independently of
frame references. The writer deliberately forges the final output reference on
its own channel and must receive canonical EACCES. The final worker verifies that
stdout is write-only, forwards each input chunk and explicitly closes stdout.
The owner independently requires exactly pipe data newline, one denied forged
request, and explicit close before accepting all child terminals.

Capture capacity is32 bytes and request bound16. Unsupported operations, malformed
padding, wrong caller/reference/binding, closed output and overflow reject before
write effects. Completed replies use the existing partial-send retention and are
never reapplied. The new code is a small private bounded sink, not a general stream
service. Numeric FD/reference knowledge alone gives no authority.

## Qualification

Commands:

- `python3 scripts/pipeline_capacity.py --libc-build /Users/cam/DEV/Aether-userland/build/native-c-5olokhku --tools-lock zig-out/init-capacity-2026-09-06/tools.lock.json`
- `zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`

All36 native cases pass on final sources; target case total is93.733 seconds.
Positive requires exact captured bytes and fifteen normal reclaims across three
generations. Malformed grant rejects child105 then owner2734 before data/reclaim.
Dropped write acknowledges without capture and fails owner2743 despite successful
worker exits. No failed attempts occurred; intentional rejection logs are retained.
Host run returns0 with104 checks. Exact build/artifact identities, Rust1.98 and
Clang-format21.1.8, pin/workflow/simplicity checks and frozen input verification
accompany the seal. Kernel mapping remains8007680 bytes.

## Compatibility and limits

There are279 frozen runtime inputs.22/46 earlier top-level ELF/raw images are
byte-identical; the24 changed images are private capacity owners. All earlier
client ELFs are unchanged; changed owners require the full native regression run.
New positive and malformed-grant owners are14264 bytes; dropped-write owner12672,
all within16384. Five private capacity files change, including the new output.rs.
No kernel/shared adapter or pipe core/SDK/dependency/quota/sibling/pin change.

The destination is a bounded in-memory capture, not serial console output. Full
inherited stdin/stdout/stderr, actual dash, child-driven builtin/exec scheduling,
concurrent blocking wait/data scheduling, signal interruption and unchanged
pipeline/early-reader scripts remain integration work. SIGPIPE/status composition,
matching full suites and independent SDK/userland intake remain open. Persistent
storage/OpenZFS, packages, recovery and sys-init assembly remain R1 requirements.
No full-dash or release claim is made.

The preimplementation review and result are in NATIVE-SHELL-STARTUP. Source and
review archives retain runtime inputs and local guidance/test support. collect.py
verifies every generated file against its archive before deleting only this run's
owned duplicate output root; cleanup.json records it. Existing sealed packets are
unchanged. SHA256SUMS covers all packet files except itself.
