/* SPDX-License-Identifier: BSD-2-Clause */
/* Opt-in native-memory v1; exact authority is enforced by Aether. */
#define _GNU_SOURCE
#include <errno.h>
#include <stdint.h>
#include <sys/auxv.h>
#include <sys/mman.h>

static long memory_call(unsigned long op, unsigned long a, unsigned long b, unsigned long c)
{
    unsigned long grant = getauxval(0xa000);
    register unsigned long fourth __asm__("r10") = c;
    register unsigned long fifth __asm__("r8") = 0;
    register unsigned long sixth __asm__("r9") = 0;
    long result = (long)op;
    __asm__ __volatile__("int $0x81"
        : "+a"(result), "+d"(b), "+r"(fifth)
        : "D"(grant), "S"(a), "r"(fourth), "r"(sixth)
        : "rcx", "memory", "cc");
    return result;
}
static long checked(long value)
{
    if (value < 0) { errno = (int)-value; return -1; }
    return value;
}
long native_memory_free_pages(void) { return memory_call(0x22000, 0, 0, 0); }
void *__mmap(void *hint, size_t bytes, int prot, int flags, int fd, off_t offset)
{
    if (hint || flags != (MAP_PRIVATE|MAP_ANONYMOUS) || fd != -1 || offset) {
        errno = ENOSYS;
        return MAP_FAILED;
    }
    return (void *)checked(memory_call(0x22001, bytes, (unsigned)prot, 0));
}
void *mmap(void *, size_t, int, int, int, off_t) __attribute__((alias("__mmap")));
int __mprotect(void *address, size_t bytes, int prot)
{
    uintptr_t a = (uintptr_t)address;
    if (!bytes || bytes > UINTPTR_MAX-a || a+bytes > UINTPTR_MAX-4095) {
        errno = EINVAL;
        return -1;
    }
    uintptr_t start = a & ~(uintptr_t)4095;
    size_t rounded = ((a+bytes+4095) & ~(uintptr_t)4095)-start;
    return (int)checked(memory_call(0x22002, start, rounded, (unsigned)prot));
}
int mprotect(void *, size_t, int) __attribute__((alias("__mprotect")));
int __munmap(void *address, size_t bytes)
{ return (int)checked(memory_call(0x22003, (uintptr_t)address, bytes, 0)); }
int munmap(void *, size_t) __attribute__((alias("__munmap")));
