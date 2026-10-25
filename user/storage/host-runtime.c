/* SPDX-License-Identifier: BSD-2-Clause */
/* Linux/glibc observation only. Link around the unchanged owned-file fixture.
 */
#include <errno.h>
#include <malloc.h>
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#ifdef CPU_VIEW
#include <stdatomic.h>
long __wrap_sysconf(int);
long __real_sysconf(int);
static _Atomic size_t engine_cpu_queries;
#endif

int __wrap_pthread_create(pthread_t *, const pthread_attr_t *,
                          void *(*)(void *), void *);
void __wrap_kernel_init(int);
void __wrap_kernel_fini(void);
int __wrap_main(int, char **);

struct demand {
    size_t calls, detached, stacks, guards, smallest, largest;
};
static struct demand demand;
static pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;
static unsigned sequence;
#ifdef DISPATCH_OBSERVER
void dispatch_snapshot(unsigned, const char *);
int dispatch_check(void);
#endif
#ifdef THREAD_NAMES
int __wrap_pthread_setname_np(pthread_t, const char *);
int __real_pthread_setname_np(pthread_t, const char *);
static struct {
    char name[64];
    size_t calls;
} names[96];
static size_t name_count;
#endif

static void require(int ok, const char *reason)
{
    if (!ok) {
        fprintf(stderr, "RUNTIME FAIL: %s\n", reason);
        exit(2);
    }
}
#ifdef LIVE_ROLES
/* Pinned zfs_context.h defines kthread_t as pthread_t. */
pthread_t *__real_zk_thread_create(const char *, void (*)(void *), void *,
                                   size_t, int);
pthread_t *__wrap_zk_thread_create(const char *, void (*)(void *), void *,
                                   size_t, int);
static _Thread_local const char *requested_role;
static struct {
    char name[64];
    size_t creates, active, finished, peak, at_global_peak;
} roles[96];
static size_t role_count;
static size_t role_index(const char *label)
{
#ifdef OMIT_ROLE_LABEL
    label = NULL;
#endif
    if (!label)
        label = "unattributed";
    size_t len = strnlen(label, sizeof roles[0].name);
    require(len && len < sizeof roles[0].name, "live role length");
    for (size_t i = 0; i < len; ++i)
        require(label[i] >= 32 && label[i] <= 126 && label[i] != '"' &&
                    label[i] != '\\',
                "live role encoding");
    for (size_t i = 0; i < role_count; ++i)
        if (!strcmp(roles[i].name, label))
            return i;
    require(role_count < 96, "live role capacity");
    memcpy(roles[role_count].name, label, len + 1);
    return role_count++;
}
pthread_t *__wrap_zk_thread_create(const char *name, void (*fn)(void *),
                                   void *arg, size_t stack, int state)
{
    const char *previous = requested_role;
    requested_role = name;
    pthread_t *result = __real_zk_thread_create(name, fn, arg, stack, state);
    requested_role = previous;
    return result;
}
#endif
#ifdef LIVE_THREADS
struct live_start {
    void *(*function)(void *);
    void *argument;
    size_t stack, guard;
    int reserved;
#ifdef LIVE_ROLES
    size_t role;
#endif
};
static struct live_start live_starts[512];
static size_t live_count, live_peak, live_stack, live_stack_peak;
static size_t live_guard, live_guard_peak, live_finished, heap_samples;
static size_t heap_used_max, heap_mmap_max, heap_arena_max;
/* Caller owns lock. Samples include observer/libc overhead and miss intervals.
 */
