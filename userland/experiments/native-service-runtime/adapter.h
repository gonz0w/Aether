/* SPDX-License-Identifier: BSD-2-Clause */
/* Private native service trap; x86-64 only. */
#include <stddef.h>
#include <stdint.h>
static inline long memtrap(unsigned long op, unsigned long cap, unsigned long a,
                           unsigned long b, unsigned long c)
{
    register unsigned long r10 __asm__("r10") = c;
    register unsigned long r8 __asm__("r8") = 0, r9 __asm__("r9") = 0;
    __asm__ __volatile__("int $0x81"
                         : "+a"(op), "+D"(cap), "+S"(a), "+d"(b), "+r"(r10),
                           "+r"(r8), "+r"(r9)
                         :
                         : "rcx", "r11", "memory", "cc");
    return (long)op;
}
