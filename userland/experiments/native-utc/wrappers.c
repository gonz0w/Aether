/* SPDX-License-Identifier: BSD-2-Clause */
#include <errno.h>
#include <sys/time.h>
#include <time.h>
/* Unlike the pinned upstream bodies, propagate failed clock observation before
 * publishing any value. Timezone interpretation is not part of this profile. */
time_t time(time_t *out)
{
    struct timespec value;
    if (clock_gettime(CLOCK_REALTIME, &value))
        return (time_t)-1;
    if (out)
        *out = value.tv_sec;
    return value.tv_sec;
}
int gettimeofday(struct timeval *restrict out, void *restrict timezone)
{
    if (timezone) {
        errno = ENOTSUP;
        return -1;
    }
    if (!out) {
        errno = EINVAL;
        return -1;
    }
    struct timespec value;
    if (clock_gettime(CLOCK_REALTIME, &value))
        return -1;
    struct timeval result = {value.tv_sec, value.tv_nsec / 1000};
    *out = result;
    return 0;
}