static void heap_sample(void)
{
    struct mallinfo2 m = mallinfo2();
    ++heap_samples;
    if (m.uordblks > heap_used_max)
        heap_used_max = m.uordblks;
    if (m.hblkhd > heap_mmap_max)
        heap_mmap_max = m.hblkhd;
    if (m.arena > heap_arena_max)
        heap_arena_max = m.arena;
}
static void live_cleanup(void *arg)
{
    struct live_start *r = arg;
    require(pthread_mutex_lock(&lock) == 0, "live cleanup lock");
    require(r->reserved && live_count && live_stack >= r->stack &&
                live_guard >= r->guard,
            "live cleanup state");
#ifndef OMIT_LIVE_EXIT
#ifdef LIVE_ROLES
    require(roles[r->role].active > 0, "live role cleanup");
    --roles[r->role].active;
    ++roles[r->role].finished;
#endif
    --live_count;
    live_stack -= r->stack;
    live_guard -= r->guard;
    ++live_finished;
    r->reserved = 0;
#endif
    heap_sample();
    require(pthread_mutex_unlock(&lock) == 0, "live cleanup unlock");
}
static void *live_run(void *arg)
{
    struct live_start *r = arg;
    void *value;
    require(pthread_mutex_lock(&lock) == 0, "live start lock");
    void *(*function)(void *) = r->function;
    void *argument = r->argument;
    require(pthread_mutex_unlock(&lock) == 0, "live start unlock");
    pthread_cleanup_push(live_cleanup, r);
    value = function(argument);
    pthread_cleanup_pop(1);
    return value;
}
static void live_snapshot(unsigned seq, const char *stage)
{
    require(pthread_mutex_lock(&lock) == 0, "live snapshot lock");
    heap_sample();
    printf("{\"format\":\"aether-libzpool-live-v1\",\"sequence\":%u,"
           "\"stage\":\"%s\",\"active_workers\":%zu,\"peak_workers\":%zu,"
           "\"finished_workers\":%zu,\"registered_creates\":%zu,\"active_stack_"
           "requests\":%zu,"
           "\"peak_stack_requests\":%zu,\"active_guard_requests\":%zu,"
           "\"peak_guard_requests\":%zu,\"heap_samples\":%zu,"
           "\"sample_max_used\":%zu,\"sample_max_mmap\":%zu,"
           "\"sample_max_arena\":%zu}\n",
           seq, stage, live_count, live_peak, live_finished, demand.calls,
           live_stack, live_stack_peak, live_guard, live_guard_peak,
           heap_samples, heap_used_max, heap_mmap_max, heap_arena_max);
#ifdef LIVE_ROLES
    printf("{\"format\":\"aether-libzpool-live-roles-v1\",\"sequence\":%u,"
           "\"stage\":\"%s\",\"groups\":[",
           seq, stage);
    for (size_t i = 0; i < role_count; ++i)
        printf("%s{\"name\":\"%s\",\"creates\":%zu,\"active\":%zu,\"finished\":"
               "%zu,\"peak\":%zu,\"at_global_peak\":%zu}",
               i ? "," : "", roles[i].name, roles[i].creates, roles[i].active,
               roles[i].finished, roles[i].peak, roles[i].at_global_peak);
    printf("]}\n");
#endif
    require(pthread_mutex_unlock(&lock) == 0, "live snapshot unlock");
}
#endif
#ifdef CPU_VIEW
long __wrap_sysconf(int key)
{
    if (key == _SC_NPROCESSORS_ONLN) {
        atomic_fetch_add_explicit(&engine_cpu_queries, 1, memory_order_relaxed);
#ifdef CPU_VIEW_WRONG
        return 2;
#else
        return 1;
#endif
    }
    return __real_sysconf(key);
}
static void cpu_view_check(void)
{
    require(sysconf(_SC_NPROCESSORS_ONLN) == 1, "one-CPU view");
    require(__real_sysconf(_SC_NPROCESSORS_ONLN) > 0 &&
                sysconf(_SC_PAGESIZE) == __real_sysconf(_SC_PAGESIZE) &&
                sysconf(_SC_PHYS_PAGES) == __real_sysconf(_SC_PHYS_PAGES),
            "CPU-view query routing");
    errno = 0;
    long observed = sysconf(-12345);
    int saved = errno;
    errno = 0;
    long expected = __real_sysconf(-12345);
    require(observed == expected && saved == errno, "CPU-view errno routing");
}
#endif
#ifdef THREAD_NAMES
int __wrap_pthread_setname_np(pthread_t thread, const char *name)
{
    size_t length = strnlen(name, sizeof names[0].name);
    require(length && length < sizeof names[0].name, "observer name length");
    for (size_t i = 0; i < length; ++i)
        require(name[i] >= 32 && name[i] <= 126 && name[i] != '"' &&
                    name[i] != '\\',
                "observer name encoding");
    int result = __real_pthread_setname_np(thread, name);
    require(pthread_mutex_lock(&lock) == 0, "names lock");
    size_t i;
    for (i = 0; i < name_count; ++i)
        if (!strcmp(names[i].name, name))
            break;
    if (i == name_count) {
        require(name_count < sizeof names / sizeof names[0],
                "observer name capacity");
        memcpy(names[i].name, name, length + 1);
        ++name_count;
    }
#ifndef OMIT_THREAD_NAMES
    ++names[i].calls;
#endif
    require(pthread_mutex_unlock(&lock) == 0, "names unlock");
    return result;
}
static void name_snapshot(unsigned seq, const char *stage)
{
    require(pthread_mutex_lock(&lock) == 0, "names snapshot lock");
    printf("{\"format\":\"aether-libzpool-thread-names-v1\",\"sequence\":%u,"
           "\"stage\":\"%s\",\"groups\":[",
           seq, stage);
    for (size_t i = 0; i < name_count; ++i)
        printf("%s{\"name\":\"%s\",\"requests\":%zu}", i ? "," : "",
               names[i].name, names[i].calls);
    printf("]}\n");
    require(pthread_mutex_unlock(&lock) == 0, "names snapshot unlock");
}
#endif
int __real_pthread_create(pthread_t *, const pthread_attr_t *,
                          void *(*)(void *), void *);
