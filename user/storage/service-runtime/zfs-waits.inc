/* SPDX-License-Identifier: BSD-2-Clause */
/* Private witness bridge. Actual caller objects retain their upstream notices.
 * This fail-closed assertion bridge must never be linked into the engine. */
#include <stdlib.h>
#include "zfs-declarations.h"
_Noreturn void libspl_assertf(const char *file, const char *func, int line,
                              const char *format, ...)
{
    (void)file, (void)func, (void)line, (void)format;
    _Exit(125);
}
static int zfs_lock(kmutex_t *mp)
{
    mutex_enter(mp);
    return pthread_equal(mp->m_owner, pthread_self()) ? 0 : EIO;
}
static int zfs_unlock(kmutex_t *mp)
{
    if (!pthread_equal(mp->m_owner, pthread_self()))
        return EIO;
    mutex_exit(mp);
    return 0;
}
static int zfs_cond_init(kcondvar_t *cv)
{
    cv_init(cv, NULL, 0, NULL);
    return 0;
}
static int zfs_wait(kcondvar_t *cv, kmutex_t *mp, const struct timespec *at)
{
    /* Fixture deadlines come from a successful bounded monotonic observation.
     */
    hrtime_t deadline = (hrtime_t)at->tv_sec * 1000000000LL + at->tv_nsec;
    int result = cv_timedwait_hires(cv, mp, deadline, 1, CALLOUT_FLAG_ABSOLUTE);
    if (!pthread_equal(mp->m_owner, pthread_self()))
        return EIO;
    return result == -1 ? ETIMEDOUT : result == 1 ? 0 : EIO;
}
