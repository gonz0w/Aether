# UL-005 bounded SDK handoff: technical review packet

For an independent reviewer of the experimental SDK/package handoff. This packet
is ready for review, not approved. The current task verified producer/consumer
identity edges and scoped evidence; it cannot supply its own independent sign-off.
Userland owns this acceptance record; pkg-mgr retains package policy and formats.

## Proposed acceptance scope

One pinned musl cross-SDK transported through private package roots, explicit
missing historical host provenance, an imported-SDK startup/adapter link, bounded
static dependency observations, and native positive/denial checks against a
verified historical producer. No live install, SDK update API, automatic rebuild
scheduler, full POSIX/TTY support or source-trust approval is proposed.

| Gate | Executed evidence / review disposition |
| --- | --- |
| SDK-01/02 | Real owner registration/export/import, all 235 bytes/modes and records corroborated by [imported consumer review](../evidence/sdk-imported-consumer-2026-09-07/README.md) |
| SDK-03/04/06 | [Owner real transport](../../../pkg-mgr/docs/SDK-REAL-HANDOFF.md): six real denials and stage-publication interruption/recovery; broader grammar/type/result-delivery coverage remains separately labelled synthetic |
| SDK-05 | [Corrected io_probe startup](../evidence/sdk-startup-link-2026-09-07/README.md): receipt/source checks, changed-source rejection, explicit imported libc/startup/adapters, missing header/libc/crt/I/O/memory-path/helper controls |
| SDK-07 local | [Relink witness](../evidence/sdk-static-rebuild-2026-09-07/README.md): unused archive change invalidates input binding even with identical relinked ELF; fresh ELF checks and retained old/new bindings |
| SDK-07 package | [Owner experiment](../../../pkg-mgr/docs/SDK-STATIC-BINDING.md) plus [consumer review](../evidence/sdk-package-review-2026-09-07/README.md): real registered direct dependency and manifest-bound SDK/input/ELF observations; new records differ with equal ELF |
| SDK-08 bounded | [Matched native run](../evidence/sdk08-matched-2026-09-07/README.md): two successful generations, reclaimed2; withheld memory grant yields worker61 and exact supervisor/profile rejection; host cleanup complete |

Review each gate within its stated scope. Full SDK-07 supported update integration
is not implemented. Its one-off direct-consumer comparison is valid evidence of
rebuild tracking, not enforcement by ordinary state verify. SDK-08 does not prove
denial-side native reclaim: that guest reports reclaimed0 before panic. Positive
reclaim must not be generalized to that path. Decide whether these bounded slices
satisfy this experimental UL-005 gate; do not silently expand or waive it.

## Required reviewer checks

1. Confirm accepted target and descriptor pins, unchanged SDK/libc/source notices,
   and the meaning of literal unrecorded host fields. These observations do not
   supply source authentication or original build-host qualification.
2. Check corrected io_probe selection against the SDK receipt and actual link
   inputs. Prior successful probe.c evidence is explicitly a different source set.
3. Review the local preflight controls below and their private-filesystem limits.
   Check static archive/SDK/input/ELF/consumer-record identity edges and the actual
   direct dependency. A changed record can include changed advisory metadata;
   do not attribute all record change solely to ABI differences.
4. Check positive serial markers and exact denial61, supervisor211/reclaimed0 and
   rejection panic. The old live-snapshot supervisor214 attempt and the wrong
   IO FAIL harness expectation remain incomplete attempts, not erased failures.
5. Confirm current claims exclude transitive scheduling, automatic admission of
   changed SDKs, denial-native-reclaim, full native suite and release support.

Record reviewer identity, reviewed packet/source hashes, findings and disposition.
Technical review is separate from any reader walkthrough or maintainer release
approval. Do not infer approval from checking hashes or a generic 'tests pass'.

## Remaining owner work and follow-ons

- pkg-mgr: before supported updates, define a read-only binding/plan contract with
  missing/stale binding rejection, independent candidate pins and explicit direct
  versus transitive scope. Existing state verify does not interpret the JSON data.
- Userland/native owners: denial-native-reclaim needs a separate workload and
  oracle before claiming it. The tested old profile is not current-kernel adoption.
- UL-003/016/012 retain broad ABI, source-trust and assembled-base gates. UL-061/062
  retain documentation/extended-review obligations; none closes by SDK transport.

UL-005 remains active pending independent review and disposition of the bounded
acceptance scope. No package-owner implementation, message or approval is implied.

## SDK-05 local preflight follow-up — 2026-09-07

The maintained startup harness now verifies copied adapter/probe hashes, retains
missing/malformed prerequisite errors, validates consumed object/digest/path fields,
and caps receipt intake at 2 MiB/64 levels with duplicate/nonfinite rejection.
Unavailable evidence storage returns an explicit failure; no retention is claimed
when writing is impossible. The package layout is included in input hashes.

Review [copy verification](../evidence/sdk-copy-check-2026-09-07/README.md),
[receipt failure retention](../evidence/sdk-receipt-failures-2026-09-07/README.md),
[field/path controls](../evidence/sdk-schema-2026-09-07/README.md), and the
[final preflight evidence](../evidence/sdk-preflight-2026-09-07/README.md). The final
source inventory there binds the harness and all four control scripts. Earlier
regressions and the final 13-command link pass with the original io_probe ELF hash.
The first nesting test failed because this interpreter accepted deep JSON; the
explicit depth check and rerun are retained. No native rerun is claimed.

This local preflight slice is ready for independent review. Limits remain: trusted
private staging after validation, no measured RSS/total in-process deadline, and
no guarantee of retained evidence on unavailable storage. These limits do not waive
any claimed native authority, cleanup, package-owner integration or source-trust gate.
