/* SPDX-License-Identifier: BSD-2-Clause */
/* Private source qualification only; never publishes CLOCK_REALTIME. */
#include <string.h>
#include <sys/mman.h>
struct rtc_sample {
    uint32_t version, bytes, source, flags;
    uint64_t before, after;
    unsigned char raw[10], reserved[22];
};
_Static_assert(sizeof(struct rtc_sample) == 64, "RTC observation64");
static long rtc_trap(unsigned long cap, void *out, unsigned long bytes,
                     unsigned long extra)
{
    unsigned long op = 0x28011;
    register unsigned long r10 __asm__("r10") = extra;
    register unsigned long r8 __asm__("r8") = 0, r9 __asm__("r9") = 0;
    __asm__ volatile("int $0x81"
                     : "+a"(op), "+r"(r10), "+r"(r8), "+r"(r9), "+d"(bytes)
                     : "D"(cap), "S"(out)
                     : "rcx", "r11", "memory", "cc");
    return (long)op;
}
static int rtc_unchanged(unsigned long cap, struct rtc_sample *out,
                         unsigned long bytes, unsigned long extra,
                         long expected)
{
    struct rtc_sample previous = *out;
    return rtc_trap(cap, out, bytes, extra) == expected &&
           !memcmp(out, &previous, sizeof(*out));
}
static int rtc_probe(void)
{
    unsigned long cap = getauxval(0xa001);
    struct rtc_sample value;
    memset(&value, 0x5a, sizeof(value));
    CHECK(cap && rtc_unchanged(0, &value, 64, 0, -13) &&
              rtc_unchanged(cap ^ 1, &value, 64, 0, -13) &&
              rtc_unchanged(cap ^ 0x100, &value, 64, 0, -13),
          832);
    struct timespec deadline;
    CHECK(!clock_gettime(CLOCK_MONOTONIC, &deadline), 833);
    ++deadline.tv_sec;
    struct rtc_sample original = value;
    long result;
    do {
        result = rtc_trap(cap, &value, 64, 0);
        if (result)
            CHECK(!memcmp(&value, &original, sizeof(value)), 839);
        if (result == -EAGAIN) {
            struct timespec now, pause = {0, 1000000};
            CHECK(!clock_gettime(CLOCK_MONOTONIC, &now) &&
                      (now.tv_sec < deadline.tv_sec ||
                       (now.tv_sec == deadline.tv_sec &&
                        now.tv_nsec < deadline.tv_nsec)) &&
                      !nanosleep(&pause, 0),
                  833);
        }
    } while (result == -EAGAIN);
    CHECK(!result, result == -ENOSYS ? 831 : 839);
    unsigned char zero[22] = {0};
    CHECK(value.version == 1 && value.bytes == 64 && value.source == 1 &&
              !value.flags && value.after >= value.before &&
              value.after - value.before <= 2000000 &&
              !memcmp(value.reserved, zero, sizeof(zero)),
          834);
    /* q35/OVMF qualification uses explicit BCD 24h noon dates; mode handling
     * and full calendar interpretation are the future userland owner's work. */
    CHECK(value.raw[8] == 2 && (value.raw[7] & 0xf0) == 0x20 &&
              (value.raw[9] & 0x80) && value.raw[0] <= 0x45 &&
              (value.raw[0] & 15) <= 9 && value.raw[1] == 0x34 &&
              value.raw[2] == 0x12 && value.raw[3] == RTC_DAY &&
              value.raw[4] == RTC_MONTH && value.raw[5] == RTC_YEAR &&
              value.raw[6] == 0x20,
          835);
    CHECK(rtc_unchanged(cap, &value, 63, 0, -22) &&
              rtc_unchanged(cap, &value, 64, 1, -22) &&
              rtc_trap(cap, (void *)((uintptr_t)&value + 1), 64, 0) == -22 &&
              rtc_trap(cap, (void *)(UINTPTR_MAX & ~7UL), 64, 0) == -14,
          836);
    unsigned char *pages = mmap(0, 8192, PROT_READ | PROT_WRITE,
                                MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    CHECK(pages != MAP_FAILED, 837);
    memset(pages, 0x5a, 8192);
    CHECK(!mprotect(pages + 4096, 4096, PROT_NONE) &&
              rtc_trap(cap, pages + 4064, 64, 0) == -14 &&
              !mprotect(pages + 4096, 4096, PROT_READ),
          837);
    CHECK(rtc_trap(cap, pages + 4064, 64, 0) == -14 &&
              rtc_trap(cap, pages + 4096, 64, 0) == -14,
          837);
    for (unsigned i = 0; i < 8192; ++i)
        CHECK(pages[i] == 0x5a, 838);
    CHECK(!munmap(pages, 8192), 838);
    return 0;
}
