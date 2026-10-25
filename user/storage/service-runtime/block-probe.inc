/* SPDX-License-Identifier: BSD-2-Clause */
/* Private region/runtime composition. No file/path or automatic regrant API. */
#include <string.h>
static int volume_bound;
static _Atomic unsigned volume_full_read;
static long volume_trap(unsigned long op, void *buffer, unsigned long sector,
                        unsigned long bytes)
{
    unsigned long argument = (uintptr_t)buffer;
    if (op == 0x27000 || op == 0x27001) {
        argument = sector;
        sector = (uintptr_t)buffer;
    }
    register unsigned long r10 __asm__("r10") = bytes;
    register unsigned long r8 __asm__("r8") = 0, r9 __asm__("r9") = 0;
    __asm__ volatile("int $0x81"
                     : "+a"(op), "+d"(sector), "+r"(r10), "+r"(r8), "+r"(r9)
                     : "D"(0xf101UL), "S"(argument)
                     : "rcx", "r11", "memory", "cc");
    return (long)op;
}
static int volume_data(unsigned char *bytes, unsigned base)
{
    for (unsigned i = 0; i < 512; ++i)
        if (bytes[i] != (unsigned char)(i * 17 + base))
            return 0;
    return 1;
}
static int volume_worker_probe(void)
{
    unsigned char bytes[512];
    if (!volume_bound)
        return volume_trap(0x27000, bytes, 0, 512) == -EACCES ? 0 : 843;
    if (volume_trap(0x27000, bytes, 0, 512) != 512 ||
        !volume_data(bytes, BLOCK_READONLY ? 3 : 91))
        return 843;
    return 0;
}
static int volume_full_probe(void)
{
    /* One representative I/O while the full cohort retires; this synchronous
     * transport fixture does not measure multi-worker disk throughput. */
    return volume_full_read++ == 0 ? volume_worker_probe() : 0;
}
static int volume_start_probe(void)
{
    uint64_t info[4] = {17, 19, 23, 29};
    /* Exact route of this private fixture, never a derived authorization. */
    if (getauxval(0xa001) != 0x50000101UL) {
        CHECK(volume_trap(0x27006, info, 32, 0) == -EACCES && info[0] == 17 &&
                  info[1] == 19 && info[2] == 23 && info[3] == 29 &&
                  volume_trap(0x27002, 0, 0, 0) == -EACCES,
              842);
        return 0;
    }
    struct timespec until;
    CHECK(!clock_gettime(CLOCK_MONOTONIC, &until), 841);
    ++until.tv_sec;
    long result;
    do {
        result = volume_trap(0x27006, info, 32, 0);
        if (result == -EACCES) {
            struct timespec current, pause = {0, 1000000};
            CHECK(!clock_gettime(CLOCK_MONOTONIC, &current) &&
                      (current.tv_sec < until.tv_sec ||
                       (current.tv_sec == until.tv_sec &&
                        current.tv_nsec < until.tv_nsec)) &&
                      !nanosleep(&pause, 0),
                  841);
        }
    } while (result == -EACCES);
    CHECK(!result && info[0] == 512 && info[1] == 16384 &&
              info[2] == (BLOCK_READONLY ? 1 : 7) && !info[3],
          841);
    unsigned char bytes[512];
    CHECK(volume_trap(0x27000, bytes, 0, 512) == 512 &&
              volume_data(bytes, BLOCK_VERIFY ? 91 : 3),
          840);
    if (BLOCK_READONLY) {
        CHECK(volume_trap(0x27001, bytes, 0, 512) == -EACCES &&
                  volume_trap(0x27002, 0, 0, 0) == -EACCES,
              842);
    } else if (!BLOCK_VERIFY) {
        for (unsigned i = 0; i < 512; ++i)
            bytes[i] = (unsigned char)(i * 17 + 91);
        CHECK(volume_trap(0x27001, bytes, 0, 512) == 512 &&
                  !volume_trap(0x27002, 0, 0, 0),
              842);
    }
    volume_bound = 1;
    return volume_worker_probe();
}
static int volume_finish_probe(void)
{
    if (!volume_bound)
        return volume_worker_probe();
    CHECK(!volume_trap(0x27004, 0, 0, 0), 844);
    unsigned char bytes[512];
    CHECK(volume_trap(0x27000, bytes, 0, 512) == -EBADF &&
              volume_trap(0x27002, 0, 0, 0) == -EBADF,
          844);
    return 0;
}
