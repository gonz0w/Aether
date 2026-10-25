# Private cross-SDK admission proposal

2026-09-07. Draft local format design following the
[SDK owner review](SDK-OWNER-REVIEW.md), for pkg-mgr and userland review before
implementation. The names and command paths below are proposed, unavailable today.
No release pin, existing wire format, runtime or shared standard changes here.
This is Aether SDK preparation; it opens no Apple product or qualification work.

## Scope and identity

Transport one aether-musl-sdk package as inert inputs to a separately provisioned
build toolchain. Retain pkg-state-v2 regular-file records, dependency fingerprints,
ordinary file modes and private-root publication/recovery semantics. Do not add a
compiler, solver, service, remote transport, live-prefix writes or payload deletion.

Keep three claims separate: which host/tools built the SDK; which bounded native
profile its inputs were prepared for; and whether a later consumer actually builds
and runs. Import verifies caller-selected identities and bytes. It does not execute
the compiler or qualify the importing machine as a compiler host or native runtime.

Require two explicit caller pins: the bundle descriptor digest and expected SDK
profile digest. The latter is selected from reviewed owner materials before using
the bundle. Computing both from an untrusted bundle is not independent selection.
A profile digest is an exact allowlist choice, not a signature or capability grant.
No aliases, ABI inference from a compiler triple or default to the newest profile.

## Proposed directory and canonical records

Use a distinct descriptor format local-sdk-directory-v1 with exactly the six
existing transport entry names: artifact.kv, package.tsv, target.kv, modes.tsv,
dependencies.tsv and files/. Their file/blob rules remain those of
[local binary transport](BINARY-PACKAGE.md). The descriptor has the same seven
ordered keys as local-binary-directory-v2, with only its format value changed:
format, record_sha256, target_sha256, modes_sha256, dependencies_sha256,
authenticity=not-proven, service_activation=unsupported. It hashes the four tables
by exact bytes. Existing v2 readers must reject this different descriptor.

The proposed target.kv is the following ordered eight-line record; angle-bracket
values describe required inputs, not literal placeholders admitted by the parser:

```text
format=cross-sdk-target-v1
role=build-inputs-only
build_os=<recorded build OS>
build_arch=<recorded build architecture>
compiler_target=<recorded compiler target string>
build_receipt_sha256=<64 lowercase hex digits>
native_profile_sha256=<64 lowercase hex digits>
modes=recorded-0000-0777
```

Exact ASCII bytes, LF after every row including the last, no CR/NUL, blank rows,
comments, whitespace trimming or duplicate/unknown/reordered keys. Maximum 4096
bytes total. The three identity strings each contain 1–128 characters and match
[A-Za-z0-9][A-Za-z0-9._+-]*. Hash values contain exactly 64 lowercase hex digits;
syntactically valid hashes must still match the required files and caller pins.
There are no optional fields or extension keys. Unsupported behavior needs a new
reviewed format, not silently ignored metadata.

The stage must contain these regular, manifest-bound files beneath
usr/local/share/pkg-mgr/aether-musl-sdk/:

- sdk-target.kv: byte-identical to target.kv.
- sdk-build-receipt: exact reviewed build receipt, hashed by build_receipt_sha256.
- sdk-native-profile: exact owner-supplied profile receipt, hashed by native_profile_sha256.

Receipt bytes are inert and never sourced or evaluated. Their digests bind the
selected documents; this small admission parser does not interpret a native ABI
or prove the statements inside a receipt. Review must establish the receipt's
producer/artifact/source identity and applicable scope before pin selection. The
build receipt must identify the actual compiler/linker inputs and observations;
missing closure remains an explicit build/qualification gap, not a synthesized
success value. The native receipt must identify one exact owner profile and its
producer artifact closure, not a moving STATE document or a locally invented ABI.

The descriptor/record/profile relationship is acyclic: receipt hashes enter the
profile; receipt/profile bytes enter the package manifest/record; the descriptor
hashes record and target. No receipt may require embedding the final package or
descriptor hash. All SDK files and musl COPYRIGHT use the reviewed layout and
remain bound by package.tsv; no second general-purpose manifest format is needed.

## Operation and compatibility proposal

Use explicit sdk-export, sdk-import and sdk-recover branches of mk/binary.sh to
reuse its candidate and publication validation. Do not auto-detect SDK admission
inside existing import/export or add public CLI commands in this first step.
Proposed signatures (not currently supported):

```text
sh mk/binary.sh sdk-export ROOT NAME EXPECTED-PROFILE-SHA256
sh mk/binary.sh sdk-import ROOT BUNDLE DESCRIPTOR-SHA256 EXPECTED-PROFILE-SHA256
sh mk/binary.sh sdk-recover ROOT BUNDLE DESCRIPTOR-SHA256 EXPECTED-PROFILE-SHA256
```

