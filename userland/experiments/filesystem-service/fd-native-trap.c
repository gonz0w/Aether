/* SPDX-License-Identifier: BSD-2-Clause */
#include "fd-native.h"
#include "native-trap-vendor.h"
_Static_assert(sizeof(unsigned long) == 8 && sizeof(void *) == 8,
               "native x86-64 ABI required");
int64_t aefd_native_trap(void *context, uint64_t op, uint64_t cap, uint64_t a,
                         uint64_t b, uint64_t c)
{
    (void)context;
    return memtrap(op, cap, a, b, c);
}
