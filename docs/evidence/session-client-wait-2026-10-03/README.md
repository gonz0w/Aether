# Private ABI24 SESSION client wait adaptation

Before-code assessment,2026-10-03. Requirement: compose the existing private
Aether SESSION client with009 endpoint waiting and retain a real dash prompt during
human idle. Aether owns this fixture; the extracted ABI23 runtime is userland-owned
and is not modified or relabelled as accepted ABI24. Sys-init policy, SDK promotion,
persistence and release assembly remain separate. Released pins and siblings stay
unchanged. Foundations O/I/E, local DEVELOPMENT and SE-01–05 apply.

Select compile-time SESSION_CHANNEL_WAIT only with SESSION_SERIAL and
PIPELINE_STREAMS. Verify009 behavior before client bootstrap by probing the new
operation with an unheld factory-as-endpoint (expected EACCES, not ENOSYS). On
transport EAGAIN wait on the same held read/write endpoint, then rescan the original
buffer and retained offset. No arbitrary poll counter/yield in this selected path;
old profiles retain their exact bounded behavior. No new grants or kernel changes.

Wait0 is a hint, never a byte count. Any other wait outcome, including unexpected
EINTR, poisons this synchronous transport and returns existing failure/EIO. Do not
restart a partially transmitted request or inject a handler inside the frame.
Existing one-context signal guards remain authoritative; this adaptation does not
provide general POSIX EINTR/SA_RESTART, job control or async signal delivery. Buffer
ownership stays synchronous, local and live until move returns. Partial progress,
EOF, peer loss and ambiguous effects must not be hidden as successful transfer.

Simpler alternative: remove only the counter. Insufficient because it burns CPU
while the human is idle. Use the already qualified endpoint wait and current
transport offset; no new runtime framework or generic polling abstraction. This
removes the selected fixed budget/yield assumption; legacy code remains for actual
consumers. Added cost is a compile-time branch and one profile guard, no new state,
allocation, service or dependency. Existing compact C formatting remains scoped;
no whole-header migration. No formatter is invoked on these legacy files; preserve
the header's two-space and client's four-space formatting under the existing local
migration scope. Toolchain Clang/LLD21.1.8, C11/GNU scope, warnings-as-errors;
Rust owner1.98/edition2024 unchanged. Upstream dash/musl bytes/terms stay pinned.

Tests: focused real move() C host fault schedules for partial read/write/wait,
interruption/closure poison and no traffic after ambiguity; native promptly fed
and delayed prompt input, real exec/pipelines/substitution/state/PID/stderr/exit
and cleanup; old11 serial cases and full host/pin/workflow checks. Kernel unchanged,
so no unrelated M4 rerun is selected unless a runtime/kernel defect requires edits.
Freeze sources during target runs and retain all failed attempts. Document the
private macro, consuming-runtime gap and next action in references/STATE. No public
script entry point or launch profile is added. ## Qualified private composition

Three positive native schedules pass against fresh worker/owner builds:
short-session593 ticks, delayed4489 ticks/3905 idle, wide-output889 ticks. Each
confirms ten terminal/reclaim identities and authorized halt. Delayed first input
arrives35 seconds after the actual dash prompt, with two-second waits at subsequent
prompts; real external helper execution, pipelines, substitution, variables/PID,
stderr and exit all complete with exact UART bytes. Wide output adds161 stdout and
65 stderr bytes beyond former fixture observation caps. This is a healthy private
prompt-idle witness; it is not actual sys-init policy or canonical runtime adoption.

The freshly rebuilt macro-disabled client reproduces early idle termination at1339
ticks, one reclaim and only `$ ` (`client-limit`). Wait-enabled clients on ABI23
reject before bootstrap through terminal143, no prompt and the exact old-profile
owner rejection (`legacy-denial`). Missing SESSION_SERIAL rejects compilation with
the named selector error. All11 old ABI23 cases pass using fresh owners and exact
sealed worker payloads; the new focused host test separately verifies unchanged
legacy100000 transfer/yield exhaustion. Kernel/build bytes are identical to the
previous endpoint-wait packet, so no new M4/ABI22 run was selected this turn.

Seven focused move schedules (six selected, one legacy) execute the actual header
function with trap scripts: partial read/write, repeated EAGAIN after a readiness
hint, retained offsets, unexpected EINTR/authority loss, partial EOF/negative
completion and poisoned-connection silence. They do not claim general POSIX signal
or malicious-server liveness. Three retained strict trace comparisons plus13 named
controls pass (including the actual old-polling trace rejected for halt totals). Full `zig build test --cache-dir .zig-cache --global-cache-dir
.zig-cache/global` passes133 Python tests plus configured Zig/Rust/pins/workflow.
Simplicity hashes and final workflow checks pass; no released-pin changes.

Every worker build verifies all647 source/input/object members of the sealed local
runtime-review archive before linking. That archive retains pinned musl SDK/libc,
dash objects, CRT, memory/public-fork objects and notices. Only the private local
SESSION client is freshly compiled/replaced; no mutable sibling build/source input
is consumed. The existing sealed candidate compile recipe uses C17, GNU features,
Clang21.1.8/LLD21.1.8 and warnings-as-errors. That retained recipe is used explicitly
here, rather than implying a repository-wide C language migration. The shared
component validator has not accepted a new public ABI24 runtime profile.

Selected parent ELF252488 bytes versus polling252296; helper23032 versus22976.
No new transport state/allocation/local buffers. Owner raw15184 bytes exactly equals
the previous sealed owner hash9afafe519e0728c6c6861ba8b3ba01b3d4ad08078eed60fa50ccc6c50270c821;
reuse of its conservative3864/4088 stack/GOT audit is justified by byte equality.
Parent/helper assembly retains0x24004 endpoint/zero-reserved traps and rescans;
no0x186a0 budget or0x1fffe yield remains. This is scoped linked inspection, not
whole-program C stack or whole-system security assurance. Exact tools/macOS host
SDK/native archive identity are recorded in environment.json.

Preparation failures are retained: two host checks lacked an explicit macOS SDK
root (first error hid stderr; second reports missing assert.h), corrected with
xcrun selection. Original Python and reconstructed exact C inputs/logs remain.
An evidence-driver generation attempt failed before producing run.py; its missing
script log and preparation note remain. No failed attempt is counted as native
success. All five actual new native schedules pass. `artifacts.tar.gz` preserves3514
members from six newly owned output roots, each read back/hash-verified before
removing those roots; cleanup.json records exact ownership/paths. Source exports,
commands, prompts/schedules, maps, assembly and failed preparations remain sealed.

## Handoff and remaining work

Canonical userland runtime remains ABI23 and unchanged. Supply this private delta,
matched worker receipts and009 wait contract for its owner to adopt/qualify against
actual signal/ambiguity policy; independent technical/reader acceptance is open.
Then compose actual sys-init-owned entry/policy in the agreed boot-owner domain.
Do not equate this bounded fixture with the assembled boot/release image. General
TTY editing/job control, dynamic lifetime expansion, persistent OpenZFS/files,
package installation and R1 are not completed here. No sibling modifications or
consumer/maintainer sign-off are inferred.

Reproduction and host command are documented in NATIVE-CONNECTIONS; copied drivers
must run in a fresh packet directory to preserve existing receipts.
