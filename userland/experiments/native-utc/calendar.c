/* SPDX-License-Identifier: BSD-2-Clause */
#include "utc.h"
#include <errno.h>
#include <limits.h>

_Static_assert(sizeof(struct aether_rtc_sample) == 64, "RTC record64");
_Static_assert(sizeof(time_t) == 8, "private signed64 time ABI");
static int number(unsigned raw, int binary)
{
    if (binary)
        return (int)raw;
    if ((raw & 15U) > 9U || (raw >> 4) > 9U)
        return -1;
    return (int)((raw >> 4) * 10U + (raw & 15U));
}
static int leap(int year)
{
    return year % 4 == 0 && (year % 100 != 0 || year % 400 == 0);
}
int aether_utc_decode(const struct aether_rtc_sample *s, unsigned policy,
                      struct aether_utc_anchor *out)
{
    if (!s || !out)
        return EINVAL;
    if (policy != AETHER_UTC_Q35_RTC_UNAUTHENTICATED)
        return ENOTSUP;
    if (s->version != 1 || s->bytes != 64 || s->source != 1 || s->flags)
        return EINVAL;
    for (unsigned i = 0; i < sizeof(s->reserved); ++i)
        if (s->reserved[i])
            return EINVAL;
    if (s->after < s->before || s->after > INT64_MAX)
        return EOVERFLOW;
    if (s->after - s->before > 2000000)
        return EAGAIN;
    /* The divider must run, UIP and SET must be clear, battery valid. */
    if ((s->raw[7] & 0xf0U) != 0x20U || (s->raw[8] & 0x80U) ||
        !(s->raw[9] & 0x80U))
        return ENOSYS;
    int binary = !!(s->raw[8] & 4U);
    int second = number(s->raw[0], binary);
    int minute = number(s->raw[1], binary);
    int hour = number(s->raw[2] & 0x7fU, binary);
    int day = number(s->raw[3], binary);
    int month = number(s->raw[4], binary);
    int short_year = number(s->raw[5], binary);
    int century = number(s->raw[6], binary);
    if (second < 0 || second > 59 || minute < 0 || minute > 59 || hour < 0 ||
        short_year < 0 || short_year > 99 || century < 0 || century > 99)
        return EINVAL;
    if (s->raw[8] & 2U) {
        if ((s->raw[2] & 0x80U) || hour > 23)
            return EINVAL;
    } else {
        if (hour < 1 || hour > 12)
            return EINVAL;
        hour = hour % 12 + ((s->raw[2] & 0x80U) ? 12 : 0);
    }
    int year = century * 100 + short_year;
    if (year < 1970 || year > 9999 || month < 1 || month > 12 || day < 1)
        return EINVAL;
    static const unsigned char lengths[12] = {31, 28, 31, 30, 31, 30,
                                              31, 31, 30, 31, 30, 31};
    int maximum = lengths[month - 1] + (month == 2 && leap(year));
    if (day > maximum)
        return EINVAL;
    /* Bounded Gregorian arithmetic: at most8030 iterations and <3M days. */
    int64_t days = 0;
    for (int y = 1970; y < year; ++y)
        days += 365 + leap(y);
    for (int m = 1; m < month; ++m)
        days += lengths[m - 1] + (m == 2 && leap(year));
    days += day - 1;
    struct aether_utc_anchor value = {
        .seconds = days * 86400 + hour * 3600 + minute * 60 + second,
        .monotonic_ns = s->after,
        .read_uncertainty_ns = s->after - s->before};
    *out = value;
    return 0;
}
int aether_utc_project(const struct aether_utc_anchor *a, uint64_t now,
                       struct timespec *out)
{
    if (!a || !out || a->seconds < 0 || a->monotonic_ns > INT64_MAX ||
        a->read_uncertainty_ns > 2000000)
        return EINVAL;
    if (now > INT64_MAX)
        return EOVERFLOW;
    if (now < a->monotonic_ns)
        return EIO;
    uint64_t delta = now - a->monotonic_ns;
    uint64_t seconds = delta / 1000000000;
    if (seconds > (uint64_t)(INT64_MAX - a->seconds))
        return EOVERFLOW;
    struct timespec result = {(time_t)(a->seconds + (int64_t)seconds),
                              (long)(delta % 1000000000)};
    *out = result;
    return 0;
}
