# 0220: Fixed AF07 exec refusal and continued-parent qualification

2026-10-23 / BG-070 / R1. Pre-code review under the maintainer's instruction to
continue remaining process failures and persistent shell paths at current limits.
Root STATE owns integration; this is a bounded qualification extension, not a new
kernel/service ABI or a request for a higher budget.

Use the existing guarded ABI31 runtime and inputs. Add three explicit fixed
qualifier selections alongside the unchanged default immutable-helper case:

| Selection | Script effect | Required native result |
| --- | --- | --- |
| exec-missing | Run /inputs/missing; print status and continued-parent marker; exit | Original ENOENT translated by actual shell to127; copied child127/parent0/engine0; no replacement admission |
| exec-denied | Run /inputs/denied; print status and continued-parent marker; exit | Original EACCES translated by actual shell to126; copied child126/parent0/engine0; no replacement admission |
| parent-close | Run helper; report wait status; close stderr2; print through stdout1; exit | Helper7/parent0/engine0, successful child replacement, parent descriptor mutation/completion after wait |

Paths remain policy selectors, never grants. The real owner freezes the current
source, captures its image receipt and returns the original refusal only after
confirming no replacement and thawing the exact token. Invalid/unknown progress
still closes the route; these scripts do not inject an unknown native completion
or establish all failure schedules. Do not treat an unrelated errno, timeout,
panic or absent child as a correct refusal. No runtime source changes are planned.
Copy does not emit a loader-admission row; refused exec therefore requires only
the original engine/parent admissions, with the actual copied child's terminal
and complete cleanup still required. Successful exec retains the exact third
admission. Require every source-bound role, balanced waits, all21 cleanup rows,
ordered terminals/continued-parent output, bounded halt, exact fixed script and
whole-file recovery. All three roles are generation1; no invented reused identity.

Bind a known case and exact script in the prepared receipt and use that same case
for serial input/oracle, rejecting unknown or mismatched selections before a VM.
No arbitrary script/path/argv input, host-side prompt repair, relaxed admission/
cleanup parser or alternate success marker. Default SCRIPT/oracle callers remain
compatible; old missing case means the exact default only. Each explicit new case
uses fresh guarded disposable media and pristine reader -> writer -> fresh recovery
only after strict writer success. Batch exactly these three sequences, maximum
nine guests, serially; stop the entire batch at its first unexpected result, with
no retry, replacement trial or continuation after unknown stop. Record prepared
identities and the maintainer's direct bounded-work instruction before execution.
This does not reuse consumed diagnostic approvals or imply independent acceptance.

Same writer60s/6000 ticks, readers30s/3000,64KiB retained capture,35MiB total backing,
seven domains/twelve channels,49152 code/8192 stack/data,9-mutation/96-request
separate storage qualification. Scripts issue zero filesystem mutation requests;
import/export may write metadata. Same source/authority/WX/guarded memory and
confirmed-stop media/canary/disposal checks. No new grants, workers, dependencies,
unsafe boundary, kernel logging or filesystem engine capability.

Simpler alternative: count existing host refusal tests or the successful default
script as native qualification. Insufficient: neither runs an actual denied exec
and resumed parent's descriptor changes through this composed native owner. Reuse
the existing qualifier, receipt freeze, guest lifecycle and strict oracle with
small fixed case data; avoid another runner or runtime diagnostic injection. No
consumed path is retired. No new production state or abstraction is necessary.

Tests before native: actual harness fixed-case script/receipt mismatch denials,
independent expected success/refusal/parent trace fixtures, missing/duplicate/
misordered terminal/cleanup/status rows, unexpected replacement, wrong errno status,
missing continued-parent output, cross-case confusion and malformed case types.
Exercise actual bounded host serial input for every fixed script and case-specific
sequence stop/unknown-stop behavior. Reuse the prior final931-method/all-Zig kernel
checkpoint only after verifying unchanged runtime/tools/input hashes; run affected
harness/process/experience checks and scoped quality inventory. No broad runtime
suite repeat for this host-only change. Freeze sources during prepared/native runs;
keep compact commands/hashes/results/short failures and dispose owned outputs.

