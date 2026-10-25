# Deterministic native suspend ordering

The existing fork/wait conformance fixture now forces both child-notification
orders. See the prospective [contract and simplicity review](../../NATIVE-SHELL-STARTUP.md#deterministic-suspend-ordering-review--2026-09-14).
The only kernel change is a read-only R9 parked bit on the existing supervisor-only,
generation-checked lifecycle query, enabled only with native-signal-suspend.
No target-post, new syscall, scheduling policy, pointer or mutable counter is added.

Before-entry: the owner receives the first WNOHANG request while the child is live,
withholds its not-ready reply, completes child I/O and confirms child terminal72.
It confirms the parent is not parked, then releases the reply. The parent therefore
enters real musl sigsuspend with an already-pending child notification.

After-park: the owner replies to WNOHANG, withholds remaining child I/O, and polls
the read-only parked observation while yielding. Only after confirming the parent
is parked and the child is live does it complete child I/O. Child terminal72 then
posts SIGCHLD. Both clients require no earlier handler, exactly one handler under
the temporary/self mask, EINTR, and restored original SIGCHLD/TRAP mask. They reset
the action/mask and run the existing wait error, retained-status and one-time
collection checks. Parent71/backend17, two generations and six reclaims qualify.

The skip control omits sigsuspend. The owner must exhaust its bounded observation
loop and reject2330 with zero reclaims and no terminal publication. This tests the
ordering oracle rather than accepting a delay or inferring parking from WNOHANG.
There is no timing/performance claim. The unchanged dash wait and disabled-route
cases are included in the focused selection as regression witnesses.

## Attempts

- Focus1 rejected owner1901 before ordering: the profile enabled signal actions
  without the required copy-signals support. Its owner loop also used the ready
  operation instead of yield; both setup mistakes were corrected together.
- Focus2 reached parent82/owner1950. The new client still selected the old local
  startup sigaction facade, which cannot install a handler.
- Focus3 added a raw setup diagnostic and confirmed parent234/owner1950 at
  sigaction. Selecting the existing STARTUP_PUBLIC_ACTION mode fixes the fixture;
  no public signal implementation was changed to bypass the rejection.
- Focus4 passes all five selected cases. Each failed source revision, command,
  log and target artifact is preserved separately. The earlier host pass belongs
  to attempt2; host-final is the qualified revision.

Host-final passes all 101 Python tests plus Zig and offline checks; all seven M4
scheduler regressions and scoped formats pass. All 306 connections cases pass in 968.37s. All 265 runtime sources remained
frozen during the final runs. See qualification.json and ordering-traces.json.

## Limits

This closes forced notification ordering only. Stale parent reuse, ignored/blocked
lifecycle posts, repeat-terminal notification, parked stop and invalid-handler
recovery still need native controls. Unsupported default effects during suspension
still return ENOTSUP; default termination and nested delivery remain gaps. Matching
command-runner qualification, independent consumer review, SDK adoption and release
assembly remain open. No sibling repository or released standards/SDK pin changed.

The source and target archives preserve reproduction inputs without adding unpacked
build trees to documentation. SHA256SUMS seals the final packet; verification
must check each listed member. Archived driver scripts document the executed
selection and local runner, not a new supported developer entry point.

Compatibility: all 582 compared pre-existing client/owner ELF and raw artifacts
are byte-identical. All 303 compared kernel images differ; no kernel byte-identity
claim is made. Full target regressions qualify their behavior. The exact inventory
is in compatibility.json. All six newly generated unpacked target directories
were removed only after every file matched its preserved archive; failed attempts
remain available in those archives. duplicate-cleanup.json records exact paths
and sizes. No other build directory was removed.
