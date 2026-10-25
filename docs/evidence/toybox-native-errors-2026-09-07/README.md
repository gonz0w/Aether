# Actual Toybox native I/O errors

Pre-code contract, 2026-09-07. Qualify actual cat read/write EIO/EINTR and unknown
reply paths. Add opt-in toybox_applet owner cfg:16-byte fault/prefix accounting,
exact Toybox/musl error diagnostics and post-error stderr allowed only after known
errors. Existing eleven-byte conformance profiles remain unchanged. Rights,
generation, local/remote closure and four-reclaim rules remain authoritative.

Read error occurs after16 read/copied bytes; write error after32 read/16 copied.
Expected stderr is `cat: -: I/O error\n` or `cat: xwrite: I/O error\n`, with
`Interrupted system call` for EINTR. Unknown first read commits16 input/no output;
unknown first write commits16 input/output; neither permits diagnostic traffic.
Actual applet/xexit code stays upstream apart from the already qualified cleanup
seam. Add channel-counter assertion through local closure and a force-zero mutant.
Wrong expected diagnostic bytes must fail independent owner1505; false status0
must fail1501. No automatic retry, new grant/quota, installed libc or sibling edit.

Select normalcopy, read/write EIO/EINTR, four malformed/cut read/write cases and
two named mutants. Then prior actual-cat/public-stdio and full command regressions,
Zig/host/pins/workflow, Rust2024 rustfmt1.98.0 and pinned C format. Retain failures
before edits; freeze runtime sources during qualification. Foundations O/I/E and
DEVELOPMENT apply. The owner change is a scoped extension in existing Rust style;
no mass migration. Update STATE/NATIVE-CAT/workflow with explicit coverage limits.
Usage/options and finalizer failure/re-entry remain follow-ons, not completed by
these error witnesses. Original source BSD-2-Clause, upstream terms/pins unchanged.

## Native cases and authority

| Case | Independent owner observation |
| --- | --- |
| copy |32 input/output bytes, no diagnostic, terminal0/backend17, four reclaims |
| read-eio / read-eintr |16 input/output bytes, exact `cat: -: ...` diagnostic, terminal1, all aliases closed |
| write-eio / write-eintr |32 input/16 output bytes, exact `cat: xwrite: ...` diagnostic, terminal1, all aliases closed |
| read-malformed / read-cut |16 input/no output/diagnostic bytes, terminal1; owner cleanup after unknown read |
| write-malformed / write-cut |16 input/output bytes, no diagnostic bytes, terminal1; owner cleanup after unknown write |
| wrong-diagnostic |Deliberately false expected stderr rejects owner1505 after terminal1 |
| force-zero |Deliberately discarded nonzero applet status rejects owner1501 |

All positive/error cases repeat through two generations and four reclaims. Known
errors allow only role2 writes after injection. Any further input/output request
still rejects1530; byte/position checks catch missing or extra diagnostics. After
unknown completion, no exception allows diagnostic traffic. Existing transport
poison counters and the finalizer assertion cover upstream diagnostic attempts
through all local closes; remaining remote cleanup belongs to the supervisor.

The real Toybox/musl code supplies the error strings and exit status. Applet source,
writeall, callbacks, flush and private cleanup seam remain the previous qualified
versions. Only optional hook assertions/status mutation and owner accounting are
extended. Default conformance fault points remain11; this profile uses16 without
widening buffers, rights or native quotas. Numeric roles and names create no new
authority. No stdin/stdout retry is permitted after a known error; stderr may use
multiple bounded requests to finish its independently checked message.

## Final qualification

Attempt2 passes all11 cases: nine normal/error outcomes with two generations and
four reclaims, plus two exact negative oracles. Prior public stdio13, normal actual
cat7 and all211 command-runner cases pass. All98 host tests, Zig/pins, workflow35
groups, Rust1.98.0 edition2024 formatting and Clang-format21.1.8 pass. Four target
receipts agree on frozen sources. Only cat-roles.rs and optional cat-probe controls
changed; all other prior runtime sources, SDK identities and UL-059 artifacts
match the previous receipt. No kernel, installed SDK, pin or sibling was changed.

[Attempt1](attempt-1-triage.md) is a retained infrastructure/build failure: the
resolved rustc executable was invoked without rustup's runtime-library setup,
and rust-lld could not load libLLVM.dylib. No target ran. The established rustc
+1.98.0 launcher fixes the invocation; resolved compiler bytes are recorded and
rechecked. Existing cfg-specific unreachable-code warnings remain in raw logs;
no warnings were newly suppressed or treated as runtime success.

Default ELF remains85,400 bytes,22 load pages,4-byte PT_TLS. owner-artifacts.json
records every freshly compiled owner hash/size; the largest is6,056 bytes, within
the existing8,192-byte cap. No grants/quotas were enlarged. Native EIO/EINTR are
injected complete error replies, not proof of real device faults or signal delivery.
Mapped image sizes are not peak-memory or performance measurements.

native/public/cat/command receipts and logs retain actual inputs, commands, UTC
run boundaries and outcomes. qualification.json binds source/SDK/bundle checks;
final-artifacts.tar.gz contains frozen sources/, run-native.py and all four output
trees, including rebuilt owner binaries and prior upstream notices. The failed
archive retains its exact source/recipe/output set. Both archive source/recipe
inventories were verified. ISO, installed-boot duplicates and kernel.elf are
omitted while artifact hashes remain in receipts. Original envelope hashes name
seed inputs; final native-c hashes bind the newly rebuilt owners and client.

Reproduce with run-native.py and the exact public/cat/command invocations in
*-timing.json, including pinned SDK/tool lock. Run host checks with
`zig build test --cache-dir .zig-cache --global-cache-dir .zig-cache/global`.
Host/format timestamps remain unavailable, not invented. Connections/inherited
and earlier isolated stdio/startup suites were not rerun: shared kernel/loader/
transport behavior is unchanged; actual-cat/public and the complete rebuilt
command suite cover the affected owner/client paths. Independent consumer review,
usage adaptation, finalizer error/re-entry work, extended testing and full R1 remain
open. No change to the release roadmap or acceptance boundary is implied.
