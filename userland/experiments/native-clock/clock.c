/* SPDX-License-Identifier: BSD-2-Clause */
#include "clock.h"
#include <errno.h>

static long request(unsigned operation, unsigned long grant,
                    unsigned long address, unsigned long expected,
                    unsigned long deadline)
{
    register unsigned long a __asm__("rax") = operation;
    register unsigned long extra __asm__("r10") = deadline;
    register unsigned long r8 __asm__("r8") = 0;
    register unsigned long r9 __asm__("r9") = 0;
    __asm__ volatile("int $0x81"
                     : "+a"(a), "+D"(grant), "+S"(address), "+d"(expected),
                       "+r"(extra), "+r"(r8), "+r"(r9)
                     :
                     : "memory", "cc", "rcx", "r11");
    return (long)a;
}

static int known_error(long result)
{
    return result == -EACCES || result == -ENOSYS || result == -EINVAL ||
           result == -EFAULT || result == -EAGAIN || result == -ETIMEDOUT ||
           result == -EIO || result == -EOVERFLOW;
}

long aether_clock_observe(unsigned long grant)
{
    long result = request(0x2800f, grant, 0, 0, 0);
    return result >= 0 || known_error(result) ? result : -EIO;
}

long aether_clock_park(unsigned long grant, volatile uint32_t *word,
                       unsigned long expected, unsigned long deadline_ns)
{
    long result =
        request(0x28010, grant, (uintptr_t)word, expected, deadline_ns);
    return result == 0 || known_error(result) ? result : -EIO;
}

long aether_clock_sleep_until(unsigned long grant, unsigned long deadline_ns)
{
    volatile uint32_t word = 0;
    long result = aether_clock_park(grant, &word, 0, deadline_ns);
    if (result != -ETIMEDOUT)
        return result == 0 ? -EIO : result;
    long now = aether_clock_observe(grant);
    if (now < 0)
        return now;
    return (unsigned long)now >= deadline_ns ? 0 : -EIO;
}
