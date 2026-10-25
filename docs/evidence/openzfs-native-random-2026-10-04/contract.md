# Checked libzpool random boundary (before implementation)

Requirement: port only actual OpenZFS2.4.4 libzpool random_init/get_bytes/
pseudo_bytes/fini to the qualified explicit native entropy grant. Preserve original
kernel.c and CDDL notice/diff; select the exact port block for a bounded component
build. Do not invoke or claim a complete engine, pool or public SDK adoption.

No ambient host random-device open/read/close, fixed seed or zero-progress loop.
Keep helper signatures; init binds auxv0xa002 once. Duplicate init, absent authority,
draw without init, denied/exhausted/closed grants and any unexpected/partial result
are fatal125. Kernel1–256-byte draws are synchronous; larger helper requests use
bounded chunks only within the4096-byte fixture budget. Prevalidate nonzero pointer/
length arithmetic before chunks. An error after prior completed chunks is fatal,
never a returned-success claim. Empty requests return0 only after valid init.
Fini closes the domain binding and clears local selector; repeated fini or reinit
of a closed lifetime fails. Restart requires a fresh explicit native admission.
No wall time, entropy quality/reseed policy or thread/service admission invented.

Tests: call both actual helpers on real entropy, chunk boundaries/empty/exact bytes,
old TLS/memory/64-yield oracles, absent grant/disabled path, missing/duplicate init,
quota exhaustion, after-fini/reinit and genuine stalled transport. A deliberately
ignored draw failure must fail the named fatal oracle. Preserve all source/tool/
firmware/command/time/log artifacts and failed attempts, freeze qualified bytes,
run full host/scoped checks and required affected target selection. SDK inputs come
from sealed provider packet, original C from sealed source packet. No sibling edits.

Authority/unsafe: same per-domain native capability/quota/close; no caller pointer
is retained or submitted to DMA. Native mappings are validated per chunk under BSP
IF clear; partial progress before an invalid later chunk cannot masquerade as full
success. Single component init/fini sequencing is owner-controlled; concurrent
engine init/fini/service policy remains unqualified and workers must quiesce before
retirement. Production lifecycle/reseed/SDK adoption requires owner review.

Simplicity: a checked replacement for the existing random boundary is smaller than
emulating /dev/random paths and descriptors. Retain only required four helper entry
points and one bound selector, using the existing trap; no random daemon/framework,
DRBG, path shim or mutable standards pin. This removes ambient FD/open policy and
an upstream possible zero-byte read spin from this private selected block. Full
engine callers/lifecycle/resource closure remains next, not hidden behind a pass.
