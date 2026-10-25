/* SPDX-License-Identifier: BSD-2-Clause */
/* Bounded native fixture bridge. Raw taskq symbols are private backend calls.
 */
#include "bridge.h"

_Static_assert(sizeof(taskq_t) <= 512, "taskq exceeds arena slot");
_Static_assert(sizeof(taskq_ent_t) <= 512, "entry exceeds arena slot");
_Static_assert(sizeof(kthread_t *) <= 512, "worker list exceeds slot");
_Static_assert(512 % _Alignof(taskq_t) == 0, "taskq alignment");
_Static_assert(512 % _Alignof(taskq_ent_t) == 0, "entry alignment");
_Static_assert(7 * 512 <= 4096, "live object budget");
/* Retained in the native object for inspection, not guessed from host layouts.
 */
const uint64_t aether_taskq_layout[] = {sizeof(taskq_t),
                                        sizeof(taskq_ent_t),
                                        sizeof(kmutex_t),
                                        sizeof(krwlock_t),
                                        sizeof(kcondvar_t),
                                        512,
                                        8,
                                        4096};

static pthread_mutex_t arena_lock = PTHREAD_MUTEX_INITIALIZER;
static unsigned char *arena;
static size_t allocated[8];
static taskq_t *queues[2];
static unsigned ready;

