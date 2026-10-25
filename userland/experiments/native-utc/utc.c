/* SPDX-License-Identifier: BSD-2-Clause */
#include "utc.h"
#include "runtime.h"
#include "adapter.h"
#include <errno.h>
#include <sys/auxv.h>

/* Release publishes immutable data; readers acquire before any field access.
 * Close must occur after application joins, so no reader overlaps closure. */
static _Atomic unsigned state;
static struct aether_utc_anchor shared;
static unsigned long established_thread;
static long call(unsigned long op, unsigned long a, unsigned long b)
{
    int saved = errno;
    unsigned long grant = getauxval(0xa001);
    long result = memtrap(op, grant, a, b, 0);
    errno = saved;
    return result;
}
static int initial(long id) { return id == 1 || id == 2; }
int aether_utc_establish(unsigned policy)
{
    if (policy != AETHER_UTC_Q35_RTC_UNAUTHENTICATED)
        return ENOTSUP;
    long id = call(0x28007, 0, 0);
    if (id < 0)
        return (int)-id;
    if (!initial(id))
        return EPERM;
    if (__c11_atomic_load(&state, __ATOMIC_ACQUIRE))
        return EALREADY;
    if (aether_runtime_live() != 1 || aether_runtime_admissions() != 1)
        return EBUSY;
    unsigned expected = 0;
    if (!__c11_atomic_compare_exchange_strong(
            &state, &expected, 1, __ATOMIC_ACQ_REL, __ATOMIC_ACQUIRE))
        return EALREADY;
    struct aether_rtc_sample sample = {0};
    long result = call(0x28011, (uintptr_t)&sample, sizeof(sample));
    struct aether_utc_anchor anchor;
    int error = result < 0 ? (int)-result
                : result   ? EIO
                           : aether_utc_decode(&sample, policy, &anchor);
    if (error) {
        __c11_atomic_store(&state, 0, __ATOMIC_RELEASE);
        return error;
    }
    shared = anchor;
    established_thread = (unsigned long)id;
    __c11_atomic_store(&state, 2, __ATOMIC_RELEASE);
    return 0;
}
int aether_utc_read(struct timespec *out)
{
    if (!out)
        return EINVAL;
    if (__c11_atomic_load(&state, __ATOMIC_ACQUIRE) != 2)
        return ENODATA;
    long now = call(0x2800f, 0, 0);
    if (now < 0)
        return (int)-now;
    return aether_utc_project(&shared, (uint64_t)now, out);
}
int aether_utc_close(void)
{
    long id = call(0x28007, 0, 0);
    if (id < 0)
        return (int)-id;
    if (__c11_atomic_load(&state, __ATOMIC_ACQUIRE) != 2)
        return ENODATA;
    if ((unsigned long)id != established_thread)
        return EPERM;
    if (aether_runtime_live() != 1)
        return EBUSY;
    __c11_atomic_store(&state, 3, __ATOMIC_RELEASE);
    return 0;
}
