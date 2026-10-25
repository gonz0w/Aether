/* SPDX-License-Identifier: BSD-2-Clause */
/* Private protocol failures only. No pool import, block I/O or service policy. */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <sys/auxv.h>
#include <unistd.h>
static _Thread_local volatile unsigned guard = 17;
static long trap(long op, long a, long b, long c, long d)
{
    /* The only pointers are synchronous borrows of initialized local frame or
     * witness buffers; no pointer survives the trap. The kernel checks endpoint
     * ownership, range and transfer length. All ABI result registers and memory
     * effects are declared, including reserved zero r8/r9 inputs. */
    register long r10 __asm__("r10") = d;
    register long r8 __asm__("r8") = 0, r9 __asm__("r9") = 0;
    __asm__ volatile("int $0x81"
                     : "+a"(op), "+D"(a), "+S"(b), "+d"(c), "+r"(r10),
                       "+r"(r8), "+r"(r9)
                     :
                     : "rcx", "r11", "memory", "cc");
    return op;
}
static void witness(unsigned char tag)
{
    uint64_t row = tag;
    if (trap(0x10001, 1, (long)&row, 8, 0) != 8)
        _Exit(90);
}
#if FAILURE != 0
static void frame(uint64_t endpoint, uint64_t body[8], int write)
{
    size_t used = 0;
    for (unsigned attempt = 0; used != 64 && attempt < 100000; ++attempt) {
        size_t count = 64 - used < 16 ? 64 - used : 16;
        long n = trap(write ? 0x24002 : 0x24001, endpoint,
                      (long)((unsigned char *)body + used), count, 0);
        if (n == -11) {
            trap(0x1fffe, 0, 0, 0, 0);
            continue;
        }
        if (n <= 0 || n > 16 || (size_t)n > 64 - used)
            _Exit(91);
        used += (size_t)n;
    }
    if (used != 64)
        _Exit(92);
}
#endif
int main(void)
{
    uint64_t reader = getauxval(0xa004), writer = getauxval(0xa005);
    if (guard != 17 || !reader || !writer || reader == writer)
        return 93;
#if FAILURE == 0
    witness('S');
    return 71;
#else
    uint64_t reply[8] = {0};
    memcpy(reply, "AFSRPC06", 8);
    reply[2] = reader;
    reply[3] = reply[4] = 1;
    if (trap(0x20004, 0, 0, 0, 0))
        return 94;
#if FAILURE == 1
    memcpy(reply, "AFSRPC05", 8);
    witness('G');
    frame(writer, reply, 1);
#else
    uint64_t request[8] = {0};
    frame(writer, reply, 1);
    frame(reader, request, 0);
    if (memcmp(request, "AFSRPC06", 8) || request[1] != 4 ||
        request[2] != reader || request[3] || request[4] || request[5] ||
        request[6] || request[7])
        return 95;
    reply[3] = reply[4] = 0;
#if FAILURE == 2
    reply[2] = reader + 1;
    witness('D');
    frame(writer, reply, 1);
#elif FAILURE == 3
    witness('F');
    frame(writer, reply, 1);
    return 72;
#elif FAILURE == 4
    witness('L');
    if (trap(0x24003, writer, 0, 0, 0))
        return 96;
#else
#error "unsupported fixed failed-peer selection"
#endif
#endif
    for (;;)
        trap(0x1fffe, 0, 0, 0, 0);
#endif
}
