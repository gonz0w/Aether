/* SPDX-License-Identifier: BSD-2-Clause */
#include "utc.h"
#include <assert.h>
#include <errno.h>
#include <limits.h>
#include <string.h>
#include "calendar-fixtures.h"
static unsigned char encode(unsigned x, int binary)
{
    return (unsigned char)(binary ? x : (x / 10 * 16 + x % 10));
}
static struct aether_rtc_sample sample(unsigned y, unsigned m, unsigned d,
                                       unsigned h, unsigned mode)
{
    int binary = !!(mode & 4U);
    unsigned hour = h;
    if (!(mode & 2U))
        hour = h % 12 ? h % 12 : 12;
    struct aether_rtc_sample s = {1, 64, 1, 0, 100, 200, {0}, {0}};
    s.raw[0] = encode(59, binary);
    s.raw[1] = encode(58, binary);
    s.raw[2] = encode(hour, binary);
    if (!(mode & 2U) && h >= 12)
        s.raw[2] |= 0x80;
    s.raw[3] = encode(d, binary);
    s.raw[4] = encode(m, binary);
    s.raw[5] = encode(y % 100, binary);
    s.raw[6] = encode(y / 100, binary);
    s.raw[7] = 0x26;
    s.raw[8] = (unsigned char)mode;
    s.raw[9] = 0x80;
    return s;
}
static void rejected(struct aether_rtc_sample s, unsigned policy, int error)
{
    struct aether_utc_anchor out = {17, 19, 23}, before = out;
    assert(aether_utc_decode(&s, policy, &out) == error);
    assert(!memcmp(&out, &before, sizeof(out)));
}
int main(void)
{
    for (unsigned i = 0; i < sizeof(fixtures) / sizeof(fixtures[0]); ++i) {
        const struct fixture *f = &fixtures[i];
        for (unsigned mode = 0; mode <= 6; mode += 2) {
            struct aether_rtc_sample s = sample(f->y, f->m, f->d, f->h, mode);
            struct aether_utc_anchor out;
            assert(!aether_utc_decode(&s, 1, &out));
            assert(out.seconds == f->seconds && out.monotonic_ns == 200 &&
                   out.read_uncertainty_ns == 100);
            struct timespec t = {7, 11};
            assert(!aether_utc_project(&out, 2000000250, &t));
            assert(t.tv_sec == f->seconds + 2 && t.tv_nsec == 50);
        }
    }
    struct aether_rtc_sample good = sample(2000, 2, 29, 0, 2), bad;
    rejected(good, 0, ENOTSUP);
    rejected(sample(1900, 2, 29, 0, 2), 1, EINVAL);
    rejected(sample(2100, 2, 29, 0, 2), 1, EINVAL);
    rejected(sample(1969, 12, 31, 0, 2), 1, EINVAL);
    rejected(sample(2000, 4, 31, 0, 2), 1, EINVAL);
    for (unsigned field = 0; field < 7; ++field) {
        bad = good;
        bad.raw[field] = 0xfa;
        rejected(bad, 1, EINVAL);
    }
    for (unsigned field = 0; field < 22; ++field) {
        bad = good;
        bad.reserved[field] = 1;
        rejected(bad, 1, EINVAL);
    }
    for (unsigned field = 0; field < 4; ++field) {
        bad = good;
        switch (field) {
        case 0:
            bad.version = 2;
            break;
        case 1:
            bad.bytes = 63;
            break;
        case 2:
            bad.source = 2;
            break;
        default:
            bad.flags = 1;
        }
        rejected(bad, 1, EINVAL);
    }
    for (unsigned mode = 0; mode < 4; ++mode) {
        bad = good;
        switch (mode) {
        case 0:
            bad.raw[7] |= 0x80;
            break;
        case 1:
            bad.raw[7] = 0x66;
            break;
        case 2:
            bad.raw[8] |= 0x80;
            break;
        default:
            bad.raw[9] = 0;
        }
        rejected(bad, 1, ENOSYS);
    }
    bad = good;
    bad.raw[2] |= 0x80;
    rejected(bad, 1, EINVAL);
    bad = good;
    bad.raw[8] = 0;
    bad.raw[2] = 0;
    rejected(bad, 1, EINVAL);
    bad = good;
    bad.after = 99;
    rejected(bad, 1, EOVERFLOW);
    bad = good;
    bad.after = (uint64_t)INT64_MAX + 1;
    rejected(bad, 1, EOVERFLOW);
    bad = good;
    bad.after = 2000101;
    rejected(bad, 1, EAGAIN);
    struct aether_utc_anchor a = {INT64_MAX, 200, 100};
    struct timespec t = {7, 11}, previous = t;
    assert(aether_utc_project(&a, 1000000200, &t) == EOVERFLOW);
    assert(!memcmp(&t, &previous, sizeof(t)));
    assert(aether_utc_project(&a, 199, &t) == EIO);
    assert(!memcmp(&t, &previous, sizeof(t)));
    assert(aether_utc_project(&a, (uint64_t)INT64_MAX + 1, &t) == EOVERFLOW);
    assert(!memcmp(&t, &previous, sizeof(t)));
    return 0;
}