Only NAME=aether-musl-sdk is admitted initially. Reject nonempty dependency tables
for this first standalone SDK package; compiler and consumer adapters are external
prerequisites, not fake installed dependencies. Future consumers can depend on its
exact registered record under existing rules, but their own native admission and
static build-input binding are separate work. An empty dependencies.tsv must agree
with an empty package dependency list. Do not generalize host dependency observations
or change ordinary binary imports while implementing this experiment.

Both export and import require the expected profile hash, strict profile schema,
manifest-bound profile equality, receipt hashes, exact modes and complete existing
state validation. Import also requires its independently selected descriptor hash.
Validate blob names/content and all record invariants before candidate publication.
Receipt/hash/profile errors must not fall back to host-only. Build OS/architecture
are provenance, not uname equality checks against the data-import host; this is
an explicit scope distinction from executable host-v2 admission, not a guarantee
that the external compiler runs there. SDK-05 must separately qualify its actual
compiler invocation without ambient header/libc/helper fallback.

No preflight, replacement or installed-SDK update branch is opened. Existing
host-v2 command arguments, descriptors, target checks and exit/output contracts
must stay byte-compatible. A registered SDK record is inspectable through state
views; attempting ordinary binary export must fail because SDK export requires its
explicit profile path. A native executable cannot become admissible by choosing
an SDK name or role: this profile conveys only selected build inputs, with no
execution action or compatibility approval. Caller-reviewed package content remains
trusted; data classification is not executable-content confinement.

For new branches, propose status64 for invalid invocation, status1 for validation,
I/O or unsupported-profile rejection, and status0 only after confirmed completion.
They should use the existing binary-error stderr style and explicit
sdk-exported/sdk-imported/sdk-recovered TAB NAME TAB DESCRIPTOR-SHA256 success rows.
No success row before confirmed publication or after failure to deliver that row;
a delivery error may leave committed state and requires inspection/recovery.
Exact new output bytes need fixture coverage before becoming a supported contract.

The existing single-writer/caller-controlled filesystem restriction applies. Do
not introduce a new hostile-input resource-limit claim for inherited package/blob
handling; the 4096-byte bound above applies only to the new target record. Validate
that bound before loading/parsing the profile. Existing scratch cleanup, occupied
stage denial and [explicit recovery](IMPORT-RECOVERY.md) remain required. Recovery
must redo the same profile/descriptor/receipt validation and preserve every byte
of an existing mismatched stage; no repair or deletion. Atomicity across stage and
record, disk durability and protection against hostile path races remain unproven.

## Required implementation oracles

| Control | Required result before admitting a real SDK |
| --- | --- |
| Valid reviewed SDK | Both private roots have identical record, selected SDK/notice/receipt/profile bytes and ordinary modes after export/import; unrelated sentinel unchanged |
| Legacy compatibility | Existing full host suite passes; old host-v2 import rejects SDK descriptor and new SDK branches reject host-v2, without changing existing result contracts |
| Profile grammar | Reject every missing/duplicate/reordered/unknown key, bad version/role, malformed hash/string, CR/NUL/missing LF and 4097-byte profile; exercise limits and I/O read failures |
| Independent policy | Correctly rehash a wrong profile and descriptor; rejection must still follow the separately supplied expected profile pin |
| Binding | Alter a receipt or the manifest-bound sdk-target.kv while keeping outer target unchanged; reject. Also reject self-consistently rehashed substituted receipt/profile under the old caller pin |
| Content/state | Same-size SDK corruption, mode change, unsupported link/special entry, occupied stage, wrong name and nonempty/mismatched dependency list reject without final publication or sentinel changes |
| Interruption | Kill before and between stage/record publication; retry/import/recovery outcomes match retained-state rules. Wrong pin, profile or changed retained file prevents recovery without alteration |
| Result delivery | Inject stdout failure after commit; nonzero result, no complete success receipt, record remains valid and explicit recovery is safe |

These are planned tests, **NOT RUN**. The positive real-package case must use the
reviewed SDK and a delivered exact native profile receipt. Synthetic parser cases
must remain labelled fixtures and cannot close SDK-01–08. Capture all failed
attempts, exact tested sources/tools, roots and outcomes. Run the standards gate,
changed-shell lint and full sh tests/check.sh for any eventual implementation.

## Decision still required before implementation

Userland must review the representation and supply the chosen native-profile
receipt with its producer identity, plus the precise build receipt selected for
this package. Its current material bundle is verified but has not been mapped to
those two required receipts. The consumer's selected I/O/memory adapters remain
separate SDK-05/08 inputs. No agreement or completed delivery is inferred here.

This proposal is local package-domain design under pinned Foundations O-01/02,
I-01/02/03/06/08 and E-01–05. Cross-project policy changes still belong in
Aether-standards. This adds no standard, exception, immutable release or runtime
conformance claim. Next: affected-owner review of this concrete proposal, then a
bounded implementation once exact receipt selection is settled.
