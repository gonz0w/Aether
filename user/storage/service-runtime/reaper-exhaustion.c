/* SPDX-License-Identifier: BSD-2-Clause */
/* Native lifetime admission exhaustion; real detached retirement owns reuse. */
#include "runtime.h"
#include <errno.h>
#include <pthread.h>
#include <stdint.h>
#include <stdlib.h>
#include <time.h>
static _Thread_local volatile unsigned cookie = 23;
static _Atomic unsigned done;
static uint64_t deadline;
#define REQUIRE(valid)                                                         \
    do {                                                                       \
        if (!(valid))                                                          \
            _Exit(1000 + __LINE__);                                            \
    } while (0)
static uint64_t now(void)
{
    struct timespec ts;
    REQUIRE(!clock_gettime(CLOCK_MONOTONIC, &ts) && ts.tv_sec >= 0 &&
            ts.tv_nsec >= 0 && ts.tv_nsec < 1000000000);
    return (uint64_t)ts.tv_sec * 1000000000 + ts.tv_nsec;
}
static void *worker(void *argument)
{
    REQUIRE(!argument && cookie == 23);
    cookie = 47;
    ++done;
    return NULL;
}
int main(void)
{
    REQUIRE(cookie == 23 && !aether_runtime_init());
    deadline = now() + 15000000000ULL;
    pthread_attr_t attr;
    REQUIRE(!pthread_attr_init(&attr) &&
            !pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_DETACHED));
    for (unsigned i = 0; i < 511; ++i) {
        pthread_t child;
        REQUIRE(!pthread_create(&child, &attr, worker, NULL));
        uint64_t progress = now() + 1000000000ULL;
        while (aether_runtime_live() != 1) {
            uint64_t elapsed = now();
            REQUIRE(elapsed < deadline && elapsed < progress);
            unsigned long op = 0x1fffe;
            __asm__ volatile("int $0x81"
                             : "+a"(op)
                             : "D"(0UL), "S"(0UL), "d"(0UL)
                             : "rcx", "r8", "r9", "r10", "r11", "memory", "cc");
        }
        REQUIRE(done == i + 1 && aether_runtime_admissions() == i + 2);
    }
    pthread_t sentinel = (pthread_t)0x1234;
    REQUIRE(pthread_create(&sentinel, &attr, worker, NULL) == EAGAIN &&
            sentinel == (pthread_t)0x1234 &&
            aether_runtime_admissions() == 512 && aether_runtime_live() == 1 &&
            done == 511 && cookie == 23);
    REQUIRE(!pthread_attr_destroy(&attr) && !aether_runtime_finish() &&
            !aether_runtime_live() && aether_runtime_admissions() == 512);
    return 0;
}
