/* SPDX-License-Identifier: BSD-2-Clause */
/* Private musl-layout witness; not a public fork implementation. */
#include "pthread_impl.h"
#include "../native-memory/adapter.h"

int copy_rebind(unsigned long memory, unsigned long reader,
                unsigned long writer, unsigned long *input,
                unsigned long *output)
{
    pthread_t self = __pthread_self();
    long pid = memtrap(0x10027, 0, 0, 0, 0);
    long parent = memtrap(0x1006e, 0, 0, 0, 0);
    if (pid <= 0 || parent <= 0 || pid == parent || self->tid != parent ||
        libc.threaded || libc.threads_minus_1 || libc.need_locks ||
        __thread_list_lock || self->next != self || self->prev != self)
        return 0;
    size_t *slots[3] = {0};
    unsigned ended = 0;
    /* This loader supplies at most 15 pairs and a terminator. */
    for (unsigned i = 0; i < 16; ++i) {
        size_t *pair = libc.auxv + 2 * i;
        if (!pair[0]) {
            ended = 1;
            break;
        }
        if (pair[0] >= 0xa000 && pair[0] <= 0xa002) {
            unsigned at = pair[0] - 0xa000;
            if (slots[at])
                return 0;
            slots[at] = pair + 1;
        }
    }
    if (!ended || !slots[0] || !slots[1] || !slots[2] || *slots[1] != *input ||
        *slots[2] != *output || memory == *slots[0] || reader == writer ||
        memtrap(0x22000, memory, 0, 0, 0) < 0 ||
        memtrap(0x24001, reader, 0, 0, 0) || memtrap(0x24002, writer, 0, 0, 0))
        return 0;
#ifndef REBIND_LIBC_REPAIR
    long tid = memtrap(0x100da, (uintptr_t)&__thread_list_lock, 0, 0, 0);
    if (tid < 0)
        return 0;
    if (tid != pid)
        __builtin_trap();
#endif
#ifndef REBIND_SKIP_AUX
    *slots[0] = memory;
    *slots[1] = reader;
    *slots[2] = writer;
#endif
#if !defined(REBIND_SKIP_TID) && !defined(REBIND_LIBC_REPAIR)
    self->tid = (int)tid;
#endif
#ifndef REBIND_SKIP_CHANNEL
    *input = reader;
    *output = writer;
#endif
    return 1;
}
