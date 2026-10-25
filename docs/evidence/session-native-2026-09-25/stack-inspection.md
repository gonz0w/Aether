# Linked SESSION stack inspection

The six probe owners are bound by SHA-256 to their raw/ELF counterparts in
`probe-stack-bindings.json`. The final retained-writer owner is separately bound by
`final-stack-comparison.json` and `owner-preflight-3.*`; the other five raw binaries
are unchanged. All consume at most3688 of4088 usable user stack bytes. Existing
serial/pipeline/early legacy critical paths retain their prior inspected bounds
because final raw bytes match the sealed prerequisite packet.

`indirect-inspection-inputs.json` records the inspected immutable .text GOT cells
and register-call loads. All cells resolve to memcpy/memset/memcmp; register calls
load those same cells before use. The linked code has no indirect jump or recursive
path accepted by the inspection aid. The initial draft's r12-to-rcx transfer was
also inspected; that form is absent in the final composed owner. The final writer
repair removes its ignore-close branch; it does not add a new indirect call target.

The aid traverses instruction control flow, checks stack-depth joins and includes
push/pop/sub/add, return addresses, red-zone references, tail calls and panic paths.
At indirect calls it conservatively charges the largest of the inspected builtin
paths. Its limitations remain explicit: compiler-output-specific inspection,
no formal proof, no kernel-stack bound, no guarantee under memory corruption or
arbitrary future compiler/source changes. It is not an independent reader review.
