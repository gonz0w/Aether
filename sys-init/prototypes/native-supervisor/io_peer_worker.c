// SPDX-License-Identifier: BSD-2-Clause
#include <errno.h>
#include <unistd.h>
static _Thread_local volatile int tag = 17;
static long call(unsigned long op, unsigned long h, unsigned long arg)
{
    long result;
    __asm__ __volatile__("int $0x81" : "=a"(result) : "a"(op), "D"(h), "S"(arg)
                         : "rcx", "rdx", "r8", "memory");
    return result;
}
static int byte(void)
{
    for (unsigned i = 0; i < 100000; ++i) {
        unsigned char c;
        ssize_t n = read(0, &c, 1);
        if (n == 1) return c;
        if (n != -1 || errno != EAGAIN) return -1;
        call(0x1fffe, 0, 0);
    }
    return -1;
}
int main(void)
{
    if (tag != 17 || call(0x20005, 0, 0) != 1) return 30;
    if (write(1, "out:1\n", 6) != 6 || write(2, "err:1\n", 6) != 6) return 31;
    unsigned long peer = 0;
    for (unsigned i = 0; i < 8; ++i) {
        int c = byte();
        if (c < 0) return 32;
        peer |= (unsigned long)c << (8*i);
    }
    if (!peer || byte() != 'P') return 33;
    const unsigned long ops[] = {0x20001, 0x20002, 0x20003, 0x20007, 0x20008, 0x20008, 0x20009, 0x20009};
    const unsigned long args[] = {0, 0, 0, 0, '!', 256, 1ul<<32, 2ul<<32};
    for (unsigned i = 0; i < sizeof(ops)/sizeof(ops[0]); ++i)
        if (call(ops[i], peer, args[i]) != -13) return 34;
    if (call(0x20004, peer, peer) != 0) return 35;
    if (write(1, "P", 1) != 1) return 36;
    if (byte() != 'X') return 37;
    return 0;
}
