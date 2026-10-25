/* SPDX-License-Identifier: BSD-2-Clause */
#include "runtime.h"
#include <errno.h>
#include <pthread.h>
#include <stdint.h>

static _Thread_local volatile unsigned cookie = 19;
static void *worker(void *unused)
{
    (void)unused;
    if (cookie != 19 || errno)
        return (void *)801;
    cookie = 41;
    errno = 73;
    return 0;
}
int main(void)
{
    if (aether_runtime_init() || aether_runtime_live() != 1 ||
        aether_runtime_admissions() != 1)
        return 800;
    for (unsigned cycle = 0; cycle < 511; ++cycle) {
        pthread_t child;
        void *result = (void *)1;
        if (pthread_create(&child, 0, worker, 0))
            return 802;
        if (pthread_join(child, &result) || result)
            return result ? (int)(uintptr_t)result : 803;
        if (aether_runtime_live() != 1 ||
            aether_runtime_admissions() != cycle + 2 || cookie != 19)
            return 804;
    }
    pthread_t sentinel = (pthread_t)0x1234;
    if (pthread_create(&sentinel, 0, worker, 0) != EAGAIN ||
        sentinel != (pthread_t)0x1234 || aether_runtime_live() != 1 ||
        aether_runtime_admissions() != 512)
        return 805;
    if (aether_runtime_finish() || aether_runtime_live() ||
        aether_runtime_admissions() != 512)
        return 806;
    return 0;
}
