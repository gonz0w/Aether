/* SPDX-License-Identifier: BSD-2-Clause */
/* Included only by the native conformance adapter's LIFE_TASKQ mode. */
#include "bridge.h"
static taskq_t *queue_a, *queue_b;
static _Atomic unsigned parent_waiting, b_queued, a_done, b_done, tail_done;
static unsigned parent_yields;
static struct task_start {
    void (*function)(void *);
    void *argument;
} task_starts[2];

_Noreturn void aether_taskq_fail(unsigned code)
{
    memtrap(0x10000 + 231, code, 0, 0, 0);
    __builtin_trap();
}
#define TC(x, code)                                                            \
    do {                                                                       \
        if (!(x))                                                              \
            aether_taskq_fail(code);                                           \
    } while (0)
void aether_taskq_require_parent(void)
{
    TC(parent_id && memtrap(0x28007, thread_cap, 0, 0, 0) == parent_id, 308);
}
static void task_yield(void)
{
    if ((unsigned)memtrap(0x28007, thread_cap, 0, 0, 0) == parent_id)
        ++parent_yields;
    memtrap(0x1fffe, 0, 0, 0, 0);
}
void *aether_taskq_map_arena(void)
{
    aether_taskq_require_parent();
    long p = memtrap(0x22001, memory_cap, 4096, 3, 0);
    TC(p > 0, 306);
    return (void *)p;
}
void aether_taskq_unmap_arena(void *p)
{
    aether_taskq_require_parent();
    TC(memtrap(0x22003, memory_cap, (unsigned long)p, 4096, 0) == 0, 306);
}
static void *task_start(void *arg)
{
    struct task_start *s = arg;
    s->function(s->argument);
    aether_taskq_fail(309); /* Upstream taskq_thread must call pthread_exit. */
}
kthread_t *aether_taskq_start(const char *name, void (*fn)(void *), void *arg)
{
    aether_taskq_require_parent();
    TC(name && fn && used < 2 && admissions < 4, 310);
    unsigned i = startups[0].thread ? 1 : 0;
    task_starts[i] = (struct task_start){fn, arg};
    pthread_attr_t attr;
    pthread_t td;
    TC(pthread_attr_init(&attr) == 0 &&
           pthread_attr_setstacksize(&attr, 128 * 1024) == 0 &&
           pthread_attr_setguardsize(&attr, 4096) == 0 &&
           pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_DETACHED) == 0 &&
           pthread_create(&td, &attr, task_start, &task_starts[i]) == 0 &&
           pthread_attr_destroy(&attr) == 0,
       310);
    return (kthread_t *)td;
}
void aether_taskq_reap_all(void)
{
    aether_taskq_require_parent();
    for (unsigned spin = 0; used && spin < 64; ++spin) {
        for (unsigned i = 0; i < 2; ++i) {
            struct startup *s = &startups[i];
            if (s->thread && s->pending && !s->allow_exit) {
                TC(memtrap(0x2800b, thread_cap, s->id, 0, 0) == 0, 311);
#ifdef TASKQ_EARLY_REAP
                TC(memtrap(0x22003, memory_cap, s->map_base, s->map_bytes, 0) ==
                       0,
                   312);
#endif
                TC(reap_detached(i) == 0 &&
                       memtrap(0x22003, memory_cap, s->map_base, s->map_bytes,
                               0) == -13,
                   312);
                s->allow_exit = 1;
            }
            TC(reap_detached(i) >= 0, 313);
        }
        if (used)
            task_yield();
    }
    TC(!used && !libc.threads_minus_1 && !__thread_list_lock &&
           pthread_self()->next == pthread_self() &&
           pthread_self()->prev == pthread_self(),
       314);
}
void aether_taskq_before_wait(kcondvar_t *c)
{
    if ((unsigned)memtrap(0x28007, thread_cap, 0, 0, 0) == parent_id &&
        queue_a && c == &queue_a->tq_wait_cv)
        parent_waiting = 1;
}
static void tail(void *arg)
{
    TC(!arg && taskq_of_curthread() == queue_a && a_done && b_done, 315);
    ++tail_done;
}
static void work_b(void *arg)
{
    TC(!arg && taskq_of_curthread() == queue_b && cookie == 17, 316);
    cookie = 42;
    for (unsigned spin = 0; !parent_waiting && spin < 128; ++spin)
        task_yield();
    TC(parent_waiting, 317);
    b_done = 1;
}
static void work_a(void *arg)
{
    TC(!arg && taskq_of_curthread() == queue_a && cookie == 17, 318);
    cookie = 41;
    TC(aether_taskq_dispatch(queue_b, work_b, NULL, TQ_NOSLEEP) == 1, 319);
    TC(aether_taskq_dispatch(queue_b, work_b, NULL, TQ_NOSLEEP) == 0 &&
           queue_b->tq_nalloc == 1,
       320);
    b_queued = 1;
    taskq_wait_id(queue_b, 1);
    TC(b_done && !tail_done && cookie == 41, 321);
    a_done = 1;
}
int main(int argc, char **argv)
{
    TC(argc == 2 && argv && cookie == 17, 180);
    thread_cap = getauxval(0xa001);
    memory_cap = getauxval(0xa000);
    parent_id = memtrap(0x28007, thread_cap, 0, 0, 0);
    TC(thread_cap && memory_cap && parent_id, 181);
    long quota = memtrap(0x22000, memory_cap, 0, 0, 0);
    aether_taskq_begin();
    for (unsigned cycle = 0; cycle < 2; ++cycle) {
        parent_waiting = b_queued = a_done = b_done = tail_done = 0;
        queue_a = aether_taskq_create("fixture_a", 2);
        queue_b = aether_taskq_create("fixture_b", 1);
        TC(queue_a && queue_b && !taskq_of_curthread() && used == 2, 322);
        long before = memtrap(0x22000, memory_cap, 0, 0, 0);
        pthread_t denied = (pthread_t)0x1234;
        TC(pthread_create(&denied, NULL, task_start, NULL) == EAGAIN &&
               denied == (pthread_t)0x1234 &&
               aether_taskq_create("third", 1) == NULL &&
               memtrap(0x22000, memory_cap, 0, 0, 0) == before,
           323);
        /* Four queue/list objects occupy four slots before entry allocation. */
        void *held[4];
        for (unsigned i = 0; i < 4; ++i) {
            held[i] = aether_taskq_alloc(512, KM_NOSLEEP);
            TC(held[i] != NULL, 335);
        }
        TC(aether_taskq_alloc(512, KM_NOSLEEP) == NULL, 335);
        for (unsigned i = 0; i < 4; ++i)
            aether_taskq_free(held[i], 512);
#ifdef TASKQ_INVALID_FREE
        aether_taskq_free((char *)queue_a + 1, sizeof(*queue_a));
#endif
#ifdef TASKQ_ALLOC_FAIL
        for (unsigned i = 0; i < 9; ++i)
            (void)aether_taskq_alloc(512, KM_SLEEP);
        aether_taskq_fail(324);
#endif
        TC(aether_taskq_dispatch(queue_a, work_a, NULL, TQ_NOSLEEP) == 1, 325);
        for (unsigned spin = 0; !b_queued && spin < 64; ++spin)
            task_yield();
        TC(b_queued && !a_done && !b_done, 326);
        TC(aether_taskq_dispatch(queue_a, tail, NULL, TQ_NOSLEEP) == 1 &&
               aether_taskq_dispatch(queue_a, tail, NULL, TQ_NOSLEEP) == 0 &&
               queue_a->tq_nalloc == 2 && !tail_done,
           327);
#ifndef TASKQ_PREMATURE_DRAIN
        taskq_wait_id(queue_a, 1);
#endif
        TC(parent_waiting && a_done && b_done && tail_done == 1, 328);
        taskqid_t delayed =
            taskq_dispatch_delay(queue_a, tail, NULL, TQ_NOSLEEP, 1);
#ifdef TASKQ_FALSE_DELAY
        delayed = 1;
#endif
        TC(delayed == 0 && tail_done == 1 &&
               taskq_cancel_id(queue_a, 1, 0) == ENOENT,
           329);
        TC(aether_taskq_dispatch(queue_a, tail, NULL, TQ_NOSLEEP) == 1, 330);
        taskq_wait(queue_a);
        taskq_wait(queue_b);
        TC(tail_done == 2, 331);
        aether_taskq_destroy(queue_a);
        aether_taskq_destroy(queue_b);
        queue_a = queue_b = NULL;
        aether_taskq_reap_all();
        TC(admissions == (cycle + 1) * 2 && cookie == 17, 332);
    }
    aether_taskq_end();
    TC(memtrap(0x22000, memory_cap, 0, 0, 0) == quota && admissions == 4, 333);
    TC(parent_yields <= 64, 334);
    while (parent_yields < 64)
        task_yield();
    TC(write(1, "AETHER MUSL NATIVE PASS\n", 24) == 16 &&
           write(1, &"AETHER MUSL NATIVE PASS\n"[16], 8) == 8,
       220);
    return 0;
}
#undef TC
