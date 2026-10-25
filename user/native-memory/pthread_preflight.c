/* SPDX-License-Identifier: BSD-2-Clause */
/* Actual pthread_create failure-path witness; no successful thread claim. */
#include "adapter.h"
#include <sys/auxv.h>
#include <unistd.h>
#include "pthread_impl.h"

static volatile unsigned ran, queries;
static _Thread_local volatile unsigned tls_sentinel = 37;
static void *child(void *arg)
{
    ran = 1;
    return arg;
}
long aether_wait_syscall(long n, long how, long input, long output, long bytes,
                         long extra, long tail)
{
    if (n != SYS_rt_sigprocmask || how != SIG_SETMASK || input || bytes != 8 ||
        extra || tail)
        return -ENOSYS;
    ++queries;
    return memtrap(0x10000 + SYS_rt_sigprocmask, how, input, output, bytes);
}
#define CHECK(x, n)                                                            \
    do {                                                                       \
        if (!(x))                                                              \
            return (n);                                                        \
    } while (0)
int main(int argc, char **argv)
{
    CHECK(argc == 2 && argv && !ran && !queries && libc.can_do_threads, 180);
    unsigned long cap = getauxval(0xa001), memory = getauxval(0xa000),
                  mask = 0x1234;
    CHECK(cap && memory, 182);
    CHECK(memtrap(0x10000 + SYS_rt_sigprocmask, SIG_SETMASK, 0,
                  (unsigned long)&mask, 8) == -ENOSYS &&
              mask == 0x1234,
          183);
    long quota = memtrap(0x22000, memory, 0, 0, 0);
    pthread_t self = pthread_self(), next = self->next, prev = self->prev;
    int threaded = libc.threaded, locks = libc.need_locks,
        count = libc.threads_minus_1;
    CHECK(!threaded && !locks && !count, 184);
    errno = 71;
    for (unsigned i = 0; i < 2; ++i) {
        pthread_t result = (pthread_t)0x1234;
        CHECK(pthread_create(&result, 0, child, (void *)37) == ENOSYS, 181);
        CHECK(result == (pthread_t)0x1234 && errno == 71 && queries == i + 1 &&
                  !ran && tls_sentinel == 37,
              185);
        CHECK(libc.threaded == threaded && libc.need_locks == locks &&
                  libc.threads_minus_1 == count && self->next == next &&
                  self->prev == prev,
              186);
        CHECK(memtrap(0x22000, memory, 0, 0, 0) == quota &&
                  memtrap(0x28002, cap, 0, 0, 0) == -2,
              187);
    }
    for (unsigned i = 0; i < 64; ++i)
        memtrap(0x1fffe, 0, 0, 0, 0);
    CHECK(!ran, 188);
    CHECK(write(1, "AETHER MUSL NATIVE PASS\n", 24) == 16, 189);
    CHECK(write(1, &"AETHER MUSL NATIVE PASS\n"[16], 8) == 8, 190);
    return 0;
}

/* Retained strict-libc I/O hook: existing startup FD1 transport. */
long __aether_io(unsigned long op, unsigned long a, unsigned long b,
                 unsigned long c)
{
    return memtrap(0x10000 + op, a, b, c, 0);
}
