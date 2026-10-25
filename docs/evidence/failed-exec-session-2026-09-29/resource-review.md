# Linked resource review

Scoped contributor inspection, not formal verification or independent reader approval.
All six new owners fit24KiB, maximum16304 bytes. The stack aid bounds the new owners
at3736–3768 of4088 bytes. Eleven rebuilt prior SESSION/recovery owners fit with
bounds3656–3720. No pool, code mapping or usable stack limit changed.

Indirect calls use the immutable memcpy/memset/memcmp GOT words. In new owners,
confirmed_terminal retains memset in r12; new retains memset in r15 and memcpy in
r14; replace retains memcpy in r12. The positive run also uses r13 loaded with
memset. The assignments and call sites are retained in register-call-review.txt;
stack-bindings.json binds resolved words and raw images. The stack aid takes the
maximum of all three memory builtins at each indirect call. These are synchronous
buffer operations; no stack pointer escapes through the new lookup parser.

The greatest new path is _start/run/replace/description/ready/transfer/call. Its
320-byte margin is a bounded experiment result, not spare budget to spend without
new linked inspection. The path and per-function details are in each stack JSON.

The final stderr-closure control has a separate final-stderr-owner disassembly,
stack result, resolved-register receipt and ELF/raw binding. All other sixteen
final owners match the already inspected bytes exactly. final-stack-bindings.json
identifies every final raw image. The maximum remains3768/4088.
