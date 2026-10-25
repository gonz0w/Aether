/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_FILESYSTEM_ENGINE_H
#define AETHER_FILESYSTEM_ENGINE_H
#include <stdint.h>
#include "native-service.h"
/* Private process-local borrow, not an RPC or a released startup ABI. The
 * initial thread owns this initialized, aligned output exclusively until run
 * returns. Code, native endpoint bindings and writable SPA remain resident.
 * Completed bits describe separate obligations; terminal0 never proves native
 * stop/reclaim or independent disk recovery. A failed process is not
 * replayable.
 */
enum aether_fs_engine_phase {
    AETHER_FS_RUNTIME = 1,
    AETHER_FS_BLOCK = 2,
    AETHER_FS_UTC = 4,
    AETHER_FS_KERNEL = 8,
    AETHER_FS_IMPORT = 16,
    AETHER_FS_SERVICE = 32,
    AETHER_FS_SPA_CLOSED = 64,
    AETHER_FS_EXPORTED = 128,
    AETHER_FS_KERNEL_STOPPED = 256,
    AETHER_FS_HELPERS_JOINED = 512,
    AETHER_FS_BLOCK_CLOSED = 1024,
    AETHER_FS_UTC_CLOSED = 2048,
    AETHER_FS_RUNTIME_STOPPED = 4096,
    AETHER_FS_FINISHED = 8191
};
struct aether_fs_launch_state {
    uint64_t version, bytes, reader, writer, phases;
    int64_t engine_error;
    struct aether_fs_service_result service;
    int64_t startup_reader_close, startup_writer_close;
};
_Static_assert(sizeof(struct aether_fs_launch_state) == 136, "launch state");
_Static_assert(__builtin_offsetof(struct aether_fs_launch_state, service) == 48,
               "launch service result");
int aether_fs_engine_run(uint64_t, struct aether_fs_launch_state *);
/* Engine calls this once with a borrowed, validated, live writable SPA. The
 * Rust owner consumes its service contexts/endpoints before returning. */
int aether_fs_launch_serve(void *, struct aether_fs_launch_state *);
#endif
