/* SPDX-License-Identifier: BSD-2-Clause */
/* Host pthread primitives for actual pinned libzpool/SPA bodies. This does not
 * emulate native thread retirement, memory grants or physical I/O. */
#define _DARWIN_C_SOURCE 1
#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <limits.h>
#include <pthread.h>
#include <signal.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#define CHECK(x)                                                               \
    do {                                                                       \
        if (!(x))                                                              \
            exit(90);                                                          \
    } while (0)
#define VERIFY0(x) CHECK((x) == 0)
#define VERIFY(x) CHECK(x)
#define ASSERT(x) CHECK(x)
#define ASSERT0(x) CHECK((x) == 0)
#define ASSERT3S(a, op, b) CHECK((a)op(b))
#define ASSERT3U(a, op, b) CHECK((a)op(b))
#define ASSERT3P(a, op, b) CHECK((a)op(b))
#define MAX(a, b) ((a) > (b) ? (a) : (b))
#define MIN(a, b) ((a) < (b) ? (a) : (b))
#define KM_SLEEP 1
#define KM_NOSLEEP 0
#define RW_DEFAULT 0
#define RW_READER 0
#define MUTEX_DEFAULT 0
#define CV_DEFAULT 0
#define TS_RUN 0
#define panic(...) abort()
static int p0, hz = 100;
static const int maxclsyspri = 0, minclsyspri = 0, wtqclsyspri = 0;
typedef unsigned uint_t;
typedef int boolean_t;
typedef int pri_t;
typedef pthread_mutex_t kmutex_t;
typedef pthread_cond_t kcondvar_t;
typedef pthread_rwlock_t krwlock_t;
typedef pthread_t kthread_t;
static _Atomic unsigned allocations;
static kthread_t threads[64];
static unsigned created;
static long aether_zfs_assigned_cpus(void) { return 1; }
static void *kmem_alloc(size_t bytes, int flags)
{
    (void)flags;
    void *p = malloc(bytes);
    CHECK(p);
    ++allocations;
    return p;
}
static void *kmem_zalloc(size_t bytes, int flags)
{
    void *p = kmem_alloc(bytes, flags);
    memset(p, 0, bytes);
    return p;
}
static void kmem_free(void *p, size_t bytes)
{
    (void)bytes;
    CHECK(p && allocations);
    free(p);
    --allocations;
}
struct start {
    void (*function)(void *);
    void *argument;
};
static void *start(void *argument)
{
    struct start copy = *(struct start *)argument;
    kmem_free(argument, sizeof copy);
    copy.function(copy.argument);
    return NULL;
}
static kthread_t *thread_create_named(const char *name, void *stack,
                                      size_t bytes, void (*function)(void *),
                                      void *argument, unsigned flags,
                                      void *process, int state, int priority)
{
    (void)name;
    (void)stack;
    (void)bytes;
    (void)flags;
    (void)process;
    (void)state;
    (void)priority;
    CHECK(created < 64);
    struct start *entry = kmem_alloc(sizeof *entry, KM_SLEEP);
    *entry = (struct start){function, argument};
    VERIFY0(pthread_create(&threads[created], NULL, start, entry));
    return &threads[created++];
}
static _Noreturn void thread_exit(void) { pthread_exit(NULL); }
#define mutex_init(m, n, t, a) VERIFY0(pthread_mutex_init(m, NULL))
#define mutex_enter(m) VERIFY0(pthread_mutex_lock(m))
#define mutex_exit(m) VERIFY0(pthread_mutex_unlock(m))
#define mutex_destroy(m) VERIFY0(pthread_mutex_destroy(m))
#define rw_init(m, n, t, a) VERIFY0(pthread_rwlock_init(m, NULL))
#define rw_enter(m, t) VERIFY0(pthread_rwlock_rdlock(m))
#define rw_exit(m) VERIFY0(pthread_rwlock_unlock(m))
#define rw_destroy(m) VERIFY0(pthread_rwlock_destroy(m))
#define cv_init(c, n, t, a) VERIFY0(pthread_cond_init(c, NULL))
#define cv_signal(c) VERIFY0(pthread_cond_signal(c))
#define cv_broadcast(c) VERIFY0(pthread_cond_broadcast(c))
#define cv_destroy(c) VERIFY0(pthread_cond_destroy(c))
static void host_cv_wait(kcondvar_t *, kmutex_t *);
#define cv_wait(c, m) host_cv_wait(c, m)
static long ddi_get_lbolt(void) { return 1; }
static int cv_timedwait(kcondvar_t *c, kmutex_t *m, long at)
{
    (void)at;
    struct timespec deadline;
    VERIFY0(clock_gettime(CLOCK_REALTIME, &deadline));
    ++deadline.tv_sec;
    int result = pthread_cond_timedwait(c, m, &deadline);
    CHECK(!result || result == ETIMEDOUT);
    return result == ETIMEDOUT ? -1 : 1;
}

/* Generated include contains upstream types, original taskq bodies and the
 * selected SPA table/sizing/finalization. Its CDDL notice is retained. */
#include "selected-queue-bodies.inc"

static pthread_mutex_t gate_lock = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t gate_cv = PTHREAD_COND_INITIALIZER;
static unsigned completion_entered, release_completion, wait_seen,
    wait_returned;
