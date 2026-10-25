# Scoped consumer source review

Reviewed frozen source-pins.json versions of session_scratch.rs, session-owner.rs,
session-scratch-client.h and the scratch oracle against SESSION-SCRATCH.md.
This is this task's technical review, not independent human reader sign-off.

Scratch::complete requires idle holders, length2, exactAB, zero tail, unchanged
protected bytes, one denial, two bytes actually read/written and observed EOF.
The data oracle is owner-local; serial text alone cannot expose every storage field.
Native lose-b/skip-read controls exercise final-state failure; bad-read and bad-byte
require external byte comparison even when internal state and cleanup pass.

Opcode86 dispatch binds authenticated peer1, first copied child and exactly one
EACCES with all reply-body bytes zero. Denial records are checked again against
actual child2 and zero image commitment at terminal. Client-synthesized EACCES
cannot satisfy this ledger and triggers confirmed parent stop/cleanup. Wrong-denied
preserves no handle yet deliberately changes the returned error and must reject.

Scratch descriptions carry namespace/sequence/index and peer holder bits, bounded
to two descriptions and32 data bytes. Sequence exhaustion rejects before truncate.
Open validates bounded paths, modes, reserved bytes and namespace. I/O validates
operation, binding7/8, frame length/tail, full reference, holder and rights before
mutation. Aliases share the description offset; holder release occurs at final
alias closure or confirmed terminal. Reopen allocates a fresh identity, and the
stale-reference client tests old writer EBADF plus zero response body before read.
The client validates successful reply identity/rights/unused binding before publish;
malformed exchange poisons the transport. Existing signal-mask and synchronous
exchange assumptions remain. Arbitrary interrupted exchange is not qualified.

Namespace reset requires idle scratch state; no persistence across parents is
claimed. Final code/stack inspection reuse is conditional on local raw and ELF
hash equality for all26 rebuilt owners. The192-byte minimum stack margin is an
estimate from contributor inspection, not a formal proof or kernel measurement.
No public VFS, credentials, general concurrency or SDK approval follows.
