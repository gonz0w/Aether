# Direct cat admission and copied startup

Before code, 2026-09-07. Extend the AECAT001 direct-owner experiment, not the runner
request protocol. The trusted owner selects the first supplied image capability;
validate exact Args argc1/envc1, cat and LC_ALL=C with all remaining bytes zero
before reserving channels. Names do not provide an image capability. Actual native
admission uses the existing factory, selected image and slot0, with backend slot1;
two generations still require four reclaims. No runner parent/collection is claimed.

Probe absent name and malformed argc/environment/padding against the same gate
before any channel reservation. In each actual launch also submit invalid native
argc5 with the reserved transfer endpoints, require EINVAL and retained endpoint
ownership, then valid admission. Overwrite the Args storage before delivering the
role bootstrap; client waits for that bootstrap before independently observing
complete cat argv/env/TLS. Native ownership transfer must reject owner closes of
the transferred endpoints. Restore reserved endpoints on admission failure.

Positive binary/empty/short copies and malformed-role no-I/O rejection compose
with admission. A gate allowing unknown names fails1510; corrupted argv after the
owner check fails client109/owner1501 before reads/writes. No new ABI, grant, limit,
dependency or unsafe block. Mutable Args stays in exclusive stack storage for each
synchronous trap; black_box keeps its later overwrite observable to the compiler.
Exact artifact hashes, tool/SDK/cfg and raw cases retained. No Toybox/umask/stdio/
finalization implementation or consumer acceptance. Preserve prior pins/bundle.
Run full command, connections/inherited, host/Zig/pin/workflow/format checks on
frozen sources; retain every attempt. Update NATIVE-CAT and STATE with limits.
