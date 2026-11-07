# Zsh inherited home working directory and external command

Owning work: [issue164](https://github.com/gonz0w/Aether/issues/164).
[Approved design](https://github.com/gonz0w/Aether/issues/164#issuecomment-6714005665)
and [decision](https://github.com/gonz0w/Aether/issues/164#issuecomment-6714021252).
The guarded pair passed: unchanged160 writer42.480s/61 requests and new164
cold27.966s/68 requests,228/172 once-only foreground PTY bytes. Actual startup
preference, parent/child/parent physical home output, helper/status23, same parent
PID/PWD, prompts, normal exit/export/MODE0/three reclaims/halt and known host
cleanup passed. Combine this with the actual-function controls and fresh linked
route below; UART text alone cannot prove child GETCWD. Delivery and review are
recorded in the owning issue;141 and assembled R1 remain open.

The first cold attempt reached child/home and helper23, then a no-child host
terminal guard stopped it during cleanup. That consumed failed attempt retains
unknown guest export/completion and known host cleanup. The new-profile-only
guard correction passed a focused actual-function control before a fresh
reviewed writer/cold pair; no failed disk was replayed.

## Closed composition

Default-off Rust `native_zsh_home_cwd_exec` and matched C
`AEFD_ZSH_HOME_CWD_EXEC_BINDINGS` require the complete162 home-CWD/login-startup/
redirection-reader/cold-reopen/file-exec/idle/operator composition. Existing162
keeps refusing fork; all old profiles and numeric limits remain unchanged.
Keep the current login argv/environment, prompt and AEFP0007 wire bytes.
No new kernel operation or namespace grant is introduced.

Rust retains ROOT/HOME directory references. Before freeze/copy effects require
fully delivered profile READ phase7, no live aliases/pending FILE transaction,
and existing child/stream/context validation. Snapshot the parent selection for
only the admitted exact child binding. Publish after known successful admission
and before child publication; retain through checked exec generation transition
and clear with confirmed settlement. Parent CWD changes do not change the child.
Known pre-effect refusal grants nothing; unknown effects contain/retire without
replay or guessed rollback. Keep existing wait, endpoint and READ-lease cleanup.

The exact child may GETCWD through actual held-directory observation and existing
length/padding/buffer/error checks. Child CHDIR, profile OPEN/READ and nested fork
stay denied. MODE/SIGINT remain parent-only. The copied shell uses the parent C
build, so helper-entry compile guards do not establish its authority. Reconstruct
actual child-local FILE/stdio callbacks/bindings/generation/sequence using the
existing336-byte snapshot and AEFP0007. No extra handle or global CWD table.

## Focused qualification

Use one unchanged fresh160 writer with its approved228-byte workload,9 logical
mutations and normal export/known stop. Bind its exact provisioner artifacts and
one-use disk to one new cold reader with zero client mutations. The cold trial is
172 once-only CR-terminated bytes, maximum50 per stage:

```zsh
[[ ! -o beep ]]; print -r -- "PROFILE $? $$"
cd /home && pwd -P; print -r -- "HOME $? $$ $PWD"
(pwd -P; exec -c /home/probe)
print -r -- "STATUS $? $$ $PWD"; pwd -P
exit 0
```

Require startup preference, parent/child/parent physical home output, HOME0,
helper/status23, same parent PID/PWD, returned prompts, actual file-exec receipt,
normal terminal results/export/MODE0/three reclaims/halt/PASS and known host cleanup.
Zsh pwd can fall back to cached state. UART output alone cannot establish an
actual child GETCWD call: combine the trial with fresh selected linked-route
inspection and actual reconstructed-context/dispatch/observation controls.

Focused checks cover settled/busy admission, snapshot independence, exact/stale/
foreign bindings, child denials, exec preservation, refused/unknown effects and
confirmed settlement. Fresh affected fits must meet81920 RX,4096 Runtime/workspace,
12280 usable stack and all existing page/request/time/input bounds before images.
Unchanged dependencies may reuse evidence only after exact identity/impact review.
A required overflow stops for replan. This checkpoint's approved focused gate
leaves141 open and does not qualify general paths, job control, packages,
authentication, general peak resource proof or assembled R1.
