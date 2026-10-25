# Scoped register provenance

Final four owner assemblies and immutable GOT cells in inspection.json were
inspected. Launch uses rbx/memset and r13/memcpy, preserved across the bounded
callee-saved builtin calls. Count/padding/foreign setup uses r14/memset; dispatch
copies use rbx/memcpy. Stale setup uses rbx/memset; dispatch uses r12/memcpy, with
no intervening r12 replacement on the path to its three indirect call sites.
The count/padding r11 load-to-call range (40122a–40131e /401227–40131b) and stale
r10 range (401345–401432) contain no other call or target-register write. Foreign
rax load-to-call (400f90–400fb8) contains only checks and argument setup. Cells
resolve only to linked memcpy/memset/memcmp; no indirect tail jump appears.

The allowlist initially rejected r11, then rax, then r10. All three inspection
attempts and their generated outputs remain retained, separate from final pass.
These are contributor inspection aids with conservative builtin stack charge,
not formal control-flow, kernel-stack or all-path proofs.
