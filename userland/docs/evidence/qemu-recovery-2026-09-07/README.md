# UL-069 explicit Linux terminal recovery

[Consumer review approval](../qemu-consumer-regression-2026-09-07/maintainer-review.json)
is recorded. This subsequent recovery slice passes four independent cases using
the same pinned consumer inputs and unchanged owned process/container helpers.
[Summary](summary.json), [raw report](guest.stdout), [verification](verification.json).

| Case | Operation result | Natural restoration | Explicit restoration | Final restoration |
| --- | --- | --- | --- | --- |
| Unchanged GNU main stty script | Exit0 | False | True | True |
| Local mutation then failure | Exit23 | False | True | True |
| Local mutation then timeout | SIGKILL, timeout recorded | False | True | True |
| Omitted-recovery negative control | Exit23 | False | False, correctly detected | True |

Both termios and window size are compared exactly. All four endpoint pairs close
only after final restoration and readback. Timeout remains a failed command with
complete=false; process cleanup is complete. The other commands have complete
process records, including the deliberately nonzero exit. All process groups are
observed gone and the owned container is confirmed absent. This is one successful
four-case attempt; the raw summary identifies its private build root.

The GNU script is unchanged and still fails natural restoration. Passing explicit
recovery does not change the earlier combined extended INCOMPLETE result. Prior
consumer failures and provider differences remain in their original evidence.
The omitted-recovery case is an expected rejection, followed by unconditional
rescue; it is not counted as successful explicit restoration.

[Plan and review scope](RECOVERY-PLAN.md) covers ownership, limits, oracles and
remaining gaps. New helpers are BSD-2-Clause Python standard-library source;
upstream and runtime licenses are unchanged. Inputs mount read-only, with no
network/capabilities, uid65534, 512 MiB and 32 PIDs. The container has120 seconds;
the normal child has45 seconds and the timeout control2 seconds. These are bounds,
not performance or resource-stress measurements. Exact source/input hashes were
rechecked after execution. [Quality gate](quality.log) and [syntax](syntax.log) pass.

The maintainer approved this recovery slice; [review receipt](maintainer-review.json)
binds the exact statement and sources. UL-069 is done for the bounded reference
emulator correction, regression and explicit-recovery scope.
No native Aether TTY acceptance, owner-SIGKILL recovery, detached-child handling
or restoration-syscall-failure coverage follows. UL-066 keeps natural main-script
cleanup, locale/static fault injection and provider differences; UL-008 owns
native terminals. Separate reader walkthrough evidence has not been supplied.
