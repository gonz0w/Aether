# Init capacity handoff — decision 0174

**Status: resolved for the bounded Terminal experiment by decision 0175.**
AENIN003/ABI 16 passes independent consumption; see the acceptance below.

## Original blocked handoff (historical)

Native Terminal integration was blocked for the composed probe.
The maintained implementation remains decision 0173. The candidate is retained
only as source/build evidence, with no native execution or application claim.
Aether owns the next profile/mechanism decision; BG-061 tracks local qualification.
The maintainer approved requesting an opt-in **16,384-byte init code profile**.
The producer task is now queued as
[Aether SI-06](../../.planning/ROADMAP.md#si-06--composed-init-lifecycle-capacity-16-kib-proposal).
Only Aether's roadmap/state were updated; kernel code and current pins are unchanged.

The candidate keeps the original Application, History, generated launch and its
acknowledged retention alive. A private session exclusively borrows History and
the application while retaining the original generated source. It starts only
with an unused sample, retains actual observe/status/observe returns, and accepts
Terminal only from that session's complete coherent sample. Application then
captures the dependent reclaim obligation. The peer and original receipts stay
owned. This remains a proposal until source review and consuming tests succeed.

## Measured blocker

The unchanged linker rejects every candidate at its two-page assertion. Sizes
below are linker-computed `.text` spans, including constants/GOT, not successful
images, runtime RAM measurements or performance benchmarks.

| Refined candidate build | Positive bytes | Largest control bytes | Result |
| --- | ---: | ---: | --- |
| Existing Rust 1.98.0, opt-level=s | 11,680 | 11,680 | exceeds 8,192 |
| Diagnostic opt-level=z | 15,216 | 15,216 | exceeds 8,192 |
| Diagnostic z, fat LTO, one codegen unit | 11,056 | 11,072 | exceeds 8,192 |

The first draft's baseline positive was 11,608 bytes. The refinement fixes source
association before sampling with an exclusive session, and still does not fit.
Both candidates, all 48 failed bounded link attempts, exact commands and maps,
and the refined assembly are retained in
[evidence](evidence/native-terminal-capacity-2026-09-07/README.md).
No limit was raised, no oversized image was executed and no diagnostic compiler
profile was adopted. These experiments do not rule out a different architecture
or future size reduction; they show this concrete composition cannot be consumed
under the current profile.

Read-only review of Aether's `kernel/native_launch.zig`, `native_c.zig`,
`user_cpu.zig` and `docs/NATIVE-INIT.md` still shows AENIN002/ABI 15, 1..8192-byte
supervisors, two RX code pages and one 4096-byte RW/NX stack. Copies and hashes are
in the evidence packet. These mutable-source observations are review inputs,
not replacement producer pins. A separate general native-C profile does not
supply an accepted init contract merely because it has larger mappings.

## Required producer decision and witness

The selected request is a separately versioned, opt-in 16 KiB init code profile.
This accommodates the measured candidate and provides headroom for the remaining
reclaim/Cleaned integration; it does not guarantee that later stages fit or set a
production memory budget. Aether must define the exact contract and identifiers,
then qualify its implementation. Stack validation remains a separate requirement. Preserve existing
AENIN001/ABI 6 and AENIN002/ABI 15 byte contracts and oversize rejection.
Do not widen native grants, add workers or change lifecycle semantics implicitly.

Specify mapped code pages, zero tail, aliases, permissions, entry, stack and
cleanup. Retain exact limit/boundary and malformed-envelope rejection, execution
from additional code pages, code-write and stack-execute denial, and normal and
closed-owner cleanup witnesses. Preserve affected older profile tests. Provide
complete source/SDK/tool artifacts suitable for independent offline consumption;
the older producer-source closure omission is not permission for another omission.

The candidate's root frame is 3,288 bytes, plus caller, saved-register and nested
frames. Assembly compilation is not a stack safety witness. The 4 KiB stack is
unchanged and still requires consuming validation; do not infer that an image
capacity change alone establishes runtime compatibility.

## Consumer acceptance after the handoff

Review and adapt the candidate to the accepted profile, then prove the positive
Terminal transition and complete reclaim capture. Retain exact owner mismatch,
unsealed source, partial sample, capture omission/corruption and repeated-delivery
results. Native errors must retain their original triples and resources; failed
source/application must close admission. Test stack behavior in the composed path.
Existing fixture disposal is not acknowledgment of the issued reclaim or Cleaned.
Provider Terminal and general mixed cuts remain follow-ons.

Run the required local gates and fresh target witnesses for affected images. Only
then promote candidate code into the maintained native path. Standards releases,
consumer pins, historical evidence and current working native implementation stay
unchanged until an explicit acceptance step.

## Composed Terminal consumption — decision 0175

Decision 0175 independently accepts AENIN003/ABI 16 for the bounded native
Terminal experiment. The producer packet matches its manifest; all 499 source
files match the archived map. A consumer-owned intake receipt preserves the
original producer source/report/envelope bytes and provenance. No sibling file,
shared release pin, old envelope or old evidence was changed.

All 214 sys-init cases pass in fresh Aether QEMU execution from captured sources,
including the generated-dependent Terminal positive (100/reclaimed 3) and five
controls (1094–1098/reclaimed 0). An independent source-extracted replay also
passes all 32 producer composed-profile boundary cases using pinned SDK libc.
Those cases cover page/length boundaries, malformed inputs, code-write and
stack-execute denial, stack guards, dirty-tail rejection and owner cleanup.
This replay rebuilds helpers and kernel, not libc. The 453 upstream cases remain
producer evidence; they are not counted as our executions.

The Terminal session binds the original owner, generated worker and retained
launch acknowledgment before observe/status/observe. Its exclusive borrows keep
the association stable through sampling/application. Actual raw returns are
retained before interpretation. Wrong-owner and premature application deny;
missing/corrupt reclaim capture retains Unknown and closes admission. Local
interruption preserves the two completed reads and prevents further capture or
application. Exact repeat application cannot issue another effect.

The positive image is 11,680 bytes within the explicit 16,384-byte limit. All six
new paths execute with the unchanged 4 KiB stack and no guest fault. This is
bounded path evidence, not a stack high-water measurement or future headroom
claim. The primitive adds no allocation or unsafe site. All 208 ABI-15 and 151
ABI-6 clients rebuild byte-identically to their qualified baseline; no new legacy
target campaign is claimed. All ten development gates pass in run-aoks0khj.

The emitted full reclaim occurrence remains Reserved. Fixture disposal is not
execution/acknowledgment of that occurrence and does not apply Cleaned. Next is
exact issued-reclaim execution and acknowledgment, then Cleaned handling under
BG-057/BG-058. Provider Terminal, general mixed cuts, generated-source errno
variants, sustained retention (BG-060), recovery (BG-033), new-profile catalog
support and independent review remain open. No production POSIX, physical-target,
performance or release-readiness claim follows. There is no current kernel blocker.