int __wrap_pthread_create(pthread_t *thread, const pthread_attr_t *attr,
                          void *(*start)(void *), void *arg)
{
    size_t stack, guard;
    int detached;
    /* All current engine calls supply explicit attributes. Fail closed if the
     * measured path changes instead of inventing a default stack request. */
    require(attr && pthread_attr_getstacksize(attr, &stack) == 0 &&
                pthread_attr_getguardsize(attr, &guard) == 0 &&
                pthread_attr_getdetachstate(attr, &detached) == 0,
            "explicit thread attributes required");
#ifdef LIVE_THREADS
    require(pthread_mutex_lock(&lock) == 0, "observer lock");
    struct live_start *r = NULL;
    for (size_t i = 0; i < 512; ++i)
        if (!live_starts[i].reserved) {
            r = &live_starts[i];
            break;
        }
    require(r != NULL, "live observer capacity");
    *r = (struct live_start){.function = start,
                             .argument = arg,
                             .stack = stack,
                             .guard = guard,
                             .reserved = 1};
#ifdef LIVE_ROLES
    r->role = role_index(requested_role);
#endif
    int result = __real_pthread_create(thread, attr, live_run, r);
    if (result) {
        r->reserved = 0;
        require(pthread_mutex_unlock(&lock) == 0, "failed create unlock");
        return result;
    }
    require(SIZE_MAX - live_stack >= stack && SIZE_MAX - live_guard >= guard,
            "live sum overflow");
#ifdef LIVE_ROLES
    ++roles[r->role].creates;
    ++roles[r->role].active;
    if (roles[r->role].active > roles[r->role].peak)
        roles[r->role].peak = roles[r->role].active;
    if (live_count + 1 > live_peak)
        for (size_t i = 0; i < role_count; ++i)
            roles[i].at_global_peak = roles[i].active;
#endif
    ++live_count;
    live_stack += stack;
    live_guard += guard;
#ifndef OMIT_LIVE_PEAK
    if (live_count > live_peak)
        live_peak = live_count;
    if (live_stack > live_stack_peak)
        live_stack_peak = live_stack;
    if (live_guard > live_guard_peak)
        live_guard_peak = live_guard;
#endif
    heap_sample();
#else
    int result = __real_pthread_create(thread, attr, start, arg);
    if (result)
        return result;
    require(pthread_mutex_lock(&lock) == 0, "observer lock");
#endif
#ifndef OMIT_THREAD_COUNT
    ++demand.calls;
#endif
    demand.detached += detached == PTHREAD_CREATE_DETACHED;
    require(SIZE_MAX - demand.stacks >= stack &&
                SIZE_MAX - demand.guards >= guard,
            "observer sum overflow");
    demand.stacks += stack;
    demand.guards += guard;
    if (!demand.smallest || stack < demand.smallest)
        demand.smallest = stack;
    if (stack > demand.largest)
        demand.largest = stack;
    require(pthread_mutex_unlock(&lock) == 0, "observer unlock");
    return 0;
}
static void snapshot(const char *stage)
{
    require(pthread_mutex_lock(&lock) == 0, "snapshot lock");
    struct demand d = demand;
    require(pthread_mutex_unlock(&lock) == 0, "snapshot unlock");
    struct mallinfo2 m = mallinfo2();
    printf("{\"format\":\"aether-libzpool-demand-v1\",\"sequence\":%u,"
           "\"stage\":\"%s\",\"creates\":%zu,\"detached\":%zu,"
           "\"stack_request_bytes\":%zu,\"guard_request_bytes\":%zu,"
           "\"stack_min_bytes\":%zu,\"stack_max_bytes\":%zu,"
           "\"malloc_arena_bytes\":%zu,\"malloc_used_bytes\":%zu,"
           "\"malloc_free_bytes\":%zu,\"malloc_mmap_bytes\":%zu}\n",
           sequence++, stage, d.calls, d.detached, d.stacks, d.guards,
           d.smallest, d.largest, m.arena, m.uordblks, m.fordblks, m.hblkhd);
#ifdef THREAD_NAMES
    name_snapshot(sequence - 1, stage);
#endif
#ifdef LIVE_THREADS
    live_snapshot(sequence - 1, stage);
#endif
#ifdef DISPATCH_OBSERVER
    dispatch_snapshot(sequence - 1, stage);
#endif
}
void __real_kernel_init(int);
void __wrap_kernel_init(int mode)
{
    snapshot("before-init");
    __real_kernel_init(mode);
    snapshot("after-init");
}
void __real_kernel_fini(void);
void __wrap_kernel_fini(void)
{
    snapshot("before-fini");
    __real_kernel_fini();
    snapshot("after-fini");
}
static void *noop(void *arg) { return arg; }
static int observer_check(void)
{
#ifdef CPU_VIEW
    cpu_view_check();
#endif
    pthread_attr_t attr;
    require(pthread_attr_init(&attr) == 0 &&
                pthread_attr_setguardsize(&attr, 4096) == 0,
            "self-check attributes");
    for (size_t size = 128 * 1024; size <= 256 * 1024; size *= 2) {
        pthread_t thread;
        void *value = NULL;
        require(pthread_attr_setstacksize(&attr, size) == 0 &&
                    __wrap_pthread_create(&thread, &attr, noop, &attr) == 0 &&
                    pthread_join(thread, &value) == 0 && value == &attr,
                "self-check lifecycle");
    }
    require(pthread_attr_destroy(&attr) == 0, "self-check attr destroy");
    require(demand.calls == 2, "observer count");
    require(!demand.detached && demand.stacks == 384 * 1024 &&
                demand.guards == 8192 && demand.smallest == 128 * 1024 &&
                demand.largest == 256 * 1024,
            "observer attributes");
#ifdef THREAD_NAMES
    require(__wrap_pthread_setname_np(pthread_self(), "observer-one") == 0 &&
                __wrap_pthread_setname_np(pthread_self(), "observer-two") == 0,
            "self-check naming");
    require(name_count == 2 && names[0].calls == 1 && names[1].calls == 1 &&
                !strcmp(names[0].name, "observer-one") &&
                !strcmp(names[1].name, "observer-two"),
            "observer names");
#endif
    snapshot("observer-check");
    return 0;
}
#ifdef LIVE_THREADS
static pthread_mutex_t check_lock = PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t check_cv = PTHREAD_COND_INITIALIZER;
static unsigned check_entered, check_release;
static void *live_check_worker(void *arg)
{
    require(pthread_mutex_lock(&check_lock) == 0, "live check lock");
    ++check_entered;
    require(pthread_cond_broadcast(&check_cv) == 0, "live check signal");
    while (!check_release)
        require(pthread_cond_wait(&check_cv, &check_lock) == 0,
                "live check wait");
    require(pthread_mutex_unlock(&check_lock) == 0, "live check unlock");
    if (arg)
        pthread_exit(arg);
    return arg;
}
static int live_check(void)
{
    pthread_attr_t attr;
    pthread_t threads[2];
    require(pthread_attr_init(&attr) == 0 &&
                pthread_attr_setstacksize(&attr, 256 * 1024) == 0 &&
                pthread_attr_setguardsize(&attr, 4096) == 0,
            "live check attributes");
    for (size_t i = 0; i < 2; ++i) {
#ifdef LIVE_ROLES
        requested_role = i ? "check-exit" : "check-return";
#endif
        require(__wrap_pthread_create(&threads[i], &attr, live_check_worker,
                                      (void *)(uintptr_t)i) == 0,
                "live check create");
    }
#ifdef LIVE_ROLES
    requested_role = NULL;
#endif
    require(pthread_mutex_lock(&check_lock) == 0, "live check parent lock");
    while (check_entered != 2)
        require(pthread_cond_wait(&check_cv, &check_lock) == 0,
                "live check parent wait");
    require(pthread_mutex_lock(&lock) == 0, "live count lock");
    require(live_count == 2 && live_peak == 2 &&
                live_stack_peak == 512 * 1024 && live_guard_peak == 8192,
            "live peak");
    require(pthread_mutex_unlock(&lock) == 0, "live count unlock");
    check_release = 1;
    require(pthread_cond_broadcast(&check_cv) == 0 &&
                pthread_mutex_unlock(&check_lock) == 0,
            "live check release");
    for (size_t i = 0; i < 2; ++i) {
        void *value = NULL;
        require(pthread_join(threads[i], &value) == 0 &&
                    value == (void *)(uintptr_t)i,
                "live check join");
    }
    require(!live_count && !live_stack && !live_guard && live_finished == 2,
            "live cleanup");
#ifdef LIVE_ROLES
    require(role_count == 2 && !strcmp(roles[0].name, "check-return") &&
                !strcmp(roles[1].name, "check-exit"),
            "live role label");
    for (size_t i = 0; i < 2; ++i)
        require(roles[i].creates == 1 && roles[i].finished == 1 &&
                    !roles[i].active && roles[i].peak == 1 &&
                    roles[i].at_global_peak == 1,
                "live role accounting");
#endif
    require(pthread_attr_destroy(&attr) == 0, "live check destroy");
    live_snapshot(0, "live-check");
    return 0;
}
#endif
int __real_main(void);
int __wrap_main(int argc, char **argv)
{
    require(setvbuf(stdout, NULL, _IONBF, 0) == 0, "unbuffered results");
#ifdef DISPATCH_OBSERVER
    if (argc == 2 && !strcmp(argv[1], "--dispatch-check"))
        return dispatch_check();
#endif
#ifdef LIVE_THREADS
    if (argc == 2 && !strcmp(argv[1], "--live-check"))
        return live_check();
#endif
    if (argc == 2 && !strcmp(argv[1], "--observer-check"))
        return observer_check();
    require(argc == 1, "unexpected argument");
    printf("{\"format\":\"aether-libzpool-environment-v1\","
           "\"cpus\":%ld,\"page_bytes\":%ld,\"physical_pages\":%ld}\n",
           sysconf(_SC_NPROCESSORS_ONLN), sysconf(_SC_PAGESIZE),
           sysconf(_SC_PHYS_PAGES));
#ifdef CPU_VIEW
    cpu_view_check();
    long host_cpus = __real_sysconf(_SC_NPROCESSORS_ONLN);
    atomic_store_explicit(&engine_cpu_queries, 0, memory_order_relaxed);
#endif
    int result = __real_main();
    snapshot("completed");
#ifdef CPU_VIEW
    size_t queries =
        atomic_load_explicit(&engine_cpu_queries, memory_order_relaxed);
    require(queries > 0, "engine CPU-view query missing");
    printf("{\"format\":\"aether-libzpool-cpu-view-v1\","
           "\"modeled_online_cpus\":1,\"host_online_cpus\":%ld,"
           "\"engine_queries\":%zu}\n",
           host_cpus, queries);
#endif
    return result;
}
