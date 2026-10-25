# Attempts

1. Original input.o: actual interactive prompt appears, but input.c::stdin_tee
allocates a pipe before its non-tee fallback. No child admitted; owner2140. Sources,
logs and named target directories retained under attempt1.
2. Native one-byte fallback: actual dash consumes the host command, launches /next,
child consumes host a and both exit72. Owner2131 catches an incorrect expected
input total: `/next; exit $?\n` is15 bytes, not14; child a makes16. Correct only
that expectation. Output counts24/2 and lifecycle checks are retained. Sources,
logs and named target directories retained under attempt2. Host, launch and old
console/profile checks passed in that round. No general pass is claimed for it.
