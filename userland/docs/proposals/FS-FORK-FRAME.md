# AEFORK01 client frame candidate — UL-007/081/082

Current follow-on: [armed fork stage/child constructor](FS-FORK-STAGE.md) now
supplies real native park/rebind/startup reconstruction and a complete pinned
shell link. Earlier missing-stage evidence remains immutable; no matching owner
transaction/native execution or whole-fit acceptance is inferred.

Aether's2026-10-22 contract selects serialized service-owner admission around the
unchanged native copy primitive. Its proposed private frames now have a bounded
userland codec in fd-fork-frame.h/c. [Pinned owner excerpt](../evidence/filesystem-fork-frame-2026-10-22/aether-contract.txt)
records the exact reviewed input. This opt-in candidate allocates no opcode and
selects no sys-init dispatcher or runtime. Matching producer/consumer agreement,
armed stage/child constructor and native qualification remain required.

## Request and sequence

AEFORK01 is exactly304 bytes: version1/length304 at8/12, pinned32-byte AEFSH001
parent identity at16, full128-byte tagged AEFDT001 map at48, seven16-byte source
records at176, two retained pipe history counters at288/292 and nonzero u64
sequence at296. Integers are little-endian. Only current shell1/generation1–3
origins validate; native memory/PID/PPID observations must agree. The codec reuses
pinned identity/map/native-source validators and checks exact source/map coverage.
FILE/PIPE/CONSOLE and close-on-exec flags remain distinct. File generations and
console references are opaque labels, never native authority.

`aefd_fork_encode` converts an immutable AEFDB001-shaped shell snapshot to this
frame, preserving bytes8–295 and every inherited flag. This function does not
capture live descriptors: the future stage must collect current identity, map,
sources and histories under the whole context guard and enforcing owner gate.
An old startup snapshot alone is not that capture. Exact in-place conversion is
supported; other overlapping ranges are forbidden. Invalid content clears the
exact304-byte output; wrong output size leaves output untouched.

`aefd_fork_decode` validates the complete inert request and publishes a borrowed
view only after success. Rejection leaves output unchanged. Header checking can
reject incompatible profiles after exactly16 bytes; incomplete prefixes return
incomplete, not successful acceptance. Neither helper consumes a channel or
resolves an already parked caller's native obligations.

`aefd_fork_next` reserves one nonzero sequence from a caller-owned counter per
authenticated channel generation. UINT64_MAX can be the final sequence; a further
reservation rejects without wrapping or altering outputs. Do not reset the counter
within a generation or reuse a reserved sequence after failed/unknown transmission.
Decode validates sequence syntax; enforcing monotonicity/replay exclusion remains
with the actual channel owner/stage. Correlation alone does not authenticate a peer.

## Parent disposition and context-ready

Parent reply is exactly32 bytes: AEFKR001, matching sequence, signed i64 result,
zero u64 tail. Positive must be canonical child2–4/epoch1–15 and exactly match the
actual native copy return. Negative must be-4095..-1 and actual native return-11,
matching the token-thaw contract. The authenticated owner must send that refusal
only after confirmed no-child or actual post-copy settlement and reservation
cleanup. The pure decoder cannot establish those facts from bytes. Zero, outside-
range errno, stale sequence, mismatched native return, partial/extra frames or
nonzero tail reject without changing output. Raw thaw-11 alone cannot manufacture
an owner-side ENOMEM error; unknown outcome forbids replay/compensating thaw.

Context-ready uses AEFKC001, the same sequence, exact positive canonical child PID
and zero tail. Encode/decode are pure; they do not claim the context exists, send
readiness or publish application/service readiness. Only a validated future child
constructor may send this receipt before returning through pinned __post_Fork.

## Proposed child-frame correspondence

`aefd_fork_child_match` revalidates the request and fresh304-byte AEFDB001 startup
against supplied actual parent/child native observations. It requires child2–4/
epoch1–15, exact parent PID/shell generation, factory0, a fresh nonzero file-channel
generation, distinct child memory grant and fresh distinct channels disjoint from
both parent endpoints. Child FD entries/flags and both pipe histories are retained
exactly. This local candidate also requires exact retained source reference labels/
selectors/rights/bounds across inheritance; sys-init must agree that relationship
before selecting it. It creates no source or transferable borrow from those labels.

This is a pure correspondence predicate, not the armed child constructor. It does
not repair auxv/TLS/thread lists, quarantine/reset an admitted context, reconstruct
internal pointers, close an endpoint, perform a native copy or prove actual grant
ownership. Supplied observations require authenticated native collection. The
request and greeting stay inert and immutable while inspected; rejection leaves
the output identity unchanged. No new live startup/context/FD ledger or heap.

## Tests and remaining integration

The private experiment recipe is run from repository root with pinned provisioned
inputs:

```sh
python3 -B experiments/filesystem-service/check-fork-frame.py
build/python-qualification/Python-3.10.21/python.exe -B experiments/filesystem-service/check-fork-frame.py
python3 -B docs/quality/check.py
```

Tests cover every request/receipt prefix and extra size; malformed headers,
reserved/identity/map/source/history bytes; exact used-source correspondence;
opaque label acceptance; cloexec/in-place/output boundaries; sequence exhaustion;
all4095 private errno values plus invalid boundary; all child PID syntax values;
stale/native-return mismatch; context-ready tail/identity; fresh child startup,
every child slot/epoch/shell generation, changed flags/file selectors and extra
FDs, reused generation and old-channel collisions. Semantic omissions must compile
and fail assertion-based oracles. Host C17/UBSan and formatting are separate from
freestanding target object/relocatable link/static frame/import inspection. No
host model or individual frame count proves full native resource fit.

[Evidence](../evidence/filesystem-fork-frame-2026-10-22/README.md) retains all attempts,
including an initially surviving child-correspondence omission: malformed-byte
coverage did not test structurally valid changed flags/selectors. Added those
cases; production checks were retained. Prior libc/source/serialized inheritance
candidates stay immutable. This source candidate has no __aether_fork_stage,
selected executable or native fork success. Remaining userland work is armed
capture/one-shot child transition with pinned copy_rebind/__post_Fork ordering;
sys-init BG-069 must select matching framing/source relationship and enforce
file/stream exclusion, then BG-070 composes actual copy/refusal/unknown settlement,
readiness/shutdown. Full link/whole fit/fresh native witnesses remain open, along
with immutable exec/public dup2/full UL/M3/R1 and independent owner/reader acceptance.
