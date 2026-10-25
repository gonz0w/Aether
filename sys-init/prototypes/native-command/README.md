# ABI9 command owner candidate

BG-067 bounded native integration; see [review](../../docs/INIT-COMMAND-ADAPTER.md)
and [capacity evidence](../../docs/evidence/command-owner-capacity-2026-09-08/README.md).
The scalar-helper build now fits the original8192-byte limit and passes five
native cases; see docs/evidence/command-owner-native-2026-09-08. Earlier oversized
images remain unaccepted. No production command is installed by these files.

`success.rs` derives from Aether's `user/native-command/success.rs`, frozen in
`docs/evidence/init-command-intake-2026-09-08/producer/sources.tar.gz` and pinned by
its source map. Original BSD-2-Clause notice retained. Local edits replace lifecycle
calls with the sys-init paired owner; protocol validation/readback oracles remain.
`lifecycle.rs` is the local ABI9 adapter, imported by that success submodule.

The capacity-study recipe stages these files alongside the unchanged producer
supervisor/command modules and copies sys-init service_owner.rs/connection_owner.rs
beside lifecycle.rs. These contextual modules are not standalone crate entry points.
Native traps remain in the frozen producer supervisor. Local reader/writer/worker
handles are nonzero values; borrowing protocol handles never transfers ownership.
The fixture caller settles file-reference policy before invoking owner cleanup.

Close/reclaim errors are conservatively Unknown, retaining outstanding state and
forbidding automatic replay. Negative launch/allocation results rely on the pinned
kernel's no-transfer-on-error contract. Actual signed native values remain in
NativeError; malformed success values are not fabricated errno receipts. Native
partial-launch/cleanup-error/stop controls remain unqualified. Five current cases
execute on the unchanged4 KiB stack; no high-water or broad stack claim follows.

The `success_stop` first-read cancellation candidate is compile-selected only.
It currently fails the enforced8 KiB link (8336-byte sizing-only result); neither
its runtime oracles nor `success_skip_retire` control have native acceptance.
See [capacity record](../../docs/evidence/command-owner-stop-capacity-2026-09-08/README.md).

The later [native stop record](../../docs/evidence/command-owner-stop-2026-09-08/README.md)
resolves the above capacity block at8176 bytes. Seven native cases qualify the
changed code, including the retirement omission control. Completed request frames
are borrowed; decoded owner terminals are used directly. Sustained idle and
operator shutdown remain outside this bounded fixture.

## Bounded script owner

`script_lifecycle.rs` and `script-owner.patch` compose the paired owner with the
verified AECAT004 script configuration. Apply the patch only against the source
hash in the retained [builder](../../docs/evidence/dash-script-owner-2026-09-09/build-script-owner.py);
its three selected configurations are script, missing-root and missing-close.
Do not enable other producer cat-roles modes with this patch. The existing
protocol stays frozen; no copy of its complete mode framework is maintained here.

Three native cases pass at8176 bytes with separate EOF-driven stream/file owners.
Partial launch and file-protocol stop cleanup remain next. Full reproduction
requires the locally frozen intake/source and boot inputs described in the
[review](../../docs/DASH-SCRIPT-ADAPTER.md); producer-image replay alone is not
this sys-init owner acceptance.

`script_launch_probe.rs` adds compile-selected startup-prefix rollback probes.
The exact five-case [runner](../../docs/evidence/dash-script-launch-2026-09-09/run-script-launch.py)
qualifies kernel-rejected startup at each position and two cleanup omission controls.
Normal script images remain unchanged; success-only entry points do not silently
acquire automatic rollback. Stream startup handles require closure before EOF.

The patch also supports `script_stop` and its `script_stop_skip_close` control:
stop at the first complete file-read request after open, before any backend effect.
The [native witness](../../docs/evidence/dash-script-stop-2026-09-09/README.md)
qualifies terminal observation and live-file retirement at the unchanged8 KiB
limit. This selection is not an operator control interface or general IPC cancel.

ABI17 opt-in: apply script-abi17.patch instead of script-owner.patch to the frozen
September9 script sources; select the verified September11 capacity kernel and
large-linker.ld, and encode AENMX002. Bootstrap must be17 with unchanged grants.
This selection uses start_next for ordinary startup rollback; the original ABI9
patch is retained. Exact staging, cases and limitations are in
docs/evidence/dash-startup-abi17-2026-09-11/README.md.

## Startup error coverage — 2026-09-11

Six native denied-grant allocation cases cover both channel positions at all
three startup slots; three injected Unknown responses exercise fail-closed startup.
Ten prior supervisor images rebuild identically. First-attempt errno expectation
was corrected from EPERM to the actual EACCES; its failure is retained. See
`docs/evidence/dash-startup-errors-2026-09-11/README.md`. Synthetic Unknown responses
are not kernel ambiguity witnesses. No production behavior or released pin changes.
Next product boundary: sustained wait/reuse/authorized shutdown and useful-session
integration; additional framework and broad failure campaigns remain outside scope.

## Opt-in sustained ABI22 consumer

success.rs also supports the frozen ABI22/v2 producer context via init_sustained
and init_sustained_v2; sustained_owner.rs implements its private fixture wait/input
and paired-owner cohort rejection. Both flags are selected together with the
matching producer supervisor/bootstrap modules; this is not a standalone crate.
Use the exact staged source and commands in
[consumer evidence](../../docs/evidence/si07-owner-2026-10-03/README.md).
Four native cases pass; five legacy ABI9 variants remain byte-identical. Code and
linked stack fit the unchanged ABI22 bounds. The console is developer-only and
halts after the bounded fifth cycle; a general request loop remains BG-067 work.

The [request-loop follow-up](../../docs/evidence/si07-loop-2026-10-03/README.md)
supersedes the fifth-cycle-only input policy: r runs one fixed workload, h halts
before further admission, including before the first command. Invalid bytes fail
closed. The console and startup idle probe remain developer fixtures; finite
private epochs and all ownership/grant bounds remain unchanged.
