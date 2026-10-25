/* SPDX-License-Identifier: BSD-2-Clause */
#include "entropy.h"
#include <errno.h>
#include <stdint.h>

static long request(unsigned operation, unsigned long grant, void *buffer,
                    size_t count)
{
    register unsigned long a __asm__("rax") = operation;
    register unsigned long d __asm__("rdi") = grant;
    register unsigned long s __asm__("rsi") = (uintptr_t)buffer;
    register unsigned long n __asm__("rdx") = count;
    register unsigned long extra __asm__("r10") = 0;
    register unsigned long r8 __asm__("r8") = 0;
    register unsigned long r9 __asm__("r9") = 0;
    __asm__ volatile("int $0x81"
                     : "+a"(a), "+D"(d), "+S"(s), "+d"(n), "+r"(extra),
                       "+r"(r8), "+r"(r9)
                     :
                     : "memory", "cc", "rcx", "r11");
    return (long)a;
}

static int known_error(long result)
{
    return result == -ENOSYS || result == -EACCES || result == -EBADF ||
           result == -EINVAL || result == -EFAULT || result == -ENOSPC;
}

long aether_entropy_draw(unsigned long grant, void *buffer, size_t count)
{
    long result = request(0x2b000, grant, buffer, count);
    if (count >= 1 && count <= 256 && result == (long)count)
        return result;
    return known_error(result) ? result : -EIO;
}

long aether_entropy_close(unsigned long grant)
{
    long result = request(0x2b001, grant, 0, 0);
    return result == 0 || known_error(result) ? result : -EIO;
}
