/* SPDX-License-Identifier: BSD-2-Clause */
/* Fixed provisioned native engine, original OpenZFS lifecycle and providers.
 * This is not the test importer: no file-layout oracle or expected-error arm.
 */
#include "runtime.h"
#include "startup-fixture.h"
#include "utc.h"
#include "volume.h"
#include "filesystem-engine.h"
#include <errno.h>
#include <limits.h>
#include <time.h>
extern void kernel_init(int);
extern void kernel_fini(void);
extern void aether_zpl_accounting_init(void);
extern int aether_pool_prepare(void);
extern int aether_fs_engine_import(struct aether_fs_launch_state *);
#include "engine-observe.inc"
/* The native static-ELF startup contract requires PT_TLS. Keep a real initial-
 * thread guard, initialized by musl, and check it again after helper joins. */
static _Thread_local volatile unsigned owner_tls = 17;
static int consumed;
void aether_engine_utc_phase(unsigned char phase) { engine_observe(phase); }

static int wait_helpers(void)
{
    struct timespec deadline, now;
    if (clock_gettime(CLOCK_MONOTONIC, &deadline))
        return EIO;
    if (deadline.tv_sec > INT64_MAX - 2)
        return EOVERFLOW;
    deadline.tv_sec += 2;
    while (aether_runtime_live() != 1) {
        if (!aether_runtime_live() || aether_runtime_live() > 82)
            return EIO;
        struct timespec pause = {0, 1000000};
        if (clock_gettime(CLOCK_MONOTONIC, &now) ||
            now.tv_sec > deadline.tv_sec ||
            (now.tv_sec == deadline.tv_sec && now.tv_nsec >= deadline.tv_nsec))
            return ETIMEDOUT;
        if (nanosleep(&pause, NULL))
            return EIO;
    }
    return 0;
}
static int bind_volume(uint64_t grant)
{
    /* The supervisor publishes the already-admitted region. EACCES while
     * waiting for that publication has no I/O effect; no failed I/O is
     * replayed. */
    struct timespec deadline, now;
    if (clock_gettime(CLOCK_MONOTONIC, &deadline))
        return EIO;
    if (deadline.tv_sec == INT64_MAX)
        return EOVERFLOW;
    ++deadline.tv_sec;
    for (;;) {
        int error = aether_zfs_volume_bind(grant);
        if (error != EACCES)
            return error;
        if (clock_gettime(CLOCK_MONOTONIC, &now) ||
            now.tv_sec > deadline.tv_sec ||
            (now.tv_sec == deadline.tv_sec && now.tv_nsec >= deadline.tv_nsec))
            return ETIMEDOUT;
        struct timespec pause = {0, 1000000};
        if (nanosleep(&pause, NULL))
            return EIO;
    }
}
#ifndef AETHER_FS_HOST_BLOCK_CLOSE
static int close_volume(uint64_t grant)
{
    uint64_t op = 0x27004, a = 0, b = 0;
    register uint64_t r10 __asm__("r10") = 0;
    register uint64_t r8 __asm__("r8") = 0, r9 __asm__("r9") = 0;
    /* Existing scalar owner-bound block close; all engine users have joined. */
    __asm__ volatile("int $0x81"
                     : "+a"(op), "+D"(grant), "+S"(a), "+d"(b), "+r"(r10),
                       "+r"(r8), "+r"(r9)
                     :
                     : "rcx", "r11", "memory", "cc");
    int64_t status = (int64_t)op;
    return status == 0                        ? 0
           : status < 0 && status >= -INT_MAX ? (int)-status
                                              : EIO;
}
#else
#define close_volume AETHER_FS_HOST_BLOCK_CLOSE
#endif
int aether_fs_engine_run(uint64_t grant, struct aether_fs_launch_state *out)
{
    if (!out || out->version != 1 || out->bytes != sizeof(*out) ||
        out->phases || out->engine_error || !grant)
        return EINVAL;
    if (consumed)
        return EALREADY;
    if (owner_tls != 17)
        return EIO;
    consumed = 1; /* Never rearm, including a failed startup or shutdown. */
    int error = aether_runtime_init();
    if (error)
        goto failed;
    out->phases |= AETHER_FS_RUNTIME;
    if (aether_runtime_live() != 1 || aether_runtime_admissions() != 1) {
        error = EIO;
        goto failed;
    }
    error = aether_zfs_startup_bind(&startup_fixture);
    if (!error)
        error = bind_volume(grant);
    if (error)
        goto failed;
    out->phases |= AETHER_FS_BLOCK;
    error = EAGAIN;
    for (unsigned attempt = 0; attempt < 16 && error == EAGAIN; ++attempt) {
        error = aether_utc_establish(AETHER_UTC_Q35_RTC_UNAUTHENTICATED);
        if (error == EAGAIN) {
            struct timespec pause = {0, 1000000};
            if (nanosleep(&pause, NULL)) {
                error = EIO;
                goto failed;
            }
        }
    }
    if (error)
        goto failed;
    out->phases |= AETHER_FS_UTC;
    kernel_init(3); /* Original SPA_MODE_READ | SPA_MODE_WRITE. */
    out->phases |= AETHER_FS_KERNEL;
    aether_zpl_accounting_init();
    error = aether_pool_prepare();
    if (error)
        goto failed;
    int service_error = aether_fs_engine_import(out);
    if (!(out->phases & AETHER_FS_EXPORTED)) {
        error = service_error ? service_error : EIO;
        goto failed;
    }
    /* Import helper preserves service failure separately after safe export. */
    kernel_fini();
    out->phases |= AETHER_FS_KERNEL_STOPPED;
    error = wait_helpers();
    if (error)
        goto failed;
    out->phases |= AETHER_FS_HELPERS_JOINED;
    error = close_volume(grant);
    if (error)
        goto failed;
    out->phases |= AETHER_FS_BLOCK_CLOSED;
    error = aether_utc_close();
    if (error)
        goto failed;
    out->phases |= AETHER_FS_UTC_CLOSED;
    error = engine_finish();
    if (error)
        goto failed;
    if (aether_runtime_live() || owner_tls != 17) {
        error = EIO;
        goto failed;
    }
    out->phases |= AETHER_FS_RUNTIME_STOPPED;
    return service_error;
failed:
    out->engine_error = error > 0 ? error : EIO;
    return (int)out->engine_error;
}
