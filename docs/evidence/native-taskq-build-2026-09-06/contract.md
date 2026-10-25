# Native compilation stage

Implement the taskq-specific derived header, explicit appended TSD helpers and
bounded platform module under NATIVE-TASKQ. The first qualification stage is
native-musl object compilation, slot layout proof, relocatable linking and exact
remaining-import inventory. No placeholder implementations of native grant,
worker, failure, wait-observation or reaping hooks; unresolved integration is
reported as missing coverage, not a runnable image. Native boot acceptance follows
only after those hooks are connected to the paired lifecycle adapter.

The private header preserves taskq structures and meaningful upstream constants,
binds kmem macros to a scoped allocator, and directs the forbidden throttle's
clock sampling to explicit failure. It does not invent clock values. CPU discovery
is taskq-only one-core scope, not a global libc override. The source prefix remains
unchanged; helper append and header adaptations retain original/derived hashes.

Select compiler/header/tool pins before compile; keep failed attempts and frozen
sources. Validate exact native layout and reviewed imports; deliberately reduce
a copied slot assertion to prove an oversized layout rejects during compilation.
No upstream or sibling edits, new kernel ABI, production claims or executing
unbound object files. Host/pin/workflow and source formatting checks are required;
they cannot establish runtime allocation/concurrency correctness.
