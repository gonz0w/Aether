/* SPDX-License-Identifier: BSD-2-Clause */
/* Private unavailable-UTC witness. Observe the real provider without changing
 * its return, errno or output. Correlate its failure with actual guarded engine
 * termination; no SPA activation, wall-time substitute or clean fini claim. */
#include <sys/spa_impl.h>
#include <sys/auxv.h>
#include <errno.h>
#include <time.h>
static unsigned armed, observed, skip_observer;
extern int __real_clock_gettime(clockid_t, struct timespec *);
extern void __real__Exit(int) __attribute__((noreturn));
int __wrap_clock_gettime(clockid_t clock, struct timespec *output)
{
    int result = __real_clock_gettime(clock, output);
    if (clock == CLOCK_REALTIME && result == -1 && errno == ENOTSUP &&
        __atomic_load_n(&armed, __ATOMIC_RELAXED) &&
        !__atomic_load_n(&skip_observer, __ATOMIC_RELAXED))
        __atomic_store_n(&observed, 1, __ATOMIC_RELAXED);
    return result;
}
void __wrap__Exit(int status)
{
    /* 849 is a private failure token, never success or normal retirement. */
    if (status == 125 && __atomic_load_n(&observed, __ATOMIC_RELAXED))
        status = 849;
    __real__Exit(status);
}
int aether_volume_spa_utc_probe(int omit_observer)
{
    struct timespec output = {17, 29};
    if (getauxval(0xa001) != 0x50000101UL ||
        __real_clock_gettime(CLOCK_REALTIME, &output) != -1 ||
        errno != ENOTSUP || output.tv_sec != 17 || output.tv_nsec != 29)
        return 848;
    __atomic_store_n(&skip_observer, omit_observer, __ATOMIC_RELAXED);
    __atomic_store_n(&armed, 1, __ATOMIC_RELAXED);
    spa_namespace_enter(FTAG);
    /* Actual spa_add -> spa_set_allocator -> __zfs_dbgmsg -> checked
     * gethrestime_sec must terminate on unavailable CLOCK_REALTIME. */
    spa_t *spa = spa_add("aether_utc_guard", NULL, NULL);
    /* An unexpected return is a failed oracle, with normal object cleanup. */
    if (spa)
        spa_remove(spa);
    spa_namespace_exit(FTAG);
    return 848;
}
