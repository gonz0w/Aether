/* SPDX-License-Identifier: BSD-2-Clause */
/* External libzpool fixed-queue call observation; no engine policy change. */
#include <sys/zfs_context.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>

void __real_system_taskq_init(void);
void __real_system_taskq_fini(void);
taskqid_t __real_taskq_dispatch(taskq_t *, task_func_t, void *, uint_t);
taskqid_t __real_taskq_dispatch_delay(taskq_t *, task_func_t, void *, uint_t,
                                      clock_t);
void __real_taskq_dispatch_ent(taskq_t *, task_func_t, void *, uint_t,
                               taskq_ent_t *);
void __real_taskq_wait(taskq_t *);
void __real_taskq_wait_id(taskq_t *, taskqid_t);
void __real_taskq_wait_outstanding(taskq_t *, taskqid_t);
int __real_taskq_cancel_id(taskq_t *, taskqid_t, boolean_t);
void __wrap_system_taskq_init(void);
void __wrap_system_taskq_fini(void);
taskqid_t __wrap_taskq_dispatch(taskq_t *, task_func_t, void *, uint_t);
taskqid_t __wrap_taskq_dispatch_delay(taskq_t *, task_func_t, void *, uint_t,
                                      clock_t);
void __wrap_taskq_dispatch_ent(taskq_t *, task_func_t, void *, uint_t,
                               taskq_ent_t *);
void __wrap_taskq_wait(taskq_t *);
void __wrap_taskq_wait_id(taskq_t *, taskqid_t);
void __wrap_taskq_wait_outstanding(taskq_t *, taskqid_t);
int __wrap_taskq_cancel_id(taskq_t *, taskqid_t, boolean_t);
void dispatch_snapshot(unsigned, const char *);
int dispatch_check(void);
static pthread_mutex_t observe_lock = PTHREAD_MUTEX_INITIALIZER;
static taskq_t *queues[2];
static unsigned created, destroyed;
enum {
    CALL,
    ACCEPT,
    REJECT,
    ENTRY,
    DELAY,
    DELAY_OK,
    DELAY_NO,
    WAIT,
    WAIT_ID,
    WAIT_OUT,
    CANCEL,
    CANCEL_NO,
    FIELDS
};
static unsigned long counts[2][FIELDS];
static void require(int ok, const char *reason)
{
    if (!ok) {
        fprintf(stderr, "DISPATCH FAIL: %s\n", reason);
        exit(2);
    }
}
static void lock(void) { require(!pthread_mutex_lock(&observe_lock), "lock"); }
static void unlock(void)
{
    require(!pthread_mutex_unlock(&observe_lock), "unlock");
}
static int record(taskq_t *q, int field)
{
    lock();
    int group = q && q == queues[0] ? 0 : q && q == queues[1] ? 1 : -1;
    if (group >= 0)
        counts[group][field]++;
    unlock();
    return group;
}
static void result(int group, int field)
{
    if (group < 0)
        return;
    lock();
    counts[group][field]++;
    unlock();
}
void __wrap_system_taskq_init(void)
{
    __real_system_taskq_init();
    lock();
    require(!queues[0] && !queues[1] && system_taskq && system_delay_taskq &&
                system_taskq != system_delay_taskq,
            "registration");
    queues[0] = system_taskq;
    queues[1] = system_delay_taskq;
    created++;
    unlock();
}
void __wrap_system_taskq_fini(void)
{
    __real_system_taskq_fini();
    lock();
    require(queues[0] && queues[1], "retirement");
    queues[0] = queues[1] = NULL;
    destroyed++;
    unlock();
}
taskqid_t __wrap_taskq_dispatch(taskq_t *q, task_func_t fn, void *arg,
                                uint_t flags)
{
    int group = record(q, CALL);
#ifdef DROP_DISPATCH_COUNT
    if (group >= 0) {
        lock();
        counts[group][CALL]--;
        unlock();
    }
#endif
    taskqid_t id = __real_taskq_dispatch(q, fn, arg, flags);
    result(group, id ? ACCEPT : REJECT);
    return id;
}
taskqid_t __wrap_taskq_dispatch_delay(taskq_t *q, task_func_t fn, void *arg,
                                      uint_t flags, clock_t when)
{
    int group = record(q, DELAY);
    taskqid_t id = __real_taskq_dispatch_delay(q, fn, arg, flags, when);
#ifdef FALSE_DELAY_SUCCESS
    id = 1;
#endif
    result(group, id ? DELAY_OK : DELAY_NO);
    return id;
}
void __wrap_taskq_dispatch_ent(taskq_t *q, task_func_t fn, void *arg,
                               uint_t flags, taskq_ent_t *entry)
{
    (void)record(q, ENTRY);
    __real_taskq_dispatch_ent(q, fn, arg, flags, entry);
}
void __wrap_taskq_wait(taskq_t *q)
{
    (void)record(q, WAIT);
    __real_taskq_wait(q);
}
void __wrap_taskq_wait_id(taskq_t *q, taskqid_t id)
{
    (void)record(q, WAIT_ID);
    __real_taskq_wait_id(q, id);
}
void __wrap_taskq_wait_outstanding(taskq_t *q, taskqid_t id)
{
    (void)record(q, WAIT_OUT);
    __real_taskq_wait_outstanding(q, id);
}
int __wrap_taskq_cancel_id(taskq_t *q, taskqid_t id, boolean_t wait)
{
    int group = record(q, CANCEL);
    int status = __real_taskq_cancel_id(q, id, wait);
    if (status == ENOENT)
        result(group, CANCEL_NO);
    return status;
}
void dispatch_snapshot(unsigned seq, const char *stage)
{
    unsigned long copy[2][FIELDS];
    lock();
    memcpy(copy, counts, sizeof copy);
    unsigned init = created, fini = destroyed;
    unlock();
    printf(
        "{\"format\":\"aether-libzpool-dispatch-v1\",\"sequence\":%u,\"stage\":"
        "\"%s\",\"created_pairs\":%u,\"destroyed_pairs\":%u,\"groups\":[",
        seq, stage, init, fini);
    for (int i = 0; i < 2; i++) {
        printf("%s{\"name\":\"%s\",\"counts\":[", i ? "," : "",
               i ? "delay_taskq" : "system_taskq");
        for (int j = 0; j < FIELDS; j++)
            printf("%s%lu", j ? "," : "", copy[i][j]);
        printf("]}");
    }
    printf("]}\n");
}
static _Atomic unsigned callbacks;
static void callback(void *arg)
{
    (void)arg;
    atomic_fetch_add(&callbacks, 1);
}
int dispatch_check(void)
{
    __wrap_system_taskq_init();
    for (int i = 0; i < 2; i++) {
        taskq_t *q = queues[i];
        taskq_ent_t entry;
        taskq_init_ent(&entry);
        taskqid_t id = __wrap_taskq_dispatch(q, callback, NULL, TQ_SLEEP);
        require(id != 0, "normal dispatch");
        __wrap_taskq_dispatch_ent(q, callback, NULL, TQ_SLEEP, &entry);
        __wrap_taskq_wait_id(q, id);
        __wrap_taskq_wait_outstanding(q, 0);
        __wrap_taskq_wait(q);
        require(__wrap_taskq_dispatch_delay(q, callback, NULL, TQ_SLEEP, 0) ==
                    0,
                "delayed result");
        require(__wrap_taskq_cancel_id(q, id, B_TRUE) == ENOENT,
                "cancel result");
    }
    __wrap_system_taskq_fini();
    require(atomic_load(&callbacks) == 4, "callback completion");
    const unsigned long expected[FIELDS] = {1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1};
    lock();
    require(!memcmp(counts[0], expected, sizeof expected) &&
                !memcmp(counts[1], expected, sizeof expected),
            "observer count");
    unlock();
    dispatch_snapshot(0, "dispatch-check");
    return 0;
}

