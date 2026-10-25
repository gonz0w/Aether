# Native memory-XDR and nvpair — 2026-10-04

**Real serialization now builds and passes a bounded Aether QEMU witness.** The
complete engine startup still does not link or execute. This R1-03 experiment
extends the sealed [engine build](../openzfs-musl-startup-2026-10-04/README.md) and
[support closure](../openzfs-native-support-2026-10-04/README.md), verifying both
packet manifests and every5037/548 archive member before private extraction.
Kernel/runtime, sibling repositories and released standards pins are unchanged.

[Contract](contract.md) records implementation scope, security and simplicity.
Eight unchanged upstream sources compile: six libtirpc memory/primitive/array/
reference/size/float units plus nvpair.c and nvpair_alloc_system.c. No RPC network,
auth, record or stdio transport is linked. Existing SPL include_next wrappers use
real RPC headers; no XDR backend or assertion is disabled. GNU99 comparison builds
retain60 upstream K&R deprecation warnings; they are not warning-clean Coding-profile
adoption. Both nvpair sources compile without warnings. New probe uses the reviewed
C formatter and -Wall/-Wextra/-Werror. Native fixture driver retains its existing
C11/freestanding/no-builtin flags.

The aggregate resolves all98 previous nvpair-family imports. Its177 imports include
172 SDK exports and five non-SDK names; LLD supplies actual tunable section bounds.
Strict startup fails with four named imports: libspl_backtrace, zfs_append_partition,
zpool_default_search_paths and __aether_io. No successful stub or ignored import
produces an engine executable. Whole-object imports include non-startup paths;
these are not a minimal startup dependency list or kernel-operation count.
Exact [build results](build-results.json) retain flags, hashes, warnings and denials.

## Native behavior and security boundary

The private [probe](probe.c) links only these serialization objects with the pinned
strict-musl SDK and existing memory conformance adapter. It executes in two isolated
instances under QEMU11.1.1/q35/TCG/qemu64, each with its existing128-page grant.
Both finish0 with the required24-byte output and64 yields. The loader reports42
initial pages per instance and86 remaining; this is fixture image/stack admission,
not peak allocation or an engine resource budget. No disk, filesystem or service runs.

| Case | Observed result |
| --- | --- |
| Encoding | Independent network-order bytes for int32/uint64/opaque/string and a scalar nvpair; aligned and unaligned memory-XDR both pass. |
| Decoding | Primitive values, nested list/string and uint32 array roundtrip; eight public allocator/pack/unpack cycles also pass. |
| Boundaries | Every shorter prefix of the bounded primitive and nested-list packets rejects; cursor limits, caller string bound, excessive name/decode length, element count, unknown type and unknown encoding reject. |
| Ownership | Input snapshots and outer canaries stay unchanged. Counting allocator returns to its baseline after each decode failure; each allocation in a valid nested decode is denied in turn, with failure cleanup checked. Successful frees return the counter to zero. This is not an allocator sanitizer or a proof for arbitrary inputs. |
| Deliberate broken encoder | Only xdr_mem's word conversion is changed. Both tasks exit210 at the independent byte check; exact ordered terminal/panic oracle passes. No watchdog or loader failure substitutes. |
| Assertion control | Probe-only libspl_assertf never returns and exits217; explicit invocation in both tasks is rejected at the exact terminal/panic boundary. It is not the production SPL diagnostic implementation or a fake traceback. |

**Unknown root versions are accepted upstream.** A new expectation that version
corruption would reject failed natively at214. Source review finds nvs_xdr_nvlist
decodes root version/flags without validation. The final probe explicitly verifies
acceptance of -1, unchanged input and complete cleanup. This characterizes the
dependency, not approval of unknown schemas. Before the future Rust service consumes
untrusted metadata it must validate its supported root version/schema, bounds and
semantic requirements. No decoded name or pointer grants resource authority.
Fuzzing/deeper recursion/overflow corpora, sanitizer coverage, broader allocation
and interruption schedules remain open before persisted-data ingress is exposed.

[Native results](native-results.json) bind the final three images, object/source/
SDK/compiler-header/tool/runtime inventories and QEMU traces. Final sources are
frozen throughout builds/runs. This is bounded serializer evidence, not native
OpenZFS startup, filesystem security, production SDK or whole-system conformance.

## Dependency and retained failures

libtirpc1.3.6 matches the recorded Linux host baseline. Explicit setup downloaded
the [upstream archive](https://sourceforge.net/projects/libtirpc/files/libtirpc/1.3.6/)
and verified SHA256 bbd26a8f0df5690a62a47f6aa30f797f3ef8d02560d1bc449a83066b5a1d3508,
size566384, against the [Buildroot checksum record](https://lists.buildroot.org/pipermail/buildroot/2025-December/791251.html).
These establish byte identity, not signer authentication or newest-release status.
[Fetch receipt](fetch.json) keeps the initial sandbox DNS failure and successful
explicit fetch separate from offline builds. No normal build downloads or follows
mutable sibling dependency bytes.

Safe extraction initially rejected an absolute INSTALL documentation symlink. The
partial tree is retained. Retry omits only that unused external document link and
uses Python's data filter on every other member; no external target was accessed.
The original archive retains all metadata and notices. [COPYING](LICENSE.libtirpc)
has BSD-style three-clause terms; full sources preserve additional per-file Sun/
other notices. OpenZFS [license](LICENSE.OpenZFS) and [copyright](COPYRIGHT.OpenZFS),
SDK musl notices and compiler inputs retain their own terms in the bound inputs.
Original probe/tooling uses BSD-2-Clause; no third-party relicensing, default ISO
payload change or distribution approval follows.

All six native attempts are preserved: initial runner assumes absent build/lock
files (no compiler); missing debug-header include/incorrect const pointer (compile
failure); omitted existing fixture compile flags produce an ELF without required
TLS (loader rejection); first bounded three-case pass; extra root-version expectation
fails214; final characterized/public-allocator three-case pass. Restoring the actual
fixture flags resolves the TLS rejection; no loader invariant is relaxed. The precise
optimization responsible for removing later driver code was not independently
localized. Patch-context preflight failure is recorded separately. No failed attempt
is rewritten as a pass.

## Checks, reproduction and next work

Full host/pin/workflow checks, simplicity snapshot digests, private Python syntax,
new C format check and local links pass. Native build-only audit independently
rejects missing mach/mach.h and aether_unreviewed_platform by exact diagnostics.
No kernel/ABI change requires unrelated target regressions; the affected optimized
serialization image and its semantic controls execute on Aether.

Private [build.py](build.py), [native.py](native.py) and [archive.py](archive.py) are
retained experiment recipes, not maintained developer entry points. Reproduce with
copied recipes and fresh output/packet constants, verified prior archives, the stated
libtirpc source and pinned SDK/tools. Never overwrite sealed packets. The explicit
source setup is separate from these offline recipes. Archive readback verifies every
new member and both reused input trees before removing only this turn's owned output
root. Earlier evidence/output roots remain untouched.

Next define the native SPL diagnostics honestly, review zutil discovery reachability
and bind the SDK I/O hook through real scoped adapters. Then feature/CPU-state,
entropy/clock/identity and pthread/resource admission need native startup/fini/restart
evidence before grant-bound volume I/O and Rust filesystem composition. The future
metadata ingress must apply the schema validation noted above. These remain R1-03
work, separate from sys-init's recipe/independent shell composition acceptance.
