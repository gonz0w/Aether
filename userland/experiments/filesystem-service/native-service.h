/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_FS_SERVICE_H
#define AETHER_FS_SERVICE_H
#include <stddef.h>
#include <stdint.h>
struct aether_fs_service_result {
    uint64_t ready, requests, stop;
    int64_t reader_close, writer_close;
    int64_t error;
    uint64_t txg, bytes_staged, state;
};
/* Trusted synchronous engine entry; see native-service.rs safety/provisioning
 * contract. Consumes validated endpoint bindings, not SPA ownership. No public
 * opcode, native grant, supervisor policy or durability promise is introduced.
 */
int aether_fs_service_run(void *spa, const unsigned char *dataset,
                          size_t length, uint64_t reader, uint64_t writer,
                          uint64_t rights,
                          struct aether_fs_service_result *out);
#endif
