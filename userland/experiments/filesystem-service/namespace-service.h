/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_FS_NAMESPACE_SERVICE_H
#define AETHER_FS_NAMESPACE_SERVICE_H
#include "native-service.h"
/* Trusted importer only: all native-service.h SPA/endpoint/pointer obligations
 * apply. Explicit uid/gid<=INT32_MAX are owner labels, not client authority.
 * This separate AFSRPC02 build exposes only this entry, not the old entry.
 * Exactly one namespace attempt; consume context before reply/endpoints. stop6
 * means successful namespace completion; return0 additionally requires both
 * endpoint closes. Results are not public durability or retry authorization. */
int aether_fs_namespace_run(void *spa, const unsigned char *dataset,
                            size_t length, uint64_t reader, uint64_t writer,
                            uint64_t rights, uint64_t uid, uint64_t gid,
                            struct aether_fs_service_result *result);
#endif
