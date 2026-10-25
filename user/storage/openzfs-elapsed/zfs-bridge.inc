/* SPDX-License-Identifier: BSD-2-Clause */
/* Private caller witness only. All definitions come from the pinned OpenZFS
 * headers. Mutex owner observations occur only while its actual lock is held.
 * The assert bridge records fail-closed125; it is never linked into the engine.
 */
static long timed_now(void);
void aether_tpool_init_probe(pthread_cond_t *);
struct timespec aether_tpool_deadline_probe(unsigned);
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
static int zfs_timedwait(kcondvar_t *cv, kmutex_t *mp,
                         const struct timespec *at)
{
    hrtime_t deadline = (hrtime_t)at->tv_sec * 1000000000LL + at->tv_nsec;
    int result = cv_timedwait_hires(cv, mp, deadline, 1, CALLOUT_FLAG_ABSOLUTE);
    if (!pthread_equal(mp->m_owner, pthread_self()))
        return EIO;
    return result == -1 ? ETIMEDOUT : result == 1 ? 0 : EIO;
}
static int zfs_raw_wait(kcondvar_t *cv, kmutex_t *mp, const struct timespec *at)
{
    /* Raw POSIX counterexamples also unlock/relock. Keep the diagnostic
     * OpenZFS owner coherent across that borrow, even on native errors. */
    memset(&mp->m_owner, 0, sizeof(pthread_t));
    int error = pthread_cond_timedwait(cv, &mp->m_lock, at);
    mp->m_owner = pthread_self();
    return error;
}
static unsigned zfs_extra(unsigned i, kcondvar_t *cv, kmutex_t *mp)
{
    int saved_errno = errno;
    CHECK(!zfs_lock(mp), 391);
    long now = timed_now();
    CHECK(now >= 0 &&
              cv_timedwait_hires(cv, mp, now, 1, CALLOUT_FLAG_ABSOLUTE) == -1 &&
              cv_timedwait_hires(cv, mp, 0, 1, 0) == -1 &&
              cv_timedwait(cv, mp, (clock_t)(now >> 23)) == -1 &&
              pthread_equal(mp->m_owner, pthread_self()),
          391);
    CHECK(cv_timedwait_hires(cv, mp, 20000000, 1, 0) == -1 &&
              timed_now() >= now + 20000000 &&
              pthread_equal(mp->m_owner, pthread_self()),
          392);
    now = timed_now();
    CHECK(now >= 0, 392);
    clock_t ticks = (clock_t)(now >> 23) + 2;
    CHECK(cv_timedwait(cv, mp, ticks) == -1 &&
              timed_now() >= (hrtime_t)ticks * (1LL << 23) &&
              pthread_equal(mp->m_owner, pthread_self()) &&
              pthread_mutex_trylock(&mp->m_lock) == EBUSY,
          392);
    CHECK(!zfs_unlock(mp), 392);
    now = timed_now();
    CHECK(now >= 0, 393);
    delay(0);
    delay(8);
    CHECK(timed_now() >= now + 8 * (1LL << 23) && errno == saved_errno, 393);
    if (i == 0) {
        /* Exact initializer/deadline blocks from libtpool, not pool lifecycle.
         */
        pthread_cond_t work;
        pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;
        aether_tpool_init_probe(&work);
        now = timed_now();
        struct timespec at = aether_tpool_deadline_probe(1);
        CHECK(!pthread_mutex_lock(&lock) &&
                  pthread_cond_timedwait(&work, &lock, &at) == ETIMEDOUT &&
                  timed_now() >= now + 1000000000LL &&
                  pthread_mutex_trylock(&lock) == EBUSY &&
                  !pthread_mutex_unlock(&lock) &&
                  !pthread_cond_destroy(&work) &&
                  !pthread_mutex_destroy(&lock) && errno == saved_errno,
              394);
    }
    return 0;
}