Persistent paths remain the next implementation contract: the current selected
FILE startup has no usable CWD/path-to-file namespace or persistent ELF authority.
Do not return a fabricated '/' or grant access based on the /inputs policy names.
After these process cases, trace the actual filesystem service directory/descriptor
contract and define the minimum CWD/path binding before implementation. Writable
FDs, actual persistent ELF loading, package state and interactive Zsh/TTY/ISO remain
R1 work. No interim RAM-only shell image or external repository wait substitutes.

Pre-native source inspection: the selected fd-libc-bindings.c explicitly returns
EOPNOTSUPP for dup2, and the pinned redir.o imports dup2. Do not run a descriptor-
duplication script expecting success. The continued-parent selection instead uses
only the supported close path after the helper exits, then proves stdout remains
usable. Full shell redirection still needs truthful public dup2 implementation;
no stub, fallback or known-failing native trial is substituted. The initial13-method
host harness pass qualified only fixtures, not availability of that shell operation.

## First batch outcome and narrow correction plan

Thirteen focused host methods/current static/process checks pass. Fresh3-case
preparation freezes574 paths; all3 kernel ELFs match each other, without a claim
they are byte-identical to the prior clock-fix ELF. No runtime sources changed.
The fixed batch stops on exec-missing writer after pristine reader success. Both
VMs stopped. Observed127/0/0, two original admissions,21 cleanup rows/230 park and
wake rows/halt1941. New18-byte AF07-PARENT:alive plus newline is split16+2 by the
actual fd-native.c stream bound, with trace rows between. Existing status127 fits
exactly16. Host output oracle correctly rejects; no recovery/other cases/retry,
no panic or new clock assertion. Metadata changed/canaries intact, whole-file
recovery unconfirmed. Keep exact bounded failure capture and source in Git.

Correct only the newly introduced marker to AF07-PARENT:ok plus newline (15 bytes
total), keeping all case/identity/cleanup/wait/media checks and runtime limits.
Add explicit <=16 marker tests and raw failed-witness rejection. No production
line buffer, trace suppression, parser projection or permission/resource change.
Prepare fresh cases and obtain renewed disposition under OPENZFS-FEASIBILITY's
Required independent disposition rule before a new native guest. Old failed
attempt remains failed; canceled prepared cases cannot be resumed.

The15-byte marker correction now passes15 focused methods, including each actual
script's generated record lengths, case/receipt and all stop/cleanup regressions,
legacy default receipt compatibility and exact raw failed-witness rejection. The
failed source is preserved in commitf8c0b97f6. Only new private marker bytes change;
no kernel/runtime producer, capture, status/identity/cleanup/wait check or limit.
Root NATIVE-C's persistent-path gap review records the actual single-component/
read-only wire and missing CWD/provisioning/loader work; it is not a fabricated
getcwd result, new path API or writable authority. Fresh preparation follows;
no native execution under the consumed batch.

All three shortened-marker cases are freshly prepared; exact receipts/artifacts/
source/tool freeze are bound by marker-prepared.json SHA256
c744cb54ec96181242155335f9d82c1ce33e0c1e3ea0477f4e92114b7ab5e8d1.
All current ELFs match the earlier failed batch kernel exactly. No additional
guest has run. Proposed renewed disposition covers only those three fixed cases/
maxnine guests with the same stop/recovery/authority/time/resource limits. Root
STATE owns this gate; no consumed/canceled receipt is reused.

## Approved corrected batch result

The maintainer explicitly approved the prepared corrected batch, current limits
and stop on first unexpected result. All3 sequences/9 guests pass: child127/126/7,
parent0/engine0,21 cleanup rows each,229/227/257 paired waits and halt1857/1929/1938.
All VM stops confirmed. Full780248-byte original file/pristine/independent recovery
and unchanged recovery media/canaries pass for each. Writer import/export metadata
changes, zero FS mutation requests. No extra guest/retry; original failed marker
attempt remains failed. Compact marker-disposition.json/marker-results.json retain
commands/input/tool/output hashes and observations; successful generated artifacts
removed after stop/verification. All limits and released pins stay exact. No
independent persistence/owner/release or public path/Zsh/ISO acceptance inferred.
