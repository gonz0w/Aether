# Sys-init-owned bounded Dash script

2026-09-09. Three fresh native cases pass with the sys-init paired owner. The
positive supervisor is8176 bytes under the original8192-byte code limit. Original
4 KiB stack, three worker slots/six channels, lifetime bounds and released pins
remain unchanged. This is a bounded script integration, not interactive/sustained
shell or full AECAT004 failure/recovery qualification.

The script-owner.patch applies only to the previously verified219-file source
packet. The maintained Rust binding uses shell slot0/Runner and stream1/file2
Backend owners. Fixed bindings carry image/slot independently of lifecycle role;
both providers retain backend_eof authority. Native::launch_at factors existing
launch behavior and returns Known EINVAL for an out-of-range local slot before
any syscall, rather than panicking on indexing. A binding/role mismatch also
returns local Known EINVAL. These are prevalidation errors, not captured kernel
errno receipts; normal native errors retain their original classification.

Three identities and owners persist across both generations. Launch and terminal
observation use retained ownership. Protocol cleanup/readback still precedes
shell cleanup; explicit stream EOF/terminal17/reclaim precedes file-service
EOF/terminal17/reclaim. File references and native handles remain separate.
The selected shell's expected terminal is decoded0/kind1. Missing-root shell2
rejects1501 as before; missing-close shell0 rejects1599 before native reclamation.
Other producer signal/cancellation modes are not supported by this narrow patch.

| Case | Native result |
| --- | --- |
| script | Exact hello-newline file evaluation; shell0/stream17/file17 twice, no live file records, supervisor100/reclaimed6. |
| missing-root | Existing1501/reclaimed0 rejection after shell2. |
| missing-close | Existing1599/reclaimed0 rejection after shell0; no recovered-cleanup claim. |

Native report contains exact commands, terminal sequences and ISO hashes. Raw
supervisors/envelopes and serial/build logs are retained. ISOs remain private.
The original Dash/service ELFs are reused byte-for-byte inside their envelopes;
the owner and selected kernel are rebuilt from local frozen inputs. This is not
a fresh Dash/libc source build, broader userland acceptance or a369-case rerun.
All original source members verify; staged originals match except the explicitly
patched cat-roles.rs. Native helper verifies boot dependencies and QEMU version;
the builder additionally pins Rust/Zig/QEMU executable hashes before execution.

Initial enforced link failed at8320-byte sizing; direct decoded terminal use and
removal of request clearing reduced it to8208. Each request is fully overwritten
before dispatch and used is reset; the EOF/partial-request check remains. Inline
layout experiments and opt-level=z did not fit. Checked slot lookup removed the
remaining panic indexing path while retaining validation, yielding8176. Sizing-only
raw files were never booted. All failed attempts remain retained. Existing memcpy/
memcmp symbol warning and fixture unreachable/dead-code warnings remain visible.
No new unsafe sites are introduced.

Five existing bytecount/stop supervisor variants build byte-identically after
launch extraction: positive, empty, fault, stop and stop-retirement control. That
also preserves the shared positive image for existing wrong-role/omitted-close
cases. Compatibility is not a claim of rerunning those unchanged native images.

SE review: reuse the paired owner and existing service protocol with a small
fixed binding. A second manager, broad fixture import or new filesystem is not
necessary. The exact patch replaces direct success-only lifecycle operations;
source hashing prevents applying it to an unreviewed producer version. Decoded
terminal state and overwrite-before-dispatch remove redundant work. Local slot
validation improves failure handling without expanding authority. O-04/I-04
ownership/completion, I-05 bounds and E-01–08 frozen evidence remain applicable.

Next: qualify partial provider/shell launch and stop cleanup on this composed
configuration before expanding its claims. Existing owner component probes do
not prove the new file-bridge interruption policy. Producer V4 malformed/lost
replies, external commands/pipes, ENV, interactive TTY and sustained shutdown stay
separate. No sibling change, new shared rule or independent review is claimed.
Full local checks and final integrity verification follow.

Final validation: all ten local gates pass in run-vuoylxon with checked sources
unchanged. Three fresh native cases pass; five earlier command/stop images remain
byte-identical. Final staged/source copies and all released locks verify.
`git diff --check` passes. No independent review, full shell or sustained-boot
acceptance is inferred. sha256.json seals retained files excluding only itself.
