# UL-007/081/082 transport-backed descriptions change review

Plan before code,2026-10-21. Both companions still require authenticated FD/path/
immutable exec translation; no new matching dispatcher/native input is present.
Connect the already tested AF07 client to shared descriptions, without a local
Owner/SPA in the transport-backed path. Extract the existing fixed-array offset/
dup/final-close/seek/cloexec logic into one module used by two actual adapters.
Existing owner-local API remains an experiment; retained sealed bytes stay fixed.
Local error variant Policy becomes Source to cover both actual error families;
tests explicitly update this internal source-only API, not any wire or SDK.

Foundations O/I/E, Distribution PX, CR/TD/SE apply as previously adopted. One
read-only root,13 FDs3–15,4096-byte read limit, single-component names, signed64
range and no allocation/unsafe/dependencies. Owner adapter retains its dedicated
context only for existing checks. Remote adapter owns an authenticated AF07 client,
retains raw remote errors and both local endpoint-close outcomes, and never
constructs/takes over a live Owner. Client gets explicit local abort, no wire send;
Drop/abort/disconnect remain distinct, with no replay or reclaim/export claim.

Store adapter contract: synchronous borrowed buffers; successful open produces a
regular-file handle, directory results must close before rejection; read clears
all output on error and validates count; size is current raw size; final close
is acknowledged or fatal. Core validates returned count defensively, clears
errors before offset publication and updates shared offset only after success.
Known errors preserve state; retired source/final-close error retires whole table.
Exec-close is still destructive only AFTER confirmed image admission, not staging
or failed-exec rollback. No fork sharing, directory resolver or executable trust.

Pin original descriptor5-member/client5-member/AF07 service77-member candidates
before reuse; retain full source diff and unchanged service bytes. Rust1.98/2021,
strict warnings/unsafe/default Clippy/rustfmt, native panic abort generic libs.
Meaningful host tests: unchanged12 local tests, client regression including abort,
actual sealed AF07 service remote FD shared/independent offsets, duplicate/final
close, seek/EOF, capacity/no-transfer, directory-handle cleanup, cloexec aliases,
known errors, partial reply zeroing/retirement/no replay and failed-close outcomes.
Compiling omissions must fail actual assertions. Actual Python3.10/3.14 drivers,
compile60s/test30s,16MiB streams, clean env/build-only roots; no network or guests.
Keep all failed attempts, pin tools/helper, compact/read back before removing new
outputs. Run quality/inventory, syntax/whitespace and affected experiments.

Simplicity: duplicating a second FD algorithm is initially simpler but would split
critical offset/lifetime fixes between two current adapters. A small synchronous
Store with concrete handle/error/cleanup types separates precisely those existing
seams; no RPC/async/VFS framework. Remove duplicated algorithm by replacing current
owner-local source with the adapter plus common core. Keep immutable original
candidate/evidence for compatibility; no native default or upstream changed.
Implementation-agent review only; affected-owner/reader/native acceptance pending.
Next exact process FD/path/binding/immutable exec translation and sys-init/native
composition remain open. Host passes cannot close UL-007/081/082/M3/R1.

Final implementation-agent technical assessment: shared core retains original
bounds, aliases/offsets/final-close/seek/cloexec semantics; local adapter retains
exact policy errors, explicit retirement state and sole-context lifetime. Remote
constructor accepts only fresh authenticated channels, not an existing client
with hidden handles. It attenuates READ2, closes directory results, preserves raw
source failures and observes existing client retirement. Any final close failure
retires whole table. Core publishes offset only after successful bounded count;
error outputs clear before return. No raw native handle, source context escape,
Owner/SPA duplication, early exec-close or authority from names/FDs/digests.

Both actual Python versions pass client12/8, local12/8 and remote8/11 tests/
controls; default Clippy/rustfmt, warnings/unsafe denial and identical native
generic-library builds pass. Quality/three standards/Experience snapshot and
inventory checks, minimum/current Python syntax and whitespace pass. Scoped
internal-recipe presentation exception is recorded in docs/EXPERIENCE.md; no
public CLI or renderer conformance. No Rust sanitizer/native enforcement claim.

All ten exact attempt roots and every regular member were archived, read back
and hash/size checked before removal:134742011 logical bytes removed and46476665
archive bytes retained. Physical disk reclamation was not measured. Exact old
remote driver versions were recovered from their unchanged local-driver block
and verified against the recorded checker SHA256 before retention. All failures,
source versions/mutation records/logs/tools/commands/cleanup receipts remain.
Source-only delivery10-member seal:
21639ae14bde1f1e82cdc9c8c6af683a256a238403c517bd8e5c66acf6919a95.
Original candidate manifests still verify. No sibling writes/messages, native
guest/default/pin/authority/lifetime/quota changes. Independent owner/reader review
and all full process/path/immutable exec/dispatcher/native acceptance remain
incomplete; no global UL/M3/R1 closure is claimed.
