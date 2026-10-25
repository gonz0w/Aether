# Fresh-root kernel backing aliases

Status: isolated bounded qualification passes,2026-10-04. [Before-code scope](contract.md)
adds actual fresh-root alias protection to the isolated boot-reserved64MiB pool.
No native State/quota, public ABI, SDK, released pin or sibling changes.
[Reference](../../NATIVE-BACKING.md) defines the private modes and limits.

Run `python3 docs/evidence/native-backing-alias-2026-10-04/native.py` with the
pinned offline tools, then `zig build test` and selected existing default/large
memory and two-core regressions. These one-off recipes are evidence, not a new
public runtime/tool entry point. Native service backing and full-engine admission
remain local work; SDK/reader review and assembled R1 gates remain separate.

First target attempt passes all13 cases: five new positives (two-root pattern/
whole-region zero/reuse and four exact hardware faults), four actual omission
controls with their forbidden-progression panics, and the four old reservation
cases. Real #PF records bind vector14, CR2ffff900000000000, CPL and exact errors
3(RO write),17(NX execute),5(user read),0(detached read). User-code progression
under deliberately exposed U-S reaches INT128 with the observed0xc3 byte; it
cannot pass on a generic fault. Kernel text/code immutability, mapped stack/
descriptor storage, WP/NX/four-level/no-PCID checks and inherited-global flush
are explicit. No frame is obtained through kernel-image pointer subtraction.

Fresh target coverage totals45:13 lab,25 default/large memory and seven M4.
All137 Python host cases plus Zig/Rust/offline pins and two geometry tests pass.
The actual omitted frame-bound check fails exact TestExpectedError. The preceding
181-case memory-plan packet binds unchanged native memory/execution/owner/client
bodies; ordinary profiles compile out this lab. That binding is historical
coverage, not181 fresh cases at this revision. The fresh memory/M4 suites prove
the changed ordinary boot/exception dispatch, while new lab cases execute it.
All13 release-designated lab configurations reject the exact guard.

A copied one-off compatibility wrapper repeated the previous global-directory
counting mistake when M4 ran concurrently. Its default-memory target receipt
actually passes all12 cases and matches final source bytes. The wrapper failure,
recipe and logs are retained. The retry reads the producer's exact output path,
recovers the complete default receipt and freshly runs all13 large cases. No
failed attempt is silently discarded or accepted as semantic rejection.

The pre-integration model, target source/packet at launch, raw logs, exact tool/
artifact/command/time receipts, SDK adaptation and licensing remain in the seal.
All1979+5037 upstream SDK/source archive members verify. Legacy SDK receipt names
are private byte-identical copies; pinned SDK originals and sibling repos remain
unchanged. Every owned archive member is read back before duplicate cleanup.
Tools: Zig0.16.0, Rust1.98.0, Clang/LLD21.1.8, Python3.14.7 and QEMU11.1.1 with
q35/qemu64/TCG. Builds180seconds, VM30seconds, owned teardown3seconds; force-kill
fails. No hardware/DMA/cross-core/general VM, service memory or full engine claim.

Next bind one explicit native owner to the retained region with off-stack page
metadata and reviewed table/resource/lifetime limits. Do not enlarge every static
State or treat64MiB as an observed engine budget. Live-worker capacity, genuine
native allocation/stack evidence, identity/configuration, feature closure and
full engine startup/fini/restart still precede filesystem/package composition.
These remain local implementation tasks; we are not externally blocked.
