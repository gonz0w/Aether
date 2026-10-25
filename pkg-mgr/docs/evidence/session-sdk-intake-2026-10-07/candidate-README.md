# Private session runtime candidate

Aether-userland owns this bounded runtime by maintainer assignment2026-09-29.
Aether retains native ABI/capabilities/enforcement and the fixture owner.
This candidate targets private AENMX009/ABI24; it is not a published SDK, package,
general POSIX runtime, new bootstrap ABI or independent-review approval.

recipe.json builds runtime/application, native memory and patched musl fork/wait/
rebind objects plus the application helper. CRT/libc/dash dependencies are shipped
as explicitly pinned prebuilt inputs with their original terms. Full upstream
source rebuild recipes and qualification remain separate accepted evidence.
The SDK retains the existing strict memory-protection patch. No network or real
prefix install is used. The component gate must pass before parent/helper linking.
The application supplies arguments/environment/path policy; the kernel/owner
retain native authority. Missing adaptation cannot be admitted via libc fallback.

Select SHA256SUMS by its externally reviewed digest before calling
support/rebuild.py's rebuild(bundle, new_output, expected_seal) function. It verifies
all input bytes and pinned tool executables, uses the unchanged owned process
runner and checks complete exit/cleanup with60-second/16MiB command bounds.
Use a private build output directory. Rebuilding proves static artifact identity;
new native execution and independent review are separate promotion gates.

Build support requires Python3.10 or later; SHA256 is streamed in1MiB chunks.

This candidate explicitly selects SESSION_SERIAL and SESSION_CHANNEL_WAIT.
Endpoint wait readiness retries the remaining bytes; a nonzero wait, including
EINTR or unsupported opcode, poisons the synchronous protocol. No automatic
handler delivery/restart is claimed. Native evidence is scoped to the matched
wait kernel and lifecycle owner, delayed prompt and ten confirmed reclaims.
Default ABI23 clients and immutable prior candidates remain unchanged.
