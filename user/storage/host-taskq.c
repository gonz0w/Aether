/* SPDX-License-Identifier: BSD-2-Clause */
/* Linux-only actual libzpool taskq witness; no native kernel/service ABI. */
#include <sys/zfs_context.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

extern int taskq_now;
void __real_cv_wait(kcondvar_t *, kmutex_t *);
void __wrap_cv_wait(kcondvar_t *, kmutex_t *);
void __real_taskq_wait_id(taskq_t *, taskqid_t);
void __wrap_taskq_wait_id(taskq_t *, taskqid_t);
taskqid_t __real_taskq_dispatch_delay(taskq_t *, task_func_t, void *, uint_t,
                                      clock_t);
taskqid_t __wrap_taskq_dispatch_delay(taskq_t *, task_func_t, void *, uint_t,
                                      clock_t);

static taskq_t *a, *b;
static _Atomic(kcondvar_t *) watched;
static _Atomic unsigned wait_seen, drain_done, b_entered, b_release, b_done;
static _Atomic unsigned tail_entered, tail_release, tail_done, a_done;
static _Atomic unsigned unexpected, reused;

static void require(int ok, const char *reason)
{
    if (!ok) {
        fprintf(stderr, "TASKQ FAIL: %s\n", reason);
        exit(2);
    }
}
static double now(void)
{
    struct timespec t;
    require(clock_gettime(CLOCK_MONOTONIC, &t) == 0, "monotonic clock");
    return (double)t.tv_sec + (double)t.tv_nsec / 1000000000.0;
}
static void await(_Atomic unsigned *flag)
{
    double limit = now() + 5.0;
    while (!atomic_load(flag)) {
        require(now() < limit, "gate deadline");
        struct timespec pause = {0, 1000000};
        nanosleep(&pause, NULL);
    }
}
void __wrap_cv_wait(kcondvar_t *cv, kmutex_t *mutex)
{
    if (cv == atomic_load(&watched))
        atomic_store(&wait_seen, 1);
    __real_cv_wait(cv, mutex);
}
void __wrap_taskq_wait_id(taskq_t *queue, taskqid_t id)
{
#ifdef EARLY_DRAIN
    (void)queue;
    (void)id;
#else
    __real_taskq_wait_id(queue, id);
#endif
}
taskqid_t __wrap_taskq_dispatch_delay(taskq_t *queue, task_func_t func,
                                      void *arg, uint_t flags, clock_t when)
{
    taskqid_t result =
        __real_taskq_dispatch_delay(queue, func, arg, flags, when);
#ifdef FALSE_DELAY
    (void)result;
    return 1;
#else
    return result;
#endif
}
static void rejected(void *arg)
{
    (void)arg;
    atomic_fetch_add(&unexpected, 1);
}
static void dependency(void *arg)
{
    (void)arg;
    require(taskq_of_curthread() == b, "dependency owner");
    atomic_store(&b_entered, 1);
    await(&b_release);
    atomic_store(&b_done, 1);
}
static void caller(void *arg)
{
    (void)arg;
    require(taskq_of_curthread() == a, "caller owner");
    require(taskq_dispatch(b, dependency, NULL, TQ_NOSLEEP) == 1,
            "dependency dispatch");
    taskq_wait(b);
    require(atomic_load(&b_done), "dependency completion");
    atomic_store(&a_done, 1);
}
static void tail(void *arg)
{
    (void)arg;
    require(taskq_of_curthread() == a && atomic_load(&a_done), "tail order");
    atomic_store(&tail_entered, 1);
    await(&tail_release);
    atomic_store(&tail_done, 1);
}
static void reuse(void *arg)
{
    (void)arg;
    require(taskq_of_curthread() == b, "reuse owner");
    atomic_fetch_add(&reused, 1);
}
static void *drain(void *arg)
{
    (void)arg;
    taskq_wait_id(a, 1);
    atomic_store(&drain_done, 1);
    return NULL;
}
static void empty(taskq_t *queue)
{
    mutex_enter(&queue->tq_lock);
    require(queue->tq_active == 0 && queue->tq_nalloc == 0 &&
                queue->tq_task.tqent_next == &queue->tq_task &&
                queue->tq_task.tqent_prev == &queue->tq_task,
            "queue drain state");
    mutex_exit(&queue->tq_lock);
}
int main(void)
{
    require(!taskq_now, "inline dispatch disabled");
    system_taskq_init();
    for (unsigned cycle = 0; cycle < 3; ++cycle) {
        wait_seen = drain_done = b_entered = b_release = b_done = 0;
        tail_entered = tail_release = tail_done = a_done = reused = 0;
        a = taskq_create("witness_a", 1, minclsyspri, 0, 2, 0);
        b = taskq_create("witness_b", 1, minclsyspri, 0, 1, 0);
        require(a && b && a != b, "distinct progress queues");
        require(taskq_dispatch(a, caller, NULL, TQ_NOSLEEP) == 1,
                "caller dispatch");
        await(&b_entered);
        require(taskq_dispatch(a, tail, NULL, TQ_NOSLEEP) == 1,
                "queued tail dispatch");
        require(taskq_dispatch(a, rejected, NULL, TQ_NOSLEEP) == 0 &&
                    taskq_dispatch(b, rejected, NULL, TQ_NOSLEEP) == 0,
                "nonblocking entry limit");
        mutex_enter(&a->tq_lock);
        require(a->tq_nalloc == 2 && a->tq_task.tqent_next != &a->tq_task &&
                    a->tq_task.tqent_next == a->tq_task.tqent_prev,
                "caller limit state");
        mutex_exit(&a->tq_lock);
        mutex_enter(&b->tq_lock);
        require(b->tq_nalloc == 1 && b->tq_task.tqent_next == &b->tq_task &&
                    b->tq_task.tqent_prev == &b->tq_task,
                "dependency limit state");
        mutex_exit(&b->tq_lock);
        require(taskq_dispatch_delay(b, rejected, NULL, TQ_NOSLEEP, 1) == 0,
                "delayed dispatch unsupported");
        require(taskq_cancel_id(b, 1, B_FALSE) == ENOENT, "cancel unsupported");
        atomic_store(&watched, &a->tq_wait_cv);
        pthread_t waiter;
        require(pthread_create(&waiter, NULL, drain, NULL) == 0,
                "drainer create");
        double limit = now() + 5.0;
        while (!atomic_load(&wait_seen) && !atomic_load(&drain_done)) {
            require(now() < limit, "drain observation deadline");
            struct timespec pause = {0, 1000000};
            nanosleep(&pause, NULL);
        }
        require(!atomic_load(&drain_done), "premature drain");
        b_release = 1;
        await(&tail_entered);
        require(atomic_load(&a_done) && atomic_load(&b_done) &&
                    !atomic_load(&drain_done),
                "drain includes later work");
        tail_release = 1;
        require(pthread_join(waiter, NULL) == 0 && atomic_load(&drain_done) &&
                    atomic_load(&tail_done),
                "drain completion");
        atomic_store(&watched, NULL);
        taskq_wait(b);
        empty(a);
        empty(b);
        require(taskq_dispatch(b, reuse, NULL, TQ_NOSLEEP) == 1,
                "entry reuse dispatch");
        taskq_wait(b);
        require(atomic_load(&reused) == 1 && !atomic_load(&unexpected),
                "entry reuse and rejected callbacks");
        empty(b);
        taskq_destroy(a);
        taskq_destroy(b);
        a = b = NULL;
    }
    system_taskq_fini();
    require(!system_taskq && !system_delay_taskq && !atomic_load(&unexpected),
            "system queue teardown");
    puts("{\"format\":\"aether-libzpool-taskq-v1\",\"cycles\":3,"
         "\"dependency_progress\":true,\"whole_queue_drain\":true,"
         "\"nonblocking_limit\":true,\"delayed_dispatch\":\"unsupported\"}");
    return 0;
}
