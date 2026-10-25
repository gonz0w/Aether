/* SPDX-License-Identifier: BSD-2-Clause */
#include "../native-memory/adapter.h"
#include <sys/auxv.h>
static _Thread_local volatile unsigned int witness = 17;
#define CALL(op, a, b, c)                                                      \
    memtrap(op, 0xf101, (unsigned long)(a), (unsigned long)(b), c)
#include "copy-boundary.h"
int main(void)
{
    unsigned char bytes[512];
    if (witness != 17)
        return 70;
    if (memtrap(0x20005, 0, 0, 0, 0) != 2) {
        for (unsigned long op = 0x27000; op <= 0x27006; ++op)
            if (CALL(op, 0, bytes, 512) != -13)
                return 71;
        return 0;
    }
    unsigned long info[4], tries;
    for (tries = 0; tries < 1000000; ++tries) {
        long n = CALL(0x27006, info, 32, 0);
        if (n == 0)
            break;
        if (n != -13)
            return 72;
        memtrap(0x1fffe, 0, 0, 0, 0);
    }
#ifdef BLOCK_READONLY
    unsigned long rights = 1;
#else
    unsigned long rights = 7;
#endif
    if (tries == 1000000 || info[0] != 512 || info[1] != 16384 ||
        info[2] != rights || info[3])
        return 72;
    volatile unsigned char *edge = (volatile unsigned char *)0x0800ffffUL;
    *edge = 0x5a;
    if (CALL(0x27006, info, 31, 0) != -22 ||
        CALL(0x27006, info, 32, 1) != -22 || CALL(0x27006, 0, 32, 0) != -14 ||
        CALL(0x27006, ~0UL, 32, 0) != -14 ||
        CALL(0x27006, edge, 32, 0) != -14 || *edge != 0x5a ||
        CALL(0x27006, getauxval(3), 32, 0) != -14 ||
        CALL(0x27005, 0, info, 24) != -13)
        return 75;
    if (CALL(0x27000, 16384, bytes, 512) != -22 ||
        CALL(0x27000, ~0UL, bytes, 512) != -22)
        return 76;
    const unsigned long sectors[3] = {0, 777, 16383};
    for (unsigned long j = 0; j < 3; ++j) {
        if (CALL(0x27000, sectors[j], bytes, 512) != 512)
            return 77;
        for (unsigned long i = 0; i < 512; ++i) {
#ifdef BLOCK_VERIFY
            unsigned char expected = (unsigned char)(i * 17 + 91 + j);
#else
            unsigned char expected = (unsigned char)(i * 17 + 3 + j);
#endif
            if (bytes[i] != expected)
                return 73;
        }
        if (j == 0 && !block_copy_boundary(sectors[j], bytes,
#ifdef BLOCK_READONLY
                                           0
#else
                                           1
#endif
                                           ))
            return 86;
#ifdef BLOCK_READONLY
        if (CALL(0x27001, sectors[j], bytes, 512) != -13)
            return 78;
#else
        if (CALL(0x27001, 16384, bytes, 512) != -22)
            return 79;
#ifndef BLOCK_VERIFY
        for (unsigned long i = 0; i < 512; ++i)
            bytes[i] = (unsigned char)(i * 17 + 91 + j);
        if (CALL(0x27001, sectors[j], bytes, 512) != 512)
            return 80;
#endif
#endif
    }
#ifdef BLOCK_READONLY
    if (CALL(0x27002, 0, 0, 0) != -13)
        return 81;
#else
    if (CALL(0x27002, 0, 0, 0) != 0)
        return 82;
#endif
#ifdef BLOCK_FAULT
    __asm__ __volatile__("ud2");
#else
    if (CALL(0x27004, 0, 0, 0) != 0 || CALL(0x27006, info, 32, 0) != -9)
        return 83;
#endif
    return 0;
}
