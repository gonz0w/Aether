/* SPDX-License-Identifier: BSD-2-Clause */
/* Private actual taskq/Rust-volume lifetime witness. It does not replace ZIO
 * completion or define a storage-service queue. One borrowed request lives
 * through taskq_wait; file/buffer cleanup follows queue destruction. */
#include <sys/zfs_context.h>
#include <sys/zfs_file.h>
#include <sys/auxv.h>
#include "volume.h"
extern int taskq_now;
#define REQUIRE(ok)                                                            \
    do {                                                                       \
        if (!(ok))                                                             \
            return 846;                                                        \
    } while (0)
struct request {
    taskq_t *queue;
    zfs_file_t *file;
    pthread_t primary;
    int readonly, held, result;
    unsigned char bytes[512];
    pthread_mutex_t lock;
    pthread_cond_t wake;
    int entered, release;
};
static int revoked;
static struct aether_volume closed_view;
static long revoke(void)
{
    unsigned long op = 0x27004, second = 0;
    register unsigned long r10 __asm__("r10") = 0;
    register unsigned long r8 __asm__("r8") = 0, r9 __asm__("r9") = 0;
    __asm__ volatile("int $0x81"
                     : "+a"(op), "+d"(second), "+r"(r10), "+r"(r8), "+r"(r9)
                     : "D"(0xf101UL), "S"(0UL)
                     : "rcx", "r11", "memory", "cc");
    return (long)op;
}
static int work(struct request *r)
{
    REQUIRE(!pthread_equal(pthread_self(), r->primary) &&
            taskq_of_curthread() == r->queue);
    if (r->held) {
        REQUIRE(!pthread_mutex_lock(&r->lock));
        r->entered = 1;
        REQUIRE(!pthread_cond_signal(&r->wake));
        while (!r->release)
            REQUIRE(!pthread_cond_wait(&r->wake, &r->lock));
        REQUIRE(!pthread_mutex_unlock(&r->lock));
        ssize_t residual = -1;
        REQUIRE(zfs_file_pread(r->file, r->bytes, sizeof(r->bytes), 0,
                               &residual) == EBADF &&
                residual == sizeof(r->bytes));
        for (unsigned i = 0; i < sizeof(r->bytes); ++i)
            REQUIRE(r->bytes[i] == 29);
        return 0;
    }
    ssize_t residual = -1;
    REQUIRE(
        !zfs_file_pread(r->file, r->bytes, sizeof(r->bytes), 0, &residual) &&
        !residual);
    unsigned base = r->readonly ? 3 : 91;
    for (unsigned i = 0; i < sizeof(r->bytes); ++i)
        REQUIRE(r->bytes[i] == (unsigned char)(i * 17 + base));
    int error =
        zfs_file_pwrite(r->file, r->bytes, sizeof(r->bytes), 0, 9, &residual);
    REQUIRE(error == (r->readonly ? EACCES : 0) &&
            residual == (r->readonly ? 512 : 0));
    REQUIRE(zfs_file_fsync(r->file, O_SYNC | O_DSYNC) ==
            (r->readonly ? EACCES : 0));
    return 0;
}
static void callback(void *argument)
{
    struct request *r = argument;
    r->result = work(r);
}
static void forbidden(void *argument)
{
    (void)argument;
    _Exit(847);
}
int aether_volume_workers_probe(int readonly, int inline_control)
{
    if (getauxval(0xa001) != 0x50000101UL) {
        struct aether_volume unused;
        REQUIRE(aether_volume_bind(0xf101, &unused) == EACCES);
        return 0;
    }
    REQUIRE(!taskq_now && !aether_volume_bind(0xf101, &closed_view));
    zfs_file_t *file = NULL;
    REQUIRE(!zfs_file_open(AETHER_VOLUME_PATH, readonly ? O_RDONLY : O_RDWR, 0,
                           NULL, &file));
    taskq_t *queue =
        taskq_create("volume_probe", 1, minclsyspri, 1, 1, TASKQ_PREPOPULATE);
    REQUIRE(queue);
    struct request r = {.queue = queue,
                        .file = file,
                        .primary = pthread_self(),
                        .readonly = readonly,
                        .result = 846,
                        .lock = PTHREAD_MUTEX_INITIALIZER,
                        .wake = PTHREAD_COND_INITIALIZER};
    /* Named negative control: real dispatcher inlines, origin check must fail.
     * The failing owner exits before fini; no clean retirement is claimed. */
    if (inline_control)
        taskq_now = 1;
    REQUIRE(taskq_dispatch(queue, callback, &r, TQ_NOSLEEP) != TASKQID_INVALID);
    taskq_wait(queue);
    REQUIRE(!r.result);
    r.held = 1;
    r.result = 846;
    memset(r.bytes, 29, sizeof(r.bytes));
    REQUIRE(taskq_dispatch(queue, callback, &r, TQ_NOSLEEP) != TASKQID_INVALID);
    struct timespec until;
    REQUIRE(!clock_gettime(CLOCK_MONOTONIC, &until));
    ++until.tv_sec;
    for (;;) {
        REQUIRE(!pthread_mutex_lock(&r.lock));
        int entered = r.entered;
        REQUIRE(!pthread_mutex_unlock(&r.lock));
        if (entered)
            break;
        struct timespec current, pause = {0, 1000000};
        REQUIRE(!clock_gettime(CLOCK_MONOTONIC, &current) &&
                (current.tv_sec < until.tv_sec ||
                 (current.tv_sec == until.tv_sec &&
                  current.tv_nsec < until.tv_nsec)) &&
                !nanosleep(&pause, NULL));
    }
    /* NOSLEEP makes the single prepopulated entry an enforcing bound; upstream
     * maxalloc is only a throttle with SLEEP and may allocate extra entries. */
    REQUIRE(taskq_dispatch(queue, forbidden, NULL, TQ_NOSLEEP) ==
            TASKQID_INVALID);
    REQUIRE(!revoke());
    revoked = 1;
    REQUIRE(!pthread_mutex_lock(&r.lock));
    r.release = 1;
    REQUIRE(!pthread_cond_signal(&r.wake) && !pthread_mutex_unlock(&r.lock));
    taskq_wait(queue);
    REQUIRE(!r.result);
    taskq_destroy(queue);
    zfs_file_close(file);
    REQUIRE(!pthread_cond_destroy(&r.wake) && !pthread_mutex_destroy(&r.lock));
    REQUIRE(aether_volume_check(&closed_view) == EBADF);
    return 0;
}
int aether_volume_workers_finish(void)
{
    if (!revoked)
        return 0; /* Unbound replacement owner. */
    REQUIRE(aether_volume_check(&closed_view) == EBADF);
    zfs_file_t *file = NULL;
    REQUIRE(zfs_file_open(AETHER_VOLUME_PATH, O_RDONLY, 0, NULL, &file) ==
                EBADF &&
            !file);
    return 0;
}
