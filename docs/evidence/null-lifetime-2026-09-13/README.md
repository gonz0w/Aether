# Native null lifetime checks

Before implementation: extend the existing private null foreground-subshell
experiment with native owner-protocol probes after the helper closes its null FD.
Aether owns this bounded enforcement fixture; userland owns independent facade
acceptance. Preserve all kernel/SDK/standards pins, old protocols and source evidence.

Requirement: prove closed and previous-instance references reject, a stale close
cannot close a new object, foreign-generation handles reject, active opens reject,
and exactly16 lifetime instances exhaust without wrap or a leaked active object.
The real helper's instance1 is followed by raw owner requests for instances2–16;
these are fixture probes, not a new libc reopen interface. Keep the parent's input
unchanged, actual helper7/parent0/backend17 twice and six confirmed reclaims.

Forbidden: accepting stale/foreign handles, letting a stale close affect a live
instance, allocating beyond quota, silently publishing a descriptor from a failed
request, or treating host tests as native evidence. Select deliberate false stale-
read and false exhausted-open replies, each requiring a distinct helper rejection
and owner2130 with zero successful reclaims. Preserve all failures and freeze
sources before focused and full connections runs. Run host/pins and C/Rust formats.

Simplicity: reuse the existing owner, wire frame and null profile rather than add a
service or general descriptor abstraction. Host-only tests are insufficient for
transport/lifetime composition. A small private probe helper adds no runtime API;
no existing path is retired. No new dependency, unsafe boundary, kernel operation
or resource quota. Messages use fixed32-byte buffers under the existing signal
mask guard, with exact replies and bounded loops. Document the scoped results in
NATIVE-CONNECTIONS, STATE and existing companion/roadmap guidance. Denied-exec
rollback, abnormal-stop cleanup and background SIGCHLD/suspend remain separate
pending work; do not claim they pass from these probes.


## Result

PASS: all 296 connections cases in 953.31s; six focused null cases,
101 host tests, scoped C/Rust formats and offline standards checks. Sources remained
frozen:264 inventory files and 249 harness inputs. The positive runs
instance1 through the actual null FD/exec/helper, then raw instances2–16 in each of
two generations. It retains helper7/parent0/backend17, exact output, intact original
stdin and six reclaims. Stale-read and exhausted-open false successes fail at the
exact child225/226 and owner2130 markers with zero reclaims. Existing handle, EOF
and retained-table controls also pass their exact rejection checks.

Of 564 previous ELF/raw images, 563 are byte-identical; see
compatibility.json for the 1 changed images. Maximum inherited owner
size is 15408 bytes within the existing16384-byte limit. No kernel,
SDK, null owner implementation, protocol, quota or released pin changed. Only the
probe helper, its guarded caller, dispatcher controls and harness selection changed.
These probes exercise the live transport but do not publish reopened libc FDs.
Denied-exec rollback and abnormal-stop cleanup are still unqualified. Background
wait was not rerun and remains blocked on actual SIGCHLD and atomic mask/suspend.
Independent consumer acceptance and R1 readiness are not claimed.

## Reproduction and evidence

connections-final.json/log record the full standard connections command, pinned SDK
and tool lock. The SDK/lock digests match the previous sealed null-native-wait
packet. preflight-driver.py selects six profiles with unchanged oracles; host.json
and formats.json record the host and formatter commands. sources.json/tar.gz and
implementation.diff bind this revision to the prior sealed packet. Every target
artifact, report, command and raw serial log from both runs is archived and each
archive member hash was read back and checked. There were no failed attempts in
this packet; the previous wait timeout and its failed revisions remain untouched.
This is local producer evidence, not an independent clean build or SDK release.
