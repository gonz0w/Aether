# ABI17 startup rollback consumer — 2026-09-11

Ten fresh native script cases and four compatibility/admission cases pass. The
previous9,152-byte startup candidate now boots under the independently consumed
AENMX002/ABI17 profile. The largest selected image is9,264 bytes. All use the
producer's enforcing16,384-byte linker and its unchanged4,096-byte RW/NX stack.
Kernel admission verifies RX user code, RO/NX aliases, separate stack and zero tail
before execution. These are mapping checks and successful bounded workloads, not
a measured worst-case stack bound for arbitrary input.

| Case | Exact outcome |
| --- | --- |
| Ordinary script | hello-newline; shell0, stream17, file17; two generations/six reclaims |
| Missing root / missing close | shell2 then1501/0; shell0 then1599/0 |
| Live-file stop / omitted close | owner-observed143/kind3, providers17, six reclaims;1599/0 |
| File / stream / shell startup EINVAL |1605 with0/1/2 reclaims; already-started providers17 in dependency order |
| Omitted failed endpoints / stream files |1604/0 with no terminals; stream123 then1604/0 |
| Old ABI9 script and stop images | Unchanged payloads pass exact previous outcomes on the new kernel |
| Oversized image downgraded to ABI9 / ABI17 length16,385 | invalid launch envelope, no worker admission or lifecycle result |

Startup is sequential. After a confirmed Known launch error, the ordinary path
cleans retained endpoints, retires pre-opened stream handles if needed, waits for
provider terminal17 and reclaims before reporting failed startup1605. It does not
retry boot or turn that failure into success. Unknown outcomes reject before any
rollback; this branch is source-reviewed, not newly native-fault-qualified here.
Native error qualification in this packet is actual launch EINVAL, not every
allocation/observation/ambiguous failure. Existing owner component coverage remains.

## Inputs, compatibility and scope

`intake.json` records verification of all75 sealed producer files,242 execution
source files and4,606 artifact members. Producer manifests and the frozen run-source
archive are retained; the897 MiB artifact archive was verified without duplicating
it. Selected producer source is from pre-fork-dispatch, not mutable current Aether.
The worker ELF inputs and script protocol sources remain the September9 script
intake. Kernel/build/scripts come from the new frozen packet. The hybrid composition
is explicit: this is not a rebuild of upstream Dash/libc or acceptance of new fork,
exec, serial-console or process-owner behavior. The retained drivers record commands,
tool hashes, environment and the exact staging choices. ISOs remain under the local
output directory with hashes; supervisor/envelope bytes and raw logs are retained.

The new opt-in `script-abi17.patch` replaces the old script patch when selecting
ordinary startup rollback and requires bootstrap17 with the same grant tuple.
`script-owner.patch` remains available for the existing ABI9 path. Maintained
script_lifecycle.rs adds the already-reviewed start_next helper; other owner and
native adapter sources are unchanged. No new unsafe boundary or runtime dependency.
No failed command or native case in this consuming attempt. Prior rejected size
experiments remain sealed. No sibling or released standards pin was changed.

## Review and remaining work

SE-01–05: the requirement is confirmed startup rollback in the existing script
composition. Keeping fail-fast launch was simpler but left providers owned without
cleanup. Existing paired ownership and direct sequential cleanup meet this need;
no framework, new service, journal or protocol is added. Function-layout alternatives
saved no space, so the producer's explicit bounded profile resolves that constraint.
O-01/04, I-01/03–06 and E-01–08 apply; no shared-standard exception is introduced.

The capacity handoff is consumed for this bounded scope. BG-067 retains missing
startup-error coverage and the separate sustained wait/reuse/authorized-shutdown
handoff. This is a script lifecycle prototype, not the complete v1 product, release
review, operator shutdown, indefinite shell or production memory budget.

## Local validation

All ten development gates pass in `run-uslbhtip` with unchanged checked sources.
Maintained lifecycle modules match the executed source snapshot; all three released
standards pins remain unchanged. `git diff --check` passes. Native qualification
is the fourteen cases above; full checks do not substitute for those witnesses.