static void check(int ok, unsigned code)
{
    if (!ok)
        aether_taskq_fail(code);
}
void *aether_taskq_alloc(size_t bytes, int flags)
{
    check(ready && bytes && bytes <= 512 &&
              (flags == KM_SLEEP || flags == KM_NOSLEEP),
          306);
    check(pthread_mutex_lock(&arena_lock) == 0, 307);
    for (unsigned i = 0; i < 8; ++i) {
        if (!allocated[i]) {
            unsigned char *p = arena + i * 512;
            memset(p, 0, 512);
            allocated[i] = bytes;
            check(pthread_mutex_unlock(&arena_lock) == 0, 307);
            return p;
        }
    }
    check(pthread_mutex_unlock(&arena_lock) == 0, 307);
    if (flags == KM_SLEEP)
        aether_taskq_fail(302);
    return NULL;
}
void aether_taskq_free(void *pointer, size_t bytes)
{
    check(ready, 303);
    uintptr_t p = (uintptr_t)pointer, base = (uintptr_t)arena;
    check(p >= base && p - base < 4096 && (p - base) % 512 == 0, 303);
    unsigned slot = (unsigned)((p - base) / 512);
    check(pthread_mutex_lock(&arena_lock) == 0, 307);
    check(bytes && allocated[slot] == bytes, 303);
    memset(pointer, 0, 512);
    allocated[slot] = 0;
    check(pthread_mutex_unlock(&arena_lock) == 0, 307);
}
void aether_taskq_begin(void)
{
    aether_taskq_require_parent();
    check(!ready && !arena && !queues[0] && !queues[1] && !taskq_now, 305);
    arena = aether_taskq_map_arena();
    check(arena && (uintptr_t)arena % 4096 == 0, 306);
    memset(allocated, 0, sizeof allocated);
    ready = 1;
    aether_taskq_tsd_init();
}
void aether_taskq_end(void)
{
    aether_taskq_require_parent();
    check(ready && !queues[0] && !queues[1], 305);
    aether_taskq_reap_all();
    for (unsigned i = 0; i < 8; ++i)
        check(!allocated[i], 306);
    aether_taskq_tsd_fini();
    aether_taskq_unmap_arena(arena);
    arena = NULL;
    ready = 0;
}
taskq_t *aether_taskq_create(const char *name, unsigned entries)
{
    aether_taskq_require_parent();
    check(ready, 305);
    if (!name || !name[0] || strnlen(name, 32) == 32 ||
        (entries != 1 && entries != 2) || (queues[0] && queues[1]))
        return NULL;
    if (!queues[0] && !queues[1])
        aether_taskq_reap_all();
    unsigned slot = queues[0] ? 1 : 0;
    taskq_t *q = taskq_create(name, 1, minclsyspri, 0, (int)entries, 0);
    check(q != NULL, 302);
    queues[slot] = q;
    return q;
}
static void owned(taskq_t *q)
{
    check(ready && q && (q == queues[0] || q == queues[1]), 304);
}
void aether_taskq_destroy(taskq_t *q)
{
    aether_taskq_require_parent();
    owned(q);
    /* Caller must first drain both queues and cease submissions. */
    unsigned slot = queues[0] == q ? 0 : 1;
    taskq_destroy(q);
    queues[slot] = NULL;
}
taskqid_t aether_taskq_dispatch(taskq_t *q, task_func_t fn, void *arg,
                                unsigned flags)
{
    owned(q);
    check(fn && flags == TQ_NOSLEEP, 304);
    return taskq_dispatch(q, fn, arg, flags);
}
void mutex_init(kmutex_t *m, char *name, int type, void *arg)
{
    check(!name && type == MUTEX_DEFAULT && !arg, 304);
    check(pthread_mutex_init(&m->m_lock, NULL) == 0, 307);
    m->m_owner = 0;
}
void mutex_destroy(kmutex_t *m)
{
    check(pthread_mutex_destroy(&m->m_lock) == 0, 307);
}
void mutex_enter(kmutex_t *m)
{
    check(pthread_mutex_lock(&m->m_lock) == 0, 307);
    m->m_owner = pthread_self();
}
void mutex_exit(kmutex_t *m)
{
    check(pthread_equal(m->m_owner, pthread_self()), 307);
    m->m_owner = 0;
    check(pthread_mutex_unlock(&m->m_lock) == 0, 307);
}
void rw_init(krwlock_t *r, char *name, int type, void *arg)
{
    check(!name && type == RW_DEFAULT && !arg, 304);
    check(pthread_rwlock_init(&r->rw_lock, NULL) == 0, 307);
    r->rw_owner = 0;
    r->rw_readers = 0;
}
void rw_destroy(krwlock_t *r)
{
    check(pthread_rwlock_destroy(&r->rw_lock) == 0, 307);
}
void rw_enter(krwlock_t *r, int mode)
{
    check(mode == RW_READER || mode == RW_WRITER, 304);
    if (mode == RW_READER) {
        check(pthread_rwlock_rdlock(&r->rw_lock) == 0, 307);
        __atomic_add_fetch(&r->rw_readers, 1, __ATOMIC_RELAXED);
    } else {
        check(pthread_rwlock_wrlock(&r->rw_lock) == 0, 307);
        r->rw_owner = pthread_self();
    }
}
void rw_exit(krwlock_t *r)
{
    if (__atomic_load_n(&r->rw_readers, __ATOMIC_RELAXED))
        __atomic_sub_fetch(&r->rw_readers, 1, __ATOMIC_RELAXED);
    else {
        check(pthread_equal(r->rw_owner, pthread_self()), 307);
        r->rw_owner = 0;
    }
    check(pthread_rwlock_unlock(&r->rw_lock) == 0, 307);
}
void cv_init(kcondvar_t *c, char *name, int type, void *arg)
{
    check(!name && type == CV_DEFAULT && !arg, 304);
    check(pthread_cond_init(c, NULL) == 0, 307);
}
void cv_destroy(kcondvar_t *c) { check(pthread_cond_destroy(c) == 0, 307); }
void cv_wait(kcondvar_t *c, kmutex_t *m)
{
    check(pthread_equal(m->m_owner, pthread_self()), 307);
    aether_taskq_before_wait(c);
    m->m_owner = 0;
    check(pthread_cond_wait(c, &m->m_lock) == 0, 307);
    m->m_owner = pthread_self();
}
int cv_timedwait(kcondvar_t *c, kmutex_t *m, clock_t when)
{
    (void)c;
    (void)m;
    (void)when;
    aether_taskq_fail(304);
}
clock_t aether_taskq_forbidden_ticks(void) { aether_taskq_fail(304); }
void cv_signal(kcondvar_t *c) { check(pthread_cond_signal(c) == 0, 307); }
void cv_broadcast(kcondvar_t *c) { check(pthread_cond_broadcast(c) == 0, 307); }

long aether_taskq_sysconf(int key)
{
    if (key == _SC_NPROCESSORS_ONLN)
        return 1;
    errno = EINVAL;
    return -1;
}
