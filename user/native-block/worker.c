/* SPDX-License-Identifier: BSD-2-Clause */
#include "../native-memory/adapter.h"
#include <sys/auxv.h>
static _Thread_local volatile unsigned int witness = 17;
#define CALL(op, sector, ptr, len)                                             \
    memtrap(op, 0xf101, sector, (unsigned long)(ptr), len)
#include "copy-boundary.h"
int main(void)
{
    unsigned char bytes[512];
    if (witness != 17)
        return 70;
    if (memtrap(0x20005, 0, 0, 0, 0) != 2) {
        for (unsigned long op = 0x27000; op <= 0x27004; ++op)
            if (CALL(op, 0, bytes, 512) != -13)
                return 71;
        return 0;
    }
    unsigned long tries;
    for (tries = 0; tries < 1000000; ++tries) {
        long n = CALL(0x27000, 0, bytes, 512);
        if (n == 512)
            break;
        if (n != -13)
            return 72;
        memtrap(0x1fffe, 0, 0, 0, 0);
    }
    if (tries == 1000000)
        return 72;
    for (unsigned long i = 0; i < 512; ++i) {
#ifdef BLOCK_VERIFY
        unsigned char expected = (unsigned char)(i * 17 + 91);
#else
        unsigned char expected = (unsigned char)(i * 17 + 3);
#endif
        if (bytes[i] != expected)
            return 73;
    }
    if (memtrap(0x27000, 0xf100, 0, (unsigned long)bytes, 512) != -13 ||
        CALL(0x27003, 0, 7, 0) != -13)
        return 74;
    volatile unsigned char *edge = (volatile unsigned char *)0x0800ffffUL;
    *edge = 0x5a;
    if (CALL(0x27000, 1, bytes, 512) != -22 ||
        CALL(0x27000, ~0UL, bytes, 512) != -22 ||
        CALL(0x27000, 0, bytes, 511) != -22 ||
        CALL(0x27000, 0, ~0UL, 512) != -14 ||
        CALL(0x27000, 0, 0x0800ffffUL, 512) != -14 ||
        CALL(0x27000, 0, getauxval(3), 512) != -14 || *edge != 0x5a)
        return 75;
    if (!block_copy_boundary(0, bytes,
#ifdef BLOCK_READONLY
                             0
#else
                             1
#endif
                             ))
        return 86;
#ifdef BLOCK_READONLY
    if (CALL(0x27001, 0, bytes, 512) != -13 || CALL(0x27002, 0, 0, 0) != -13)
        return 76;
#else
    if (CALL(0x27001, 1, bytes, 512) != -22 ||
        CALL(0x27001, 0, bytes, 513) != -22 ||
        CALL(0x27001, 0, 0x0800ffffUL, 512) != -14 ||
        CALL(0x27001, 0, ~0UL, 512) != -14 || CALL(0x27002, 1, 0, 0) != -22)
        return 77;
#ifndef BLOCK_VERIFY
    for (unsigned long i = 0; i < 512; ++i)
        bytes[i] = (unsigned char)(i * 17 + 91);
    if (CALL(0x27001, 0, bytes, 512) != 512 || CALL(0x27002, 0, 0, 0) != 0)
        return 78;
#endif
#endif
#ifdef BLOCK_FAULT
    __asm__ __volatile__("ud2");
#else
    if (CALL(0x27004, 0, 0, 1) != -22 || CALL(0x27004, 0, 0, 0) != 0)
        return 79;
    for (unsigned long op = 0x27000; op <= 0x27004; ++op)
        if (CALL(op, 0, bytes, 512) != -9)
            return 80;
#endif
    return 0;
}
