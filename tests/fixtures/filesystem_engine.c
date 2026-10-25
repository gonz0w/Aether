/* SPDX-License-Identifier: BSD-2-Clause */
/* Execute the actual lifecycle. Only external providers and scalar trap vary.
 */
#include <assert.h>
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "runtime.h"
#include "startup.h"
#include "filesystem-engine.h"
static int fault, step, initialized, finished, service_error, helper_wait,
    finish_wait, scenario, volume_pending, utc_pending, clock_calls;
static int point(int expected)
{
    if (++step != expected) {
        fprintf(stderr, "ENGINE oracle94 step %d expected %d\n", step,
                expected);
        exit(94);
    }
    return fault == expected ? EIO : 0;
}
#define CHECK(x)                                                               \
    do {                                                                       \
        if (!(x)) {                                                            \
            fprintf(stderr, "ENGINE oracle94 line %d\n", __LINE__);            \
            exit(94);                                                          \
        }                                                                      \
    } while (0)
int aether_runtime_init(void)
{
    int e = point(1);
    initialized = !e;
    return e;
}
unsigned aether_runtime_live(void)
{
    return finished ? 0 : helper_wait ? 2 : 1;
}
unsigned aether_runtime_admissions(void) { return 1; }
int aether_zfs_startup_bind(const struct aether_zfs_startup *s)
{
    CHECK(initialized && s->version == 1 && s->cache_policy == 1);
    return point(2);
}
int aether_zfs_volume_bind(uint64_t grant)
{
    CHECK(grant == 0xf101);
    if (volume_pending) {
        --volume_pending;
        return EACCES;
    }
    return point(3);
}
int aether_utc_establish(unsigned policy)
{
    CHECK(policy == 1);
    if (utc_pending) {
        --utc_pending;
        return EAGAIN;
    }
    return point(4);
}
void kernel_init(int mode)
{
    CHECK(mode == 3);
    CHECK(!point(5));
}
void aether_zpl_accounting_init(void) { CHECK(!point(6)); }
int aether_pool_prepare(void) { return point(7); }
int aether_fs_engine_import(struct aether_fs_launch_state *out)
{
    int e = point(8);
    if (!e)
        out->phases |= AETHER_FS_IMPORT | AETHER_FS_SERVICE |
                       AETHER_FS_SPA_CLOSED | AETHER_FS_EXPORTED;
    return e ? e : service_error;
}
void kernel_fini(void)
{
    CHECK(!point(9));
    if (scenario == 28)
        helper_wait = 2;
}
int host_block_close(uint64_t grant)
{
    CHECK(grant == 0xf101 && !helper_wait);
    return point(10);
}
int aether_utc_close(void) { return point(11); }
int aether_runtime_finish(void)
{
    if (finish_wait) {
        --finish_wait;
        return EBUSY;
    }
    int e = point(12);
    finished = !e;
    return e;
}
uint64_t aether_zfs_granted_pages(void) { return 8192; }
uint64_t aether_zfs_free_pages(void) { return 4096; }
static int fake_clock(clockid_t id, struct timespec *t)
{
    CHECK(id == CLOCK_MONOTONIC);
    t->tv_sec = scenario == 26 ? ++clock_calls : 1;
    t->tv_nsec = 0;
    return 0;
}
static int fake_sleep(const struct timespec *a, struct timespec *b)
{
    CHECK(a->tv_nsec == 1000000 && !b);
    helper_wait = 0;
    return 0;
}
#define AETHER_FS_HOST_BLOCK_CLOSE host_block_close
#define clock_gettime fake_clock
#define nanosleep fake_sleep
#include "engine-under-test.inc"
int main(int argc, char **argv)
{
    CHECK(argc == 2);
    fault = scenario = atoi(argv[1]);
    if (scenario >= 23) {
        fault = 0;
        volume_pending = scenario == 23 ? 1 : scenario == 26 ? 20 : 0;
        utc_pending = scenario == 24 ? 2 : scenario == 25 ? 16 : 0;
    }
    if (fault == 20) {
        fault = 0;
        service_error = EPIPE;
    }
    if (fault == 21) {
        fault = 0;
        finish_wait = 2;
    }
    if (fault == 22) {
        fault = 0;
        helper_wait = 0;
    }
    struct aether_fs_launch_state s = {.version = 1, .bytes = sizeof(s)};
    CHECK(aether_fs_engine_run(0, &s) == EINVAL && step == 0);
    CHECK(aether_fs_engine_run(0xf101, NULL) == EINVAL && step == 0);
    int error = aether_fs_engine_run(0xf101, &s);
    if (scenario == 25 || scenario == 26) {
        int expected = scenario == 25 ? EAGAIN : ETIMEDOUT;
        CHECK(error == expected && s.engine_error == expected);
        CHECK(step == (scenario == 25 ? 3 : 2));
        CHECK(s.phases == (scenario == 25 ? 3 : 1));
    } else if (fault) {
        CHECK(error == EIO && s.engine_error == EIO && step == fault);
        unsigned required = fault == 1                 ? 0
                            : fault == 2 || fault == 3 ? 1
                            : fault == 4               ? 3
                            : fault == 7 || fault == 8 ? 15
                            : fault == 10              ? 1023
                            : fault == 11              ? 2047
                                                       : 4095;
        CHECK(s.phases == required);
    } else {
        CHECK(step == 12 && error == service_error && s.engine_error == 0);
        CHECK(s.phases == AETHER_FS_FINISHED && finished);
    }
    struct aether_fs_launch_state next = {.version = 1, .bytes = sizeof(next)};
    CHECK(aether_fs_engine_run(0xf101, &next) == EALREADY);
    CHECK(next.phases == 0 && next.engine_error == 0);
    return 0;
}
