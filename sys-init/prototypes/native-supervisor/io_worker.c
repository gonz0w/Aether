// SPDX-License-Identifier: BSD-2-Clause
#include <errno.h>
#include <unistd.h>

static _Thread_local volatile int tag = 17;
static long native(unsigned long op)
{
    long result;
    __asm__ __volatile__("int $0x81" : "=a"(result) : "a"(op), "D"(0ul), "S"(0ul)
                         : "rcx", "rdx", "r8", "memory");
    return result;
}
#ifdef READINESS_AUTHORITY
static long attempt(unsigned long op, unsigned long holder, unsigned long argument)
{
    long result;
    __asm__ __volatile__("int $0x81" : "=a"(result) : "a"(op), "D"(holder), "S"(argument)
                         : "rcx", "rdx", "r8", "memory");
    return result;
}
#endif
int main(void)
{
    long generation = native(0x20005);
    if (tag != 17 || generation < 1 || generation > 2) return 20;
#ifdef READINESS_AUTHORITY
    const unsigned long controls[] = {0x20000, 0x20001, 0x20002, 0x20003,
                                      0x20006, 0x20007, 0x20008, 0x20009};
    const unsigned long holders[] = {0, 0xa001, ~0ul};
    for (unsigned i = 0; i < sizeof(controls)/sizeof(controls[0]); ++i)
        for (unsigned j = 0; j < sizeof(holders)/sizeof(holders[0]); ++j)
            if (attempt(controls[i], holders[j], j == 0 ? 0 : ~0ul) != -13) return 27;
#endif
    char out[] = "out:0\n", err[] = "err:0\n";
    out[4] = err[4] = (char)('0' + generation);
    if (write(1, out, 6) != 6 || write(2, err, 6) != 6) return 21;
#ifndef READINESS_ORDERING
    if (native(0x20004) != 0) return 22;
#endif
    for (unsigned i = 0; i < 100000; ++i) {
        char command = 0;
        ssize_t n = read(0, &command, 1);
        if (n == -1 && errno == EAGAIN) { native(0x1fffe); continue; }
        if (n != 1) return 23;
#ifdef READINESS_ORDERING
        if (command == 'R' || command == 'D') {
#ifdef READINESS_AUTHORITY
            if (attempt(0x20004, 0xa001, ~0ul) != 0 ||
                attempt(0x20004, ~0ul, 0xa001) != 0) return 28;
#else
            if (native(0x20004) != 0) return 22;
#endif
            if (command == 'D') { __asm__ __volatile__("ud2"); return 24; }
            return 0;
        }
#endif
        if (command == 'F') { __asm__ __volatile__("ud2"); return 24; }
        if (command == 'X') return 0;
        return 25;
    }
    return 26;
}
