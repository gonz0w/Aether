/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_UTC_H
#define AETHER_UTC_H
#include <stdint.h>
#include <time.h>
/* Explicit developer profile selection, never a source trust assertion. */
#define AETHER_UTC_Q35_RTC_UNAUTHENTICATED 1U
struct aether_rtc_sample {
    uint32_t version, bytes, source, flags;
    uint64_t before, after;
    unsigned char raw[10], reserved[22];
};
struct aether_utc_anchor {
    int64_t seconds;
    uint64_t monotonic_ns, read_uncertainty_ns;
};
/* Pure checked conversion/projection; positive errno, output unchanged on
 * error. */
int aether_utc_decode(const struct aether_rtc_sample *sample, unsigned policy,
                      struct aether_utc_anchor *out);
int aether_utc_project(const struct aether_utc_anchor *anchor, uint64_t now,
                       struct timespec *out);
/* Serialized initial thread only, after runtime init and before app creation.
 * One establishment per address-space lifetime; close after app joins. Borrowed
 * pointers must designate valid in-process objects. No adjustment or reset API.
 */
int aether_utc_establish(unsigned policy);
int aether_utc_read(struct timespec *out);
int aether_utc_close(void);
#endif
