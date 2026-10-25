/* Single-threaded, eight-descriptor facade over caller-bound native streams. */
static signed char fds[8] = {0, 1, 2, -1, -1, -1, -1, -1};
static unsigned refs[3] = {1, 1, 1};
static long trap(unsigned long op, unsigned long a, unsigned long b, unsigned long c)
{
    long result;
    __asm__ __volatile__("int $0x81" : "=a"(result) : "a"(op), "D"(a), "S"(b), "d"(c) : "rcx", "r8", "memory");
    return result;
}
static int valid(unsigned long fd) { return fd < 8 && fds[fd] >= 0; }
static long drop(unsigned long fd)
{
    unsigned stream = (unsigned)fds[fd];
    if (refs[stream] == 1) { long r = trap(0x21002, stream, 0, 0); if (r < 0) return r; }
    fds[fd] = -1; refs[stream]--; return 0;
}
long __aether_io(unsigned long op, unsigned long a, unsigned long b, unsigned long c)
{
    if (!valid(a)) return -9;
    if (op == 0 || op == 1)
        return trap(op == 0 ? 0x21000 : 0x21001, (unsigned)fds[a], b, c);
    if (op == 3) return drop(a);
    if (op == 32) {
        for (unsigned fd = 0; fd < 8; fd++) if (fds[fd] == -1) {
            fds[fd] = fds[a];
#ifndef AETHER_BAD_DUP
            refs[(unsigned)fds[a]]++;
#endif
            return fd;
        }
        return -24;
    }
    if (op == 33) {
        if (b >= 8) return -9;
        if (a == b) return (long)b;
        unsigned stream = (unsigned)fds[a];
        /* Retain first: source and destination may already alias one stream. */
        refs[stream]++;
        if (valid(b)) { long r = drop(b); if (r < 0) { refs[stream]--; return r; } }
        fds[b] = (signed char)stream;
        return (long)b;
    }
    return -38;
}
