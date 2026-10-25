/* SPDX-License-Identifier: BSD-2-Clause */
/* Trusted importer fixture only; the service consumes its own C context and
 * validated endpoint obligations. Preserve progress even when its reply fails.
 */
#include <sys/auxv.h>
#include "native-service.h"
_Static_assert(sizeof(struct aether_fs_service_result) == 72, "service result");
_Static_assert(offsetof(struct aether_fs_service_result, txg) == 48,
               "service progress");
#ifndef AETHER_FS_SERVICE_CASE
#define AETHER_FS_SERVICE_CASE 0
#endif
#ifndef AETHER_FS_SERVICE_LIFETIMES
#define AETHER_FS_SERVICE_LIFETIMES 0
#endif
#if AETHER_FS_SERVICE_LIFETIMES
#define FS_REQUESTS 39
#define FS_PARTIAL_REQUESTS 38
#define FS_CLOSES 9
#else
#define FS_REQUESTS 11
#define FS_PARTIAL_REQUESTS 10
#define FS_CLOSES 1
#endif
#if AETHER_FS_SERVICE_CASE == 3
/* This fixed fault arm is initial-thread-only. Original context destruction
 * precedes the injected one-way endpoint close. Outcomes never reset/rearm. */
static uint64_t fs_close_reader;
static unsigned fs_injected;
static int fs_injection_error;
extern void __real_aether_zpl_close(aether_zpl_view **);
#ifndef AETHER_FS_HOST_CLOSE
static int64_t fs_channel_close(uint64_t endpoint)
{
    uint64_t op = 0x24003, a = 0, b = 0;
    register uint64_t r10 __asm__("r10") = 0;
    register uint64_t r8 __asm__("r8") = 0, r9 __asm__("r9") = 0;
    /* Scalar close of this instance's retained endpoint, no pointers. */
    __asm__ volatile("int $0x81"
                     : "+a"(op), "+D"(endpoint), "+S"(a), "+d"(b), "+r"(r10),
                       "+r"(r8), "+r"(r9)
                     :
                     : "rcx", "r11", "memory", "cc");
    return (int64_t)op;
}
#else
#define fs_channel_close AETHER_FS_HOST_CLOSE
#endif
void __wrap_aether_zpl_close(aether_zpl_view **view)
{
    __real_aether_zpl_close(view);
    if (fs_close_reader) {
#if AETHER_FS_SERVICE_LIFETIMES
        /* Eight success-only cycle closes precede final service consumption.
         * Count never resets; inject only the last retained-context close. */
        if (fs_injected < 8) {
            ++fs_injected;
            return;
        }
#endif
        uint64_t reader = fs_close_reader;
        fs_close_reader = 0; /* Consumed arm; count/error remain permanent. */
        if (fs_injected++ != FS_CLOSES - 1 || fs_channel_close(reader))
            fs_injection_error = EIO;
    }
}
#endif
static int aether_fs_owner_probe(spa_t *spa, aether_zpl_write_result *result)
{
    static const unsigned char dataset[] = "testpool_zstd/x86_64";
    const uint64_t reader = getauxval(0xa004), writer = getauxval(0xa005);
    struct aether_fs_service_result completion = {0};
#if AETHER_FS_SERVICE_CASE == 3
    if (fs_close_reader || fs_injected || fs_injection_error)
        return EIO;
    fs_close_reader = reader;
#endif
    int error = aether_fs_service_run(spa, dataset, sizeof(dataset) - 1, reader,
                                      writer, 7, &completion);
    result->txg = completion.txg;
    result->bytes_staged = completion.bytes_staged;
    result->state = completion.state;
#if AETHER_FS_SERVICE_CASE == 1
    if (error != 5 || completion.ready != 1 || completion.requests != 5 ||
        completion.stop != 2 || completion.reader_close ||
        completion.writer_close || completion.error != -32)
        return error ? error : EIO;
#elif AETHER_FS_SERVICE_CASE == 2
    if (error != 5 || completion.ready != 1 || completion.requests != FS_PARTIAL_REQUESTS ||
        completion.stop != 1 || completion.reader_close ||
        completion.writer_close || completion.error != -5)
        return error ? error : EIO;
#elif AETHER_FS_SERVICE_CASE == 3
    if (error != 5 || completion.ready != 1 || completion.requests != FS_REQUESTS ||
        completion.stop || completion.reader_close != -13 ||
        completion.writer_close || completion.error != -13 || fs_close_reader ||
        fs_injected != FS_CLOSES || fs_injection_error)
        return error ? error : EIO;
#else
    if (error)
        return error;
    if (completion.ready != 1 || completion.requests != FS_REQUESTS || completion.stop ||
        completion.reader_close || completion.writer_close || completion.error)
        return EIO;
#endif
    return 0;
}
