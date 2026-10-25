# Smallest serial boot composition

Reviewed 2026-10-03 under BG-067. Select one interactive serial dash session as the
next bounded usable environment. This is local integration direction, not a new
native ABI or accepted shell product. The kernel and wait-aware userland inputs now have sealed evidence. An actual
sys-init-owned entry has bounded native witnesses; complete composition acceptance
remains open. A confirmed terminal/read-EOF race is now repaired; exact attribution
of the initial historical failure remains limited by its missing caller. The working ABI22
[developer baseline](AETHER-BASELINE.md) stays available unchanged.

The [captured review](evidence/serial-boot-review-2026-10-03/README.md) verifies
Aether's sealed contract review and compares its source inputs with current files.
It retains the userland runtime/serial acceptance references and exact current
local command-owner inputs. Build/test tools must continue using offline pins;
these research copies are not new executable dependencies.

## Available paths and compatibility

| Path | Existing coverage | Why it is not the selected assembled boot |
| --- | --- | --- |
| ABI17 script adapter | Native dash script startup, command execution and stop in the [script adapter](DASH-SCRIPT-ADAPTER.md) | Bounded script execution does not supply the current interactive SESSION process/descriptor closure or sustained manual prompt. |
| AENSI001 / ABI22 | Maintained command recipe, typed owners, wait/idle, fixed Backend/Runner/Command table, bounded pre-effect retry and clean halt | Three-image80-byte envelope, supervisor slot3,16KiB owner, private v2 epochs. It cannot accept SESSION payloads or implement shell copy/exec merely by linking them. |
| AENMX008 / ABI23 | Userland independently accepts SERIAL-SESSION-01–06; actual shell variables/PID, external programs, redirection/pipelines and cleanup | Three-image112-byte envelope, supervisor slot5,24KiB owner, SESSION identities and15 task/channel lifetimes. Healthy kernel ticks still stop at3000; fixture owner has100000-step loops, three parent generations and observation-count finish. |
| AENMX009 / ABI24 lifecycle | Sealed kernel lifecycle, one-parent SESSION owner and endpoint wait probes, reviewed in [the producer intake](evidence/abi24-producer-intake-2026-10-03/README.md) | Userland009 now survives35-second prompt idle; the owned sys-init candidate passes bounded boot/workload/cleanup/halt cases. A confirmed terminal/read-EOF race is repaired; historical caller attribution remains limited. |

The captured kernel checks factories and UART against the actual supervisor.
Numeric grants, UID1000, executable paths and component hashes do not transfer
that authority. The old sustained-init selector explicitly excludes the SESSION
copy/exec/memory/capacity closure. Do not combine old flags, invent a new selector,
patch an envelope magic or silently downgrade to another profile.

At the earlier design-review intake, the source-current comparison initially rejected changed native_launch.zig.
A subsequent capture records native_launch.zig/build.zig edits and unchanged
captured enforcement/owner source at that instant. The producer's old sys-init
disposition copy is also behind our local work. Retain the initial rejection and
new observations; neither changes the producer's sealed design record. Current
siblings can continue changing after capture.

## Matched runtime and owned candidate

[Decision0182](decisions/0182-abi24-producer-intake.md) verifies the sealed producer
records for009/ABI24 lifecycle, selected SESSION owner and endpoint readiness wait.
The actual owner executes prompt-driven shell commands and confirms cleanup/halt;
withheld-input testing exposes client polling exhaustion, not a healthy idle prompt.
Endpoint waiting now passes a separate seven-generation worker probe beyond3000
healthy ticks. Neither witness is actual sys-init or a wait-aware dash client.

The experimental009 operation0x24004 waits on the caller's existing endpoint,
without pointers or new grants. Zero return means rescan/retry the original transfer,
not bytes transferred or EOF. Userland's sealed009 adaptation preserves offsets,
uses wait on EAGAIN and poisons the transaction on nonzero wait, including EINTR;
there is no automatic signal restart. Its35-second real prompt witness closes the
old polling dependency. The externally selected kit binds the matching kernel,
clients, envelope and firmware;008 remains separate and unchanged.

[The owned sys-init candidate](decisions/0183-owned-serial-session-entry.md) now
composes that closure with a local entry and explicitly borrowed dispatch module.
It validates boot arguments, supervises one session through confirmed settlement
and console closure, then selects authorized halt. Immediate and delayed positives
pass the independent90-byte/identity/ten-reclaim oracle. Wrong ABI and a small
pre-admission omitted-console cleanup control reject. The composed normal estimate
is3816/4088 stack and15056 code bytes; earlier over-limit builds are retained.
One initial delayed run reached guest failure after the final helper.
[Decision0184](decisions/0184-terminal-transport-interleaving.md) now reproduces a
compatible terminal/read-EOF race and repairs it with fresh before/after target
witnesses. The exact historical caller was not captured; do not infer exact
attribution. This remains a candidate pending maintained recipe and remaining
composition qualification.

