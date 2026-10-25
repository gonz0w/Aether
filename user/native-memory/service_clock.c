/* SPDX-License-Identifier: BSD-2-Clause */
/* Private full-owner wait witness: bare stack/FS cookie, not a musl TCB. */
#include "adapter.h"
#include <stdatomic.h>
#include <sys/auxv.h>
#include <sys/mman.h>
#include <unistd.h>

#define CHECK(c, n)                                                            \
    do {                                                                       \
        if (!(c))                                                              \
            return n;                                                          \
    } while (0)
struct storage {
    unsigned version, size;
    unsigned long entry, stack, bytes, rsp, fs, clear_tid, argument;
    unsigned long tls, tls_bytes, parent_tid, reserved;
};
_Static_assert(sizeof(struct storage) == 96, "native storage descriptor");
static struct worker_data {
    unsigned long cap, fs, deadline, end;
    unsigned spare;
    _Atomic unsigned error;
} args[83];
static unsigned parent_tid[83];
static unsigned long ids[83];
static void *stacks[83], *tls[83];
static _Atomic unsigned begin;
static _Thread_local volatile unsigned tls_marker = 17;
static _Atomic(volatile unsigned *) source;
static volatile unsigned *destination;

static long observe(unsigned long cap)
{
    return memtrap(0x2800f, cap, 0, 0, 0);
}
static long waiting(unsigned long cap, unsigned long id, unsigned long *parked)
{
    unsigned long op = 0x2800b, aux = 0;
    register unsigned long r10 __asm__("r10") = 0;
    register unsigned long r8 __asm__("r8") = 0, r9 __asm__("r9") = 0;
    __asm__ __volatile__("int $0x81"
                         : "+a"(op), "+D"(cap), "+d"(aux), "+r"(r10), "+r"(r8),
                           "+r"(r9)
                         : "S"(id)
                         : "rcx", "r11", "memory");
    *parked = aux;
    return (long)op;
}
static _Noreturn __attribute__((no_stack_protector)) void
worker(unsigned long arg)
{
    struct worker_data *a = (void *)arg;
    unsigned long cookie;
    __asm__ __volatile__("movq %%fs:0,%0" : "=r"(cookie) : : "memory");
    if (cookie != a->fs)
        a->error = 389;
    while (!atomic_load_explicit(&begin, memory_order_acquire))
        if (memtrap(0x28008, a->cap, (uintptr_t)&begin, 0, 0) < 0)
            a->error = 390;
    long result = memtrap(0x28010, a->cap, (uintptr_t)source, 0, a->deadline);
    long end = observe(a->cap);
    a->end = end < 0 ? 0 : (unsigned long)end;
    if (a->spare) {
#if MODE == 1
        if (result != -11)
#else
        if (result != -110)
#endif
            a->error = 391;
    } else {
#if MODE == 1
        if (result != 0 || end < 0 || (unsigned long)end >= a->deadline)
            a->error = 391;
#else
        if (result != -110 || end < 0 || (unsigned long)end < a->deadline ||
            (unsigned long)end - a->deadline > 1000000000UL)
            a->error = 391;
#endif
    }
    memtrap(0x28001, a->cap, 0, 0, 0);
    __builtin_trap();
}
static long create(unsigned i, size_t bytes, unsigned long cap)
{
    struct storage d = {1,
                        96,
                        (uintptr_t)worker,
                        (uintptr_t)stacks[i],
                        bytes,
                        (uintptr_t)stacks[i] + bytes - 8,
                        (uintptr_t)tls[i],
                        (uintptr_t)tls[i] + 16,
                        (uintptr_t)&args[i],
                        (uintptr_t)tls[i],
                        4096,
                        (uintptr_t)&parent_tid[i],
                        0};
    return memtrap(0x28006, cap, (uintptr_t)&d, 0, 0);
}
#if MODE == 2
static long move(unsigned long cap, unsigned count)
{
    unsigned long op = 0x2800d;
    register unsigned long r10 __asm__("r10") = count;
    register unsigned long r8 __asm__("r8") = (uintptr_t)destination;
    register unsigned long r9 __asm__("r9") = 0;
    __asm__ __volatile__("int $0x81"
                         : "+a"(op), "+r"(r10), "+r"(r8), "+r"(r9)
                         : "D"(cap), "S"((uintptr_t)source), "d"(0UL)
                         : "rcx", "r11", "memory");
    return (long)op;
}
#endif
int main(int argc, char **argv)
{
    CHECK(argc == 2 && argv, 380);
    unsigned instance = argv[0][11] - '0';
    CHECK((instance == 1 || instance == 2) && tls_marker == 17, 380);
    tls_marker = instance;
    unsigned count = instance == 1 ? 82 : 2;
    size_t bytes = count == 82 ? 256UL * 1024 : 4096;
    unsigned extra = 0;
    unsigned long cap = getauxval(0xa001), memory = getauxval(0xa000);
    CHECK(cap && memory && observe(cap) >= 0, 381);
    CHECK(observe(cap ^ 3) == -13, 381);
    long before = memtrap(0x22000, memory, 0, 0, 0);
    CHECK(before > 0, 382);
    source = mmap(0, 4096, 3, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    destination = mmap(0, 4096, 3, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    CHECK((void *)source != MAP_FAILED && (void *)destination != MAP_FAILED,
          382);
    for (unsigned i = 0; i <= count; ++i) {
        stacks[i] = mmap(0, bytes, 3, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        tls[i] = mmap(0, 4096, 3, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        CHECK(stacks[i] != MAP_FAILED && tls[i] != MAP_FAILED, 382);
        *(uintptr_t *)tls[i] = (uintptr_t)tls[i];
        args[i].cap = cap;
        args[i].fs = (uintptr_t)tls[i];
    }
    for (unsigned i = 0; i < count; ++i) {
        long id = create(i, bytes, cap);
        CHECK(id > 0 && parent_tid[i] == (unsigned long)id, 383);
        ids[i] = id;
        CHECK(ids[i] == (count == 82 ? 3UL : 4UL) + 8UL * i, 383);
    }
    long full = memtrap(0x22000, memory, 0, 0, 0);
    CHECK(create(count, bytes, cap) == -28 && parent_tid[count] == 0 &&
              memtrap(0x22000, memory, 0, 0, 0) == full,
          384);
    // All workers must first be parked before publishing a shared deadline.
    for (unsigned i = 0; i < count; ++i) {
        unsigned long parked = 0;
        for (unsigned tries = 0; tries < 1000000 && !parked; ++tries) {
            CHECK(waiting(cap, ids[i], &parked) == 0, 385);
            if (!parked) {
                memtrap(0x1fffe, 0, 0, 0, 0);
                ++extra;
            }
        }
        CHECK(parked == 1, 385);
    }
    long start = observe(cap);
    CHECK(start >= 0 &&
              (unsigned long)start <= 0x7fffffffffffffffUL - 900000000UL,
          386);
    unsigned long deadline = (unsigned long)start + 900000000UL;
    for (unsigned i = 0; i < count; ++i)
        args[i].deadline = deadline;
    atomic_store_explicit(&begin, 1, memory_order_release);
    CHECK(memtrap(0x2800c, cap, (uintptr_t)&begin, count, 0) == count, 387);
    for (unsigned i = 0; i < count; ++i) {
        unsigned long parked = 0;
        for (unsigned tries = 0; tries < 1000000 && !parked; ++tries) {
            CHECK(waiting(cap, ids[i], &parked) == 0, 388);
            if (!parked) {
                memtrap(0x1fffe, 0, 0, 0, 0);
                ++extra;
            }
        }
        CHECK(parked == 1, 388);
        CHECK(memtrap(0x2800a, cap, ids[i], 0, 0) == -16, 388);
        CHECK(memtrap(0x22003, memory, (uintptr_t)stacks[i], bytes, 0) == -13,
              388);
    }
    CHECK(memtrap(0x22002, memory, (uintptr_t)source, 4096, 0) == -13 &&
              memtrap(0x22003, memory, (uintptr_t)source, 4096, 0) == -13,
          392);
#ifdef STOP_WORKERS
    if (count == 82 && memtrap(0x20005, 0, 0, 0, 0) == 1) {
        CHECK(memtrap(0x20004, 0, 0, 0, 0) == 0, 393);
        for (;;) {
            memtrap(0x1fffe, 0, 0, 0, 0);
        }
    }
#endif
#if MODE == 1
    unsigned first = count / 2;
    CHECK(memtrap(0x2800c, cap, (uintptr_t)source, first, 0) == first, 394);
    CHECK(memtrap(0x22003, memory, (uintptr_t)source, 4096, 0) == -13, 392);
    CHECK(memtrap(0x2800c, cap, (uintptr_t)source, count, 0) == count - first,
          394);
#elif MODE == 2
    CHECK(move(cap, count) == count, 395);
    CHECK(memtrap(0x22003, memory, (uintptr_t)destination, 4096, 0) == -13 &&
              memtrap(0x22002, memory, (uintptr_t)destination, 4096, 0) == -13,
          392);
    CHECK(memtrap(0x22003, memory, (uintptr_t)source, 4096, 0) == 0, 395);
    void *old_source = (void *)source;
    source = mmap(0, 4096, 3, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    CHECK((void *)source == old_source && *source == 0, 395);
#endif
    // Wait for confirmed exit, then retire exact IDs before releasing backing.
    for (unsigned i = 0; i < count; ++i) {
        unsigned long parked;
        long done = 0;
        for (unsigned tries = 0; tries < 1000000 && !done; ++tries) {
            done = waiting(cap, ids[i], &parked);
            CHECK(done >= 0, 396);
            if (!done) {
                memtrap(0x1fffe, 0, 0, 0, 0);
                ++extra;
            }
        }
        CHECK(done == 1 && *(unsigned *)((uintptr_t)tls[i] + 16) == 0, 396);
        CHECK(args[i].error == 0, args[i].error);
        CHECK(memtrap(0x2800a, cap, ids[i], 0, 0) == 0, 397);
    }
    // Full-slot denial must not consume an ordinal. New worker sees begin=1
    // and an expired deadline, and must leave no retained wait registration.
    args[count].spare = 1;
    args[count].deadline = 0;
#if MODE == 1
    // A compare-and-park mismatch completes as EAGAIN without registration.
    args[count].deadline = observe(cap) + 100000000;
    if (source)
        *source = 1;
#endif
    long next = create(count, bytes, cap);
    CHECK(next == (long)(ids[0] + 8UL * count), 398);
    unsigned long parked;
    long done = 0;
    for (unsigned tries = 0; tries < 1000000 && !done; ++tries) {
        done = waiting(cap, next, &parked);
        CHECK(done >= 0, 398);
        if (!done) {
            memtrap(0x1fffe, 0, 0, 0, 0);
            ++extra;
        }
    }
    CHECK(done == 1 && args[count].error == 0 &&
              *(unsigned *)((uintptr_t)tls[count] + 16) == 0 &&
              memtrap(0x2800a, cap, next, 0, 0) == 0,
          398);
    for (unsigned i = 0; i <= count; ++i)
        CHECK(munmap(stacks[i], bytes) == 0 && munmap(tls[i], 4096) == 0, 399);
    if (source)
        CHECK(munmap((void *)source, 4096) == 0, 399);
    CHECK(munmap((void *)destination, 4096) == 0 &&
              memtrap(0x22000, memory, 0, 0, 0) == before,
          399);
    // Preserve the borrowed supervisor's four-byte yield-count contract.
    CHECK(extra <= 2000000, 400);
    CHECK(write(1, &extra, 4) == 4, 400);
    for (unsigned i = 0; i < 64; ++i)
        memtrap(0x1fffe, 0, 0, 0, 0);
    return 0;
}