static _Atomic unsigned completed, parent_completed;
static pthread_t waiter;
static _Thread_local unsigned designated_waiter;
static taskq_t *completion_queue;

static void host_cv_wait(kcondvar_t *condition, kmutex_t *mutex)
{
    if (condition == &system_delay_taskq->tq_wait_cv && designated_waiter) {
        VERIFY0(pthread_mutex_lock(&gate_lock));
        wait_seen = 1;
        VERIFY0(pthread_cond_broadcast(&gate_cv));
        VERIFY0(pthread_mutex_unlock(&gate_lock));
    }
    VERIFY0(pthread_cond_wait(condition, mutex));
}
static void completed_work(void *argument)
{
    (void)argument;
    CHECK(taskq_of_curthread() == completion_queue);
    VERIFY0(pthread_mutex_lock(&gate_lock));
    completion_entered = 1;
    VERIFY0(pthread_cond_broadcast(&gate_cv));
    while (!release_completion)
        VERIFY0(pthread_cond_wait(&gate_cv, &gate_lock));
    VERIFY0(pthread_mutex_unlock(&gate_lock));
    ++completed;
}
static void issuing_work(void *argument)
{
    (void)argument;
    CHECK(taskq_of_curthread() == system_taskq);
    CHECK(taskq_dispatch(completion_queue, completed_work, NULL, TQ_SLEEP));
    taskq_wait(completion_queue);
    CHECK(completed == 1);
    ++parent_completed;
}
static void *wait_for_completion(void *argument)
{
    (void)argument;
    designated_waiter = 1;
    taskq_wait(system_delay_taskq);
    VERIFY0(pthread_mutex_lock(&gate_lock));
    wait_returned = 1;
    VERIFY0(pthread_cond_broadcast(&gate_cv));
    VERIFY0(pthread_mutex_unlock(&gate_lock));
    return NULL;
}
static void count_work(void *argument)
{
    CHECK(taskq_of_curthread() == argument);
    ++completed;
}
static void deadlock_alarm(int signal)
{
    (void)signal;
    /* Deliberately merged issue/completion queues must not be a success. */
    _Exit(99);
}
int main(int argc, char **argv)
{
    CHECK(argc == 2);
    int mode = atoi(argv[1]);
    system_taskq_init();
    CHECK(created == 2 && system_taskq != system_delay_taskq &&
          system_taskq->tq_nthreads == 1 &&
          system_delay_taskq->tq_nthreads == 1);
    CHECK(system_taskq->tq_maxalloc == 512 &&
          system_delay_taskq->tq_maxalloc == 512);
    if (mode == 0 || mode == 1) {
        signal(SIGALRM, deadlock_alarm);
        alarm(2);
        completion_queue = mode == 1 ? system_taskq : system_delay_taskq;
        CHECK(taskq_dispatch(system_taskq, issuing_work, NULL, TQ_SLEEP));
        VERIFY0(pthread_mutex_lock(&gate_lock));
        while (!completion_entered)
            VERIFY0(pthread_cond_wait(&gate_cv, &gate_lock));
        VERIFY0(pthread_create(&waiter, NULL, wait_for_completion, NULL));
        while (!wait_seen && !wait_returned)
            VERIFY0(pthread_cond_wait(&gate_cv, &gate_lock));
        if (wait_returned || completed || parent_completed)
            return 98;
        release_completion = 1;
        VERIFY0(pthread_cond_broadcast(&gate_cv));
        VERIFY0(pthread_mutex_unlock(&gate_lock));
        VERIFY0(pthread_join(waiter, NULL));
        taskq_wait(system_taskq);
        CHECK(completed == 1 && parent_completed == 1);
        alarm(0);
    } else if (mode == 2) {
        spa_t spa = {.spa_alloc_count = 1};
        const int expected[7][4] = {{1, 0, 1, 0}, {8, 0, 1, 0}, {1, 0, 1, 0},
                                    {8, 0, 1, 0}, {1, 0, 1, 0}, {1, 0, 1, 0},
                                    {4, 0, 1, 0}};
        for (int t = 0; t < 7; ++t)
            for (int q = 0; q < 4; ++q) {
                spa_taskqs_init(&spa, t, q);
                spa_taskqs_t *queues = &spa.spa_zio_taskq[t][q];
                CHECK(queues->stqs_count == (unsigned)(expected[t][q] != 0));
                if (!expected[t][q])
                    continue;
                taskq_t *queue = queues->stqs_taskq[0];
                CHECK(queue->tq_nthreads == expected[t][q]);
                CHECK(taskq_dispatch(queue, count_work, queue, TQ_SLEEP));
            }
        CHECK(created == 33);
        for (int t = 0; t < 7; ++t)
            for (int q = 0; q < 4; ++q)
                spa_taskqs_fini(&spa, t, q);
        CHECK(completed == 14);
    } else
        return 97;
    system_taskq_fini();
    CHECK(!system_taskq && !system_delay_taskq);
    for (unsigned i = 0; i < created; ++i)
        VERIFY0(pthread_join(threads[i], NULL));
    CHECK(allocations == 0);
    return 0;
}
