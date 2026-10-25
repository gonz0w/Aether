/* SPDX-License-Identifier: BSD-2-Clause */
/* Fixed native exec/wait probe, not a shell or descriptor-policy service. */
#include <stdint.h>
#include <sys/auxv.h>
#include <unistd.h>
static _Thread_local volatile unsigned guard = 17;
static long trap(long op, long a, long b, long c, long d)
{
    register long r10 __asm__("r10") = d;
    register long r8 __asm__("r8") = 0, r9 __asm__("r9") = 0;
    __asm__ volatile("int $0x81"
                     : "+a"(op), "+D"(a), "+S"(b), "+d"(c), "+r"(r10), "+r"(r8),
                       "+r"(r9)
                     :
                     : "rcx", "r11", "memory", "cc");
    return op;
}
int main(int argc, char **argv)
{
    if (guard != 17 || argc != 1 || argv[0][0] != 'p' || getpid() <= 0 ||
        getppid() <= 0)
        return 61;
    /* A copied number supplies no engine thread, block or factory authority. */
    if (getauxval(0xa001) != 0 || trap(0x28000, 0, 0, 0, 0) != -38 ||
        trap(0x27006, 0xf101, 0, 32, 0) != -13 ||
        trap(0x24000, 0xd002, 0, 0, 0) != -13)
        return 62;
#ifdef REPLACEMENT
    return write(1, "P", 1) == 1 ? 0 : 63;
#else
    (void)trap(0x23003, 0, 0, 0, 0);
    return 64; /* Must be replaced while frozen, never resumed here. */
#endif
}
