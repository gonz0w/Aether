# Scoped linked-image inspection

Both final images use GOT cells4026a0/4026a8/4026b0 for linked memset/memcpy/memcmp.
Register-indirect calls are limited to launch rbx/memset (4002a5–400304) and
r13/memcpy (4002e3–400330), setup r14/memset (400bde–400c10), and dispatch
rbx/memcpy (400ec1–400eda). Loaded targets are not replaced before their call;
callee-saved registers persist across intervening builtin calls. The two images
have corresponding call-site layouts, with the delayed predicate elsewhere.
No indirect tail jumps appear. Raw extraction equals owner.raw for both images.
The conservative stack aid includes all present memory builtins; maximum3784/4088
is an inspection estimate, not formal all-path or kernel-stack assurance.
