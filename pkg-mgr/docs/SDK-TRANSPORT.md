# Private SDK transport

Implemented 2026-09-07 for synthetic regular-file SDK fixtures. This is the explicit
transport from the [admission design](SDK-ADMISSION-PROPOSAL.md), using the
[profile validator](SDK-PROFILE.md). It transports caller-reviewed build inputs;
it grants no execution authority or native compatibility. The [real SDK handoff](SDK-REAL-HANDOFF.md) now records owner-side transport
under the exact consumer-accepted target. Compiler/native qualification remains
separate; original host provenance stays explicitly unrecorded.

```text
sh mk/binary.sh sdk-export ROOT aether-musl-sdk EXPECTED-PROFILE-SHA256
sh mk/binary.sh sdk-import ROOT BUNDLE DESCRIPTOR-SHA256 EXPECTED-PROFILE-SHA256
sh mk/binary.sh sdk-recover ROOT BUNDLE DESCRIPTOR-SHA256 EXPECTED-PROFILE-SHA256
```

ROOT must satisfy the existing initialized private-root/state contract. Export
requires a registered aether-musl-sdk record. The exact profile and build/native
receipts must be recorded at the paths defined in the admission design; all three
must be manifest-bound, with no package dependencies. The compiler and consumer
adapters remain external prerequisites. Import/recovery take an absolute bundle
path and independently selected descriptor and complete canonical target digests.
Never substitute the native receipt digest for the complete target digest.

SDK descriptors use local-sdk-directory-v1; target.kv uses cross-sdk-target-v1.
The six directory entries and descriptor field order are as specified in the
proposal. Package-state-v2, blob content checks and exact ordinary modes are
reused. Export/import/recovery validate both receipt hashes and the full profile
pin, and import/recovery require target.kv to equal the manifest-bound profile.
Every hash command must succeed before its output is accepted. A syntactically
valid or self-consistently rehashed substitution cannot replace the caller pin.

Only the explicit SDK branches select this format. Existing host-v2 commands,
identity rules and output bytes remain unchanged; they reject SDK bundles. SDK
branches reject host-v2 descriptors. The public CLI has no new dispatch command.
No preflight, replacement, installed-payload removal or automatic rebuild is added.
The input role is not hostile-content confinement; caller-reviewed recipes/content
remain trusted. Merely naming a payload SDK data does not qualify its execution.

Successful operations print one LF-terminated TSV row, respectively:

```text
sdk-exported<TAB>aether-musl-sdk<TAB>DESCRIPTOR-SHA256
sdk-imported<TAB>aether-musl-sdk<TAB>DESCRIPTOR-SHA256
sdk-recovered<TAB>aether-musl-sdk<TAB>DESCRIPTOR-SHA256
```

Literal TAB separators are used. Invalid SDK-specific argument count/name/pin
syntax returns 64 after the existing helper's minimum-three-argument guard;
that legacy guard still returns 1 with its unchanged usage diagnostic. Validation
and handled failures return nonzero; helper/provider diagnostics may also appear.
SDK stdout failure and PIPE are reported with status1. A failed success-row write
can follow a committed state; inspect and explicitly recover rather than assuming
nothing happened. No success row is emitted before publication.

The existing single-writer/caller-controlled path constraints and two-step
stage/record publication remain. Occupied stages reject import. Explicit recovery
revalidates pins, profiles, receipts, records and modes before adopting an exact
retained stage; it never repairs, deletes or replaces it. SIGKILL can leave private
scratch, which is not authority and is not consumed by recovery. A repeated
recovery of an exact committed record succeeds without rewriting it. No fsync,
power-loss durability, concurrent-writer or hostile-filesystem guarantee is added.

[Transport controls](../tests/sdk-transport.py) use synthetic SDK data and receipts:
round trip, exact records/modes, cross-format rejection, wrong/full profile pins,
self-consistent substitution, content/mode/type/dependency rejection, occupied
stages, retained-stage drift, hash-provider failure with plausible output, three
publication kills and closed stdout after commit. They retain an unrelated
sentinel and compare authority/payload before and after rejection. Killed scratch
is explicitly excluded from authority snapshots and remains in the private test
root until test cleanup. Profile grammar has separate 65-case coverage.

[Evidence](evidence/sdk-transport-2026-09-07/README.md) records all attempts and
selected checks. This implements the transport seam; SDK-01–08 real-package gates
are not closed by synthetic fixtures. The exact target and missing-provenance representation were subsequently accepted
by userland; the linked real handoff records actual data transport. Next is
independent artifact verification and imported-SDK build/native consumer work.
