# Next denied-launch implementation review

Read-only design review, not implemented or consumer-approved. Existing userland
RUNNER-OWNER-HANDOFF / RUNNER-LOCAL-OUTCOMES require actual ENOENT/EACCES/EBUSY
observations, no child admission, exact diagnostics and independent cleanup.
Current AEOUT001 has only runner outputs, so it cannot silently supply the existing
child stdin/output authority. Do not manufacture an errno from parent exit2.

A concrete next slice should use a separately identified combined carrier rather
than append invisible bindings to AEOUT001. Proposed shape: a new domain magic,
32-byte header plus four complete 32-byte records (160 total). Keep stdout/stderr
roles/capacities and existing parent fd3 input/fd4 child-output rights distinct.
Validate the entire carrier before publishing any descriptor. Exact magic/role
identities must be specified in the preimplementation contract; none is allocated
by this review. Preserve AEOUT001 and existing startup/child profiles unchanged.

The backend needs one additional 64-byte child-output record alongside immutable
input and the independent 512/256 runner sinks. This is user-space fixture storage,
not justification for new kernel capacity. Reuse the existing 384-byte launch frame
and owner `validate`/`admit` rules. ENOENT comes from name selection; EACCES from
an actual rights-widening request; EBUSY should use the existing held-channel-pair
partial-reservation path and verify actual admission failure before native launch.

For each denied invocation independently require one complete launch request,
exact selected errno, zero successful admissions and collection attempts, exact
stderr text/status2, empty other outputs and untouched input. After releasing
held/partially allocated transport pairs, probe the available pair quota and
restore it before continuing. Four backend records and all aliases must close;
parent/backend still account for four native reclaims across two generations.
Do not add a successful child just to test cleanup in this no-admission witness.

Required controls include fabricated exit2/no request, wrong returned errno,
wrong diagnostic or sink, leaked reservation and unexpected receipt/admission.
Userland then independently adopts a reviewed immutable producer bundle. Full
child launch composition, denied-diagnostic delivery failures and other RL cases
must remain explicit until they have matching target evidence.
