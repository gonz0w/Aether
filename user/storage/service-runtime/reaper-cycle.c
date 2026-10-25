/* SPDX-License-Identifier: BSD-2-Clause */
/* Order actual detached exits; never alter the maintained reaper or its
 * records. Native status queries use the same owner's existing thread grant. */
#include "runtime.h"
#include "adapter.h"
#include <pthread.h>
#include <stdint.h>
#include <stdlib.h>
#include <sys/auxv.h>
#include <time.h>

extern volatile int __thread_list_lock;
extern _Noreturn void __real___unmapself(void *, size_t);
extern void __real___tl_lock(void);
static unsigned long grant;
static _Thread_local volatile unsigned cookie = 23;
static _Atomic unsigned ids[2], release_a, exiting_a;
#ifdef REAPER_CYCLE
static _Atomic unsigned entered_b;
#else
static _Atomic unsigned release_b;
#endif
static unsigned reaper_id;
static uint64_t deadline;
static unsigned roles[] = {0, 1};

static void verify(int valid, unsigned line)
{
    if (!valid)
        _Exit(1000 + line);
}
#define require(valid) verify((valid), __LINE__)
static uint64_t now(void)
{
    struct timespec ts;
    require(!clock_gettime(CLOCK_MONOTONIC, &ts) && ts.tv_sec >= 0 &&
            ts.tv_nsec >= 0 && ts.tv_nsec < 1000000000);
    return (uint64_t)ts.tv_sec * 1000000000 + ts.tv_nsec;
}
static void yield(void)
{
    require(now() < deadline);
    memtrap(0x1fffe, 0, 0, 0, 0);
}
static void publish(_Atomic unsigned *word)
{
    *word = 1;
    require(memtrap(0x2800c, grant, (uintptr_t)word, INT32_MAX, 0) >= 0);
}
static void await(_Atomic unsigned *word)
{
    while (!*word) {
        require(now() < deadline);
        long result = memtrap(0x28008, grant, (uintptr_t)word, 0, 0);
        require(!result || result == -11);
    }
}
struct observation {
    long status;
    unsigned long parked;
};
static struct observation observe(unsigned id)
{
    unsigned long op = 0x2800b, capability = grant, target = id, parked = 0;
    register unsigned long r10 __asm__("r10") = 0;
    register unsigned long r8 __asm__("r8") = 0, r9 __asm__("r9") = 0;
    /* Scalar read-only query. RDX reports this context's registered wait;
     * neither an ID nor this observation authorizes retirement or unmapping. */
    __asm__ volatile("int $0x81"
                     : "+a"(op), "+D"(capability), "+S"(target), "+d"(parked),
                       "+r"(r10), "+r"(r8), "+r"(r9)
                     :
                     : "rcx", "r11", "memory", "cc");
    return (struct observation){(long)op, parked};
}
static int lock_owner(unsigned id)
{
    /* Read the real aligned musl futex word; never mutate or release it. */
    return __atomic_load_n(&__thread_list_lock, __ATOMIC_SEQ_CST) == (int)id;
}
void __wrap___tl_lock(void)
{
#if defined(REAPER_CYCLE) && !defined(REAPER_FIXED)
    /* Order the original reaper's lock entry after B's real exit lock.
     * No record/lock mutation; the original lock still performs acquisition. */
    unsigned id = memtrap(0x28007, grant, 0, 0, 0);
    if (reaper_id && id == reaper_id && exiting_a) {
        require(observe(ids[0]).status == 1);
        while (!lock_owner(ids[1]))
            yield();
    }
#endif
    __real___tl_lock();
}
_Noreturn void __wrap___unmapself(void *base, size_t bytes)
{
    unsigned id = memtrap(0x28007, grant, 0, 0, 0);
    require(lock_owner(id));
    if (id == ids[0]) {
        publish(&exiting_a);
#ifdef REAPER_CYCLE
        /* Queue B on the held musl lock before publishing A to the reaper.
         * Wake clears the earlier callback wait, so a new park is its real
         * pthread-exit lock wait. A still calls the original exit body. */
        while (!observe(ids[1]).parked)
            yield();
        require(lock_owner(id));
#endif
    } else {
        require(id == ids[1]);
#ifdef REAPER_CYCLE
#ifdef REAPER_FIXED
        /* A must be retired while B still owns musl's lock, before B enters
         * the real exit body. Cleanup is observed, never supplied here. */
        while (observe(ids[0]).status != -9)
            yield();
        require(lock_owner(id));
#else
        /* B owns the real list lock. Wait only for the original reaper to
         * reach its lock acquisition after observing A's native stop. */
        for (;;) {
            struct observation a = observe(ids[0]), r = observe(reaper_id);
            require(a.status == 1);
            require(!a.parked);
            require(r.status == 0);
            if (r.parked)
                break;
            yield();
        }
#endif
        entered_b = 1;
#endif
    }
    /* This is the original sealed body, including pending/event publication
     * and its allow-exit wait. No ordering gate remains after this call. */
    __real___unmapself(base, bytes);
}
static void *worker(void *argument)
{
    unsigned role = *(unsigned *)argument;
    require(role < 2 && cookie == 23);
    cookie = 47;
    long id = memtrap(0x28007, grant, 0, 0, 0);
    require(id > 0 && id <= UINT32_MAX);
    ids[role] = id;
    if (!role)
        await(&release_a);
    else {
#ifdef REAPER_CYCLE
        await(&exiting_a);
#else
        await(&release_b);
#endif
    }
    return NULL;
}
#if defined(REAPER_CYCLE) && !defined(REAPER_FIXED)
static int cycle(void)
{
    struct observation a = observe(ids[0]), b = observe(ids[1]);
    struct observation r = observe(reaper_id);
    return entered_b && a.status == 1 && !a.parked && b.status == 0 &&
           b.parked == 1 && r.status == 0 && r.parked == 1 &&
           lock_owner(ids[1]) && aether_runtime_live() == 3 &&
           aether_runtime_admissions() == 3;
}
#endif
int main(void)
{
    require(cookie == 23 && !aether_runtime_init());
    grant = getauxval(0xa001);
    require(grant);
    unsigned long op = 0x22000, memory = getauxval(0xa000), total = 0;
    register unsigned long r10 __asm__("r10") = 0;
    register unsigned long r8 __asm__("r8") = 0, r9 __asm__("r9") = 0;
    __asm__ volatile("int $0x81"
                     : "+a"(op), "+d"(total), "+r"(r10), "+r"(r8), "+r"(r9)
                     : "D"(memory), "S"(0UL)
                     : "rcx", "r11", "memory", "cc");
    require((long)op >= 0 && (r8 == 128 || r8 == 8192));
    if (r8 == 128) {
        require(!aether_runtime_finish() && !aether_runtime_live());
        return 0;
    }
    deadline = now() + 2000000000ULL;
    pthread_attr_t attr;
    pthread_t children[2];
    require(!pthread_attr_init(&attr) &&
            !pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_DETACHED) &&
            !pthread_attr_setstacksize(&attr, 262144) &&
            !pthread_attr_setguardsize(&attr, 4096));
    unsigned rounds = 1;
