
## Extended backing experiment contract — 2026-09-06

Before implementation: explicit native-memory-large build option and --large
memory-suite mode select 2048 eager private backing pages (8 MiB) per native slot,
with an 8-MiB arena at the existing base. Default remains 128 pages. This is a
four-leaf transaction experiment justified by the measured 1287-page engine ELF,
not a selected OpenZFS service/cache budget or larger executable admission.
The loader file/image/TLS limits remain unchanged. Opt-in requires native memory.

Keep owner-local grants, errors, zeroing, NX, TLS/TID pins and stop/reclaim semantics.
Use quota-specific planner types and 16-bit backing indices for the large profile;
no global pool or implicit growth. Four fixed slots reserve 32 MiB of backing in
the opt-in kernel image. Expand only that profile's kernel alias coverage to 64 MiB
and reject image overflow before entry. Query reports actual profile quota/end.
Sys-init/userland policies and package pins remain owned by their companions;
this kernel conformance profile is not consumer acceptance. No new dependency/FFI.

Run all eleven existing memory outcomes in both profiles; the large probe also
checks every backing page, cross-leaf protection, full middle-leaf release/reuse
and retained neighbors. A single bad boundary expectation must reject specifically.
Use three large saturation rounds instead of forty small rounds to bound fixture
cost; neither is a performance/soak claim. Host planner tests cover the widened
slot range and exact quota failure. Freeze inputs and retain all attempts; run
host/standards/workflow, scoped formatting and default boot checks. Kernel stack
high-water and native service budget remain unmeasured. Update this reference
and workflow inventory; preserve machine markers and existing adapter ABI.
