/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_FS_MIXED_SERVICE_H
#define AETHER_FS_MIXED_SERVICE_H
#include "native-service.h"
/* Trusted importer: base SPA/endpoint/pointer/serialization obligations apply.
 * Explicit uid/gid<=INT32_MAX are trusted labels. Private AFSRPC03 permits at
 * most8 TOTAL mutations (namespace0 or16-byte writes),64 requests. Both typed
 * success-only retirements consume old contexts before reopen/next reply.
 * Root aliases refresh, file aliases survive rename; live aliases deny remove.
 * Failed/unknown outcomes retire permanently, never reset/replay. stop0 means
 * explicit disconnect, return0 additionally requires both closes. No
 * operational readiness, public durability, arbitrary staging or restart
 * authorization. */
int aether_fs_mixed_run(void *spa, const unsigned char *dataset, size_t length,
                        uint64_t reader, uint64_t writer, uint64_t rights,
                        uint64_t uid, uint64_t gid,
                        struct aether_fs_service_result *result);
#endif
