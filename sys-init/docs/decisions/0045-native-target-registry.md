# 0045 — Trusted native target registry and terminal projection

Accepted for BG-058 on 2026-09-06, using decision 0042's frozen ABI-6 sources.
Add one TargetRegistry per ResultApplier lifetime. This is a trusted model for an
initially empty two-slot native domain; attaching to existing workers, native
invocation, recovery and external authentication remain unsupported.

reserve accepts an exact issued launch token and free slot 0/1. Retain at most
two records, binding service/model generation and token to the expected native
handle. A slot's native generation advances only on confirmed successful launch,
through 1..3; model generation is independent. Deny duplicate service/slot,
non-launch/unissued/stale tokens and exhausted slots before changing registry
state. Return the expected handle for the existing ResultApplier.bind operation.
Unknown launch retains its reservation and cannot free or reuse the slot.

accept_launch consumes only the applier's most recent recorded launch result,
matching the reserved exact token and target and the journal's terminal outcome.
The driver must consume this result before applying another result. Success marks
admitted and advances native generation. Confirmed pre-effect rejection frees only
the target reservation; it does not clear model ownership or other resources.
Duplicate adoption rejects; no cache or restart/replay protocol is added.

status projects an exact trusted abi6-status-v1 record containing profile,
producer, target, syscall=0x20001, result (RAX) and kind (R8). Require the original
owner, admitted target and current owned model generation. Running is result=0 /
kind=0 and returns None. Terminal is detail=result-1: normal kind 1/detail 0..255,
fault kind 2/detail 134 (#UD), and stopped kind 3/detail 143. This first
projection selects the retained #UD witness only: the producer computes fault
detail as 128 + vector, so other fault vectors remain unsupported here. Reject
other combinations, absent/stale targets and profile/owner mismatch. Return a
detached native-terminal-v1 tuple with service, model generation, epoch, native
target, named native kind and exact detail. Keep normal exit 134/143 distinct from
fault/stop. No POSIX signal status or historical-ready admission is inferred.

accept_reclaim uses the latest recorded successful reclaim for the same admitted
target and service generation, with model reclaim_sent still true. Retain a local
native-cleanup-v1 fact and mark reclaimed; do not issue Model.batch, clear ownership
or discard the target binding. retire requires separately observed model cleanup
complete, unowned, same generation. Only then is the registry slot reusable; native
generation high-water stays retained. The cleanup fact covers the native target,
not outstanding supervisor channels/waits, helpers, devices or cross-core work.

No observation method acknowledges journal effects or reconciles unknown. Registry
checks compare trusted fixture data; real producer/target correspondence requires
a fresh consuming adapter witness. Native kind projection remains separate from
legacy Model event policy, particularly supervisor-stop and failed-launch cleanup.
BG-058 retains those mapping decisions and native composition; BG-033 recovery,
force mapping and BG-057 control composition remain open.

Test reservation uniqueness/exhaustion, independent generations, rejected/unknown
launch, stale result binding, terminal kind/detail identity, reclaim versus cleanup
and retirement. Add a target-generation omission control. Full model/development
checks and retained source/log hashes are required. Standard-library Python only;
existing native sources, journal/schema APIs and shared pins stay unchanged.

Decision 0045 validation: 190 model tests / 18 distinct mutation controls,
48 host tests, 37 harness tests and all offline gates pass. Retained evidence:
`docs/evidence/target-registry-2026-09-06/`. No fresh native execution.
