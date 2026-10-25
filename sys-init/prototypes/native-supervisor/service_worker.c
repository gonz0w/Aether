/* SPDX-License-Identifier: BSD-2-Clause */
/* Fixture worker for decision 0019 follow-on; not a production service API. */
#include <stdint.h>
#include <sys/auxv.h>
#include <string.h>

static _Thread_local volatile unsigned tag = 29;

static long native(unsigned long operation, unsigned long holder,
                   unsigned long a, unsigned long b)
{
    register unsigned long r10 __asm__("r10") = 0;
    register unsigned long r8 __asm__("r8") = 0;
    register unsigned long r9 __asm__("r9") = 0;
    __asm__ __volatile__("int $0x81"
                         : "+a"(operation), "+D"(holder), "+S"(a), "+d"(b),
                           "+r"(r10), "+r"(r8), "+r"(r9)
                         :
                         : "rcx", "r11", "memory");
    return (long)operation;
}

int main(int argc, char **argv)
{
    unsigned char ready = 42;
    unsigned long writer;
    long result;

    (void)argv;
    if (argc != 2 || tag != 29) return 71;
    writer = getauxval(0xa001);
    if (!strcmp(argv[1], "silent")) {
        for (;;) native(0x1fffe, 0, 0, 0);
    }
    if (!strcmp(argv[1], "malformed")) ready = 41;
    if (native(0x24002, writer, (uintptr_t)&ready, 1) != 1) return 72;
    if (native(0x20004, 0, 0, 0) != 0) return 73;

    /* Terminal-kind collision stimuli, after readiness publication. */
    if (!strcmp(argv[1], "terminal-exit134")) return 134;
    if (!strcmp(argv[1], "terminal-exit143")) return 143;
    if (!strcmp(argv[1], "terminal-exit17")) return 17;
    if (!strcmp(argv[1], "terminal-fault")) __asm__ __volatile__("ud2");

    /* The supervisor closes its reader only after dependent admission. */
    for (;;) {
        result = native(0x24002, writer, (uintptr_t)&ready, 1);
        if (result == -32) return 17;
        if (result != 1 && result != -11) return 74;
        native(0x1fffe, 0, 0, 0);
    }
}
