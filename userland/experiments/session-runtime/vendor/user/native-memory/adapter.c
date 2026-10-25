/* SPDX-License-Identifier: BSD-2-Clause */
#include "adapter.h"
#include <sys/auxv.h>
#include <sys/mman.h>
#include <errno.h>
#include <stdint.h>
static long checked(long value) { if (value < 0) { errno = (int)-value; return -1; } return value; }
void *__mmap(void *hint, size_t length, int prot, int flags, int fd, off_t offset)
{
    if (hint || flags != (MAP_PRIVATE | MAP_ANONYMOUS) || fd != -1 || offset) {
        errno = ENOSYS; return MAP_FAILED;
    }
    return (void *)checked(memtrap(0x22001, getauxval(0xa000), length, (unsigned)prot, 0));
}
void *mmap(void *, size_t, int, int, int, off_t) __attribute__((alias("__mmap")));
int __mprotect(void *address, size_t length, int prot)
{
    uintptr_t a = (uintptr_t)address;
    if (!length || length > UINTPTR_MAX - a || a + length > UINTPTR_MAX - 4095) {
        errno = EINVAL; return -1;
    }
    uintptr_t start = a & ~(uintptr_t)4095;
    size_t bytes = ((a + length + 4095) & ~(uintptr_t)4095) - start;
    return (int)checked(memtrap(0x22002, getauxval(0xa000), start, bytes, (unsigned)prot));
}
int mprotect(void *, size_t, int) __attribute__((alias("__mprotect")));
int __munmap(void *address, size_t length)
{ return (int)checked(memtrap(0x22003, getauxval(0xa000), (uintptr_t)address, length, 0)); }
int munmap(void *, size_t) __attribute__((alias("__munmap")));
/* The retained strict-libc fixture has an I/O interception hook. This test
   uses the existing startup FD1 transport; it does not implement descriptors. */
long __aether_io(unsigned long op, unsigned long a, unsigned long b, unsigned long c)
{ return memtrap(0x10000 + op, a, b, c, 0); }