_Static_assert(
    __builtin_types_compatible_p(__typeof(&system_taskq_init),
                                 __typeof(&__wrap_system_taskq_init)),
    "system_taskq_init signature");

_Static_assert(
    __builtin_types_compatible_p(__typeof(&system_taskq_fini),
                                 __typeof(&__wrap_system_taskq_fini)),
    "system_taskq_fini signature");

_Static_assert(__builtin_types_compatible_p(__typeof(&taskq_dispatch),
                                            __typeof(&__wrap_taskq_dispatch)),
               "taskq_dispatch signature");

_Static_assert(
    __builtin_types_compatible_p(__typeof(&taskq_dispatch_delay),
                                 __typeof(&__wrap_taskq_dispatch_delay)),
    "taskq_dispatch_delay signature");

_Static_assert(
    __builtin_types_compatible_p(__typeof(&taskq_dispatch_ent),
                                 __typeof(&__wrap_taskq_dispatch_ent)),
    "taskq_dispatch_ent signature");

_Static_assert(__builtin_types_compatible_p(__typeof(&taskq_wait),
                                            __typeof(&__wrap_taskq_wait)),
               "taskq_wait signature");

_Static_assert(__builtin_types_compatible_p(__typeof(&taskq_wait_id),
                                            __typeof(&__wrap_taskq_wait_id)),
               "taskq_wait_id signature");

_Static_assert(
    __builtin_types_compatible_p(__typeof(&taskq_wait_outstanding),
                                 __typeof(&__wrap_taskq_wait_outstanding)),
    "taskq_wait_outstanding signature");

_Static_assert(__builtin_types_compatible_p(__typeof(&taskq_cancel_id),
                                            __typeof(&__wrap_taskq_cancel_id)),
               "taskq_cancel_id signature");