#if defined(REAPER_FIXED) && defined(REAPER_CYCLE)
    rounds = 8;
#endif
    for (unsigned round = 0; round < rounds; ++round) {
        ids[0] = ids[1] = release_a = exiting_a = 0;
#ifdef REAPER_CYCLE
        entered_b = 0;
#else
        release_b = 0;
#endif
        for (unsigned i = 0; i < 2; ++i)
            require(!pthread_create(&children[i], &attr, worker, &roles[i]));
        while (!ids[0] || !ids[1])
            yield();
        /* Private IDs follow admission order with stride8. Only the first
         * pair identifies the charged reaper; later pairs reuse records. */
        require(ids[0] > 8 && ids[1] == ids[0] + 8);
        if (!reaper_id)
            reaper_id = ids[0] - 8;
        require(observe(reaper_id).status == 0);
        publish(&release_a);
#if defined(REAPER_CYCLE) && !defined(REAPER_FIXED)
        while (!cycle())
            yield();
        struct timespec pause = {0, 1000000};
        require(!nanosleep(&pause, NULL) && cycle());
        _Exit(870); /* Exact blocked cycle; never certify clean retirement. */
#else
#ifndef REAPER_CYCLE
        while (observe(ids[0]).status != -9)
            yield();
        publish(&release_b);
#endif
        while (aether_runtime_live() != 1)
            yield();
        require(observe(ids[0]).status == -9 && observe(ids[1]).status == -9);
#ifdef REAPER_CYCLE
        require(entered_b);
#endif
        require(aether_runtime_admissions() == 1 + 2 * (round + 1));
#endif
    }
    require(!pthread_attr_destroy(&attr));
    require(!aether_runtime_finish() && !aether_runtime_live());
    return 0;
}
