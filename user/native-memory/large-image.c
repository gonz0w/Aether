/* SPDX-License-Identifier: BSD-2-Clause */
#include "adapter.h"
#include <stdint.h>
#include <sys/auxv.h>
#include <sys/mman.h>
#include <unistd.h>

static volatile unsigned char initialized[2 * 1024 * 1024] = {
    [0] = 0x35, [2 * 1024 * 1024 - 1] = 0xa7};
static volatile unsigned char zeroed[4 * 1024 * 1024];
static _Thread_local volatile unsigned tls_value = 17;
#define CHECK(condition, code)                                                 \
    do {                                                                       \
        if (!(condition))                                                      \
            return (code);                                                     \
    } while (0)

int main(int argc, char **argv)
{
    CHECK(argc == 2, 160);
    unsigned instance = argv[0][11] - '0';
    for (size_t i = 0; i < sizeof(initialized); i++) {
        unsigned char expected = i == 0                         ? 0x35
                                 : i == sizeof(initialized) - 1 ? 0xa7
                                                                : 0;
        CHECK(initialized[i] == expected, 161);
        initialized[i] = (unsigned char)(instance + i);
    }
    for (size_t i = 0; i < sizeof(zeroed); i++) {
        CHECK(zeroed[i] == 0, 162);
        zeroed[i] = (unsigned char)(instance + i / 4096);
    }
    unsigned long cap = getauxval(0xa000);
    long free_pages = memtrap(0x22000, cap, 0, 0, 0);
    CHECK(free_pages > 64 && free_pages < 512, 163);
    volatile unsigned char *held = mmap(0, (size_t)free_pages * 4096, 3,
                                        MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    CHECK(held != MAP_FAILED, 164);
    for (size_t i = 0; i < (size_t)free_pages * 4096; i++) {
        CHECK(held[i] == 0, 165);
        held[i] = (unsigned char)(instance + 73);
    }
    CHECK(memtrap(0x22000, cap, 0, 0, 0) == 0, 166);
#ifdef STOP_LIVE
    if (instance == 1 && memtrap(0x20005, 0, 0, 0, 0) == 1) {
        CHECK(mprotect((void *)(held + 4096), 4096, PROT_READ) == 0, 167);
        CHECK(mprotect((void *)(held + 8192), 4096, PROT_NONE) == 0, 168);
        CHECK(memtrap(0x20004, 0, 0, 0, 0) == 0, 169);
        for (;;)
            memtrap(0x1fffe, 0, 0, 0, 0);
    }
#endif
    CHECK(munmap((void *)held, (size_t)free_pages * 4096) == 0, 170);
    CHECK(tls_value == 17, 171);
    tls_value = instance;
    for (unsigned i = 0; i < 64; i++) {
        memtrap(0x1fffe, 0, 0, 0, 0);
        CHECK(tls_value == instance, 172);
    }
    const char text[] = "AETHER MUSL NATIVE PASS\n";
    for (size_t i = 0; i < sizeof(text) - 1;) {
        ssize_t n = write(1, text + i, sizeof(text) - 1 - i);
        CHECK(n > 0, 173);
        i += (size_t)n;
    }
    return 0;
}
