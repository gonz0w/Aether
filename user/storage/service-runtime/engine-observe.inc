/* SPDX-License-Identifier: BSD-2-Clause */
/* Private fixed-width observations, read by the bounded supervisor. They are
 * test results, not a service protocol. All providers keep their existing
 * grants.
 */
#include <errno.h>
#include <stdint.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>
extern uint64_t aether_zfs_granted_pages(void);
extern uint64_t aether_zfs_free_pages(void);

static void engine_observe(unsigned char phase)
{
    uint64_t total = aether_zfs_granted_pages();
    uint64_t free = aether_zfs_free_pages();
    unsigned live = aether_runtime_live();
    unsigned admissions = aether_runtime_admissions();
    if (total != 8192 || free > total || live > 82 || admissions > 512)
        _Exit(227);
    unsigned char row[8] = {phase, live,      admissions, admissions >> 8,
                            free,  free >> 8, total,      total >> 8};
    /* The admitted stdout operation is bounded, and short writes stay explicit.
     */
    size_t offset = 0;
    while (offset < sizeof(row)) {
        ssize_t count = write(1, row + offset, sizeof(row) - offset);
        if (count <= 0 || (size_t)count > sizeof(row) - offset)
            _Exit(227);
        offset += (size_t)count;
    }
}

#ifndef ENGINE_SKIP_FINISH
static int engine_finish(void)
{
    struct timespec deadline, current;
    if (clock_gettime(CLOCK_MONOTONIC, &deadline))
        return EIO;
    deadline.tv_sec += 2;
    for (;;) {
        int error = aether_runtime_finish();
        if (error != EBUSY)
            return error;
        if (clock_gettime(CLOCK_MONOTONIC, &current))
            return EIO;
        if (current.tv_sec > deadline.tv_sec ||
            (current.tv_sec == deadline.tv_sec &&
             current.tv_nsec >= deadline.tv_nsec))
            return ETIMEDOUT;
        struct timespec pause = {0, 1000000};
        if (nanosleep(&pause, NULL))
            return EIO;
    }
}
#endif