Reuse the bounded dispatcher deliberately: Session::pump handles protocol/children/
pipe retirement, run_lifecycle handles observe/drain/park and confirmed settlement,
and the entry validates selection and closes UART before halt. Sys-init must supply
its genuine entry/policy and inspect the resulting linked code/stack. The existing
producer owner estimates3864/4088 stack; that narrow margin cannot be inherited by
modified code. Do not rename the kernel fixture or widen worker authority.

## Ownership and minimal policy

Use one boot supervisor domain. Sys-init supplies the genuine boot/session loop
and policy; userland supplies the bounded client/libc/POSIX runtime and application
payloads; Aether supplies enforcement and qualifies the selected native profile.
The existing dispatcher responsibility must compose explicitly in that owner,
not become an ordinary child with supervisor grants. Co-location includes dispatch
in sys-init's trusted computing base and shares its failure domain; it does not
provide restartable-service isolation. A process server/delegation framework is
outside this slice.

Start one shell with the delivered image/bootstrap/component set. Route serial
input and output through the matching bounded SESSION dispatcher. Preserve the
parent across input and use owner observation/drain/park when idle. Test schedules,
startup delay probes and observation-count assertions belong in controls, not
normal initialization. Shell exit selects shutdown only after actual terminal
collection, descriptor/pipe retirement and reclamation. Shell exit itself grants
no kernel final-action authority.

Do not automatically restart shell work: its effects are not covered by the ABI22
bytecount pre-effect retry proof. Preserve finite SESSION lifetime/pipe quotas and
explicit exhaustion. Denied/missing components, uncertain transport or unknown
cleanup must stop admission and retain ownership; do not report a clean shutdown
or retry an unknown effect. No new login, general TTY, signals/jobs, filesystem,
package lifecycle or persistence is added by this direction.

## Required matching delivery before wiring

Aether now supplies sealed opt-in producer evidence; consuming intake must bind
the exact envelope, owner ABI and
build selection, owner grants/state/error/cleanup contract, unchanged old-profile
regressions and native witnesses. Required mechanisms are owner-scoped monotonic
snapshot, compare/register park and separately authorized quiescent halt. Keep
SESSION identity/resource bounds and distinguish healthy idle from the external
watchdog. A wake is a rescan hint, not an I/O result or terminal receipt. Do not
copy ABI22 numbers or outcomes without the producer's explicit contract.

Userland must bind its runtime/application components to that exact profile:
bootstrap, descriptor/process/memory/mask behavior, component/symbol providers,
source/SDK/CRT/libc/tool pins, terms and private offline build recipe. The currently
sealed008/ABI23 extraction remains evidence for008 only. Required memory adaptation
cannot be omitted because stock musl happens to link. SDK promotion/independent
reader review stays separate; it does not prevent a clearly labelled private
matching integration experiment.

Sys-init intake must reject missing/wrong/mixed envelope, ABI, selector or component
sets before a successful acceptance. Inspect the actual linked owner code/stack,
record unsafe/FFI and dispatch obligations, and freeze firmware/tools/dependencies
and source/artifacts. Never obtain missing bytes from a mutable sibling during a
build. A design review or kernel private fixture witness is not our consuming run.

## Consuming acceptance and stopping point

Once the delivery is frozen, qualify an actual sys-init-owned image that:

1. Boots directly to one serial prompt without the old idle test or three-parent schedule.
2. Preserves shell PID/state across delayed input beyond3000 ticks and executes the
   existing external-program, redirection and pipeline workload with exact streams/status.
3. Confirms child and parent terminal results, retires all references/pipes and
   reclaims before owner-authorized shutdown; no fixture finish counts select policy.
4. Explicitly rejects profile/component/grant mismatches and exhausted admission;
   retains interrupted/unknown ownership without automatic replay or false completion.
5. Records reproducible private inputs, resource inspection, failed attempts,
   native oracles and full local checks. Independent assembled release review remains required.

These criteria are a consuming experiment, not full SUSTAIN-01–06, POSIX conformance
or v1 publication. The old matching kernel/client dependencies are closed in the candidate intake.
The [maintained candidate recipe](AETHER-SESSION.md) now replaces private-only
composition scripts. Next qualify remaining mismatch/exhaustion/uncertain-cleanup
acceptance. Recheck producer handoffs for future changes; do not expand the
runtime to compensate for the missing delivery. Remaining ABI22 protocol schedules
are still named in [the disposition](SI07-DISPOSITION.md), not erased by this choice.

Further [local diagnosis](evidence/serial-session-diagnosis-2026-10-03/README.md)
adds six exact delayed witnesses, including three unchanged normal images. The
original end-path failure remains unexplained; private direct-failure caller
capture is next before promotion. Successful retries do not close this finding.

Private [failure capture](evidence/serial-session-failure-capture-2026-10-03/README.md)
now distinguishes check/direct failure sites and panic paths within existing bounds.
Eight delayed cases and three forced controls pass; the original finding remains
open. Use that capture for focused investigation, not acceptance from retries.

[Terminal/read race evidence](evidence/terminal-read-race-2026-10-04/README.md)
retains actual yielded EOF failures, four exact repaired workloads and two
fail-closed controls. EOF needs fresh same-peer terminal confirmation; it alone
does not authorize resource release. WriteEPIPE recovery remains unqualified.
