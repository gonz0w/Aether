# Native OpenZFS startup link and prerequisite audit — 2026-10-04

**A real static startup image now links; engine execution remains blocked.**
The [contract](contract.md) and [source review](source-review.md) record the scoped
R1-03 work and native SDK defects. Kernel/runtime, siblings, quotas, released pins
and normal boot are unchanged. This is private port evidence, not a mounted
filesystem or release image.

Setup verifies all manifest files and every5037/548/666 member of the sealed
[engine](../openzfs-musl-startup-2026-10-04/README.md),
[support](../openzfs-native-support-2026-10-04/README.md) and
[XDR](../openzfs-native-xdr-2026-10-04/README.md) inputs before extraction.
SDK/tools/header inventories are bound in the receipts and frozen through runs.

## Link closure and diagnostic behavior

The private AETHER_NATIVE_PROFILE preserves assertions but uses a constant ASCII
stderr diagnostic and _Exit(125), without allocator, identity discovery, locks,
format/argument disclosure or unwinding. Enabling nonfatal assertion mode also
terminates125. The upstream no-unwind fallback performs an actual write to the
caller's descriptor and says traceback unavailable; no successful frames are
fabricated. Derived CDDL source, original source and diffs retain their notices.

Unchanged zutil path and Linux getmntany sources are rebuilt with function/data
sections. Strict startup GC retains actual tunable registrations with
`-z nostart-stop-gc`; unreachable device discovery and mount-table/TLS are removed
without raising quotas or adding platform stubs. Whole-object link still rejects
zfs_append_partition/zpool_default_search_paths. Explicitly rooting both discovery
functions still rejects those exact missing imports. This does not implement a
general device-discovery API.

The existing source-built native-memory adapter binds __aether_io with actual
scoped fixture mappings, not a filesystem backend. Actual startup calls
kernel_init/fini and checks an initialized TLS marker17, but is only linked and
parsed here. [Build results](build-results.json) bind the static image and denials.
No external import or relocation remains. musl retains a zero-valued local hidden
UND _DYNAMIC sentinel; this is recorded separately, not waived as a missing API.

[Native diagnostic results](native-results.json) qualify four optimized images:

| Case | Native result in both isolated contexts |
| --- | --- |
| No-trace fallback | A real write to invalid descriptor rejects EBADF; both finish0 with existing24-byte output/64-yield acceptance. |
| Deliberately silent fallback | Both exit222 at the exact named check and ordered terminal/panic oracle. |
| Fatal assertion | Both exit125; a denied diagnostic write cannot return to the failed invariant. |
| Attempted nonfatal mode | Both exit125 before returning from the setter. |

FD2 is unbound in this legacy fixture. Actual diagnostic delivery, reentrant or
interrupted reporting and general SPL compatibility remain unqualified. These are
private diagnostic controls, not an executed engine or production SDK adoption.

## Geometry and unsafe runtime prerequisites

The [geometry witness](geometry-results.json) uses unchanged actual loader/parser
copies. The4,371,768-byte image has four load segments and4 bytes of TLS. Ordinary
limits reject it; existing large-image layout accepts1309 pages including the
fixed64KiB stack, leaving739 pages (3,026,944 bytes). W+X and4097-byte TLS controls
reject. This describes admission geometry, not RSS, peak heap, child stacks or
proof that the selected engine profile fits.

[Final prerequisite results](prerequisite-results.json) execute only small public
SDK operations, never kernel_init or a disk. Actual clock/sysinfo/uname/getentropy
and random-device calls lack native providers. Raw calls and identity/resource/
entropy probes reject ENOSYS without changing caller buffers; public monotonic
clock maps the error to EINVAL. Random-device open rejects ENOSYS.

Two SDK assumptions block safe startup: public realtime clock reports false
success after failed gettimeofday, and physical-page sysconf reads an
uninitialized result after failed sysinfo. Native reproduction, exact source and
linked instructions are retained. The final probe characterizes the false clock
success as a defect and avoids repeating the unsafe sysconf call. A passing
classification probe is not a passing provider. Userland needs error-guard fixes
and a matched SDK delivery; Aether still needs real scoped providers, feature/
CPU-state review and resource/thread admission before native startup/fini/restart.
See [owner requirements](source-review.md#owner-work-before-engine-execution).

## Retained attempts and checks

All failures remain: first link loses tunable bounds under GC; second links but
its overly strict nm audit rejects the local hidden _DYNAMIC sentinel; a patch
context/existing-directory runner preflight fails before compiling; third build
correctly retains tunables and audits the actual sentinel. First prerequisite
expectation exits230 because monotonic public errno is EINVAL, not ENOSYS. Second
passes the false-clock characterization then exits232 at unsafe physical-page
sysconf. Third safely classifies sysinfo/entropy/device failures and passes.
Each failed attempt keeps its own source/receipt/log/image; no failure is relabeled.
Initial geometry and the formatted identical-semantics repeat are retained.

Full133-Python host suite plus configured Zig/Rust/pins/workflow, Experience,
simplicity digests, scoped C/Zig formatting, Python syntax and local-file links
pass. Host-header/unknown-platform and rooted discovery link controls reject
exactly. Required inputs remain frozen through qualified runs. No unrelated
runtime change requires additional kernel target suites.

Original recipes/probes use BSD-2-Clause. OpenZFS
[license](LICENSE.OpenZFS)/[copyright](COPYRIGHT.OpenZFS), bundled dependency and
[musl notices](COPYRIGHT.musl) remain distinct. This adds no engine payload to the
normal ISO and grants no distribution clearance. Exact reused source bytes/notices
remain in the preceding sealed packets; new adaptations remain in this archive.

Private [build](build.py), [diagnostic](native.py), [prerequisite](prerequisites.py),
[check](checks.py) and [retention](archive.py) recipes are evidence, not maintained
developer entry points. Reproduce in fresh output/packet locations using verified
prior inputs and stated SDK/tools; do not overwrite sealed evidence. Every new
archive member and all three reused trees verify before removing only this turn's
owned output root. The engine is blocked at prerequisites; granted storage and
Rust filesystem/package integration follow actual startup/fini/restart evidence.
